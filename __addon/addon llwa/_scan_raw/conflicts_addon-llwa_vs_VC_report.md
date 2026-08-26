# addon-llwa vs VC — conflict report (key-level heuristic)

- addon-llwa root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods/__addon/addon llwa`
- VC root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods_out/VC`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/ai_strategies — 3 duplicates
- `ai_strategy_great_reforms`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - VC: `common/ai_strategies/joi_political_strategies.txt`
- `ai_strategy_meiji_restoration`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - VC: `common/ai_strategies/joi_political_strategies.txt`
- `ai_strategy_tanzimat_reforms`
  - addon-llwa: `common/ai_strategies/03_political_strategies.txt`
  - addon-llwa: `common/ai_strategies/zzzz_llwa_kai_vc_reforms.txt`
  - VC: `common/ai_strategies/joi_political_strategies.txt`

### common/company_types — 21 duplicates
- `company_a_markwald_and_company`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_admiralty_rijkswerf`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_caribbean_petroleum`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_david_sassoon`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_franco_belge`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_great_indian_railway`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_kaiping_mining`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_mantetsu`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_massey_harris`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_orient_express`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_panama_company`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_prussian_state_railways`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_russian_american_company`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_siemens_and_halske`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_societe_francaise_charbonnages_du_tonkin`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_standard_oil`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_stt`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_suez_company`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_united_fruit`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_uragadockcompany`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`
- `company_yasuda`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - VC: `common/company_types/joi_companies.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - addon-llwa: `common/history/global/zz_llwa_ef_stocks_init.txt`
  - VC: `common/history/global/joi_global.txt`

### common/production_methods — 3 duplicates
- `pm_no_passenger_trains`
  - addon-llwa: `common/production_methods/zz_llwa_vc_rails.txt`
  - VC: `common/production_methods/joi_methods.txt`
- `pm_steel_passenger_carriages`
  - addon-llwa: `common/production_methods/zz_llwa_vc_rails.txt`
  - VC: `common/production_methods/joi_methods.txt`
- `pm_wooden_passenger_carriages`
  - addon-llwa: `common/production_methods/zz_llwa_vc_rails.txt`
  - VC: `common/production_methods/joi_methods.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**