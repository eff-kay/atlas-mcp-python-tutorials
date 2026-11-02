import json
import os
import time
import uuid
from pathlib import Path
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

LOG = Path(os.getenv("ATLAS_LOG", "events.jsonl"))
mcp = MCPServer("Atlas: outcomes, not raw chats")


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    )
)
def search_docs(query: str, inject_failure: bool = False) -> dict:
    """Search a fixed public fixture; inject_failure demonstrates a tool failure without raw-input logging."""
    started = time.perf_counter()
    outcome = "tool_error" if inject_failure else "ok"
    # Allowlist telemetry at collection, not after capturing the entire request.
    record = {
        "trace_id": uuid.uuid4().hex,
        "tool": "search_docs",
        "outcome": outcome,
        "duration_ms": round((time.perf_counter() - started) * 1000, 3),
    }
    with LOG.open("a") as output:
        output.write(json.dumps(record) + "\n")
    if inject_failure:
        raise ToolError(
            "INDEX_UNAVAILABLE: a simulated dependency failure; retry later."
        )
    return {"hits": ["public-v2"], "source": "https://docs.atlas.example/v2/keys"}


if __name__ == "__main__":
    mcp.run()
