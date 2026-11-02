"""A local resource-server lab, not a production identity provider."""

import os
import jwt
from pydantic import AnyHttpUrl
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.types import ToolAnnotations
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.mcpserver.exceptions import ToolError
from pathlib import Path
import json

PORT = int(os.getenv("PORT", "8000"))
RESOURCE = f"http://127.0.0.1:{PORT}/mcp"
SECRET = os.environ["ATLAS_DEMO_SECRET"]  # supplied locally; no committed credential
ISSUER = "https://issuer.atlas.example"


class Verifier:
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            claims = jwt.decode(
                token,
                SECRET,
                algorithms=["HS256"],
                audience=RESOURCE,
                issuer=ISSUER,
                options={"require": ["exp", "sub", "aud", "iss"]},
            )
            return AccessToken(
                token=token,
                client_id="atlas-workshop",
                subject=claims["sub"],
                scopes=claims.get("scope", "").split(),
                resource=RESOURCE,
                expires_at=claims["exp"],
                claims=claims,
            )
        except jwt.PyJWTError:
            return None


mcp = MCPServer(
    "Atlas: verify each HTTP request",
    token_verifier=Verifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(ISSUER),
        resource_server_url=AnyHttpUrl(RESOURCE),
        required_scopes=["docs:read"],
        validate_token_resource=True,
    ),
)

DOCS = json.loads(Path(__file__).with_name("docs.json").read_text())


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    )
)
def get_doc(doc_id: str) -> dict:
    """Fetch only a document visible to the token's tenant. No tenant argument is accepted."""
    token = get_access_token()
    tenant = (token.claims or {}).get("tenant") if token else None
    if tenant not in {"north", "harbor"}:
        raise ToolError("No accessible document.")
    for doc in DOCS:
        if doc["id"] == doc_id and doc["tenant"] in {"public", tenant}:
            return doc
    raise ToolError("No accessible document.")


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=PORT)
