"""Build the offline presentation kit. Does not deploy, connect or submit anything."""

import base64
import copy
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from html import escape
from pathlib import Path

import jsonschema

from build_packages import ROOT, build

OUT = ROOT / "showcase"
ASSETS = ROOT / "showcase-assets"
PUBLIC = "https://eff-kay.github.io/talks/mcp/submission-showcase/"
SOURCES = {
    "ChatGPT package format": "https://developers.openai.com/plugins/build/plugins",
    "ChatGPT upload and review": "https://developers.openai.com/plugins/deploy/submission",
    "ChatGPT review requirements": "https://developers.openai.com/plugins/deploy/app-review",
    "Claude plugin structure": "https://claude.com/docs/plugins/build",
    "Claude GitHub submission": "https://claude.com/docs/plugins/submit",
    "Claude plugin preflight": "https://claude.com/docs/plugins/pre-submission-checklist",
    "Claude connector submission": "https://claude.com/docs/connectors/building/submission",
    "Claude connector tool review": "https://claude.com/docs/connectors/building/review-criteria",
}
DIFFERENCES = [
    [
        "What you send",
        "Plugin ZIP, with manifests at its root",
        "GitHub repo + plugin folder + tracked branch/tag",
        "Hosted HTTPS MCP URL + portal listing",
    ],
    [
        "Identity file",
        "plugin.json",
        ".claude-plugin/plugin.json",
        "Listing fields in the portal",
    ],
    [
        "MCP connection file",
        "mcp.json · type: streamable-http",
        ".mcp.json · type: http",
        "The URL is entered in the portal",
    ],
    [
        "Platform metadata",
        "extensions.com.openai.interface, review, publication",
        "Native manifest plus README; data handling in portal",
        "Documentation, privacy, support, icon, use cases",
    ],
    [
        "Sign-in configuration",
        "OpenAI auth extension: type none for this public fixture",
        "No authentication for the referenced public fixture",
        "Choose No authentication for this public fixture",
    ],
    [
        "Review evidence",
        "Initial MCP review: 5 positive + 3 negative cases and walkthrough",
        "Repository scan, directory checks and any reviewer requests",
        "Test every tool; supply populated reviewer account",
    ],
    [
        "Skills",
        "Shared skills/ folder in this sample",
        "Same shared skills/ folder",
        "Not a standalone skill submission",
    ],
    [
        "Publishing",
        "Resolve findings → review → publish approved ZIP",
        "Scan → possible review → applicable publishing gate",
        "Auto-screened Community by default; exceptions exist",
    ],
    [
        "What this sample lacks",
        "Real stable endpoint, publisher setup, recording and review",
        "Real connected service, production policies and directory checks",
        "Live stable URL, listing and portal submission",
    ],
]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def dump(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def archive(folder, dest, prefix=""):
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(folder.rglob("*")):
            if f.is_file() and f != dest:
                name = prefix + f.relative_to(folder).as_posix()
                info = zipfile.ZipInfo(name, (2026, 11, 3, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, f.read_bytes())


def simple_cases():
    return json.loads((ROOT / "simple-showcase-inputs/scenarios.json").read_text())


def main():
    # Only remove this generator's output; curated inputs and old profiles remain.
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    with tempfile.TemporaryDirectory() as tmp:
        build(json.loads((ROOT / "release.example.json").read_text()), out=tmp)
        shutil.copytree(Path(tmp) / "chatgpt", OUT / "chatgpt-upload")
        shutil.copytree(Path(tmp) / "claude", OUT / "claude-plugin-repo")
    oa = OUT / "chatgpt-upload"
    cl = OUT / "claude-plugin-repo"
    om = json.loads((oa / "plugin.json").read_text())
    auth = json.loads((oa / "mcp.json").read_text())
    auth["mcpServers"]["trailshop"]["extensions"]["com.openai"]["auth"] = {
        "type": "none"
    }
    om["version"] = "0.3.0"
    om["description"] = (
        "Search a demo backpack and quote delivery. No purchases or accounts."
    )
    om["keywords"] = ["shopping", "mcp", "quotes"]
    ext = om["extensions"]["com.openai"]
    ext["interface"].update(
        shortDescription="Search and quote delivery",
        longDescription=om["description"],
        capabilities=["Search products", "Quote delivery"],
        defaultPrompt=[
            "Find a blue backpack and tell me the total including delivery."
        ],
    )
    ext["review"].update(
        test_cases=simple_cases(),
        commerce=False,
        commerce_description="Fictional catalog and pricing information only; no checkout, transactions or payments.",
    )
    ext["publication"]["release_notes"] = (
        "Two synchronous tools: search_products and quote_delivery."
    )
    dump(oa / "plugin.json", om)
    dump(oa / "mcp.json", auth)
    cm = json.loads((cl / ".claude-plugin/plugin.json").read_text())
    cm.update(
        displayName="TrailShop Store Demo",
        version="0.3.0",
        description=om["description"],
    )
    dump(cl / ".claude-plugin/plugin.json", cm)
    skill = """---
name: shop-with-trailshop
description: Find a backpack and quote its delivery using the connected demo store.
---
Use search_products to find the requested color. Use the returned product ID with quote_delivery. Explain the item price, delivery cost and total in USD. Friday is a fictional estimate. Report an empty search or unknown product honestly. This server has no purchase, cancellation or account tools. Do not invent those capabilities.
"""
    for folder in [oa, cl]:
        write(folder / "skills/shop-with-trailshop/SKILL.md", skill)
        write(
            folder / "README.md",
            """# TrailShop: two-function demo

Teaching sample with reserved .example URLs. This plugin connects to the same simple server used in the live talk. search_products finds a fictional blue backpack priced at $79; quote_delivery returns $12 shipping and a $91 total, with a fictional Friday estimate. Both functions are synchronous and print logs in their server terminal.

The public fixture has no authentication, accounts, orders, checkout or payments. Unknown colors return no matches; unknown product IDs return an error object. The service runs separately from the plugin. Replace the placeholder endpoint, support, privacy, terms and recording URLs before a real submission. The service owner must publish accurate data-handling information. Docsalot branding belongs to its owner; the code license does not grant trademark rights.
""",
        )
    connector = {
        "_format": "Presenter worksheet, not an official import schema",
        "example_only": True,
        "portal": "https://claude.ai/directory/manage",
        "submission_type": "MCP connector",
        "connection": {"url": "https://store.example/mcp"},
        "listing": {
            "name": "TrailShop Store Demo",
            "description": om["description"],
            "documentation_url": "https://store.example/docs",
            "privacy_url": "https://store.example/privacy",
            "support_contact": "support@store.example",
        },
        "authentication": {
            "required": False,
            "method": "No authentication",
            "reason": "Public fictional catalog and prices; no accounts or personal data",
        },
        "tools": ["search_products", "quote_delivery"],
        "status": "NOT SUBMITTED",
    }
    dump(OUT / "claude-connector/portal-worksheet.example.json", connector)
    write(
        OUT / "claude-connector/README.md",
        "# Remote connector worksheet\n\nEnter the hosted HTTPS /mcp URL, listing and No authentication in the portal. This JSON is our worksheet, not an import format. A referenced remote server also needs a connector submission when distributing a Claude plugin.\n",
    )
    (OUT / "review-evidence").mkdir()
    for name in ["tool-inventory.json", "store-review-results.json", "origin.json"]:
        shutil.copy2(
            ROOT / "simple-showcase-inputs" / name, OUT / "review-evidence" / name
        )
    dump(OUT / "review-evidence/scenarios.json", simple_cases())
    write(
        OUT / "review-evidence/README.md",
        """# Evidence scope

Captured from the actual store/simple-demo/server.py over HTTP. Exactly two tools, no async/await in the demo source, no authentication, database or transactions. Five positive and three negative preparation scenarios refer only to search and quotation. Negative cases include empty results and an unknown product; these are business outcomes, not necessarily MCP protocol errors. The unsupported-purchase case checks that no purchase tool exists; a model refusal still requires testing in the target app. Local results do not establish target-app behavior, portal approval or a completed recording. See origin.json for the source hash.
""",
    )
    write(
        OUT / "review-evidence/walkthrough-script.md",
        "# Recording outline — actual recording still required\n\n1. Connect the hosted two-function server with No authentication.\n2. Ask: Find a blue backpack and tell me the total including delivery.\n3. Show search_products and quote_delivery in the terminal logs.\n4. Show $79 plus $12 equals $91 USD, with a fictional Friday estimate.\n5. Demonstrate green/no match and an unknown product ID.\n6. Explain there is no purchase tool. Record the actual target app before submitting.\n",
    )
    write(
        OUT / "review-evidence/data-handling-worksheet.md",
        "# Data-handling worksheet\n\nThis demo processes a color and a product ID and prints them in the local terminal. It has no user accounts, saved addresses, database or payment processing. Document actual hosted request logging, retention, support and privacy practices before release; the local fixture is not a production privacy policy.\n",
    )
    write(
        OUT / "START-HERE.md",
        """# The same two-function server, three submission routes

Open index.html for the side-by-side viewer. chatgpt-upload/ is the exact ChatGPT ZIP content. claude-plugin-repo/ is the native GitHub plugin folder (including hidden manifests). claude-connector/ is a portal worksheet, not a plugin. review-evidence/ contains actual HTTP fixture outputs and preparation cases. See DIFFERENCES.md, PRESENTING.md and REPLACE-BEFORE-SUBMIT.md.

Live code: https://github.com/eff-kay/atlas-mcp-python-tutorials/tree/main/store/simple-demo

Run from that folder: uv run python server.py. Local endpoint: http://127.0.0.1:8770/mcp. For ngrok: ngrok http http://127.0.0.1:8770 --host-header=127.0.0.1:8770, then use the current HTTPS URL with /mcp. The packaged HTTPS .example URL is deliberately a placeholder; it will not connect until replaced.

Exactly two tools: search_products(color) and quote_delivery(product_id). No orders, cancellation, OAuth, database or external APIs. The packages reference the hosted server; they do not deploy it. The complete kit ZIP is a presenter artifact, not a universal marketplace upload.
""",
    )
    table = (
        "| Difference | ChatGPT plugin | Claude plugin | Claude connector |\n|---|---|---|---|\n"
        + "\n".join("| " + " | ".join(r) + " |" for r in DIFFERENCES)
    )
    write(
        OUT / "DIFFERENCES.md",
        "# Same simple server; different packaging\n\n"
        + table
        + "\n\nBoth plugin folders share identical search-and-quote instructions and point to the same hosted MCP URL. This example uses No authentication because all data is public and fictional. Authenticated account integrations are a different example. ChatGPT review cases and recording metadata live in extensions.com.openai.review; release notes live in extensions.com.openai.publication. Claude reads its native manifest and README and takes a repository/path. A Claude connector takes the URL and portal fields. The two MCP configuration type values are wrapper dialects for the same protocol.\n",
    )
    write(
        OUT / "PRESENTING.md",
        """# First-person submission walkthrough

“This is the exact example we just ran: search_products and quote_delivery. It finds a $79 blue backpack and returns a $91 total with shipping. There are no orders or user accounts.”

“For ChatGPT, I show the upload ZIP. plugin.json contains identity, listing and five positive/three negative review cases. mcp.json references the hosted endpoint with auth type none. The actual recording and policy URLs must replace these placeholders.”

“For Claude, I show .claude-plugin/plugin.json and .mcp.json. The shared skill is identical. I submit this native folder through GitHub. The remote connector route instead asks for the HTTPS endpoint, No authentication and listing details.”

“The captured evidence exercises the two tools over HTTP. Empty results and an unknown product are negative scenarios. The no-purchase scenario checks the inventory; I still need to show the actual app refusing an unsupported purchase in my recording.”

“The .example URL is a teaching placeholder. My working ngrok URL is for the live connection; a stable hosted endpoint and completed review material are needed for a real directory submission.”
""",
    )
    write(
        OUT / "REPLACE-BEFORE-SUBMIT.md",
        "# Replace before submission\n\n- Replace https://store.example/mcp in both MCP files and the connector worksheet with the actual stable HTTPS endpoint, including /mcp.\n- Replace website, support, privacy, terms, contact and recording placeholders with real accessible material.\n- Keep No authentication only for this public fictional catalog. Do not add account data without proper authorization.\n- Rerun every review case in the target app and record the experience; local HTTP checks are not an app recording.\n- Confirm tool titles/annotations against each platform’s requirements; this minimal live demo intentionally has no review-specific hints yet.\n- Complete publisher/domain checks and current portal validation. Submit only the ChatGPT plugin ZIP, or the Claude native repository folder; the complete presenter ZIP is not an upload format.\n",
    )
    write(
        OUT / "SOURCES.md",
        "# Official sources\n\n"
        + "\n".join(f"- [{k}]({v})" for k, v in SOURCES.items())
        + "\n",
    )
    shutil.copy2(ROOT.parent / "LICENSE", OUT / "LICENSE")
    (OUT / "server-source").mkdir()
    shutil.copy2(
        ROOT / "simple-showcase-inputs/server.py", OUT / "server-source/server.py"
    )
    verify(om, cm, auth)
    archive(oa, OUT / "trailshop-chatgpt.EXAMPLE.zip")
    archive(cl, OUT / "trailshop-claude-plugin.EXAMPLE.zip")
    report = {
        "example_only": True,
        "checked": "2026-11-03",
        "local_checks": [
            "Portable plugin schema",
            "Portable MCP base schema excluding documented OpenAI extension",
            "OpenAI known metadata/auth field placement (scoped checks, not full host schema)",
            "Claude required fields/paths, README/license and JSON structure",
            "Shared skill identical across profiles",
            "Two-tool inventory, five positive/three negative fixture preparation cases",
            "No credential fields, absolute/archive traversal paths, system junk or omitted hidden manifests",
        ],
        "fixture_execution": json.loads(
            (OUT / "review-evidence/origin.json").read_text()
        ),
        "not_run": [
            "ChatGPT portal import/scan/review",
            "Claude native CLI: not installed",
            "Codex native validation: installed CLI exposes no validate command",
            "Claude portal validation/security scan",
            "Hosted deployment or target-app conversation tests",
            "Commerce eligibility review",
        ],
        "release_ready": False,
    }
    dump(OUT / "validation-report.json", report)
    render(om, cm, auth)
    # Check the archives' real member names, including hidden paths.
    for target, required in [
        ("trailshop-chatgpt.EXAMPLE.zip", "plugin.json"),
        ("trailshop-claude-plugin.EXAMPLE.zip", ".claude-plugin/plugin.json"),
    ]:
        with zipfile.ZipFile(OUT / target) as z:
            names = z.namelist()
            assert required in names
            assert all(
                not n.startswith("/") and ".." not in Path(n).parts for n in names
            )
            assert all(
                Path(n).name not in {".DS_Store", "Thumbs.db"} and "__MACOSX" not in n
                for n in names
            )
    write(
        OUT / "checksums.sha256",
        "\n".join(
            hashlib.sha256(f.read_bytes()).hexdigest()
            + "  "
            + f.relative_to(OUT).as_posix()
            for f in sorted(OUT.rglob("*"))
            if f.is_file()
        )
        + "\n",
    )
    archive(
        OUT,
        OUT / "trailshop-submission-showcase.EXAMPLE.zip",
        "trailshop-submission-showcase/",
    )
    print(
        f"Built {OUT}: three routes, two plugin exports, complete presenter kit and scoped validation report."
    )


def verify(om, cm, auth):
    jsonschema.validate(
        om, json.loads((ROOT / "schemas/agent-plugin-1.0.0.json").read_text())
    )
    base = copy.deepcopy(auth)
    base["mcpServers"]["trailshop"].pop("extensions")
    jsonschema.validate(
        base, json.loads((ROOT / "schemas/agent-mcp-1.0.0.json").read_text())
    )
    ext = om["extensions"]["com.openai"]
    assert "release_notes" not in ext and ext["publication"]["release_notes"]
    assert len(ext["review"]["test_cases"]["positive"]) == 5
    assert len(ext["review"]["test_cases"]["negative"]) == 3
    assert len(cm["name"]) <= 64 and re.fullmatch(
        "[a-z0-9]+(?:-[a-z0-9]+)*", cm["name"]
    )
    assert len((OUT / "claude-plugin-repo/README.md").read_text().split()) >= 40
    assert (
        OUT / "chatgpt-upload/skills/shop-with-trailshop/SKILL.md"
    ).read_bytes() == (
        OUT / "claude-plugin-repo/skills/shop-with-trailshop/SKILL.md"
    ).read_bytes()
    result = json.loads((OUT / "review-evidence/store-review-results.json").read_text())
    assert len(result) == 8 and sum(x["negative"] for x in result) == 3
    for folder in ["chatgpt-upload", "claude-plugin-repo"]:
        for f in (OUT / folder).rglob("*"):
            if f.is_file():
                assert f.name not in {
                    ".env",
                    ".DS_Store",
                    "Thumbs.db",
                } and f.suffix not in {".sqlite3", ".pyc"}
                if f.suffix == ".json":

                    def scan(obj):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                assert k not in {
                                    "clientSecret",
                                    "client_secret",
                                    "password",
                                    "test_credentials",
                                    "reviewer_instructions",
                                    "headers",
                                }
                                scan(v)
                        elif isinstance(obj, list):
                            for v in obj:
                                scan(v)

                    scan(json.loads(f.read_text()))


def render(om, cm, auth):
    template = (ROOT / "showcase-template.html").read_text()
    payload = {
        "files": {
            "chatgptManifest": json.dumps(om, indent=2),
            "claudeManifest": json.dumps(cm, indent=2),
            "chatgptConnection": json.dumps(auth, indent=2),
            "claudeConnection": (OUT / "claude-plugin-repo/.mcp.json").read_text(),
            "connector": (
                OUT / "claude-connector/portal-worksheet.example.json"
            ).read_text(),
            "skill": (
                OUT / "chatgpt-upload/skills/shop-with-trailshop/SKILL.md"
            ).read_text(),
        },
        "differences": DIFFERENCES,
        "sources": SOURCES,
        "cases": json.loads(
            (OUT / "review-evidence/store-review-results.json").read_text()
        ),
    }

    def data(file, mime):
        return (
            "data:"
            + mime
            + ";base64,"
            + base64.b64encode((ASSETS / file).read_bytes()).decode()
        )

    for key, val in {
        "JAKARTA_FONT": data("PlusJakartaSans.ttf", "font/ttf"),
        "MONO_FONT": data("JetBrainsMono.ttf", "font/ttf"),
        "BRAND_LOGO": data("docsalot-logo.svg", "image/svg+xml"),
        "ALL_KIT_URL": PUBLIC + "trailshop-submission-showcase.EXAMPLE.zip",
        "EMBEDDED_PAYLOAD": json.dumps(payload, ensure_ascii=False).replace(
            "</", "<\\/"
        ),
        "FONT_LICENSES": escape(
            (ASSETS / "PlusJakartaSans-OFL.txt").read_text()
            + "\n"
            + (ASSETS / "JetBrainsMono-OFL.txt").read_text()
        ),
    }.items():
        template = template.replace("@@" + key + "@@", val)
    assert "@@" not in template
    write(OUT / "index.html", template)


if __name__ == "__main__":
    main()
