"""SQLite store lab. No real orders, charges, refunds or addresses. Local identity is a trusted process fixture."""

import os, sqlite3, time, uuid, json, hashlib
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

mcp = MCPServer("TrailShop: order lifecycle")
READ = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, open_world_hint=False
)
WRITE = ToolAnnotations(
    read_only_hint=False, destructive_hint=True, open_world_hint=False
)
DB = os.getenv("STORE_DB", "store.sqlite3")


def customer():
    return os.getenv("STORE_CUSTOMER", "maya")


def require_write():
    pass  # trusted local lab only; HTTP lesson replaces with token scope enforcement


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
def search_products(color: str = "blue") -> dict:
    """Return one in-stock blue carry-on fixture, or an honest no-match."""
    return {
        "products": [{"id": "blue-carryon", "price_cents": 7900, "currency": "USD"}]
        if color == "blue"
        else []
    }


@mcp.tool(title="Prepare a checkout quote", annotations=READ)
def quote_delivery(product_id: str, address_ref: str) -> dict:
    """Prepare a customer-bound, two-minute $91 fixture quote; no payment occurs."""
    if product_id != "blue-carryon" or address_ref != "demo-home":
        raise ToolError("No quote for that product/address fixture")
    q = "q_" + uuid.uuid4().hex
    expires = int(time.time()) + 120
    with db() as c:
        c.execute(
            "INSERT INTO quotes VALUES(?,?,?,?,?)",
            (q, customer(), product_id, 9100, expires),
        )
    return {
        "quote_id": q,
        "item_cents": 7900,
        "shipping_cents": 1200,
        "total_cents": 9100,
        "currency": "USD",
        "tax_included": True,
        "distance_km": 12,
        "eta": "Friday (fixture estimate)",
        "expires_at": expires,
    }


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


@mcp.tool(title="Read an owned store order", annotations=READ)
def get_order(order_id: str) -> dict:
    """Read only the authenticated/local-fixture customer's order."""
    with db() as c:
        o = c.execute(
            "SELECT * FROM orders WHERE id=? AND customer=?", (order_id, customer())
        ).fetchone()
    if not o:
        raise ToolError("No accessible order")
    return dict(o)


if __name__ == "__main__":
    mcp.run()
