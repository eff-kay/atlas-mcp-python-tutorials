"""Use after starting server.py in a different terminal."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import http_mcp, show, require


async def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    async with http_mcp(base) as client:
        result = await client.call_tool("get_guide", {})
        require(not result.is_error, "Tool failed")
        show("Public guide over HTTP", result)


if __name__ == "__main__":
    asyncio.run(main())
