# 05 · Verify a resource-bound token

**One concept:** Check signature, issuer, expiry, audience and required scope on HTTP requests.

**Atlas story:** Private docs need a real identity boundary. This maps to talk stage **S3**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 05-token-verification/demo.py
```

Or, after setup, `cd 05-token-verification` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

No token, wrong audience, expiry and missing scope are rejected; a valid fixture token works.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Change the issuer claim or signing key in the demo and observe rejection.

## What this does—and does not—provide

The demo mints ephemeral fixture tokens locally. This folder is a resource-server verification lab, not an OAuth sign-in flow.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [A remote-capable transport](../04-streamable-http/) · Next: [Authorization code + PKCE](../06-oauth-pkce/)
