---
title: Nástroje na procesní mapy (stav 2026)
date: 2026-10-01
---

# Nástroje na procesní mapy (stav 2026)

Kdy který nástroj a co umí. Ceny, exporty a MCP servery jsou ověřené 2026-10-01 na oficiálních stránkách a mají ID z [research.md](research.md) (`[F 4.1]`). Ceny se mění, před nabídkou klientovi je ověř znovu. Věty bez ID jsou naše doporučení.

<a id="rychla-volba"></a>
## Rychlá volba

| Situace | Nástroj | Proč |
|---|---|---|
| Klient chce mapu upravovat sám | draw.io | zdarma a bez registrace [F 4.19], v Confluence Cloud zdarma do 10 uživatelů [F 4.24] |
| Klient chce upravovat na sdílené tabuli | Miro | od plánu Starter upraví board i návštěvník bez přihlášení [F 4.11] |
| Prezentace pro vedení, krokování na schůzce | HTML výkres z pluginu | animace, krokování, detail kroku, tisk; offline soubor |
| Obrázek do prezentace nebo dokumentu | SVG z pluginu | `pmap.py svg` |
| Dokumentace v repu | Mermaid z pluginu | GitHub vykresluje Mermaid nativně [F 4.46] |
| Formální BPMN pro IT nebo workflow engine | Camunda Desktop Modeler, bpmn.io | zdarma, offline, přímá práce s XML [F 4.34] [F 4.32] |
| Workshop na dálku | Miro, FigJam | Miro Free má 3 boardy [F 4.5]; FigJam pokrývá Collab seat za 3 € [F 4.1] |
| Klient má jen Microsoft 365 | draw.io v SharePointu, OneDrivu nebo Teams | Visio v M365 neumí swimlane ani BPMN [F 4.28]; draw.io se do M365 integruje [F 4.19] |
| Klient trvá na Visiu | Visio Plan 1 (swimlane) nebo Plan 2 (BPMN) | 5 USD a 15 USD za uživatele a měsíc při roční platbě [F 4.26] [F 4.28] [F 4.29] |
| Klient chce soubor VSDX | Lucidchart (placený plán) | export do Visia jen na placených plánech [F 4.14] |
| Offline nebo on-prem | draw.io Desktop nebo Docker, Camunda Desktop Modeler, HTML z pluginu | draw.io Desktop je izolovaný od internetu [F 4.20]; Camunda Modeler pracuje offline [F 4.34] |
| Data musí zůstat v EU | Miro, Camunda SaaS | Miro má EU jako výchozí region pro všechny plány [F 4.10]; Camunda hostuje Modeler v EU [F 4.36] |
| Klient a designéři pracují ve Figmě | Figma přes skill `process-map-figma` | zápis agentem potřebuje Full seat, Dev seat zapisuje jen do draftů [F 4.3] |
| Zadání pro vývoj | HTML z pluginu, Mermaid, `templates/process-doc.md` | sekvenční diagramy v Mermaidu nebo PlantUML |
| Architektura systémů (C4) | Structurizr | nástroj pro model C4 s oficiálním MCP [F 4.57] |

<a id="srovnani"></a>
## Srovnání

Ceny jsou za editora (uživatele, člena) a měsíc při ročním placení, pokud není uvedeno jinak. Sloupce „Spolupráce“ a „Klient upraví“ a buňky bez ID jsou naše zkušenost, ne research. Otazník znamená, že research údaj neověřil.

