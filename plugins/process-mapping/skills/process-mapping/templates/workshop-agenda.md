---
title: Workshop mapování procesu a validační schůzka (agendy)
date: 2026-10-01
---

# Workshop: {název procesu}

**Účastníci:** lidé, kteří proces opravdu dělají (3–7), facilitátor, zapisovatel · **Délka:** 90–120 min

**Pomůcky:** dlouhá plocha (papír nebo online tabule) a lepíky:

- žlutá = krok
- červená = bolest
- zelená = nápad (odkladiště)
- modrá = otázka `??`

**Varianta:** když už proběhly rozhovory, začni z návrhu mapy (vytištěný HTML výkres nebo tabule). Je to rychlejší než prázdná zeď.

| Čas | Blok | Co se děje | Výstup |
|---|---|---|---|
| 0:00 | Úvod (10 min) | Proč mapujeme. Pravidla: popisujeme realitu, neřešíme viníky, nápady na lepší stav jdou do odkladiště | Shoda na cíli |
| 0:10 | Rámec (10 min) | Spouštěč, konec, hranice, role (pruhy na plochu) | Pruhy rolí |
| 0:20 | Kroky (35 min) | Každý píše kroky na žluté lepíky (sloveso + předmět), pak řadíme zleva doprava do pruhů | Hrubý tok as-is |
| 0:55 | Rozhodnutí a výjimky (20 min) | Kde se rozhoduje, co když…, čekání a předávky | Rozhodnutí, výjimky |
| 1:15 | Bolesti (15 min) | Červené lepíky na místa, která zdržují nebo bolí. Každý má 3 tečky na hlasování | Mapa bolestí s pořadím |
| 1:30 | Shrnutí (10 min) | Projít tok nahlas, otevřené otázky `??` s vlastníky, odkladiště nápadů | Seznam `??`, kdo co ověří |

**Po workshopu:**

1. Plochu hned vyfoť.
2. Přepiš ji do `<proces>-as-is.process.toml` a spusť `pmap.py check`.
3. Vyrenderuj a pošli účastníkům k ověření s termínem pro zpětnou vazbu.

# Validační schůzka: {název procesu}

**Účastníci:** vlastník procesu, 2–3 lidé z procesu, schvalovatel · **Délka:** 45–60 min · **Pomůcky:** HTML výkres v režimu Krokovat

| Čas | Blok | Co se děje | Výstup |
|---|---|---|---|
| 0:00 | Úvod (5 min) | Co validujeme (as-is, nebo to-be), verze mapy | |
| 0:05 | Průchod (25 min) | Krokovat mapu a na ní projít 2–3 skutečné nedávné případy, z toho jednu výjimku | Seznam rozdílů |
| 0:30 | Otázky (15 min) | Projít otevřené `??` v panelu výkresu, zapsat odpovědi | Vyřešené otázky (`answer`) |
| 0:45 | Rozhodnutí (10 min) | Schváleno, nebo co změnit a kdy další kolo | `status`, `approved`, nová `version` |
