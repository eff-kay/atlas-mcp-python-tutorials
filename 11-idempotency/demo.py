import asyncio, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        env = {"ATLAS_DB": str(Path(tmp) / "ops.sqlite3"), "ATLAS_TENANT": "north"}
        args = {
            "operation_key": "p42",
            "body": "Reviewed change",
            "expected_revision": 17,
        }
        async with stdio(__file__, env) as client:
            lost = await client.call_tool("publish_doc", {**args, "lose_ack": True})
            require(
                lost.is_error,
                "The caller should observe the injected failed acknowledgement",
            )
            show("Committed but caller saw failure", lost)
        async with stdio(__file__, env) as restarted:
            result = show(
                "Retry after restart recovers original result",
                await restarted.call_tool("publish_doc", args),
            )
            require(result["revision"] == 18, "Retry must not create r19")
            conflict = await restarted.call_tool(
                "publish_doc", {**args, "body": "Different change"}
            )
            require(conflict.is_error, "Conflicting reuse must fail")
            show("Same key, different payload", conflict)


if __name__ == "__main__":
    asyncio.run(main())
