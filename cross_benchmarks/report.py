"""
HTML + JSON report generator for benchmark results.
"""

from __future__ import annotations
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.html_template import generate_html_report
from shared.results_schema import validate_result


def _fmt(x: Any, digits: int = 6) -> str:
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{digits}f}"
    return str(x)


def build_report_sections(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Turn raw results into report sections."""
    sections = []

    total = len(results)
    converged = sum(1 for r in results if r.get("converged"))
    by_fw = defaultdict(int)
    by_solver = defaultdict(int)
    for r in results:
        by_fw[r.get("framework", "?")] += 1
        by_solver[r.get("solver", "?")] += 1

    summary_rows = [
        ["Metric", "Value"],
        ["Total runs", str(total)],
        ["Converged", f"{converged} ({100*converged/total:.0f}%)" if total else "0"],
        ["Frameworks", ", ".join(f"{k}:{v}" for k, v in sorted(by_fw.items()))],
        ["Solvers", ", ".join(f"{k}:{v}" for k, v in sorted(by_solver.items()))],
    ]
    sections.append({"heading": "Summary", "table": summary_rows})

    header = ["Problem", "Framework", "Solver", "n", "Energy", "Error", "Time (s)", "Converged"]
    rows = [header]
    for r in sorted(results, key=lambda x: (x.get("problem_id", ""), x.get("framework", ""), x.get("solver", ""))):
        rows.append([
            r.get("problem_id", ""),
            r.get("framework", ""),
            r.get("solver", ""),
            str(r.get("n_qubits", "")),
            _fmt(r.get("energy")),
            _fmt(r.get("energy_error"), 4),
            _fmt(r.get("wall_time_seconds"), 3),
            "✓" if r.get("converged") else "✗",
        ])
    sections.append({"heading": "All Results", "table": rows})

    errors = [r for r in results if r.get("metadata", {}).get("error")]
    if errors:
        err_rows = [["Problem", "Framework", "Solver", "Error"]]
        for r in errors:
            err_rows.append([
                r.get("problem_id", ""),
                r.get("framework", ""),
                r.get("solver", ""),
                str(r.get("metadata", {}).get("error", ""))[:80],
            ])
        sections.append({"heading": "Errors / Skipped", "table": err_rows})

    return sections


def generate_benchmark_report(
    results: List[Dict[str, Any]],
    title: str = "LQE Ecosystem Cross-Framework Benchmark",
    out_path: Optional[str] = None,
) -> str:
    """Generate HTML report string; optionally write to disk."""
    valid = [r for r in results if validate_result(r)]
    sections = build_report_sections(valid)
    html = generate_html_report(
        title=title,
        sections=sections,
        subtitle=f"{len(valid)} runs · pure where possible · honest limitations",
    )
    if out_path:
        Path(out_path).write_text(html, encoding="utf-8")
    return html


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="Path to benchmark_*.json")
    parser.add_argument("-o", "--output", default=None, help="Output HTML path")
    args = parser.parse_args()

    with open(args.json_file) as f:
        results = json.load(f)

    out = args.output
    if out is None:
        out = str(Path(args.json_file).with_suffix(".html"))

    generate_benchmark_report(results, out_path=out)
    print(f"Report written → {out}")


if __name__ == "__main__":
    main()


def generate_report(results, output_path) -> None:
    """Plan API: write HTML report to output_path."""
    generate_benchmark_report(results, out_path=output_path)
