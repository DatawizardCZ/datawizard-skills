"""Načtení a datový model zdrojového popisu procesu (<soubor>.process.toml)."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # Python 3.9 / 3.10
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]

STEP_TYPES = ("start", "task", "decision", "checks", "end")
FLOW_KINDS = ("main", "loop", "alt")
PROCESS_KINDS = ("as-is", "to-be")
STATUSES = ("draft", "k-validaci", "schvaleno")
QUESTION_STATUSES = ("open", "resolved")

# Povolené klíče bloků; neznámý klíč je skoro vždy překlep, check() na něj upozorní.
KEYS: Dict[str, set] = {
    "process": {"id", "title", "kind", "status", "version", "updated", "source", "states_label", "today",
                "auto_flow", "owner", "trigger", "outcome", "purpose", "volume", "approved"},
    "lane": {"id", "name", "access", "desc"},
    "step": {"id", "lane", "title", "type", "label", "sub", "detail", "out", "today", "col", "items",
             "tools", "time", "pain", "next"},
    "item": {"title", "sub"},
    "flow": {"from", "to", "kind", "label", "route"},
    "span": {"lane", "from", "to", "title", "text"},
    "state": {"id", "name", "at", "sub", "detail"},
    "question": {"ref", "step", "text", "status", "who", "answer"},
}
TOP_KEYS = {"process", "lane", "step", "flow", "span", "state", "question"}

TOML_HINT = (
    "nelze načíst TOML: Python {ver} nemá tomllib a chybí knihovna tomli.\n"
    "  Spusť skript přes uv:   uv run pmap.py …\n"
    "  nebo doinstaluj tomli:  python3 -m pip install --user tomli"
)


class SpecError(Exception):
    """Chyba ve zdrojovém popisu (nečitelný soubor, neplatné TOML, chybějící nebo špatné pole)."""


@dataclass
class Lane:
    id: str
    name: str
    access: str = ""
    desc: str = ""


@dataclass
class Item:
    title: str
    sub: str = ""


@dataclass
class Step:
    id: str
    lane: str
    title: str
    type: str = "task"
    label: str = ""
    sub: str = ""
    detail: str = ""
    out: str = ""
    today: str = ""
    col: Optional[int] = None
    items: List[Item] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    time: str = ""
    pain: List[str] = field(default_factory=list)
    next: bool = True


@dataclass
class Flow:
    src: str
    dst: str
    kind: str = "main"
    label: str = ""
    route: str = ""
    auto: bool = False


@dataclass
class Span:
    lane: str
    src: str
    dst: str
    title: str = ""
    text: str = ""


@dataclass
class State:
    id: str
    name: str
    at: str
    sub: str = ""
    detail: str = ""


@dataclass
class Question:
    ref: str
    text: str
    status: str = "open"
    who: str = ""
    answer: str = ""


@dataclass
class Process:
    id: str
    title: str
    kind: str = "to-be"
    status: str = "draft"
    version: str = "0.1"
    updated: str = ""
    source: str = ""
    states_label: str = "Stavy"
    today: List[str] = field(default_factory=list)
    auto_flow: bool = True
    owner: str = ""
    trigger: str = ""
    outcome: str = ""
    purpose: str = ""
    volume: str = ""
    approved: str = ""
    lanes: List[Lane] = field(default_factory=list)
    steps: List[Step] = field(default_factory=list)
    flows: List[Flow] = field(default_factory=list)
    spans: List[Span] = field(default_factory=list)
    states: List[State] = field(default_factory=list)
    questions: List[Question] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)  # upozornění z načtení (neznámé klíče, typ version)

    def all_flows(self) -> List[Flow]:
        """Explicitní přechody + automatický hlavní tok mezi po sobě jdoucími kroky.

        Automatický tok z kroku se nepřidá, když je krok typu end, má next = false,
        nebo když z něj už vede explicitní přechod typu main.
        """
        flows = list(self.flows)
        if self.auto_flow:
            explicit_main = {f.src for f in self.flows if f.kind == "main"}
            for a, b in zip(self.steps, self.steps[1:]):
                if a.type == "end" or not a.next or a.id in explicit_main:
                    continue
                flows.append(Flow(src=a.id, dst=b.id, kind="main", auto=True))
        return flows

    def open_questions(self, ref: Optional[str] = None) -> List[Question]:
        return [q for q in self.questions if q.status == "open" and (ref is None or q.ref == ref)]

    def resolved_questions(self, ref: Optional[str] = None) -> List[Question]:
        return [q for q in self.questions if q.status == "resolved" and (ref is None or q.ref == ref)]


def _line(v) -> str:
    """Jednořádkový text: převede na řetězec a slije bílé znaky (konce řádků nesmí rozbít výstupy).
    Seznam v jednořádkovém poli se spojí čárkami."""
    if isinstance(v, list):
        return ", ".join(_line(x) for x in v)
    return " ".join(str(v).split())


def _text(v) -> str:
    return str(v).strip()


def _list(v, key: str, where: str) -> List[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [_line(v)] if v.strip() else []
    if not isinstance(v, list) or any(isinstance(x, (dict, list)) for x in v):
        raise SpecError(f"{where}: {key} má být text nebo seznam textů, ne {v!r}")
    return [_line(x) for x in v]


def _bool(d: dict, key: str, where: str) -> bool:
    v = d.get(key, True)
    if not isinstance(v, bool):
        raise SpecError(f"{where}: {key} musí být true nebo false (bez uvozovek), ne {v!r}")
    return v


def _req(d: dict, key: str, where: str) -> str:
    if key not in d or d[key] in ("", None):
        raise SpecError(f"{where}: chybí povinné pole '{key}'")
    return _line(d[key])


def _unknown(d: dict, kind: str, where: str, notes: List[str]) -> None:
    for k in sorted(set(d) - KEYS[kind]):
        notes.append(f"{where}: neznámý klíč '{k}' (překlep?)")


def _blocks(data: dict, key: str) -> list:
    v = data.get(key, [])
    if not isinstance(v, list) or not all(isinstance(x, dict) for x in v):
        raise SpecError(f"[[{key}]] musí být pole bloků, ne jedna hodnota ani seznam textů")
    return v


def from_dict(data: dict) -> Process:
    p = data.get("process")
    if not isinstance(p, dict):
        raise SpecError("chybí blok [process]")
    notes: List[str] = []
    for k in sorted(set(data) - TOP_KEYS):
        notes.append(f"neznámý blok '{k}' (překlep?)")
    _unknown(p, "process", "[process]", notes)
    version = p.get("version", "0.1")
    if not isinstance(version, str):
        notes.append(f"[process] version = {version!r} zapiš v uvozovkách (\"0.10\" by bez nich bylo 0.1)")
    proc = Process(
        id=_req(p, "id", "[process]"),
        title=_req(p, "title", "[process]"),
        kind=_line(p.get("kind", "to-be")),
        status=_line(p.get("status", "draft")),
        version=_line(version),
        updated=_line(p.get("updated", "")),
        source=_line(p.get("source", "")),
        states_label=_line(p.get("states_label", "Stavy")),
        today=_list(p.get("today"), "today", "[process]"),
        auto_flow=_bool(p, "auto_flow", "[process]"),
        owner=_line(p.get("owner", "")),
        trigger=_line(p.get("trigger", "")),
        outcome=_line(p.get("outcome", "")),
        purpose=_line(p.get("purpose", "")),
        volume=_line(p.get("volume", "")),
        approved=_line(p.get("approved", "")),
        notes=notes,
    )
    for i, d in enumerate(_blocks(data, "lane"), 1):
        w = f"[[lane]] č. {i}"
        _unknown(d, "lane", w, notes)
        proc.lanes.append(Lane(id=_req(d, "id", w), name=_req(d, "name", w),
                               access=_line(d.get("access", "")), desc=_text(d.get("desc", ""))))
    for i, d in enumerate(_blocks(data, "step"), 1):
        w = f"[[step]] č. {i}"
        _unknown(d, "step", w, notes)
        items = []
        raw_items = d.get("items", [])
        if not isinstance(raw_items, list) or not all(isinstance(it, dict) for it in raw_items):
            raise SpecError(f'{w}: items má být seznam dlaždic {{ title = "…", sub = "…" }}')
        for it in raw_items:
            _unknown(it, "item", f"{w} items", notes)
            items.append(Item(title=_req(it, "title", f"{w} items"), sub=_line(it.get("sub", ""))))
        col = d.get("col")
        if col is not None and (isinstance(col, bool) or not isinstance(col, int)):
            raise SpecError(f"{w}: col musí být celé číslo, ne {col!r}")
        proc.steps.append(Step(
            id=_req(d, "id", w), lane=_req(d, "lane", w), title=_req(d, "title", w),
            type=_line(d.get("type", "task")), label=_line(d.get("label", "")), sub=_line(d.get("sub", "")),
            detail=_text(d.get("detail", "")), out=_line(d.get("out", "")), today=_line(d.get("today", "")),
            col=col, items=items, tools=_list(d.get("tools"), "tools", w), time=_line(d.get("time", "")),
            pain=_list(d.get("pain"), "pain", w), next=_bool(d, "next", w)))
    for i, d in enumerate(_blocks(data, "flow"), 1):
        w = f"[[flow]] č. {i}"
        _unknown(d, "flow", w, notes)
        proc.flows.append(Flow(src=_req(d, "from", w), dst=_req(d, "to", w), kind=_line(d.get("kind", "main")),
                               label=_line(d.get("label", "")), route=_line(d.get("route", ""))))
    for i, d in enumerate(_blocks(data, "span"), 1):
        w = f"[[span]] č. {i}"
        _unknown(d, "span", w, notes)
        proc.spans.append(Span(lane=_req(d, "lane", w), src=_req(d, "from", w), dst=_req(d, "to", w),
                               title=_line(d.get("title", "")), text=_line(d.get("text", ""))))
    for i, d in enumerate(_blocks(data, "state"), 1):
        w = f"[[state]] č. {i}"
        _unknown(d, "state", w, notes)
        proc.states.append(State(id=_line(d.get("id") or f"st{i}"), name=_req(d, "name", w), at=_req(d, "at", w),
                                 sub=_line(d.get("sub", "")), detail=_text(d.get("detail", ""))))
    for i, d in enumerate(_blocks(data, "question"), 1):
        w = f"[[question]] č. {i}"
        _unknown(d, "question", w, notes)
        ref = d.get("ref", d.get("step"))
        if ref in ("", None):
            raise SpecError(f"{w}: chybí povinné pole 'ref' (id kroku, role nebo stavu)")
        proc.questions.append(Question(ref=_line(ref), text=_req(d, "text", w), status=_line(d.get("status", "open")),
                                       who=_line(d.get("who", "")), answer=_text(d.get("answer", ""))))
    if not proc.steps:
        raise SpecError("proces nemá žádný [[step]]")
    return proc


def load(path) -> Process:
    if tomllib is None:
        raise SpecError(TOML_HINT.format(ver=sys.version.split()[0]))
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except FileNotFoundError:
        raise SpecError(f"soubor neexistuje: {path}") from None
    except OSError as e:
        raise SpecError(f"soubor nejde přečíst: {path} ({e.strerror})") from None
    try:
        text = raw.decode("utf-8-sig")  # BOM z Windows editorů nevadí
    except UnicodeDecodeError:
        raise SpecError(f"{path}: soubor není v kódování UTF-8 (třeba cp1250 z Windows); ulož ho jako UTF-8") from None
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        raise SpecError(f"{path}: neplatné TOML: {e}") from None
    return from_dict(data)
