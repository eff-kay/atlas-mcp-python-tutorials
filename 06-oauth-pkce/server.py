"""A local resource-server lab, not a production identity provider."""

import os
import jwt
from pydantic import AnyHttpUrl
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.types import ToolAnnotations

PORT = int(os.getenv("PORT", "8000"))
RESOURCE = f"http://127.0.0.1:{PORT}/mcp"
SECRET = os.environ["ATLAS_DEMO_SECRET"]  # supplied locally; no committed credential
ISSUER = os.environ["ATLAS_ISSUER"]


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


@mcp.tool(
    annotations=ToolAnnotations(
        read_only_hint=True, destructive_hint=False, open_world_hint=False
    )
)
def get_guide() -> dict:
    """Read a private v2 fixture after token signature, issuer, audience and scope checks."""
    return {"id": "north-v2", "version": "v2"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=PORT)
