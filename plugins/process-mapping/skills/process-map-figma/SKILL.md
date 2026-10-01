---
name: process-map-figma
description: Postaví z popisu procesu (<proces>.process.toml) swimlane procesní mapu ve Figmě a přidá animaci (kroky naskakují, šipky se kreslí, rámeček jde po stavech). Když motion není pro účet zapnutý, postaví statickou mapu. Používá Figma MCP a skilly figma-use a figma-use-motion. Použij, když uživatel chce procesní mapu ve Figmě, animovanou mapu pro prezentaci, nebo ji chce dál upravovat s designérem. Triggeruj na „procesní mapa ve Figmě“, „swimlane ve Figmě“, „animovaný proces ve Figmě“, „motion procesní mapa“. Komunikuj česky.
---

# Procesní mapa ve Figmě

Geometrii nepočítá Figma, počítá ji `pmap.py`. Figma i HTML výkres tak mají stejné rozložení. Kód pro `use_figma` vyrábí `pmap.py figma`: data vloží jako JSON, takže text z popisu procesu se do JavaScriptu nikdy neskládá ručně.

## Postup

1. **Načti skilly.** Načti `figma:figma-use` a `figma:figma-use-motion`; před `create_new_file` ještě `figma:figma-create-new-file`. U každého `use_figma` předávej `skillNames: "figma-use,figma-use-motion"`.
2. **Zkontroluj spec.**
   ```bash
   P="${CLAUDE_PLUGIN_ROOT}/skills/process-mapping/scripts/pmap.py"
   python3 "$P" check "<spec>"
   ```
   Bez `${CLAUDE_PLUGIN_ROOT}` (Cursor) použij `"<SKILL_DIR>/../process-mapping/scripts/pmap.py"`.
3. **Vyber soubor.**
   - Buď existující soubor od uživatele, nebo nový přes `create_new_file`.
   - Plán vyber podle `whoami`. Když má uživatel víc týmů, zeptej se.
   - Klientská mapa patří jen do týmu nebo projektu klienta s omezeným sdílením.
4. **Ověř motion API.** Zavolej `figma.motion.figmaAnimationStyles()` v `use_figma`. Když vrátí „not a supported API“, motion není pro účet zapnutý: postav jen statickou mapu (krok 5), krok 6 vynech a řekni to uživateli.
5. **Postav mapu.**
   ```bash
   python3 "$P" figma "<spec>" --part build -o "<scratchpad>/<proces>.figma-build.js"
   ```
   Obsah souboru pošli beze změny jako `code` do `use_figma`. Vrácený objekt `ids` ulož jako JSON do `<scratchpad>/<proces>.ids.json`.
6. **Přidej animaci.**
   ```bash
   python3 "$P" figma "<spec>" --part motion --ids "<scratchpad>/<proces>.ids.json" -o "<scratchpad>/<proces>.figma-motion.js"
   ```
   Pošli do `use_figma`. Zkontroluj `warnings` ve výsledku.
7. **Ověř animaci.**
   - Spusť `export_video` na `frameId` (`constraint: {type: "WIDTH", value: 960}`, `fps: 5`, `quality: "low"`).
   - MP4 stáhni do scratchpadu a vytáhni 4–6 snímků: `ffmpeg -ss <t> -i anim.mp4 -frames:v 1 f_<t>.png`. Časy vyber podle layoutu (start, kontroly, smyčka, rozhodnutí, konec).
   - Video i snímky po kontrole smaž. Bez `ffmpeg` export vynech.
8. **Předej odkaz.** Dej uživateli `https://www.figma.com/design/<fileKey>?node-id=<frameId s pomlčkou>` a řekni, že animace se pouští přehráním časové osy rámce. Klíč souboru ani odkaz nezapisuj do commitovaných souborů.

## Pasti (ověřené)

- Motion API je za feature flagem; při „not a supported API“ hned skonči, nezkoušej znovu.
- `PATH_TRIM_END` nejde na čárkovaných čarách; smyčka a alternativa se proto jen plynule objeví.
- Neanimuj rámec na nejvyšší úrovni stránky, jen jeho potomky.
- Statický návrh je finální stav a keyframes animují k němu. Rámeček stavů proto stojí na posledním stavu a animace ho posouvá z prvního (posun je relativní). Snímek obrazovky tak ukazuje celou mapu.
- Písmo Inter, styl „Semi Bold“ s mezerou. Znak ↺ Inter nemá, ve Figmě se nepoužívá.
- Kód pro `use_figma` má limit 50 000 znaků; `pmap.py figma` delší kód odmítne. Vzor (9 kroků) má asi 17 000 znaků. Větší proces rozděl na podprocesy.
- Keyframes jedné stopy musí jít časově po sobě; `add-motion.js` je proto posune o 0,01 s.
- Figma MCP se přihlašuje přes OAuth. Tokeny ani klíče do chatu nevkládej.
