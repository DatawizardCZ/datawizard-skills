"""Kód pro Figma MCP (use_figma): šablona skriptu + layout vložený jako JSON literál."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .model import SpecError

FIGMA_DIR = Path(__file__).resolve().parents[3] / "process-map-figma" / "scripts"
TEMPLATES = {"build": "build-swimlane.js", "motion": "add-motion.js"}
MAX_CODE = 50000  # limit parametru code nástroje use_figma


def _literal(obj) -> str:
    """JSON s jen ASCII znaky je platný JS literál; uvozovky, zpětná lomítka i U+2028 jsou escapované."""
    return json.dumps(obj, ensure_ascii=True, separators=(",", ":"))


def figma_code(L: dict, part: str, ids: Optional[dict] = None) -> str:
    if part not in TEMPLATES:
        raise SpecError(f"--part musí být build nebo motion, ne '{part}'")
    code = (FIGMA_DIR / TEMPLATES[part]).read_text(encoding="utf-8").replace("/*LAYOUT*/null", _literal(L))
    if part == "motion":
        if not isinstance(ids, dict):
            raise SpecError("pro --part motion je potřeba --ids s objektem ids z výsledku build")
        code = code.replace("/*IDS*/null", _literal(ids))
    if len(code) > MAX_CODE:
        raise SpecError(f"kód pro Figmu má {len(code)} znaků, use_figma unese {MAX_CODE}; rozděl proces na podprocesy")
    return code
