"""
Main benchmark runner for the LQE Ecosystem.
Runs problem × framework × solver combinations with consistent schema.
"""

from __future__ import annotations
import sys
import os
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

# Ensure package imports work when run as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.paths import ensure_lqe_on_path
ensure_lqe_on_path()

from shared.constants import list_problems, get_hamiltonian
from shared.results_schema import BenchmarkResult, validate_result, result_to_dict
from cross_benchmarks.adapters import ADAPTERS, LQEAdapter, QiskitAdapter, CirqAdapter
from cross_benchmarks.problems import get_problem


def run_benchmarks(
    problem_ids: Optional[List[str]] = None,
    frameworks: Optional[List[str]] = None,
    solvers: Optional[List[str]] = None,
    max_iter_vqe: int = 100,
    max_iter_qaoa: int = 80,
    quiet: bool = False,
) -> List[Dict[str, Any]]:
    """
    Run all requested combinations.

    Returns list of result dicts (BenchmarkResult.to_dict()).
    """
    if problem_ids is None:
        problem_ids = list_problems()
    if frameworks is None:
        frameworks = ["lqe", "qiskit", "cirq"]
    if solvers is None:
        solvers = ["exact", "vqe", "qaoa"]

    results: List[Dict[str, Any]] = []
    available = {name: cls.available() for name, cls in ADAPTERS.items()}

    if not quiet:
        print("Available frameworks:", {k: v for k, v in available.items()})
        print(f"Problems: {problem_ids}")
        print(f"Solvers:  {solvers}")
        print("-" * 60)

    for pid in problem_ids:
        try:
            prob = get_problem(pid)
        except KeyError:
            if not quiet:
                print(f"[skip] unknown problem {pid}")
            continue

        n = prob["n_qubits"]
        H = prob["matrix"]
        edges = prob.get("edges")
        ptype = prob.get("type", "spin")

        for fw in frameworks:
            AdapterCls = ADAPTERS.get(fw)
            if AdapterCls is None:
                continue

            adapter = AdapterCls(n, H, problem_id=pid)

            for solver in solvers:
                # Applicability filters
                if solver == "qaoa" and (edges is None or ptype != "maxcut"):
                    continue
                if solver == "vqe" and ptype == "maxcut" and edges is None:
                    pass

                if not quiet:
                    print(f"  {pid:18s} | {fw:7s} | {solver:6s} ...", end=" ", flush=True)

                try:
                    if solver == "exact":
                        res = adapter.solve_exact()
                    elif solver == "vqe":
                        res = adapter.solve_vqe(max_iter=max_iter_vqe)
                    elif solver == "qaoa":
                        res = adapter.solve_qaoa(edges=edges or [], p=1, max_iter=max_iter_qaoa)
                    else:
                        if not quiet:
                            print("skipped (unknown solver)")
                        continue
                except Exception as e:
                    from shared.results_schema import make_error_result
                    res = make_error_result(pid, fw, solver, n, str(e))

                d = result_to_dict(res)
                results.append(d)

                if not quiet:
                    status = "OK" if d.get("converged") else "—"
                    if d.get("metadata", {}).get("error"):
                        status = "ERR"
                    e = d.get("energy")
                    e_str = f"{e:.6f}" if e is not None else "None"
                    print(f"{e_str:>12s}  ({d.get('wall_time_seconds', 0):.3f}s) [{status}]")

    return results


def save_results(results: List[Dict[str, Any]], out_dir: str = "results") -> Path:
    """Write JSON results + return path."""
    out = Path(__file__).resolve().parent / out_dir
    out.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = out / f"benchmark_{ts}.json"
    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    return path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="LQE Ecosystem cross-framework benchmarks")
    parser.add_argument("--problems", nargs="*", default=None, help="Problem IDs (default: all)")
    parser.add_argument("--frameworks", nargs="*", default=["lqe"], help="Frameworks to run")
    parser.add_argument("--solvers", nargs="*", default=["exact", "vqe"], help="Solvers")
    parser.add_argument("--vqe-iter", type=int, default=80)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    results = run_benchmarks(
        problem_ids=args.problems,
        frameworks=args.frameworks,
        solvers=args.solvers,
        max_iter_vqe=args.vqe_iter,
        quiet=args.quiet,
    )
    path = save_results(results)
    print(f"\nSaved {len(results)} results → {path}")

    ok = sum(1 for r in results if r.get("converged"))
    print(f"Converged: {ok}/{len(results)}")


if __name__ == "__main__":
    main()
