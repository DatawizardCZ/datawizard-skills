---
name: process-mapping
description: Vede mapování firemního procesu od rámce přes as-is, analýzu a to-be až po validaci s klientem a z jednoho zdrojového popisu (<proces>.process.toml) vyrábí procesní mapu jako animovaný HTML výkres, statické SVG, Figmu nebo Mermaid. Obsahuje znalostní bázi typů diagramů, notace, metodiky a nástrojů. Použij, kdykoli uživatel chce zmapovat nebo nakreslit proces, udělat procesní mapu, procesní schéma, swimlane, BPMN nebo vývojový diagram, popsat as-is a to-be, zjistit kdo co dělá a kde jsou předávky, připravit rozhovor nebo workshop o procesu, SIPOC, RACI, nebo vybrat vhodný typ diagramu či nástroj. Triggeruj na „zmapuj proces“, „procesní mapa“, „nakresli proces“, „diagram procesu“, „swimlane“, „BPMN“, „as-is“, „to-be“, „jak funguje proces“, „jaký diagram použít“. Nepoužívej pro průchody obrazovkami aplikace (product-design:user-flow-visualizer) ani pro discovery nového produktu přes víc oblastí (client-delivery:client-discovery). Komunikuj česky.
---

# Mapování procesů

Vedeš mapování firemního procesu a kreslíš ho. Zdroj pravdy je jeden soubor `<proces>.process.toml`; všechny výstupy se z něj generují a ručně se needitují.

