# Place one confirmed order

**One concept:** Persist a quote and create an order once, with an idempotency key.

From the repository root:

```sh
uv sync --locked --python 3.12
uv run python store/03-place-order/demo.py
```

No earlier lesson needs to be running. The demo starts its own server, makes actual SDK calls and exits nonzero if a promised outcome fails. Temporary databases and local servers are cleaned up. Repeating the demo starts fresh.

Read server.py first, then demo.py. This lesson never imports another lesson's server. The root workshop.py is client plumbing only.

## Expected behavior

Persist a quote and create an order once, with an idempotency key. The demo prints expected denials alongside successful calls. An error in a denied scenario is success for that check.

## Teaching boundary

The customer is a trusted local process fixture, not a tool argument or production identity. Lesson 05 demonstrates verified HTTP identity. No real addresses, orders, charges, refunds or cancellations occur. A confirmed=True argument represents approval supplied by a trusted caller; it cannot prove a human approved in an untrusted client. Production authorization and host checkout policies must be enforced separately. The $79 + $12 = $91 fixture includes tax, and Friday is an illustration, not a delivery promise.

## Try it

Change the demo request to exercise a no-match, an unconfirmed action or an order owned by a different fixture customer, depending on the lesson. Keep assertions consistent with the behavior you intend to demonstrate.
