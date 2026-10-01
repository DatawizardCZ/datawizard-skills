/* Fullscreen prohlížeč SVG výkresu (process-mapping).
 *
 * initFullscreen(): ke každému hostiteli .fs-host přidá tlačítko „Celá obrazovka“.
 * Overlay: kolečko = zoom, tažení = posun, dvojklik = přiblížit, Esc = zavřít, +/- = zoom,
 * 0 = přizpůsobit, 1 = 100 %. SVG se do overlaye přesouvá (ne kopíruje), klik-handlery zůstávají.
 * closeFullscreen(): zavře otevřený overlay (volá se třeba před otevřením detailu v panelu).
 * Ukazatel se zachytí až po tahu delším než 3 px, aby obyčejný klik došel na uzel výkresu.
 */
function initFullscreen(root) {
  root = root || document;
  injectStyles();
  root.querySelectorAll(".fs-host").forEach(function (host) {
    var svg = host.querySelector(":scope > svg");
    if (!svg || host.querySelector(":scope > .fs-btn")) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "fs-btn";
    btn.title = "Otevřít výkres přes celou obrazovku";
    btn.innerHTML = ICON + "<span>Celá obrazovka</span>";
    btn.addEventListener("click", function (e) { e.stopPropagation(); openOverlay(svg, document.title); });
    host.appendChild(btn);
  });
}

var closeCurrent = null;
function closeFullscreen() { if (closeCurrent) closeCurrent(); }

var ICON = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M2 6V2h4M14 6V2h-4M2 10v4h4M14 10v4h-4"/></svg>';

var FS_CSS = [
  ".fs-host { position: relative; }",
  ".fs-btn { position: absolute; top: .5rem; right: .5rem; z-index: 5; display: inline-flex; align-items: center; gap: .35rem;",
  "  padding: .3rem .65rem; border: 1px solid var(--border, #e2e8f0); background: white; color: var(--text, #0f172a);",
  "  border-radius: 6px; cursor: pointer; font: 500 .78rem/1.2 inherit; opacity: .75; }",
  ".fs-btn:hover { opacity: 1; border-color: var(--accent, #1168bd); }",
  ".fs-btn svg { width: 14px; height: 14px; }",
  ".fs-overlay { position: fixed; inset: 0; z-index: 9999; background: var(--bg, #f8fafc); color: var(--text, #0f172a);",
  "  display: flex; flex-direction: column; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }",
  ".fs-toolbar { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; padding: .6rem 1rem; background: white;",
  "  border-bottom: 1px solid var(--border, #e2e8f0); }",
  ".fs-toolbar .fs-title { flex: 1; min-width: 0; font-size: .9rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }",
  ".fs-toolbar button { padding: .35rem .7rem; min-width: 2.2rem; border: 1px solid var(--border, #e2e8f0); background: white;",
  "  color: inherit; border-radius: 6px; cursor: pointer; font: 500 .82rem/1.2 inherit; }",
  ".fs-toolbar button:hover { border-color: var(--accent, #1168bd); }",
  ".fs-toolbar .fs-zoom { min-width: 3.6rem; text-align: center; font-size: .8rem; color: var(--text-muted, #64748b); }",
  ".fs-toolbar .fs-close { background: var(--accent, #1168bd); color: white; border-color: var(--accent, #1168bd); }",
  ".fs-toolbar .fs-hint { font-size: .75rem; color: var(--text-muted, #64748b); margin-left: .5rem; }",
  ".fs-viewport { flex: 1; position: relative; overflow: hidden; cursor: grab; touch-action: none; }",
  ".fs-viewport.dragging { cursor: grabbing; }",
  ".fs-canvas { position: absolute; left: 0; top: 0; transform-origin: 0 0; }",
  ".fs-canvas svg { display: block; }",
  "@media (max-width: 700px) { .fs-toolbar .fs-hint { display: none; } }",
  "@media print { .fs-btn { display: none; } }"
].join("\n");

function injectStyles() {
  if (document.getElementById("fs-styles")) return;
  var s = document.createElement("style");
  s.id = "fs-styles";
  s.textContent = FS_CSS;
  document.head.appendChild(s);
}

function naturalSize(svg) {
  var vb = svg.viewBox && svg.viewBox.baseVal;
  if (vb && vb.width && vb.height) return { w: vb.width, h: vb.height };
  var r = svg.getBoundingClientRect();
  return { w: r.width || 800, h: r.height || 600 };
}

