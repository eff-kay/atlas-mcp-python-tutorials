import asyncio
import secrets
import sys
import time
from pathlib import Path
import httpx
import jwt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import process_http, http_mcp, show, require


async def main():
    secret = secrets.token_urlsafe(32)
    async with process_http(__file__, env={"ATLAS_DEMO_SECRET": secret}) as base:
        async with httpx.AsyncClient(trust_env=False) as http:
            missing = await http.get(base + "/mcp")
            require(missing.status_code == 401, "Missing token must be rejected")
            print("No token:", missing.status_code)
            print("Challenge:", missing.headers["www-authenticate"])
            claims = {
                "sub": "maya",
                "scope": "docs:read",
                "aud": base + "/mcp",
                "iss": "https://issuer.atlas.example",
                "exp": int(time.time()) + 120,
            }
            for label, patch in [
                ("wrong audience", {"aud": "https://other.example/mcp"}),
                ("expired", {"exp": int(time.time()) - 30}),
                ("missing scope", {"scope": ""}),
            ]:
                token = jwt.encode({**claims, **patch}, secret, algorithm="HS256")
                response = await http.get(
                    base + "/mcp", headers={"Authorization": "Bearer " + token}
                )
                require(response.status_code in {401, 403}, f"Must reject {label}")
                print(label + ":", response.status_code)
        token = jwt.encode(claims, secret, algorithm="HS256")
        async with http_mcp(base, token) as client:
            result = await client.call_tool("get_guide", {})
            require(not result.is_error, "Valid token should work")
            show("Authorized guide", result)
    print("This lab minted its own fixture tokens; it is not a sign-in flow.")


if __name__ == "__main__":
    asyncio.run(main())
