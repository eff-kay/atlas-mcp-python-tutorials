# Verify the shopper over HTTP

**One concept:** Derive the customer from a verified token and enforce read/write scopes.

From the repository root:

```sh
uv sync --locked --python 3.12
uv run python store/05-authenticated-http/demo.py
```

No earlier lesson needs to be running. The demo starts its own server, makes actual SDK calls and exits nonzero if a promised outcome fails. Temporary databases and local servers are cleaned up. Repeating the demo starts fresh.

Read server.py first, then demo.py. This lesson never imports another lesson's server. The root workshop.py is client plumbing only.

## Expected behavior

Derive the customer from a verified token and enforce read/write scopes. The demo prints expected denials alongside successful calls. An error in a denied scenario is success for that check.

## Teaching boundary

This is a loopback resource-server lab with ephemeral self-minted JWTs. It verifies tokens; it does not implement an OAuth sign-in provider, production hosting, checkout or actual payments. The earlier 06-oauth-pkce lesson explains the separate sign-in mechanics. No real addresses, orders, charges, refunds or cancellations occur. A confirmed=True argument represents approval supplied by a trusted caller; it cannot prove a human approved in an untrusted client. Production authorization and host checkout policies must be enforced separately. The $79 + $12 = $91 fixture includes tax, and Friday is an illustration, not a delivery promise.

## Try it

Change the demo request to exercise a no-match, an unconfirmed action or an order owned by a different fixture customer, depending on the lesson. Keep assertions consistent with the behavior you intend to demonstrate.
