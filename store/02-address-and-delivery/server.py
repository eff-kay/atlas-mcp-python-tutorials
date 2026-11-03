from typing import Annotated
from pydantic import Field
from mcp.server import MCPServer
from mcp.types import ToolAnnotations

mcp = MCPServer("TrailShop: catalog")
READ = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, open_world_hint=False
)
PRODUCTS = [
    {
        "id": "blue-carryon",
        "name": "Blue carry-on backpack",
        "color": "blue",
        "carry_on": True,
        "price_cents": 7900,
        "currency": "USD",
        "in_stock": True,
    },
    {
        "id": "red-carryon",
        "name": "Red carry-on backpack",
        "color": "red",
        "carry_on": True,
        "price_cents": 6900,
        "currency": "USD",
        "in_stock": True,
    },
]


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


import os, httpx
from mcp.server.mcpserver.exceptions import ToolError


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


if __name__ == "__main__":
    mcp.run()
