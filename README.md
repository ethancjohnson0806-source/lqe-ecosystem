# LQE Ecosystem

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Engine](https://img.shields.io/badge/Engine-LQE%20v5.0-blue)](https://github.com/ethancjohnson0806-source/Legitimate-Quantum-Engine)

**Benchmarks, educational notebooks, and an interactive web course for the [Legitimate Quantum Engine](https://github.com/ethancjohnson0806-source/Legitimate-Quantum-Engine).**

The LQE Ecosystem turns the engine into a complete learning and reference platform: cross-framework benchmarks to validate results, a curated database of standard quantum problems, 20 hands-on notebooks, and a phone-friendly web course where students write and run real quantum code.

---

## What You Get

| Component | What It Does |
|---|---|
| `cross_benchmarks/` | Run identical problems across LQE, Qiskit, and Cirq; compare accuracy and speed |
| `quantum_db/` | 10 validated Hamiltonians with exact ground-state energies, searchable by tag or qubit count |
| `notebooks/` | 20 lessons: qubits → entanglement → VQE → tensor networks → quantum chemistry → full pipeline |
| `web-course/` | FastAPI backend + vanilla JS frontend — lessons with quizzes and a live code runner |

---

## Quick Start

### 1. Clone Both Repos Side by Side

```bash
git clone https://github.com/ethancjohnson0806-source/Legitimate-Quantum-Engine.git
git clone https://github.com/ethancjohnson0806-source/lqe-ecosystem.git
cd lqe-ecosystem
```

2. Install

```bash
pip install -e .
```

Optional: install web course dependencies:

```bash
pip install -e '.[web]'
```

3. Verify Everything Works

```bash
python -m quantum_db.validator        # 10 PASS
python -m cross_benchmarks            # Generates results/latest_report.html
python tests/run_notebooks.py         # Runs all 20 notebooks
python web-course/backend.py          # Starts on localhost:8000
```

4. Set Custom Engine Path (if needed)

```bash
export LQE_PATH=/path/to/your/engine
```

---

Example: Run a Benchmark

```bash
python -m cross_benchmarks
# Benchmarked 8 configurations
# Report saved to cross_benchmarks/results/latest_report.html
```

Open `cross_benchmarks/results/latest_report.html` in a browser to see comparison tables and bar charts.

---

Example: Query the Database

```python
from quantum_db.api import QuantumDB

db = QuantumDB()
db.list_all()                          # All 10 entries
db.filter_by_tag("ising")              # Ising-type Hamiltonians
db.filter_by_n_qubits(4, 8)            # 4-to-8 qubit range
db.get_exact_energy("TFI_chain_4")     # -3.4641
```

---

Example: Start the Web Course

```bash
pip install -e '.[web]'
python web-course/backend.py
```

Then open `http://localhost:8000` in a browser. Each lesson has text explanations, runnable code blocks, and quizzes. Progress is saved in localStorage.

---

Honest Limitations

- The engine repo must be cloned/importable. The ecosystem does not bundle it.
- Web course requires FastAPI and Uvicorn (`pip install -e '.[web]'`).
- Notebooks use text/ASCII output only. No matplotlib required.
- Benchmark Qiskit/Cirq comparisons only appear if those packages are installed.
- Web course `/api/run` has a 5-second timeout and runs in a subprocess sandbox.
- Quantum DB contains 10 seed entries. Community contributions welcome.

---

License

MIT License — see [LICENSE](LICENSE) for details.
