---
title: "Plugin process-mapping: mapování procesů a procesní diagramy"
date: 2026-10-01
status: draft
type: strategy
---

# Plugin `process-mapping`

Návrh nového pluginu v `datawizard-skills`. Plugin vede mapování procesu od rámce po schválené to-be a z jednoho zdrojového popisu vyrábí:

- animovaný HTML výkres s krokováním,
- statické SVG,
- procesní mapu ve Figmě,
- Mermaid.

Součástí je znalostní báze (typy diagramů, metodika, notace, nástroje) podložená researchem.

Návrh vznikal postupně:

- **2026-09-30 až 2026-10-01:** schválený v konverzaci po částech.
- **Review sedmi agentů (replan):** přidal ochranu klientských dat, škálování na velké procesy, tisk, statické SVG, krokování a data z mapování v popisu.

Nic z toho zatím není postavené.

## Cíl

1. Na novém projektu stačí říct „zmapuj proces X“. Agent vybere vhodný typ diagramu, provede mapování (as-is, analýza, to-be, validace) a vytvoří výstup ve zvoleném nástroji v kvalitě referenční procesní mapy z klientského projektu (výroba, 2026-09).
2. Tým má na jednom místě znalostní bázi: jak procesy mapovat a kreslit, jaké typy diagramů existují a kdy který použít, jaké nástroje máme k dispozici.
3. Proces se popisuje jednou (zdrojový soubor) a všechny výstupy se z něj generují, takže se nerozjedou.
4. Výkres jde použít na schůzce (krokování), poslat e-mailem (funguje offline i v náhledu přílohy), vytisknout a vložit do prezentace.

## Výchozí stav

| Co existuje | Co umí | Vztah k novému pluginu |
|---|---|---|
| `client-delivery:client-discovery` | Rozhovor s expertem, formalizace do textové process definition, dál business analýza a produktový design | Zůstává pro discovery k produktu. Jeho process definition je platný vstup fáze 1. Do popisu obou skillů jedna věta o hranici (schváleno). |
| `product-design:user-flow-visualizer` | Uživatelské průchody aplikací (Mermaid + HTML prototypy obrazovek) | Zůstává pro UI flows. Do jeho popisu jedna věta, že firemní procesy kreslí `process-mapping` (schváleno). |
| `web-motion:animated-demo-windows` (`blueprint-pipeline.html`) | Kreslící se SVG výkres (pathLength + stroke-dashoffset), časování, reduced-motion | Zdroj animačního vzoru; HTML výkres převezme hodnoty a odkáže na šablonu. |
| `knowledge-capture:web-research` | Pravidla pro research (bezplatné nástroje první) | Podle něj se dělá research. |
| Referenční klientský projekt: generátor HTML výkresu | Ručně rozmístěný animovaný výkres jednoho procesu | Vzor pro HTML výstup; zůstává, jak je. Přejímací test ho napodobí lokálně. |
| Referenční klientský projekt: Figma soubor s procesní mapou | Swimlane s motion keyframes přes Figma MCP | Vzor pro Figma výstup a zdroj pastí. |

## Rozhodnutí

- **Nový plugin** `process-mapping` (varianta A). Zamítnuto: rozšířit `client-delivery`, rozdělit do tří pluginů.
- **Celý cyklus:** skill vede i samotné mapování.
- **Výstupy, které plugin skutečně vyrobí:** HTML výkres, statické SVG, Figma (s animací; když motion není pro účet zapnutý, statická mapa), Mermaid. draw.io a BPMN XML jsou jen ve znalostní bázi.
- **Verze 0.1 obsahuje i:** tisk a PDF, statické SVG, datum ve výkresu, velké procesy (minimální měřítko, vodorovný posun, zrychlení animace, zátěžový test), data z mapování v popisu, režim krokování. (Karel, 2026-10-01.)
- **Zdrojový popis v TOML.** Python 3.11+ načte vestavěným `tomllib`, starší Python knihovnou `tomli`, jinak hláška s návodem na `uv run` (PEP 723 hlavička `requires-python = ">=3.11"`).
- **Výstupy bez externích zdrojů.** Žádné webové fonty (GDPR u klientských dokumentů, práce offline); systémové neproporcionální písmo, CSP s hashi skriptů, `no-referrer`.
- **Commity** lokálně po každém tasku na větvi `agent/process-mapping-plugin`, push jen na Karlův pokyn. (Karel, 2026-10-01.)
- **Repo je veřejné:**
  - Vzorový proces je celý vymyšlený a strukturou se od referenčního liší: schvalování přijatých faktur, 5 rolí, rozhodnutí o dvou větvích.
  - Žádná jména, data ani formulace klienta, ani v historii commitů.
  - Kontrolu dělají lokální git hooky (`pre-commit` nad připraveným obsahem, `commit-msg`, `pre-push` nad historií) se seznamem výrazů, který je jen lokálně.
  - Odkazy na referenční projekt jsou v gitignorovaných `docs/plans/*.local.*`.

