# PSC vs kai — conflict report (key-level heuristic)

- PSC root: `/sessions/rcw-01yzgwbcydhw5vzewcycgo9p/mnt/Projects/vic3_mods_out/PSC`
- kai root: `/sessions/rcw-01yzgwbcydhw5vzewcycgo9p/mnt/Projects/vic3_mods_out/TechRes+Kuromi/kai`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/buildings — 1 duplicates
- `building_construction_sector`
  - PSC: `common/buildings/zz_PSC_construction.txt`
  - kai: `common/buildings/kai_buildings.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**