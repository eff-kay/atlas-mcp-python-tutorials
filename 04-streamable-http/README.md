# 04 · A remote-capable transport

**One concept:** Serve the same kind of tool over actual loopback HTTP.

**Atlas story:** A teammate can connect without a stdio subprocess in their host. This maps to talk stage **S2**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 04-streamable-http/demo.py
```

Or, after setup, `cd 04-streamable-http` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

A temporary HTTP endpoint responds with the v2 guide.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

For two terminals, start the server from the repository root:

```sh
uv run python 04-streamable-http/server.py
```

Then run the client in another terminal:

```sh
uv run python 04-streamable-http/client.py
```

The server binds only to `127.0.0.1:8000`; override `PORT` for a different local port.

## Try one change

Run server.py manually, then call client.py in another terminal.

## What this does—and does not—provide

Loopback HTTP is a local development endpoint, not public hosting, TLS, auth, or a directory listing.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Schemas and honest errors](../03-validation-and-errors/) · Next: [Verify a resource-bound token](../05-token-verification/)
