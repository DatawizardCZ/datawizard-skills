"""HTML výkres a statické SVG: layout + proces → samostatný soubor (vzor web-motion / blueprint-pipeline)."""
from __future__ import annotations

import base64
import datetime
import hashlib
import html as _html
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .model import Process

ASSETS = Path(__file__).resolve().parents[2] / "assets"
STATUS_LABEL = {"draft": "Návrh", "k-validaci": "K validaci", "schvaleno": "Schváleno"}
KIND_LABEL = {"as-is": "as-is (dnes)", "to-be": "to-be (návrh)"}
MONO = '"SF Mono", Menlo, Consolas, "Liberation Mono", "DejaVu Sans Mono", monospace'
MIN_SCALE = 0.85  # výkres se nezmenší pod 85 %; širší proces se posouvá vodorovně

LIGHT = {
    "--bp-sheet": "#eef2f7", "--bp-paper": "#ffffff", "--bp-grid-f": "rgba(15,23,42,.035)",
    "--bp-grid-m": "rgba(15,23,42,.07)", "--bp-line": "#d6dee8", "--bp-line2": "#b6c3d3", "--bp-band": "#f5f8fb",
    "--bp-box": "#ffffff", "--bp-ink": "#0f172a", "--bp-mut": "#475569", "--bp-mut2": "#94a3b8",
    "--bp-cyan": "#1168bd", "--bp-cyan-dim": "#1168bd", "--bp-cyan-soft": "rgba(17,104,189,.08)",
    "--bp-wire": "#64748b", "--bp-amber": "#b45309",
}

SVG_CSS = """  #schema text { font-family: var(--mono); }
  .paper { fill: var(--bp-paper); }
  .grid-f { fill: none; stroke: var(--bp-grid-f); stroke-width: 1; }
  .grid-m { fill: none; stroke: var(--bp-grid-m); stroke-width: 1; }
  .lane-band { fill: transparent; }
  .lane-band.alt { fill: var(--bp-band); }
  .lane-sep { stroke: var(--bp-line); stroke-width: 1; fill: none; }
  .s-box { fill: var(--bp-box); stroke: var(--bp-line2); stroke-width: 1.2; }
  .s-box-hi { fill: var(--bp-cyan-soft); stroke: var(--bp-cyan); stroke-width: 1.6; }
  .s-box-soft { fill: transparent; stroke: var(--bp-line2); stroke-width: 1; }
  .s-chip { fill: var(--bp-cyan-soft); }
  .s-wire { fill: none; stroke: var(--bp-wire); stroke-width: 1.5; }
  .s-loop { fill: none; stroke: var(--bp-amber); stroke-width: 1.5; stroke-dasharray: 5 4; }
  .s-alt { fill: none; stroke: var(--bp-mut2); stroke-width: 1.5; stroke-dasharray: 5 4; }
  .s-dim { fill: none; stroke: var(--bp-line); stroke-width: 1; }
  .mk { fill: var(--bp-wire); }
  .mk-a { fill: var(--bp-amber); }
  .s-lbl { font-size: 10px; font-weight: 600; letter-spacing: .14em; fill: var(--bp-cyan); }
  .s-lane { font-size: 10.5px; font-weight: 700; letter-spacing: .16em; fill: var(--bp-cyan-dim); }
  .s-txt { font-size: 12.5px; font-weight: 700; fill: var(--bp-ink); }
  .s-sub { font-size: 10px; fill: var(--bp-mut); }
  .s-sub2 { font-size: 11px; fill: var(--bp-mut); }
  .s-q { font-size: 10.5px; font-weight: 700; fill: var(--bp-amber); }
  .s-warn { font-size: 10px; font-weight: 600; letter-spacing: .04em; fill: var(--bp-amber); }
  .s-note { font-size: 10px; font-weight: 600; fill: var(--bp-mut); }
  .s-chip-t { font-size: 11px; font-weight: 700; fill: var(--bp-ink); }
  .s-chip-s { font-size: 9.5px; fill: var(--bp-mut); }
  .s-st { font-size: 12px; font-weight: 700; fill: var(--bp-ink); }
  .ring { fill: none; stroke: var(--bp-cyan); stroke-width: 2; }
  .hitpad { fill: transparent; }"""


