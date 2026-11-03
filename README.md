# Runnable MCP tutorials: ecommerce store + Atlas

[![Run the lessons](https://github.com/eff-kay/atlas-mcp-python-tutorials/actions/workflows/lessons.yml/badge.svg)](https://github.com/eff-kay/atlas-mcp-python-tutorials/actions/workflows/lessons.yml)


## Start with the ecommerce talk

The current talk uses **one store**, a catalog, an address/distance provider, a delivery quote, a confirmed order and a cancellation. Start with the [six independent store lessons](store/README.md); all calls use real MCP SDK connections and local fixtures, without real transactions.

```sh
uv sync --locked --python 3.12
uv run python store/01-catalog/demo.py
uv run python store/02-address-and-delivery/demo.py
uv run python store/04-cancel-order/demo.py
```

Read [marketplace package examples](publication/README.md) to inspect five ZIP layouts and platform-specific submission routes. These are labeled example packages; production endpoint/auth, real listing materials and host review remain required.

The original 14 documentation tutorials below are preserved as a separate learning track. `run_all_demos.py` runs all 20 lessons.

**One concept per folder. A real server, a runnable client, and a result you can inspect.**

These tutorials accompany [Faizan Khan’s MCP talk](https://eff-kay.github.io/talks/mcp/). They follow **Atlas Docs**, a fictional documentation product, as Maya’s request grows from “find the v2 guide” into a hosted, authorized, observable and reviewable integration.

You can start any lesson directly. No earlier lesson needs to be running. No model subscription, API key, real customer data or external service is required. HTTP examples use loopback only; all credentials and identities are generated local fixtures.

## Get something working

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
git clone https://github.com/eff-kay/atlas-mcp-python-tutorials.git
cd atlas-mcp-python-tutorials
uv sync --locked --python 3.12
uv run python 01-smallest-server/demo.py
```

You should see the discovered `get_guide` tool and its v1 fixture. That result is deliberately insufficient for a v2 question—the next lesson fixes the contract.

Try the next concept:

```sh
uv run python 02-versioned-search/demo.py
```

Or run all the learner-facing demos:

```sh
uv run python run_all_demos.py
```

The runner stops each server, records a nonzero exit if a promised outcome fails, and uses temporary state for mutable examples. It prints successful behavior and expected denials. Random IDs and ports vary.

Python **3.11+** is required. The lockfile pins official **MCP Python SDK 2.3.0** and all resolved dependencies. This is SDK v2 (`MCPServer`, `Client`), not the older FastMCP/v1 API. If you prefer pip, create a Python 3.11+ virtual environment and install `requirements.txt`; run the same scripts with that environment’s `python`.

## Choose a concept

| Folder | One concept | What you see |
|---|---|---|
| [01-smallest-server](01-smallest-server/) | A tool over stdio | Discovery and one actual call |
| [02-versioned-search](02-versioned-search/) | Version-aware retrieval | Search v2, fetch source evidence |
| [03-validation-and-errors](03-validation-and-errors/) | Schema versus domain errors | Valid no-match and explicit failures |
| [04-streamable-http](04-streamable-http/) | HTTP transport | Real local server and client |
| [05-token-verification](05-token-verification/) | Resource-bound token checks | Missing, expired, wrong-audience and wrong-scope denials |
| [06-oauth-pkce](06-oauth-pkce/) | Authorization-code + PKCE | Discovery, consent, code exchange and protected call |
| [07-tenant-isolation](07-tenant-isolation/) | Object authorization | North can read North, not Harbor |
| [08-safe-publishing](08-safe-publishing/) | Revision preconditions | r17 → competing r18 → reviewed r19 |
| [09-observability](09-observability/) | Useful, minimized telemetry | Success/error records without raw query capture |
| [10-durable-jobs](10-durable-jobs/) | Work surviving disconnect | Persist, run a worker, restart, poll result |
| [11-idempotency](11-idempotency/) | Recover a committed operation | Same key returns original outcome after restart |
| [12-tenant-quotas](12-tenant-quotas/) | Admission fairness | North’s limit does not consume Harbor’s allowance |
| [13-review-evidence](13-review-evidence/) | Replayable review material | Tool inventory, five positive/three negative scenarios, evidence ZIP |
| [14-compatible-changes](14-compatible-changes/) | Compatible contract rollout | Old and new callers both work |

Each README explains the goal, run command, expected behavior, a small exercise, boundaries and the next lesson. Each server owns its behavior and fixtures. `workshop.py` is only shared demo plumbing; servers do not import earlier lessons.

## Use a real host

The demos use the official Python client instead of an LLM, so you can inspect deterministic behavior first. To inspect lesson 01 interactively:

```sh
uv run mcp dev 01-smallest-server/server.py
```

The Inspector needs Node.js and `npx`. A host that supports launching stdio programs can also use this configuration after replacing the example checkout path and locating `uv` on that machine:

```json
{
  "mcpServers": {
    "atlas-smallest": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/atlas-mcp-python-tutorials", "run", "--locked", "python", "01-smallest-server/server.py"]
    }
  }
}
```

Host formats and supported protocol revisions vary. This SDK supports the current protocol; confirm your host’s compatibility. Terminal `python server.py` on a stdio lesson waits for a client—silence is normal, not a failure.

## Where the teaching boundaries are

- **05** validates ephemeral fixture JWTs. **06** separately implements a local pre-registered authorization-code/PKCE flow with explicit fixture consent. It is not a production identity provider: there is no real login, refresh, DCR, key rotation or public TLS service.
- **07** derives tenant identity from validated signed claims. The local demo knows the signing secret to manufacture scenarios; real clients do not mint their own trusted identity.
- **08, 10–12** use trusted process configuration for the fixture role/tenant so each lesson stays focused. That configuration is not an authentication mechanism for untrusted clients. Compose with a real authenticated context before deployment.
- **10** uses explicit application job tools, not the optional MCP Tasks extension. **11** deliberately injects a post-commit failed acknowledgement, rather than pretending to drop a real network packet.
- **13** creates review **evidence**, not an upload-ready plugin or an approval guarantee. Public hosting, supported auth, platform manifests, ownership, private reviewer access, policy and manual submission remain separate requirements.

The examples demonstrate specific boundaries, not a complete production system. Source URLs under `.example` are fictional and are not fetched. All write operations affect local fixture databases only.

## Development and repeatability

```sh
uv sync --locked --python 3.12
uv run ruff check --select F .
uv run ruff format --check .
uv run python run_all_demos.py
```

GitHub Actions runs the same demos on Python 3.11 and 3.12. The dependency lock is committed; generated databases, logs, credentials and review output are ignored. Manual server exercises may create local state; use a fresh `ATLAS_DB` file for a fresh fixture. Demo scripts clean up their own temporary files and processes.

## Read alongside the talk

- [Atlas walkthrough](https://eff-kay.github.io/talks/mcp/)
- [Broader visual field guide](https://eff-kay.github.io/talks/mcp/field-guide.html)
- [Official references and version notes](REFERENCES.md)

Built by Faizan Khan, founder of Docsalot. Atlas and its users are fictional teaching examples. MIT licensed.
