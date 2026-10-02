---
name: feedback-from-message
description: >-
  Převede jakoukoli zprávu s feedbackem (e-mail .eml, .msg, .txt přepis, Slack
  export, paste konverzace, screenshoty) do strukturovaného Markdown dokumentu
  a interaktivní HTML prezentace s navigací po jednotlivých bodech, copy
  tlačítky pro kódovacího agenta a "Hotovo" stavem v localStorage. Použij
  kdykoli uživatel dostal feedback od klienta/testera/kolegy a chce z toho
  udělat klikatelný přehled bodů, který lze procházet a řešit jeden po druhém.
  Triggeruj na "feedback do prezentace", "udělej z toho feedback HTML",
  "zpracuj feedback", "feedback od klienta", "rozkousej feedback", "prezentace
  feedbacku", "/feedback". Komunikuj česky.
---

# Feedback from Message

Převede vstupní zprávu s feedbackem do dvou výstupů ve stejné složce:

1. **Markdown** — strukturovaný dokument s body feedbacku, citáty, kategoriemi a navrhovanými akcemi.
2. **HTML prezentace** — klikatelný prohlížeč: jedna slide = jeden bod, vlevo obrázek, vpravo text + akce + copy tlačítka, navigace šipkami/klávesnicí, persistentní "Hotovo" stav v localStorage.

Vzorový výstup: `<projekt>/60-user-testing/2026-05-29-onboarding-v1/feedback-tester.{md,html}`.

## Když skill spustit

Uživatel dodá jeden ze vstupů:

- `.eml` soubor (Outlook export, mail s inline obrázky)
- `.msg` soubor (Outlook nativní) — potřeba `extract-msg`
- `.txt` / `.md` přepis konverzace, hlasové poznámky, Slack export
- Paste textu do chatu ("vlepuji co mi napsal klient")
- Slack/Teams konverzace zkopírovaná do textu
- Kombinace text + samostatné screenshoty ve složce

Skill funguje i bez obrázků — body můžou být jen textové.

## Postup

### 1. Identifikuj a načti vstup

Pokud uživatel ukáže na soubor → použij absolutní cestu.
Pokud vleple paste do chatu → ulož do `/tmp/feedback-input-<datum>.txt` a pracuj odtamtud.
Pokud je `.eml`, použij `assets/extract_eml.py` (viz níže).

### 2. Urči cílovou složku

Default: vedle vstupního souboru. Pokud uživatel pracuje v rámci nějakého projektu / klienta, doporuč strukturovanou cestu:

- Projekt s uživatelským testováním → `60-user-testing/YYYY-MM-DD-co-se-testovalo/`
- Klientský workspace → `_KLIENTI/<klient>/docs/inbox/` nebo dedikovaná feedback složka
- Jinak → `feedback-YYYY-MM-DD/` ve working dir

Vždy se zeptej, pokud není zřejmé. Slug ve formátu `YYYY-MM-DD-<kdo>-<co>` (např. `2026-05-30-tester-onboarding`).

### 3. Extrakce obsahu

#### Pro .eml soubor

Spusť pomocí Shell nástroje (`<SKILL_DIR>` je složka tohoto skillu, vypíše se při načtení jako Base directory):

```bash
python3 "<SKILL_DIR>/assets/extract_eml.py" "CESTA_K_EML" "VYSTUPNI_SLOZKA"
```

Skript:
- Uloží `body.txt` a `body.html` do `<vystup>/attachments/`
- Extrahuje obrázky jako `img-01.png`, `img-02.png`, … v pořadí výskytu v HTML
- Uloží `cid-map.txt` (mapování CID → soubor)

#### Pro .msg soubor

Použij vzor ze skillu `email-to-markdown` (`extract-msg` + BeautifulSoup), případně doporuč uživateli předtím export do `.eml`.

#### Pro text / paste

Stačí přečíst do paměti.

### 4. Rozseparuj na body

Hledej v textu strukturu (bullet body, odrážky, číslované seznamy, samostatné odstavce uvozené prázdným řádkem). Každý logický bod = jedna slide.

Pro každý bod identifikuj:

- **Originální citát** (verbatim — nepřepisuj, nečisti gramatiku, zachovej autorův hlas)
- **Titulek** (krátký, akční, max ~10 slov — ty ho napíšeš)
- **Kategorie:**
  - `Bug` — nefunguje něco
  - `Feature` — návrh nové funkce
  - `UX / Copy` — text, pořadí, drobné úpravy
  - `Konfigurace` — data cleanup, business pravidla
  - `Otevřená otázka` — vyžaduje diskuzi
  - `Resolved` — pisatel sám vzal zpět nebo vyřešil
- **Obrázek** (pokud existuje a patří k bodu — typicky `attachments/img-NN.png`)
- **Akce** (1–4 odrážky — co s tím konkrétně udělat)

### 5. Napiš Markdown

Šablona (uprav podle vstupu):

```markdown
---
title: Feedback od {kdo} — {co}
date: YYYY-MM-DD
type: feedback
source: {kdo}
status: raw
---

# Feedback od {kdo} — {co}

**Kontext:** {co se testovalo / o čem to je}
**Kdy dorazil:** YYYY-MM-DD HH:MM
**Originál:** `attachments/body.txt` (+ obrázky `attachments/img-NN.png`)

---

## Body feedbacku

### 1. {Titulek}

> {Verbatim citát}

**Obrázek:** `attachments/img-01.png`
**Kategorie:** {kategorie}
**Akce:**
- ...
- ...

---

### 2. ...
```

