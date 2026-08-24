# megapack vs TheGreatRevision — conflict report (key-level heuristic)

- megapack root: `/sessions/rcw-017nsstx3myg2nhohj7hh2ls/mnt/Projects/vic3_mods/__megapacks/megapack`
- TheGreatRevision root: `/sessions/rcw-017nsstx3myg2nhohj7hh2ls/mnt/Projects/vic3_mods_out/TheGreatRevision`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/ai_strategies — 1 duplicates
- `ai_strategy_resource_expansion`
  - megapack: `common/ai_strategies/zz_tr_kai_tgr_ai_strategies.txt`
  - TheGreatRevision: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`

### common/buildings — 3 duplicates
- `building_automotive_industry`
  - megapack: `common/buildings/zz_tr_kai_tgr_buildings.txt`
  - megapack: `common/buildings/zztr_vanilla_buildings.txt`
  - megapack: `common/buildings/zzzz_megapack_tgr_industry_groups.txt`
  - TheGreatRevision: `common/buildings/TGR_POLITICS_industry.txt`
- `building_construction_sector`
  - megapack: `common/buildings/zz_pb_ef_construction_sector.txt`
  - TheGreatRevision: `common/buildings/TGR_TRADE_construction.txt`
- `building_synthetics_plant`
  - megapack: `common/buildings/zz_tr_kai_tgr_buildings.txt`
  - megapack: `common/buildings/zztr_vanilla_buildings.txt`
  - megapack: `common/buildings/zzzz_megapack_tgr_industry_groups.txt`
  - TheGreatRevision: `common/buildings/TGR_POLITICS_industry.txt`

### common/defines — 1 duplicates
- `NEconomy`
  - megapack: `common/defines/ef_tgr_defines.txt`
  - TheGreatRevision: `common/defines/TGR_TRADE_defines.txt`

### common/diplomatic_actions — 1 duplicates
- `force_regime_change`
  - megapack: `common/diplomatic_actions/zz_pbe_tgr_force_regime_change.txt`
  - TheGreatRevision: `common/diplomatic_actions/TGR_ADJUSTMENTS_power_bloc_force_regime_change.txt`

### common/goods — 3 duplicates
- `aeroplanes`
  - megapack: `common/goods/zz_tr_kai_tgr_goods.txt`
  - TheGreatRevision: `common/goods/TGR_TRADE_goods.txt`
- `automobiles`
  - megapack: `common/goods/zz_tr_kai_tgr_goods.txt`
  - TheGreatRevision: `common/goods/TGR_TRADE_goods.txt`
- `clothes`
  - megapack: `common/goods/zz_tr_kai_tgr_goods.txt`
  - TheGreatRevision: `common/goods/TGR_TRADE_goods.txt`

### common/history/buildings — 1 duplicates
- `BUILDINGS`
  - megapack: `common/history/buildings/00_ef_building.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_austria_setup.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_net_setup.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_ottomans_setup.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_russia_setup.txt`
  - TheGreatRevision: `common/history/buildings/TGR_TRADE_spain_setup.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - megapack: `common/history/global/zz_ef_mr_stocks_init.txt`
  - megapack: `common/history/global/zzzz_ef_tr_fix_init.txt`
  - TheGreatRevision: `common/history/global/TGR_LOANS_global.txt`
  - TheGreatRevision: `common/history/global/TGR_POLITICS_global.txt`
  - TheGreatRevision: `common/history/global/TGR_TAX_PANEL_global.txt`
  - TheGreatRevision: `common/history/global/TGR_TRADE_global.txt`
  - TheGreatRevision: `common/history/global/TGR_TRADE_obsessions.txt`

### common/journal_entries — 1 duplicates
- `je_international_loans`
  - megapack: `common/journal_entries/zz_disable_tgr_international_loans.txt`
  - TheGreatRevision: `common/journal_entries/TGR_LOANS_panel.txt`

### common/laws — 4 duplicates
- `law_colonial_exploitation`
  - megapack: `common/laws/zz_tr_kai_tgr_laws.txt`
  - TheGreatRevision: `common/laws/TGR_POLITICS_colonial_affairs.txt`
- `law_colonial_resettlement`
  - megapack: `common/laws/zz_tr_kai_tgr_laws.txt`
  - TheGreatRevision: `common/laws/TGR_POLITICS_colonial_affairs.txt`
- `law_extraction_economy`
  - megapack: `common/laws/zz_tr_kai_tgr_laws.txt`
  - TheGreatRevision: `common/laws/TGR_POLITICS_economic_system.txt`
- `law_frontier_colonization`
  - megapack: `common/laws/zz_tr_kai_tgr_laws.txt`
  - TheGreatRevision: `common/laws/TGR_POLITICS_colonial_affairs.txt`

### common/on_actions — 2 duplicates
- `on_monthly_pulse_country`
  - megapack: `common/on_actions/zz_pb_ef_psc_overbuilt_off.txt`
  - TheGreatRevision: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TheGreatRevision: `common/on_actions/TGR_GER_UNIFICATION_code_on_actions.txt`
  - TheGreatRevision: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
- `on_yearly_pulse_country`
  - megapack: `common/on_actions/zz_ef_mr_on_actions.txt`
  - megapack: `common/on_actions/zzzz_ef_tr_fix_on_actions.txt`
  - TheGreatRevision: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TheGreatRevision: `common/on_actions/TGR_GER_UNIFICATION_code_on_actions.txt`
  - TheGreatRevision: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
  - TheGreatRevision: `common/on_actions/TGR_POLITICS_gain_ideology.txt`
  - TheGreatRevision: `common/on_actions/TGR_TRADE_code_on_actions.txt`

### common/production_methods — 9 duplicates
- `pm_basic_port`
  - megapack: `common/production_methods/zz_tr_kai_tgr_production_methods.txt`
  - TheGreatRevision: `common/production_methods/TGR_TRADE_private_infrastructure_ports.txt`
- `pm_diesel_trains`
  - megapack: `common/production_methods/zz_tr_kai_tgr_production_methods.txt`
  - TheGreatRevision: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_diesel_trains_principle_transport_3`
  - megapack: `common/production_methods/zz_tr_kai_tgr_production_methods.txt`
  - TheGreatRevision: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_electric_trains`
  - megapack: `common/production_methods/zz_tr_kai_tgr_production_methods.txt`
  - TheGreatRevision: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_electric_trains_principle_transport_3`
  - megapack: `common/production_methods/zz_tr_kai_tgr_production_methods.txt`
  - TheGreatRevision: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_industrial_port`
  - megapack: `common/production_methods/zz_tr_kai_tgr_production_methods.txt`
  - TheGreatRevision: `common/production_methods/TGR_TRADE_private_infrastructure_ports.txt`
- `pm_modern_port`
  - megapack: `common/production_methods/zz_tr_kai_tgr_production_methods.txt`
  - TheGreatRevision: `common/production_methods/TGR_TRADE_private_infrastructure_ports.txt`
- `pm_steam_trains`
  - megapack: `common/production_methods/zz_tr_kai_tgr_production_methods.txt`
  - TheGreatRevision: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`
- `pm_steam_trains_principle_transport_3`
  - megapack: `common/production_methods/zz_tr_kai_tgr_production_methods.txt`
  - TheGreatRevision: `common/production_methods/TGR_TRADE_private_infrastructure_railway.txt`

### common/scripted_buttons — 8 duplicates
- `tgr_loans_button_1`
  - megapack: `common/scripted_buttons/zz_disable_tgr_international_loans_buttons.txt`
  - TheGreatRevision: `common/scripted_buttons/TGR_LOANS_buttons.txt`
- `tgr_loans_button_2`
  - megapack: `common/scripted_buttons/zz_disable_tgr_international_loans_buttons.txt`
  - TheGreatRevision: `common/scripted_buttons/TGR_LOANS_buttons.txt`
- `tgr_loans_button_3`
  - megapack: `common/scripted_buttons/zz_disable_tgr_international_loans_buttons.txt`
  - TheGreatRevision: `common/scripted_buttons/TGR_LOANS_buttons.txt`
- `tgr_loans_button_4`
  - megapack: `common/scripted_buttons/zz_disable_tgr_international_loans_buttons.txt`
  - TheGreatRevision: `common/scripted_buttons/TGR_LOANS_buttons.txt`
- `tgr_loans_button_5`
  - megapack: `common/scripted_buttons/zz_disable_tgr_international_loans_buttons.txt`
  - TheGreatRevision: `common/scripted_buttons/TGR_LOANS_buttons.txt`
- `tgr_loans_button_6`
  - megapack: `common/scripted_buttons/zz_disable_tgr_international_loans_buttons.txt`
  - TheGreatRevision: `common/scripted_buttons/TGR_LOANS_buttons.txt`
- `tgr_loans_button_7`
  - megapack: `common/scripted_buttons/zz_disable_tgr_international_loans_buttons.txt`
  - TheGreatRevision: `common/scripted_buttons/TGR_LOANS_buttons.txt`
- `tgr_loans_button_8`
  - megapack: `common/scripted_buttons/zz_disable_tgr_international_loans_buttons.txt`
  - TheGreatRevision: `common/scripted_buttons/TGR_LOANS_buttons.txt`

### common/static_modifiers — 1 duplicates
- `base_values`
  - megapack: `common/static_modifiers/ef_tgr_base_values_compat.txt`
  - TheGreatRevision: `common/static_modifiers/TGR_LOANS_code_static_modifiers.txt`
  - TheGreatRevision: `common/static_modifiers/TGR_POLITICS_code_static_modifiers.txt`
  - TheGreatRevision: `common/static_modifiers/TGR_TRADE_code_static_modifiers.txt`

### common/technology/technologies — 7 duplicates
- `banking`
  - megapack: `common/technology/technologies/ef_tgr_technology_compat.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_LOANS_society.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_TRADE_society.txt`
- `central_banking`
  - megapack: `common/technology/technologies/ef_tgr_technology_compat.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_LOANS_society.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_TRADE_society.txt`
- `corporate_charters`
  - megapack: `common/technology/technologies/ef_tgr_technology_compat.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_TRADE_society.txt`
- `investment_banks`
  - megapack: `common/technology/technologies/ef_tgr_technology_compat.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_TRADE_society.txt`
- `joint_stock_companies`
  - megapack: `common/technology/technologies/ef_tgr_technology_compat.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_TRADE_society.txt`
- `malaria_prevention`
  - megapack: `common/technology/technologies/zz_tr_kai_tgr_technologies.txt`
  - megapack: `common/technology/technologies/zzz_compatch_mr_society.txt`
  - megapack: `common/technology/technologies/zzzz_megapack_malaria_prevention.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_POLITICS_society.txt`
- `mutual_funds`
  - megapack: `common/technology/technologies/ef_tgr_technology_compat.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_LOANS_society.txt`
  - TheGreatRevision: `common/technology/technologies/TGR_TRADE_society.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**