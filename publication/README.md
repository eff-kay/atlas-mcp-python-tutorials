# What belongs in a marketplace package?

These are **inspectable sample packages for the same TrailShop ecommerce example**. They use a fictional `.example` endpoint and are named `EXAMPLE.zip` deliberately. They are not deployed integrations, approved listings or upload-ready production releases.

## Presentation showcase

Open [the sample submission showcase](showcase/index.html) for a side-by-side file viewer. [Download the complete presenter kit](showcase/trailshop-submission-showcase.EXAMPLE.zip), or read [DIFFERENCES.md](showcase/DIFFERENCES.md) and [the three-minute walkthrough](showcase/PRESENTING.md). It compares ChatGPT ZIP, Claude GitHub plugin and Claude URL connector routes, with captured fixture evidence and an explicit replacement checklist.

Rebuild the showcase with `uv run python publication/build_showcase.py`. The captured inputs under `showcase-inputs/` are dated local fixture outputs; the builder does not run or submit a server.

## Other ecosystem profiles

Build and inspect them:

```sh
uv run python publication/build_packages.py
```

| Target | Files in the plugin folder | How it is submitted/distributed |
|---|---|---|
| Portable Agent Plugin | `plugin.json`, `mcp.json`, optional `skills/`, `assets/`, README and license | Starting format supported by several hosts; individual host requirements still apply |
| ChatGPT | Root manifests above, with documented OpenAI metadata/auth extensions | Upload ZIP to Plugins; complete publisher, domain, OAuth, scans, review evidence and publication |
| Claude | `.claude-plugin/plugin.json`, `.mcp.json`, optional `skills/`, assets, README and license | Current plugin portal takes a GitHub repository/branch/path. Your remote MCP server also has its own connector submission |
| Cursor | `.cursor-plugin/plugin.json`, `mcp.json`, optional skills/assets/docs | Submit a tested public repository to the Cursor marketplace; ZIP is an export |
| Factory | `.factory-plugin/plugin.json`, `mcp.json`, skills/docs | Register a Git marketplace containing `.factory-plugin/marketplace.json`; official curation is separate |
| Hermes | Portable Agent Plugin + catalog entry | Validate with Hermes, then propose a catalog YAML pinned to a reviewed 40-character commit; sample entry included separately |
| Muse | Hosted MCP/API details, docs, business/data questionnaire and review access | Connector intake, not a verified generic plugin-ZIP interface. Sample intake JSON included |
| Instinct | Not established | The user confirmed instinct.com. No public MCP/plugin submission route was verified; do not treat its logo as an open intake |

The ZIPs are in `publication/dist/`; the unpacked folders beside them make every file easy to inspect. `validation-report.json` names the scope of local checks. No host CLI or public portal approval is claimed.

## One real package to learn from

Anthropic's own documentation recommends the **productivity** plugin as a compact example of the directory format:

- [Official plugin source](https://github.com/anthropics/knowledge-work-plugins/tree/2574e29377c7173d0cecffef29a6ecbd7f8ccb5d/productivity)
- [Official structure guide identifying that example](https://claude.com/docs/plugins/build)

It has `.claude-plugin/plugin.json`, `.mcp.json`, skills and documentation. Copy the structure, not another publisher's identities, credentials, branding or tool claims. We inspected its actual manifests; the store examples here are original. OpenAI's [package guide](https://developers.openai.com/plugins/build/plugins) and [official Figma bundle](https://github.com/openai/plugins/tree/main/plugins/figma) provide the corresponding OpenAI reference, though the Figma bundle has additional platform-specific components.

## Make a real release candidate

Copy `release.example.json` to a private configuration file outside the public repository. Set the actual HTTPS endpoint, website, support, privacy/terms URLs, walkthrough URL and repository. Complete `RELEASE-CHECKLIST.md`, then set `review_ready` and run:

```sh
uv run python publication/build_packages.py --config /absolute/path/to/release.json --release
```

Release mode rejects fixture/private IP URLs and missing readiness acknowledgement. This is a local packaging gate, not a reachability test or platform approval. Authenticated endpoints must really implement the authorization flow. The Python labs' self-minted tokens are not a production OAuth provider. The server is hosted separately; do not upload the `.venv`, SQLite database or local lab process as a hosted service.

### Important schema distinction

The strict Agent Plugins 1.0 MCP schema does not declare OpenAI's documented per-server `extensions.com.openai.auth` field. We validate the portable base against the upstream schema and separately check the documented host extension. We do **not** claim the extended file passes the unmodified strict portable schema. Run the actual target-host validators and portal scans before release. Claude, Cursor and Factory examples receive structural/path checks locally; their native host validators were not run.

## Keep out of the ZIP

No bearer tokens, API keys, OAuth client secrets, reviewer passwords, `.env`, databases, raw customer data, node_modules or virtual environment. Reviewer access belongs in the platform's secure submission fields. A domain challenge token is served on your host; it is not a substitute for DNS/hosting control and not a reason to embed credentials.

The bundled Docsalot icon is a brand asset used for this author's teaching example; the repository MIT license does not grant third-party rights to the Docsalot trademark.

Checked November 3, 2026. See `SOURCES.md` and `ecosystem-routes.md`. No directory submission was made.

The installed Hermes CLI in this authoring environment did not expose the current documented `plugins validate` command, so native Hermes validation was not completed. The portable schema checks passed; use a suitable Hermes version and the reviewed catalog flow before claiming Hermes compatibility.
