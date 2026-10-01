(function () {
  "use strict";
  var nodeData = /*DETAILS*/null;
  var steps = /*STEPS*/null;   // [{id, until}] pro krokování; until = do kdy patří prvky k danému kroku
  var ringSteps = /*RING*/null; // [{t, dx}] nebo null
  var duration = /*DURATION*/0;

  var svg = document.getElementById("schema");
  var sheetBody = document.getElementById("sheet-body");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var doneTimer = null;

  // ---------- animace: start přes IntersectionObserver, replay, přeskočit
  function setMode(mode) {
    svg.classList.remove("armed", "play", "stepping");
    if (mode === "armed") svg.classList.add("armed");
    if (mode === "play") svg.classList.add("armed", "play");
    if (mode === "stepping") svg.classList.add("stepping");
  }
  function play() {
    stopStepping();
    setMode("armed");
    void svg.getBoundingClientRect();
    setMode("play");
    clearTimeout(doneTimer);
    // po doběhnutí přepnout na statický finální stav, aby přesun SVG (fullscreen) animaci nerestartoval
    doneTimer = setTimeout(skip, (duration + 0.5) * 1000);
  }
  function skip() { clearTimeout(doneTimer); stopStepping(); setMode("done"); }

  if (!reduce) {
    setMode("armed");
    var started = false;
    var start = function () { if (!started) { started = true; setTimeout(play, 400); } };
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { io.disconnect(); start(); } });
    }, { threshold: 0 });
    io.observe(svg);
    setTimeout(function () { io.disconnect(); start(); }, 2500); // pojistka pro velmi vysoké výkresy
  }
  document.getElementById("b-replay").addEventListener("click", function () { if (reduce) skip(); else play(); });
  document.getElementById("b-skip").addEventListener("click", skip);

  // ---------- světlý / blueprint výkres (pamatuje se v prohlížeči)
  var tLight = document.getElementById("t-light");
  try { tLight.checked = localStorage.getItem("pmap-light") === "1"; } catch (_) { /* ignore */ }
  function applyTheme() {
    document.body.classList.toggle("light", tLight.checked);
    try { localStorage.setItem("pmap-light", tLight.checked ? "1" : "0"); } catch (_) { /* ignore */ }
  }
  tLight.addEventListener("change", applyTheme);
  applyTheme();

  // ---------- popisky rolí zůstávají vidět při vodorovném posunu
  var laneLabels = Array.prototype.slice.call(svg.querySelectorAll(".lane-lbl"));
  var vbWidth = svg.viewBox.baseVal.width || 1;
  sheetBody.addEventListener("scroll", function () {
    var scale = svg.clientWidth / vbWidth || 1;
    var dx = sheetBody.scrollLeft / scale;
    laneLabels.forEach(function (g) { g.style.transform = dx ? "translateX(" + dx + "px)" : ""; });
  });

  // ---------- detail
  var detail = document.getElementById("detail");
  var overview = document.getElementById("overview");
  function el(tag, opts, children) {
    var n = document.createElement(tag);
    opts = opts || {};
    if (opts.cls) n.className = opts.cls;
    if (opts.text != null) n.textContent = opts.text;
    (children || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  function select(k) {
    Array.prototype.forEach.call(svg.querySelectorAll(".hit.sel"), function (n) { n.classList.remove("sel"); });
    if (!k) return;
    var g = Array.prototype.find.call(svg.querySelectorAll("[data-k]"), function (n) { return n.dataset.k === k; });
    if (g) g.classList.add("sel");
  }
  function showOverview() { select(null); detail.replaceChildren(overview); }
  function list(title, items, cls) {
    if (!items || !items.length) return [];
    var out = [el("h3", { text: title })];
    items.forEach(function (t) { out.push(el("div", { cls: cls, text: t })); });
    return out;
  }
  function openDetail(k, keepFullscreen) {
    var d = nodeData[k];
    if (!d) return;
    if (!keepFullscreen && window.closeFullscreen) window.closeFullscreen();
    select(k);
    var back = el("button", { cls: "detail-back", text: "← Přehled a otázky" });
    back.type = "button";
    back.addEventListener("click", showOverview);
    var parts = [back, el("h2", { text: d.label })];
    (d.tags || []).forEach(function (t) { parts.push(el("span", { cls: "detail-role", text: t })); });
    if (d.desc) parts.push(el("div", { cls: "detail-description", text: d.desc }));
    var rows = (d.rows || []).filter(function (r) { return r[1]; });
    if (rows.length) {
      var table = el("table", { cls: "detail-table" });
      rows.forEach(function (r) { table.appendChild(el("tr", {}, [el("td", { text: r[0] }), el("td", { text: r[1] })])); });
      parts.push(table);
    }
    if (d.items && d.items.length) {
      parts.push(el("h3", { text: "Obsah" }));
      var ul = el("ul");
      d.items.forEach(function (t) { ul.appendChild(el("li", { text: t })); });
      parts.push(ul);
    }
    parts = parts.concat(list("Bolesti", d.pain, "detail-pain"));
    parts = parts.concat(list("Otevřené otázky", d.q, "detail-q"));
    parts = parts.concat(list("Vyřešené otázky", d.done, "detail-q done"));
    if (d.src) parts.push(el("div", { cls: "detail-src", text: "Zdroj: " + d.src }));
    detail.replaceChildren.apply(detail, parts);
  }
  svg.addEventListener("click", function (e) { var g = e.target.closest("[data-k]"); if (g) openDetail(g.dataset.k); });
  svg.addEventListener("keydown", function (e) {
    if (svg.classList.contains("stepping")) return;
    if (e.key !== "Enter" && e.key !== " ") return;
    var g = e.target.closest && e.target.closest("[data-k]");
    if (g) { e.preventDefault(); openDetail(g.dataset.k); }
  });
  overview.addEventListener("click", function (e) { var b = e.target.closest("[data-open]"); if (b) openDetail(b.dataset.open); });

  // ---------- krokování
  var bStep = document.getElementById("b-step");
  var hint = document.getElementById("step-hint");
  var ring = svg.querySelector(".ring");
  var timed = Array.prototype.map.call(svg.querySelectorAll("[style*='--d']"), function (n) {
    return { n: n, d: parseFloat(n.style.getPropertyValue("--d")) || 0, l: parseFloat(n.style.getPropertyValue("--l")) };
  });
  var si = -1;
  function showStep(i) {
    si = Math.max(0, Math.min(steps.length - 1, i));
    var until = steps[si].until;
    timed.forEach(function (o) {
      o.n.classList.toggle("on", o.d <= until);
      if (!isNaN(o.l)) o.n.classList.toggle("lit", o.l <= until);
    });
    if (ring && ringSteps) {
      var cur = null;
      ringSteps.forEach(function (r) { if (r.t <= until) cur = r; });
      ring.classList.toggle("on", !!cur);
      ring.style.transform = "translateX(" + (cur ? cur.dx : 0) + "px)";
    }
    openDetail("step:" + steps[si].id, true);
  }
  function startStepping() {
    clearTimeout(doneTimer);
    setMode("stepping");
    bStep.setAttribute("aria-pressed", "true");
    hint.hidden = false;
    showStep(0);
  }
  function stopStepping() {
    if (!svg.classList.contains("stepping")) return;
    svg.classList.remove("stepping");
    bStep.setAttribute("aria-pressed", "false");
    hint.hidden = true;
    timed.forEach(function (o) { o.n.classList.remove("on", "lit"); });
    if (ring) { ring.classList.remove("on"); ring.style.transform = ""; }
    si = -1;
  }
  bStep.addEventListener("click", function () {
    if (svg.classList.contains("stepping")) { stopStepping(); setMode("done"); } else startStepping();
  });
  document.addEventListener("keydown", function (e) {
    if (!svg.classList.contains("stepping")) return;
    if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
    if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") { e.preventDefault(); showStep(si + 1); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); showStep(si - 1); }
    else if (e.key === "Escape") { e.preventDefault(); stopStepping(); setMode("done"); }
  });

  if (window.initFullscreen) window.initFullscreen();
})();
