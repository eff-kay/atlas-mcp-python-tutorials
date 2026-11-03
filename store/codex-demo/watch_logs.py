"""Follow the presentation event log; Ctrl-C stops viewing, not the server."""

import argparse
import json
import os
from pathlib import Path
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recent", type=int, default=0, help="print this many existing events first"
    )
    parser.add_argument(
        "--once", action="store_true", help="print existing events and exit"
    )
    args = parser.parse_args()
    path = (
        Path(
            os.environ.get(
                "TRAILSHOP_DEMO_STATE", Path.home() / ".local/state/trailshop-codex"
            )
        )
        / "events.jsonl"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    print(
        f"Watching {path} — no arguments, credentials or response payloads", flush=True
    )

    def show(line):
        row = json.loads(line)
        details = " ".join(
            f"{k}={v}" for k, v in row.items() if k not in {"time", "trace", "event"}
        )
        print(
            f"{row['time']}  {row.get('trace') or '--------'}  {row['event']:<18} {details}",
            flush=True,
        )

    with path.open() as f:
        existing = f.readlines()
        for line in existing[-max(0, args.recent) :] if args.recent else []:
            show(line)
        if args.once:
            return
        try:
            while True:
                line = f.readline()
                if line:
                    show(line)
                else:
                    time.sleep(0.15)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