def esc(s) -> str:
    return _html.escape(str(s), quote=True)


def light_vars() -> str:
    return " ".join(f"{k}: {v};" for k, v in LIGHT.items())


def static_css() -> str:
    """CSS výkresu bez proměnných (samostatné SVG nezná proměnné na body)."""
    css = SVG_CSS.replace("var(--mono)", MONO)
    return re.sub(r"var\((--bp-[a-z0-9-]+)\)", lambda m: LIGHT[m.group(1)], css)


def _d(points) -> str:
    return "M" + " L".join(f"{x:g},{y:g}" for x, y in points)


def _tip_d(tip) -> str:
    a, b, c = tip
    return f"M{a[0]:g},{a[1]:g} L{b[0]:g},{b[1]:g} L{c[0]:g},{c[1]:g} z"


def _txt(x, y, cls: str, s: str, anchor: str = "") -> str:
    a = f' text-anchor="{anchor}"' if anchor and anchor != "start" else ""
    return f'<text class="{cls}" x="{x:g}" y="{y:g}"{a}>{esc(s)}</text>'


def _hit(key: str, label: str) -> str:
    return f'data-k="{esc(key)}" tabindex="0" role="button" aria-label="{esc(label)}"'


def build_svg(L: dict, proc: Process, static: bool = False) -> str:
    """SVG výkresu. static = True: světlé barvy přímo v SVG, finální stav, bez animačních tříd a masek."""
    W, H = L["width"], L["height"]
    draw = "" if static else " draw"

    def plen() -> str:
        return "" if static else ' pathLength="1"'

    def dl(t) -> str:
        return "" if static else f' style="--d:{t}s"'

    S: List[str] = [f'<svg xmlns="http://www.w3.org/2000/svg" id="schema" viewBox="0 0 {W} {H}" role="group" '
                    f'aria-label="{esc(proc.title)}">']
    if static:
        S.append(f"<style>\n{static_css()}\n</style>")
    S += ["<defs>",
          '<pattern id="g-fine" width="12" height="12" patternUnits="userSpaceOnUse"><path class="grid-f" d="M12,0 H0 V12"/></pattern>',
          '<pattern id="g-major" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="url(#g-fine)"/><path class="grid-m" d="M60,0 H0 V60"/></pattern>']
    if not static:
        for w in L["wires"]:
            if w["kind"] in ("loop", "alt"):
                S.append(f'<mask id="m-{w["id"]}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                         f'<path class="draw" pathLength="1" d="{_d(w["points"])}" fill="none" stroke="#fff" '
                         f'stroke-width="18" stroke-linecap="square" style="--d:{w["t"]}s"/></mask>')
    S.append("</defs>")
    S.append(f'<rect class="paper" width="{W}" height="{H}"/><rect width="{W}" height="{H}" fill="url(#g-major)"/>')

    for ln in L["lanes"]:
        alt = " alt" if ln["alt"] else ""
        sep = f'<path class="lane-sep" d="M0,{ln["y"]} H{W}"/>' if ln["y"] > 0 else ""
        S.append(f'<g class="node"{dl(ln["t"])}><rect class="lane-band{alt}" x="0" y="{ln["y"]}" '
                 f'width="{W}" height="{ln["h"]}"/>{sep}</g>')
        pad_w = int(len(ln["name"]) * 8.2) + 16
        S.append(f'<g class="node hit lane-lbl" {_hit("lane:" + ln["id"], "Role: " + ln["name"])}{dl(ln["label_t"])}>'
                 f'<rect class="hitpad" x="12" y="{ln["y"] + 4}" width="{pad_w}" height="20" rx="3"/>'
                 f'{_txt(20, ln["label_y"], "s-lane", ln["name"].upper())}</g>')
    S.append(f'<path class="lane-sep" d="M0,{L["lanes_bottom"]} H{W}"/>')

    for w in L["wires"]:
        if w["kind"] == "state":
            continue
        if w["kind"] in ("loop", "alt"):
            cls = "s-loop" if w["kind"] == "loop" else "s-alt"
            mask = "" if static else f' mask="url(#m-{w["id"]})"'
            S.append(f'<path class="{cls}" d="{_d(w["points"])}"{mask}/>')
        else:
            S.append(f'<path class="s-wire{draw}"{plen()} d="{_d(w["points"])}"{dl(w["t"])}/>')
        tip_cls = "mk-a" if w["kind"] == "loop" else "mk"
        S.append(f'<path class="{tip_cls} tip" d="{_tip_d(w["tip"])}"{dl(w["tip_t"])}/>')
        if w["label"]:
            lx, ly = w["label_pos"]
            label = ("↺ " + w["label"]) if w["kind"] == "loop" else w["label"]
            cls = "s-warn" if w["kind"] == "loop" else "s-note"
            S.append(f'<g class="node"{dl(w["label_t"])}>{_txt(lx, ly, cls, label, w["label_anchor"])}</g>')

    for sp in L["spans"]:
        S.append(f'<g class="node hit" {_hit(sp["key"], sp["title"] + ": " + sp["text"])}{dl(sp["t"])}>'
                 f'<rect class="s-box-soft{draw}"{plen()} x="{sp["x"]}" y="{sp["y"]}" width="{sp["w"]}" height="{sp["h"]}" rx="6"/>'
                 f'{_txt(sp["x"] + 14, sp["y"] + 24, "s-lbl", sp["title"].upper())}'
                 f'{_txt(sp["x"] + 14, sp["y"] + 44, "s-sub2", sp["text"])}</g>')

    for c in L["cards"]:
        box = "s-box-hi" if c["type"] == "decision" else "s-box"
        rx = 22 if c["type"] in ("start", "end") else 6
        g = [f'<g class="node hit" {_hit("step:" + c["id"], c["label"].capitalize() + ": " + " ".join(c["title_lines"]))}{dl(c["t"])}>',
             f'<rect class="{box}{draw}"{plen()} x="{c["x"]}" y="{c["y"]}" width="{c["w"]}" height="{c["h"]}" rx="{rx}"/>',
             _txt(c["x"] + 12, c["y"] + 20, "s-lbl", c["label"])]
        if c["question"]:
            g.append(_txt(c["x"] + c["w"] - 12, c["y"] + 20, "s-q", "??", "end"))
        ty = c["y"] + 41
        g += [_txt(c["x"] + 12, ty + i * 16, "s-txt", line) for i, line in enumerate(c["title_lines"])]
        if c["type"] == "checks":
            g += [_txt(c["x"] + 12, c["y"] + 57, "s-warn", line) for line in c["sub_lines"][:1]]
            for it in c["items"]:
                g.append(f'<g class="node"{dl(it["t"])}><rect class="s-chip" x="{it["x"]}" y="{it["y"]}" '
                         f'width="{it["w"]}" height="{it["h"]}" rx="4"/>'
                         f'{_txt(it["x"] + 10, it["y"] + 17, "s-chip-t", it["title"])}'
                         f'{_txt(it["x"] + 10, it["y"] + 31, "s-chip-s", it["sub"])}</g>')
        else:
            sy = ty + (len(c["title_lines"]) - 1) * 16 + 18
            g += [_txt(c["x"] + 12, sy + i * 14, "s-sub", line) for i, line in enumerate(c["sub_lines"])]
        g.append("</g>")
        S.append("".join(g))

    st = L["states"]
    if st:
        S.append(f'<path class="s-dim{draw}"{plen()} d="M0,{st["divider_y"]} H{W}"{dl(0.2)}/>')
        S.append(f'<g class="node"{dl(0.3)}>{_txt(20, st["label_y"], "s-lane", st["label"].upper())}</g>')
        for p in st["pills"]:
            style = "" if static else f' style="--d:{p["t"]}s;--l:{p["lit_t"]}s"'
            S.append(f'<g class="st hit" {_hit("state:" + p["id"], "Stav: " + p["name"])}{style}>'
                     f'<rect class="s-box{draw}"{plen()} x="{p["x"]}" y="{p["y"]}" width="{p["w"]}" height="{p["h"]}" rx="6"/>'
                     f'{_txt(p["x"] + 14, p["y"] + 21, "s-st", p["name"])}{_txt(p["x"] + 14, p["y"] + 38, "s-sub", p["sub"])}</g>')
        for w in L["wires"]:
            if w["kind"] == "state":
                S.append(f'<path class="s-wire{draw}"{plen()} d="{_d(w["points"])}"{dl(w["t"])}/>'
                         f'<path class="mk tip" d="{_tip_d(w["tip"])}"{dl(w["tip_t"])}/>')
        r = st["ring"]
        end = f' transform="translate({r["steps"][-1]["dx"]},0)"' if static else ""
        S.append(f'<rect class="ring" x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}" rx="9"{end}/>')
    S.append("</svg>")
    return "\n".join(S)


