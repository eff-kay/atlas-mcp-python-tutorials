# 10 · Work that survives disconnects

**One concept:** Persist a queued job, run an external worker, restart the MCP server, and poll owned state.

**Atlas story:** Reindexing cannot rely on an in-memory asyncio task surviving a request. This maps to talk stage **S6**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 10-durable-jobs/demo.py
```

Or, after setup, `cd 10-durable-jobs` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

The job remains after disconnect; a separate worker builds two index rows; restart returns completed.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

`server.py` durably queues work and serves status; `worker.py` processes one queued or expired-lease job. The index upsert and terminal result share a local transaction. A crash before completion leaves a lease that can expire; repeating the deterministic index operation is safe for this fixture. This is at-least-once work, not exactly-once external effects.

## Try one change

Run worker.py twice, inspect indexed_docs, or expire a working lease to observe a retry.

## What this does—and does not—provide

Application-defined start/status tools, not the MCP Tasks extension. Leases are deliberately small; long production jobs need renewal/fencing, quotas, and reconciliation. Fixture tenant context is local, not real authentication.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Observe outcomes without raw chats](../09-observability/) · Next: [Recover an ambiguous write](../11-idempotency/)
