"""
Validator CLI for quantum-db data files.
Usage: python -m quantum_db.validator
Exits 0 if all PASS, 1 if any FAIL.
"""

from __future__ import annotations
import sys
from pathlib import Path

from .schema import validate_all

DATA_DIR = Path(__file__).resolve().parent / "data"


def main() -> int:
    passed, failed, errors = validate_all(str(DATA_DIR))
    for name in passed:
        print(f"PASS  {name}")
    for name in failed:
        print(f"FAIL  {name}")
    for err in errors:
        print(f"  -> {err}")
    print(f"\n{len(passed)} passed, {len(failed)} failed")
    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
