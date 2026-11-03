# TrailShop: the talk's ecommerce walkthrough

One store exposes its catalog and order system, backed by a fictional address/distance service and courier quote provider. A shopper finds a blue carry-on, reviews a $91 quote, places a simulated order and cancels it if eligible.

For a single server to use from Codex during the call, start with the [combined local plugin demo](codex-demo/README.md). It includes the provider-backed quote and order lifecycle in one example.

These six independent lessons match the talk; the original 14 documentation lessons remain at the repository root.

| Lesson | What to run | What it proves |
|---|---|---|
| [Find the blue carry-on](01-catalog/) | `uv run python store/01-catalog/demo.py` | Discover and call one read-only product search. |
| [Coordinate independent providers](02-address-and-delivery/) | `uv run python store/02-address-and-delivery/demo.py` | Resolve a fixture address/distance over HTTP, then request a delivery quote. |
| [Place one confirmed order](03-place-order/) | `uv run python store/03-place-order/demo.py` | Persist a quote and create an order once, with an idempotency key. |
| [Cancel an eligible order](04-cancel-order/) | `uv run python store/04-cancel-order/demo.py` | Check ownership and dispatch state; preserve the cancellation result. |
| [Verify the shopper over HTTP](05-authenticated-http/) | `uv run python store/05-authenticated-http/demo.py` | Derive the customer from a verified token and enforce read/write scopes. |
| [Prepare marketplace evidence](06-review-evidence/) | `uv run python store/06-review-evidence/demo.py` | Run five positive and three negative store scenarios and export evidence. |

The first two lessons isolate search and real loopback provider calls. Later transaction lessons use an internal fixture quote to isolate order behavior; they do not depend on provider processes. Lesson 05 uses a real HTTP MCP server with verified customer/scopes. All transactions are simulated local state. OAuth sign-in, payment processing, production hosting and marketplace approval are outside these runnable labs.

Run every store lesson with `uv run python store/run_demos.py`. For marketplace package examples, see [publication](../publication/README.md).
