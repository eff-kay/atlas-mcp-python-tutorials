import asyncio, json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "events.jsonl"
        async with stdio(__file__, {"ATLAS_LOG": str(log)}) as client:
            show(
                "Good tool result",
                await client.call_tool(
                    "search_docs", {"query": "fixture-sensitive-query"}
                ),
            )
            failed = await client.call_tool(
                "search_docs",
                {"query": "fixture-sensitive-query", "inject_failure": True},
            )
            require(failed.is_error, "Dependency failure is a tool error")
            show("RPC completed, tool failed", failed)
        raw = log.read_text()
        require("fixture-sensitive-query" not in raw, "Do not record the raw query")
        events = [json.loads(line) for line in raw.splitlines()]
        require(
            [x["outcome"] for x in events] == ["ok", "tool_error"],
            "Keep both outcome classes",
        )
        print("Internal telemetry:", json.dumps(events, indent=2))
        print(
            "Trace IDs stay internal; final answer quality still needs workflow evaluation."
        )


if __name__ == "__main__":
    asyncio.run(main())