## Skript

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/process-mapping/scripts/pmap.py" check "<spec>"
```

- Pracovní složka zůstává v projektu uživatele, cesty ke specu a výstupům dávej v uvozovkách (OneDrive cesty mají mezery a diakritiku).
- Když `${CLAUDE_PLUGIN_ROOT}` není k dispozici (Cursor, ruční kopie), použij adresář tohoto skillu, který se vypíše při načtení jako Base directory: `"<SKILL_DIR>/scripts/pmap.py"`.
- Na Pythonu < 3.11 je potřeba knihovna `tomli`; jinak `uv run "<…>/pmap.py" …`. Návratové kódy: 0 OK, 1 chyby v popisu, 2 soubor nejde načíst.

Příkazy: `check`, `layout`, `mermaid`, `html`, `svg`, `figma`. Formát popisu je v [references/process-spec.md](references/process-spec.md), vzor v `examples/schvalovani-faktur.process.toml`.

## 1. Poznej situaci a řekni ji nahlas

Nejdřív ověř, že jde o firemní proces: „Jde o proces s rolemi a předávkami mezi lidmi a systémy, nebo o průchod obrazovkami aplikace?“ Obrazovky patří do `product-design:user-flow-visualizer`.

| Signál | Fáze | Detail |
|---|---|---|
| „zmapuj proces X“, nový proces | 0 · Rámec | otázky níže, [mapping-method.md](references/mapping-method.md) |
| přepis schůzky, tabulka, „projdeme to s …“ | 1 · Sběr as-is | `templates/interview-guide.md`, `templates/workshop-agenda.md`; přepis nejdřív přes `content-tools:process-meeting-transcript` |
| máme kroky a role | 2 · Model as-is | spec `kind = "as-is"`, výkres, ověření s expertem |
| „co je na tom špatně“ | 3 · Analýza | bolesti (`pain`), čekání (`time`), předávky, výjimky, pravidla |
| „jak by to mělo být v systému“ | 4 · Návrh to-be | nový spec `kind = "to-be"`, každá změna navazuje na problém z analýzy |
| feedback od klienta | 5 · Validace | `templates/workshop-agenda.md` (validační schůzka), verze a stav |
| „připrav to pro vývoj“ | 6 · Předání | `templates/process-doc.md`, navazuje `product-design:implementation-spec` |

Když fáze není jasná, zeptej se: „Mapujeme, jak to funguje dnes, nebo navrhujeme, jak to má fungovat?“

Vstupem fáze 1 může být i process definition z `client-delivery:client-discovery`.

### Fáze 0: otázky (po jedné)

1. Proč proces mapujeme? (automatizace, zadání vývoje, zlepšení, dokumentace, audit) → určuje úroveň detailu: vývoj L3, zlepšení L2, přehled pro vedení L1.
2. Čím proces začíná a čím končí?
3. Kdo ho vlastní a kdo v něm pracuje?
4. Kdo mapu na konci schválí a do kdy?
5. Jak často proběhne? (objem)

Odpovědi zapiš do `[process]` (`purpose`, `trigger`, `outcome`, `owner`, `volume`) a hranice do dokumentu procesu jako SIPOC.

### Na konci každé fáze

Shrň, co vzniklo, vyjmenuj otevřené `??`, navrhni další fázi a počkej na uživatele.

## 2. Vyber diagram

Výchozí je swimlane (role a předávky). Podle [diagram-types.md](references/diagram-types.md) doporuč jiný typ, když jde o:

- životní cyklus objektu (stavový diagram),
- komunikaci systémů (sekvenční diagram),
- pravidla (rozhodovací tabulka),
- odpovědnosti (RACI).

Řekni, jestli ho plugin vyrobí.

- **„Chceme BPMN“:** swimlane z pluginu používá podmnožinu BPMN (start, úloha, rozhodnutí, smyčka, alternativa). Formální BPMN XML pro IT nebo workflow engine dělej v bpmn.io nebo draw.io podle [tools.md](references/tools.md).
- **Složité větvení** (paralelní větve, víc rozhodnutí za sebou): zapiš přechody explicitně (`auto_flow = false` a `[[flow]]`) a použij Mermaid výstup. Když se HTML výkres nepovede, řekni to.
- **Víc než 15 kroků:** navrhni rozdělit proces na podprocesy (každý svůj spec) s přehledovou mapou L1.

## 3. Zapiš proces do zdrojového popisu

- **Nic nevymýšlej.** Krok, roli, pravidlo ani číslo, které nezaznělo, nepřidávej. Zapiš ho jako `[[question]]` (ve výstupech `??`).
- **Ruční rozhodnutí a pravidla** patří do `detail` a `today`, ne do titulku. Systémy do `tools`, čekání a trvání do `time`, bolesti do `pain`.
- **U otázek** vyplň `who` (kdo odpoví). Po odpovědi `status = "resolved"` a `answer`.
- **Po každé změně** spusť `pmap.py check "<spec>"`. Chyby oprav, upozornění projdi s uživatelem. Upozornění na neznámý klíč je skoro vždy překlep.
- **Krok, po kterém tok nepokračuje** na další v pořadí (třeba konec větve), označ `next = false`.

## 4. Vyrob výstup

| Výstup | Kdy | Jak |
|---|---|---|
| HTML výkres | výchozí; prezentace, krokování na schůzce, offline prohlížení, tisk do PDF | skill `process-map-html` |
| Statické SVG | obrázek do prezentace nebo dokumentu | `pmap.py svg "<spec>"` |
| Figma | klient a designéři pracují ve Figmě, animace v prezentaci | skill `process-map-figma` |
| Mermaid | dokumentace v repu, GitHub, rychlý náhled, složité větvení | `pmap.py mermaid "<spec>"`, vzory v [references/mermaid.md](references/mermaid.md) |

## 5. Kam s výstupy

Když má projekt vlastní konvenci pro schémata, drž se jí. Jinak:

```text
processes/<proces>/
├── <proces>-as-is.process.toml   zdroj pravdy dnešního stavu
├── <proces>-to-be.process.toml   zdroj pravdy návrhu
├── <proces>-to-be.html           generované (výstupy se jmenují podle souboru specu)
├── <proces>-to-be.svg            generované
├── <proces>-to-be.mermaid.md     generované
└── <proces>.md                   dokument procesu k ruční editaci (templates/process-doc.md)
```

## Pravidla

- **Realita, ne ideál.** Mapuj, jak proces opravdu probíhá. As-is a to-be jsou dva soubory.
- **Stav a verze** jsou ve `[process]`: `draft` → `k-validaci` → `schvaleno`. Při každé validaci zvyš `version` (vždy v uvozovkách) a nastav `updated`. Schválení zapiš do `approved` (kdo, kdy).
- **Klientská data** zůstávají v klientském projektu. Do `source` nepiš interní cesty ani jména lidí. HTML ukazuje zdroj, otázky i poznámky „dnes“ každému, kdo soubor dostane.
- **Generované soubory** se needitují ručně. Změna jde vždy do specu a výstup se přegeneruje.

## Znalostní báze

- [diagram-types.md](references/diagram-types.md): typy diagramů a rychlá volba
- [mapping-method.md](references/mapping-method.md): fáze, rozhovor, workshop, analýza, časté chyby, kdy animovat
- [notation.md](references/notation.md): swimlane pravidla, úrovně detailu, BPMN podmnožina, naše značení
- [tools.md](references/tools.md): srovnání nástrojů a kdy který
- [research.md](references/research.md): zdroje ke všemu výše
