from pathlib import Path
import subprocess, sys

root = Path(__file__).resolve().parents[1]
for p in sorted(Path(__file__).parent.glob("[0-9][0-9]-*")):
    print("\n=== " + str(p.relative_to(root)) + " ===", flush=True)
    subprocess.run(
        [sys.executable, str(p / "demo.py")], cwd=root, check=True, timeout=60
    )
print("All six store lessons completed.")
