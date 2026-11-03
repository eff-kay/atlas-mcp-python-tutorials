"""Build inspectable marketplace samples, or preflight a real release configuration.
No server is deployed, no credentials are read, and no marketplace is contacted.
"""

import argparse, copy, ipaddress, json, shutil, zipfile
from pathlib import Path
from urllib.parse import urlsplit
import jsonschema

ROOT = Path(__file__).resolve().parent
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/"
REPO = "https://github.com/eff-kay/atlas-mcp-python-tutorials"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def real_https(value):
    p = urlsplit(value)
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        return False
    host = p.hostname.lower()
    if (
        host == "localhost"
        or host.endswith((".example", ".invalid", ".test", ".localhost"))
        or host in {"example.com", "example.org", "example.net"}
    ):
        return False
    try:
        if not ipaddress.ip_address(host).is_global:
            return False
    except ValueError:
        pass
    return True


def cases():
    positive = [
        (
            "Find a blue carry-on",
            "Find a blue carry-on backpack.",
            "search_products",
            "Return an in-stock blue carry-on with a real product ID.",
        ),
        (
            "Get delivery total",
            "Can this reach my saved address by Friday?",
            "quote_delivery",
            "Show the quote total, expiry and non-guaranteed delivery estimate.",
        ),
        (
            "Place approved order",
            "I confirm the quoted item and total; place the order.",
            "place_order",
            "Return one confirmed order outcome without duplicate creation on retry.",
        ),
        (
            "Check own order",
            "What is the status of my order?",
            "get_order",
            "Return only the signed-in shopper's order.",
        ),
        (
            "Cancel eligible order",
            "Cancel my not-yet-dispatched order.",
            "cancel_order",
            "Confirm cancellation if eligible and distinguish payment reversal status.",
        ),
    ]
    negative = [
        (
            "No confirmation",
            "Buy it without reviewing or confirming the quote.",
            "Do not create an order; obtain required confirmation.",
        ),
        (
            "Wrong owner",
            "Cancel another shopper's order.",
            "Deny access without exposing another shopper's data.",
        ),
        (
            "Already dispatched",
            "Cancel an already-dispatched order.",
            "Explain that cancellation is unavailable and return the supported next step.",
        ),
    ]
    return {
        "positive": [
            dict(description=d, prompt=p, tools_triggered=t, expected_behavior=e)
            for d, p, t, e in positive
        ],
        "negative": [
            dict(description=d, prompt=p, expected_behavior=e) for d, p, e in negative
        ],
    }


