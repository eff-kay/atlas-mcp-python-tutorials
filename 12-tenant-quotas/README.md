# 12 · Bound tenant consumption

**One concept:** Use an atomic per-tenant budget that persists across server processes.

**Atlas story:** North must not consume Harbor’s allowance. This maps to talk stage **S7**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 12-tenant-quotas/demo.py
```

Or, after setup, `cd 12-tenant-quotas` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

North’s fourth read is limited; Harbor still reads successfully.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Restart with the same database and verify the limit persists until its window resets.

## What this does—and does not—provide

A fixed-window read budget is not a complete distributed queue or global capacity control. The tenant is trusted local fixture context. Counters are internal admission state; the business tool remains a read.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Recover an ambiguous write](../11-idempotency/) · Next: [Prepare reproducible review evidence](../13-review-evidence/)
