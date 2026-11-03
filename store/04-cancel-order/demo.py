import asyncio, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workshop import stdio, show, require
import tempfile


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        env = {"STORE_DB": str(Path(tmp) / "store.sqlite3"), "STORE_CUSTOMER": "maya"}
        async with stdio(__file__, env) as c:
            q = show(
                "Quote",
                await c.call_tool(
                    "quote_delivery",
                    {"product_id": "blue-carryon", "address_ref": "demo-home"},
                ),
            )
            o = show(
                "Place",
                await c.call_tool(
                    "place_order",
                    {
                        "quote_id": q["quote_id"],
                        "confirmed": True,
                        "idempotency_key": "checkout-1",
                    },
                ),
            )
            a = {"order_id": o["order_id"], "confirmed": True}
            one = show("Cancel", await c.call_tool("cancel_order", a))
            two = show("Repeat cancellation", await c.call_tool("cancel_order", a))
            require(
                one == two and one["status"] == "cancelled",
                "Stable cancellation result",
            )
            for label, oid in [
                ("Other shopper", "demo-other"),
                ("Dispatched", "demo-shipped"),
            ]:
                result = await c.call_tool(
                    "cancel_order", {"order_id": oid, "confirmed": True}
                )
                require(result.is_error, label + " must be denied")
                show(label + " denied", result)
        async with stdio(__file__, {**env, "STORE_CUSTOMER": "jules"}) as c:
            denied = await c.call_tool("get_order", {"order_id": o["order_id"]})
            require(denied.is_error, "An order ID is not permission")


if __name__ == "__main__":
    asyncio.run(main())
