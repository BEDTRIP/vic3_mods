# TGR vs MMRPA — conflict report (key-level heuristic)

- TGR root: `C:/Users/Andrey/Projects/vic3_mods_out/TheGreatRevision`
- MMRPA root: `C:/Users/Andrey/Projects/vic3_mods_out/MMRPA`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/production_methods — 10 duplicates
- `pm_diesel_trains`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`
- `pm_diesel_trains_principle_transport_3`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`
- `pm_early_trains`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`
- `pm_electric_trains`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`
- `pm_electric_trains_principle_transport_3`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`
- `pm_no_passenger_trains`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`
- `pm_steam_trains`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`
- `pm_steam_trains_principle_transport_3`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`
- `pm_steel_passenger_carriages`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`
- `pm_wooden_passenger_carriages`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
  - MMRPA: `common/production_methods/zzz_mrpa_railway.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**