def ring_css(L: dict) -> Tuple[str, float, float, float]:
    """Keyframes posunu rámečku po stavech; vrací (keyframes, start, délka, konečný posun)."""
    st = L["states"]
    if not st:
        return "0% { transform: translateX(0px); } 100% { transform: translateX(0px); }", 0.0, 1.0, 0.0
    steps, total = st["ring"]["steps"], st["ring"]["total"]
    out = ["0% { transform: translateX(0px); animation-timing-function: ease-in-out; }"]
    for prev, cur in zip(steps, steps[1:]):
        a = max(cur["t"] - 0.3, prev["t"], 0) / total * 100
        b = cur["t"] / total * 100
        out.append(f"{a:.2f}% {{ transform: translateX({prev['dx']}px); animation-timing-function: ease-in-out; }}")
        out.append(f"{b:.2f}% {{ transform: translateX({cur['dx']}px); animation-timing-function: ease-in-out; }}")
    out.append(f"100% {{ transform: translateX({steps[-1]['dx']}px); }}")
    return "\n    ".join(out), steps[0]["t"], total, steps[-1]["dx"]


def _ref_key(proc: Process, ref: str) -> str:
    if any(s.id == ref for s in proc.steps):
        return "step:" + ref
    if any(l.id == ref for l in proc.lanes):
        return "lane:" + ref
    return "state:" + ref


