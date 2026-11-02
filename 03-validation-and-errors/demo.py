import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    async with stdio(__file__) as client:
        empty = await client.call_tool(
            "search_docs", {"query": "unicorn", "version": "v2"}
        )
        require(
            not empty.is_error and empty.structured_content["hits"] == [],
            "No match is a valid outcome",
        )
        show("Valid empty result", empty)
        for label, args in [
            ("Bad schema", {"query": "key", "version": "v2", "limit": 99}),
            ("Bad domain value", {"query": "key", "version": "v9"}),
        ]:
            result = await client.call_tool("search_docs", args)
            require(result.is_error, "Invalid request must fail")
            show(label, result)


if __name__ == "__main__":
    asyncio.run(main())
