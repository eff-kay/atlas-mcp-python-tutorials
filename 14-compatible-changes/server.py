from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

mcp = MCPServer("Atlas: expand before migration")


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    )
)
def search_docs(query: str, folder: str | None = None) -> dict:
    """Search the public v2 fixture. Old callers omit folder; new callers may use 'public'."""
    if folder not in {None, "public"}:
        raise ToolError("UNSUPPORTED_FOLDER")
    return {"hits": ["public-v2"] if "key" in query.lower() else []}


if __name__ == "__main__":
    mcp.run()
