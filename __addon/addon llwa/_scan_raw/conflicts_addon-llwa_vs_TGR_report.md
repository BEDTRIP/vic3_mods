# addon-llwa vs TGR — conflict report (key-level heuristic)

- addon-llwa root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods/__addon/addon llwa`
- TGR root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods_out/TheGreatRevision`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/production_methods — 10 duplicates
- `pm_diesel_trains`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_diesel_trains_principle_transport_3`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_early_trains`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_electric_trains`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_electric_trains_principle_transport_3`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_no_passenger_trains`
  - addon-llwa: `common/production_methods/zz_llwa_vc_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_steam_trains`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_steam_trains_principle_transport_3`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_steel_passenger_carriages`
  - addon-llwa: `common/production_methods/zz_llwa_vc_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_wooden_passenger_carriages`
  - addon-llwa: `common/production_methods/zz_llwa_vc_rails.txt`
  - TGR: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**