## Struktura pluginu

```text
plugins/process-mapping/
├── .claude-plugin/plugin.json
├── README.md
└── skills/
    ├── process-mapping/
    │   ├── SKILL.md
    │   ├── references/          research, diagram-types, mapping-method, notation, tools, process-spec, mermaid
    │   ├── templates/           interview-guide, workshop-agenda (vč. validační schůzky), process-doc
    │   ├── examples/schvalovani-faktur.process.toml
    │   ├── assets/              process-map.html.tmpl, process-map.js, fullscreen.js
    │   └── scripts/
    │       ├── pmap.py          CLI
    │       ├── pmaplib/         model, check, text, layout, lint, mermaid, html, figma
    │       └── tests/
    ├── process-map-figma/
    │   ├── SKILL.md
    │   └── scripts/             build-swimlane.js, add-motion.js (šablony, data vkládá pmap.py figma)
    └── process-map-html/
        └── SKILL.md
```

Skilly volají skript přes `"${CLAUDE_PLUGIN_ROOT}/skills/process-mapping/scripts/pmap.py"`; bez proměnné (Cursor) přes adresář skillu. Pracovní složka zůstává v projektu uživatele, cesty jsou v uvozovkách.

## Zdrojový popis procesu (`<proces>.process.toml`)

Bloky a pole (plný popis v `references/process-spec.md`):

- **`[process]`:** `id` (kebab-case), `title`, `kind` (as-is | to-be), `status` (draft | k-validaci | schvaleno), `version` (text), `updated`, `source`, `owner`, `trigger`, `outcome`, `purpose`, `volume`, `approved`, `today` (seznam), `states_label`, `auto_flow`.
- **`[[lane]]`:** `id`, `name`, `access`, `desc`.
- **`[[step]]`:** `id`, `lane`, `title`, `type` (start | task | decision | checks | end), `label`, `sub`, `detail`, `out`, `today`, `tools` (seznam), `time`, `pain` (seznam), `items` (u checks), `col`, `next` (false = bez automatického toku na další krok).
- **`[[flow]]`:** `from`, `to`, `kind` (main | loop | alt), `label`, `route` (vh | hv). Explicitní `main` z kroku nahradí automatický tok.
- **`[[span]]`:** průběžná role přes víc kroků (`lane`, `from`, `to`, `title`, `text`).
- **`[[state]]`:** `id`, `name`, `at`, `sub`, `detail`.
- **`[[question]]`:** `ref` (nebo `step`; krok, role nebo stav), `text`, `who`, `status` (open | resolved), `answer`.

Načtení:

- jednořádková pole se slijí do jednoho řádku;
- hodnoty se převedou na text;
- `today` smí být i jeden text;
- neznámý klíč nebo `version` bez uvozovek je upozornění;
- chybějící povinné pole, špatné `col` nebo nečitelný soubor je srozumitelná chyba (žádný traceback).

## `pmap.py`

| Příkaz | Co dělá |
|---|---|
| `check` | Kontrola popisu (odkazy, výčty, tvar id, unikátnost, visící kroky, upozornění z načtení) a rozložení (překryvy karet = chyba; šipky přes karty včetně vlastních, šipky na stejné čáře, přetečení textů, pořadí stavů = upozornění s radou, co změnit) |
| `layout` | `<soubor>.layout.json` (`schema: 1`): sloupce, karty, trasy, stavy, časování, meta pro Figmu |
| `mermaid` | `<soubor>.mermaid.md`: tok s pruhy rolí (i role jen s průběžnou rolí), stavy, otevřené a vyřešené otázky |
| `html` | `<soubor>.html` (`--link TEXT=URL`, jen relativní, http, https, mailto) |
| `svg` | `<soubor>.svg`: statické světlé SVG ve finálním stavu |
| `figma` | kód pro `use_figma` (`--part build` nebo `motion --ids`), data jako ASCII JSON literál, odmítne kód nad 50 000 znaků |

