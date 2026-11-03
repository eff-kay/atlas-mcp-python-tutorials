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

from build_packages import ROOT, build, cases

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
        "OpenAI auth extension declares OAuth client/scopes; secrets in portal",
        "Remote connector handles account sign-in; no secret in .mcp.json",
        "Configure OAuth for user-account access in portal",
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
        "Real endpoint, publisher setup, OAuth, recording and review",
        "Real connected service, production policies and directory checks",
        "Live URL, real auth and portal submission",
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
    auth["mcpServers"]["trailshop"]["extensions"]["com.openai"]["auth"].update(
        {
            "client": {
                "mode": "provided",
                "clientId": "trailshop-demo-client",
                "tokenEndpointAuthMethod": "client_secret_basic",
            },
            "authorizationUrl": "https://store.example/oauth/authorize",
            "tokenUrl": "https://store.example/oauth/token",
        }
    )
    dump(oa / "mcp.json", auth)
    cm = json.loads((cl / ".claude-plugin/plugin.json").read_text())
    cm["displayName"] = "TrailShop Store Demo"
    dump(cl / ".claude-plugin/plugin.json", cm)
    for folder, route in [
        (oa, "ChatGPT upload ZIP"),
        (cl, "Claude GitHub plugin folder"),
    ]:
        write(
            folder / "README.md",
            f"""# TrailShop Store Demo

**Teaching sample: reserved .example URLs. Replace and test before submission.**

This plugin connects a fictional store workflow: search for a blue backpack, prepare delivery pricing, review and confirm an eligible order, retrieve its status, and cancel it when permitted. Its MCP service is hosted separately. The Python workshop simulates all orders and payments; these manifests do not deploy a service or implement OAuth.

Distribution route: {route}. The shared skill describes the shopping sequence; the server remains responsible for customer ownership and order-state checks. Installation does not grant permission to act on another customer's order. Review the actual host's commerce rules before enabling purchases.

## Privacy and support

The planned workflow uses product IDs, a destination reference and the connected shopper's order details. Real data practices, retention, providers, support and privacy/terms pages must be documented by the service owner before launch. The sample URLs are placeholders, not published policies.

The bundled mark belongs to Docsalot and is used for this author's workshop. The MIT license covers example code, not trademark rights.
""",
        )
    connector = {
        "_format": "Presenter worksheet, not an official import schema or API payload",
        "example_only": True,
        "portal": "https://claude.ai/directory/manage",
        "submission_type": "MCP connector",
        "connection": {
            "url": "https://store.example/mcp",
            "users_connect_to_different_urls": False,
        },
        "listing": {
            "name": "TrailShop Store Demo",
            "one_liner": "Find products and manage your own eligible store orders.",
            "documentation_url": "https://store.example/docs",
            "privacy_url": "https://store.example/privacy",
            "support_contact": "support@store.example",
            "icon": "../chatgpt-upload/assets/icon.png",
        },
        "use_cases": [
            "Find a product",
            "Quote delivery",
            "Review a permitted order action",
            "Retrieve own order",
            "Cancel an eligible order",
        ],
        "authentication": {
            "required": True,
            "method": "OAuth 2.0",
            "planned_scopes": ["store:read", "store:write"],
            "secrets": "Enter privately in the portal; absent from this kit",
        },
        "data_handling": "Complete the worksheet with the actual service owner. No production assertions are made here.",
        "reviewer_access": "Provide a populated dedicated account through secure portal fields; no credentials in this file.",
        "verification": "Standard shared URL sample. Per-customer URLs have separate Verified requirements.",
        "status": "NOT SUBMITTED",
    }
    dump(OUT / "claude-connector/portal-worksheet.example.json", connector)
    write(
        OUT / "claude-connector/README.md",
        """# Claude remote connector

This folder is a presenter worksheet. It is not a Claude plugin and its JSON is not an official import format. The portal receives the HTTPS URL, listing, OAuth setup, data disclosures and reviewer instructions. For a remote server referenced by a plugin, create its connector submission as well. Default Community screening and exceptions follow the current official guide. This fixture has no live endpoint and has not been submitted.
""",
    )
    (OUT / "review-evidence").mkdir(exist_ok=True)
    for name in ["tool-inventory.json", "store-review-results.json", "origin.json"]:
        shutil.copy2(ROOT / "showcase-inputs" / name, OUT / "review-evidence" / name)
    dump(OUT / "review-evidence/scenarios.json", cases())
    write(
        OUT / "review-evidence/README.md",
        """# What this evidence proves

The results were captured from store/06-review-evidence/demo.py using an isolated local SQLite fixture over stdio. Five success scenarios and three expected denials completed; origin.json records the capture and source hash. No real account, payment or production OAuth was exercised. This is not evidence of a ChatGPT or Claude conversation, an uploaded recording, portal scan, marketplace compatibility or approval.

The tool inventory belongs to that specific lesson snapshot. Re-export the deployed server's inventory and rerun every case in the target app using the reviewer account before a real submission. Confirm annotation semantics against actual side effects and each host's rules; do not treat this snapshot as a reviewed tool contract. Generated IDs and expiry timestamps are historical fixture values, not reusable requests.
""",
    )
    write(
        OUT / "review-evidence/walkthrough-script.md",
        """# Recording outline — recording still required

1. Start as the reviewer with the account already populated. Show sign-in without exposing credentials.
2. Ask for a blue carry-on backpack under $100. Show search_products and the selected product.
3. Ask for delivery to the saved destination. Show quote_delivery, total, expiry and delivery estimate.
4. Confirm the displayed quote. Show place_order and one authoritative result.
5. Ask for status with get_order; then cancel the eligible order with cancel_order.
6. Demonstrate three denials: missing confirmation, another customer's order, already-dispatched order.
7. Explain fixture vs production checkout and show the permitted real flow for the host.

The accessible recording URL in the ChatGPT manifest is a placeholder. A script is not a recording. Rerun in each actual host, with fresh IDs and a current quote. No recording is included or claimed.
""",
    )
    write(
        OUT / "review-evidence/data-handling-worksheet.md",
        """# Data handling — fill with the service owner

This is a worksheet, not a privacy policy.

| Question | Complete before submission |
|---|---|
| What personal data is read or stored? | Identify account, destination and order fields actually used |
| Where does it go? | Map the store, routing and courier providers and any telemetry processor |
| What is retained, and for how long? | State actual storage, deletion and retention behavior |
| What APIs do you own or have rights to use? | Identify first-party APIs and authorized partners |
| What appears in logs? | Explain redaction and access control; exclude credentials |
| How are purchases and cancellations handled? | State actual supported checkout, confirmations and refund behavior |
| Where can users get help? | Publish real support, privacy and terms links |

Keep private reviewer credentials and OAuth secrets in the platforms' secure fields. The simulated store makes no real data-retention or payment-provider promise.
""",
    )
    write(
        OUT / "START-HERE.md",
        """# One store. Three submission routes.

Open index.html for a presentation-friendly comparison, or start with DIFFERENCES.md. All store URLs use the reserved .example domain. No server is deployed and no marketplace submission is made.

| Folder/file | What to show |
|---|---|
| chatgpt-upload/ | Exact contents of the sample ChatGPT ZIP; manifests are at the ZIP root |
| claude-plugin-repo/ | Claude plugin folder, including hidden .claude-plugin/ and .mcp.json |
| claude-connector/ | Portal worksheet for the hosted server; not an import schema |
| review-evidence/ | Five success cases, three denials, captured fixture outputs and recording outline |
| DIFFERENCES.md | File, metadata, authentication, evidence and publication comparison |
| PRESENTING.md | A short first-person walkthrough |
| REPLACE-BEFORE-SUBMIT.md | Specific placeholders and external steps |
| validation-report.json | What was checked locally and what remains unchecked |

The individual ChatGPT ZIP is the upload-shaped artifact. The Claude ZIP preserves its GitHub folder for inspection; the portal route is GitHub. The larger showcase ZIP is a presenter kit, not a universal marketplace upload. Enable hidden-file display when browsing the Claude folder.

Code: https://github.com/eff-kay/atlas-mcp-python-tutorials/tree/main/store/codex-demo
Offline kit: the file viewer embeds its fonts, logo and source examples. Individual ZIPs are included; the complete-kit download button links to the public site.
""",
    )
    table = (
        "| Difference | ChatGPT plugin | Claude plugin | Claude connector |\n|---|---|---|---|\n"
        + "\n".join("| " + " | ".join(r) + " |" for r in DIFFERENCES)
    )
    write(
        OUT / "DIFFERENCES.md",
        "# Same store; different submission artifacts\n\nChecked November 3, 2026. This kit chooses the Agent Plugins root format for ChatGPT; OpenAI also documents a Codex compatibility format.\n\n"
        + table
        + """

## What stays the same

The store workflow, hosted MCP URL, server-side tool schemas, shared skill, customer ownership checks and order-state rules. The protocol does not require rebuilding the business service for each listing. The plugin file formats and platform review/setup requirements differ.

## What belongs outside public plugin files

Reviewer credentials, OAuth client secrets, production tokens, databases and customer data. Deployment, domain verification, sign-in, working privacy/support pages, actual host testing and publication happen outside the ZIP. Review material may be packaged where supported, but secrets use private portal fields.

## Changes worth pointing out in the code

- ChatGPT listing fields live under extensions.com.openai.interface.
- ChatGPT review cases and recording URL live under extensions.com.openai.review.
- ChatGPT release notes live under extensions.com.openai.publication.release_notes.
- The chosen ChatGPT MCP entry uses streamable-http and an OpenAI auth extension; Claude uses http in .mcp.json. These are configuration dialects for the remote MCP connection, not different store APIs.
- Claude's plugin folder is the submitted repository subfolder, not the entire workshop repository. Its remote server also needs the connector route.

See SOURCES.md for official references and REPLACE-BEFORE-SUBMIT.md for the actual release work. Local checks do not establish acceptance or commerce eligibility.
""",
    )
    write(
        OUT / "PRESENTING.md",
        """# A three-minute first-person walkthrough

## 0:00 — One server, different distribution

“This is still Maya's store. I haven't rebuilt the store three times. I have the same hosted MCP interface, but each directory asks me to describe and deliver it differently. The .example address makes this an inspectable teaching sample.”

## 0:30 — Open the ChatGPT ZIP

“I'll open plugin.json. Here is the identity, the listing, and the review evidence. Notice the five positive and three negative cases. Release notes are under publication. In mcp.json, I point to the hosted server and declare the OAuth setup. The client ID is public configuration; the secret is entered privately. Uploading this ZIP doesn't deploy the server.”

## 1:20 — Switch to Claude

“Now look at the hidden .claude-plugin/plugin.json and .mcp.json files. The skill is the same. I submit a GitHub repository and plugin path, rather than this ZIP. That ZIP is just an export for us to inspect. For the hosted server, the connector route asks for the URL, sign-in and listing details.”

## 2:00 — Show the evidence

“These are real outputs from our fictional local fixture: successful search, quote, order, status and cancellation; plus three requests that must not succeed. This proves the lesson ran. It doesn't prove that a marketplace or production OAuth accepted it. I'd rerun the cases in the target app with the review account and record that experience.”

## 2:40 — Show what must change

“I replace the placeholder endpoint, policies and recording, configure real authentication, verify the publisher and permitted commerce flow, and finish the portal's checks. The package is one artifact in submission. A reviewed, live customer experience requires the service and the evidence too.”
""",
    )
    write(
        OUT / "REPLACE-BEFORE-SUBMIT.md",
        """# Replace before a real submission

- Replace every https://store.example URL with your working service, docs, website, support, privacy, terms and reviewer-accessible recording links. Replace support@store.example. These are intentionally non-working fixtures.
- Replace the sample OAuth client ID/endpoints/scopes with the real provider's configuration, implement and test the actual flow, and register the host's redirect URI. Enter secrets through private platform setup.
- Verify the publishing identity, repository rights and relevant platform account permissions. Choose the real directory category from the current portal.
- Export tool definitions from the deployed server, confirm hints match side effects, and test every operation with the reviewer account. Rerun and record target-app tests; the captured local stdio run is insufficient.
- Complete data-handling, privacy/support pages and API ownership disclosures. Verify permitted checkout and cancellation/refund behavior separately for each platform.
- ChatGPT: upload the individual sample-shaped plugin ZIP after replacing fixtures; complete domain/auth/scans, review details, review and publication.
- Claude plugin: place only the native plugin folder in a clean repository/subfolder; connect GitHub with push rights, validate the selected commit, and follow the portal. The repo must be public before it goes live. Also submit the remote server as a connector.
- Claude connector: use the portal worksheet as a checklist, not an import file. Configure the real HTTPS URL, OAuth, listing and reviewer access. Follow the actual status and any review/verification requirement.

Do not upload the complete presenter-kit ZIP as a plugin. No deployment, public endpoint, live auth, completed video, private credentials, portal scan or approval is included here.
""",
    )
    write(
        OUT / "SOURCES.md",
        "# Official references\n\nChecked November 3, 2026. These define the routes and configuration; the worksheets in this kit are our own teaching format.\n\n"
        + "\n".join(f"- [{name}]({url})" for name, url in SOURCES.items())
        + "\n",
    )
    shutil.copy2(ROOT.parent / "LICENSE", OUT / "LICENSE")
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
            "Five positive/three negative scenario counts and captured fixture outputs",
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
            "Hosted HTTPS/OAuth or target-app conversation tests",
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
    assert len(result) == 8 and sum(x["expected_error"] for x in result) == 3
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
