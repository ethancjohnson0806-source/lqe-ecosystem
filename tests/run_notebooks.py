"""Extract and execute code cells from all notebooks. Exit 1 on failure."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from shared.paths import ensure_lqe_on_path

ensure_lqe_on_path()


def main() -> int:
    nb_dir = ROOT / "notebooks"
    paths = sorted(nb_dir.glob("*.ipynb"))
    if not paths:
        print("No notebooks found")
        return 1
    failed = []
    for path in paths:
        nb = json.loads(path.read_text(encoding="utf-8"))
        ok = True
        for i, cell in enumerate(c for c in nb.get("cells", []) if c.get("cell_type") == "code"):
            src = "".join(cell.get("source", []))
            try:
                exec(compile(src, f"{path.name}:{i}", "exec"), {"__name__": "__main__"})
            except Exception as e:
                ok = False
                failed.append((path.name, i, type(e).__name__, str(e)[:120]))
        print(f"{'OK' if ok else 'FAIL'}  {path.name}")
    if failed:
        print("\nFailures:")
        for f in failed:
            print(" ", f)
        return 1
    print(f"\nALL {len(paths)} NOTEBOOKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