Výchozí výstupy leží vedle specu a jmenují se podle souboru specu (as-is a to-be se nepřepíšou); `-o` vytvoří i chybějící složku. Návratové kódy 0 / 1 / 2.

### Rozložení a trasy

- Sloupec 166 px, karta 152 × 100, kontrolní karta přes 2 sloupce s dlaždicemi 2 × N, nad kartami 52 px (kanál smyček na 34 px).
- Kroky zleva doprava v pořadí zápisu. Krok v jiném pruhu sdílí sloupec předchozího, když je místo volné a předchozí krok sám nepřišel z jiného pruhu (žádný cik-cak). `col` pravidlo přepíše.
- Šipky pravoúhle: stejný pruh vodorovně, překryv ve sloupci svisle, jinak `vh`, nebo `hv`. Vybere se první trasa, která neprotne kartu ani průběžnou roli a neleží na stejné čáře jako už nakreslená šipka.
- Smyčka vede horem nad kartami (čárkovaná oranžová), alternativa je čárkovaná šedá. Popisek je nad vodorovným úsekem, u svislého vedle čáry.
- Složité větvení (paralelní větve, víc rozhodnutí za sebou) mimo rozsah automatiky: explicitní `[[flow]]` + Mermaid.

### Časování

- **Hodnoty z web-motion:** čára 0,7 s, uzel 0,55 s, start přes IntersectionObserver (práh 0) + odklad 400 ms, pojistka 2,5 s.
- **Rytmus kroků:** 0,8 s. Kontrolní krok má navíc 0,4 s + 0,15 s na dlaždici a krok se smyčkou navíc 0,9 s.
- **Šipky a hroty:** šipka do kroku začíná 0,5 s před ním. Hrot je samostatný prvek a objeví se 0,55 s po začátku čáry.
- **Dlouhé procesy:** když by animace trvala déle než 11 s, celý rytmus se úměrně zrychlí (32 kroků se vejde do 15 s).
- **Stavy** se rozsvěcují s krokem `at`. Na stejném kroku jdou po 0,8 s a vždy rostoucím tempem, takže rámeček nepřeskočí dva stavy najednou. Stav mimo pořadí kroků je upozornění.

## Výstupy

### HTML výkres (`process-map-html`)

- **Obsah stránky:**
  - hlavička se stavem, verzí, datem úpravy i vygenerování a zdrojem;
  - blueprint i světlý výkres;
  - tiskový styl (světlý, na šířku, bez ovládání a panelu, finální stav).
- **Animace a prezentace:**
  - Přehrát znovu, Přeskočit, Krokovat (← →, mezerník, Esc), s otevřeným detailem aktuálního kroku;
  - bez JavaScriptu a při reduced-motion rovnou finální stav (skryté stavy jen pod třídou `armed`);
  - po doběhnutí se výkres přepne do statického stavu, takže fullscreen animaci nerestartuje.
- **Detail a přehled:**
  - klik nebo Enter na krok, roli, průběžnou roli a stav otevře detail: popis, výstup, dnes, systémy, čas, id, bolesti, otevřené i vyřešené otázky;
  - přehled v panelu ukazuje rámec, dnes, bolesti a otevřené otázky, všechno klikací.
- **Velké procesy:** výkres se nezmenší pod 85 %, posouvá se vodorovně a popisky rolí zůstávají vidět.
- **Fullscreen:** zoom a posun; klik na uzel funguje (ukazatel se zachytí až po tahu).
- **Bezpečnost:** žádné externí zdroje, CSP s hashi skriptů, data ve skriptu jako JSON s escapovaným `<`, `>`, `&`, U+2028/2029.

### Statické SVG

Světlé barvy přímo v SVG, finální stav, bez animačních tříd a masek. Obrázek do prezentace nebo dokumentu.

