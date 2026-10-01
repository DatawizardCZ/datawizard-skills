---
title: process-mapping
date: 2026-10-01
---

# process-mapping

Mapování firemních procesů a procesní diagramy. Proces se popíše jednou v souboru `<proces>.process.toml` a z něj se generuje animovaný HTML výkres (s krokováním pro schůzky a tiskem do PDF), statické SVG, swimlane ve Figmě i Mermaid.

## Skilly

| Skill | K čemu |
|---|---|
| `process-mapping` | Vede mapování (rámec, as-is, analýza, to-be, validace, předání), vybírá typ diagramu, drží zdrojový popis |
| `process-map-html` | Animovaný HTML výkres: krokování, klik na detail, otázky a bolesti, světlý výkres, tisk, fullscreen, statické SVG |
| `process-map-figma` | Swimlane ve Figmě s animací, nebo staticky, když motion není zapnutý (Figma MCP) |

## Rychlý start

1. Řekni „zmapuj proces …“. Skill se zeptá na rámec a provede tě sběrem as-is.
2. Vzor popisu: `skills/process-mapping/examples/schvalovani-faktur.process.toml` (vymyšlený proces).
3. `python3 skills/process-mapping/scripts/pmap.py check|layout|mermaid|html|svg|figma "<spec>"`. Potřebuje Python 3.11+, nebo starší Python s knihovnou `tomli`, nebo `uv run`.

## Znalostní báze

V `skills/process-mapping/references/`:

- typy diagramů a rychlá volba,
- metodika mapování,
- notace,
- nástroje,
- formát popisu, Mermaid vzory,
- research se zdroji.

Šablony rozhovoru, workshopu s validační schůzkou a dokumentu procesu jsou v `templates/`.

## Vývoj

- **Testy:** `(cd skills/process-mapping/scripts && python3 -m unittest discover -s tests -t . -v)`.
- **Klientská data:** repo je veřejné, do příkladů, testů a commitů nepatří data klientů.
