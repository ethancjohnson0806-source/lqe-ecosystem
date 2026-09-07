"""
Framework adapters with identical public API.
LQE is always available (pure NumPy core).
Qiskit and Cirq are optional and degrade gracefully.
"""

from __future__ import annotations
import time
import sys
import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# Make the sibling shared package importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.results_schema import BenchmarkResult, make_error_result
from shared.constants import get_hamiltonian


# ---------------------------------------------------------------------------
# Optional memory tracking
# ---------------------------------------------------------------------------
try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


def _memory_mb() -> Optional[float]:
    if not _HAS_PSUTIL:
        return None
    try:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# LQE Adapter (always available when the engine is on PYTHONPATH)
# ---------------------------------------------------------------------------

class LQEAdapter:
    """Adapter for Legitimate Quantum Engine."""

    def __init__(self, n_qubits: int, hamiltonian: np.ndarray, problem_id: str = "unknown"):
        self.n = n_qubits
        self.H = np.asarray(hamiltonian, dtype=complex)
        self.problem_id = problem_id
        self._lqe = None
        self._available = self._try_import()

    def _try_import(self) -> bool:
        try:
            from shared.paths import ensure_lqe_on_path
            ensure_lqe_on_path()
            import legitimate_quantum_engine as lqe  # noqa: F401
            self._lqe = lqe
            return True
        except Exception:
            return False

    @staticmethod
    def available() -> bool:
        try:
            from shared.paths import ensure_lqe_on_path
            ensure_lqe_on_path()
            import legitimate_quantum_engine  # noqa: F401
            return True
        except Exception:
            return False

    def solve_exact(self) -> BenchmarkResult:
        t0 = time.perf_counter()
        mem0 = _memory_mb()
        try:
            evals = np.linalg.eigvalsh(self.H)
            energy = float(np.min(np.real(evals)))
            dt = time.perf_counter() - t0
            mem1 = _memory_mb()
            return BenchmarkResult(
                problem_id=self.problem_id,
                framework="lqe",
                solver="exact",
                n_qubits=self.n,
                energy=energy,
                energy_error=0.0,
                wall_time_seconds=dt,
                memory_mb=(mem1 - mem0) if (mem0 and mem1) else mem1,
                iterations=None,
                converged=True,
                metadata={"method": "dense_eigvalsh"},
            )
        except Exception as e:
            return make_error_result(self.problem_id, "lqe", "exact", self.n, str(e))

    def solve_vqe(self, max_iter: int = 200) -> BenchmarkResult:
        if not self._available:
            return make_error_result(self.problem_id, "lqe", "vqe", self.n, "LQE not importable")

        t0 = time.perf_counter()
        mem0 = _memory_mb()
        try:
            from legitimate_quantum_engine.solvers.vqe_ground import VQE
            vqe = VQE(self.n, self.H, num_layers=2, max_iterations=max_iter)
            out = vqe.solve(verbose=False)
            dt = time.perf_counter() - t0
            mem1 = _memory_mb()
            return BenchmarkResult(
                problem_id=self.problem_id,
                framework="lqe",
                solver="vqe",
                n_qubits=self.n,
                energy=float(out["energy"]),
                energy_error=float(out.get("error", abs(out["energy"] - out.get("exact", out["energy"])))),
                wall_time_seconds=dt,
                memory_mb=(mem1 - mem0) if (mem0 and mem1) else mem1,
                iterations=max_iter,
                converged=bool(out.get("converged", False)),
                metadata={
                    "exact": out.get("exact"),
                    "relative_error": out.get("relative_error"),
                    "status": out.get("status"),
                },
            )
        except Exception as e:
            return make_error_result(self.problem_id, "lqe", "vqe", self.n, str(e))

    def solve_qaoa(self, edges: List[Tuple[int, int]], p: int = 1, max_iter: int = 100) -> BenchmarkResult:
        if not self._available:
            return make_error_result(self.problem_id, "lqe", "qaoa", self.n, "LQE not importable")

        t0 = time.perf_counter()
        mem0 = _memory_mb()
        try:
            from legitimate_quantum_engine.solvers.qaoa import QAOA
            qaoa = QAOA(self.n, edges, p=p, max_iterations=max_iter)
            out = qaoa.solve(verbose=False)
            dt = time.perf_counter() - t0
            mem1 = _memory_mb()
            return BenchmarkResult(
                problem_id=self.problem_id,
                framework="lqe",
                solver="qaoa",
                n_qubits=self.n,
                energy=float(out["energy"]),
                energy_error=float(out.get("error", 0.0)),
                wall_time_seconds=dt,
                memory_mb=(mem1 - mem0) if (mem0 and mem1) else mem1,
                iterations=max_iter,
                converged=bool(out.get("converged", False)),
                metadata={"p": p, "exact": out.get("exact")},
            )
        except Exception as e:
            return make_error_result(self.problem_id, "lqe", "qaoa", self.n, str(e))


