---
title: Metodika mapování procesu
date: 2026-10-01
---

# Metodika mapování procesu

Postup od rámce po předání vývoji. Fáze odpovídají skillu `process-mapping`. Fakta mají ID z [research.md](research.md) (`[F 1.11]`). Věty bez ID jsou naše doporučení.

Na objevování procesu si nech čas. Podle 7PMG strávily nejúspěšnější organizace přes 40 % času projektu objevováním procesu a tvorbou prvního modelu [F 1.20].

<a id="faze-0"></a>
## Fáze 0 · Rámec

- **Cíl:** vědět, proč a co mapujeme, kde proces začíná a končí a kdo mapu schválí.
- **Vstupy:** zadání od klienta, organizační struktura, existující dokumentace.
- **Postup:**
  1. Zjisti účel mapování. Určuje úroveň detailu: přehled pro vedení L1, zlepšení L2, zadání vývoje L3 (viz [notation.md](notation.md#urovne-detailu)).
  2. Vymez hranice: spouštěč, výsledek a co je mimo. SIPOC slouží právě k vymezení rozsahu [F 1.4].
  3. Vyplň SIPOC v pořadí proces, výstupy, zákazníci, vstupy, dodavatelé [F 1.5]. Proces má 5 až 7 kroků [F 1.3].
  4. Sepiš stakeholdery: vlastník procesu, sponzor, lidé v procesu, kdo mapu validuje a kdo ji schválí.
  5. Domluv zdroje: koho se ptát, kdy je workshop, jestli existují data ze systémů.
- **Otázky:**
  - Proč proces mapujeme? (automatizace, zadání vývoje, zlepšení, dokumentace, audit)
  - Čím proces začíná a čím končí? Co už do něj nepatří?
  - Kdo ho vlastní a kdo v něm pracuje?
  - Kdo mapu na konci schválí a do kdy?
  - Jak často proběhne?
- **Výstup:** `[process]` ve specu (`purpose`, `trigger`, `outcome`, `owner`, `volume`), SIPOC a rámec v dokumentu procesu.
- **Hotovo, když:** vlastník procesu souhlasí s hranicemi a víme, kdo bude validovat.

<a id="faze-1"></a>
## Fáze 1 · Sběr as-is

- **Cíl:** zjistit, jak proces opravdu probíhá dnes.
- **Vstupy:** rámec z fáze 0, seznam lidí, případně logy ze systému.
- **Postup:**
  1. Rozhovory s lidmi, kteří práci dělají (viz [Rozhovor s expertem](#rozhovor-s-expertem)).
  2. Workshop, když proces jde přes víc rolí (viz [Workshop](#workshop)).
  3. Pozorování na místě, kde práce vzniká (gemba): sleduj jeden případ od začátku do konce napříč odděleními [F 1.16]. Gemba je jakékoli místo, kde vzniká hodnota, nejen výroba [F 1.17].
  4. Data ze systému, když existují: minimální log má případ, aktivitu a čas [F 1.28]. Extrakci řiď otázkami, ne tím, co je k dispozici [F 1.29].
  5. Rozdíly mezi tím, co lidé řekli, a tím, co ukázalo pozorování nebo data, zapisuj zvlášť.
- **Otázky:** po krocích podle [templates/interview-guide.md](../templates/interview-guide.md): rámec, kroky na posledním případu, rozhodnutí, výjimky, data, bolesti.
- **Výstup:** zápisy z rozhovorů, fotka workshopové plochy, seznam otázek `??`.
- **Hotovo, když:** máme od začátku do konce aspoň jeden skutečný případ a víme, kde se liší výpovědi.

<a id="faze-2"></a>
## Fáze 2 · Model as-is

- **Cíl:** zapsat proces do `<proces>-as-is.process.toml` a ověřit ho s expertem.
- **Vstupy:** výstupy fáze 1.
- **Postup:**
  1. Nejdřív nejčastější průběh, výjimky potom a postupně podle priority [F 1.18].
  2. Každý krok musí mít oporu ve zdroji. Krok, který nezazněl, zapiš jako otázku, ne jako krok (viz [Časté chyby](#caste-chyby)).
  3. Spusť `pmap.py check` a oprav chyby. Kontrola stavby je jiná věc než validace: model musí odpovídat skutečnému procesu [F 1.19].
  4. Drž model malý a strukturovaný: co nejméně prvků, jeden start a jeden konec, popisky sloveso + předmět [F 1.21].
  5. Vyrenderuj výkres a projdi ho s expertem krok po kroku.
- **Výstup:** as-is spec ve stavu `draft`, výkres, otevřené `??`.
- **Hotovo, když:** expert řekne „takhle to dnes je“ a otázky mají vlastníka.

<a id="faze-3"></a>
## Fáze 3 · Analýza

- **Cíl:** najít, co zdržuje, co nepřidává hodnotu a proč.
- **Vstupy:** as-is model s časy (`time`) a bolestmi (`pain`).
- **Postup:** podle [Analýza](#analyza) níže. Označ kroky, najdi plýtvání, hledej příčiny, spočítej dopad a seřaď.
- **Otázky:**
  - Kde se nejvíc čeká a proč?
  - Co se dělá dvakrát nebo se vrací?
  - Které předávky by šly zrušit?
  - Co se stane, když krok vynecháme?
- **Výstup:** tabulka problémů v dokumentu procesu (dopad, příčina, návrh).
- **Hotovo, když:** vlastník souhlasí s pořadím problémů.

<a id="faze-4"></a>
## Fáze 4 · Návrh to-be

- **Cíl:** navrhnout, jak má proces fungovat.
- **Vstupy:** as-is model a seřazené problémy z analýzy.
- **Postup:**
  1. Nejdřív zjednodušit: zrušit zbytečné kroky, předávky a kontroly.
  2. Pak přesunout práci tam, kde vzniká informace.
  3. Až potom automatizovat. Automatizovaný zbytečný krok je pořád zbytečný.
  4. Každá změna navazuje na problém z analýzy (tabulka „Změny oproti as-is“ v dokumentu procesu).
  5. To-be je nový soubor `<proces>-to-be.process.toml`. Id kroků, které zůstávají, nech stejné.
- **Otázky:**
  - Který problém tahle změna řeší?
  - Kdo ztratí nebo získá práci?
  - Co systém musí umět, aby to fungovalo?
- **Výstup:** to-be spec, výkres, tabulka změn.
- **Hotovo, když:** každá změna má problém, který řeší, a vlastník návrh zná.

<a id="faze-5"></a>
## Fáze 5 · Validace

- **Cíl:** potvrdit, že mapa odpovídá realitě (as-is) nebo že návrh půjde provozovat (to-be).
- **Vstupy:** výkres v režimu Krokovat, otevřené `??`.
- **Postup:**
  1. Na validační schůzce projdi mapu krok po kroku na 2 až 3 skutečných nedávných případech, z toho jedné výjimce ([templates/workshop-agenda.md](../templates/workshop-agenda.md), validační schůzka). Krokování odpovídá tomu, jak lidé děj chápou: po krocích [F 5.3].
  2. Zapiš rozdíly a odpovědi na `??` (`status = "resolved"`, `answer`).
  3. Na konci projdi celý tok nahlas, ať nic nechybí [F 1.14].
  4. Zapiš schválení: `status`, `approved` (kdo, kdy), nová `version`.
- **Výstup:** spec ve stavu `k-validaci` nebo `schvaleno`, zápis rozdílů.
- **Hotovo, když:** schvalovatel řekl ano a otevřené `??` nejsou blokující.

<a id="faze-6"></a>
## Fáze 6 · Předání

- **Cíl:** předat schválený proces dál, typicky do vývoje.
- **Vstupy:** schválený to-be spec.
- **Postup:**
  1. Doplň dokument procesu podle [templates/process-doc.md](../templates/process-doc.md): kroky, role, výjimky, pravidla, data, ukazatele.
  2. Pravidla s víc podmínkami dej do rozhodovací tabulky (viz [diagram-types.md](diagram-types.md#katalog)).
  3. Vyrob výstupy pro příjemce: HTML výkres, SVG do dokumentu, Mermaid do repa.
  4. Navazuje `product-design:implementation-spec`.
- **Výstup:** dokument procesu, výkres, generované výstupy.
- **Hotovo, když:** příjemce ví, co má postavit, a nemá otázky k průběhu.

<a id="analyza"></a>
## Analýza

1. **Přidaná hodnota u kroků.** Označ každý krok VA (přidává hodnotu zákazníkovi), BVA (nutný pro chod firmy nebo kvůli předpisům) a NVA (vše ostatní). Předávky, čekání a přepracování jsou NVA [F 1.10].
2. **Osm druhů plýtvání.** Ohnových sedm (nadvýroba, čekání, doprava, zbytečné zpracování, zásoby, pohyb, vady) a osmý, nevyužitý talent [F 1.22]. U každého plýtvání rozliš, jestli ho jde odstranit hned, nebo zatím ne [F 1.23].
3. **Příčiny.** 5× proč se ptá, dokud se nedojde k příčině; číslo pět není podstatné [F 1.24]. U složitějšího problému pomůže Ishikawa [F 2.35].
4. **Časy.** Čas, který tvoří hodnotu, je kratší než cycle time a ten je kratší než lead time [F 1.7]. Účinnost cycle time (teoretický cycle time, tedy jen zpracování, dělený skutečným) ukáže, kolik procesu tvoří čekání a předávky [F 1.25].
5. **Kvantifikace.** Dopad počítej jako součin faktorů za období, jako v Dumasově příkladu [F 1.25]. Doporučujeme četnost × čas = hodiny měsíčně (třeba 300 faktur × 10 min = 50 h měsíčně). To je podklad pro business case.
6. **Pořadí.** Problémy veď v registru a seřaď je Paretem [F 1.25]. Pro výběr, co řešit první, doporučujeme matici dopad × náročnost.

<a id="rozhovor-s-expertem"></a>
## Rozhovor s expertem

- Na otázku „jak to obvykle děláte“ lidé popíšou idealizovaný postup bez zkratek a odchylek [F 1.11]. Ptej se proto na poslední konkrétní případ.
- Technika kritických incidentů žádá vybavit si konkrétní událost, ne zvyk [F 1.12]. Doporučujeme doplnit poslední problematický případ.
- Zapisuj, co člověk udělal, ne co by měl dělat. Abstrakci do modelu dělá až analytik.
- Scénář: [templates/interview-guide.md](../templates/interview-guide.md).

<a id="workshop"></a>
## Workshop

- **Kdo:** víceúrovňový tým napříč odděleními a zkušený neutrální facilitátor [F 1.13]. Aspoň jeden facilitátor a jeden zapisovatel [F 1.14].
- **Jak dlouho:** zdroje uvádějí nejvýš 4 hodiny [F 1.14] nebo nejvýš den [F 1.13]. Naše šablona počítá s 90 až 120 minutami.
- **Jak:** role papíru a barevné lístky [F 1.13]. Každý píše kroky sám za sebe a na konci facilitátor projde celý tok [F 1.14].
- **Vedoucí:** zvaž, jestli má být v místnosti. V případové studii LEI se vedoucí záměrně neúčastnila a tým 22 lidí našel 29 míst s plýtváním [F 1.15].
- **Šablona:** [templates/workshop-agenda.md](../templates/workshop-agenda.md).

## Realita, ne ideál

- Mapuj, co se děje, ne co by se dít mělo [F 1.13]. Co lidé říkají, se liší od toho, co dělají [F 1.11].
- Ověřuj pozorováním [F 1.16] nebo daty ze systému [F 1.28]. Data z ERP mají pasti: jedna událost patří k víc případům nebo se aktivita v případu opakuje [F 1.30].
- As-is a to-be jsou dva soubory. Návrh do as-is nepatří.
- Doporučujeme u modelu poznamenat zdroj: pozorováno, deklarováno v rozhovoru, nebo návrh.

## Výjimky a předávky

- Výjimky sbírej, seřaď podle četnosti a přidávej postupně, až po hlavním průběhu [F 1.18].
- Předávka je místo, kde se čeká. Swimlane pomáhá předávky a čekání najít [F 2.12]; v analýze jsou předávky NVA [F 1.10].
- U každé výjimky zapiš, jak se řeší dnes, jak často nastává a co s ní bude v to-be (tabulka výjimek v dokumentu procesu).

<a id="caste-chyby"></a>
## Časté chyby

1. **Mapa ideálu místo reality.** Otázka „jak to obvykle děláte“ vede k idealizovanému postupu [F 1.11].
2. **Vymyšlené kroky při práci z přepisů.** Jazykové modely při generování procesních modelů přepisují netypický průběh na učebnicový [F 1.26]; vymyšlené aktivity a chybné vazby jsou opakovaný problém a validace člověkem je nutná [F 1.27]. Každý krok musí mít oporu v přepisu; co nezaznělo, je `??`. Zvlášť hlídej procesy, které vypadají standardně (objednávka, fakturace).
3. **Začít výjimkami.** Hlavní průběh se v nich ztratí [F 1.18].
4. **Moc velký model.** Nad 50 prvků rozdělit [F 3.21]; čím větší model, tím víc chyb [F 1.21].
5. **Úroveň detailu bez účelu.** Bez odpovědi na „proč mapujeme“ vznikne buď moc hrubá, nebo moc jemná mapa.
6. **Vedoucí diktuje.** Problémy mají pojmenovat lidé, kteří práci dělají [F 1.15].
7. **Kontrola místo validace.** Bezchybný `check` neznamená, že mapa odpovídá realitě [F 1.19].
8. **Rozhodnutí bez otázky.** Brána bez otázky a bez popsaných výstupů nejde přečíst [F 3.12].
9. **Automatizovat dřív než zjednodušit.** Změna bez problému z analýzy je jen jiný proces.
10. **Barva jako jediný nositel významu** [F 3.25].
11. **Podcenit objevování.** Úspěšné projekty mu věnovaly přes 40 % času [F 1.20].

<a id="kdy-animovat"></a>
## Kdy animovat

- **Statická mapa nese všechno.** Kde animace nad statickou grafikou vyhrála, nebylo srovnání rovnocenné [F 5.1]. Papírové statické diagramy nebyly v experimentech nikdy horší než animace a ve 4 z 8 srovnání byly lepší [F 5.8]. Animace je proto jen volitelná vrstva.
- **Výzkum je smíšený.** Metaanalýzy ukazují malou až střední výhodu instruktážních animací [F 5.9] [F 5.10]. Pro analýzu je animace nejhorší forma [F 5.14]; při prezentaci je rychlá a lidi baví, ale vede k chybám [F 5.15].
- **Na schůzce krokovat.** Lidé si děj představují jako sled kroků [F 5.2], proto je přirozené ho po krocích i ukázat [F 5.3]. Zastavení a opakování dovolí vrátit se k části [F 5.4]; když tempo řídí uživatel, chápe se lépe [F 5.6].
- **Přechody krátké.** Tak dlouhé, aby šlo změnu sledovat, a ne déle, kolem 1 sekundy [F 5.13]. Najednou se dají sledovat jen 3 až 4 objekty [F 5.16].
- **Nic opakovaně samo.** Animace, kterou člověk vidí znovu a znovu, zdržuje od obsahu [F 5.18]. Automatický pohyb nad 5 sekund musí jít zastavit [F 5.28].
- **Omezený pohyb.** Respektuj `prefers-reduced-motion` [F 5.30]; podle WCAG má jít vypnout pohyb spuštěný interakcí [F 5.25]. Změna barvy a průhlednosti se za pohybovou animaci nepočítá [F 5.27].
- **Znalci procesu animaci nepotřebují.** Lidem, kteří si systém umí rozpohybovat v hlavě sami, může v některých případech škodit [F 5.7].
- **Napřed přehled, detail na vyžádání** [F 5.23]. Víc než dvě úrovně odhalování mívají nízkou použitelnost [F 5.20].

**Jak to dělá HTML výkres pluginu:** animace se přehraje jednou po zobrazení výkresu, jde přeskočit a přehrát znovu. Režim Krokovat ovládá presenter šipkou nebo mezerníkem. Při omezeném pohybu, v tisku a bez JavaScriptu se ukáže hotový stav. Detail kroku se otevře klikem v panelu vpravo.
