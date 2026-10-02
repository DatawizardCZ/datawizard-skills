---
title: client-delivery
date: 2026-04-28
---

# client-delivery

Client work tools: discovery process, blindspot pass over a brief, client feedback, measurement setup before Google Ads, email preparation, and project scaffolding.

## Skills

- **client-discovery** — Guides AI through a structured client discovery process — from interviewing domain experts to creating formal process definitions, business analysis, compliance checks, and product design. Includes a 7-phase methodology with laptop handoff protocol and Mermaid diagram conventions.
- **send-email** — Prepares an email from a Markdown draft (YAML frontmatter), converts to HTML and opens in Outlook (macOS) or prints plain text. Signatures resolve per person: `~/.claude/email-signatures/` overrides bundled `signatures/` templates.
- **blindspot-pass**: Projde zadání, specifikaci nebo složku podkladů a najde unknown unknowns, tedy věci, na které by zadavatel sám nepomyslel.
- **feedback-from-message**: Převede zprávu s feedbackem (e-mail, přepis, Slack, screenshoty) na strukturovaný Markdown a interaktivní HTML prezentaci po bodech.
- **analytics-launch**: Checklist napojení měření na web klienta před spuštěním Google Ads (GTM, GA4, Consent Mode v2, konverze, Search Console) a agenturní struktura účtů.

> `ivo-cdo-advisor` se přesunul do osobního repa `karel-simek-skills` (2026-09-05).

## Scripts

- **scaffold-client.sh** — Scaffolds a full client workspace under `_KLIENTI/<client-name>/` with directory structure, template files, and `.claudeignore`.

## Installation

```
/plugin install client-delivery@datawizard-skills
```
