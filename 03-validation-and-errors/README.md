# 03 · Schemas and honest errors

**One concept:** Separate a valid no-match, invalid arguments, and unsupported domain input.

**Atlas story:** A completed RPC is not automatically a successful tool operation. This maps to talk stage **S1**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 03-validation-and-errors/demo.py
```

Or, after setup, `cd 03-validation-and-errors` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

No-match succeeds; limit=99 and version=v9 return tool errors.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Return a Pydantic model with an extra provenance field and inspect list_tools().

## What this does—and does not—provide

Generic dict returns are text JSON in these lessons; the Pydantic model here declares structured output. Always check is_error.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Versioned retrieval](../02-versioned-search/) · Next: [A remote-capable transport](../04-streamable-http/)