### Figma (`process-map-figma`)

Postup:

1. Načíst skilly (`figma-use`, `figma-use-motion`, před novým souborem `figma-create-new-file`).
2. `pmap.py check`.
3. Soubor (klientská mapa jen v týmu klienta).
4. Ověřit motion API: bez něj statická mapa a krok 6 se vynechá.
5. `pmap.py figma --part build` → `use_figma`; uložit `ids`.
6. `pmap.py figma --part motion --ids` → `use_figma`.
7. `export_video` + snímky přes `ffmpeg` ve scratchpadu, pak smazat.

Pasti:

- **Motion API:** feature flag, `PATH_TRIM_END` nejde na čárkované čáry, neanimovat rámec na nejvyšší úrovni.
- **Klidový stav = finální stav:** rámeček stavů stojí na posledním stavu, animace ho posouvá relativně.
- **Písmo:** Inter „Semi Bold“, bez znaku ↺.
- **Limit:** 50 000 znaků kódu.

### Mermaid

Entity pro speciální znaky (`#quot;`, `#lt;`, `#gt;`, `#amp;`, `#35;`), jednoznačná id (`a-b` ≠ `a_b`, `end` je bezpečné), konvence sladěné s `client-discovery` (popisky v `["…"]`, jediné stylování je třída `q` pro otázky). Ověření přes připnutý `@mermaid-js/mermaid-cli@12.0.0`; klientské diagramy ne do online editorů.

### Kam s výstupy

Konvence projektu má přednost. Jinak `processes/<proces>/` s `<proces>-as-is.process.toml`, `<proces>-to-be.process.toml`, generovanými výstupy podle jména souboru a ručním `<proces>.md`.

## Cyklus mapování (hlavní skill)

Fáze 0–6 (Rámec, Sběr as-is, Model as-is, Analýza, Návrh to-be, Validace, Předání). Skill fázi řekne nahlas.

Na konci každé fáze:

- shrne, co vzniklo;
- vyjmenuje `??`;
- navrhne další fázi a počká.

Fáze 0 se ptá po jedné otázce: účel a z něj úroveň detailu, začátek a konec, vlastník a lidé v procesu, kdo schválí a do kdy, objem.

Pravidla:

- **Nic nevymýšlet.** Co nezaznělo, jde do `??` s `who`.
- **Analýza** používá bolesti, čas, předávky, výjimky a pravidla.
- **To-be** navazuje na problémy z analýzy.
- **Validace** prochází 2–3 skutečné případy na krokované mapě a končí schválením (`approved`, `version`).

Hranice proti `user-flow-visualizer` pohlídá úvodní otázka „proces s rolemi a předávkami, nebo průchod obrazovkami?“.

## Znalostní báze (`references/`)

**`diagram-types.md`:**

- rychlá volba (tabulka) a katalog;
- u každého typu: k čemu, kdy ano a kdy ne, úroveň, publikum, nástroj, poctivé „v pluginu“;
- typy:
  - mapa procesů, SIPOC, vývojový diagram, swimlane (výchozí), BPMN 2.0, value stream map;
  - stavový a sekvenční diagram, blokové schéma / C4, tok dat;
  - service blueprint, customer journey;
  - rozhodovací tabulka (DMN), RACI, Ishikawa, event storming;
  - jen zmínka: EPC, ERD, spaghetti diagram, karta procesu ISO 9001.

**`mapping-method.md`:**

- fáze s cílem, vstupy, postupem, otázkami, výstupem a „hotovo, když“;
- rozhovor, workshop, realita vs. ideál, výjimky a předávky, analýza (VA/NVA, plýtvání, 5× proč, kvantifikace četnost × čas, dopad × náročnost);
- časté chyby (včetně vymyšlených kroků při práci z přepisů), kdy animovat.

**`notation.md`:**

- pravidla swimlane, úrovně detailu L0–L3, podmnožina BPMN;
- pojmenování (titulky ve 3. osobě, role je podmět), naše značení, velikost diagramu, přístupnost.
- domácí konvence (12–15 kroků, převod L0–L3 na APQC) jsou označené jako naše doporučení, ne standard.

**`tools.md`:**

