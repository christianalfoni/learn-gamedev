/* Shared behaviour for sketch guides:
   - a small GDScript highlighter (no dependencies, no CDN)
   - per-step progress, persisted in localStorage
   - copy buttons
   - logging a finished session back into the sketchbook's own store
*/
(() => {
  "use strict";

  /* ── GDScript highlighting ─────────────────────────────────
     Tokenise the raw source, then escape as we build the output.
     Escaping first would corrupt string literals ("→&quot;).      */

  const KEYWORDS = new Set([
    "func", "var", "const", "extends", "class_name", "class", "signal", "enum",
    "if", "elif", "else", "for", "while", "match", "when", "return", "break",
    "continue", "pass", "and", "or", "not", "in", "is", "as", "null", "true",
    "false", "self", "super", "await", "static", "void", "breakpoint", "assert",
    "preload", "load", "yield", "range"
  ]);

  // Lowercase built-in types, which the "starts with a capital" rule would miss.
  const BUILTIN_TYPES = new Set(["float", "int", "bool"]);

  const TOKEN = /(#[^\n]*)|("(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')|(@[A-Za-z_]\w*)|(\b\d[\d_]*(?:\.\d+)?\b)|([A-Za-z_]\w*)/g;

  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const span = (cls, s) => `<span class="${cls}">${esc(s)}</span>`;

  function highlightGD(src) {
    let out = "";
    let last = 0;
    let m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(src)) !== null) {
      out += esc(src.slice(last, m.index));
      last = m.index + m[0].length;

      if (m[1]) out += span("tok-com", m[1]);
      else if (m[2]) out += span("tok-str", m[2]);
      else if (m[3]) out += span("tok-ann", m[3]);
      else if (m[4]) out += span("tok-num", m[4]);
      else {
        const w = m[5];
        const after = src.slice(last);
        const callsNext = /^\s*\(/.test(after);
        const prev = src.slice(0, m.index).match(/(\w+)\s+$/);
        const isDef = prev && prev[1] === "func";

        if (KEYWORDS.has(w)) out += span("tok-kw", w);
        else if (BUILTIN_TYPES.has(w)) out += span("tok-type", w);
        else if (isDef || (callsNext && /^[a-z_]/.test(w))) out += span("tok-fn", w);
        else if (/^[A-Z]/.test(w)) out += span("tok-type", w);
        else out += esc(w);
      }
    }
    out += esc(src.slice(last));
    return out;
  }

  document.querySelectorAll("figure.code code").forEach(code => {
    const raw = code.textContent.replace(/^\n/, "").replace(/\s+$/, "");
    code.dataset.raw = raw;
    code.innerHTML = highlightGD(raw);
  });

  /* ── Copy buttons ──────────────────────────────────────────── */

  document.querySelectorAll("figure.code").forEach(fig => {
    const btn = fig.querySelector("button.copy");
    const code = fig.querySelector("code");
    if (!btn || !code) return;
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(code.dataset.raw || code.textContent);
        const was = btn.textContent;
        btn.textContent = "copied";
        setTimeout(() => { btn.textContent = was; }, 1400);
      } catch (e) {
        btn.textContent = "select it";
        setTimeout(() => { btn.textContent = "copy"; }, 1400);
      }
    });
  });

  /* ── Step progress ─────────────────────────────────────────── */

  const guideId = document.body.dataset.guide;          // e.g. "a1-good-movement"
  const sketchId = document.body.dataset.sketch;        // e.g. "A1"
  const KEY = "gamedev-guide-" + guideId + "-v1";
  const SKETCHBOOK_KEY = "gamedev-sketchbook-v1";

  const steps = Array.from(document.querySelectorAll(".step"));
  let done = new Set();

  try {
    const raw = localStorage.getItem(KEY);
    if (raw) done = new Set(JSON.parse(raw));
  } catch (e) { /* private mode, or corrupt — start clean */ }

  const bar = document.querySelector(".rail .bar i");
  const pct = document.querySelector(".rail .pct");

  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(Array.from(done))); } catch (e) { /* no-op */ }
  }

  function render() {
    steps.forEach(s => { s.dataset.done = done.has(s.id) ? "1" : "0"; });
    const n = steps.filter(s => done.has(s.id)).length;
    if (bar) bar.style.width = (steps.length ? (n / steps.length) * 100 : 0) + "%";
    if (pct) pct.textContent = n + "/" + steps.length + " steps";
    const finished = n === steps.length && steps.length > 0;
    document.querySelectorAll("[data-when-finished]").forEach(el => { el.hidden = !finished; });
  }

  steps.forEach(s => {
    const btn = s.querySelector(".step-check");
    if (!btn) return;
    btn.setAttribute("aria-label", "Mark this step done");
    btn.addEventListener("click", () => {
      if (done.has(s.id)) done.delete(s.id); else done.add(s.id);
      persist();
      render();
    });
  });

  render();

  /* ── Log the session back into the sketchbook ──────────────
     Same origin, so the tracker at / reads this on its next load. */

  const logBtn = document.getElementById("logSession");
  const logMsg = document.getElementById("logMsg");

  if (logBtn && sketchId) {
    logBtn.addEventListener("click", () => {
      try {
        const raw = localStorage.getItem(SKETCHBOOK_KEY);
        const state = raw ? JSON.parse(raw) : {};
        state.sketches = state.sketches || {};
        const r = state.sketches[sketchId] || { reps: 0, last: null, note: "" };
        r.reps = (r.reps || 0) + 1;
        r.last = new Date().toISOString();
        state.sketches[sketchId] = r;
        state.steps = state.steps || {};
        state.updated = new Date().toISOString();
        localStorage.setItem(SKETCHBOOK_KEY, JSON.stringify(state));
        logBtn.disabled = true;
        logBtn.textContent = "Logged";
        if (logMsg) logMsg.textContent = `${sketchId} is now at ×${r.reps} in the sketchbook.`;
      } catch (e) {
        if (logMsg) logMsg.textContent = "Couldn't write to this browser's storage — log it by hand on the sketchbook page.";
      }
    });
  }
})();
