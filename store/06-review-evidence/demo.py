import asyncio, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workshop import stdio, show, require
import json, tempfile, zipfile


async def main():
    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        async with stdio(
            __file__,
            {"STORE_DB": str(Path(tmp) / "store.sqlite3"), "STORE_CUSTOMER": "maya"},
        ) as c:
            inventory = [
                t.model_dump(by_alias=True, exclude_none=True)
                for t in (await c.list_tools()).tools
            ]

            async def case(name, tool, args, error=False):
                r = await c.call_tool(tool, args)
                require(r.is_error == error, name)
                value = show(name, r)
                results.append(
                    {
                        "name": name,
                        "tool": tool,
                        "arguments": args,
                        "expected_error": error,
                        "actual": value,
                    }
                )
                return value

            await case("Find the blue carry-on", "search_products", {"color": "blue"})
            q = await case(
                "Quote the delivery",
                "quote_delivery",
                {"product_id": "blue-carryon", "address_ref": "demo-home"},
            )
            o = await case(
                "Place confirmed order",
                "place_order",
                {
                    "quote_id": q["quote_id"],
                    "confirmed": True,
                    "idempotency_key": "review-1",
                },
            )
            await case("Read owned order", "get_order", {"order_id": o["order_id"]})
            await case(
                "Cancel eligible order",
                "cancel_order",
                {"order_id": o["order_id"], "confirmed": True},
            )
            await case(
                "No checkout confirmation",
                "place_order",
                {
                    "quote_id": q["quote_id"],
                    "confirmed": False,
                    "idempotency_key": "denied",
                },
                True,
            )
            await case(
                "Another customer's order",
                "cancel_order",
                {"order_id": "demo-other", "confirmed": True},
                True,
            )
            await case(
                "Already dispatched",
                "cancel_order",
                {"order_id": "demo-shipped", "confirmed": True},
                True,
            )
            owned = show(
                "Final state",
                await c.call_tool("get_order", {"order_id": o["order_id"]}),
            )
            require(owned["status"] == "cancelled", "Promised workflow must complete")
    require(
        len(results) == 8 and sum(r["expected_error"] for r in results) == 3,
        "Need five positive and three negative cases",
    )
    for t in inventory:
        require(
            "title" in t
            and all(
                isinstance(t["annotations"].get(k), bool)
                for k in ["readOnlyHint", "destructiveHint", "openWorldHint"]
            ),
            "Explicit tool metadata",
        )
    (out / "tool-inventory.json").write_text(json.dumps(inventory, indent=2))
    (out / "store-review-results.json").write_text(json.dumps(results, indent=2))
    with zipfile.ZipFile(out / "store-review-evidence.zip", "w") as z:
        for name in ["tool-inventory.json", "store-review-results.json"]:
            z.write(out / name, name)
    print(
        "Created evidence ZIP. Not a plugin package, production service, recording or approval guarantee."
    )


if __name__ == "__main__":
    asyncio.run(main())