function openOverlay(svg, title) {
  if (closeCurrent) closeCurrent();
  var placeholder = document.createComment("fs-placeholder");
  svg.parentNode.insertBefore(placeholder, svg);
  var saved = { width: svg.getAttribute("width"), height: svg.getAttribute("height"), style: svg.getAttribute("style") };
  var size = naturalSize(svg), W = size.w, H = size.h;

  var overlay = document.createElement("div");
  overlay.className = "fs-overlay";
  overlay.innerHTML =
    '<div class="fs-toolbar"><div class="fs-title"></div>' +
    '<button type="button" data-act="out" title="Oddálit (−)">−</button><span class="fs-zoom">100 %</span>' +
    '<button type="button" data-act="in" title="Přiblížit (+)">+</button>' +
    '<button type="button" data-act="fit" title="Přizpůsobit obrazovce (0)">Přizpůsobit</button>' +
    '<button type="button" data-act="one" title="Skutečná velikost (1)">1:1</button>' +
    '<span class="fs-hint">kolečko = zoom · tažení = posun · Esc = zavřít</span>' +
    '<button type="button" class="fs-close" data-act="close" title="Zavřít (Esc)">✕ Zavřít</button></div>' +
    '<div class="fs-viewport"><div class="fs-canvas"></div></div>';
  overlay.querySelector(".fs-title").textContent = title || document.title;
  var viewport = overlay.querySelector(".fs-viewport");
  var canvas = overlay.querySelector(".fs-canvas");
  var zoomLabel = overlay.querySelector(".fs-zoom");

  svg.setAttribute("width", W);
  svg.setAttribute("height", H);
  svg.style.maxWidth = "none";
  svg.style.minWidth = "0";
  canvas.appendChild(svg);
  document.body.appendChild(overlay);
  var prevOverflow = document.body.style.overflow;
  document.body.style.overflow = "hidden";

  var s = 1, tx = 0, ty = 0;
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
  function apply() { canvas.style.transform = "translate(" + tx + "px, " + ty + "px) scale(" + s + ")"; zoomLabel.textContent = Math.round(s * 100) + " %"; }
  function zoomAt(f, cx, cy) { var ns = clamp(s * f, 0.05, 10); tx = cx - (cx - tx) * (ns / s); ty = cy - (cy - ty) * (ns / s); s = ns; apply(); }
  function center() { var r = viewport.getBoundingClientRect(); return { x: r.width / 2, y: r.height / 2 }; }
  function fit() {
    var r = viewport.getBoundingClientRect(), pad = 32;
    s = Math.min((r.width - pad) / W, (r.height - pad) / H);
    if (!isFinite(s) || s <= 0) s = 1;
    tx = (r.width - W * s) / 2; ty = (r.height - H * s) / 2; apply();
  }
  function one() { var r = viewport.getBoundingClientRect(); s = 1; tx = Math.max((r.width - W) / 2, 16); ty = Math.max((r.height - H) / 2, 16); apply(); }

  var closed = false;
  function close() {
    if (closed) return;
    closed = true;
    closeCurrent = null;
    ["width", "height", "style"].forEach(function (k) { if (saved[k] == null) svg.removeAttribute(k); else svg.setAttribute(k, saved[k]); });
    placeholder.parentNode.insertBefore(svg, placeholder);
    placeholder.remove();
    overlay.remove();
    document.body.style.overflow = prevOverflow;
    document.removeEventListener("keydown", onKey);
    document.removeEventListener("fullscreenchange", onFsChange);
    window.removeEventListener("resize", fit);
    if (document.fullscreenElement) document.exitFullscreen().catch(function () {});
  }
  closeCurrent = close;

  overlay.querySelector(".fs-toolbar").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-act]");
    if (!b) return;
    var c = center();
    if (b.dataset.act === "in") zoomAt(1.25, c.x, c.y);
    else if (b.dataset.act === "out") zoomAt(1 / 1.25, c.x, c.y);
    else if (b.dataset.act === "fit") fit();
    else if (b.dataset.act === "one") one();
    else if (b.dataset.act === "close") close();
  });
  viewport.addEventListener("wheel", function (e) {
    e.preventDefault();
    var r = viewport.getBoundingClientRect();
    zoomAt(Math.exp(-e.deltaY * (e.deltaMode === 1 ? 0.05 : 0.0015)), e.clientX - r.left, e.clientY - r.top);
  }, { passive: false });

  var drag = null;
  viewport.addEventListener("pointerdown", function (e) {
    if (e.button !== 0) return;
    drag = { x: e.clientX, y: e.clientY, tx: tx, ty: ty, moved: false, id: e.pointerId };
  });
  viewport.addEventListener("pointermove", function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!drag.moved) {
      if (Math.abs(dx) + Math.abs(dy) <= 3) return;
      drag.moved = true;
      try { viewport.setPointerCapture(drag.id); } catch (_) { /* ignore */ }
      viewport.classList.add("dragging");
    }
    tx = drag.tx + dx; ty = drag.ty + dy; apply();
  });
  function endDrag() {
    if (!drag) return;
    try { viewport.releasePointerCapture(drag.id); } catch (_) { /* ignore */ }
    drag = null;
    viewport.classList.remove("dragging");
  }
  viewport.addEventListener("pointerup", endDrag);
  viewport.addEventListener("pointercancel", endDrag);
  viewport.addEventListener("dblclick", function (e) { var r = viewport.getBoundingClientRect(); zoomAt(1.6, e.clientX - r.left, e.clientY - r.top); });

  function onKey(e) {
    if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
    var c = center();
    if (e.key === "Escape") { e.preventDefault(); close(); }
    else if (e.key === "+" || e.key === "=") { e.preventDefault(); zoomAt(1.25, c.x, c.y); }
    else if (e.key === "-" || e.key === "_") { e.preventDefault(); zoomAt(1 / 1.25, c.x, c.y); }
    else if (e.key === "0") { e.preventDefault(); fit(); }
    else if (e.key === "1") { e.preventDefault(); one(); }
  }
  document.addEventListener("keydown", onKey);
  var nativeRequested = false;
  function onFsChange() { if (nativeRequested && !document.fullscreenElement) close(); }
  document.addEventListener("fullscreenchange", onFsChange);
  if (document.documentElement.requestFullscreen) {
    document.documentElement.requestFullscreen().then(function () { nativeRequested = true; }).catch(function () {});
  }
  window.addEventListener("resize", fit);
  fit();
}
