---
title: Mermaid výstup a ruční vzory
date: 2026-10-01
---

# Mermaid

Mermaid je nejrychlejší výstup: žije přímo v markdownu, GitHub ho vykreslí a nepotřebuje žádný nástroj. Animaci ani přesné rozložení nemá; pruhy rolí jsou jen přibližné (`subgraph`).

## Co generuje pmap.py

`pmap.py mermaid "<spec>"` vyrobí `<proces>.mermaid.md` se třemi částmi: tok s pruhy rolí, diagram stavů a seznam otevřených a vyřešených otázek. Zkrácená ukázka ze vzoru:

```mermaid
flowchart LR
  subgraph lane_ucetni["Účetní"]
    direction LR
    n_s1(["Přijme fakturu"])
    n_s3["Doplní středisko"]
  end
  subgraph lane_system["Systém"]
    direction LR
    n_k[["Kontroly faktury ??"]]
    n_s6{"Nad 50 000 Kč? ??"}
  end
  n_k -.->|"opravit údaje"| n_s3
  n_s6 -.->|"do limitu"| n_s8
  classDef q stroke:#d97706,stroke-width:2px
  class n_k,n_s6 q
```

- **Tvary uzlů podle typu kroku:** úloha `["…"]`, rozhodnutí `{"…"}`, start a konec `(["…"])`, kontroly `[["…"]]`, průběžná role `[/"…"/]`.
- **Šipky:** smyčka a alternativa jsou čárkované `-.->`.
- **Otázky** `??` mají jemný oranžový rámeček (třída `q`). Je to jediné barevné značení. Jinak výstup drží konvence `client-delivery:client-discovery` (popisky v `["…"]`, rozhodnutí jako otázka, bez dalšího stylování).
- **Směr je `LR`** (zleva doprava) kvůli shodě s HTML výkresem; `client-discovery` používá `TD`. Pro dlouhý úzký proces v dokumentaci můžeš `LR` ručně přepsat na `TD`.
- **Speciální znaky** (`"`, `<`, `>`, `&`, `#`) se zapisují jako entity Mermaid (`#quot;`, `#lt;`, `#gt;`, `#amp;`, `#35;`), takže se zobrazí doslova.

## Ruční vzory

Tok s pruhy rolí (když nestačí generovaný, třeba pro složité větvení):

```mermaid
flowchart LR
  subgraph lane_a["Obchod"]
    a1["Přijme poptávku"] --> a2{"Standardní zakázka?"}
  end
  subgraph lane_b["Výroba"]
    b1["Ověří kapacitu"]
  end
  a2 -->|"ano"| a3["Pošle nabídku"]
  a2 -->|"ne"| b1
  b1 --> a3
```

Stavy objektu:

```mermaid
stateDiagram-v2
  state "Nová" as nova
  state "Ke schválení" as ke_schvaleni
  state "Schválená" as schvalena
  [*] --> nova
  nova --> ke_schvaleni
  ke_schvaleni --> schvalena
  ke_schvaleni --> nova : vrácená
  schvalena --> [*]
```

Komunikace mezi systémy (sekvenční diagram; plugin ho negeneruje, piš ručně):

```mermaid
sequenceDiagram
  participant W as Webová aplikace
  participant B as Backend
  participant E as ERP
  W->>B: odešle objednávku
  B->>E: založí doklad
  E-->>B: číslo dokladu
  B-->>W: potvrzení
  E--xB: chyba (sklad nedostupný)
  B-->>W: upozornění pro uživatele
```

## Ověření

- Lokálně: `npx -y @mermaid-js/mermaid-cli@12.0.0 -i "<proces>.mermaid.md" -o "<proces>.svg"`. Verze je připnutá. První běh stahuje prohlížeč a trvá několik minut, spouštěj ho s delším časovým limitem nebo na pozadí.
- Klientské diagramy nevkládej do mermaid.live ani do jiných online editorů se sdílením přes odkaz: diagram je zakódovaný přímo v URL.
