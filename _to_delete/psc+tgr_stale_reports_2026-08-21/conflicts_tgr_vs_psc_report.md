# TGR vs PSC — conflict report (key-level heuristic)

- TGR root: `C:/Users/Andrey/Projects/vic3_mods_out/TheGreatRevision`
- PSC root: `C:/Users/Andrey/Projects/vic3_mods_out/PSC`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/buildings — 1 duplicates
- `building_construction_sector`
  - TGR: `common/buildings/TGR_TRADE_construction.txt`
  - PSC: `common/buildings/zz_PSC_construction.txt`

### common/history/buildings — 1 duplicates
- `BUILDINGS`
  - TGR: `common/history/buildings/TGR_TRADE_company_buildings_setup.txt`
  - TGR: `common/history/buildings/TGR_TRADE_net_setup.txt`
  - TGR: `common/history/buildings/TGR_TRADE_russia_setup.txt`
  - TGR: `common/history/buildings/TGR_TRADE_trade_center_setup.txt`
  - TGR: `common/history/buildings/TGR_TRADE_uk_setup.txt`
  - PSC: `common/history/buildings/PSC_buildings.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - TGR: `common/history/global/TGR_LOANS_global.txt`
  - TGR: `common/history/global/TGR_POLITICS_global.txt`
  - TGR: `common/history/global/TGR_TAX_PANEL_global.txt`
  - TGR: `common/history/global/TGR_TRADE_global.txt`
  - TGR: `common/history/global/TGR_TRADE_obsessions.txt`
  - PSC: `common/history/global/PSC_global.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**