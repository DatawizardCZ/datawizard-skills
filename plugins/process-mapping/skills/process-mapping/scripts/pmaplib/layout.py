"""Automatické rozložení swimlane mapy: sloupce, karty, trasy šipek, stavy a časování.

Výstup je obyčejný dict (JSON, "schema": 1), ze kterého kreslí HTML, SVG i Figma. Souřadnice
jsou v jednotkách SVG viewBoxu; Figma je násobí měřítkem. Předpokládá proces, který prošel check().
"""
from __future__ import annotations

from math import hypot
from typing import Dict, List, Optional, Sequence, Tuple

from . import text
from .model import Flow, Process, Step

Point = Tuple[float, float]
Rect = Tuple[float, float, float, float]

SCHEMA = 1
COL_W = 166
CARD_W = 152
CARD_H = 100
MARGIN = 20
LANE_TOP = 52
LANE_BOTTOM = 28
LANE_LABEL_Y = 18
EMPTY_LANE_H = 90
SPAN_H = 60
SPAN_TOP = 30
CHECKS_HEAD = 69
ITEM_ROW = 46
ITEM_W = 144
ITEM_H = 40
ITEM_STEP_X = 150
ANCHOR_Y = 50
TIP_GAP = 7
LOOP_CHANNEL = 34
LOOP_INSET = 40
STATE_GAP = 30
STATE_H = 50
STATE_MIN_W = 150

FIRST_STEP_T = 0.5
STEP_T = 0.8
WIRE_LEAD = 0.5
TIP_DELAY = 0.55
ITEM_T = 0.15
CHECKS_EXTRA = 0.4
LOOP_EXTRA = 0.9
SPAN_DELAY = 0.3
LABEL_DELAY = 0.5
SAME_STATE_DELAY = 0.8
MIN_STATE_GAP = 0.5
FLOW_BUDGET = 11.0  # nad touto délkou se rytmus kroků úměrně zrychlí


def _r(v: float) -> float:
    return round(v, 3)


def col_span(step: Step) -> int:
    return 2 if step.type == "checks" else 1


def card_size(step: Step) -> Tuple[int, int]:
    w = CARD_W + (col_span(step) - 1) * COL_W
    if step.type == "checks" and step.items:
        rows = (len(step.items) + 1) // 2
        return w, CHECKS_HEAD + rows * ITEM_ROW + 3
    return w, CARD_H


def x_of(col: int) -> int:
    return MARGIN + col * COL_W


def assign_columns(proc: Process) -> Dict[str, int]:
    """Sloupce kroků v pořadí zápisu.

    Krok v jiném pruhu dostane sloupec předchozího kroku, když je místo volné a předchozí
    krok sám nepřišel z jiného pruhu (bez cik-caku). Jinak další volný sloupec. `col` přepíše.
    """
    occupied = set()
    cols: Dict[str, int] = {}
    came_cross: Dict[str, bool] = {}
    prev: Optional[Step] = None
    for s in proc.steps:
        w = col_span(s)
        if s.col is not None:
            c = s.col
        elif prev is None:
            c = 0
        else:
            pc = cols[prev.id]
            free = all((s.lane, pc + k) not in occupied for k in range(w))
            if s.lane != prev.lane and free and not came_cross[prev.id]:
                c = pc
            else:
                c = pc + col_span(prev)
                while any((s.lane, c + k) in occupied for k in range(w)):
                    c += 1
        cols[s.id] = c
        came_cross[s.id] = prev is not None and prev.lane != s.lane
        for k in range(w):
            occupied.add((s.lane, c + k))
        prev = s
    return cols


