"""Shared infrastructure for the LQE Ecosystem.
Standard Hamiltonians, results schema, and HTML reporting.
"""

from .constants import STANDARD_HAMILTONIANS, get_hamiltonian
from .results_schema import BenchmarkResult, validate_result, result_to_dict

__all__ = [
    "STANDARD_HAMILTONIANS",
    "get_hamiltonian",
    "BenchmarkResult",
    "validate_result",
    "result_to_dict",
]
