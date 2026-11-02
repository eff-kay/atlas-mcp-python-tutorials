import os
import sqlite3
from typing import Annotated
from pydantic import Field
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

DB = os.getenv("ATLAS_DB", "state.sqlite3")
ROLE = os.getenv(
    "ATLAS_ROLE", "reader"
)  # trusted local process fixture; NOT a caller tool argument
mcp = MCPServer("Atlas: optimistic concurrency")
with sqlite3.connect(DB) as db:
    db.execute(
        "CREATE TABLE IF NOT EXISTS docs(id TEXT PRIMARY KEY, body TEXT, revision INTEGER)"
    )
    db.execute("INSERT OR IGNORE INTO docs VALUES('north-v2','Original guide',17)")


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    )
)
def get_doc() -> dict:
    """Inspect the fixed North document and its current revision."""
    with sqlite3.connect(DB) as db:
        body, revision = db.execute(
            "SELECT body,revision FROM docs WHERE id='north-v2'"
        ).fetchone()
    return {"id": "north-v2", "body": body, "revision": revision}


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False, destructive_hint=True, open_world_hint=False
    )
)
def publish_doc(
    body: Annotated[str, Field(min_length=1, max_length=2000)], expected_revision: int
) -> dict:
    """Overwrite the fixed North document only for an editor at the approved base revision."""
    if ROLE != "editor":
        raise ToolError("EDITOR_REQUIRED")
    with sqlite3.connect(DB) as db:
        changed = db.execute(
            "UPDATE docs SET body=?,revision=revision+1 WHERE id='north-v2' AND revision=?",
            (body, expected_revision),
        ).rowcount
        if not changed:
            raise ToolError(
                "REVISION_CONFLICT: fetch current content, review the diff, approve again."
            )
    return {"revision": expected_revision + 1}


if __name__ == "__main__":
    mcp.run()
