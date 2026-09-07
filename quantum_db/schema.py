"""
JSON schema and validation for Hamiltonian entries (quantum-db).
Matches LQE Ecosystem Build Plan v1.0 Part 3.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import json
from pathlib import Path


REQUIRED_TOP = {"id", "name", "description", "type", "n_qubits", "hamiltonian", "tags"}
ALLOWED_TYPES = {"spin", "fermionic", "maxcut", "oracle"}
ALLOWED_FORMATS = {"pauli_sum", "matrix"}


def validate_entry(entry: dict) -> bool:
    """Return True if entry satisfies the minimal schema."""
    if not isinstance(entry, dict):
        return False
    if not REQUIRED_TOP.issubset(entry.keys()):
        return False
    if not isinstance(entry["id"], str) or not entry["id"]:
        return False
    if not isinstance(entry["name"], str):
        return False
    if not isinstance(entry["description"], str):
        return False
    if entry["type"] not in ALLOWED_TYPES:
        return False
    if not isinstance(entry["n_qubits"], int) or entry["n_qubits"] < 1:
        return False
    if not isinstance(entry["tags"], list):
        return False

    ham = entry.get("hamiltonian")
    if not isinstance(ham, dict):
        return False
    if ham.get("format") not in ALLOWED_FORMATS:
        return False
    if ham["format"] == "pauli_sum":
        terms = ham.get("terms")
        if not isinstance(terms, list) or len(terms) == 0:
            return False
        for t in terms:
            if not isinstance(t, dict):
                return False
            if "coefficient" not in t or "pauli" not in t:
                return False
            if not isinstance(t["pauli"], str):
                return False

    exact = entry.get("exact")
    if exact is not None:
        if not isinstance(exact, dict):
            return False
        if "ground_state_energy" in exact and not isinstance(
            exact["ground_state_energy"], (int, float)
        ):
            return False

    return True


def validate_all(data_dir: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Walk data_dir, validate every .json.
    Returns (passed, failed, errors).
    """
    passed: List[str] = []
    failed: List[str] = []
    errors: List[str] = []
    root = Path(data_dir)
    if not root.exists():
        return [], [], [f"data_dir does not exist: {data_dir}"]

    for path in sorted(root.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if validate_entry(data):
                passed.append(path.name)
            else:
                failed.append(path.name)
                errors.append(f"{path.name}: schema validation failed")
        except Exception as e:
            failed.append(path.name)
            errors.append(f"{path.name}: {e}")

    return passed, failed, errors
