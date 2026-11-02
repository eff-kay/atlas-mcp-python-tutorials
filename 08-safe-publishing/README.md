# 08 · Publish with a revision precondition

**One concept:** Separate a read from an explicit write and atomically reject stale edits in SQLite.

**Atlas story:** Maya starts from r17; another editor publishes r18; Maya reviews again before r19. This maps to talk stage **S4**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 08-safe-publishing/demo.py
```

Or, after setup, `cd 08-safe-publishing` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

Reader denied; stale base rejected; reviewed update reaches r19.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Open a second editor against the same SQLite file and create a competing edit.

## What this does—and does not—provide

ATLAS_ROLE is trusted process fixture context, not HTTP auth. Compose with lesson 07 for a real identity boundary. No implicit host/user approval is implemented.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Authorize the object](../07-tenant-isolation/) · Next: [Observe outcomes without raw chats](../09-observability/)
