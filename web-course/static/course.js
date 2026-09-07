/* LQE Web Course — vanilla JS */

const state = {
  lessons: [],
  currentId: null,
  progress: JSON.parse(localStorage.getItem("lqe_course_progress") || "{}"),
};

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function trackProgress(id) {
  state.progress[id] = true;
  localStorage.setItem("lqe_course_progress", JSON.stringify(state.progress));
  renderSidebar();
}

function renderSidebar() {
  const el = document.getElementById("lesson-list");
  el.innerHTML = "";
  state.lessons.forEach((L) => {
    const btn = document.createElement("button");
    btn.className = "lesson-item";
    if (L.id === state.currentId) btn.classList.add("active");
    if (state.progress[L.id]) btn.classList.add("done");
    btn.innerHTML = `<div>${L.title}</div><div class="dur">${L.duration_minutes || "?"} min · ${L.id}</div>`;
    btn.onclick = () => loadLesson(L.id);
    el.appendChild(btn);
  });
}

function renderSection(sec, idx) {
  const wrap = document.createElement("div");
  wrap.className = `section ${sec.type}`;

  if (sec.type === "text") {
    const p = document.createElement("p");
    p.textContent = sec.content;
    wrap.appendChild(p);
  } else if (sec.type === "code") {
    if (sec.description) {
      const d = document.createElement("div");
      d.className = "desc";
      d.textContent = sec.description;
      wrap.appendChild(d);
    }
    const pre = document.createElement("pre");
    pre.textContent = sec.code;
    wrap.appendChild(pre);
    const btn = document.createElement("button");
    btn.className = "btn-run";
    btn.textContent = "Run";
    const out = document.createElement("div");
    out.className = "output";
    out.style.display = "none";
    btn.onclick = async () => {
      btn.disabled = true;
      btn.textContent = "Running…";
      out.style.display = "block";
      out.classList.remove("err");
      out.textContent = "";
      try {
        const data = await fetchJSON("/api/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: sec.code }),
        });
        if (data.success) {
          out.textContent = data.stdout || "(no stdout)";
        } else {
          out.classList.add("err");
          out.textContent = (data.stderr || data.stdout || "Error").trim();
        }
      } catch (e) {
        out.classList.add("err");
        out.textContent = String(e);
      } finally {
        btn.disabled = false;
        btn.textContent = "Run";
      }
    };
    wrap.appendChild(btn);
    wrap.appendChild(out);
  } else if (sec.type === "quiz") {
    const q = document.createElement("div");
    q.className = "q";
    q.textContent = sec.question;
    wrap.appendChild(q);
    const form = document.createElement("div");
    const name = `quiz_${idx}`;
    (sec.options || []).forEach((opt, i) => {
      const lab = document.createElement("label");
      const inp = document.createElement("input");
      inp.type = "radio";
      inp.name = name;
      inp.value = String(i);
      lab.appendChild(inp);
      lab.appendChild(document.createTextNode(" " + opt));
      form.appendChild(lab);
    });
    wrap.appendChild(form);
    const fb = document.createElement("div");
    fb.className = "feedback";
    wrap.appendChild(fb);
    form.addEventListener("change", (e) => {
      const val = Number(e.target.value);
      if (val === sec.correct) {
        fb.textContent = "Correct";
        fb.className = "feedback ok";
        if (state.currentId) trackProgress(state.currentId);
      } else {
        fb.textContent = "Try again";
        fb.className = "feedback bad";
      }
    });
  }
  return wrap;
}

async function loadLesson(id) {
  state.currentId = id;
  renderSidebar();
  const data = await fetchJSON(`/api/lessons/${id}`);
  const content = document.getElementById("content");
  content.innerHTML = "";
  const h = document.createElement("h2");
  h.textContent = data.title;
  content.appendChild(h);
  (data.sections || []).forEach((sec, i) => content.appendChild(renderSection(sec, i)));

  const nav = document.createElement("div");
  nav.className = "nav-btns";
  const idx = state.lessons.findIndex((L) => L.id === id);
  if (idx > 0) {
    const prev = document.createElement("button");
    prev.textContent = "← Previous";
    prev.onclick = () => loadLesson(state.lessons[idx - 1].id);
    nav.appendChild(prev);
  }
  if (idx < state.lessons.length - 1) {
    const next = document.createElement("button");
    next.textContent = "Next →";
    next.onclick = () => loadLesson(state.lessons[idx + 1].id);
    nav.appendChild(next);
  }
  content.appendChild(nav);
}

async function init() {
  state.lessons = await fetchJSON("/api/lessons");
  renderSidebar();
  if (state.lessons.length) {
    await loadLesson(state.lessons[0].id);
  } else {
    document.getElementById("content").textContent = "No lessons found.";
  }
}

init().catch((e) => {
  document.getElementById("content").textContent = "Failed to load course: " + e;
});
