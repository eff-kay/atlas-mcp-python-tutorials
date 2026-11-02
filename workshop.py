"""Demo plumbing only. Servers never import this module or another lesson."""

from contextlib import asynccontextmanager
from pathlib import Path
import asyncio
import json
import os
import socket
import subprocess
import sys
import tempfile

import httpx
import httpx2
from mcp import Client, StdioServerParameters
from mcp.client.streamable_http import streamable_http_client


def stdio(demo_file, env=None):
    folder = Path(demo_file).resolve().parent
    return Client(
        StdioServerParameters(
            command=sys.executable,
            args=[str(folder / "server.py")],
            cwd=folder,
            env={**os.environ, **(env or {})},
        )
    )


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def show(label, result):
    data = result.structured_content
    if data is None:
        texts = [getattr(block, "text", "") for block in result.content]
        try:
            data = json.loads(texts[0]) if len(texts) == 1 else texts
        except (ValueError, IndexError):
            data = texts
    print(f"{label}: {json.dumps(data, ensure_ascii=False)}")
    return data


@asynccontextmanager
async def process_http(demo_file, script="server.py", env=None, fixed_port=None):
    """Launch a loopback-only server on a free port, then always stop it."""
    folder = Path(demo_file).resolve().parent
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = fixed_port or sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryFile(mode="w+t") as log:
        process = subprocess.Popen(
            [sys.executable, str(folder / script)],
            cwd=folder,
            env={**os.environ, **(env or {}), "PORT": str(port)},
            stdout=log,
            stderr=log,
        )
        try:
            async with httpx.AsyncClient(trust_env=False) as probe:
                for _ in range(150):
                    if process.poll() is not None:
                        log.seek(0)
                        raise RuntimeError(log.read())
                    try:
                        await probe.get(base + "/", timeout=0.3)
                        break
                    except httpx.TransportError:
                        await asyncio.sleep(0.04)
                else:
                    raise RuntimeError("Local server did not become ready")
            yield base
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


@asynccontextmanager
async def http_mcp(base, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx2.AsyncClient(headers=headers, timeout=30, trust_env=False) as http:
        async with Client(
            streamable_http_client(base + "/mcp", http_client=http)
        ) as client:
            yield client
