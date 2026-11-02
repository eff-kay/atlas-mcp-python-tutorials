import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    async with stdio(__file__) as client:
        result = await client.call_tool(
            "search_docs", {"query": "key", "version": "v2"}
        )
        hits = show("Versioned evidence", result)["hits"]
        require(len(hits) == 1 and hits[0]["version"] == "v2", "Expected only v2")
        show(
            "Fetched source",
            await client.call_tool("get_doc", {"doc_id": hits[0]["id"]}),
        )


if __name__ == "__main__":
    asyncio.run(main())
