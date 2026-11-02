# 11 · Recover an ambiguous write

**One concept:** Atomically commit a document revision and its operation outcome in SQLite.

**Atlas story:** p42 must recover the same publish after a failed acknowledgement and server restart. This maps to talk stage **S6**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 11-idempotency/demo.py
```

Or, after setup, `cd 11-idempotency` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

Injected post-commit failure; retry returns r18, not r19; different payload under p42 is rejected.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Use a new key with the current base revision for a genuinely new operation.

## What this does—and does not—provide

lose_ack is an explicit fault-injection switch, not a real dropped network packet. This fixed editor/tenant fixture omits login. Production keys need actor/action/target binding and retention; external effects need reconciliation.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Work that survives disconnects](../10-durable-jobs/) · Next: [Bound tenant consumption](../12-tenant-quotas/)
