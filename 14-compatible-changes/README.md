# 14 · Keep old callers working

**One concept:** Add a new optional field while continuing to accept the old request shape.

**Atlas story:** A deployed server can change while a host retains its published schema. This maps to talk stage **S9**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 14-compatible-changes/demo.py
```

Or, after setup, `cd 14-compatible-changes` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

Old and new calls both return public-v2; folder is not required.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Make folder required and see why the old-contract check fails.

## What this does—and does not—provide

A local demonstration of compatibility, not a simulation of any platform’s review backend. Keep semantic behavior compatible too.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Prepare reproducible review evidence](../13-review-evidence/) · Next: [Talk slides](https://eff-kay.github.io/talks/mcp/)
