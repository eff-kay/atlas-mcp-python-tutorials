import hashlib
import json
import os
import sqlite3
from typing import Annotated
from pydantic import Field
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

DB = os.getenv("ATLAS_DB", "state.sqlite3")
TENANT = os.getenv("ATLAS_TENANT", "north")
mcp = MCPServer("Atlas: durable operation outcomes")
with sqlite3.connect(DB) as db:
    db.execute(
        "CREATE TABLE IF NOT EXISTS docs(tenant TEXT PRIMARY KEY, body TEXT, revision INTEGER)"
    )
    db.execute("INSERT OR IGNORE INTO docs VALUES(?,'Original',17)", (TENANT,))
    db.execute(
        "CREATE TABLE IF NOT EXISTS operations(tenant TEXT, op_key TEXT, payload_hash TEXT, result TEXT, PRIMARY KEY(tenant,op_key))"
    )


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=False, destructive_hint=True, open_world_hint=False
    )
)
def publish_doc(
    operation_key: Annotated[str, Field(min_length=1, max_length=100)],
    body: Annotated[str, Field(min_length=1, max_length=2000)],
    expected_revision: int,
    lose_ack: bool = False,
) -> dict:
    """Publish the fixed editor fixture once per key/payload. lose_ack injects a post-commit failure for this lab."""
    payload = json.dumps(
        {"action": "publish", "body": body, "base": expected_revision}, sort_keys=True
    )
    fingerprint = hashlib.sha256(payload.encode()).hexdigest()
    with sqlite3.connect(DB) as db:
        db.execute("BEGIN IMMEDIATE")
        prior = db.execute(
            "SELECT payload_hash,result FROM operations WHERE tenant=? AND op_key=?",
            (TENANT, operation_key),
        ).fetchone()
        if prior:
            if prior[0] != fingerprint:
                raise ToolError(
                    "KEY_REUSE_CONFLICT: same key, different operation payload."
                )
            return json.loads(
                prior[1]
            )  # recognize own retry BEFORE checking now-stale base revision
        count = db.execute(
            "UPDATE docs SET body=?,revision=revision+1 WHERE tenant=? AND revision=?",
            (body, TENANT, expected_revision),
        ).rowcount
        if count != 1:
            raise ToolError("REVISION_CONFLICT")
        result = {"revision": expected_revision + 1}
        db.execute(
            "INSERT INTO operations VALUES(?,?,?,?)",
            (TENANT, operation_key, fingerprint, json.dumps(result)),
        )
    if lose_ack:
        raise ToolError(
            "SIMULATED_ACK_LOSS: write committed; caller must recover the stored outcome."
        )
    return result


if __name__ == "__main__":
    mcp.run()
