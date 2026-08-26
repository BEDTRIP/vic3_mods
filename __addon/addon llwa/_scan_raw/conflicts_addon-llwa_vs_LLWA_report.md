# addon-llwa vs LLWA — conflict report (key-level heuristic)

- addon-llwa root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods/__addon/addon llwa`
- LLWA root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods_out/llwa`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/ai_strategies — 9 duplicates
- `ai_strategy_conservative_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - LLWA: `common/ai_strategies/03_political_strategies.txt`
- `ai_strategy_egalitarian_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - LLWA: `common/ai_strategies/03_political_strategies.txt`
- `ai_strategy_great_reforms`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - LLWA: `common/ai_strategies/03_political_strategies.txt`
- `ai_strategy_maintain_mandate_of_heaven`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - LLWA: `common/ai_strategies/03_political_strategies.txt`
- `ai_strategy_meiji_restoration`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - LLWA: `common/ai_strategies/03_political_strategies.txt`
- `ai_strategy_nationalist_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - LLWA: `common/ai_strategies/03_political_strategies.txt`
- `ai_strategy_progressive_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - LLWA: `common/ai_strategies/03_political_strategies.txt`
- `ai_strategy_reactionary_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - LLWA: `common/ai_strategies/03_political_strategies.txt`
- `ai_strategy_tanzimat_reforms`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - LLWA: `common/ai_strategies/03_political_strategies.txt`

### common/production_methods — 10 duplicates
- `pm_diesel_trains`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`
- `pm_diesel_trains_principle_transport_3`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`
- `pm_early_trains`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`
- `pm_electric_trains`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`
- `pm_electric_trains_principle_transport_3`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`
- `pm_no_passenger_trains`
  - addon-llwa: `common/production_methods/zz_llwa_vc_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`
- `pm_steam_trains`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`
- `pm_steam_trains_principle_transport_3`
  - addon-llwa: `common/production_methods/zz_llwa_tgr_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`
- `pm_steel_passenger_carriages`
  - addon-llwa: `common/production_methods/zz_llwa_vc_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`
- `pm_wooden_passenger_carriages`
  - addon-llwa: `common/production_methods/zz_llwa_vc_rails.txt`
  - LLWA: `common/production_methods/LLWA_rails.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**