def lane_geometry(proc: Process) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    y = 0
    for i, lane in enumerate(proc.lanes):
        hs = [card_size(s)[1] for s in proc.steps if s.lane == lane.id]
        has_span = any(sp.lane == lane.id for sp in proc.spans)
        if hs:
            body = LANE_TOP + max(hs)
            span_y = y + body + 12 if has_span else None
            h = body + (12 + SPAN_H if has_span else 0) + LANE_BOTTOM
        elif has_span:
            span_y = y + SPAN_TOP
            h = SPAN_TOP + SPAN_H + 16
        else:
            span_y = None
            h = EMPTY_LANE_H
        out[lane.id] = {"id": lane.id, "name": lane.name, "index": i, "y": y, "h": h,
                        "label_y": y + LANE_LABEL_Y, "span_y": span_y, "alt": i % 2 == 1,
                        "t": _r(i * 0.1), "label_t": _r(0.1 + i * 0.1)}
        y += h
    return out


def pace(proc: Process) -> float:
    """Násobek rytmu animace: 1 pro běžné procesy, méně pro dlouhé (celkem zhruba do 11 s)."""
    return min(1.0, FLOW_BUDGET / (STEP_T * max(1, len(proc.steps))))


def step_times(proc: Process, flows: Sequence[Flow], f: float) -> Dict[str, float]:
    loop_src = {fl.src for fl in flows if fl.kind == "loop"}
    times: Dict[str, float] = {}
    t = FIRST_STEP_T
    for s in proc.steps:
        times[s.id] = _r(t)
        extra = 0.0
        if s.type == "checks":
            extra += CHECKS_EXTRA + ITEM_T * len(s.items)
        if s.id in loop_src:
            extra += LOOP_EXTRA
        t += (STEP_T + extra) * f
    return times


