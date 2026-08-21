# PSC vs TheGreatRevision — conflict report (key-level heuristic)

- PSC root: `/sessions/rcw-01rp5i9hgkg5gzceyc7axcjg/mnt/Projects/vic3_mods_out/PSC`
- TheGreatRevision root: `/sessions/rcw-01rp5i9hgkg5gzceyc7axcjg/mnt/Projects/vic3_mods_out/TheGreatRevision`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/buildings — 1 duplicates
- `building_construction_sector`
  - PSC: `common/buildings/zz_PSC_construction.txt`
  - TheGreatRevision: `common/buildings/TGR_TRADE_construction.txt`

### common/history/buildings — 1 duplicates
- `BUILDINGS`
  - PSC: `common/history/buildings/PSC_buildings.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_austria_setup.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_net_setup.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_ottomans_setup.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_russia_setup.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_spain_setup.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - PSC: `common/history/global/PSC_global.txt`
  - TheGreatRevision: `common/history/global/TGR_LOANS_global.txt`
  - TheGreatRevision: `common/history/global/TGR_POLITICS_global.txt`
  - TheGreatRevision: `common/history/global/TGR_TAX_PANEL_global.txt`
  - TheGreatRevision: `common/history/global/TGR_TRADE_global.txt`
  - TheGreatRevision: `common/history/global/TGR_TRADE_obsessions.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**