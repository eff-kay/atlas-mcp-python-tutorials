# Open the talk with the live connection

Use three panes: editor, terminal logs, and a fresh local Codex session. The plugin is currently installed; remove it yourself before rehearsal if you want to demonstrate installation from scratch. Removing the plugin does not delete orders or stop the server.

## 1. Tour the folder first

Open `store/codex-demo/` and explain:

| File | What I say |
|---|---|
| `server.py` | “This is our store's MCP interface: five tools, two resources, one prompt. The decorator exposes each Python function.” |
| `providers.py` | “These are two local HTTP services: address-to-distance, then distance-to-shipping.” |
| `plugin/.codex-plugin/plugin.json` | “This names the plugin and points to its connection file.” |
| `plugin/.mcp.json` | “This tells Codex to connect to http://127.0.0.1:8767/mcp.” |
| `manage.py` | “This starts and stops the server. Installing the plugin alone doesn't run it.” |
| `validate.py` | “This checks the full MCP flow without an LLM.” |
| `telemetry.py` / `watch_logs.py` | “These record and display the tool and provider events we will watch.” |
| `demo.py` | “This runs an isolated check with temporary state and ports.” |

Show the `@mcp.tool` decorator and typed arguments in `server.py`, then the two HTTP calls in `quote_delivery`. Explain the order checks before making a quote, because quotes expire in 120 seconds.

## 2. Prepare the terminals

In both terminals, start in the repository:

```sh
cd /Users/faizank/workspace/experiments/live_projects/atlas-mcp-python-tutorials
```

Terminal A:

```sh
uv run python store/codex-demo/manage.py start
uv run python store/codex-demo/watch_logs.py
```

The watcher follows **new events only**, so previous validation orders won't clutter the presentation. Ctrl-C stops the watcher, not the server. To inspect recent history instead:

```sh
uv run python store/codex-demo/watch_logs.py --recent 20 --once
```

## 3. Connect in front of the audience

Optional preparation **before** the call, if you want a clean install demonstration:

```sh
codex plugin remove trailshop-local@docsalot-mcp-workshop
```

On stage, Terminal B:

```sh
codex plugin marketplace add .
codex plugin add trailshop-local@docsalot-mcp-workshop
codex plugin list --marketplace docsalot-mcp-workshop --json
```

The marketplace is already registered on this laptop; you can skip the first command if it is still registered. Show `installed: true` and `enabled: true`.

“This registers a local plugin source and installs the connection configuration. It is not a public marketplace submission.”

Then open a **new local Codex session** (run `codex` here, or open a fresh desktop chat that loads the local plugin). Existing conversations may retain their previous tool inventory. HTTP is supported in the tested native Codex client; a public HTTPS tunnel is unnecessary.

The clean event log records business tool calls, not the initial protocol handshake. To show connection/discovery traffic, use a separate terminal:

```sh
tail -n 0 -f /Users/faizank/.local/state/trailshop-codex/server.log
```

This raw SDK log can include probe requests, session identifiers and auth-discovery 404s for this unauthenticated local fixture. An address-bar GET is not a valid MCP tool call. Successful tool discovery/calls are the connection proof, not the absence of every 4xx probe.

## 4. Trigger the visible flow

Ask Codex:

> Use Trailshop Local Demo. Find a blue carry-on backpack under $100 total, delivered by Friday to demo-home. Show the quote and wait before ordering.

The clean log will show this pattern; IDs/times/durations vary:

```text
17:30:00  a1b2c3d4  tool.started       tool=search_products
17:30:00  a1b2c3d4  tool.succeeded     tool=search_products duration_ms=0 outcome=ok
17:30:01  e5f6a7b8  tool.started       tool=quote_delivery
17:30:01  e5f6a7b8  provider.request   provider=address path=/route status=200
17:30:01  e5f6a7b8  provider.request   provider=delivery path=/quote status=200
17:30:01  e5f6a7b8  tool.succeeded     tool=quote_delivery duration_ms=10 outcome=ok
```

“These three entries share a trace ID: one tool invocation has called two providers. Codex talks MCP to the store; the store still talks HTTP to its providers.”

Expand Codex's tool cards for actual arguments/results. The event log deliberately omits payloads and credentials. The displayed examples above illustrate the format, not measured timings.

The quote should show $79 + $12 = $91 USD, with a fictional Friday estimate. Then send:

> Yes, place that simulated order.

> Cancel that simulated order.

> Check its status again.

Show `tool.succeeded` with `outcome=placed`, then `outcome=cancelled`. A failed attempt, such as cancelling `demo-shipped`, shows `tool.failed`; expand the tool result to explain `ALREADY_DISPATCHED`.

Each tool invocation has its own trace ID; this is a small local demonstration logger, not full distributed tracing or production observability. All transactions are fictional and Maya's identity is fixed. Confirmation flags are not a production authorization system.

## 5. Rehearsal check and fallback

Before the audience arrives:

```sh
uv run python store/codex-demo/validate.py --transactions
```

Expect `PASS`. If the model demo is interrupted, this same command visibly exercises discovery, provider-backed quotation, purchase/retry, cancellation and denials over the real MCP HTTP transport. It proves the server path; it does not demonstrate LLM tool selection.

For the fuller conversation and code walkthrough, see [PRESENTING.md](PRESENTING.md).
