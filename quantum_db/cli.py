"""
CLI for quantum-db.
python -m quantum_db.cli list
python -m quantum_db.cli list --tag ising
python -m quantum_db.cli show tfi_chain_4
python -m quantum_db.cli validate
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from .api import QuantumDB, list_entries
from .schema import validate_all


def main():
    parser = argparse.ArgumentParser(description="LQE Quantum Hamiltonian DB")
    sub = parser.add_subparsers(dest="cmd")

    p_list = sub.add_parser("list", help="List entries")
    p_list.add_argument("--tag", default=None)

    p_show = sub.add_parser("show", help="Show one entry")
    p_show.add_argument("id")

    sub.add_parser("validate", help="Validate all data files")

    args = parser.parse_args()
    db = QuantumDB()

    if args.cmd == "list":
        if args.tag:
            for e in db.filter_by_tag(args.tag):
                print(e["id"])
        else:
            for eid in list_entries():
                print(eid)
    elif args.cmd == "show":
        print(json.dumps(db.load(args.id), indent=2))
    elif args.cmd == "validate":
        data_dir = Path(__file__).resolve().parent / "data"
        passed, failed, errors = validate_all(str(data_dir))
        for name in passed:
            print(f"PASS  {name}")
        for name in failed:
            print(f"FAIL  {name}")
        for err in errors:
            print(f"  -> {err}")
        print(f"\n{len(passed)} passed, {len(failed)} failed")
        sys.exit(0 if not failed else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
