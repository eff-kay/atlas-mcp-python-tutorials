import asyncio, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workshop import stdio, show, require
from workshop import process_http


async def main():
    async with process_http(
        __file__, script="providers.py", env={"PROVIDER": "address"}
    ) as address:
        async with process_http(
            __file__, script="providers.py", env={"PROVIDER": "delivery"}
        ) as delivery:
            async with stdio(
                __file__, {"ADDRESS_URL": address, "DELIVERY_URL": delivery}
            ) as c:
                result = show(
                    "Catalog + address + delivery",
                    await c.call_tool(
                        "quote_delivery",
                        {"product_id": "blue-carryon", "address_ref": "demo-home"},
                    ),
                )
                require(
                    result["total_cents"] == 9100
                    and result["route"]["distance_km"] == 12,
                    "Expected the slide fixture",
                )
                denied = await c.call_tool(
                    "quote_delivery",
                    {"product_id": "blue-carryon", "address_ref": "unknown"},
                )
                require(denied.is_error, "No invented route or delivery result")
                show("Unknown fixture address rejected", denied)


if __name__ == "__main__":
    asyncio.run(main())