def build_cards(proc: Process, cols: Dict[str, int], lanes: Dict[str, dict], times: Dict[str, float],
                f: float) -> List[dict]:
    open_refs = {q.ref for q in proc.open_questions()}
    cards: List[dict] = []
    num = 0
    for s in proc.steps:
        w, h = card_size(s)
        x = x_of(cols[s.id])
        y = lanes[s.lane]["y"] + LANE_TOP
        if s.type in ("start", "end"):
            default = "START" if s.type == "start" else "KONEC"
        else:
            num += 1
            default = f"KROK {num}"
        inner = w - 24
        items = []
        if s.type == "checks":
            for i, it in enumerate(s.items):
                items.append({"title": it.title, "sub": it.sub,
                              "x": x + 12 + (i % 2) * ITEM_STEP_X, "y": y + CHECKS_HEAD + (i // 2) * ITEM_ROW,
                              "w": ITEM_W, "h": ITEM_H, "t": _r(times[s.id] + (CHECKS_EXTRA + i * ITEM_T) * f)})
        sub_px = text.WARN_PX if s.type == "checks" else text.SUB_PX
        cards.append({
            "id": s.id, "type": s.type, "lane": s.lane, "col": cols[s.id], "x": x, "y": y, "w": w, "h": h,
            "label": s.label or default,
            "title_lines": text.wrap(s.title, text.chars_for(inner, text.TITLE_PX)),
            "sub_lines": text.wrap(s.sub, text.chars_for(inner, sub_px)),
            "items": items, "question": s.id in open_refs, "t": times[s.id],
            "max_lines": [1, 1] if s.type == "checks" else [2, 2],
        })
    return cards


# ------------------------------------------------------------------ geometrie

def rect_of(d: dict) -> Rect:
    return (d["x"], d["y"], d["x"] + d["w"], d["y"] + d["h"])


def rects_overlap(a: Rect, b: Rect) -> bool:
    return a[0] < b[2] - 0.5 and b[0] < a[2] - 0.5 and a[1] < b[3] - 0.5 and b[1] < a[3] - 0.5


def segment_hits_rect(p: Sequence[float], q: Sequence[float], r: Rect, pad: float = 1.0) -> bool:
    x0, y0, x1, y1 = r[0] + pad, r[1] + pad, r[2] - pad, r[3] - pad
    sx0, sx1 = sorted((p[0], q[0]))
    sy0, sy1 = sorted((p[1], q[1]))
    return sx0 < x1 and sx1 > x0 and sy0 < y1 and sy1 > y0


def path_hits(points: Sequence[Sequence[float]], rects: Sequence[Rect]) -> bool:
    return any(segment_hits_rect(a, b, r) for a, b in zip(points, points[1:]) for r in rects)


def _collinear_overlap(p1, q1, p2, q2) -> bool:
    if p1[0] == q1[0] == p2[0] == q2[0]:
        a0, a1 = sorted((p1[1], q1[1]))
        b0, b1 = sorted((p2[1], q2[1]))
        return min(a1, b1) - max(a0, b0) > 0.5
    if p1[1] == q1[1] == p2[1] == q2[1]:
        a0, a1 = sorted((p1[0], q1[0]))
        b0, b1 = sorted((p2[0], q2[0]))
        return min(a1, b1) - max(a0, b0) > 0.5
    return False


def path_overlaps(points, others) -> bool:
    return any(_collinear_overlap(a, b, c, d)
               for a, b in zip(points, points[1:]) for o in others for c, d in zip(o, o[1:]))


def _cx(c: dict) -> float:
    return c["x"] + c["w"] / 2


def _ay(c: dict) -> float:
    return c["y"] + ANCHOR_Y


def route_main(a: dict, b: dict, how: str) -> List[Point]:
    """Pravoúhlá trasa a → b. how: h (stejný pruh), v (překryv ve sloupci), vh, hv."""
    down = b["y"] > a["y"]
    right = b["x"] > a["x"]
    if how == "h":
        if right:
            return [(a["x"] + a["w"], _ay(a)), (b["x"] - TIP_GAP, _ay(b))]
        return [(a["x"], _ay(a)), (b["x"] + b["w"] + TIP_GAP, _ay(b))]
    if how == "v":
        if b["x"] <= _cx(a) <= b["x"] + b["w"]:
            x = _cx(a)
        elif a["x"] <= _cx(b) <= a["x"] + a["w"]:
            x = _cx(b)
        else:
            x = (max(a["x"], b["x"]) + min(a["x"] + a["w"], b["x"] + b["w"])) / 2
        if down:
            return [(x, a["y"] + a["h"]), (x, b["y"] - TIP_GAP)]
        return [(x, a["y"]), (x, b["y"] + b["h"] + TIP_GAP)]
    if how == "vh":
        sx = _cx(a)
        sy = a["y"] + a["h"] if down else a["y"]
        ex = b["x"] - TIP_GAP if right else b["x"] + b["w"] + TIP_GAP
        return [(sx, sy), (sx, _ay(b)), (ex, _ay(b))]
    sx = a["x"] + a["w"] if right else a["x"]
    ex = _cx(b)
    ey = b["y"] - TIP_GAP if down else b["y"] + b["h"] + TIP_GAP
    return [(sx, _ay(a)), (ex, _ay(a)), (ex, ey)]


def route_loop(a: dict, b: dict, lanes: Dict[str, dict]) -> List[Point]:
    sx = a["x"] + a["w"] - LOOP_INSET
    ch = min(lanes[a["lane"]]["y"], lanes[b["lane"]]["y"]) + LOOP_CHANNEL
    ex = _cx(b)
    return [(sx, a["y"]), (sx, ch), (ex, ch), (ex, b["y"] - TIP_GAP)]


def choose_route(fl: Flow, a: dict, b: dict, obstacles: List[Rect], placed: List[List[Point]],
                 lanes: Dict[str, dict]) -> Tuple[List[Point], str]:
    if fl.kind == "loop" or (a["lane"] == b["lane"] and b["x"] <= a["x"]):
        return route_loop(a, b, lanes), "loop"
    if a["lane"] == b["lane"]:
        return route_main(a, b, "h"), "h"
    if a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]:
        return route_main(a, b, "v"), "v"
    order = [fl.route] if fl.route else ["vh", "hv"]
    cands = [(h, route_main(a, b, h)) for h in order]
    for h, pts in cands:
        if not path_hits(pts, obstacles) and not path_overlaps(pts, placed):
            return pts, h
    for h, pts in cands:
        if not path_hits(pts, obstacles):
            return pts, h
    return cands[0][1], cands[0][0]


