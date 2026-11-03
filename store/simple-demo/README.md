# Two-function MCP demo

One file, two ordinary synchronous Python functions, logs printed in the same terminal. All data is fictional. No orders, database, external APIs, background workers or custom async code.

From this folder:

```sh
uv run python server.py
```

Or, with the repository virtual environment already activated, run `python server.py`.

Connect a local MCP client to `http://127.0.0.1:8770/mcp` and ask:

> Find a blue carry-on backpack and tell me the total including delivery. Use search_products and quote_delivery.

Expected calls: search_products(color="blue"), then quote_delivery(product_id="backpack"). Expected total: $91 USD. The terminal prints each call and its result. Ctrl-C stops the server. The MCP SDK handles the network transport internally; neither tool uses async/await.

A cloud custom-plugin dialog still needs a reachable HTTPS endpoint or tunnel; this loopback URL is for local clients.
