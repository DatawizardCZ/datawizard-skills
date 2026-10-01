---
title: Notace a konvence procesních map
date: 2026-10-01
---

# Notace a konvence procesních map

Pravidla pro kreslení a pojmenování. Fakta mají ID z [research.md](research.md) (`[F 3.8]`). Věty bez ID jsou naše doporučení a konvence pluginu.

<a id="swimlane"></a>
## Swimlane

1. **Pruh je role nebo systém, který kroky vykonává** [F 3.13]. Role a oddělení jedné organizace patří do pruhů jednoho celku, ne do samostatných poolů [F 3.13]. Doporučujeme pruh pojmenovat rolí („Účetní“), ne jménem člověka.
2. **Krok je sloveso + předmět** [F 3.8]. Česky doporučujeme 3. osobu („Kontroluje fakturu“), protože podmětem je role pruhu. Rozkazovací tvar („Zkontroluj fakturu“) je taky v pořádku; v jedné mapě tvary nemíchej.
3. **Jedna karta je jedna činnost.** Když titulek potřebuje „a“, doporučujeme kartu rozdělit.
4. **Rozhodnutí je otázka s popsanými výstupy.** Bránu označ otázkou a výstupy odpověďmi [F 3.12]; při dvou výstupech stačí „ano“ a „ne“ [F 3.10].
5. **Tok jde zleva doprava.** U vývojových diagramů je standardní směr shora dolů a zleva doprava [F 3.16]. Pruhy mohou být vodorovné i svislé [F 3.15]; plugin kreslí vodorovné.
6. **Předávka je šipka mezi pruhy.** Právě na předávkách se v swimlanu hledá čekání [F 2.12].
7. **Nejdřív nejčastější průběh, výjimky potom.** Výjimky se sbírají, seřadí a přidávají postupně [F 1.18]. V mapě je kresli jako alternativu (šedá čárkovaná) nebo smyčku (oranžová čárkovaná).
8. **Kontrolní karta (`checks`) odpovídá paralelnímu rozdělení a sloučení,** tedy bráně AND v BPMN. Výstupy brány AND se nepopisují [F 3.10].
9. **Víc konců pojmenuj koncovým stavem.** Každá koncová událost nese název stavu, jediná se nepojmenovává [F 3.9].
10. **Diagram má mít jen jeden výklad** a logika má jít přečíst ze samotného diagramu [F 3.7]. Co se do karty nevejde, patří do detailu, ne mimo mapu.

Pravidla 3 a 6 jsou naše konvence. Někteří výrobci BPMN nástrojů pruhy u většiny modelů nedoporučují kvůli údržbě [F 3.17]; pro mapování s lidmi z provozu je přesto doporučujeme, protože předávky jsou to první, na co se ptají.

<a id="urovne-detailu"></a>
## Úrovně detailu

APQC PCF má pět úrovní: kategorie, skupina procesů, proces, aktivita, úkol [F 1.1]. Na úrovni aktivit se rámec nejvíc upravuje, protože tam začíná popis toho, jak to dělá konkrétní firma [F 1.2]. Převod na naše L0 až L3 je naše konvence; standard pro něj neexistuje.

| Úroveň | Název | Co ukazuje | Příklad | APQC (doporučujeme) |
|---|---|---|---|---|
| L0 | Mapa procesů | všechny procesy firmy, řídicí, hlavní a podpůrné [F 2.1] | prodej, nákup, výroba, účetnictví | úroveň 1 (kategorie) |
| L1 | Proces od začátku do konce | 5 až 7 kroků v SIPOC [F 1.3], přehled 6 až 12 kroků [F 2.8] | od objednávky po zaplacení | úrovně 2 a 3 |
| L2 | Tok aktivit s rolemi | swimlane: kdo co dělá a kde se předává | schválení faktury | úroveň 4 |
| L3 | Úkoly a postup | kroky v systému, pole, pravidla, výjimky | zaúčtování faktury v systému | úroveň 5 |

