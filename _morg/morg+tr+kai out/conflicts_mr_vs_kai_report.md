# Morgenrote vs KAI — conflict report (key-level heuristic)

- Morgenrote root: `C:/Users/Andrey/Projects/vic3_mods_out/Morgenrote`
- KAI root: `C:/Users/Andrey/Projects/vic3_mods_out/TechRes+Kuromi/kai`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/buildings — 1 duplicates
- `building_government_administration`
  - Morgenrote: `common/buildings/mr_vanilla_buildings_replace.txt`
  - KAI: `common/buildings/kai_buildings.txt`

### common/technology/technologies — 1 duplicates
- `atmospheric_engine`
  - Morgenrote: `common/technology/technologies/a_vanilla_production_technologies.txt`
  - KAI: `common/technology/technologies/kai_technologies.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**