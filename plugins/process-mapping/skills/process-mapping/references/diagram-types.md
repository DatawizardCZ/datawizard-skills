---
title: Typy diagramů a kdy který
date: 2026-10-01
---

# Typy diagramů a kdy který

Diagram vybírej podle otázky, na kterou má odpovědět, ne podle názvu. Fakta mají ID z [research.md](research.md) (`[F 2.8]`). Věty bez ID jsou naše doporučení.

<a id="rychla-volba"></a>
## Rychlá volba

| Co potřebuju ukázat | Diagram | Plugin vyrobí | Jinak nástroj |
|---|---|---|---|
| Jaké procesy firma má a jak na sebe navazují | Mapa procesů firmy (L0) | ne | Miro, draw.io |
| Hranice procesu: kdo dodává, co vstupuje, co vystupuje, pro koho | SIPOC | šablona v `templates/process-doc.md` | tabulka |
| Pořadí kroků jednoho vlastníka, větvení | Vývojový diagram | Mermaid | Mermaid, draw.io |
| Kdo co dělá a kde se předává práce | Swimlane | HTML, SVG, Figma, Mermaid | draw.io, Miro, Visio |
| Formální model pro IT nebo workflow engine | BPMN 2.0 | ne (jen podmnožina ve swimlane) | bpmn.io, Camunda Modeler, draw.io |
| Kde se ztrácí čas a co nepřidává hodnotu | Value stream map | ne | Miro, papír |
| Jakými stavy prochází doklad nebo objednávka | Stavový diagram | Mermaid a pruh stavů v HTML | Mermaid, PlantUML |
| Kdo s kým komunikuje mezi systémy a v jakém pořadí | Sekvenční diagram | ne (ruční vzor v `mermaid.md`) | Mermaid, PlantUML |
| Jaké systémy existují a jak spolu souvisí | Blokové schéma / C4 | ne | Structurizr, draw.io |
| Kudy tečou data mezi procesy a úložišti | Diagram toku dat | ne | draw.io |
| Co se děje uvnitř firmy kolem cesty zákazníka | Service blueprint | ne | Miro, Figma |
| Jak službu zažívá zákazník | Customer journey map | ne | Miro, Figma |
| Jaké pravidlo rozhoduje a podle čeho | Rozhodovací tabulka (DMN) | šablona v `templates/process-doc.md` | tabulka, Camunda Modeler |
| Kdo za co odpovídá | RACI matice | šablona v `templates/process-doc.md` | tabulka |
| Proč vzniká konkrétní problém | Ishikawa | ne | Miro, papír |
| Společné poznání domény na workshopu | Event storming | ne | Miro, papír a lístky |

Když si nejsi jistý, začni swimlanem. Pokrývá většinu firemních procesů a plugin ho vyrobí ve všech výstupech.

<a id="katalog"></a>
## Katalog

### Mapa procesů firmy (L0)

- **K čemu:** přehled všech procesů firmy na jedné stránce. Procesy se běžně dělí na řídicí, hlavní a podpůrné; hlavní tvoří hodnotu pro zákazníka a jsou páteří mapy [F 2.1]. Mapa má ukázat návaznost hlavních procesů [F 2.3].
- **Kdy ano:** doporučujeme na začátku spolupráce, při výběru prvního procesu k mapování a jako vstup k ISO 9001.
- **Kdy ne:** když řešíme průběh jednoho procesu. Na to je swimlane.
- **Úroveň detailu:** L0. Odpovídá první úrovni APQC PCF (kategorie) [F 1.1].
- **Publikum:** vedení a vlastníci procesů.
- **Nástroj:** jednotná notace pro mapu procesů neexistuje [F 2.2]. Doporučujeme pár tvarů a stejný vizuální slovník napříč mapami. Procesy zajišťované externě odliš [F 2.3].
- **V pluginu:** ne.
- **Zdroj:** F 1.1, F 2.1, F 2.2, F 2.3.

### SIPOC

- **K čemu:** vymezí hranice procesu a dá týmu společné porozumění. Sloupce Suppliers, Inputs, Process, Outputs, Customers; sloupec Process má 5 až 7 kroků [F 1.3].
- **Kdy ano:** na začátku zlepšovacího projektu, k vymezení rozsahu a jako podklad pro detailnější mapy [F 1.4]. V DMAIC patří do fáze Define [F 1.5].
- **Kdy ne:** když potřebujeme vidět role a předávky. SIPOC je tabulka, ne tok.
- **Úroveň detailu:** L1, celý proces od začátku do konce.
- **Publikum:** vlastník procesu, sponzor, tým.
- **Nástroj:** tabulka. Vyplňuj v pořadí proces, výstupy, zákazníci, vstupy, dodavatelé [F 1.5].
- **V pluginu:** šablona v `templates/process-doc.md`.
- **Zdroj:** F 1.3, F 1.4, F 1.5.

