# 09 · Observe outcomes without raw chats

**One concept:** Write allowlisted JSON events for success and a simulated dependency failure.

**Atlas story:** HTTP/RPC completion and useful execution are different signals. This maps to talk stage **S5**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 09-observability/demo.py
```

Or, after setup, `cd 09-observability` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

Two internal events, ok and tool_error; raw query absent; trace ID absent from model result.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Add a bounded error category; avoid adding request inputs or tokens.

## What this does—and does not—provide

This is a minimal structured telemetry exercise, not a complete OpenTelemetry deployment or end-user satisfaction measurement.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Publish with a revision precondition](../08-safe-publishing/) · Next: [Work that survives disconnects](../10-durable-jobs/)
