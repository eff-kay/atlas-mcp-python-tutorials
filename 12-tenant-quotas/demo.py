import asyncio, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        env = {"ATLAS_DB": str(Path(tmp) / "budget.sqlite3")}
        async with stdio(__file__, {**env, "ATLAS_TENANT": "north"}) as north:
            for i in range(3):
                require(
                    not (await north.call_tool("get_guide", {})).is_error,
                    "Budgeted read should pass",
                )
            denied = await north.call_tool("get_guide", {})
            require(denied.is_error, "Fourth read must be rate limited")
            show("North has used its budget", denied)
        async with stdio(__file__, {**env, "ATLAS_TENANT": "harbor"}) as harbor:
            result = await harbor.call_tool("get_guide", {})
            require(not result.is_error, "North must not consume Harbor's budget")
            show("Harbor still has capacity", result)


if __name__ == "__main__":
    asyncio.run(main())
