# Store code excerpts

These are excerpts from the runnable lessons, not a separate server. Each linked folder contains its own complete server and demo. All orders and payments are simulated.

## Find a product

Source: [01-catalog/server.py](01-catalog/server.py)

```python
@mcp.tool(title="Search store products", annotations=READ)
def search_products(
    color: str = "blue", max_item_price_cents: Annotated[int, Field(ge=0)] = 10000
) -> dict:
    """Search this store's in-stock carry-on fixtures. Delivery is priced separately."""
    return {
        "products": [
            p
            for p in PRODUCTS
            if p["color"] == color
            and p["in_stock"]
            and p["price_cents"] <= max_item_price_cents
        ]
    }
```

## Address, distance and delivery

Source: [02-address-and-delivery/server.py](02-address-and-delivery/server.py)

```python
@mcp.tool(title="Quote store delivery", annotations=READ)
def quote_delivery(product_id: str, address_ref: str) -> dict:
    """Resolve a saved fixture address through GeoRoute, then quote ParcelQuote. No real address data."""
    if product_id != "blue-carryon":
        raise ToolError("Unknown product")
    try:
        with httpx.Client(trust_env=False, timeout=3) as http:
            route = http.post(
                os.environ["ADDRESS_URL"] + "/route", json={"address_ref": address_ref}
            )
            route.raise_for_status()
            r = route.json()
            delivery = http.post(
                os.environ["DELIVERY_URL"] + "/quote",
                json={"distance_km": r["distance_km"], "product_id": product_id},
            )
            delivery.raise_for_status()
            d = delivery.json()
        return {
            "product_id": product_id,
            "item_cents": 7900,
            "route": r,
            "delivery": d,
            "total_cents": 7900 + d["shipping_cents"],
            "currency": "USD",
            "tax_included": True,
        }
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        raise ToolError(
            "DELIVERY_UNAVAILABLE: no completed quote; try again or correct the fixture input"
        ) from exc
```

## Confirm and create one order

Source: [03-place-order/server.py](03-place-order/server.py)

```python
@mcp.tool(title="Place a confirmed store order", annotations=WRITE)
def place_order(quote_id: str, confirmed: bool, idempotency_key: str) -> dict:
    """Create a simulated order only for this customer's quote and explicit confirmation. No real payment."""
    require_write()
    if not confirmed:
        raise ToolError("CONFIRMATION_REQUIRED: review the quote before ordering")
    if not 1 <= len(idempotency_key) <= 128:
        raise ToolError("Use a nonempty idempotency key of at most 128 characters")
    owner = customer()
    digest = hashlib.sha256(
        json.dumps({"quote_id": quote_id}, sort_keys=True).encode()
    ).hexdigest()
    with db() as c:
        c.execute("BEGIN IMMEDIATE")
        prior = c.execute(
            "SELECT * FROM operations WHERE customer=? AND key=?",
            (owner, idempotency_key),
        ).fetchone()
        if prior:
            if prior["digest"] != digest:
                raise ToolError(
                    "IDEMPOTENCY_CONFLICT: key belongs to a different quote"
                )
            return json.loads(prior["result"])
        q = c.execute(
            "SELECT * FROM quotes WHERE id=? AND customer=?", (quote_id, owner)
        ).fetchone()
        if not q:
            raise ToolError("No accessible quote")
        if q["expires"] <= int(time.time()):
            raise ToolError("QUOTE_EXPIRED: request a fresh quote")
        # One quote cannot be purchased twice under a new key.
        consumed = c.execute(
            "SELECT 1 FROM operations WHERE customer=? AND digest=?", (owner, digest)
        ).fetchone()
        if consumed:
            raise ToolError(
                "QUOTE_ALREADY_USED: retrieve the original operation outcome"
            )
        order = "order_" + uuid.uuid4().hex
        c.execute(
            "INSERT INTO orders VALUES(?,?,?,?)", (order, owner, "placed", q["total"])
        )
        result = {
            "order_id": order,
            "status": "placed",
            "total_cents": q["total"],
            "payment": "simulated; no charge",
        }
        c.execute(
            "INSERT INTO operations VALUES(?,?,?,?)",
            (owner, idempotency_key, digest, json.dumps(result)),
        )
        return result
```

## Cancel only an owned eligible order

Source: [04-cancel-order/server.py](04-cancel-order/server.py)

```python
@mcp.tool(title="Cancel an eligible store order", annotations=WRITE)
def cancel_order(order_id: str, confirmed: bool) -> dict:
    """Cancel an owned, not-dispatched fixture order. Cancellation is not proof of a refund."""
    require_write()
    if not confirmed:
        raise ToolError("CONFIRMATION_REQUIRED")
    with db() as c:
        c.execute("BEGIN IMMEDIATE")
        o = c.execute(
            "SELECT * FROM orders WHERE id=? AND customer=?", (order_id, customer())
        ).fetchone()
        if not o:
            raise ToolError("No accessible order")
        if o["status"] == "dispatched":
            raise ToolError(
                "ALREADY_DISPATCHED: cancellation is unavailable; use the store's return process"
            )
        if o["status"] not in {"placed", "cancelled"}:
            raise ToolError("Order cannot be cancelled in this state")
        c.execute(
            "UPDATE orders SET status='cancelled' WHERE id=? AND status='placed'",
            (order_id,),
        )
        return {
            "order_id": order_id,
            "status": "cancelled",
            "payment_reversal": "not simulated; not confirmed",
        }
```
