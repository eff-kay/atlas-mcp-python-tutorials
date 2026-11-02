from typing import Annotated
from pydantic import BaseModel, Field
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

mcp = MCPServer("Atlas: honest outcomes")


class SearchResult(BaseModel):
    version: str
    hits: list[str]


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    )
)
def search_docs(
    query: Annotated[str, Field(min_length=1, max_length=100)],
    version: str,
    limit: Annotated[int, Field(ge=1, le=3)] = 3,
) -> SearchResult:
    """Search public v2; unsupported versions are errors, no match is success."""
    if version != "v2":
        raise ToolError("VERSION_UNSUPPORTED: choose v2; no silent fallback.")
    return SearchResult(
        version=version, hits=["public-v2"] if "key" in query.lower() else []
    )


if __name__ == "__main__":
    mcp.run()
