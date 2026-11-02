import asyncio, os, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import stdio, show, require


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        env = {"ATLAS_DB": str(Path(tmp) / "jobs.sqlite3"), "ATLAS_TENANT": "north"}
        async with stdio(__file__, env) as client:
            job = show(
                "Persisted before acknowledgement",
                await client.call_tool("start_reindex", {}),
            )
        print("Server disconnected. The job remains in SQLite.")
        subprocess.run(
            [sys.executable, str(Path(__file__).with_name("worker.py"))],
            env={**os.environ, **env},
            check=True,
        )
        async with stdio(__file__, env) as restarted:
            result = show(
                "After server restart",
                await restarted.call_tool("get_job", {"job_id": job["job_id"]}),
            )
            require(
                result["status"] == "completed"
                and result["result"]["indexed_docs"] == 2,
                "Expected durable completion",
            )
        async with stdio(__file__, {**env, "ATLAS_TENANT": "harbor"}) as stranger:
            denied = await stranger.call_tool("get_job", {"job_id": job["job_id"]})
            require(denied.is_error, "A job ID is not authorization")
            show("Other tenant denied", denied)


if __name__ == "__main__":
    asyncio.run(main())
