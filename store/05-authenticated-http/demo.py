import asyncio, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workshop import show, require
import tempfile, secrets, time, jwt, httpx
from workshop import process_http, http_mcp


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        secret = secrets.token_urlsafe(32)
        async with process_http(
            __file__,
            env={
                "STORE_DB": str(Path(tmp) / "store.sqlite3"),
                "STORE_DEMO_SECRET": secret,
            },
        ) as base:
            claims = {
                "iss": "https://issuer.trailshop.example",
                "aud": base + "/mcp",
                "sub": "maya",
                "scope": "store:read",
                "exp": int(time.time()) + 120,
            }
            async with httpx.AsyncClient(trust_env=False) as http:
                require(
                    (await http.get(base + "/mcp")).status_code == 401,
                    "No token must fail",
                )
                wrong = jwt.encode(
                    {**claims, "aud": "https://other.example/mcp"},
                    secret,
                    algorithm="HS256",
                )
                require(
                    (
                        await http.get(
                            base + "/mcp", headers={"Authorization": "Bearer " + wrong}
                        )
                    ).status_code
                    == 401,
                    "Wrong audience must fail",
                )
            token = jwt.encode(claims, secret, algorithm="HS256")
            async with http_mcp(base, token) as c:
                q = show(
                    "Authorized shopper quote",
                    await c.call_tool(
                        "quote_delivery",
                        {"product_id": "blue-carryon", "address_ref": "demo-home"},
                    ),
                )
                denied = await c.call_tool(
                    "place_order",
                    {
                        "quote_id": q["quote_id"],
                        "confirmed": True,
                        "idempotency_key": "http-1",
                    },
                )
                require(denied.is_error, "Read scope cannot purchase")
                show("Read-only token denied purchase", denied)
            token = jwt.encode(
                {**claims, "scope": "store:read store:write"}, secret, algorithm="HS256"
            )
            async with http_mcp(base, token) as c:
                o = show(
                    "Write-scoped simulated purchase",
                    await c.call_tool(
                        "place_order",
                        {
                            "quote_id": q["quote_id"],
                            "confirmed": True,
                            "idempotency_key": "http-1",
                        },
                    ),
                )
                show(
                    "Write-scoped cancellation",
                    await c.call_tool(
                        "cancel_order", {"order_id": o["order_id"], "confirmed": True}
                    ),
                )
            other = jwt.encode({**claims, "sub": "jules"}, secret, algorithm="HS256")
            async with http_mcp(base, other) as c:
                denied = await c.call_tool("get_order", {"order_id": o["order_id"]})
                require(denied.is_error, "Verified other user cannot read Maya's order")
    print("Fixture tokens only: no production login or real payment is implemented.")


if __name__ == "__main__":
    asyncio.run(main())
