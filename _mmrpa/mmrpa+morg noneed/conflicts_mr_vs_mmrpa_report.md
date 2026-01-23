# Morgenrote vs MMRPA — conflict report (key-level heuristic)

- Morgenrote root: `C:/Users/Andrey/Projects/vic3_mods_out/Morgenrote`
- MMRPA root: `C:/Users/Andrey/Projects/vic3_mods_out/MMRPA`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/buildings — 1 duplicates
- `building_railway`
  - Morgenrote: `common/buildings/mr_vanilla_buildings_replace.txt`
  - MMRPA: `common/buildings/zzz_mrpa_railway.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**