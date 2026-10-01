#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""pmap: zdrojový popis procesu (<soubor>.process.toml) → kontrola a výstupy.

Použití:
    pmap.py check   <spec>
    pmap.py layout  <spec> [-o <soubor>.layout.json]
    pmap.py mermaid <spec> [-o <soubor>.mermaid.md]
    pmap.py html    <spec> [-o <soubor>.html] [--link "Dokument=proces.md"]...
    pmap.py svg     <spec> [-o <soubor>.svg]
    pmap.py figma   <spec> --part build|motion [--ids ids.json] [-o kod.js]

Výchozí výstup leží vedle specu a jmenuje se podle souboru specu (<soubor> = název bez .process.toml),
takže as-is a to-be ve stejné složce se nepřepíšou.
Návratové kódy: 0 OK, 1 chyby v popisu nebo v argumentech, 2 soubor nejde načíst.
Na Pythonu < 3.11 je potřeba knihovna tomli, nebo spuštění přes `uv run pmap.py …`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pmaplib.check import Issue, check  # noqa: E402
from pmaplib.model import SpecError, load  # noqa: E402

COMMANDS = ("check", "layout", "mermaid", "html", "svg", "figma")
SUFFIX = {"layout": ".layout.json", "mermaid": ".mermaid.md", "html": ".html", "svg": ".svg"}
SAFE_URL = re.compile(r"^(https?:|mailto:|[^:/?#]+(?:[/?#]|$)|[./?#])", re.IGNORECASE)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="pmap.py", description="Zdrojový popis procesu → kontrola a výstupy.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in COMMANDS:
        p = sub.add_parser(name)
        p.add_argument("spec", help="cesta k <soubor>.process.toml")
        if name != "check":
            p.add_argument("-o", "--out", help="výstupní soubor (výchozí vedle specu)")
        if name == "html":
            p.add_argument("--link", action="append", default=[], metavar="TEXT=URL",
                           help="odkaz v hlavičce stránky (relativní cesta, http, https, mailto); lze opakovat")
        if name == "figma":
            p.add_argument("--part", required=True, choices=("build", "motion"))
            p.add_argument("--ids", help="JSON soubor s objektem ids z výsledku build (pro --part motion)")
    return ap


def spec_stem(spec: Path) -> str:
    name = spec.name
    return name[: -len(".process.toml")] if name.endswith(".process.toml") else spec.stem


def default_out(spec: Path, cmd: str, part: str = "") -> Path:
    if cmd == "figma":
        return spec.parent / f"{spec_stem(spec)}.figma-{part}.js"
    return spec.parent / f"{spec_stem(spec)}{SUFFIX[cmd]}"


def parse_links(raw: List[str]) -> List[Tuple[str, str]]:
    links = []
    for item in raw:
        text, sep, url = item.partition("=")
        if not sep or not text or not url:
            raise SpecError(f"--link čeká TEXT=URL, dostal '{item}'")
        if not SAFE_URL.match(url):
            raise SpecError(f"--link: povolená je relativní cesta, http, https nebo mailto, ne '{url}'")
        links.append((text, url))
    return links


def run_checks(proc) -> Tuple[Optional[dict], List[Issue]]:
    """Kontrola popisu; když nemá chyby, spočítá layout a zkontroluje i ten."""
    issues = check(proc)
    if any(i.level == "error" for i in issues):
        return None, issues
    from pmaplib.layout import compute_layout
    from pmaplib.lint import check_layout
    L = compute_layout(proc)
    return L, issues + check_layout(L)


def render(cmd: str, proc, L: dict, a, spec: Path) -> str:
    if cmd == "layout":
        return json.dumps(L, ensure_ascii=False, indent=1)
    if cmd == "mermaid":
        from pmaplib.mermaid import render_markdown
        return render_markdown(proc, spec.name)
    if cmd == "html":
        from pmaplib.html import render_html
        return render_html(proc, L, parse_links(a.link))
    if cmd == "svg":
        from pmaplib.html import render_svg
        return render_svg(proc, L)
    if cmd == "figma":
        from pmaplib.figma import figma_code
        ids = None
        if a.part == "motion":
            if not a.ids:
                raise SpecError("--part motion potřebuje --ids <ids.json>")
            try:
                ids = json.loads(Path(a.ids).read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                raise SpecError(f"--ids nejde přečíst jako JSON: {e}") from None
        return figma_code(L, a.part, ids)
    raise ValueError(cmd)


def main(argv: Optional[List[str]] = None) -> int:
    a = build_parser().parse_args(argv)
    try:
        proc = load(a.spec)
    except SpecError as e:
        print(f"CHYBA: {e}", file=sys.stderr)
        return 2
    L, issues = run_checks(proc)
    for i in issues:
        print(i, file=sys.stderr)
    if L is None or any(i.level == "error" for i in issues):
        return 1
    if a.cmd == "check":
        warnings = sum(1 for i in issues if i.level == "warning")
        note = f", {warnings} upozornění" if warnings else ""
        print(f"OK: {proc.id} · {len(proc.steps)} kroků, {len(proc.lanes)} rolí{note}")
        return 0
    spec = Path(a.spec)
    try:
        content = render(a.cmd, proc, L, a, spec)
    except SpecError as e:
        print(f"CHYBA: {e}", file=sys.stderr)
        return 1
    out = Path(a.out) if a.out else default_out(spec, a.cmd, getattr(a, "part", ""))
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
    except OSError as e:
        print(f"CHYBA: výstup nejde zapsat: {out} ({e.strerror}); -o čeká cestu k souboru", file=sys.stderr)
        return 1
    print(f"OK: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
