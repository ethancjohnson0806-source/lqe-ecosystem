"""
python -m cross_benchmarks
Runs LQE benchmarks (Qiskit/Cirq skipped if absent) and writes HTML report.
"""

from __future__ import annotations
import sys
from pathlib import Path

# Ensure LQE and package root are importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from shared.paths import ensure_lqe_on_path
ensure_lqe_on_path()

from cross_benchmarks.runner import run_benchmarks, save_results
from cross_benchmarks.report import generate_report


def main():
    # Default: LQE only, exact + vqe, a representative subset for speed
    # Full suite can be requested via CLI flags on runner
    results = run_benchmarks(
        problem_ids=["TFI_chain_4", "Heisenberg_4", "MaxCut_triangle", "Grover_3bit"],
        frameworks=["lqe"],
        solvers=["exact", "vqe"],
        max_iter_vqe=60,
        quiet=False,
    )
    out_dir = Path(__file__).resolve().parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = save_results(results, out_dir=str(out_dir))
    html_path = out_dir / "latest_report.html"
    generate_report(results, str(html_path))
    print(f"Benchmarked {len(results)} configurations")
    print(f"Report saved to {html_path}")
    print(f"JSON saved to {json_path}")


if __name__ == "__main__":
    main()
