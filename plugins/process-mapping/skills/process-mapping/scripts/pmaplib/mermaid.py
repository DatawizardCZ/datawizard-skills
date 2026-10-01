"""Mermaid výstup: tok s pruhy rolí, diagram stavů a seznam otázek v markdownu."""
from __future__ import annotations

import re
from typing import List

from .model import Process

SHAPES = {
    "task": ('["', '"]'),
    "decision": ('{"', '"}'),
    "start": ('(["', '"])'),
    "end": ('(["', '"])'),
    "checks": ('[["', '"]]'),
}


def _q(s: str) -> str:
    """Text do popisku Mermaid: entity místo znaků, které by Mermaid vyložil jako HTML nebo syntaxi."""
    return (s.replace("#", "#35;").replace("&", "#amp;").replace("<", "#lt;")
             .replace(">", "#gt;").replace('"', "#quot;"))


def _md(s: str) -> str:
    """Text do markdownu mimo diagram."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _id(raw: str, prefix: str = "n_") -> str:
    """Bezpečné a jednoznačné id (vyhne se klíčovým slovům jako end; a-b a a_b zůstanou různé)."""
    return prefix + re.sub(r"[^0-9A-Za-z_]", lambda m: f"_{ord(m.group()):x}_", raw)


def render_flowchart(proc: Process) -> str:
    qs = {q.ref for q in proc.open_questions()}
    lines: List[str] = ["flowchart LR"]
    for lane in proc.lanes:
        steps = [s for s in proc.steps if s.lane == lane.id]
        spans = [(i, sp) for i, sp in enumerate(proc.spans) if sp.lane == lane.id]
        if not steps and not spans:
            continue
        lines.append(f'  subgraph {_id(lane.id, "lane_")}["{_q(lane.name)}"]')
        lines.append("    direction LR")
        for s in steps:
            a, b = SHAPES.get(s.type, SHAPES["task"])
            label = _q(s.title) + (" ??" if s.id in qs else "")
            lines.append(f"    {_id(s.id)}{a}{label}{b}")
        for i, sp in spans:
            lines.append(f'    span_{i}[/"{_q((sp.title or "Průběžně") + ": " + sp.text)}"/]')
        lines.append("  end")
    for f in proc.all_flows():
        arrow = "-.->" if f.kind in ("loop", "alt") else "-->"
        lab = f'|"{_q(f.label)}"|' if f.label else ""
        lines.append(f"  {_id(f.src)} {arrow}{lab} {_id(f.dst)}")
    marked = [_id(s.id) for s in proc.steps if s.id in qs]
    if marked:
        lines.append("  classDef q stroke:#d97706,stroke-width:2px")
        lines.append(f"  class {','.join(marked)} q")
    return "\n".join(lines)


def render_states(proc: Process) -> str:
    if not proc.states:
        return ""
    lines = ["stateDiagram-v2"]
    for st in proc.states:
        lines.append(f'  state "{_q(st.name)}" as {_id(st.id)}')
    ids = [_id(st.id) for st in proc.states]
    lines.append(f"  [*] --> {ids[0]}")
    lines += [f"  {a} --> {b}" for a, b in zip(ids, ids[1:])]
    lines.append(f"  {ids[-1]} --> [*]")
    return "\n".join(lines)


def _ref_name(proc: Process, ref: str) -> str:
    for s in proc.steps:
        if s.id == ref:
            return s.title
    for l in proc.lanes:
        if l.id == ref:
            return f"role {l.name}"
    for st in proc.states:
        if st.id == ref:
            return f"stav {st.name}"
    return ref


def render_markdown(proc: Process, source_name: str = "") -> str:
    bits = [proc.kind, proc.status, "v" + proc.version] + ([proc.updated] if proc.updated else [])
    meta = "_" + _md(" · ".join(bits)) + (f" · zdroj: {_md(proc.source)}" if proc.source else "") + "_"
    src = source_name or f"{proc.id}.process.toml"
    parts = [f"# {_md(proc.title)}", "", meta, "",
             f"> Generováno z `{src}` příkazem `pmap.py mermaid`. Needituj ručně, uprav zdroj.",
             "", "## Tok", "", "```mermaid", render_flowchart(proc), "```"]
    if proc.states:
        parts += ["", f"## {_md(proc.states_label)}", "", "```mermaid", render_states(proc), "```"]
    oq = proc.open_questions()
    if oq:
        parts += ["", "## Otevřené otázky", ""]
        parts += [f"- `??` {_md(q.text)} ({_md(_ref_name(proc, q.ref))}"
                  + (f", odpoví: {_md(q.who)}" if q.who else "") + ")" for q in oq]
    rq = proc.resolved_questions()
    if rq:
        parts += ["", "## Vyřešené otázky", ""]
        parts += [f"- {_md(q.text)} → {_md(q.answer)}" for q in rq]
    return "\n".join(parts) + "\n"
