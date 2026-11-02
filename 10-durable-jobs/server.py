import json
import os
import sqlite3
import uuid
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

DB = os.getenv("ATLAS_DB", "state.sqlite3")
TENANT = os.getenv("ATLAS_TENANT", "north")  # trusted fixture context, not an input
mcp = MCPServer("Atlas: application-defined jobs")
with sqlite3.connect(DB) as db:
    db.execute(
        "CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, tenant TEXT, status TEXT, lease_until REAL, result TEXT)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS indexed_docs(id TEXT PRIMARY KEY, body TEXT)"
    )


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False, destructive_hint=False, open_world_hint=False
    )
)
def start_reindex() -> dict:
    """Durably queue the fixed fixture corpus. This starts work and is a write."""
    job_id = uuid.uuid4().hex
    with sqlite3.connect(DB) as db:
        db.execute("INSERT INTO jobs VALUES(?,?,'queued',0,NULL)", (job_id, TENANT))
    return {"job_id": job_id, "status": "queued"}


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    )
)
def get_job(job_id: str) -> dict:
    """Read only a job belonging to the validated fixture tenant."""
    with sqlite3.connect(DB) as db:
        row = db.execute(
            "SELECT status,result FROM jobs WHERE id=? AND tenant=?", (job_id, TENANT)
        ).fetchone()
    if row is None:
        raise ToolError("No accessible job.")
    return {
        "job_id": job_id,
        "status": row[0],
        "result": json.loads(row[1]) if row[1] else None,
    }


if __name__ == "__main__":
    mcp.run()