Úroveň vybírej podle účelu: přehled pro vedení L1, zlepšení L2, zadání pro vývoj L3. Plugin kreslí L1 až L3; L0 nakresli zvlášť (viz [diagram-types.md](diagram-types.md#katalog)).

<a id="bpmn"></a>
## BPMN podmnožina

BPMN 2.0.2 je aktuální verze standardu OMG [F 3.1]. Pro běžnou práci stačí podtřída Descriptive, tedy viditelné prvky pro modelování na vysoké úrovni [F 3.2]. Odpovídá jí paleta Level 1 z BPMN Method & Style [F 3.5] [F 3.6]. Podtřída Analytic přidává hlavně mezilehlé události a event gateway [F 3.4]; doporučujeme ji jen na vyžádání IT.

Výčet prvků je ověřený [F 3.6], popis tvarů ne: tvary jsou standardní kresba BPMN, jak ji znají běžné nástroje.

| Prvek | Tvar | Kdy | V pluginu |
|---|---|---|---|
| Počáteční událost | tenký kruh | čím proces začíná | `type = "start"` |
| Koncová událost | tlustý kruh | čím proces končí, u víc konců s názvem stavu [F 3.9] | `type = "end"` |
| Úloha | obdélník se zaoblenými rohy | jedna činnost jedné role | `type = "task"` (výchozí) |
| Podproces | úloha se znakem plus | skupina kroků s vlastním diagramem [F 3.23] | samostatný spec |
| Brána XOR | kosočtverec (s křížkem) | jeden z výstupů podle podmínky, otázka [F 3.12] | `type = "decision"` + `main` a `alt` |
| Brána AND | kosočtverec s plusem | paralelní větve a jejich sloučení | `type = "checks"` |
| Sekvenční tok | plná šipka | pořadí kroků uvnitř procesu | automaticky, `[[flow]]` |
| Zprávový tok | čárkovaná šipka s kroužkem | zpráva mezi organizacemi | ne |
| Pool | velký obdélník | jedna organizace nebo účastník | ne (jedna mapa = jeden pool) |
| Lane | pruh v poolu | role nebo systém [F 3.13] | `[[lane]]` |
| Datový objekt | list s ohnutým rohem | dokument nebo data, která krok vytváří | `out`, `tools` |

Formální BPMN XML plugin nevyrábí. Pro IT a workflow engine použij nástroj z [tools.md](tools.md#rychla-volba).

## Pojmenování

- **Kroky:** sloveso + předmět [F 3.8]. Titulek se vejde na 17 znaků × 2 řádky; co se nevejde, patří do `sub` nebo `detail`.
- **Rozhodnutí:** otázka („Je nad limit?“), výstupy jako odpovědi [F 3.10] [F 3.12].
- **Koncové stavy:** podstatné a přídavné jméno („Faktura zaplacená“), jen když je konců víc [F 3.9]. Podproces s víc konci následuje brána se stejnými názvy větví [F 3.11].
- **Pruhy:** role nebo systém, ne jméno člověka.
- **Stavy objektu:** příčestí nebo podstatné jméno („Přijatá“, „Ke schválení“) ve stejném tvaru pro všechny stavy.
- **Otázky:** konkrétní a s tím, kdo odpoví (`who`).

<a id="nase-znaceni"></a>
## Naše značení

| Značka | Význam | Kde |
|---|---|---|
| `??` | otevřená otázka, odpověď zatím nemáme | HTML, Mermaid, dokument procesu |
| oranžová čárkovaná šipka s ↺ | smyčka, návrat k dřívějšímu kroku | HTML, SVG, Figma |
| šedá čárkovaná šipka | alternativa, vedlejší větev | HTML, SVG, Figma |
| zvýrazněný rámeček karty | rozhodnutí | HTML, SVG; ve Figmě jantarová barva |
| kontrolní karta s dlaždicemi | několik souběžných kontrol (AND) | HTML, SVG, Figma |
| jemný rámeček přes víc sloupců (ve Figmě čárkovaný) | průběžná role (`[[span]]`) | HTML, SVG, Figma |
| pruh stavů pod pruhy rolí | stavy objektu, rozsvěcují se s kroky | HTML, SVG, Figma |
| barva pruhu ve Figmě | rozlišení rolí, šest barev dokola | Figma |

Barva nikdy není jediný nositel významu: smyčka má navíc čárkování a symbol ↺, rozhodnutí tvar otázky a popsané výstupy (viz Přístupnost).

## Velikost diagramu

- **Naše konvence:** do 15 kroků na mapu. Víc rozděl na podprocesy, každý ve vlastním specu, a nad ně přehledovou mapu L1. `check` velikost nehlídá, hlídáš ji ty.
- **7PMG:** rozdělit model nad 50 prvků [F 3.21]. Práh se mezi zdroji liší (50 nebo 30), původní článek jsme nepřečetli.
- **BPMN Method & Style:** nejvýš 10 aktivit na jednu úroveň procesu, aby se vešla na jednu tištěnou stranu [F 3.22].
- **Signavio:** nejvýš formát A3 [F 3.24].
- **Jak dělit:** podproces se v nadřazeném diagramu ukáže sbalený a v podřízeném rozbalený [F 3.23]. Čím větší model, tím hůř se mu rozumí a tím víc má chyb [F 1.21].

## Přístupnost

- **Barva nesmí být jediný nositel informace** (WCAG 2.2, SC 1.4.1) [F 3.25]. Lidé se slabozrakostí a starší lidé barvy často rozlišují špatně [F 3.26].
- **Kontrast textu** aspoň 4.5:1, u velkého textu 3:1; platí i pro text uvnitř grafiky [F 3.27].
- **Kontrast čar a značek** aspoň 3:1 vůči pozadí [F 3.28].
- **Pohyb:** respektuj `prefers-reduced-motion` [F 5.30] a nech animaci zastavit [F 5.28]. HTML výkres pluginu má tlačítko „Přeskočit animaci“ a při omezeném pohybu ukáže hotový stav bez animace. Víc v [mapping-method.md](mapping-method.md#kdy-animovat).
- **Barvy v BPMN XML:** pro výměnu barev mezi nástroji existuje rozšíření BPMN in Color [F 3.29].
