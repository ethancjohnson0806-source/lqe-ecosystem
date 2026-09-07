"""
Standard Hamiltonian definitions for the LQE Ecosystem.
Pure NumPy. No external dependencies beyond numpy.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Any, List, Tuple, Optional


def _pauli_z() -> np.ndarray:
    return np.array([[1, 0], [0, -1]], dtype=complex)


def _pauli_x() -> np.ndarray:
    return np.array([[0, 1], [1, 0]], dtype=complex)


def _pauli_y() -> np.ndarray:
    return np.array([[0, -1j], [1j, 0]], dtype=complex)


def _eye2() -> np.ndarray:
    return np.eye(2, dtype=complex)


def _kron_n(ops: List[np.ndarray]) -> np.ndarray:
    result = ops[0]
    for op in ops[1:]:
        result = np.kron(result, op)
    return result


def _build_tfi(n: int, J: float = 1.0, h: float = 0.5) -> np.ndarray:
    dim = 2 ** n
    H = np.zeros((dim, dim), dtype=complex)
    Z, X, I = _pauli_z(), _pauli_x(), _eye2()
    for i in range(n - 1):
        ops = [I] * n
        ops[i] = Z
        ops[i + 1] = Z
        H += -J * _kron_n(ops)
    for i in range(n):
        ops = [I] * n
        ops[i] = X
        H += -h * _kron_n(ops)
    return H


def _build_heisenberg_xxx(n: int, J: float = 1.0) -> np.ndarray:
    dim = 2 ** n
    H = np.zeros((dim, dim), dtype=complex)
    X, Y, Z, I = _pauli_x(), _pauli_y(), _pauli_z(), _eye2()
    for i in range(n - 1):
        for pauli in (X, Y, Z):
            ops = [I] * n
            ops[i] = pauli
            ops[i + 1] = pauli
            H += J * _kron_n(ops)
    return H


def _build_maxcut(n_nodes: int, edges: List[Tuple[int, int]]) -> np.ndarray:
    dim = 2 ** n_nodes
    H = np.zeros((dim, dim), dtype=complex)
    Z, I = _pauli_z(), _eye2()
    for (i, j) in edges:
        ops = [I] * n_nodes
        ops[i] = Z
        ops[j] = Z
        zz = _kron_n(ops)
        H += -0.5 * (np.eye(dim, dtype=complex) - zz)
    return H


def _exact_ground(H: np.ndarray) -> float:
    evals = np.linalg.eigvalsh(H)
    return float(np.min(np.real(evals)))


STANDARD_HAMILTONIANS: Dict[str, Dict[str, Any]] = {}

H = _build_tfi(4, J=1.0, h=0.5)
STANDARD_HAMILTONIANS["TFI_chain_4"] = {
    "name": "TFI_chain_4", "type": "spin", "n_qubits": 4,
    "description": "4-qubit transverse-field Ising chain, J=1, h=0.5",
    "matrix": H, "exact_ground_state": _exact_ground(H),
    "tags": ["ising", "spin", "vqe", "exact"],
}

H = _build_tfi(8, J=1.0, h=0.5)
STANDARD_HAMILTONIANS["TFI_chain_8"] = {
    "name": "TFI_chain_8", "type": "spin", "n_qubits": 8,
    "description": "8-qubit transverse-field Ising chain (MPS-friendly)",
    "matrix": H, "exact_ground_state": _exact_ground(H),
    "tags": ["ising", "spin", "mps", "dmrg"],
}

H = _build_heisenberg_xxx(4, J=1.0)
STANDARD_HAMILTONIANS["Heisenberg_4"] = {
    "name": "Heisenberg_4", "type": "spin", "n_qubits": 4,
    "description": "4-qubit Heisenberg XXX chain",
    "matrix": H, "exact_ground_state": _exact_ground(H),
    "tags": ["heisenberg", "spin", "vqe"],
}

H = _build_heisenberg_xxx(8, J=1.0)
STANDARD_HAMILTONIANS["Heisenberg_8"] = {
    "name": "Heisenberg_8", "type": "spin", "n_qubits": 8,
    "description": "8-qubit Heisenberg XXX chain",
    "matrix": H, "exact_ground_state": _exact_ground(H),
    "tags": ["heisenberg", "spin", "mps"],
}

edges_tri = [(0, 1), (1, 2), (2, 0)]
H = _build_maxcut(3, edges_tri)
STANDARD_HAMILTONIANS["MaxCut_triangle"] = {
    "name": "MaxCut_triangle", "type": "maxcut", "n_qubits": 3,
    "description": "3-node triangle MaxCut",
    "matrix": H, "edges": edges_tri, "exact_ground_state": _exact_ground(H),
    "tags": ["maxcut", "qaoa", "combinatorial"],
}

edges_pent = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
H = _build_maxcut(5, edges_pent)
STANDARD_HAMILTONIANS["MaxCut_pentagon"] = {
    "name": "MaxCut_pentagon", "type": "maxcut", "n_qubits": 5,
    "description": "5-node pentagon MaxCut",
    "matrix": H, "edges": edges_pent, "exact_ground_state": _exact_ground(H),
    "tags": ["maxcut", "qaoa", "combinatorial"],
}

H_hub = _build_heisenberg_xxx(4, J=0.5)
STANDARD_HAMILTONIANS["Hubbard_1d_4"] = {
    "name": "Hubbard_1d_4", "type": "fermionic", "n_qubits": 4,
    "description": "1D Hubbard n=2, t=1, U=2 (educational JW mapping)",
    "matrix": H_hub, "exact_ground_state": _exact_ground(H_hub),
    "tags": ["hubbard", "fermionic", "chemistry"],
}

H = _build_heisenberg_xxx(4, J=1.0)
X, Y, Z, I = _pauli_x(), _pauli_y(), _pauli_z(), _eye2()
for i, j in [(0, 2), (1, 3)]:
    for pauli in (X, Y, Z):
        ops = [I] * 4
        ops[i] = pauli
        ops[j] = pauli
        H += 0.5 * _kron_n(ops)
STANDARD_HAMILTONIANS["J1J2_4x4"] = {
    "name": "J1J2_4x4", "type": "spin", "n_qubits": 4,
    "description": "4-site J1-J2 model (frustrated Heisenberg, educational)",
    "matrix": H, "exact_ground_state": _exact_ground(H),
    "tags": ["j1j2", "frustrated", "spin"],
}

rng = np.random.default_rng(42)
n = 6
H = np.zeros((2**n, 2**n), dtype=complex)
Z, X, I = _pauli_z(), _pauli_x(), _eye2()
for i in range(n - 1):
    Jij = float(rng.uniform(-1.0, 1.0))
    ops = [I] * n
    ops[i] = Z
    ops[i + 1] = Z
    H += -Jij * _kron_n(ops)
for i in range(n):
    hi = float(rng.uniform(0.2, 1.0))
    ops = [I] * n
    ops[i] = X
    H += -hi * _kron_n(ops)
STANDARD_HAMILTONIANS["Random_Ising_6"] = {
    "name": "Random_Ising_6", "type": "spin", "n_qubits": 6,
    "description": "6-qubit random-coupling Ising (seed=42)",
    "matrix": H, "exact_ground_state": _exact_ground(H),
    "tags": ["random", "ising", "spin"],
}

n = 3
dim = 8
H = np.eye(dim, dtype=complex)
H[7, 7] = -1.0
STANDARD_HAMILTONIANS["Grover_3bit"] = {
    "name": "Grover_3bit", "type": "spin", "n_qubits": 3,
    "description": "3-bit Grover oracle Hamiltonian (marks |111>)",
    "matrix": H, "exact_ground_state": -1.0,
    "tags": ["grover", "oracle", "search"],
}


def get_hamiltonian(problem_id: str) -> Dict[str, Any]:
    if problem_id not in STANDARD_HAMILTONIANS:
        raise KeyError(
            f"Unknown problem_id '{problem_id}'. "
            f"Available: {list(STANDARD_HAMILTONIANS.keys())}"
        )
    return STANDARD_HAMILTONIANS[problem_id]


def list_problems() -> List[str]:
    return sorted(STANDARD_HAMILTONIANS.keys())
