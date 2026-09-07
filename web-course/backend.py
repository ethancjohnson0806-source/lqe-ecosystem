"""
LQE Ecosystem Web Course backend (FastAPI).
Endpoints:
  GET  /                  -> static/index.html
  GET  /api/lessons       -> list lessons
  GET  /api/lessons/{id}  -> full lesson JSON
  POST /api/run           -> execute restricted Python (subprocess + timeout)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
LESSONS_DIR = ROOT / "lessons"
STATIC_DIR = ROOT / "static"
sys.path.insert(0, str(ROOT.parent))
from shared.paths import lqe_path, ecosystem_root
LQE_PATH = str(lqe_path())
ECO_PATH = str(ecosystem_root())

app = FastAPI(title="LQE Web Course", version="1.0")


def _load_all_lessons() -> List[Dict[str, Any]]:
    lessons = []
    for path in sorted(LESSONS_DIR.glob("lesson_*.json")):
        with open(path, encoding="utf-8") as f:
            lessons.append(json.load(f))
    return lessons


def _find_lesson(lesson_id: str) -> Dict[str, Any] | None:
    for path in LESSONS_DIR.glob("lesson_*.json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("id") == lesson_id:
            return data
    return None


@app.get("/api/lessons")
def list_lessons():
    items = [
        {"id": L["id"], "title": L["title"], "duration_minutes": L.get("duration_minutes", 10)}
        for L in _load_all_lessons()
    ]
    return items


@app.get("/api/lessons/{lesson_id}")
def get_lesson(lesson_id: str):
    data = _find_lesson(lesson_id)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")
    return data


class RunRequest(BaseModel):
    code: str = Field(..., max_length=8000)


_BLOCKED = re.compile(
    r"\b(eval|exec|__import__|compile|open|input|breakpoint|os\.system|subprocess|"
    r"socket|requests|urllib|pathlib|shutil|ctypes|multiprocessing|pickle|marshal)\b"
)


def _is_code_safe(code: str) -> tuple[bool, str]:
    if _BLOCKED.search(code):
        return False, "Blocked builtin or module referenced"
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            if not (
                stripped.startswith("import sys")
                or stripped.startswith("import numpy")
                or "legitimate_quantum_engine" in stripped
                or "numpy" in stripped
                or "quantum_db" in stripped
            ):
                if not re.match(r"import\s+numpy(\s+as\s+\w+)?", stripped):
                    if not re.match(r"from\s+numpy", stripped):
                        if "legitimate_quantum_engine" not in stripped and "quantum_db" not in stripped:
                            return False, f"Import not allowed: {stripped[:60]}"
    return True, ""


@app.post("/api/run")
def run_code(req: RunRequest):
    ok, reason = _is_code_safe(req.code)
    if not ok:
        return JSONResponse({"stdout": "", "stderr": f"Security: {reason}", "success": False})

    preamble = (
        "import sys\n"
        f"sys.path.insert(0, {LQE_PATH!r})\n"
        f"sys.path.insert(0, {ECO_PATH!r})\n"
    )
    full = preamble + req.code

    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
            tf.write(full)
            tf_path = tf.name
        try:
            proc = subprocess.run(
                [sys.executable, tf_path],
                capture_output=True,
                text=True,
                timeout=5,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "NO_PROXY": "*"},
            )
            return {
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-2000:],
                "success": proc.returncode == 0,
            }
        finally:
            try:
                os.unlink(tf_path)
            except OSError:
                pass
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Timeout: exceeded 5 seconds", "success": False}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "success": False}


@app.get("/")
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html missing")
    return FileResponse(index_path)


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
