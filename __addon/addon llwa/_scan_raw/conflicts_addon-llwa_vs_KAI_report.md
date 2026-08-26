# addon-llwa vs KAI — conflict report (key-level heuristic)

- addon-llwa root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods/__addon/addon llwa`
- KAI root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods_out/TechRes+Kuromi/kai`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/ai_strategies — 8 duplicates
- `ai_strategy_conservative_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
- `ai_strategy_egalitarian_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
- `ai_strategy_great_reforms`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
- `ai_strategy_meiji_restoration`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
- `ai_strategy_nationalist_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
- `ai_strategy_progressive_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
- `ai_strategy_reactionary_agenda`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzz_llwa_kai_political_strategies.txt`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
- `ai_strategy_tanzimat_reforms`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**