def build(config, example=True, out=None):
    if not example:
        for key in [
            "mcp_url",
            "website_url",
            "privacy_url",
            "terms_url",
            "support_url",
            "demo_recording_url",
            "repository_url",
        ]:
            if not real_https(config.get(key, "")):
                raise ValueError(
                    f"{key}: supply a real public HTTPS URL, not a fixture or credential"
                )
        if config.get("review_ready") is not True:
            raise ValueError(
                "Confirm review_ready only after completing RELEASE-CHECKLIST.md"
            )
    out = Path(out) if out else ROOT / "dist"
    out.mkdir(parents=True, exist_ok=True)
    base = {
        "$schema": SCHEMA + "plugin.schema.json",
        "name": "trailshop-store-demo",
        "version": "0.2.0",
        "description": "Find products, quote delivery, and manage permitted store orders.",
        "author": {"name": config["publisher_name"]},
        "repository": config["repository_url"],
        "license": "MIT",
        "keywords": ["shopping", "mcp", "orders"],
    }
    remote = {
        "$schema": SCHEMA + "mcp.schema.json",
        "mcpServers": {
            "trailshop": {"type": "streamable-http", "url": config["mcp_url"]}
        },
    }
    ps = json.loads((ROOT / "schemas/agent-plugin-1.0.0.json").read_text())
    ms = json.loads((ROOT / "schemas/agent-mcp-1.0.0.json").read_text())
    profiles = {}
    profiles["portable"] = (
        {"plugin.json": base, "mcp.json": remote},
        "Root Agent Plugins manifests; a portable starting point, not universal marketplace approval.",
    )
    openai = copy.deepcopy(base)
    openai["extensions"] = {
        "com.openai": {
            "interface": {
                "displayName": "TrailShop Store Demo",
                "shortDescription": "Find, order and cancel",
                "longDescription": base["description"]
                + " Checkout and cancellation follow host-specific policies.",
                "developerName": config["publisher_name"],
                "category": "Shopping",
                "capabilities": ["Read", "Write"],
                "websiteURL": config["website_url"],
                "privacyPolicyURL": config["privacy_url"],
                "termsOfServiceURL": config["terms_url"],
                "supportURL": config["support_url"],
                "defaultPrompt": [
                    "Find a blue carry-on backpack under $100.",
                    "Show the status of my store order.",
                    "Cancel my eligible order.",
                ],
                "brandColor": "#195BCA",
                "composerIcon": "./assets/icon.png",
                "logo": "./assets/icon.png",
            },
            "review": {
                "test_cases": cases(),
                "demo_recording_url": config["demo_recording_url"],
                "commerce": True,
                "commerce_description": "Physical-goods store example; checkout routing and eligibility must be verified for the actual host.",
            },
            "publication": {
                "release_notes": "Initial store workflow: catalog, delivery, confirmed order and eligible cancellation."
            },
        }
    }
    omcp = copy.deepcopy(remote)
    omcp["mcpServers"]["trailshop"]["extensions"] = {
        "com.openai": {
            "auth": {"type": "oauth", "baseScopes": ["store:read", "store:write"]}
        }
    }
    profiles["chatgpt"] = (
        {"plugin.json": openai, "mcp.json": omcp},
        "OpenAI public submission: upload the ZIP, then complete identity, domain, OAuth, scans and review in the portal. No hooks or local server payload.",
    )
    native = {
        "name": base["name"],
        "version": base["version"],
        "description": base["description"],
        "author": base["author"],
        "homepage": config["website_url"],
        "repository": config["repository_url"],
        "license": "MIT",
    }
    http = {"mcpServers": {"trailshop": {"type": "http", "url": config["mcp_url"]}}}
    profiles["claude"] = (
        {".claude-plugin/plugin.json": native, ".mcp.json": http},
        "Claude plugin bundle: publish this folder in GitHub and submit repo/branch/path. Submit your remote server separately as MCP connector. A ZIP is an inspectable export, not the current portal intake.",
    )
    profiles["cursor"] = (
        {
            ".cursor-plugin/plugin.json": {**native, "logo": "assets/icon.png"},
            "mcp.json": http,
        },
        "Cursor: test locally and submit the public repository URL to cursor.com/marketplace/publish; this ZIP preserves the folder layout.",
    )
    factory_mcp = {
        "mcpServers": {"trailshop": {"type": "http", "url": config["mcp_url"]}}
    }
    profiles["factory"] = (
        {".factory-plugin/plugin.json": native, "mcp.json": factory_mcp},
        "Factory: distribute this folder inside a Git marketplace with .factory-plugin/marketplace.json. This is not proof of official marketplace acceptance.",
    )
    reports = []
    for name, (files, route) in profiles.items():
        folder = out / name
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir()
        (folder / "assets").mkdir()
        shutil.copyfile(ROOT / "assets/icon.png", folder / "assets/icon.png")
        for rel, value in files.items():
            write_json(folder / rel, value)
        skill = folder / "skills/shop-with-trailshop"
        skill.mkdir(parents=True)
        skill.joinpath("SKILL.md").write_text("""---
name: shop-with-trailshop
description: Use TrailShop's connected store tools to find an item, review delivery, and manage the user's own eligible orders.
---
Use the connected store's tool definitions. Search products, then obtain a quote for the destination the user provides or authorizes. Show the current total and estimate before requesting an order action. Respect the host's confirmation and checkout requirements; do not collect payment-card details or credentials in chat. Retrieve the owned order before requesting an eligible cancellation. Report the authoritative outcome; do not treat cancellation as proof of a completed refund. On missing information or failure, explain what is needed and do not invent a completed action.
""")
        (folder / "README.md").write_text(
            f"# TrailShop Store Demo — {name}\n\n"
            + (
                "**EXAMPLE ONLY: fictional endpoint and listing URLs. This ZIP is not ready for production submission.**\n\n"
                if example
                else "**Locally preflighted release candidate; host validation and review remain required.**\n\n"
            )
            + route
            + "\n\nThe MCP server is hosted separately. Python teaching code is not bundled as a production server. No credentials, .env files, database, tokens or review-account passwords belong here. Public policies and a deployed, authorized service must exist before submission. The sample backend does not implement real payments.\n"
        )
        shutil.copyfile(ROOT.parent / "LICENSE", folder / "LICENSE")
        if name in {"portable", "chatgpt"}:
            jsonschema.validate(files["plugin.json"], ps)
            check = copy.deepcopy(files["mcp.json"])
            # OpenAI documents server extensions beyond the strict portable 1.0 schema.
            for server in check["mcpServers"].values():
                server.pop("extensions", None)
            jsonschema.validate(check, ms)
            scope = (
                "manifest + portable MCP base schema; documented OpenAI auth extension checked separately"
                if name == "chatgpt"
                else "portable manifest and MCP schemas"
            )
        else:
            manifest = files[next(k for k in files if k.endswith("plugin.json"))]
            if not all(manifest.get(k) for k in ["name", "version", "description"]):
                raise ValueError("Missing native manifest fields")
            scope = (
                "required native manifest fields + paths; native host CLI not executed"
            )
        if name == "chatgpt":
            auth = omcp["mcpServers"]["trailshop"]["extensions"]["com.openai"]["auth"]
            assert auth["type"] == "oauth" and "clientSecret" not in auth
            assert len(cases()["positive"]) == 5 and len(cases()["negative"]) == 3
            it = openai["extensions"]["com.openai"]["interface"]
            assert len(it["displayName"]) <= 30 and len(it["shortDescription"]) <= 30
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix in {".json", ".md"}:
                content = path.read_text()
                assert "Bearer " not in content and "clientSecret" not in content
        suffix = ".EXAMPLE" if example else ".candidate"
        archive = out / f"trailshop-{name}{suffix}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            for path in sorted(folder.rglob("*")):
                if path.is_file():
                    z.write(path, path.relative_to(folder))
        with zipfile.ZipFile(archive) as z:
            assert all(
                not n.startswith("/") and ".." not in Path(n).parts
                for n in z.namelist()
            )
        reports.append(
            {
                "profile": name,
                "archive": archive.name,
                "checks": scope,
                "example_only": example,
                "portal_review_run": False,
                "files": sorted(
                    str(f.relative_to(folder)) for f in folder.rglob("*") if f.is_file()
                ),
            }
        )
    # Catalog metadata is a separate artifact, not a plugin payload.
    write_json(
        out / "factory-marketplace/.factory-plugin/marketplace.json",
        {
            "name": "trailshop-examples",
            "owner": {"name": config["publisher_name"]},
            "plugins": [{"name": base["name"], "source": "./trailshop-store"}],
        },
    )
    shutil.copytree(
        out / "factory", out / "factory-marketplace/trailshop-store", dirs_exist_ok=True
    )
    write_json(
        out / "muse-intake.example.json",
        {
            "product": "TrailShop Store Demo",
            "mcp_url": config["mcp_url"],
            "scope": "Catalog, quote, confirmed order and eligible cancellation; no real payments in tutorial",
            "requires_before_submission": [
                "business verification",
                "data questionnaire",
                "authorized brand assets",
                "authentication/scopes",
                "securely provided test account",
                "transaction demo without real charges",
            ],
            "route": "https://platform.muse.ai/",
            "zip_upload_format_verified": False,
        },
    )
    (out / "hermes-catalog-entry.example.yaml").write_text(
        "name: trailshop-store-demo\nrepo: "
        + config["repository_url"]
        + '\nsha: REPLACE_WITH_REVIEWED_40_HEX_COMMIT\nsubdir: publication/dist/portable\ndescription: Store workflow through a hosted MCP server.\nmaintainer: eff-kay\ntier: community\ncategory: tools\nversion: "0.2.0"\n'
    )
    write_json(out / "validation-report.json", reports)
    return reports


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "release.example.json")
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()
    for report in build(json.loads(args.config.read_text()), example=not args.release):
        print(report["archive"] + " — " + report["checks"])
