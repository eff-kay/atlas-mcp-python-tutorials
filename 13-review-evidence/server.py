import json
from pathlib import Path
from typing import Annotated
from pydantic import Field
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

mcp = MCPServer("Atlas: versioned retrieval")
DOCS = json.loads(Path(__file__).with_name("docs.json").read_text())
READ = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, open_world_hint=False
)


@mcp.tool(title="Search a documentation version", annotations=READ)
def search_docs(
    query: Annotated[str, Field(min_length=1, max_length=200)],
    version: str,
    limit: Annotated[int, Field(ge=1, le=3)] = 3,
) -> dict:
    """Find bounded public guides in exactly v1 or v2; return source evidence."""
    if version not in {"v1", "v2"}:
        raise ToolError("Unsupported version. Choose v1 or v2.")
    words = set(query.lower().split())
    hits = [
        d
        for d in DOCS
        if d["version"] == version
        and words.intersection((d["title"] + " " + d["body"]).lower().split())
    ]
    return {
        "hits": [
            {
                "id": d["id"],
                "version": d["version"],
                "source": d["source"],
                "excerpt": d["body"],
            }
            for d in hits[:limit]
        ]
    }


@mcp.tool(title="Fetch a public guide", annotations=READ)
def get_doc(doc_id: str) -> dict:
    """Fetch a known public fixture by ID, never an arbitrary URL."""
    for doc in DOCS:
        if doc["id"] == doc_id:
            return doc
    raise ToolError("No accessible document with this ID.")


if __name__ == "__main__":
    mcp.run()
