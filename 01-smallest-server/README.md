# 01 · The smallest MCP server

**One concept:** Register and discover one read-only tool over stdio.

**Atlas story:** A host can call Atlas, but a single v1 fixture cannot answer Maya’s v2 question. This maps to talk stage **S0**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 01-smallest-server/demo.py
```

Or, after setup, `cd 01-smallest-server` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

Discovered: ['get_guide']; the returned guide identifies v1.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Change the returned fixture and rerun the client. Then ask what this still cannot answer.

## What this does—and does not—provide

stdout carries protocol messages; use logging/stderr while serving.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Repository guide](../README.md) · Next: [Versioned retrieval](../02-versioned-search/)