def _ref_label(proc: Process, L: dict, ref: str) -> str:
    for c in L["cards"]:
        if c["id"] == ref:
            return c["label"].capitalize()
    for l in proc.lanes:
        if l.id == ref:
            return "Role · " + l.name
    for st in proc.states:
        if st.id == ref:
            return "Stav · " + st.name
    return ref


def _qtexts(proc: Process, ref: str) -> Tuple[List[str], List[str]]:
    open_q = [q.text + (f" (odpoví: {q.who})" if q.who else "") for q in proc.open_questions(ref)]
    done_q = [f"{q.text} → {q.answer}" for q in proc.resolved_questions(ref)]
    return open_q, done_q


def details(proc: Process, L: dict) -> Dict[str, dict]:
    lane = {l.id: l for l in proc.lanes}
    label = {c["id"]: c["label"] for c in L["cards"]}
    D: Dict[str, dict] = {}
    for s in proc.steps:
        q, done = _qtexts(proc, s.id)
        D["step:" + s.id] = {
            "label": f"{label[s.id].capitalize()} · {s.title}", "tags": [lane[s.lane].name],
            "desc": s.detail or s.sub,
            "rows": [["Výstup", s.out], ["Dnes", s.today], ["Systémy", ", ".join(s.tools)], ["Čas", s.time],
                     ["Id", s.id]],
            "items": [f"{i.title}: {i.sub}" if i.sub else i.title for i in s.items],
            "pain": s.pain, "q": q, "done": done, "src": proc.source}
    for l in proc.lanes:
        q, done = _qtexts(proc, l.id)
        D["lane:" + l.id] = {"label": "Role · " + l.name, "tags": [l.access] if l.access else [], "desc": l.desc,
                             "q": q, "done": done}
    for sp in L["spans"]:
        D[sp["key"]] = {"label": sp["title"], "tags": [lane[sp["lane"]].name], "desc": sp["text"]}
    for st in proc.states:
        q, done = _qtexts(proc, st.id)
        D["state:" + st.id] = {"label": "Stav · " + st.name, "desc": st.detail or st.sub, "q": q, "done": done}
    return D


