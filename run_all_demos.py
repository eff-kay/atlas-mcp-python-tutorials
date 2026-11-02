"""Run the learner-facing examples, with cleanup and a bounded timeout per folder."""

from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
lessons = sorted(p for p in root.iterdir() if p.is_dir() and p.name[:2].isdigit())
failed = []
for folder in lessons:
    print(f"\n=== {folder.name} ===", flush=True)
    started = time.monotonic()
    try:
        result = subprocess.run(
            [sys.executable, str(folder / "demo.py")],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(result.stdout, end="")
        if result.returncode:
            failed.append(folder.name)
            print(result.stderr, file=sys.stderr)
        else:
            print(f"PASS ({time.monotonic() - started:.1f}s)")
    except subprocess.TimeoutExpired:
        failed.append(folder.name)
        print("Demo timed out", file=sys.stderr)
if failed:
    raise SystemExit("Failed demos: " + ", ".join(failed))
print(f"\nAll {len(lessons)} runnable lessons completed.")
