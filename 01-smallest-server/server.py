from mcp.server import MCPServer
from mcp.types import ToolAnnotations

mcp = MCPServer("Atlas: one public guide")


@mcp.tool(
    title="Get the sample guide",
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    ),
)
def get_guide() -> str:
    """Return one public v1 fixture. This tool cannot answer v2 questions."""
    return "Atlas API v1: create a replacement key before revoking the old key."


if __name__ == "__main__":
    mcp.run()
