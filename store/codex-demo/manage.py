"""Start/stop only this demo process. No autostart service or public tunnel."""

import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
STATE = Path(
    os.environ.get("TRAILSHOP_DEMO_STATE", Path.home() / ".local/state/trailshop-codex")
)
PIDFILE = STATE / "process.json"
PORT = 8767


def running():
    if not PIDFILE.exists():
        return None
    info = json.loads(PIDFILE.read_text())
    result = subprocess.run(
        ["ps", "-p", str(info["pid"]), "-o", "args="], capture_output=True, text=True
    )
    return info if str(HERE / "server.py") in result.stdout else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop", "status"])
    args = parser.parse_args()
    STATE.mkdir(parents=True, exist_ok=True)
    info = running()
    if args.action == "stop":
        if info:
            os.kill(info["pid"], signal.SIGTERM)
            for _ in range(50):
                if not running():
                    break
                time.sleep(0.1)
            else:
                raise SystemExit("Demo is still shutting down; try stop again.")
            PIDFILE.unlink(missing_ok=True)
        print("Trailshop demo stopped.")
        return
    if args.action == "status":
        print(
            json.dumps(
                {
                    "running": bool(info),
                    "endpoint": f"http://127.0.0.1:{PORT}/mcp",
                    "state_directory": str(STATE),
                    "pid": info["pid"] if info else None,
                },
                indent=2,
            )
        )
        return
    if info:
        print(f"Already running: http://127.0.0.1:{PORT}/mcp (PID {info['pid']})")
        return
    for port in [8767, 8768, 8769]:
        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                raise SystemExit(
                    f"Port {port} is busy. Stop the conflicting service before starting this demo."
                ) from None
    with (STATE / "server.log").open("ab") as log:
        child = subprocess.Popen(
            [sys.executable, str(HERE / "server.py")],
            cwd=HERE,
            env={
                **os.environ,
                "PORT": str(PORT),
                "ADDRESS_PORT": "8768",
                "DELIVERY_PORT": "8769",
                "TRAILSHOP_DEMO_STATE": str(STATE),
            },
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
        )
    PIDFILE.write_text(json.dumps({"pid": child.pid}))
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(100):
        if child.poll() is not None:
            PIDFILE.unlink(missing_ok=True)
            raise SystemExit(f"Demo exited. See {STATE / 'server.log'}")
        try:
            opener.open(f"http://127.0.0.1:{PORT}/mcp", timeout=0.2)
            break
        except urllib.error.HTTPError as exc:
            if exc.code in {400, 405, 406}:
                break
            raise
        except urllib.error.URLError:
            time.sleep(0.05)
    else:
        child.terminate()
        child.wait(timeout=5)
        PIDFILE.unlink(missing_ok=True)
        raise SystemExit("Server startup timed out.")
    print(f"Trailshop ready: http://127.0.0.1:{PORT}/mcp")
    print(f"State and logs: {STATE}")


if __name__ == "__main__":
    main()
