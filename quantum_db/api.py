"""
Python API for the quantum Hamiltonian database.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .schema import validate_entry

DATA_DIR = Path(__file__).resolve().parent / "data"


class QuantumDB:
    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR

    def _load_raw(self, entry_id: str) -> dict:
        path = self.data_dir / f"{entry_id}.json"
        if not path.exists():
            path = self.data_dir / entry_id
        if not path.exists():
            raise FileNotFoundError(f"No entry '{entry_id}' in {self.data_dir}")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not validate_entry(data):
            raise ValueError(f"Entry '{entry_id}' failed schema validation")
        return data

    def load(self, entry_id: str) -> dict:
        return self._load_raw(entry_id)

    def list_all(self) -> List[dict]:
        out = []
        for path in sorted(self.data_dir.glob("*.json")):
            try:
                out.append(self._load_raw(path.stem))
            except Exception:
                continue
        return out

    def filter_by_tag(self, tag: str) -> List[dict]:
        return [e for e in self.list_all() if tag in (e.get("tags") or [])]

    def filter_by_n_qubits(self, min_n: int, max_n: int) -> List[dict]:
        return [
            e
            for e in self.list_all()
            if min_n <= e.get("n_qubits", 0) <= max_n
        ]

    def filter_by_type(self, ham_type: str) -> List[dict]:
        return [e for e in self.list_all() if e.get("type") == ham_type]

    def get_exact_energy(self, entry_id: str) -> Optional[float]:
        e = self._load_raw(entry_id)
        exact = e.get("exact") or {}
        val = exact.get("ground_state_energy")
        return float(val) if val is not None else None

    def to_matrix(self, entry_id: str) -> np.ndarray:
        """Reconstruct dense matrix from pauli_sum terms (small n only)."""
        e = self._load_raw(entry_id)
        n = e["n_qubits"]
        ham = e["hamiltonian"]
        if ham.get("format") != "pauli_sum":
            raise ValueError("to_matrix only supports format=pauli_sum")
        dim = 2**n
        H = np.zeros((dim, dim), dtype=complex)
        pauli_map = {
            "I": np.eye(2, dtype=complex),
            "X": np.array([[0, 1], [1, 0]], dtype=complex),
            "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
            "Z": np.array([[1, 0], [0, -1]], dtype=complex),
        }
        for term in ham["terms"]:
            coeff = complex(term["coefficient"])
            pstr = term["pauli"]
            if len(pstr) != n:
                raise ValueError(f"Pauli string length {len(pstr)} != n_qubits {n}")
            op = pauli_map[pstr[0]]
            for ch in pstr[1:]:
                op = np.kron(op, pauli_map[ch])
            H += coeff * op
        return H


def list_entries() -> List[str]:
    return sorted(p.stem for p in DATA_DIR.glob("*.json"))


def load_entry(entry_id: str) -> dict:
    return QuantumDB().load(entry_id)


def query(
    type: Optional[str] = None,
    max_qubits: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> List[dict]:
    db = QuantumDB()
    results = db.list_all()
    if type is not None:
        results = [e for e in results if e.get("type") == type]
    if max_qubits is not None:
        results = [e for e in results if e.get("n_qubits", 999) <= max_qubits]
    if tags:
        results = [e for e in results if set(tags).issubset(set(e.get("tags") or []))]
    return results
