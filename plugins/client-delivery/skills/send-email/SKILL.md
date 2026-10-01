---
name: send-email
description: Připraví email z Markdown draftu s YAML frontmatter — převede na HTML a otevře v Outlooku, nebo vypíše jako čistý text ke zkopírování. Používej tento skill kdykoli uživatel chce poslat email, napsat email klientovi, připravit zprávu, naformátovat email, nebo říká "/send-email". Triggeruj i na "pošli email", "napiš email", "otevři v Outlooku", "připrav zprávu pro klienta", "send this email", "open in Outlook", "draft an email", "naformátuj email". Komunikuj česky.
---

# Send Email

Připravíš email z Markdown draftu. Výchozí výstup je otevření zprávy v Microsoft Outlooku. Alternativně můžeš vypsat čistý text, který si uživatel zkopíruje sám.

## Kdy se skill aktivuje

- Uživatel má hotový `.md` soubor s email draftem a chce ho poslat
- Uživatel chce napsat email od nuly
- Uživatel říká cokoliv o posílání emailu klientovi

## Výstupní formáty

| Formát | Kdy použít | Jak |
|--------|-----------|-----|
| `outlook` (výchozí) | Uživatel chce otevřít v Outlooku | `--format outlook` |
| `text` | Uživatel říká "jenom text", "zkopíruju si to sám", "nechci Outlook" | `--format text` |
| inline obrázky | Draft má v těle `![popis](cesta.png)` a obrázky mají být uvnitř mailu | jiný skript, viz níže |

Pokud uživatel nespecifikuje, použij `outlook`.

## Workflow

### Varianta A: Existující Markdown draft

Pokud uživatel odkáže na existující `.md` soubor:

1. Přečti soubor a ověř, že má YAML frontmatter s povinnými poli (`to`, `subject`)
2. Pokud chybí povinná pole, doptej se
3. Spusť bundlovaný skript:

```bash
# Outlook (výchozí)
python "<SKILL_DIR>/scripts/open-in-outlook.py" "<cesta-k-md-souboru>"

# Plain text
python "<SKILL_DIR>/scripts/open-in-outlook.py" "<cesta-k-md-souboru>" --format text

# S přílohami
python "<SKILL_DIR>/scripts/open-in-outlook.py" "<cesta-k-md-souboru>" \
  --attachment "/cesta/k/priloha1.pdf" \
  --attachment "/cesta/k/priloha2.docx"
```

### Obrázky v těle mailu (inline)

Když má být screenshot **uvnitř** mailu, ne jako příloha, napiš ho do draftu
markdownem na samostatný řádek:

```markdown
![Popis obrázku](img/01-screenshot.png)
```

a pusť druhý skript:

```bash
python "<SKILL_DIR>/scripts/open-in-outlook-inline.py" "<cesta-k-md-souboru>"

# jen vyrobit .eml a nesahat na Outlook (kontrola před importem)
python "<SKILL_DIR>/scripts/open-in-outlook-inline.py" "<cesta>" --eml-only /tmp/draft.eml

# šířka zobrazení obrázků, výchozí 720 px
python "<SKILL_DIR>/scripts/open-in-outlook-inline.py" "<cesta>" --max-width 600
```

Proč zvlášť: `content` se do Outlooku posílá přes AppleScript a ten neumí přiřadit
příloze Content-ID, takže obrázek se do těla nedostane. Base64 `data:` URI zase
nezobrazí Outlook na Windows. Inline skript proto poskládá regulérní MIME zprávu
(`multipart/related` s `cid:` odkazy) a naimportuje ji do složky Koncepty přes
`import eml`. Obrázky pak vidí Outlook na Windows, Outlook Web i Gmail.

Rozdíly proti `open-in-outlook.py`:

- Zpráva **končí ve složce Koncepty**, neotevře se jako nové okno zprávy.
- `attachments:` ve frontmatteru pořád funguje, jde o běžné přílohy vedle inline obrázků.
- Pole `from:` se použije jako odesílatel zprávy (u druhého skriptu je jen pro kontext).

Po importu řekni uživateli, ať koncept v Outlooku otevře, zkontroluje a pošle ručně.

### Varianta B: Email od nuly

Pokud uživatel chce napsat nový email:

1. Zeptej se na klíčové informace (pokud nejsou zřejmé z kontextu):
   - Komu? (jméno + email)
   - Předmět?
   - O čem má email být? (body/kontext)
   - Přílohy?
2. Napiš Markdown draft a ulož ho do příslušné složky
3. Ukaž uživateli draft k odsouhlasení
4. Po schválení spusť skript

### Kde uložit nový draft

Pokud pracuješ v klientské složce, ulož draft do:
```
<klient>/01-communications/02-messages/<YYYY-MM-DD>-<popis>/
```

Pokud ne, zeptej se uživatele kam uložit.

## Formát Markdown draftu