def overview_html(proc: Process, L: dict) -> str:
    meta = f"{KIND_LABEL.get(proc.kind, proc.kind)} · v{proc.version}" + (f" · {proc.updated}" if proc.updated else "")
    parts = [f"<h2>{esc(proc.title)}</h2>", f"<p>{esc(meta)}</p>",
             "<p>Klikni na krok, roli nebo stav a vpravo se ukáže detail. Na schůzce pomůže tlačítko Krokovat.</p>"]
    frame = [("Vlastník", proc.owner), ("Spouštěč", proc.trigger), ("Výsledek", proc.outcome),
             ("Účel mapy", proc.purpose), ("Objem", proc.volume), ("Schváleno", proc.approved)]
    frame = [(a, b) for a, b in frame if b]
    if frame:
        rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in frame)
        parts += ["<h3>Rámec</h3>", f'<table class="frame-table">{rows}</table>']
    if proc.today:
        parts += ["<h3>Dnes</h3>", "<ul>" + "".join(f"<li>{esc(t)}</li>" for t in proc.today) + "</ul>"]
    pains = [(s, p) for s in proc.steps for p in s.pain]
    if pains:
        items = "".join(f'<li><button type="button" class="q-link pain" data-open="step:{esc(s.id)}">'
                        f'<span class="q-step">{esc(_ref_label(proc, L, s.id))}</span>{esc(p)}</button></li>'
                        for s, p in pains)
        parts += [f"<h3>Bolesti ({len(pains)})</h3>", f'<ul class="q-list">{items}</ul>']
    oq = proc.open_questions()
    parts.append(f"<h3>Otevřené otázky ({len(oq)})</h3>")
    if oq:
        items = "".join(
            f'<li><button type="button" class="q-link" data-open="{esc(_ref_key(proc, q.ref))}">'
            f'<span class="q-step">{esc(_ref_label(proc, L, q.ref))}</span>{esc(q.text)}</button></li>' for q in oq)
        parts.append(f'<ul class="q-list">{items}</ul>')
    else:
        parts.append("<p>Žádné otevřené otázky.</p>")
    return "\n".join(parts)


def step_list(L: dict) -> List[dict]:
    """Krokování: k-tý krok ukáže všechno, co animace stihne před šipkou do dalšího kroku."""
    cards = L["cards"]
    lead = 0.5 * L["pace"] + 0.05
    out = []
    for i, c in enumerate(cards):
        until = cards[i + 1]["t"] - lead if i + 1 < len(cards) else 1e9
        out.append({"id": c["id"], "until": round(until, 3)})
    return out


def _sr_text(proc: Process) -> str:
    lane = {l.id: l.name for l in proc.lanes}
    s = " ".join(f"{lane[st.lane]}: {st.title}." for st in proc.steps)
    if proc.states:
        s += f" {proc.states_label}: " + ", ".join(x.name for x in proc.states) + "."
    return s


