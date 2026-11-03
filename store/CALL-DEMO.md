# TrailShop call walkthrough

From the repository root:

```sh
uv sync --locked --python 3.12
```

1. `uv run python store/01-catalog/demo.py` — discover search and find the $79 blue carry-on. A green search returns no matches.
2. `uv run python store/02-address-and-delivery/demo.py` — the store calls two separate loopback API processes: GeoRoute returns 12 km; ParcelQuote returns $12 and a fictional Friday estimate. The total is $91. An unknown address fixture fails.
3. `uv run python store/03-place-order/demo.py` — unconfirmed checkout fails. Confirmation creates a simulated order. Restarting and retrying the same key returns the same order.
4. `uv run python store/04-cancel-order/demo.py` — cancel the owned order and repeat safely. Another shopper's order and a dispatched order are denied.
5. `uv run python store/05-authenticated-http/demo.py` — no token/wrong audience fail, a read-only token cannot purchase, write scope permits the simulated action, and a different authenticated shopper cannot read the order.
6. `uv run python store/06-review-evidence/demo.py` — five positive and three negative cases export review evidence.

For the shorter talk, demonstrate 02 and 04; the slides cover the rest. The demo scripts make real MCP calls, but no LLM selects the tools. The local state is deliberately simulated and temporary. Friday, tax-inclusive totals, stock, distance and addresses are teaching fixtures. `confirmed=True` is not an independent proof of a human's consent; production needs host controls and server authorization.

Package inspection:

```sh
uv run python publication/build_packages.py
unzip -l publication/dist/trailshop-chatgpt.EXAMPLE.zip
```

Show the manifest, MCP config, skill, assets, README and license. Contrast Claude/Cursor's repository intake with OpenAI's ZIP intake. The evidence ZIP from lesson 06 is not the installable plugin package.