def tip_points(points: Sequence[Sequence[float]]) -> List[List[float]]:
    (x1, y1), (x2, y2) = points[-2], points[-1]
    length = hypot(x2 - x1, y2 - y1) or 1e-6
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    px, py = -uy, ux
    bx, by = x2 - ux * 6, y2 - uy * 6
    return [[round(x2 + ux * 2, 1), round(y2 + uy * 2, 1)],
            [round(bx + px * 4, 1), round(by + py * 4, 1)],
            [round(bx - px * 4, 1), round(by - py * 4, 1)]]


def _label_pos(points: List[Point], kind: str) -> Tuple[List[float], str]:
    """Pozice a zarovnání popisku: nad vodorovným úsekem na střed, vedle svislého úseku vlevo zarovnaný."""
    if kind == "loop":
        (x1, y1), (x2, _) = points[1], points[2]
        return [round((x1 + x2) / 2, 1), round(y1 - 6, 1)], "middle"
    segs = list(zip(points, points[1:]))
    (x1, y1), (x2, y2) = max(segs, key=lambda s: hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]))
    if x1 == x2:
        return [round(x1 + 8, 1), round((y1 + y2) / 2 + 4, 1)], "start"
    return [round((x1 + x2) / 2, 1), round(y1 - 6, 1)], "middle"


def _wire_time(fl: Flow, proc: Process, times: Dict[str, float], f: float) -> float:
    if fl.kind == "loop":
        src = next(s for s in proc.steps if s.id == fl.src)
        extra = CHECKS_EXTRA + ITEM_T * len(src.items) if src.type == "checks" else 0.0
        return _r(times[fl.src] + (extra + 0.2) * f)
    if times[fl.dst] > times[fl.src]:
        return _r(times[fl.dst] - WIRE_LEAD * f)
    return _r(times[fl.src] + TIP_DELAY)


def build_spans(proc: Process, cards: Dict[str, dict], lanes: Dict[str, dict], times: Dict[str, float],
                f: float) -> List[dict]:
    out = []
    for i, sp in enumerate(proc.spans):
        a, b = cards[sp.src], cards[sp.dst]
        x0 = min(a["x"], b["x"])
        x1 = max(a["x"] + a["w"], b["x"] + b["w"])
        out.append({"key": f"span:{i}", "lane": sp.lane, "x": x0, "y": lanes[sp.lane]["span_y"], "w": x1 - x0,
                    "h": SPAN_H, "title": sp.title or "Průběžně", "text": sp.text,
                    "t": _r(times[sp.src] + SPAN_DELAY * f)})
    return out