def _json(obj) -> str:
    """JSON bezpečný uvnitř <script>: žádné <, >, & ani U+2028/2029."""
    s = json.dumps(obj, ensure_ascii=False)
    return (s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
             .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def _hash(script: str) -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode() + "'"


JS_SLOTS = re.compile(r"/\*(DETAILS|STEPS|RING)\*/null|/\*(DURATION)\*/0")


def _fill(tmpl: str, values: Dict[str, str]) -> str:
    """Jeden průchod: vložené hodnoty se už jako tokeny nevyhodnocují. Neznámý token = KeyError."""
    return re.sub(r"__([A-Z][A-Z_]*)__", lambda m: values[m.group(1)], tmpl)


def render_html(proc: Process, L: dict, links: Optional[List[Tuple[str, str]]] = None,
                generated: Optional[str] = None) -> str:
    generated = generated or datetime.date.today().isoformat()
    keyframes, ring_in, ring_total, ring_end = ring_css(L)
    status = STATUS_LABEL.get(proc.status, proc.status)
    dates = (f" · upraveno {esc(proc.updated)}" if proc.updated else "") + f" · vygenerováno {esc(generated)}"
    meta = (f'<span class="status-badge status-{esc(proc.status)}">{esc(status)}</span> '
            f'{esc(KIND_LABEL.get(proc.kind, proc.kind))} · v{esc(proc.version)}{dates}'
            + (f" · {esc(proc.source)}" if proc.source else ""))
    fs = (ASSETS / "fullscreen.js").read_text(encoding="utf-8")
    fullscreen_script = ("(function () {\n" + fs + "\nwindow.initFullscreen = initFullscreen;"
                         "\nwindow.closeFullscreen = closeFullscreen;\n})();")
    ring = L["states"]["ring"]["steps"] if L["states"] else None
    slots = {"DETAILS": _json(details(proc, L)), "STEPS": _json(step_list(L)), "RING": _json(ring),
             "DURATION": f"{L['duration']:g}"}
    # jeden průchod šablonou: značky v textu, který se právě vložil, se už nenahrazují
    main_script = JS_SLOTS.sub(lambda m: slots[m.group(1) or m.group(2)],
                               (ASSETS / "process-map.js").read_text(encoding="utf-8"))
    values = {
        "TITLE": esc(proc.title),
        "META": meta,
        "LINKS": "".join(f'<a href="{esc(url)}">{esc(text)}</a>' for text, url in (links or [])),
        "HEAD_LEFT": "Procesní mapa · " + esc(proc.title),
        "HEAD_RIGHT": f"{esc(proc.kind)} · v{esc(proc.version)}" + (f" · {esc(proc.updated)}" if proc.updated else ""),
        "FOOT_LEFT": ("zdroj: " + esc(proc.source)) if proc.source else "",
        "FOOT_RIGHT": "● " + esc(status.lower()) + f" · vygenerováno {esc(generated)}",
        "SR_TEXT": esc(_sr_text(proc)),
        "SVG": build_svg(L, proc),
        "SVG_CSS": SVG_CSS,
        "LIGHT_VARS": light_vars(),
        "MIN_WIDTH": f"{round(L['width'] * MIN_SCALE)}",
        "OVERVIEW": overview_html(proc, L),
        "FULLSCREEN_SCRIPT": fullscreen_script,
        "MAIN_SCRIPT": main_script,
        "SCRIPT_HASHES": _hash(fullscreen_script) + " " + _hash(main_script),
        "RING_KEYFRAMES": keyframes,
        "RING_IN": f"{ring_in:g}",
        "RING_TOTAL": f"{ring_total:g}",
        "RING_END": f"{ring_end:g}",
    }
    return _fill((ASSETS / "process-map.html.tmpl").read_text(encoding="utf-8"), values)


def render_svg(proc: Process, L: dict) -> str:
    """Statické světlé SVG ve finálním stavu (obrázek do prezentace nebo dokumentu)."""
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + build_svg(L, proc, static=True) + "\n"
