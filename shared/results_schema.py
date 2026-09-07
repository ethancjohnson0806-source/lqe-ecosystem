"""
Standard results schema for LQE Ecosystem benchmarks.
Ensures every framework (LQE / Qiskit / Cirq) emits identical structure.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
import json


@dataclass
class BenchmarkResult:
    """Canonical result object produced by every adapter."""

    problem_id: str
    framework: str                 # "lqe" | "qiskit" | "cirq"
    solver: str                    # "vqe" | "qaoa" | "exact" | "dmrg" | ...
    n_qubits: int
    energy: Optional[float] = None
    energy_error: Optional[float] = None
    wall_time_seconds: float = 0.0
    memory_mb: Optional[float] = None
    iterations: Optional[int] = None
    converged: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def result_to_dict(result: BenchmarkResult | Dict[str, Any]) -> Dict[str, Any]:
    """Normalize to plain dict."""
    if isinstance(result, BenchmarkResult):
        return result.to_dict()
    return dict(result)


REQUIRED_FIELDS = {
    "problem_id": str,
    "framework": str,
    "solver": str,
    "n_qubits": int,
}


def validate_result(result: Dict[str, Any]) -> bool:
    """
    Lightweight schema validation.
    Returns True if the result is well-formed enough for reporting.
    """
    if not isinstance(result, dict):
        return False

    for key, typ in REQUIRED_FIELDS.items():
        if key not in result:
            return False
        if not isinstance(result[key], typ):
            return False

    if "energy" in result and result["energy"] is not None:
        if not isinstance(result["energy"], (int, float)):
            return False
    if "energy_error" in result and result["energy_error"] is not None:
        if not isinstance(result["energy_error"], (int, float)):
            return False
    if "wall_time_seconds" in result:
        if not isinstance(result["wall_time_seconds"], (int, float)):
            return False
    if "converged" in result and not isinstance(result["converged"], bool):
        return False

    return True


def make_error_result(
    problem_id: str,
    framework: str,
    solver: str,
    n_qubits: int,
    error_msg: str,
) -> BenchmarkResult:
    """Factory for failed runs so the runner can continue."""
    return BenchmarkResult(
        problem_id=problem_id,
        framework=framework,
        solver=solver,
        n_qubits=n_qubits,
        energy=None,
        energy_error=None,
        wall_time_seconds=0.0,
        converged=False,
        metadata={"error": error_msg},
    )
