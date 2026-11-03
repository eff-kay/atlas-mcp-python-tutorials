"""SQLite store lab. No real orders, charges, refunds or addresses. Local identity is a trusted process fixture."""

import os, sqlite3, time, uuid, json, hashlib
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from pathlib import Path
import httpx
from providers import start_providers
from telemetry import traced, TRACE

STATE = Path(
    os.environ.get("TRAILSHOP_DEMO_STATE", Path.home() / ".local/state/trailshop-codex")
)
STATE.mkdir(parents=True, exist_ok=True)
PORT = int(os.environ.get("PORT", "8767"))
ADDRESS_PORT = int(os.environ.get("ADDRESS_PORT", "8768"))
DELIVERY_PORT = int(os.environ.get("DELIVERY_PORT", "8769"))
mcp = MCPServer(
    "Trailshop local demo",
    instructions="""Fictional local store for Maya. No real addresses, payments or purchases.
Use search_products, then quote_delivery with address_ref='demo-home'.
Show the total and ask the user before place_order or cancel_order.
Use a stable idempotency key for retries. A confirmed boolean alone is not authentication.
This process fixes the shopper as Maya; it is not a production login service.""",
)
READ = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, open_world_hint=False
)
WRITE = ToolAnnotations(
    read_only_hint=False, destructive_hint=True, open_world_hint=False
)
DB = os.getenv("STORE_DB", str(STATE / "store.sqlite3"))


def customer():
    return "maya"  # fixed, fictional local demo identity


def require_write():
    pass  # loopback fixture only; no real accounts or authorization


def db():
    c = sqlite3.connect(DB, timeout=5)
    c.row_factory = sqlite3.Row
    c.executescript("""CREATE TABLE IF NOT EXISTS quotes(id TEXT PRIMARY KEY,customer TEXT,product TEXT,total INTEGER,expires INTEGER);
CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY,customer TEXT,status TEXT,total INTEGER);
CREATE TABLE IF NOT EXISTS operations(customer TEXT,key TEXT,digest TEXT,result TEXT,PRIMARY KEY(customer,key));""")
    c.execute(
        "INSERT OR IGNORE INTO orders VALUES('demo-shipped','maya','dispatched',9100)"
    )
    c.execute("INSERT OR IGNORE INTO orders VALUES('demo-other','jules','placed',9100)")
    c.commit()
    return c


@mcp.tool(title="Search store products", annotations=READ)
@traced
def search_products(color: str = "blue") -> dict:
    """Return one in-stock blue carry-on fixture, or an honest no-match."""
    return {
        "products": [
            {
                "id": "blue-carryon",
                "name": "Blue carry-on backpack",
                "color": "blue",
                "carry_on": True,
                "in_stock": True,
                "price_cents": 7900,
                "currency": "USD",
            }
        ]
        if color == "blue"
        else []
    }


@mcp.tool(
    title="Prepare a delivery quote",
    annotations=ToolAnnotations(
        read_only_hint=False, destructive_hint=False, open_world_hint=False
    ),
)
@traced
def quote_delivery(product_id: str, address_ref: str) -> dict:
    """Call local GeoRoute and ParcelQuote HTTP fixtures. Use demo-home for Maya's saved destination. Quote expires in 120 seconds; no payment."""
    if product_id != "blue-carryon":
        raise ToolError("UNKNOWN_PRODUCT")
    try:
        with httpx.Client(
            trust_env=False, timeout=3, headers={"X-Demo-Trace-Id": TRACE.get() or ""}
        ) as http:
            route = http.post(
                f"http://127.0.0.1:{ADDRESS_PORT}/route",
                json={"address_ref": address_ref},
            )
            route.raise_for_status()
            r = route.json()
            delivery = http.post(
                f"http://127.0.0.1:{DELIVERY_PORT}/quote",
                json={"distance_km": r["distance_km"], "product_id": product_id},
            )
            delivery.raise_for_status()
            shipping = delivery.json()
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        raise ToolError(
            "DELIVERY_UNAVAILABLE: use the saved fixture address demo-home"
        ) from exc
    q = "q_" + uuid.uuid4().hex
    expires = int(time.time()) + 120
    total = 7900 + shipping["shipping_cents"]
    with db() as c:
        c.execute(
            "INSERT INTO quotes VALUES(?,?,?,?,?)",
            (q, customer(), product_id, total, expires),
        )
    return {
        "quote_id": q,
        "item_cents": 7900,
        "shipping_cents": shipping["shipping_cents"],
        "total_cents": total,
        "currency": "USD",
        "tax_included": True,
        "distance_km": r["distance_km"],
        "eta": shipping["eta"],
        "expires_at": expires,
        "route_provider": r["provider"],
        "delivery_provider": shipping["provider"],
        "simulation": True,
    }


@mcp.tool(title="Place a confirmed store order", annotations=WRITE)
@traced
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


@mcp.tool(title="Read an owned store order", annotations=READ)
@traced
def get_order(order_id: str) -> dict:
    """Read only the authenticated/local-fixture customer's order."""
    with db() as c:
        o = c.execute(
            "SELECT * FROM orders WHERE id=? AND customer=?", (order_id, customer())
        ).fetchone()
    if not o:
        raise ToolError("No accessible order")
    return dict(o)


@mcp.tool(title="Cancel an eligible store order", annotations=WRITE)
@traced
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


@mcp.resource(
    "trailshop://policies/returns",
    name="Store cancellation and return policy",
    mime_type="text/plain",
)
def return_policy() -> str:
    return "Fictional Trailshop: Maya may cancel an owned order before dispatch. A dispatched order cannot be cancelled. Payment reversal is separate and is not simulated. No real charges occur."


@mcp.resource(
    "trailshop://guides/carry-on", name="Carry-on size guide", mime_type="text/plain"
)
def carry_on_guide() -> str:
    return "The demo blue-carryon backpack measures 45 x 30 x 20 cm. Airline limits vary; confirm the specific carrier. This is fixture product data."


@mcp.prompt(name="shop_for_maya", title="Find Maya's backpack")
def shop_for_maya() -> str:
    return "Find a blue carry-on backpack under $100 total, delivered by Friday to my saved demo-home destination. Search and quote first, show the total, then wait for my purchase confirmation. Use only this fictional store."


if __name__ == "__main__":
    providers = start_providers(ADDRESS_PORT, DELIVERY_PORT)
    try:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=PORT)
    finally:
        for provider in providers:
            provider.shutdown()
            provider.server_close()
