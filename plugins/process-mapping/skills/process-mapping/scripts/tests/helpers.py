"""Sdílené pomůcky testů pmaplib."""
from __future__ import annotations

import copy
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "schvalovani-faktur.process.toml"

_BASE = {
    "process": {"id": "test", "title": "Test", "kind": "to-be", "status": "draft"},
    "lane": [{"id": "a", "name": "Role A"}, {"id": "b", "name": "Role B"}],
    "step": [
        {"id": "x1", "lane": "a", "title": "První"},
        {"id": "x2", "lane": "b", "title": "Druhý"},
        {"id": "x3", "lane": "a", "title": "Třetí"},
    ],
}


def base_spec() -> dict:
    """Minimální platný proces jako dict (kopie, test ho může měnit)."""
    return copy.deepcopy(_BASE)


def big_spec(n_steps: int = 32, n_lanes: int = 7) -> dict:
    """Zátěžový proces: hodně kroků a rolí, rozhodnutí s alternativou, smyčky, kontrolní krok."""
    lanes = [{"id": f"r{i}", "name": f"Role číslo {i}"} for i in range(n_lanes)]
    steps, flows = [], []
    for i in range(n_steps):
        lane = f"r{(i * 3) % n_lanes}"
        step = {"id": f"k{i}", "lane": lane, "title": f"Krok číslo {i} s delším názvem",
                "sub": "popis kroku, který se zalomí na dva řádky"}
        if i % 9 == 4 and i + 3 < n_steps:
            step["type"] = "decision"
            flows.append({"from": f"k{i}", "to": f"k{i + 3}", "kind": "alt", "label": "jinak"})
        if i % 11 == 7:
            flows.append({"from": f"k{i}", "to": f"k{i - 3}", "kind": "loop", "label": "vrátit"})
        if i == 15:
            step.update(type="checks", items=[{"title": f"Kontrola {j}", "sub": "něco"} for j in range(5)])
        steps.append(step)
    steps[0]["type"] = "start"
    steps[-1]["type"] = "end"
    return {"process": {"id": "big", "title": "Velký proces", "kind": "as-is", "status": "draft", "version": "0.1"},
            "lane": lanes, "step": steps, "flow": flows,
            "state": [{"name": f"Stav {j}", "at": f"k{j * 6}"} for j in range(5)]}