### Vývojový diagram (alias UML activity)

- **K čemu:** pořadí kroků a větvení. Přehledový vývojový diagram má 6 až 12 kroků [F 2.8], detailní desítky kroků [F 2.9]. Rozhodovací kosočtverec obvykle představuje otázku ano/ne [F 3.18]. Diagram aktivit UML ukazuje tok řízení nebo tok objektů a jeho oddíly mají podobu drah [F 2.15].
- **Kdy ano:** přehled procesu v rané fázi projektu [F 2.8]. Detail až po nalezení problému nebo při změně procesu [F 2.9]. Doporučujeme ho pro proces s jedním vlastníkem a složitým větvením.
- **Kdy ne:** neukazuje, kde vzniká hodnota, a vyžaduje hlubokou znalost procesu [F 2.10]. Když jde o víc rolí, použij swimlane.
- **Úroveň detailu:** L1 (přehled) nebo L3 (detail).
- **Publikum:** tým procesu; UML activity pro technické publikum. UML lze podle OMG použít i pro byznysové modelování [F 2.14].
- **Nástroj:** Mermaid, draw.io. Tvary podle ISO 5807 znej jen jako zvyk; norma je placená a detailní znění symbolů máme jen ze sekundárního zdroje [F 3.19] [F 3.20].
- **V pluginu:** Mermaid. Složité větvení zapiš přes `auto_flow = false` a `[[flow]]`.
- **Zdroj:** F 2.8, F 2.9, F 2.10, F 2.14, F 2.15, F 3.18, F 3.19, F 3.20.

### Swimlane

