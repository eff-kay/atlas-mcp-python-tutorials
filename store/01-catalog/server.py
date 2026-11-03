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


if __name__ == "__main__":
    mcp.run()
