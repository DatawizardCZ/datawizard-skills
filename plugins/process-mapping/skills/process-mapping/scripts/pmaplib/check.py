"""Kontrola zdrojového popisu: odkazy, výčty, tvar id, visící kroky, upozornění z načtení."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

from .model import FLOW_KINDS, PROCESS_KINDS, QUESTION_STATUSES, STATUSES, STEP_TYPES, Process

PROCESS_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NODE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass
class Issue:
    level: str  # "error" | "warning"
    msg: str

    def __str__(self) -> str:
        return ("CHYBA: " if self.level == "error" else "POZOR: ") + self.msg


def check(proc: Process) -> List[Issue]:
    out: List[Issue] = []

    def err(m: str) -> None:
        out.append(Issue("error", m))

    def warn(m: str) -> None:
        out.append(Issue("warning", m))

    for note in proc.notes:
        warn(note)
    if not PROCESS_ID.match(proc.id):
        err(f"[process] id '{proc.id}' musí být kebab-case (malá písmena, číslice, pomlčky)")
    if proc.kind not in PROCESS_KINDS:
        err(f"[process] kind = '{proc.kind}', povolené: {', '.join(PROCESS_KINDS)}")
    if proc.status not in STATUSES:
        err(f"[process] status = '{proc.status}', povolené: {', '.join(STATUSES)}")

    seen: Dict[str, str] = {}
    for what, items in (("role", proc.lanes), ("krok", proc.steps), ("stav", proc.states)):
        for it in items:
            if not NODE_ID.match(it.id):
                err(f"{what} '{it.id}': id smí obsahovat jen písmena bez diakritiky, číslice, - a _")
            if it.id in seen:
                err(f"id '{it.id}' je použité dvakrát ({seen[it.id]} a {what})")
            else:
                seen[it.id] = what

    lanes = {l.id for l in proc.lanes}
    steps = {s.id for s in proc.steps}
    states = {s.id for s in proc.states}

    for s in proc.steps:
        if s.lane not in lanes:
            err(f"krok '{s.id}': role '{s.lane}' neexistuje")
        if s.type not in STEP_TYPES:
            err(f"krok '{s.id}': typ '{s.type}', povolené: {', '.join(STEP_TYPES)}")
        if s.type == "checks" and not s.items:
            warn(f"krok '{s.id}': typ checks nemá žádné items")
        if s.col is not None and s.col < 0:
            err(f"krok '{s.id}': col musí být 0 nebo víc")
    for f in proc.flows:
        for end in (f.src, f.dst):
            if end not in steps:
                err(f"přechod {f.src} → {f.dst}: krok '{end}' neexistuje")
        if f.kind not in FLOW_KINDS:
            err(f"přechod {f.src} → {f.dst}: kind '{f.kind}', povolené: {', '.join(FLOW_KINDS)}")
        if f.route not in ("", "vh", "hv"):
            err(f"přechod {f.src} → {f.dst}: route '{f.route}', povolené: vh, hv")
        if f.src == f.dst:
            err(f"přechod {f.src} → {f.dst} vede sám do sebe")
    for sp in proc.spans:
        if sp.lane not in lanes:
            err(f"průběžná role: role '{sp.lane}' neexistuje")
        for end in (sp.src, sp.dst):
            if end not in steps:
                err(f"průběžná role v '{sp.lane}': krok '{end}' neexistuje")
    for st in proc.states:
        if st.at not in steps:
            err(f"stav '{st.id}': krok '{st.at}' (at) neexistuje")
    for q in proc.questions:
        if q.ref not in steps | lanes | states:
            err(f"otázka „{q.text[:40]}“: '{q.ref}' není krok, role ani stav")
        if q.status not in QUESTION_STATUSES:
            err(f"otázka „{q.text[:40]}“: status '{q.status}', povolené: {', '.join(QUESTION_STATUSES)}")
        if q.status == "resolved" and not q.answer:
            warn(f"otázka „{q.text[:40]}“ je vyřešená, ale nemá answer")

    used_lanes = {s.lane for s in proc.steps} | {sp.lane for sp in proc.spans}
    for l in proc.lanes:
        if l.id not in used_lanes:
            warn(f"role '{l.id}' nemá žádný krok ani průběžnou roli")

    valid = [f for f in proc.all_flows() if f.src in steps and f.dst in steps]
    has_in = {f.dst for f in valid}
    has_out = {f.src for f in valid}
    last = len(proc.steps) - 1
    for i, s in enumerate(proc.steps):
        if i > 0 and s.type != "start" and s.id not in has_in:
            warn(f"krok '{s.id}' nemá žádný vstup")
        if i < last and s.type != "end" and s.id not in has_out:
            warn(f"krok '{s.id}' nemá žádný výstup")
    return out
