# PSC vs t&r — conflict report (key-level heuristic)

- PSC root: `/sessions/rcw-01yzgwbcydhw5vzewcycgo9p/mnt/Projects/vic3_mods_out/PSC`
- t&r root: `/sessions/rcw-01yzgwbcydhw5vzewcycgo9p/mnt/Projects/vic3_mods_out/TechRes+Kuromi/t&r`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/history/buildings — 1 duplicates
- `BUILDINGS`
  - PSC: `common/history/buildings/PSC_buildings.txt`
  - t&r: `common/history/buildings/elgar_opera.txt`
  - t&r: `common/history/buildings/manzoni_printing.txt`
  - t&r: `common/history/buildings/mr_buildings.txt`
  - t&r: `common/history/buildings/ztr_buildings.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - PSC: `common/history/global/PSC_global.txt`
  - t&r: `common/history/global/ztr_global.txt`

### common/on_actions — 1 duplicates
- `on_acquired_technology`
  - PSC: `common/on_actions/PSC_on_actions.txt`
  - t&r: `common/on_actions/ztr_on_actions.txt`

### common/production_methods — 3 duplicates
- `pm_arc_welded_buildings`
  - PSC: `common/production_methods/zz_PSC_construction.txt`
  - t&r: `common/production_methods/ztr_construction_production_methods.txt`
- `pm_iron_frame_buildings`
  - PSC: `common/production_methods/zz_PSC_construction.txt`
  - t&r: `common/production_methods/ztr_construction_production_methods.txt`
- `pm_steel_frame_buildings`
  - PSC: `common/production_methods/zz_PSC_construction.txt`
  - t&r: `common/production_methods/ztr_construction_production_methods.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**