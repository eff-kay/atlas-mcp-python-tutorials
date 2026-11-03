import asyncio, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workshop import stdio, show, require


async def main():
    async with stdio(__file__) as c:
        print("Discovered:", [t.name for t in (await c.list_tools()).tools])
        data = show(
            "Matching item", await c.call_tool("search_products", {"color": "blue"})
        )
        require(data["products"][0]["price_cents"] == 7900, "Expected the $79 fixture")
        empty = show(
            "Honest no-match", await c.call_tool("search_products", {"color": "green"})
        )
        require(empty["products"] == [], "No invented products")


if __name__ == "__main__":
    asyncio.run(main())
