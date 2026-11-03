"""Isolated CI demo; never touches the presenter's running store/database."""

import asyncio
from pathlib import Path
import socket
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from workshop import process_http
from validate import validate


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        address_port = free_port()
        delivery_port = free_port()
        while delivery_port == address_port:
            delivery_port = free_port()
        async with process_http(
            __file__,
            env={
                "TRAILSHOP_DEMO_STATE": tmp,
                "STORE_DB": str(Path(tmp) / "store.sqlite3"),
                "ADDRESS_PORT": str(address_port),
                "DELIVERY_PORT": str(delivery_port),
            },
        ) as base:
            await validate(base, transactions=True)


if __name__ == "__main__":
    asyncio.run(main())
