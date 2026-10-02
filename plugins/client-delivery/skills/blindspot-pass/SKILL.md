---
name: blindspot-pass
description: Udělá blindspot pass nad zadáním, specifikací nebo složkou podkladů — najde unknown unknowns (věci, na které by zadavatel sám nepomyslel), každou vysvětlí jednou větou, nic neopravuje, jen upozorní, a uloží výsledek jako separátní markdown vedle zdrojů. Používej kdykoli uživatel řekne "blindspot", "blind spot", "blindspot pass", "slepá místa", "unknown unknowns", "na co jsem nepomyslel / nezapomněl jsem na něco", "co mi uniká", "zkontroluj zadání", "/blindspot" — i když neřekne, nad kterým dokumentem; v tom případě se nejdřív zeptej, co načíst. Komunikuj česky.
---

# Blindspot pass

Cíl: dodat zadavateli seznam **unknown unknowns** jeho zadání — věcí, které v podkladech ani v hlavě nemá, a přitom mu při implementaci vybuchnou pod rukama. Nejde o review kvality dokumentu ani o návrhy řešení; jde o upozornění.

## Postup

1. **Zjisti rozsah.** Pokud uživatel neurčil, který dokument / složku analyzovat, **vždy se nejdřív zeptej** („Nad kterým dokumentem nebo složkou mám blindspot pass udělat?"). Neodhaduj sám — špatně zvolený rozsah znehodnotí celý výstup.
2. **Načti všechno v rozsahu** — nejen hlavní dokument, ale i soubory, na které odkazuje (spec, open questions, analýzy, exporty). Důvod: co už je někde zapsáno jako otevřená otázka nebo rozhodnutí, je *known* unknown a do blindspotů nepatří — bez načtení kontextu bys recykloval známé věci a výstup by ztratil hodnotu.
3. **Proveď pass podle jádrového zadání:**

   > Udělej blindspot pass: najdi mé unknown unknowns tohoto zadání — věci, na které bych sám nepomyslel — a vysvětli mi každou jednou větou. Nic neopravuj, jen mě upozorni.

4. **Ulož výstup** jako separátní markdown vedle zdrojů (viz Formát) a pokud má složka README s tabulkou souborů, přidej do ní řádek.
5. **V odpovědi uživateli** shrň 2–3 nejsilnější nálezy prosou — neopakuj celý seznam.

## Kde blindspoty hledat (checklist myšlení)

Projdi zadání těmito objektivy — každý cílí na kategorii, kterou autoři specifikací systematicky vynechávají:

- **Lifecycle mimo happy path** — spec typicky řeší vytvoření a zrušení; vybuchuje editace, změna za běhu, snížení limitů, návrat zpět.
- **Přechody a migrace** — souběh starého a nového systému, zdroj pravdy, přenos historie, záznamy mizející ze zdrojových dat.
- **Krajní škály** — nejmenší a největší reálný případ (10 vs. 500 položek) a souběh (dva lidé, poslední místo).
- **Čas** — lhůty na poslední chvíli, časová pásma, vícedenní/přesnoční případy, expirace obsahu.
- **Lidé mimo hlavní roli** — hosté, bývalí uživatelé, lidé bez účtu, člověk co změní stav mezi akcí A a B.
- **Právo a platformy** — GDPR (jména, zdravotní data, kontakty), souhlasy, VOP, požadavky App Store/Google Play (UGC moderace).
- **Rozpory mezi podklady** — dva dokumenty tvrdí různé hodnoty téže věci; nikdo si toho nevšiml.
- **Dnešní workaroundy** — co provoz řeší „bokem" (komentáře, QR obrázky, tabulky) je skrytý požadavek, který v datech neuvidíš.
- **Metriky a vynucení** — pravidla, která dnes nikdo nevynucuje; čísla, jejichž význam nikdo nezná; „informovali jsme" ≠ „přečetl si".

Ne každý objektiv vydá nález — prázdný je v pořádku, vycpávky ne. Dobrý pass má typicky 10–20 položek; když jich máš 5, hledal jsi málo, když 40, sklouzl jsi do review.

## Pravidla

- **Jedna věta na položku** — věta smí být souvětí, ale musí unést celé riziko sama; detail patří do případné navazující práce, ne sem.
- **Nic neopravuj a nenavrhuj řešení** — formulace „nikdo nedefinoval X" ano, „doporučuji přidat pole X" ne. Výjimka: šipka na existující otázku (viz níže).
- **Vynech known knowns** — co už je v open questions, rozhodnutích nebo poznámkách zadavatele, sem nepatří.
- **Piš pro zadavatele, ne pro sebe** — bez žargonu, který nezná; pointa musí být srozumitelná na první čtení.

## Formát výstupu

Soubor `blindspot-pass-<tema>.md` vedle zdrojů:

```markdown
---
title: Blindspot pass — <téma>
date: <YYYY-MM-DD>
type: research
---

# Blindspot pass: <téma>

**Účel:** Unknown unknowns zadání — věci nepokryté ve zdrojových dokumentech
ani otevřených otázkách. Nic tu neřeším, jen upozorňuji. Jedna věta na položku.

## <Tematická skupina>

1. **<Úderný název>** — jedna věta vysvětlující riziko. **[→ task X]** *(jen pokud
   položka už má odraz v otázce pro klienta)*

## <Další skupina>
...
```

- Čísluj průběžně přes celý dokument (položky se pak citují číslem).
- Skupiny voľ podle tématu (3–6 skupin), ne podle checklistu výše.
- Při pozdější aktualizaci dokument **nepřečíslovávej**: potvrzené položky označ ✅ s datem, nové přidej do sekce „Doplněno <datum>" na konec.
