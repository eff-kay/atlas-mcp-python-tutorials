import asyncio
import base64
import hashlib
import re
import secrets
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop import process_http, http_mcp, require, show


async def main():
    secret = secrets.token_urlsafe(32)
    # The issuer needs the resource URL before the resource process starts. Reserve a port.
    import socket

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        resource_port = sock.getsockname()[1]
    resource = f"http://127.0.0.1:{resource_port}/mcp"
    async with process_http(
        __file__,
        script="issuer.py",
        env={"ATLAS_DEMO_SECRET": secret, "ATLAS_RESOURCE": resource},
    ) as issuer:
        # process_http accepts a requested PORT for this resource via fixed_port.
        async with process_http(
            __file__,
            env={"ATLAS_DEMO_SECRET": secret, "ATLAS_ISSUER": issuer},
            fixed_port=resource_port,
        ) as base:
            async with httpx.AsyncClient(
                trust_env=False, follow_redirects=False
            ) as http:
                discovery = (
                    await http.get(base + "/.well-known/oauth-protected-resource/mcp")
                ).json()
                require(
                    discovery["authorization_servers"][0].rstrip("/") == issuer,
                    "Issuer must match discovery",
                )
                metadata = (
                    await http.get(issuer + "/.well-known/oauth-authorization-server")
                ).json()
                verifier = secrets.token_urlsafe(48)
                challenge = (
                    base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
                    .rstrip(b"=")
                    .decode()
                )
                state = secrets.token_urlsafe(24)
                page = await http.get(
                    metadata["authorization_endpoint"],
                    params={
                        "client_id": "atlas-workshop",
                        "redirect_uri": "http://127.0.0.1:8765/callback",
                        "resource": resource,
                        "scope": "docs:read",
                        "response_type": "code",
                        "state": state,
                        "code_challenge": challenge,
                        "code_challenge_method": "S256",
                    },
                )
                require(page.status_code == 200, "Consent page must load")
                handle = re.search(
                    r'name="request_id" value="([^"]+)"', page.text
                ).group(1)
                print(
                    "Consent: explicitly approving the local Maya fixture (no real login)."
                )
                approval = await http.post(
                    issuer + "/approve",
                    data={"request_id": handle, "decision": "allow"},
                )
                callback = parse_qs(urlsplit(approval.headers["location"]).query)
                require(callback["state"][0] == state, "Reject mismatched state")
                form = {
                    "grant_type": "authorization_code",
                    "client_id": "atlas-workshop",
                    "redirect_uri": "http://127.0.0.1:8765/callback",
                    "resource": resource,
                    "code": callback["code"][0],
                    "code_verifier": verifier,
                }
                response = await http.post(metadata["token_endpoint"], data=form)
                require(response.status_code == 200, "PKCE exchange must succeed")
                token = response.json()["access_token"]
                replay = await http.post(metadata["token_endpoint"], data=form)
                require(
                    replay.status_code == 400, "Authorization code must be single-use"
                )
                print("Code replay rejected:", replay.status_code)
                bad_page = await http.get(page.request.url)
                bad_handle = re.search(
                    r'name="request_id" value="([^"]+)"', bad_page.text
                ).group(1)
                bad_approval = await http.post(
                    issuer + "/approve",
                    data={"request_id": bad_handle, "decision": "allow"},
                )
                bad_code = parse_qs(urlsplit(bad_approval.headers["location"]).query)[
                    "code"
                ][0]
                bad = await http.post(
                    metadata["token_endpoint"],
                    data={
                        **form,
                        "code": bad_code,
                        "code_verifier": secrets.token_urlsafe(48),
                    },
                )
                require(bad.status_code == 400, "Wrong PKCE proof must fail")
                print("Wrong PKCE verifier rejected:", bad.status_code)
                bad_redirect = await http.get(
                    metadata["authorization_endpoint"],
                    params={
                        **dict(page.request.url.params),
                        "redirect_uri": "https://attacker.example/callback",
                    },
                )
                require(
                    bad_redirect.status_code == 400, "Unregistered redirect must fail"
                )
                print("Unregistered redirect rejected:", bad_redirect.status_code)
                async with http_mcp(base, token) as client:
                    show(
                        "Discovered → consented → called",
                        await client.call_tool("get_guide", {}),
                    )


if __name__ == "__main__":
    asyncio.run(main())
