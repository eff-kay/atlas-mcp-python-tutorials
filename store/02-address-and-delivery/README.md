# Coordinate independent providers

**One concept:** Resolve a fixture address/distance over HTTP, then request a delivery quote.

From the repository root:

```sh
uv sync --locked --python 3.12
uv run python store/02-address-and-delivery/demo.py
```

No earlier lesson needs to be running. The demo starts its own server, makes actual SDK calls and exits nonzero if a promised outcome fails. Temporary databases and local servers are cleaned up. Repeating the demo starts fresh.

Read server.py first, then demo.py. This lesson never imports another lesson's server. The root workshop.py is client plumbing only.

This lesson starts two separate loopback fixture API processes. The MCP server calls GeoRoute first, then ParcelQuote over real HTTP. For manual server runs, start providers.py twice with PROVIDER=address / delivery and different PORT values, then pass ADDRESS_URL and DELIVERY_URL to server.py. demo.py handles that setup and cleanup automatically.

## Expected behavior

Resolve a fixture address/distance over HTTP, then request a delivery quote. The demo prints expected denials alongside successful calls. An error in a denied scenario is success for that check.

## Teaching boundary

All products, addresses, distances, delivery estimates and identities are fictional fixtures. No real addresses, orders, charges, refunds or cancellations occur. A confirmed=True argument represents approval supplied by a trusted caller; it cannot prove a human approved in an untrusted client. Production authorization and host checkout policies must be enforced separately. The $79 + $12 = $91 fixture includes tax, and Friday is an illustration, not a delivery promise.

## Try it

Change the demo request to exercise a no-match, an unconfirmed action or an order owned by a different fixture customer, depending on the lesson. Keep assertions consistent with the behavior you intend to demonstrate.
