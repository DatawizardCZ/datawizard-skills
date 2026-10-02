---
title: Datawizard Skills
date: 2026-04-28
---

# Datawizard Skills

Monorepo s tematickými pluginy pro **Claude Code**, **Cursor** a další AI nástroje podporující formát `SKILL.md`.

Repo: [github.com/Karyzard/datawizard-skills](https://github.com/Karyzard/datawizard-skills)

## Pluginy

| Plugin | Účel |
|---|---|
| [datawizard-core](plugins/datawizard-core/) | Workflow `ship` (commit + push) + globální pravidla |
| [project-os](plugins/project-os/) | Standard projektových rep `project-*`: metodika, založení, migrace, delivery itemy, audit; šablona repa uvnitř |
| [content-tools](plugins/content-tools/) | Konverze dokumentů (email, PDF, přepisy schůzek) a generování obrázků |
| [client-delivery](plugins/client-delivery/) | Klientská práce — discovery, příprava emailů, scaffolding |
| [product-design](plugins/product-design/) | Design Thinking pipeline, prototyping, UI/UX intelligence |
| [business-advice](plugins/business-advice/) | Konzultantské persony (Hormozi, Inizio) |
| [wiki-tools](plugins/wiki-tools/) | Markdown wiki — ingest, lint, query |
| [web-conversion](plugins/web-conversion/) | Konverze web prototypů do produkčních stacků, scaffolding z šablon |
| [web-motion](plugins/web-motion/) | Animovaná demo okna (terminál, IDE, blueprint, CRT) + hook-switcher pro hero copy |
| [knowledge-capture](plugins/knowledge-capture/) | Sběr znalostí z externích zdrojů — přepisy YouTube playlistů/kanálů, průvodce web research nástroji (zdarma vs. placené) |
| [process-mapping](plugins/process-mapping/) | Mapování procesů od rámce po schválené to-be, procesní mapy z jednoho popisu (animovaný HTML výkres s krokováním, SVG, Figma s animací, Mermaid) a znalostní báze typů diagramů, notace a nástrojů |

> Osobní pluginy (talent-coaching, writing-style, start/wrap session workflow, ivo-cdo-advisor) se přesunuly do samostatného soukromého repa `karel-simek-skills` (2026-09-05). Tohle repo obsahuje jen skilly použitelné kýmkoliv z Datawizardu.

## Instalace pro Claude Code

### 1. Přidej marketplace (jednorázově)

```
/plugin marketplace add DatawizardCZ/datawizard-skills
```

> Marketplace může být i soukromé repo. Claude Code použije tvoje git přihlášení k GitHubu (ověřeno 2026-10-02).

Po úspěchu uvidíš: `Successfully added marketplace: datawizard-skills`

### 2. Nainstaluj jednotlivé pluginy

```
/plugin install datawizard-core@datawizard-skills
/plugin install project-os@datawizard-skills
/plugin install content-tools@datawizard-skills
/plugin install client-delivery@datawizard-skills
/plugin install product-design@datawizard-skills
/plugin install business-advice@datawizard-skills
/plugin install wiki-tools@datawizard-skills
/plugin install web-conversion@datawizard-skills
/plugin install web-motion@datawizard-skills
/plugin install knowledge-capture@datawizard-skills
/plugin install process-mapping@datawizard-skills
```

Nainstaluj jen ty, které potřebuješ.

### 3. Použití

Skills se pak buď **automaticky aktivují** podle popisu v dané situaci, nebo je můžeš zavolat jako slash command:

```
/ship          # commit + push
```

Skill list zobrazíš příkazem `/plugin`.

### Aktualizace

Pluginy nemají pevné číslo verze, Claude Code je verzuje podle commitu. Každý merge do `main` je tedy nová verze. S `autoUpdate` se stáhne sama, ručně:

```
/plugin marketplace update datawizard-skills
/plugin update <plugin-name>@datawizard-skills
```

Do `plugin.json` ani `marketplace.json` proto nepiš `version`. S pevným číslem by Claude Code držel starou kopii z cache, dokud se číslo nezmění.

### Odinstalace

```
/plugin uninstall <plugin-name>@datawizard-skills
/plugin marketplace remove datawizard-skills
```

## Instalace pro Cursor

Cursor zatím plugin systém nemá — používá `~/.cursor/skills/` jako složku. Skills sdílíš symlinkem:

```bash
# Pro celý plugin (např. content-tools)
ln -s /cesta/k/datawizard-skills/plugins/content-tools/skills ~/.cursor/skills/content-tools
```

Po naklonování repa nastav cestu podle vlastního umístění:

```bash
git clone https://github.com/Karyzard/datawizard-skills.git ~/dev/datawizard-skills
ln -s ~/dev/datawizard-skills/plugins/content-tools/skills ~/.cursor/skills/content-tools
```

## Pro vývoj a přispívání

### Konvence

- Každý plugin žije v `plugins/<name>/`
- Plugin manifest: `plugins/<name>/.claude-plugin/plugin.json`
- Skills: `plugins/<name>/skills/<skill-name>/SKILL.md`
- Marketplace manifest (root): `.claude-plugin/marketplace.json`
- Všechny `SKILL.md` mají YAML frontmatter s `name:` a `description:`

### Přidání nového skillu

1. Vyber plugin podle tématu (nebo založ nový)
2. Vytvoř složku `plugins/<plugin>/skills/<new-skill>/`
3. Napiš `SKILL.md` s frontmatter:
   ```yaml
   ---
   name: new-skill
   description: Stručně co skill dělá a kdy ho použít. Tento popis Claude používá pro auto-aktivaci.
   ---
   ```
4. Pokud přidáváš celý nový plugin, přidej ho do `.claude-plugin/marketplace.json`
5. Commit + push na main

### Vzorový plugin

Podívej se na [`plugins/datawizard-core/`](plugins/datawizard-core/) — nejjednodušší příklad se skillem a `rules/`.

### Vzorový komplexní plugin

[`plugins/product-design/`](plugins/product-design/) — 12 skills, většina s `references/` podadresářem pro hlubší dokumentaci.

## Troubleshooting

**`/plugin marketplace add` selhává s SSH chybou:**
Repo musí být **veřejné**. Privátní repos nejdou (Claude Code 2026).

**`Marketplace file not found`:**
Repo nemá `.claude-plugin/marketplace.json` v rootu. Zkontroluj že existuje.

**Plugin se nainstaluje ale skill nefunguje:**
Restartuj Claude Code session (`/clear` nestačí — opravdu zavři a otevři okno).

**Cursor nevidí skill:**
Cursor neumí pluginy — musíš použít symlink do `~/.cursor/skills/`.
