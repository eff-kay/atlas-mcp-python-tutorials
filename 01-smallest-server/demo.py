import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    async with stdio(__file__) as client:
        tools = await client.list_tools()
        print("Discovered:", [t.name for t in tools.tools])
        result = await client.call_tool("get_guide", {})
        require(not result.is_error, "Tool should succeed")
        show("Guide (v1, not v2)", result)


if __name__ == "__main__":
    asyncio.run(main())
