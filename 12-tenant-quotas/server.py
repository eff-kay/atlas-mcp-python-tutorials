import os
import sqlite3
import time
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

DB = os.getenv("ATLAS_DB", "state.sqlite3")
TENANT = os.getenv("ATLAS_TENANT", "north")
LIMIT = 3
mcp = MCPServer("Atlas: fair admission")
with sqlite3.connect(DB) as db:
    db.execute(
        "CREATE TABLE IF NOT EXISTS budgets(tenant TEXT PRIMARY KEY, used INTEGER, reset_at REAL)"
    )


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    )
)
def get_guide() -> dict:
    """Read public v2 docs within the caller's per-tenant budget: 3 requests per 60-second window."""
    now = time.time()
    with sqlite3.connect(DB) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT used,reset_at FROM budgets WHERE tenant=?", (TENANT,)
        ).fetchone()
        used, reset = row if row and row[1] > now else (0, now + 60)
        if used >= LIMIT:
            raise ToolError(
                f"RATE_LIMITED: retry in {max(1, int(reset - now))} seconds; do not immediately loop."
            )
        db.execute(
            "INSERT INTO budgets VALUES(?,?,?) ON CONFLICT(tenant) DO UPDATE SET used=excluded.used,reset_at=excluded.reset_at",
            (TENANT, used + 1, reset),
        )
    return {"version": "v2"}


if __name__ == "__main__":
    mcp.run()
