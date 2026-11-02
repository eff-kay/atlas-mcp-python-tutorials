# 02 · Versioned retrieval

**One concept:** Filter a local corpus before returning bounded source evidence.

**Atlas story:** Give Maya the v2 guide instead of whichever guide happens to exist. This maps to talk stage **S1**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 02-versioned-search/demo.py
```

Or, after setup, `cd 02-versioned-search` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

One v2 hit, followed by its source document.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

## Try one change

Search v1, change the query to unicorn, then try a URL as a document ID.

## What this does—and does not—provide

This tiny lexical matcher is a fixture, not a production search engine. No network fetch occurs.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [The smallest MCP server](../01-smallest-server/) · Next: [Schemas and honest errors](../03-validation-and-errors/)
