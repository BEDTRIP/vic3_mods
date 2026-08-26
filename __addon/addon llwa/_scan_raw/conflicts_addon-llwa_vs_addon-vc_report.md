# addon-llwa vs addon-vc — conflict report (key-level heuristic)

- addon-llwa root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods/__addon/addon llwa`
- addon-vc root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods/__addon/addon vc`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/ai_strategies — 3 duplicates
- `ai_strategy_great_reforms`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - addon-vc: `common/ai_strategies/zz_vc_kai_ai_strategies.txt`
- `ai_strategy_meiji_restoration`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - addon-vc: `common/ai_strategies/zz_vc_kai_ai_strategies.txt`
- `ai_strategy_tanzimat_reforms`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - addon-vc: `common/ai_strategies/zz_vc_kai_ai_strategies.txt`

### common/company_types — 3 duplicates
- `company_russian_american_company`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - addon-vc: `common/company_types/zz_vc_tgr_company_types.txt`
- `company_standard_oil`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - addon-vc: `common/company_types/zz_vc_ef_company_types.txt`
- `company_united_fruit`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - addon-vc: `common/company_types/zz_vc_tgr_company_types.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**