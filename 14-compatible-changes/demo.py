import asyncio, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    async with stdio(__file__) as client:
        tools = await client.list_tools()
        schema = tools.tools[0].input_schema
        require(
            "folder" not in schema.get("required", []),
            "Do not require the new field while old metadata is live",
        )
        for label, args in [
            ("Old published input", {"query": "key"}),
            ("New input", {"query": "key", "folder": "public"}),
        ]:
            result = await client.call_tool("search_docs", args)
            require(not result.is_error, "Both contracts must work")
            require(
                show(label, result)["hits"] == ["public-v2"], "Same semantic result"
            )
        print(
            "Expand -> deploy compatibly -> rescan/adopt -> retire only after migration."
        )


if __name__ == "__main__":
    asyncio.run(main())