```markdown
---
type: sent-email
date: 2026-04-08
to: Jméno Příjemce <email@example.com>
subject: Předmět emailu
from: Jméno Odesílatele <jmeno@datawizard.cz>
signature: default
status: draft
attachments:
  - ../priloha1.pdf
  - /absolutni/cesta/k/priloha2.docx
---

# Název emailu (neposílá se — slouží jako nadpis v souboru)

Dobrý den,

text emailu v Markdownu...

S pozdravem,
```

> **Podpis do těla nepiš.** Skript ho přidá sám podle pole `signature` (viz níže).
> Draft zakonči jen pozdravem („S pozdravem," / „Měj se,").

### Frontmatter pole

| Pole | Povinné | Popis |
|------|---------|-------|
| `to` | ano | Příjemce — `Jméno <email>` nebo jen `email` |
| `subject` | ano | Předmět zprávy |
| `from` | ne | Odesílatel (pro kontext, Outlook použije aktivní účet) |
| `signature` | ne | Profil odesílatele — bez uvedení se použije `default` (tvůj osobní profil), jinak jméno profilu — viz níže |
| `date` | ne | Datum draftu |
| `type` | ne | Vždy `sent-email` |
| `status` | ne | `draft` nebo `sent` |
| `attachments` | ne | Seznam cest k přílohám (relativní k .md souboru nebo absolutní) |

### Podpis / profil odesílatele

Podpis se **nepíše do těla mailu** — skript ho vyrenderuje z profilu odesílatele a přidá na konec (do Outlooku jako HTML, do textového výstupu jako plain text). Profil vybírá pole `signature` ve frontmatter; bez něj se použije profil `default`, tj. **tvůj vlastní podpis**.

**Profil = malý JSON** se čtyřmi poli (všechna volitelná kromě `name`) — viz `signatures/_template.json`:

```json
{
  "name": "Jméno Příjmení",
  "tagline": "Krátký popis role / co děláš",
  "email": "jmeno@datawizard.cz",
  "phone": "+420 000 000 000"
}
```

**První nastavení (jednou per člověk):** zkopíruj `signatures/_template.json` do `~/.claude/email-signatures/default.json` a vyplň svoje údaje. Hotovo — všechny emaily bez explicitního `signature:` pole dostanou tvůj podpis. Konfigurace žije mimo plugin, takže přežije jeho update a nesdílí se.

**Sdílené profily v repu** (`signatures/<jmeno>.json`) — šablony jednotlivých lidí, hodí se když někdo posílá email „za" kolegu nebo pod jinou značkou:

| `signature` | Kdo | Soubor |
|-------------|-----|--------|
| `karel-simek` | Karel Šimek — DatawizardCZ | `signatures/karel-simek.json` |
| `karel-simek-tokada` | Karel Šimek — Tokada | `signatures/karel-simek-tokada.json` |

Chceš do repa přidat svůj sdílený profil? Zkopíruj `_template.json` na `signatures/<jmeno>.json` a commitni.

**Pořadí hledání profilu** (první nález vyhrává): `~/.claude/email-signatures/<name>.json` → `~/.claude/email-signatures/<name>.html` → `signatures/<name>.json` ve skillu → `signatures/<name>.html` ve skillu. Pro pokročilý podpis (logo apod.) můžeš místo JSON vložit `<name>.html` s hotovým HTML blokem — použije se doslovně.

### Co skript dělá s Markdown body

- Odstraní blockquoty na začátku (metadata draft) a úvodní `# Nadpis`
- **Formát `outlook`**: Převede Markdown na HTML (Calibri, inline styly), **připojí podpis odesílatele**, otevře v Outlooku přes AppleScript
- **Formát `text`**: Vypíše hlavičku (Komu, Předmět) + čistý Markdown body + textový podpis na stdout

### Podporovaný Markdown

| Syntax | Výstup |
|--------|--------|
| `**text**` | **tučný** |
| `*text*` | *kurzíva* |
| `[text](url)` | odkaz |
| `# Nadpis` | nadpis (h1–h3) |
| `- položka` | odrážkový seznam |
| `1. položka` | číslovaný seznam |
| `---` | horizontální čára |
| `` `kód` `` | inline kód |

## Spuštění skriptu

Skript je bundlovaný v tomto skillu. Cesta ke skriptu je relativní k SKILL.md:

```
<tento-skill>/scripts/open-in-outlook.py
```

Skript potřebuje Python 3 (standardní knihovny, žádné dependencies). **Formát `outlook` funguje jen na macOS s nainstalovaným Microsoft Outlookem** (používá AppleScript). Na jiné platformě nebo bez Outlooku použij `--format text` a výstup zkopíruj do libovolného mail klienta.

## Po spuštění

- **Outlook**: Oznam, že zpráva je otevřená. Připomeň: "Zkontroluj a pošli ručně"
- **Text**: Výstup skriptu ukaž uživateli — je to hotový text ke zkopírování
- Pokud je `status: draft` ve frontmatter, nabídni aktualizaci na `status: sent` po odeslání

## Důležité

- Nikdy neposílej email automaticky — vždy jen připrav k ruční kontrole
- Přílohy: ověř, že soubory existují, než spustíš skript
- Pokud skript selže (Outlook není otevřený, špatná cesta), vypiš srozumitelnou chybu