# ---------------------------------------------------------------------------
# Qiskit Adapter (optional)
# ---------------------------------------------------------------------------

class QiskitAdapter:
    def __init__(self, n_qubits: int, hamiltonian: np.ndarray, problem_id: str = "unknown"):
        self.n = n_qubits
        self.H = np.asarray(hamiltonian, dtype=complex)
        self.problem_id = problem_id

    @staticmethod
    def available() -> bool:
        try:
            import qiskit  # noqa: F401
            return True
        except ImportError:
            return False

    def solve_exact(self) -> BenchmarkResult:
        if not self.available():
            return make_error_result(self.problem_id, "qiskit", "exact", self.n, "qiskit not installed")
        t0 = time.perf_counter()
        try:
            energy = float(np.min(np.real(np.linalg.eigvalsh(self.H))))
            return BenchmarkResult(
                problem_id=self.problem_id,
                framework="qiskit",
                solver="exact",
                n_qubits=self.n,
                energy=energy,
                energy_error=0.0,
                wall_time_seconds=time.perf_counter() - t0,
                converged=True,
                metadata={"note": "NumPy backend (qiskit primitives not required for exact)"},
            )
        except Exception as e:
            return make_error_result(self.problem_id, "qiskit", "exact", self.n, str(e))

    def solve_vqe(self, max_iter: int = 200) -> BenchmarkResult:
        if not self.available():
            return make_error_result(self.problem_id, "qiskit", "vqe", self.n, "qiskit not installed")
        return make_error_result(
            self.problem_id, "qiskit", "vqe", self.n,
            "Qiskit VQE path not yet wired in this foundation build (optional dependency)"
        )

    def solve_qaoa(self, edges: List[Tuple[int, int]], p: int = 1, max_iter: int = 100) -> BenchmarkResult:
        if not self.available():
            return make_error_result(self.problem_id, "qiskit", "qaoa", self.n, "qiskit not installed")
        return make_error_result(
            self.problem_id, "qiskit", "qaoa", self.n,
            "Qiskit QAOA path not yet wired in this foundation build (optional dependency)"
        )


# ---------------------------------------------------------------------------
# Cirq Adapter (optional)
# ---------------------------------------------------------------------------

class CirqAdapter:
    def __init__(self, n_qubits: int, hamiltonian: np.ndarray, problem_id: str = "unknown"):
        self.n = n_qubits
        self.H = np.asarray(hamiltonian, dtype=complex)
        self.problem_id = problem_id

    @staticmethod
    def available() -> bool:
        try:
            import cirq  # noqa: F401
            return True
        except ImportError:
            return False

    def solve_exact(self) -> BenchmarkResult:
        if not self.available():
            return make_error_result(self.problem_id, "cirq", "exact", self.n, "cirq not installed")
        t0 = time.perf_counter()
        try:
            energy = float(np.min(np.real(np.linalg.eigvalsh(self.H))))
            return BenchmarkResult(
                problem_id=self.problem_id,
                framework="cirq",
                solver="exact",
                n_qubits=self.n,
                energy=energy,
                energy_error=0.0,
                wall_time_seconds=time.perf_counter() - t0,
                converged=True,
                metadata={"note": "NumPy backend"},
            )
        except Exception as e:
            return make_error_result(self.problem_id, "cirq", "exact", self.n, str(e))

    def solve_vqe(self, max_iter: int = 200) -> BenchmarkResult:
        if not self.available():
            return make_error_result(self.problem_id, "cirq", "vqe", self.n, "cirq not installed")
        return make_error_result(
            self.problem_id, "cirq", "vqe", self.n,
            "Cirq VQE path not yet wired in this foundation build (optional dependency)"
        )

    def solve_qaoa(self, edges: List[Tuple[int, int]], p: int = 1, max_iter: int = 100) -> BenchmarkResult:
        if not self.available():
            return make_error_result(self.problem_id, "cirq", "qaoa", self.n, "cirq not installed")
        return make_error_result(
            self.problem_id, "cirq", "qaoa", self.n,
            "Cirq QAOA path not yet wired in this foundation build (optional dependency)"
        )


# Convenience map
ADAPTERS = {
    "lqe": LQEAdapter,
    "qiskit": QiskitAdapter,
    "cirq": CirqAdapter,
}
