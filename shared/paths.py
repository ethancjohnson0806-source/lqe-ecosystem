"""
Portable path resolution for the LQE engine and ecosystem root.

Layout expected (side-by-side clones):

    parent/
      legitimate_quantum_engine_v5.0/   # or set LQE_PATH
      lqe-ecosystem/

Environment overrides:
  LQE_PATH              — directory containing the legitimate_quantum_engine package
  LQE_ECOSYSTEM_PATH    — ecosystem repo root (this project)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# lqe-ecosystem/shared/paths.py → ecosystem root is parent of shared/
_ECOSYSTEM_ROOT = Path(__file__).resolve().parent.parent
_PARENT = _ECOSYSTEM_ROOT.parent


def ecosystem_root() -> Path:
    env = os.environ.get("LQE_ECOSYSTEM_PATH")
    if env:
        return Path(env).resolve()
    return _ECOSYSTEM_ROOT


def lqe_path() -> Path:
    env = os.environ.get("LQE_PATH")
    if env:
        return Path(env).resolve()
    # Side-by-side default
    sibling = _PARENT / "legitimate_quantum_engine_v5.0"
    if sibling.is_dir():
        return sibling
    # Common alternate names
    for name in (
        "Legitimate-Quantum-Engine",
        "legitimate_quantum_engine",
        "lqe",
    ):
        alt = _PARENT / name
        if alt.is_dir():
            return alt
    # Last resort: sibling path even if missing (caller may still have PYTHONPATH)
    return sibling


def ensure_lqe_on_path() -> str:
    """Insert LQE package root on sys.path if needed. Returns the path used."""
    path = str(lqe_path())
    if path not in sys.path:
        sys.path.insert(0, path)
    eco = str(ecosystem_root())
    if eco not in sys.path:
        sys.path.insert(0, eco)
    return path
