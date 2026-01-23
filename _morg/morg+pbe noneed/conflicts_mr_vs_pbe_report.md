# Morgenrote vs PBE — conflict report (key-level heuristic)

- Morgenrote root: `C:/Users/Andrey/Projects/vic3_mods_out/Morgenrote`
- PBE root: `C:/Users/Andrey/Projects/vic3_mods_out/PowerBlocksExpanded`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/on_actions — 2 duplicates
- `on_monthly_pulse`
  - Morgenrote: `common/on_actions/mr_on_actions.txt`
  - PBE: `common/on_actions/kates_power_bloc_on_actions.txt`
- `on_monthly_pulse_country`
  - Morgenrote: `common/on_actions/academics_on_actions.txt`
  - Morgenrote: `common/on_actions/agassiz_on_actions.txt`
  - Morgenrote: `common/on_actions/ai_on_actions.txt`
  - Morgenrote: `common/on_actions/artists_on_actions.txt`
  - Morgenrote: `common/on_actions/curtiss_on_actions.txt`
  - PBE: `common/on_actions/kates_power_bloc_on_actions.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**