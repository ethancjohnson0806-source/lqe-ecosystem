# LQE Ecosystem

Foundation for standardized quantum education access and prototyping.

**Philosophy**: pure where possible · honest limitations · test-first

Built against **LQE Ecosystem Build Plan v1.0**. Does **not** modify the LQE engine.

## Status (v1.0 foundation)

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | `shared/` constants, results schema, HTML template | ✓ |
| 1 | `quantum_db/` schema, API, CLI, validator, 10 JSON entries | ✓ |
| 2 | `cross_benchmarks/` adapters, runner, report | ✓ |
| 3 | `notebooks/` 01–20 | ✓ (code cells pass) |
| 4 | `web-course/` lessons, FastAPI backend, static SPA | ✓ |
| 5 | `README.md`, `pyproject.toml`, integration smoke tests | ✓ |

## Layout

```
lqe-ecosystem/
├── shared/              # Hamiltonians, BenchmarkResult, HTML reports
├── quantum_db/          # Schema + API + CLI + data/*.json
├── cross_benchmarks/    # LQE/Qiskit/Cirq adapters, runner, report
├── notebooks/           # 20 teaching notebooks (numpy + LQE only)
├── web-course/          # FastAPI + vanilla JS course
├── pyproject.toml
└── README.md
```

## Prerequisites

- Python 3.10+
- NumPy
- Optional: FastAPI + uvicorn (web course only)
- Optional: Qiskit / Cirq (cross-benchmarks compare only if installed)

## Setup

Clone this repo **and** the LQE engine repo into the **same parent directory**:

```bash
parent/
  legitimate_quantum_engine_v5.0/   # LQE engine
  lqe-ecosystem/                    # this repo
```

Or set an explicit path:

```bash
export LQE_PATH=/path/to/legitimate_quantum_engine_v5.0
# optional: export LQE_ECOSYSTEM_PATH=/path/to/lqe-ecosystem
```

No hardcoded machine paths are required.

## Quick start

```bash
cd lqe-ecosystem

# Quantum DB
python -m quantum_db.validator          # 10 PASS
python -m quantum_db.cli list

# Cross-benchmarks (LQE only if Qiskit/Cirq absent)
python -m cross_benchmarks              # writes results/latest_report.html

# Web course
pip install fastapi uvicorn             # once
python web-course/backend.py            # http://localhost:8000
```

## Smoke tests (Build Plan Part 6)

1. **Cross-benchmarks** — `python -m cross_benchmarks`  
   → LQE runs even without Qiskit/Cirq; produces `results/latest_report.html`

2. **Quantum DB** — `python -m quantum_db.validator`  
   → 10 PASS, exit 0; `python -m quantum_db.cli list` → 10 names

3. **Notebooks** — extract code cells and execute  
   → all 20 notebooks run without error (numpy + LQE)

4. **Web course** — backend on :8000  
   - `curl localhost:8000/api/lessons` → JSON list  
   - `POST /api/run` with StatevectorSim snippet → stdout statevector

## Honest limitations

| Area | Limitation |
|------|------------|
| Cross-benchmarks | Qiskit/Cirq only if installed; stubs otherwise |
| Quantum DB | 10 seed entries; no contribution UI |
| Notebooks | No matplotlib — ASCII/text only |
| Web course | localStorage progress; `/api/run` 5s timeout, soft sandbox |
| All | Requires LQE engine importable |

## Critical rules followed

- No heavy deps on core paths (FastAPI only for web-course)
- JSON validated against schema before use
- Missing frameworks handled gracefully
- `/api/run` uses subprocess + timeout (no eval/exec)
- LQE engine not modified
- Shared constants used for Hamiltonians (no duplicate hardcoding)

---

*LQE Ecosystem · pure where possible · honest limitations*