| Nástroj | K čemu | Cena (ověřeno 2026-10-01) | Spolupráce | Notace | Export | Agent (MCP / API / text) | Klient upraví | EU / offline |
|---|---|---|---|---|---|---|---|---|
| Figma a FigJam | design, prezentace; FigJam na workshopy | Professional 16 € (Full seat), 3 € (Collab seat, pokrývá FigJam) [F 4.1] | v reálném čase | FigJam z Mermaidu: flowchart, state, sequence, ERD a další [F 4.2]; BPMN ? | FigJam PNG, JPG, PDF, CSV, ne SVG [F 4.4] | oficiální MCP [F 4.2]; zápis Full seat, Dev seat jen do draftů [F 4.3] | ano, s účtem | ? |
| Miro | workshop, discovery | Starter 8 €, Business 20 €; Free 3 boardy [F 4.5] | v reálném čase | BPMN, UML, Mermaid tvary od Business [F 4.6] | JPG, PDF, SVG, CSV; Free jen nízké rozlišení [F 4.7] | oficiální MCP na všech plánech [F 4.8]; komunitní [F 4.9] | ano, návštěvník bez přihlášení od Starter [F 4.11] | EU výchozí pro všechny plány [F 4.10] |
| Lucidchart | diagramy ve firmě, výměna s Visiem | Individual 9 USD, Team 10 USD, bez DPH; Free 3 dokumenty [F 4.12] | v reálném čase | BPMN 2.0 [F 4.13] | PDF, PNG, JPEG, SVG, BPMN 2.0 [F 4.13]; VSDX jen placené [F 4.14] | oficiální MCP, v Team a Enterprise ho zapíná admin [F 4.16] | ano, s účtem | EU region jen Enterprise [F 4.17] |
| draw.io (diagrams.net) | editovatelná mapa pro klienta | zdarma, Apache 2.0 [F 4.19]; Confluence Cloud zdarma do 10 uživatelů [F 4.24] | podle úložiště | BPMN 2.0 tvary s pooly a lanes, bez BPMN XML [F 4.21] | PNG, SVG, JPEG, GIF, PDF, HTML, XML; ne VSDX, ne BPMN XML [F 4.22] | oficiální MCP: hostovaný bere jen XML, lokální `@drawio/mcp` i CSV a Mermaid [F 4.23] | ano, bez registrace | Desktop offline, Docker image [F 4.20] |
| Microsoft Visio | firmy s Microsoftem | web v komerčních M365 plánech [F 4.26] [F 4.27]; Plan 1 5 USD, Plan 2 15 USD [F 4.26] | v M365 | web bez swimlane a BPMN; swimlane od Plan 1, BPMN v Plan 2 [F 4.28] [F 4.29] | web PDF, JPEG, PNG; desktop i SVG [F 4.30] | jen komunitní MCP, potřebuje desktopové Visio Professional [F 4.31] | ano, s licencí | ? |
| bpmn.io a Camunda Modeler | formální BPMN a DMN | bpmn.io zdarma s povinným vodoznakem [F 4.33]; Desktop Modeler zdarma, MIT [F 4.34]; SaaS po zkušební době zdarma jen modelování [F 4.35] | Web Modeler v SaaS | BPMN 2.0, DMN [F 4.32] [F 4.34] | BPMN XML [F 4.32] [F 4.34] | MCP Camundy slouží běhu procesů, ne modelování; BPMN Copilot v alfě [F 4.37]; komunitní MCP [F 4.38] | spíš ne, je to nástroj pro analytiky | Desktop offline [F 4.34]; SaaS Modeler v EU [F 4.36] |
| Bizagi Modeler | BPMN na Windows | desktop zdarma (freeware) [F 4.39]; cloud placený [F 4.42] | cloud za poplatek [F 4.42] | BPMN [F 4.41] | BPMN, XPDL, Visio [F 4.41] | ? | spíš ne | desktop jen Windows [F 4.40] |
| SAP Signavio | podnikové řízení procesů | cena neveřejná [F 4.43] | ano | BPMN 2.0 [F 4.43] | ? | AI generuje diagram z textu [F 4.43]; MCP ? | ne | ? |
| Mermaid | diagram jako text v repu | knihovna zdarma, MIT [F 4.44]; Mermaid Chart Plus 10 USD, Premium 20 USD [F 4.47] | přes Git | flowchart, state, sequence; swimlane jen beta [F 4.45]; BPMN ne [F 4.44] | SVG a PNG přes render | oficiální MCP [F 4.48]; text | ano, když zná Markdown | knihovna offline |
| PlantUML | UML jako text | open source [F 4.49] | přes Git | UML, swimlane v diagramu aktivit [F 4.50] | PNG, SVG, LaTeX, EPS, ASCII [F 4.49] | oficiální lokální MCP [F 4.51]; text | spíš ne | lokálně [F 4.51] |
| D2 | diagramy jako text | MPL-2.0 [F 4.52] | přes Git | obecné diagramy | SVG, PNG, PDF, PPTX, GIF, ASCII [F 4.52] | text; oficiální MCP ? | spíš ne | lokálně |
| Excalidraw | rychlé skici | open source, MIT [F 4.53]; Plus 6 USD [F 4.54] | šifrovaná v reálném čase [F 4.53] | volné kreslení | PNG, SVG, JSON [F 4.53] | oficiální MCP App [F 4.55] | ano | offline jako PWA [F 4.53] |
| Structurizr | architektura C4 | za instalaci: 300 GBP měsíčně pro 1 až 20 uživatelů, asi 15 GBP na uživatele [F 4.56] | podle instalace | C4 | PlantUML, Mermaid přes MCP [F 4.57] | oficiální MCP zdarma [F 4.57] | ne | vlastní instalace [F 4.56] |
| Whimsical | rychlé flowcharty | Pro 10 USD, Business 20 USD; Free 50 objektů měsíčně, vodoznak [F 4.58] | v reálném čase | flowchart, sekvenční [F 4.59] | PNG, PDF, SVG, kopie jako Mermaid [F 4.59] | oficiální MCP [F 4.60] | ano | ? |
| HTML výkres (tento plugin) | prezentace, krokování, validace, předání | zdarma | soubor posíláš | swimlane s podmnožinou BPMN ([notation.md](notation.md#bpmn)) | HTML, SVG, Mermaid, Figma | `pmap.py`, text (`*.process.toml`) | ne přímo; změna jde do specu | offline, jeden soubor |

<a id="jak-s-nimi-pracuje-plugin"></a>
## Jak s nimi pracuje plugin

- **HTML, SVG a Mermaid** vyrábí `pmap.py` z jednoho specu (`html`, `svg`, `mermaid`). Popis je ve skillu `process-map-html` a v [mermaid.md](mermaid.md).
- **Figma:** skill `process-map-figma` postaví swimlane s animací a statickou zálohou. Zápis přes MCP potřebuje Full seat na placeném plánu; Dev seat zapisuje jen do draftů [F 4.3].
- **Diagram ve FigJamu:** Figma MCP má nástroj `generate_diagram`, který udělá diagram z Mermaidu [F 4.2]. Zkus mu dát Mermaid výstup pluginu. Neověřeno, ověř před použitím.
- **Editovatelný diagram v draw.io:** lokální MCP Tool Server draw.io (npm `@drawio/mcp`) bere Mermaid, hostovaný server jen XML [F 4.23]. draw.io umí Mermaid diagramy upravovat [F 4.25]. I tady zkus Mermaid výstup pluginu; neověřeno.

<a id="drawio-a-bpmn-xml"></a>
## draw.io a BPMN XML

Plugin zatím nevyrábí ani soubor `.drawio`, ani BPMN XML. To je další krok. Pozor, draw.io má tvary BPMN 2.0, ale dokumentace nezmiňuje import ani export BPMN XML [F 4.21] [F 4.22]. Když klient potřebuje BPMN XML, model překresli v Camunda Modeleru nebo bpmn.io [F 4.34] [F 4.32]; Lucidchart umí BPMN 2.0 exportovat i importovat [F 4.13] [F 4.15].

<a id="enterprise"></a>
## Enterprise

- **SAP Signavio:** podnikový modelář s BPMN 2.0 a generováním diagramu z textu, cenu nezveřejňuje [F 4.43]. Když ho klient má, doporučujeme předávat mapu tak, aby šla překreslit do BPMN.
- **ARIS:** podniková platforma postavená kolem metody ARIS a notace EPC [F 2.38]. Cenu jsme neověřili; doporučujeme stejný postup jako u Signavia.
