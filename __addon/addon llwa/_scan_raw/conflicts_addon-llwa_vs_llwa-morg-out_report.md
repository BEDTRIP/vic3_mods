# addon-llwa vs llwa+morg out — conflict report (key-level heuristic)

- addon-llwa root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods/__addon/addon llwa`
- llwa+morg out root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods/_llwa/llwa+morg out`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/buildings — 3 duplicates
- `LLWA_building_airway`
  - addon-llwa: `common/buildings/zz_llwa_ef_buildings_inject.txt`
  - llwa+morg out: `common/buildings/zz_LLWAMR_buildings.txt`
- `building_airport`
  - addon-llwa: `common/buildings/zz_llwa_morg_ef_buildings.txt`
  - llwa+morg out: `common/buildings/zz_LLWAMR_buildings.txt`
- `building_railway`
  - addon-llwa: `common/buildings/zz_llwa_morg_ef_buildings.txt`
  - llwa+morg out: `common/buildings/zz_LLWAMR_buildings.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**