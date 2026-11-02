# 06 · Authorization code + PKCE

**One concept:** Discover the resource and issuer, explicitly approve a fixture consent, exchange a single-use code, and call MCP.

**Atlas story:** Connect the client, issuer and protected Atlas endpoint without asking for a pasted user credential. This maps to talk stage **S3**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 06-oauth-pkce/demo.py
```

Or, after setup, `cd 06-oauth-pkce` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

The MCP call succeeds; code replay, wrong PKCE proof and an unregistered redirect fail.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Use the issuer consent page code to inspect which fields are bound to the request handle.

## What this does—and does not—provide

Local issuer only: one fictional user, pre-registered client, no real login, refresh, DCR, key rotation or production session management. HTTP is allowed only on loopback.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Verify a resource-bound token](../05-token-verification/) · Next: [Authorize the object](../07-tenant-isolation/)
