import asyncio, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workshop import stdio, show, require
import tempfile


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        env = {"STORE_DB": str(Path(tmp) / "store.sqlite3"), "STORE_CUSTOMER": "maya"}
        async with stdio(__file__, env) as c:
            quote = show(
                "Review quote",
                await c.call_tool(
                    "quote_delivery",
                    {"product_id": "blue-carryon", "address_ref": "demo-home"},
                ),
            )
            no = await c.call_tool(
                "place_order",
                {
                    "quote_id": quote["quote_id"],
                    "confirmed": False,
                    "idempotency_key": "checkout-1",
                },
            )
            require(no.is_error, "Must require confirmation")
            args = {
                "quote_id": quote["quote_id"],
                "confirmed": True,
                "idempotency_key": "checkout-1",
            }
            first = show(
                "Confirmed simulated order", await c.call_tool("place_order", args)
            )
        async with stdio(__file__, env) as restarted:
            retry = show(
                "Retry after restart", await restarted.call_tool("place_order", args)
            )
            require(first == retry, "Retry must return the same order")
            order = show(
                "Read owned order",
                await restarted.call_tool("get_order", {"order_id": first["order_id"]}),
            )
            require(order["status"] == "placed", "Expected placed state")


if __name__ == "__main__":
    asyncio.run(main())
