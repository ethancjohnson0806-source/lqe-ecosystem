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
├── tests/               # Notebook runner smoke test
├── pyproject.toml
└── README.md
```

## Setup

The ecosystem depends on the [Legitimate Quantum Engine](https://github.com/ethancjohnson0806-source/Legitimate-Quantum-Engine) but does not modify it. Keep both repos in the same parent directory:

```bash
# 1. Clone both repos side by side
git clone https://github.com/ethancjohnson0806-source/Legitimate-Quantum-Engine.git
git clone https://github.com/ethancjohnson0806-source/lqe-ecosystem.git

# 2. The ecosystem auto-detects the engine via relative paths
cd lqe-ecosystem

# 3. Install ecosystem dependencies
pip install -e .

# 4. (Optional) Install web course dependencies
pip install -e '.[web]'

# 5. Verify everything works
python -m quantum_db.validator        # Should print 10 PASS
python -m cross_benchmarks            # Should generate results/latest_report.html
python tests/run_notebooks.py         # Should run all 20 notebooks
python web-course/backend.py          # Should start on localhost:8000
```

If your engine checkout lives somewhere else, set the path:

```bash
export LQE_PATH=/path/to/your/legitimate_quantum_engine_v5.0
python -m cross_benchmarks
```

Optional: `export LQE_ECOSYSTEM_PATH=/path/to/lqe-ecosystem` if the ecosystem root is non-standard.

## Honest limitations

- The engine repo must be importable. The ecosystem does not bundle it.
- Web course requires FastAPI and Uvicorn (`pip install -e '.[web]'`).
- Notebooks use text/ASCII output only. No matplotlib required.
- Benchmark Qiskit/Cirq comparisons only appear if those packages are installed.
- Web course progress is localStorage only; `/api/run` has a 5s timeout (subprocess, no eval/exec).

## Critical rules followed

- No heavy deps on core paths (FastAPI only for web-course)
- JSON validated against schema before use
- Missing frameworks handled gracefully
- `/api/run` uses subprocess + timeout (no eval/exec)
- LQE engine not modified
- Shared constants used for Hamiltonians (no duplicate hardcoding)
- No hardcoded machine paths (`LQE_PATH` / side-by-side layout only)

---

*LQE Ecosystem · pure where possible · honest limitations*