- rychlá volba podle situace;
- srovnání: cena s datem ověření, spolupráce, notace, export, ovládání agentem (oficiální a komunitní MCP zvlášť), co klient už má, hosting v EU / offline;
- jak s nástroji pracuje plugin, draw.io a BPMN XML jako další krok, enterprise zmínka.

**`process-spec.md`, `mermaid.md`:** formát popisu a vzory.

**`research.md`:**

- fakta `[F n.m]` s doslovnou citací (do 25 slov), odkazem a datem; doporučení `[D]`; neověřené `[?]`;
- primární zdroje první, blogy výrobců nikdy jako jediný zdroj metodiky;
- ostatní soubory citují ID faktů.

Kotvy pro odkazy jsou explicitní (`<a id="…"></a>`), protože GitHub v kotvách drží diakritiku.

## Research

- Pět témat paralelně: metodika, typy diagramů, notace, nástroje (2026), animované a interaktivní mapy.
- Každé téma má seznam primárních zdrojů a vlastnictví (BPMN v §3, SIPOC v §1).
- Agenti používají jen WebSearch a WebFetch (u ceníků nástrojů smí Playwright), nic nezapisují a nic lokálně nečtou. Výstup jde nejdřív do scratchpadu.
- Ověřovací agent znovu otevře všechny ceny a tvrzení o MCP a aspoň 20 % ostatních, ověří citaci a nepotvrzené přesune do `[?]`. Stavy odkazů se zkontrolují přes `curl -sIL`.

## Testování

- **Unit testy (unittest, Python 3.9 i 3.12):**
  - model (pole, převody, neznámé klíče, chyby);
  - check (odkazy, výčty, id);
  - text, layout (vzor s přesnými hodnotami, vlastnosti rozložení, okrajové případy, zátěžový proces se 32 kroky a 7 rolemi);
  - lint, Mermaid (escapování, id);
  - HTML (úplnost, CSP hashe, escapování včetně `<!--<script>`, bez externích zdrojů, statické SVG);
  - Figma (JSON literál, nepřátelský text, limit);
  - CLI (návratové kódy, výchozí jména, `--link`, složky, figma).
- **Mermaid:** `@mermaid-js/mermaid-cli@12.0.0` nad vzorem, okrajovými případy a `mermaid.md`.
- **Prohlížeč (Playwright, sériově):**
  - animace, krokování, klik ve fullscreenu;
  - tisk (`emulate_media print`), reduced-motion (`emulate_media`), bez JS;
  - vodorovný posun s popisky rolí, statické SVG.
- **Figma:** vzor v testovacím souboru, export videa a snímky.
- **Spouštění skillů:** fráze ze všech čtyř sousedních skillů.
- **Přejímací test:** lokálně, nic se necommituje. Stejný počet rolí, karet, stavů a průběžných rolí jako referenční výkres, stejné sloupce kroků, `check` bez upozornění. Snímky jen ve scratchpadu.

## Mimo rozsah

- Export do draw.io a BPMN XML (jen popis v `tools.md`).
- Automatické rozložení složitého větvení a obcházení karet ve stejném pruhu (řeší `col`, `route`, `next` a Mermaid).
- Diff verzí as-is / to-be a odznaky změn (zatím `id` v detailu a tabulka „Změny oproti as-is“ v dokumentu).
- Přepis generátoru v referenčním projektu.
- Samostatná webová stránka znalostní báze.

## Zavedení

- **Větev:** `agent/process-mapping-plugin`, plugin ve verzi 0.1.0.
- **Ochrana:** lokální git hooky proti klientským datům před prvním tasku.
- **Registrace:** zápis do `marketplace.json` a kořenového README; věta o hranici v popisu `client-discovery` a `user-flow-visualizer`.
- **Commity a push:** commit po každém tasku, push jen na Karlův pokyn.
- **Provádění:** ze session otevřené v `~/dev/datawizard/datawizard-skills`, ne v klientském projektu.

## Závislosti

- Python 3.11+, nebo starší s `tomli`, nebo `uv`.
- Figma: plugin `figma` (Figma MCP), volitelně `ffmpeg`.
- Mermaid ověření: `npx` a síť (jen pro ověření, výstupy síť nepotřebují).
- Prohlížečové ověření: Playwright MCP.
