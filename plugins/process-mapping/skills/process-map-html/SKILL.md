---
name: process-map-html
description: Vyrobí z popisu procesu (<proces>.process.toml) animovaný HTML výkres procesní mapy ve stylu blueprint. Kroky a šipky se postupně kreslí, na schůzce jde mapu krokovat šipkami, klik na krok ukáže detail s otázkami a bolestmi, je tu světlá varianta, tisk do PDF, fullscreen a statické SVG pro prezentace. Použij, když uživatel chce interaktivní nebo animovanou procesní mapu do prohlížeče, výkres pro klienta k prohlížení offline, obrázek procesu do prezentace, nebo přegenerovat existující mapu po změně procesu. Triggeruj na „HTML procesní mapa“, „animovaný výkres procesu“, „interaktivní swimlane“, „vyrenderuj proces“, „proces do PDF“. Animovaná demo okna do webu jsou web-motion:animated-demo-windows. Komunikuj česky.
---

# Procesní mapa jako HTML výkres

Jeden samostatný HTML soubor z popisu procesu: bez externích zdrojů, funguje offline, posílá se e-mailem. Obsah (role, kroky, otázky) se mění jen ve zdrojovém `<proces>.process.toml`, HTML se vždycky přegeneruje.

## Postup

1. Popis procesu musí existovat. Když neexistuje, nejdřív skill `process-mapping` (vede mapování a založí popis).
2. Kontrola:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/process-mapping/scripts/pmap.py" check "<spec>"
   ```
   Chyby oprav ve specu, upozornění projdi s uživatelem. Bez `${CLAUDE_PLUGIN_ROOT}` (Cursor) použij `"<SKILL_DIR>/../process-mapping/scripts/pmap.py"`, kde `SKILL_DIR` je Base directory tohoto skillu. Pracovní složka zůstává v projektu uživatele.
3. Výkres:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/process-mapping/scripts/pmap.py" html "<spec>" [-o "<cesta>.html"] [--link "Dokument=proces.md"]
   ```
   `--link` přijme jen relativní cestu, `http`, `https` nebo `mailto`.
4. Obrázek do prezentace: `… pmap.py svg "<spec>"` (světlé statické SVG ve finálním stavu). Když ho PowerPoint nebo Word zobrazí bez stylů, vlož snímek obrazovky ze světlého výkresu.
5. Ověř v prohlížeči (Playwright, jedna stránka po druhé, nikdy paralelně):
   - animace doběhne do finálního stavu;
   - „Krokovat“ jde šipkami;
   - klik na krok ukáže detail;
   - světlý výkres, tisk (`browser_emulate_media` s `media: "print"`) a reduced-motion (`reducedMotion: "reduce"`) fungují;
   - fullscreen otevře overlay a klik na uzel v něm otevře detail.

   Snímky ukládej mimo repo a po kontrole smaž složku `.playwright-mcp`, kterou Playwright založí v pracovní složce.
6. Když nesedí rozložení, uprav spec (`col` u kroku, `route = "vh" | "hv"` u přechodu, `next = false`) a vygeneruj znovu. HTML ručně needituj.

## Co výkres umí

- Hlavička se stavem (návrh, k validaci, schváleno), verzí, datem úpravy a vygenerování, zdrojem a odkazy (`--link`).
- Blueprint výkres a světlá varianta (volba se pamatuje v prohlížeči), tiskový styl na šířku bez ovládacích prvků.
- Přehrát znovu, přeskočit, krokovat (← →, mezerník, Esc); `prefers-reduced-motion` a prohlížení bez JavaScriptu (náhled přílohy) ukážou rovnou finální stav.
- Klik nebo Enter na krok, roli, průběžnou roli a stav: detail (popis, výstup, dnes, systémy, čas, bolesti, otevřené i vyřešené otázky).
- Panel s přehledem: rámec procesu, shrnutí „dnes“, bolesti a otevřené otázky, všechno klikací.
- Široký proces se nezmenší pod 85 %, posouvá se vodorovně a popisky rolí zůstávají vidět.
- Fullscreen se zoomem a posunem.

## Ověřené hodnoty (neměnit bez důvodu)

- Z `web-motion:animated-demo-windows` (šablona `blueprint-pipeline.html`): čára `.7s ease`, uzel `.55s ease`, kreslení přes `pathLength="1"` a `stroke-dashoffset`, start přes IntersectionObserver.
- Z referenčního výkresu: odklad startu 400 ms, kroky po 0,8 s, šipka do kroku začíná 0,5 s před ním.
- Proces delší než 11 s animace se úměrně zrychlí.

## Pasti

- Hrot šipky je samostatný prvek, ne `marker-end`. Marker by byl vidět dřív, než se k němu čára dokreslí.
- Čárkovaná čára (smyčka, alternativa) se kreslí přes masku, protože `stroke-dasharray` už slouží animaci.
- Skryté výchozí stavy jsou jen pod třídou `armed`, kterou přidá JavaScript. Bez JS je výkres hotový.
- Barvy výkresu jsou proměnné na `body`, aby fungovaly i ve fullscreen overlayi.
- Po doběhnutí se výkres přepne do statického stavu. Přesun SVG do fullscreenu by jinak animaci spustil znovu.
- Data ve skriptu jsou JSON s escapovaným `<`, `>`, `&`; stránka má CSP s hashi obou skriptů, takže nic nenačítá zvenku.
- Delší texty karet zalamuje `pmap.py` podle počtu znaků; když `check` hlásí přetečení, zkrať text ve specu.
