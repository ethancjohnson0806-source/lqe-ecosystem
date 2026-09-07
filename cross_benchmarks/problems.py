"""Load standard benchmark problems from shared.constants."""

from __future__ import annotations
import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.constants import STANDARD_HAMILTONIANS, get_hamiltonian, list_problems


def get_problem(problem_id: str) -> Dict[str, Any]:
    """Return the full problem dict (includes matrix, edges when present, etc.)."""
    return get_hamiltonian(problem_id)


def all_problem_ids() -> List[str]:
    return list_problems()
