# Morgenrote vs PSC — conflict report (key-level heuristic)

> Regenerated 2026-08-21 against Morgenrote 2.8.3e / PSC 1.3.7 (game 1.13.10).
> Verdict: no conflict — see README.md for the full checklist.

- Morgenrote root: `C:/Users/Andrey/Projects/vic3_mods_out/Morgenrote`
- PSC root: `C:/Users/Andrey/Projects/vic3_mods_out/PSC`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/history/buildings — 1 duplicates
- `BUILDINGS`
  - Morgenrote: `common/history/buildings/elgar_opera.txt`
  - Morgenrote: `common/history/buildings/gaudi_monument.txt`
  - Morgenrote: `common/history/buildings/manzoni_printing.txt`
  - Morgenrote: `common/history/buildings/mr_buildings.txt`
  - Morgenrote: `common/history/buildings/verrier_observatory.txt`
  - PSC: `common/history/buildings/PSC_buildings.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - Morgenrote: `common/history/global/0_mr_cmf_initiation.txt`
  - Morgenrote: `common/history/global/mr_global.txt`
  - PSC: `common/history/global/PSC_global.txt`

### common/on_actions — 3 duplicates
- `on_acquired_technology`
  - Morgenrote: `common/on_actions/mr_arts_artists_on_actions.txt`
  - Morgenrote: `common/on_actions/mr_arts_elgar_on_actions.txt`
  - Morgenrote: `common/on_actions/mr_arts_gaudi_on_actions.txt`
  - Morgenrote: `common/on_actions/mr_general_rapanui_on_actions.txt`
  - Morgenrote: `common/on_actions/mr_science_agassiz_on_actions.txt`
  - PSC: `common/on_actions/PSC_on_actions.txt`
- `on_building_built`
  - Morgenrote: `common/on_actions/mr_arts_artists_on_actions.txt`
  - Morgenrote: `common/on_actions/mr_arts_klimt_on_actions.txt`
  - Morgenrote: `common/on_actions/mr_arts_manzoni_on_actions.txt`
  - Morgenrote: `common/on_actions/mr_science_agassiz_on_actions.txt`
  - Morgenrote: `common/on_actions/mr_science_andersson_on_actions.txt`
  - PSC: `common/on_actions/PSC_on_actions.txt`
- `on_monthly_pulse`
  - Morgenrote: `common/on_actions/mr_on_actions.txt`
  - PSC: `common/on_actions/PSC_on_actions.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**