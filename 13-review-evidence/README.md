# 13 · Prepare reproducible review evidence

**One concept:** Discover actual tool metadata and execute five positive/three negative fixture scenarios.

**Atlas story:** Give a reviewer the same product journey, not a disconnected marketing demo. This maps to talk stage **S8**.

## Run it

From a fresh checkout, do the one-time setup in the repository root:

```sh
uv sync --locked --python 3.12
```

Run just this lesson, without running any earlier lesson:

```sh
uv run python 13-review-evidence/demo.py
```

Or, after setup, `cd 13-review-evidence` and run `uv run python demo.py`. The demo starts its own server, uses the actual SDK client, checks the outcomes below, and shuts down. Stateful demos use temporary SQLite files, so repeating a demo starts clean. No model subscription, API key, real customer account or external service is needed.

## What you should see

output/ contains inventory, observed outcomes and review-evidence.zip.

The demo exits nonzero if its documented outcome fails. Port numbers, trace identifiers and job IDs vary.

## Read the code

Start with `server.py`, then `demo.py`. The server never imports another lesson. `../workshop.py` contains only shared demo plumbing: subprocess setup, temporary HTTP server cleanup, result display and failure reporting. Each folder owns its domain behavior and fixtures.

`scenarios.json` defines the prompts, tool arguments and observable expectations. The ZIP contains only the inventory and results. A real directory application still needs a public service, appropriate auth, publishing identity, listing/privacy/support material, private reviewer access and the current platform-specific package. See the [OpenAI submission guide](https://developers.openai.com/plugins/deploy/submission) and [Claude submission guide](https://claude.com/docs/connectors/building/submission).

## Try one change

Break a hint or scenario expectation, rerun, and inspect the actionable failure.

## What this does—and does not—provide

This is evidence preparation, not a compliant platform plugin manifest, deployed OAuth service, submission, or approval guarantee. No credentials belong in this archive. Verify current platform rules.

The examples are hypothetical. `*.atlas.example` addresses are evidence placeholders and are not fetched. Manual server runs may create local state files; `.gitignore` excludes these files. Remove only your generated state to reset a manual exercise.

## Continue

Previous: [Bound tenant consumption](../12-tenant-quotas/) · Next: [Keep old callers working](../14-compatible-changes/)
