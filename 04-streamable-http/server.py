import os
from mcp.server import MCPServer
from mcp.types import ToolAnnotations

mcp = MCPServer("Atlas: HTTP adapter")


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    )
)
def get_guide() -> dict:
    """Return one public v2 fixture over HTTP."""
    return {"version": "v2", "source": "https://docs.atlas.example/v2/keys"}


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=int(os.getenv("PORT", "8000")),
    )
