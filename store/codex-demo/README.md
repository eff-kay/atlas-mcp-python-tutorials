# One local store, connected to Codex as a plugin

This is the combined example for the talk: one persistent MCP server, five tools, two resources and one prompt. The quote tool makes actual HTTP calls to two separate loopback fixture endpoints. No external provider or real checkout is contacted.

## Start it

From the repository root:

```sh
uv sync --locked --python 3.12
uv run python store/codex-demo/manage.py start
```

The manager starts a detached demo process and returns. That process serves all three loopback listeners:

| Endpoint | Role |
|---|---|
| `http://127.0.0.1:8767/mcp` | Streamable HTTP MCP endpoint for Codex |
| `http://127.0.0.1:8768/route` | GeoRoute address/distance fixture API |
| `http://127.0.0.1:8769/quote` | ParcelQuote shipping fixture API |

Codex desktop can connect to loopback HTTP; HTTPS and a public tunnel are unnecessary for this setup. A remote/cloud Codex runtime cannot reach a server on your laptop via its own loopback address.

## Install the actual Codex plugin

From the repository root, once:

```sh
codex plugin marketplace add .
codex plugin add trailshop-local@docsalot-mcp-workshop
codex plugin list --marketplace docsalot-mcp-workshop --json
```

Open a **new Codex chat** after installation so the plugin's tools are loaded. Look for **Trailshop Local Demo** in the plugin picker if needed. Installation uses the local marketplace, not a public marketplace submission. It does not enable a tunnel, auto-approval setting or an OS login service.

The plugin contains `.codex-plugin/plugin.json` and `.mcp.json`. Its MCP configuration points to port 8767. The server must be running before the host connects. All existing six lessons are still independent.

## Demo in a Codex conversation

Send these separately; allow the assistant to show the quote before confirming:

1. **Find me a blue carry-on backpack under $100 total, delivered by Friday to my saved `demo-home` address. Use the Trailshop Local Demo tools. Show me the quote and wait before placing an order.**
2. After reviewing the $91 quote: **Yes, place that simulated order.**
3. **Show me the order status.**
4. **Cancel that simulated order.** Confirm if asked.
5. Optional: **Try cancelling `demo-shipped` and explain why it fails.**

The product costs $79; shipping is $12; the $91 fixture total includes tax. Delivery is a fictional Friday estimate. Quotes expire after **120 seconds**; ask for a new quote if necessary. The server returns generated quote/order IDs—use those IDs instead of the fixed IDs from a slide.

| Capability | How to explain it |
|---|---|
| `search_products` | Read one in-stock blue backpack fixture; other colors produce no match |
| `quote_delivery` | GeoRoute `/route` → ParcelQuote `/quote` → persist Maya's quote |
| `place_order` | Check confirmation/quote and persist exactly one simulated order per quote |
| `get_order` | Read Maya's stored order state |
| `cancel_order` | Cancel only an owned, not-dispatched order |
| `trailshop://policies/returns` | Readable cancellation policy resource |
| `trailshop://guides/carry-on` | Readable carry-on size guide resource |
| `shop_for_maya` | A reusable starting prompt; host display/support varies |

## Validate without an LLM

Against the running server:

```sh
uv run python store/codex-demo/validate.py
uv run python store/codex-demo/validate.py --transactions
```

The first validates discovery, resources/prompt, search and provider-backed quotation. The second also writes and cancels a simulated order, tests retry idempotency, prevents quote reuse and rejects other-customer/dispatched orders. It never places a real purchase. For an isolated server and temporary state, run:

```sh
uv run python store/codex-demo/demo.py
```

## State, logs and shutdown

```sh
uv run python store/codex-demo/manage.py status
uv run python store/codex-demo/manage.py stop
```

State is stored at `~/.local/state/trailshop-codex/`: `store.sqlite3`, `server.log` and `process.json`. Restarting preserves orders. The manager checks the process command before stopping it. It does not start on OS login; rerun `start` after reboot. To uninstall the plugin:

```sh
codex plugin remove trailshop-local@docsalot-mcp-workshop
```

## Scope of this local fixture

The shopper is fixed to fictional Maya. There is **no production authentication**; loopback-only access is the demo boundary, and any local client can act as this fixture customer. `confirmed: true` is a caller flag, not independent proof of human consent. Use the host's confirmation experience for the live presentation. The authenticated-HTTP lesson shows token/subject/scope checks separately. No real addresses, money, orders or refunds exist. The state machine and idempotency examples are real local code, not production payment guarantees.

The installed Codex CLI's own help, generated app-server schema and bundled `.codex-plugin`/`.agents/plugins` examples were used to verify this native plugin layout. Codex's actual MCP client discovered all five tools and both resources from the installed plugin over HTTP during setup.
