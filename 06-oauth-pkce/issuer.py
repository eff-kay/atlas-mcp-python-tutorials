"""Pre-registered loopback PKCE lab. One fixture user, no production login/refresh/DCR."""

import base64
import hashlib
import hmac
import html
import os
import secrets
import time
from urllib.parse import urlencode
import jwt
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.routing import Route

ISSUER = f"http://127.0.0.1:{os.environ['PORT']}"
SECRET = os.environ["ATLAS_DEMO_SECRET"]
RESOURCE = os.environ["ATLAS_RESOURCE"]
CLIENT = "atlas-workshop"
REDIRECT = "http://127.0.0.1:8765/callback"
pending = {}
codes = {}


async def metadata(request):
    return JSONResponse(
        {
            "issuer": ISSUER,
            "authorization_endpoint": ISSUER + "/authorize",
            "token_endpoint": ISSUER + "/token",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "token_endpoint_auth_methods_supported": ["none"],
            "code_challenge_methods_supported": ["S256"],
            "scopes_supported": ["docs:read"],
        }
    )


async def authorize(request: Request):
    p = dict(request.query_params)
    valid = (
        p.get("client_id") == CLIENT
        and p.get("redirect_uri") == REDIRECT
        and p.get("resource") == RESOURCE
        and p.get("response_type") == "code"
        and p.get("scope") == "docs:read"
        and p.get("code_challenge_method") == "S256"
        and len(p.get("code_challenge", "")) == 43
        and bool(p.get("state"))
    )
    if not valid:
        return JSONResponse({"error": "invalid_request"}, status_code=400)
    handle = secrets.token_urlsafe(24)
    pending[handle] = {**p, "expires": time.time() + 60}
    return HTMLResponse(
        f"<h1>Local fixture: Maya</h1><p>Allow Atlas Workshop to read the fixture docs?</p>"
        f'<form method="post" action="/approve"><input type="hidden" name="request_id" '
        f'value="{html.escape(handle)}"><button name="decision" value="allow">Allow</button></form>'
    )


async def approve(request: Request):
    form = await request.form()
    p = pending.pop(str(form.get("request_id", "")), None)
    if not p or p["expires"] < time.time() or form.get("decision") != "allow":
        return JSONResponse({"error": "access_denied"}, status_code=400)
    code = secrets.token_urlsafe(32)
    codes[code] = p
    return RedirectResponse(
        REDIRECT + "?" + urlencode({"code": code, "state": p["state"]}), status_code=303
    )


async def token(request: Request):
    form = await request.form()
    grant = codes.pop(
        str(form.get("code", "")), None
    )  # one attempt; consumed atomically in this process
    verifier = str(form.get("code_verifier", ""))
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    if (
        not grant
        or grant["expires"] < time.time()
        or not 43 <= len(verifier) <= 128
        or not hmac.compare_digest(challenge, grant["code_challenge"])
        or form.get("client_id") != CLIENT
        or form.get("redirect_uri") != REDIRECT
        or form.get("resource") != RESOURCE
        or form.get("grant_type") != "authorization_code"
    ):
        return JSONResponse({"error": "invalid_grant"}, status_code=400)
    claims = {
        "iss": ISSUER,
        "aud": RESOURCE,
        "sub": "maya",
        "scope": "docs:read",
        "exp": int(time.time()) + 120,
    }
    return JSONResponse(
        {
            "access_token": jwt.encode(claims, SECRET, algorithm="HS256"),
            "token_type": "Bearer",
            "expires_in": 120,
            "scope": "docs:read",
        },
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )


app = Starlette(
    routes=[
        Route("/.well-known/oauth-authorization-server", metadata),
        Route("/authorize", authorize),
        Route("/approve", approve, methods=["POST"]),
        Route("/token", token, methods=["POST"]),
    ]
)
if __name__ == "__main__":
    uvicorn.run(
        app, host="127.0.0.1", port=int(os.environ["PORT"]), log_level="warning"
    )