def build_states(proc: Process, cards: List[dict], lanes_bottom: float, times: Dict[str, float], f: float):
    if not proc.states:
        return None, []
    content_right = max(c["x"] + c["w"] for c in cards)
    n = len(proc.states)
    pw = max(STATE_MIN_W, int((content_right - MARGIN - (n - 1) * STATE_GAP) / n))
    py = lanes_bottom + 40
    same: Dict[str, int] = {}
    pills, wires, steps = [], [], []
    in_order = True
    prev_raw = prev_lit = -1.0
    for i, st in enumerate(proc.states):
        k = same.get(st.at, 0)
        same[st.at] = k + 1
        raw = times[st.at] + SAME_STATE_DELAY * k * f
        if raw < prev_raw:
            in_order = False
        lit = _r(max(raw, prev_lit + MIN_STATE_GAP * f))  # rámeček nikdy nepřeskočí dva stavy najednou
        prev_raw, prev_lit = raw, lit
        x = MARGIN + i * (pw + STATE_GAP)
        pills.append({"id": st.id, "name": st.name, "sub": st.sub, "x": x, "y": py, "w": pw, "h": STATE_H,
                      "t": _r(0.35 + i * 0.06), "lit_t": lit})
        steps.append({"t": lit, "dx": i * (pw + STATE_GAP)})
        if i < n - 1:
            pts = [(x + pw + 5, py + STATE_H / 2), (x + pw + STATE_GAP - TIP_GAP, py + STATE_H / 2)]
            t = _r(0.45 + i * 0.06)
            wires.append({"id": f"sw{i}", "kind": "state", "src": st.id, "dst": proc.states[i + 1].id, "route": "h",
                          "points": [[round(x_, 1), round(y_, 1)] for x_, y_ in pts], "tip": tip_points(pts),
                          "t": t, "tip_t": _r(t + TIP_DELAY), "label": "", "label_pos": None,
                          "label_anchor": "middle", "label_t": None})
    total = _r(max(s["t"] for s in steps) + 0.6)
    return {"label": proc.states_label, "in_order": in_order, "divider_y": lanes_bottom + 12,
            "label_y": lanes_bottom + 30, "pills": pills, "ring": {"x": MARGIN - 5, "y": py - 5, "w": pw + 10, "h": STATE_H + 10,
                                     "steps": steps, "total": total}}, wires


def subtitle(proc: Process) -> str:
    parts = [proc.kind, "v" + proc.version]
    if proc.updated:
        parts.append(proc.updated)
    if proc.source:
        parts.append(proc.source)
    return " · ".join(parts)


def compute_layout(proc: Process) -> dict:
    flows = proc.all_flows()
    f = pace(proc)
    cols = assign_columns(proc)
    lanes = lane_geometry(proc)
    times = step_times(proc, flows, f)
    cards = build_cards(proc, cols, lanes, times, f)
    by_id = {c["id"]: c for c in cards}
    lanes_bottom = sum(l["h"] for l in lanes.values())
    spans = build_spans(proc, by_id, lanes, times, f)

    wires: List[dict] = []
    placed: List[List[Point]] = []
    for i, fl in enumerate(flows):
        a, b = by_id[fl.src], by_id[fl.dst]
        obstacles = [rect_of(c) for c in cards if c["id"] not in (a["id"], b["id"])] + [rect_of(s) for s in spans]
        pts, how = choose_route(fl, a, b, obstacles, placed, lanes)
        placed.append(pts)
        t = _wire_time(fl, proc, times, f)
        lpos, anchor = _label_pos(pts, fl.kind) if fl.label else (None, "middle")
        wires.append({"id": f"w{i}", "kind": fl.kind, "src": fl.src, "dst": fl.dst, "route": how,
                      "points": [[round(x, 1), round(y, 1)] for x, y in pts], "tip": tip_points(pts),
                      "t": t, "tip_t": _r(t + TIP_DELAY), "label": fl.label, "label_pos": lpos,
                      "label_anchor": anchor, "label_t": _r(t + LABEL_DELAY) if fl.label else None})

    states, state_wires = build_states(proc, cards, lanes_bottom, times, f)
    wires += state_wires
    right = max(c["x"] + c["w"] for c in cards)
    if states:
        last = states["pills"][-1]
        right = max(right, last["x"] + last["w"])
    height = states["pills"][0]["y"] + STATE_H + 16 if states else lanes_bottom + 16
    duration = _r(max(times.values()) + 1.0)
    if states:
        duration = max(duration, states["ring"]["total"])
    return {
        "schema": SCHEMA,
        "process": {"id": proc.id, "title": proc.title, "kind": proc.kind, "status": proc.status,
                    "version": proc.version, "updated": proc.updated, "source": proc.source},
        "meta": {"title": proc.title, "subtitle": subtitle(proc)},
        "width": right + MARGIN, "height": height, "duration": duration, "pace": _r(f),
        "lanes_bottom": lanes_bottom,
        "lanes": list(lanes.values()), "cards": cards, "wires": wires, "spans": spans, "states": states,
    }
