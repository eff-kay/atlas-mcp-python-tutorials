# 07 · Authorize the object

**One concept:** Derive the tenant from validated token claims, not a tool argument.

**Atlas story:** Maya can read North; knowing Harbor’s document ID is insufficient. This maps to talk stage **S3**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 07-tenant-isolation/demo.py
```

Or, after setup, `cd 07-tenant-isolation` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

North succeeds. Harbor and unknown IDs receive the same denial.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Mint a Harbor fixture token and reverse the allowed/denied requests.

## What this does—and does not—provide

The fixture client knows the signing key only to exercise the lab. In production only the trusted issuer mints claims; tools never accept raw identity claims as authority.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Authorization code + PKCE](../06-oauth-pkce/) · Next: [Publish with a revision precondition](../08-safe-publishing/)
