"""Kontroly nad spočítaným rozložením: překryvy karet, šipky přes karty a přes sebe, délka textů, pořadí stavů."""
from __future__ import annotations

from typing import List

from . import text
from .check import Issue
from .layout import ITEM_W, _collinear_overlap, path_hits, rect_of, rects_overlap


def _advice(kind: str) -> str:
    if kind == "loop":
        return "posuň krok jinam přes col, nebo smyčku rozděl"
    return "pomůže route = \"hv\" / \"vh\" u přechodu nebo col u kroku"


def check_layout(L: dict) -> List[Issue]:
    out: List[Issue] = []

    def warn(m: str) -> None:
        out.append(Issue("warning", m))

    cards = L["cards"]
    by_id = {c["id"]: c for c in cards}
    for i, a in enumerate(cards):
        for b in cards[i + 1:]:
            if rects_overlap(rect_of(a), rect_of(b)):
                out.append(Issue("error", f"karty '{a['id']}' a '{b['id']}' se překrývají (zkontroluj ruční col)"))

    span_rects = [rect_of(s) for s in L["spans"]]
    flow_wires = [w for w in L["wires"] if w["kind"] != "state"]
    for w in flow_wires:
        pts = w["points"]
        others = [rect_of(c) for c in cards if c["id"] not in (w["src"], w["dst"])] + span_rects
        own = path_hits(pts[1:], [rect_of(by_id[w["src"]])]) or path_hits(pts[:-1], [rect_of(by_id[w["dst"]])])
        if path_hits(pts, others) or own:
            warn(f"šipka {w['src']} → {w['dst']} vede přes kartu; {_advice(w['kind'])}")
    for i, a in enumerate(flow_wires):
        for b in flow_wires[i + 1:]:
            if any(_collinear_overlap(p, q, r, s)
                   for p, q in zip(a["points"], a["points"][1:]) for r, s in zip(b["points"], b["points"][1:])):
                warn(f"šipky {a['src']} → {a['dst']} a {b['src']} → {b['dst']} leží na stejné čáře; "
                     f"pomůže route nebo col")

    for c in cards:
        mt, ms = c["max_lines"]
        if len(c["title_lines"]) > mt:
            warn(f"krok '{c['id']}': titulek má {len(c['title_lines'])} řádky, vejde se {mt}")
        if len(c["sub_lines"]) > ms:
            warn(f"krok '{c['id']}': popis (sub) má {len(c['sub_lines'])} řádky, vejde se {ms}")
        lim_t = text.chars_for(c["w"] - 24, text.TITLE_PX)
        lim_s = text.chars_for(c["w"] - 24, text.WARN_PX if c["type"] == "checks" else text.SUB_PX)
        if any(len(line) > lim_t for line in c["title_lines"]) or any(len(line) > lim_s for line in c["sub_lines"]):
            warn(f"krok '{c['id']}': slovo je delší než karta (třeba adresa); zkrať ho nebo dej do detail")
        for it in c["items"]:
            if (len(it["title"]) > text.chars_for(ITEM_W - 20, text.ITEM_TITLE_PX)
                    or len(it["sub"]) > text.chars_for(ITEM_W - 20, text.ITEM_SUB_PX)):
                warn(f"krok '{c['id']}': položka „{it['title']}“ se nevejde do dlaždice")
    for sp in L["spans"]:
        if len(sp["text"]) > text.chars_for(sp["w"] - 28, text.SPAN_PX):
            warn(f"průběžná role v '{sp['lane']}': text se nevejde, zkrať ho")
    if L["states"] and not L["states"]["in_order"]:
        warn("stavy jdou mimo pořadí kroků; zkontroluj 'at' u [[state]]")
    return out