Na konec markdownu přidej **souhrn pro kódovacího agenta**:

```markdown
## Souhrn pro kódovacího agenta

**Bugy (priorita):** #1, #5, #6
**Změny pravidel / konfigurace:** #2, #8
**Features:** #3
**Rozhodnutí potřeba:** #10
```

### 6. Vygeneruj HTML prezentaci

Použij `assets/template.html` jako základ. V templatu nahraď 4 placeholdery:

| Placeholder | Hodnota |
|---|---|
| `{{TITLE}}` | `<title>` tagu — např. `"Feedback Tester: Onboarding v1"` |
| `{{HEADER_TITLE}}` | Text v hlavičce stránky — např. `"Tester: Feedback Onboarding v1 (2026-05-30)"` |
| `{{SLIDES_JSON}}` | Pole JSON objektů — viz dále |
| `{{STORAGE_KEY}}` | Unikátní localStorage klíč — např. `"feedback-tester-onboarding-v1-done"` (slug + `-done`) |

Postup: `Read` template.html, pak `Write` výstupu se třemi `replace`y:

```python
template = read("<SKILL_DIR>/assets/template.html")
out = (template
    .replace("{{TITLE}}", "Feedback Tester: Onboarding v1")
    .replace("{{HEADER_TITLE}}", "Tester: Feedback Onboarding v1 (2026-05-30)")
    .replace("{{STORAGE_KEY}}", "feedback-tester-onboarding-v1-done")
    .replace("{{SLIDES_JSON}}", json.dumps(slides, ensure_ascii=False, indent=2))
)
write("VYSTUPNI/feedback-<slug>.html", out)
```

Struktura každého slide objektu:

```json
{
  "n": 1,
  "title": "Titulek bodu",
  "category": "Kategorie human-readable",
  "catClass": "cat-bug",
  "img": "attachments/img-01.png",
  "quote": "Verbatim citát s newlines jako \n",
  "actions": ["První akce", "Druhá akce"]
}
```

`img` může být `null`, pak prezentace zobrazí „Bez obrázku".

Možné `catClass` hodnoty (definované v CSS):
- `cat-bug` (červená)
- `cat-feature` (modrá)
- `cat-config` (zelená)
- `cat-decision` (žlutá)
- `cat-resolved` (šedá)

Title v `<header>` a klíč v `STORAGE_KEY` přizpůsob feedbacku (např. `feedback-{slug}-done`), aby done-stav nekolidoval mezi různými feedbacky.

### 7. Otestuj zobrazení

Po vytvoření souborů ověř, že obrázky jsou validní a HTML otevíratelné:

```bash
python3 -c "
import os
folder = 'CESTA_K_ATTACHMENTS'
for f in sorted(os.listdir(folder)):
    if f.startswith('img-'):
        with open(os.path.join(folder, f), 'rb') as fp:
            ok = fp.read(4) == b'\\x89PNG'
        print(f, 'OK' if ok else 'BAD')
"
```

Pokud cesta obsahuje mezery nebo diakritiku (typické pro OneDrive), pro spolehlivé zobrazení obrázků nabídni uživateli **lokální HTTP server**:

```bash
cd "CESTA_KE_SLOZCE_S_HTML" && python3 -m http.server 8765 > /tmp/feedback-server.log 2>&1 &
echo $! > /tmp/feedback-server.pid
sleep 1
open "http://localhost:8765/feedback-<slug>.html"
```

Zastavení: `kill $(cat /tmp/feedback-server.pid)`.

### 8. Updatuj index (pokud existuje)

Pokud cílová složka má `README.md` s tabulkou kol feedbacku (např. `60-user-testing/README.md`), přidej řádek se nového kola.

## Funkce HTML prezentace (template)

- **Navigace:** šipky `← →` / klávesnice / nahoře tlačítka `Předchozí / Další`
- **Obrázek:** klik = lightbox (zavřít `Esc`)
- **Copy tlačítka:**
  - „📋 Kopírovat originál pro agenta" — citát + cesta k obrázku
  - „📋 Kopírovat vše" — kompletní markdown blok (titulek, kategorie, citát, akce)
- **Done stav:**
  - tlačítko `✓ Hotovo` / `↶ Vrátit zpět`
  - klávesa `D`
  - vizuální stav: zelený badge "HOTOVO", přeškrtnutý titulek, ztmavený obrázek
  - počítadlo v hlavičce `✓ X / N hotovo`
  - persistence v `localStorage` (přežije refresh)
- **Hash v URL** drží aktuální bod (`#7` = bod 7) — sdílení konkrétního bodu odkazem

## Důležité

- **Nikdy nepřepisuj originální text klienta.** Citát zůstává verbatim. Tvoje úpravy jsou jen v titulku, kategorii a akcích.
- **Nepřidávej body, které tam nejsou.** Pokud klient napsal 5 vět = pravděpodobně 5 bodů, ne 7.
- **Pokud jsou věci propojené,** explicit to v akci („vztah s bodem #3").
- **Vstupní soubor nemaž ani nepřejmenovávej** — vytvoř nové soubory vedle.
- **HTML otevírej přes lokální server,** ne `file://`, pokud cesta obsahuje mezery/diakritiku (typické pro OneDrive Datawizardu).
