import asyncio, secrets, sys, time
from pathlib import Path
import jwt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import process_http, http_mcp, show, require


async def main():
    secret = secrets.token_urlsafe(32)
    async with process_http(__file__, env={"ATLAS_DEMO_SECRET": secret}) as base:
        token = jwt.encode(
            {
                "sub": "maya",
                "tenant": "north",
                "scope": "docs:read",
                "aud": base + "/mcp",
                "iss": "https://issuer.atlas.example",
                "exp": int(time.time()) + 120,
            },
            secret,
            algorithm="HS256",
        )
        async with http_mcp(base, token) as client:
            own = await client.call_tool("get_doc", {"doc_id": "north-v2"})
            require(not own.is_error, "North should read North")
            show("North allowed", own)
            for doc_id in ["harbor-v2", "does-not-exist"]:
                result = await client.call_tool("get_doc", {"doc_id": doc_id})
                require(result.is_error, "Denied and unknown IDs must both fail")
                show("Same denial for " + doc_id, result)


if __name__ == "__main__":
    asyncio.run(main())
