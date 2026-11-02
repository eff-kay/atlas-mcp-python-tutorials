import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import process_http, http_mcp, show, require


async def main():
    async with process_http(__file__) as base:
        print("HTTP endpoint:", base + "/mcp")
        async with http_mcp(base) as client:
            result = await client.call_tool("get_guide", {})
            require(not result.is_error, "HTTP call should succeed")
            show("Same tool, HTTP transport", result)


if __name__ == "__main__":
    asyncio.run(main())
