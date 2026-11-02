import asyncio, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        env = {"ATLAS_DB": str(Path(tmp) / "docs.sqlite3")}
        async with stdio(__file__, {**env, "ATLAS_ROLE": "reader"}) as reader:
            denied = await reader.call_tool(
                "publish_doc", {"body": "No permission", "expected_revision": 17}
            )
            require(denied.is_error, "Reader cannot publish")
        async with stdio(__file__, {**env, "ATLAS_ROLE": "editor"}) as editor:
            show("Original", await editor.call_tool("get_doc", {}))
            show(
                "Other editor publishes r18",
                await editor.call_tool(
                    "publish_doc", {"body": "Other edit", "expected_revision": 17}
                ),
            )
            stale = await editor.call_tool(
                "publish_doc", {"body": "Maya's stale edit", "expected_revision": 17}
            )
            require(stale.is_error, "Stale update must fail")
            show("Stale approval rejected", stale)
            show("Reload r18", await editor.call_tool("get_doc", {}))
            updated = await editor.call_tool(
                "publish_doc", {"body": "Reviewed merged edit", "expected_revision": 18}
            )
            require(
                show("New explicit approval -> r19", updated)["revision"] == 19,
                "Expected r19",
            )


if __name__ == "__main__":
    asyncio.run(main())
