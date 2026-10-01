"""Zalamování textu karet podle počtu znaků (neproporcionální písmo, šířka znaku 0,6 em)."""
from __future__ import annotations

from typing import List

CHAR_EM = 0.6
TITLE_PX = 12.5
SUB_PX = 10.0
WARN_PX = 10.4      # popis kontrolní karty má prostrkání .04 em
ITEM_TITLE_PX = 11.0
ITEM_SUB_PX = 9.5
SPAN_PX = 11.0


def chars_for(width_px: float, font_px: float) -> int:
    """Kolik znaků se vejde na řádek dané šířky."""
    return max(1, int(width_px // (font_px * CHAR_EM)))


def wrap(s: str, width: int) -> List[str]:
    """Zalomí text po slovech. Slovo delší než řádek zůstane celé na vlastním řádku."""
    lines: List[str] = []
    cur = ""
    for word in s.split():
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= width:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines
