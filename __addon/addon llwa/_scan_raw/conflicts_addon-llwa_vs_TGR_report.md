# addon-llwa vs TGR — conflict report (key-level heuristic)

- addon-llwa root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods/__addon/addon llwa`
- TGR root: `/sessions/rcw-01s7yfvp5sxa9mvgzb8skzmm/mnt/Projects/vic3_mods_out/TheGreatRevision`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/company_types — 10 duplicates
- `company_altos_hornos_de_vizcaya`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
- `company_dmc`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
- `company_hbc`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
- `company_lkab`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
- `company_mantero_seta`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
- `company_mantero_seta_two_sicilies`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
- `company_ong_lung_sheng_tea_company_heaven_kingdom`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
- `company_russian_american_company`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
- `company_sherkate_eslamiya`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`
- `company_united_fruit`
  - addon-llwa: `common/company_types/zz_llwa_companies_extensions.txt`
  - TGR: `common/company_types/TGR_TRADE_companies.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - addon-llwa: `common/history/global/zz_llwa_ef_stocks_init.txt`
  - TGR: `common/history/global/TGR_LOANS_global.txt`
  - TGR: `common/history/global/TGR_POLITICS_global.txt`
  - TGR: `common/history/global/TGR_TAX_PANEL_global.txt`
  - TGR: `common/history/global/TGR_TRADE_global.txt`
  - TGR: `common/history/global/TGR_TRADE_obsessions.txt`

### common/on_actions — 1 duplicates
- `on_yearly_pulse_country`
  - addon-llwa: `common/on_actions/zz_llwa_ef_on_actions.txt`
  - TGR: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_GER_UNIFICATION_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_POLITICS_gain_ideology.txt`
  - TGR: `common/on_actions/TGR_TRADE_code_on_actions.txt`

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