- **K čemu:** vývojový diagram rozdělený do drah podle odpovědnosti. Ukáže předávky a čekání mezi odděleními [F 2.12]. Technika pochází ze 40. let a název jí dali Rummler a Brache v roce 1990 [F 2.11]. Pruh určuje, kdo kroky vykonává [F 3.13]. Dráhy mohou být vodorovné i svislé [F 3.15].
- **Kdy ano:** doporučujeme jako výchozí typ pro každý proces s víc než jednou rolí nebo systémem.
- **Kdy ne:** když nás zajímá čas a plýtvání s daty (value stream map) nebo jen stavy objektu (stavový diagram). Výrobce BPMN nástroje Camunda je u většiny modelů nedoporučuje kvůli pracnosti údržby [F 3.17].
- **Úroveň detailu:** L2 (aktivity s rolemi).
- **Publikum:** lidé v procesu, vlastník procesu, analytik, vývoj.
- **Nástroj:** draw.io, Miro, Visio, Figma.
- **V pluginu:** HTML, SVG, Figma a Mermaid. Lineární tok, rozhodnutí o dvou výstupech, smyčky. Pravidla v [notation.md](notation.md#swimlane).
- **Zdroj:** F 2.11, F 2.12, F 3.13, F 3.15, F 3.17.

### BPMN 2.0

- **K čemu:** standard OMG pro procesní modely. Aktuální verze je 2.0.2 a OMG ji popisuje jako notaci podobnou vývojovému diagramu, nezávislou na prováděcím prostředí [F 3.1]. Podtřída Descriptive pokrývá viditelné prvky pro modelování na vysoké úrovni [F 3.2]. Paleta Level 1 z BPMN Method & Style odpovídá podtřídě Descriptive [F 3.5] a obsahuje úlohy, podprocesy, brány, počáteční a koncové události, toky, pooly, pruhy a datové objekty [F 3.6].
- **Kdy ano:** když model pokračuje do IT nebo workflow enginu, nebo když ho klient chce ve standardní notaci. Diagram má mít jen jeden výklad [F 3.7].
- **Kdy ne:** doporučujeme ho nevnucovat lidem z provozu. Na validaci s nimi stačí swimlane.
- **Úroveň detailu:** L2 až L3.
- **Publikum:** analytici, IT, vývoj.
- **Nástroj:** bpmn.io, Camunda Modeler, draw.io.
- **V pluginu:** ne. Swimlane z pluginu používá podmnožinu prvků (start, úloha, rozhodnutí, smyčka, alternativa), viz [notation.md](notation.md#bpmn).
- **Zdroj:** F 3.1, F 3.2, F 3.5, F 3.6, F 3.7.

### Value stream map

- **K čemu:** tok materiálu a informací od objednávky po dodání [F 1.6]. U každého kroku čas zpracování, čekání a podíl práce bez vad (%C/A) [F 1.8]. Čas, který tvoří hodnotu, je kratší než cycle time a ten je kratší než lead time [F 1.7].
- **Kdy ano:** když je cílem zkrátit průběžnou dobu a máme data o časech. Začíná se mapou současného stavu na úrovni „door-to-door“, pak cílový stav [F 1.6].
- **Kdy ne:** bez dat o časech. V administrativě často nejde oddělit tok materiálu od toku informací, protože informace putuje s dokumentem [F 1.9]; doporučujeme pak swimlane s časy u kroků.
- **Úroveň detailu:** L1 až L2.
- **Publikum:** vlastník procesu, tým zlepšování.
- **Nástroj:** papír a lístky, Miro.
- **V pluginu:** ne. Časy a čekání zapiš do `time` u kroků swimlanu.
- **Zdroj:** F 1.6, F 1.7, F 1.8, F 1.9.

### Stavový diagram

- **K čemu:** chování části systému jako přechody mezi konečným počtem stavů [F 2.16]. Typicky životní cyklus dokladu, objednávky nebo požadavku.
- **Kdy ano:** když se proces točí kolem jednoho objektu a jeho stavů. C4 výslovně doporučuje doplnit architekturu stavovými diagramy UML [F 2.22].
- **Kdy ne:** neukazuje, kdo co dělá. Na to je swimlane.
- **Úroveň detailu:** L2 až L3.
- **Publikum:** analytici, vývoj, vlastník procesu.
- **Nástroj:** Mermaid, PlantUML.
- **V pluginu:** Mermaid a pruh stavů v HTML výkresu (jen lineární sled stavů).
- **Zdroj:** F 2.16, F 2.22.

### Sekvenční diagram

- **K čemu:** pořadí zpráv mezi účastníky (lifelines) [F 2.17]. Typicky komunikace mezi systémy, API a integrace.
- **Kdy ano:** zadání integrace, předání vývoji.
- **Kdy ne:** pro byznysový proces s lidmi. C4 radí dynamické diagramy kreslit jen výjimečně [F 2.22].
- **Úroveň detailu:** L3.
- **Publikum:** vývoj, architekti.
- **Nástroj:** Mermaid, PlantUML.
- **V pluginu:** ne. Ruční vzor v [mermaid.md](mermaid.md).
- **Zdroj:** F 2.17, F 2.22.

### Blokové schéma / C4

- **K čemu:** statická struktura softwaru. Kontextový diagram ukazuje jeden systém v okolí lidí a jiných systémů a je určený všem [F 2.18]. Diagram kontejnerů ukazuje aplikace a datová úložiště pro technické publikum [F 2.19]. Diagram krajiny systémů pokrývá celou firmu [F 2.23].
- **Kdy ano:** když potřebujeme ukázat, jaké systémy proces používá. Většině týmů stačí kontext a kontejnery [F 2.20].
- **Kdy ne:** pro průběh procesu. C4 popisuje strukturu, ne procesy, a méně se hodí pro silně customizovaný krabicový software [F 2.21].
- **Úroveň detailu:** krajina systémů, kontext, kontejnery.
- **Publikum:** kontext všichni [F 2.18]; kontejnery technické publikum [F 2.19].
- **Nástroj:** Structurizr, draw.io.
- **V pluginu:** ne.
- **Zdroj:** F 2.18, F 2.19, F 2.20, F 2.21, F 2.22, F 2.23.

### Diagram toku dat

- **K čemu:** tok dat mezi procesy, úložišti a externími entitami. Nemá tok řízení, rozhodnutí ani smyčky [F 2.24].
- **Kdy ano:** bezpečnostní nebo GDPR pohled. OWASP ho používá při modelování hrozeb a přidává hranici důvěry [F 2.25].
- **Kdy ne:** pro pořadí kroků a rozhodnutí, to DFD neumí [F 2.24].
- **Úroveň detailu:** hierarchicky po úrovních [F 2.25].
- **Publikum:** analytici, bezpečnost, IT.
- **Nástroj:** draw.io.
- **V pluginu:** ne.
- **Zdroj:** F 2.24, F 2.25.

### Service blueprint

- **K čemu:** co se kolem cesty zákazníka děje uvnitř firmy. Navazuje na customer journey map [F 2.26]. Linie interakce, viditelnosti a vnitřní interakce dělí činnosti na vrstvy [F 2.27].
- **Kdy ano:** služby napříč kanály a odděleními [F 2.26], po journey mappingu a před organizační nebo procesní změnou [F 2.28].
- **Kdy ne:** velšská vládní metodika ho nedoporučuje pro nové služby ani jako nástroj na nápady [F 2.28].
- **Úroveň detailu:** L2.
- **Publikum:** vlastníci služby, design, provoz.
- **Nástroj:** Miro, Figma.
- **V pluginu:** ne. Blízko má swimlane s pruhem zákazníka nahoře.
- **Zdroj:** F 2.26, F 2.27, F 2.28.

### Customer journey map

- **K čemu:** cesta člověka k cíli. Má aktéra, scénář s očekáváními, fáze, akce s myšlenkami a emocemi a příležitosti [F 2.29].
- **Kdy ano:** když nás zajímá zážitek zákazníka. Je psaná z pohledu uživatele a procesní detaily vynechává [F 2.30].
- **Kdy ne:** pro vnitřní průběh procesu. Na to je blueprint nebo swimlane [F 2.30].
- **Úroveň detailu:** L1.
- **Publikum:** vedení, marketing, design.
- **Nástroj:** Miro, Figma.
- **V pluginu:** ne.
- **Zdroj:** F 2.29, F 2.30.

### Rozhodovací tabulka (DMN)

- **K čemu:** přesný popis byznysových rozhodnutí a pravidel. DMN je standard OMG navržený pro souběžné použití s BPMN [F 2.31]. Grafická část ukazuje závislosti mezi rozhodnutími, výrazová část obsahuje rozhodovací tabulky [F 2.32].
- **Kdy ano:** když pravidlo závisí na víc podmínkách. Doporučujeme pravidlo vyčlenit do tabulky a z kroku na ni jen odkázat, místo kreslit strom rozhodnutí.
- **Kdy ne:** pro jedno rozhodnutí ano/ne. To stačí jako rozhodovací karta ve swimlanu.
- **Úroveň detailu:** L3.
- **Publikum:** vlastník pravidla, analytik, vývoj.
- **Nástroj:** tabulka v dokumentu, Camunda Modeler pro DMN.
- **V pluginu:** šablona rozhodovací tabulky v `templates/process-doc.md`.
- **Zdroj:** F 2.31, F 2.32.

### RACI matice

- **K čemu:** přiřazuje úkolům role Responsible, Accountable, Consulted, Informed. Používá se hlavně tam, kde se práce dělí mezi oddělení [F 2.33].
- **Kdy ano:** když se nejasnosti týkají odpovědnosti, ne pořadí kroků. Každý řádek má právě jedno A [F 2.34].
- **Kdy ne:** neukazuje tok. Doporučujeme ji jako doplněk ke swimlanu.
- **Úroveň detailu:** L1 až L2.
- **Publikum:** vedení, vlastník procesu.
- **Nástroj:** tabulka.
- **V pluginu:** šablona RACI v `templates/process-doc.md`.
- **Zdroj:** F 2.33, F 2.34.

### Ishikawa

- **K čemu:** hledání možných příčin jednoho problému. Klasická rybí kost třídí příčiny do kategorií, procesní varianta je řadí ke krokům procesu [F 2.35].
- **Kdy ano:** v analýze, když známe problém a hledáme příčinu. Kombinuj s 5× proč, kde se ptá, dokud se nedojde k příčině [F 1.24].
- **Kdy ne:** k popisu průběhu procesu.
- **Úroveň detailu:** jeden problém.
- **Publikum:** tým zlepšování.
- **Nástroj:** papír, Miro.
- **V pluginu:** ne. Výsledek zapiš do tabulky problémů v `templates/process-doc.md`.
- **Zdroj:** F 2.35, F 1.24.

### Event storming

- **K čemu:** workshop, ne notace. Slouží ke společnému poznání složité domény [F 2.36]. Kniha popisuje tři formáty (Big Picture, Process Modeling, Design-Level) a jako pomůcky stačí papírová role a lepicí lístky [F 2.37].
- **Kdy ano:** doporučujeme jako vstup na začátku sběru, když doménu nikdo nezná celou.
- **Kdy ne:** jako finální diagram. Výstup převeď do swimlanu nebo stavového diagramu.
- **Úroveň detailu:** od přehledu po detail podle formátu [F 2.37].
- **Publikum:** lidé z provozu i z IT společně.
- **Nástroj:** papír a lístky, Miro.
- **V pluginu:** ne.
- **Zdroj:** F 2.36, F 2.37.

## Jen pro úplnost

EPC je notace metody ARIS z roku 1992 [F 2.38]. Musí začínat i končit událostí [F 2.39] a její sémantika je nelokální; netriviální paralelní struktury nemají jasně definované provádění [F 2.40]; doporučujeme ji jen číst nebo převádět starší modely. Karta procesu je česká praxe kolem ISO 9001: jednostránkový popis s deseti poli jako alternativa k želvímu diagramu [F 2.5], pole odvozená z kapitoly 4.4.1 normy [F 2.4]. Nová ISO 9001:2026 má přechodné období do září 2029 [F 2.7], před použitím karty proto zkontroluj číslování kapitol. Náš rámec procesu v `templates/process-doc.md` kartě odpovídá. ERD, spaghetti diagram a CMMN (DMN s ním počítá vedle BPMN [F 2.31]) plugin nepokrývá; doporučujeme je kreslit v nástroji, který používá tým.
