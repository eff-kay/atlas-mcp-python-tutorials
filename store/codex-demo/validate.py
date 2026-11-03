"""Validate a running local demo over its real MCP HTTP endpoint."""

import argparse
import asyncio
import json
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workshop import http_mcp, require, show


async def validate(base, transactions):
    async with http_mcp(base) as client:
        inventory = [t.name for t in (await client.list_tools()).tools]
        require(
            set(inventory)
            == {
                "search_products",
                "quote_delivery",
                "place_order",
                "get_order",
                "cancel_order",
            },
            "Expected five store tools",
        )
        print("Discovered tools:", json.dumps(inventory))
        resources = [str(r.uri) for r in (await client.list_resources()).resources]
        require(len(resources) == 2, "Expected policy and guide resources")
        print("Discovered resources:", json.dumps(resources))
        require(len((await client.list_prompts()).prompts) == 1, "Expected Maya prompt")
        require(
            bool((await client.read_resource("trailshop://policies/returns")).contents),
            "Policy must be readable",
        )
        require(
            bool((await client.get_prompt("shop_for_maya")).messages),
            "Prompt must be retrievable",
        )
        product = show(
            "Search", await client.call_tool("search_products", {"color": "blue"})
        )
        require(product["products"][0]["price_cents"] == 7900, "Expected $79 product")
        empty = show(
            "No-match", await client.call_tool("search_products", {"color": "green"})
        )
        require(empty["products"] == [], "No fabricated match")
        quote = show(
            "Quote through provider APIs",
            await client.call_tool(
                "quote_delivery",
                {"product_id": "blue-carryon", "address_ref": "demo-home"},
            ),
        )
        require(
            quote["total_cents"] == 9100 and quote["distance_km"] == 12,
            "Expected $91 quote via 12km route",
        )
        require(
            "GeoRoute" in quote["route_provider"]
            and "ParcelQuote" in quote["delivery_provider"],
            "Expected both providers",
        )
        if transactions:
            key = "validation-" + uuid.uuid4().hex
            args = {
                "quote_id": quote["quote_id"],
                "confirmed": True,
                "idempotency_key": key,
            }
            denied = await client.call_tool("place_order", {**args, "confirmed": False})
            require(denied.is_error, "Confirmation required")
            order = show(
                "Simulated purchase", await client.call_tool("place_order", args)
            )
            replay = show("Same-key retry", await client.call_tool("place_order", args))
            require(
                replay["order_id"] == order["order_id"], "Retry must return same order"
            )
            denied = await client.call_tool(
                "place_order", {**args, "idempotency_key": key + "-other"}
            )
            require(denied.is_error, "Quote cannot be purchased twice")
            cancelled = show(
                "Cancellation",
                await client.call_tool(
                    "cancel_order", {"order_id": order["order_id"], "confirmed": True}
                ),
            )
            require(cancelled["status"] == "cancelled", "Cancellation must persist")
            for fixture in ["demo-other", "demo-shipped"]:
                require(
                    (
                        await client.call_tool(
                            "cancel_order", {"order_id": fixture, "confirmed": True}
                        )
                    ).is_error,
                    "Ownership/dispatch check must hold",
                )
            final = show(
                "Final order",
                await client.call_tool("get_order", {"order_id": order["order_id"]}),
            )
            require(final["status"] == "cancelled", "Expected final persisted state")
    print("PASS: local HTTP demo works. No real purchase or payment occurred.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8767")
    parser.add_argument(
        "--transactions",
        action="store_true",
        help="also place and cancel one simulated order",
    )
    args = parser.parse_args()
    asyncio.run(validate(args.url, args.transactions))
