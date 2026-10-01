---
title: Formát zdrojového popisu procesu (<proces>.process.toml)
date: 2026-10-01
---

# Formát zdrojového popisu procesu

Jeden proces = jeden soubor `<proces>.process.toml` (as-is a to-be zvlášť, třeba `faktury-as-is.process.toml` a `faktury-to-be.process.toml`). Výstupy se jmenují podle souboru, ne podle `id`. Vzor se všemi možnostmi: `examples/schvalovani-faktur.process.toml`.

**Pořadí je důležité.** Kroky (`[[step]]`) se kreslí zleva doprava v pořadí zápisu a mezi po sobě jdoucími kroky vede automaticky hlavní tok. Přesunutím bloku se změní tok i sloupce.

**Texty** v jednořádkových polích (titulek, popis, názvy) se slijí do jednoho řádku. Víceřádkový text (`"""…"""`) má smysl jen v `detail`, `desc` a `answer`.

**Neznámý klíč** (`detial`, `type` u přechodu místo `kind`) `check` ohlásí jako upozornění; do výstupů se nedostane.

## [process]

| Pole | Povinné | Hodnoty | Výchozí | Co dělá |
|---|---|---|---|---|
| `id` | ano | kebab-case | | identifikátor procesu |
| `title` | ano | text | | název ve výkresu |
| `kind` | | `as-is`, `to-be` | `to-be` | dnešní stav, nebo návrh |
| `status` | | `draft`, `k-validaci`, `schvaleno` | `draft` | štítek ve výkresu |
| `version` | | text v uvozovkách | `"0.1"` | `0.10` bez uvozovek by bylo `0.1` |
| `updated` | | datum `YYYY-MM-DD` | | datum poslední úpravy ve výkresu |
| `source` | | text | | zdroj (schůzka, workshop); bez interních cest a jmen |
| `owner` | | text | | vlastník procesu |
| `trigger` | | text | | čím proces začíná |
| `outcome` | | text | | čím končí, výsledek |
| `purpose` | | text | | proč mapujeme (určuje úroveň detailu) |
| `volume` | | text | | objem („zhruba 300 měsíčně“) |
| `approved` | | text | | kdo a kdy schválil |
| `today` | | seznam textů (nebo jeden text) | | shrnutí as-is v přehledu |
| `states_label` | | text | `Stavy` | nadpis pruhu stavů |
| `auto_flow` | | `true`, `false` | `true` | automatický hlavní tok mezi kroky |

## [[lane]] (role nebo systém)

| Pole | Povinné | Hodnoty | Výchozí | Co dělá |
|---|---|---|---|---|
| `id` | ano | písmena bez diakritiky, číslice, `-`, `_` | | identifikátor |
| `name` | ano | text | | popisek pruhu |
| `access` | | text | | oprávnění (v detailu role) |
| `desc` | | text | | co role dělá |

## [[step]]

| Pole | Povinné | Hodnoty | Výchozí | Co dělá |
|---|---|---|---|---|
| `id` | ano | jako u role | | identifikátor (zůstává stejný napříč verzemi, ukazuje se v detailu) |
| `lane` | ano | id role | | pruh |
| `title` | ano | text | | titulek karty (17 znaků × 2 řádky; sloveso + předmět) |
| `type` | | `start`, `task`, `decision`, `checks`, `end` | `task` | tvar karty |
| `label` | | text | `KROK n`, `START`, `KONEC` | štítek karty |
| `sub` | | text | | popis na kartě (21 znaků × 2 řádky) |
| `detail` | | text | | popis v panelu po kliku |
| `out` | | text | | výstup kroku |
| `today` | | text | | jak se to dělá dnes |
| `tools` | | seznam textů | | systémy a nástroje |
| `time` | | text | | trvání a čekání („15 min, čeká 1–2 dny“) |
| `pain` | | seznam textů | | bolesti (v detailu a v přehledu) |
| `items` | jen `checks` | seznam `{ title, sub }` | | dlaždice kontrolní karty (18 / 21 znaků) |
| `col` | | celé číslo ≥ 0 | | ruční sloupec |
| `next` | | `true`, `false` | `true` | `false` = z kroku nevede automatický tok na další |

## [[flow]] (jen to, co nejde automaticky)

| Pole | Povinné | Hodnoty | Výchozí | Co dělá |
|---|---|---|---|---|
| `from`, `to` | ano | id kroků | | odkud a kam |
| `kind` | | `main`, `loop`, `alt` | `main` | hlavní tok, návrat (oranžová čárkovaná), alternativa (šedá čárkovaná) |
| `label` | | text | | popisek šipky |
| `route` | | `vh`, `hv` | automaticky | ruční trasa: svisle a pak vodorovně, nebo naopak |

Explicitní `main` z kroku nahradí jeho automatický tok. Rozhodnutí se dvěma výstupy: jeden `main` (může mít popisek), druhý `alt`.

## [[span]] (průběžná role)

| Pole | Povinné | Co dělá |
|---|---|---|
| `lane` | ano | pruh |
| `from`, `to` | ano | první a poslední krok, nad kterými se táhne |
| `title` | | nadpis (výchozí „Průběžně“) |
| `text` | | co role dělá |

## [[state]] (stavy objektu)

| Pole | Povinné | Výchozí | Co dělá |
|---|---|---|---|
| `id` | | `st<n>` | identifikátor (pro otázky) |
| `name` | ano | | název stavu |
| `at` | ano | | krok, se kterým se stav rozsvítí |
| `sub` | | | popis na kartě stavu |
| `detail` | | | popis v panelu |

Víc stavů na stejném kroku se rozsvítí postupně. Stavy mají jít ve stejném pořadí jako kroky, jinak `check` upozorní.

## [[question]]

| Pole | Povinné | Hodnoty | Výchozí | Co dělá |
|---|---|---|---|---|
| `ref` (nebo `step`) | ano | id kroku, role nebo stavu | | k čemu se otázka váže |
| `text` | ano | text | | otázka (ve výstupech `??`) |
| `who` | | text | | kdo odpoví |
| `status` | | `open`, `resolved` | `open` | |
| `answer` | | text | | odpověď (u vyřešené) |

## Rozložení

- **Sloupce.** Krok dostane sloupec podle pořadí. Krok v jiném pruhu než předchozí sdílí jeho sloupec, když je místo volné a předchozí krok sám nepřišel z jiného pruhu. Kontrolní karta zabírá 2 sloupce.
- **Trasy.** Ve stejném pruhu vodorovně, ve stejném sloupci svisle, jinak `vh` nebo `hv` tak, aby šipka neprotnula kartu a neležela na jiné šipce. Smyčka vede horem nad kartami.
- **Když výsledek nesedí:** `col` u kroku, `route` u přechodu, `next = false`. Nad 15 kroků rozděl proces na podprocesy.

## Příkazy pmap.py

| Příkaz | Výstup |
|---|---|
| `check "<spec>"` | kontrola popisu i rozložení; upozornění neblokují |
| `layout "<spec>"` | `<proces>.layout.json` (geometrie a časování) |
| `mermaid "<spec>"` | `<proces>.mermaid.md` |
| `html "<spec>" [--link "Text=cesta"]` | `<proces>.html` |
| `svg "<spec>"` | `<proces>.svg` (statický, světlý) |
| `figma "<spec>" --part build\|motion [--ids ids.json]` | kód pro `use_figma` |

Všechny mají `-o` pro jinou cestu. Návratové kódy: 0 OK, 1 chyby v popisu nebo argumentech, 2 soubor nejde načíst.
