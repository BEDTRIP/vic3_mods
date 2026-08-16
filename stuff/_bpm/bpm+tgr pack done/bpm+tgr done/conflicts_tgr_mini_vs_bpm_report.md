# TGR_mini vs BPM — conflict report (key-level heuristic)

- TGR_mini root: `C:/Users/Andrey/Projects/vic3_mods_out/TGR mini`
- BPM root: `C:/Users/Andrey/Projects/vic3_mods_out/BPM`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/decisions — 2 duplicates
- `canada_unite_can`
  - TGR_mini: `common/decisions/canada_australia.txt`
  - BPM: `common/decisions/zz_bnap_decisions_override.txt`
- `canada_unite_gbr`
  - TGR_mini: `common/decisions/canada_australia.txt`
  - BPM: `common/decisions/zz_bnap_decisions_override.txt`

### common/defines — 1 duplicates
- `NAI`
  - TGR_mini: `common/defines/TGR_ADJUSTMENTS_ai.txt`
  - TGR_mini: `common/defines/TGR_TAX_PANEL_defines.txt`
  - TGR_mini: `common/defines/TGR_TRADE_ai.txt`
  - BPM: `common/defines/BPM_defines.txt`

### common/history/countries — 1 duplicates
- `COUNTRIES`
  - TGR_mini: `common/history/countries/aus - austria.txt`
  - TGR_mini: `common/history/countries/brz - brazil.txt`
  - TGR_mini: `common/history/countries/chi - china.txt`
  - TGR_mini: `common/history/countries/fra - france.txt`
  - TGR_mini: `common/history/countries/gbr - great britain.txt`
  - BPM: `common/history/countries/brz - brazil.txt`
  - BPM: `common/history/countries/chi - china.txt`
  - BPM: `common/history/countries/chl - chile.txt`
  - BPM: `common/history/countries/fra - france.txt`
  - BPM: `common/history/countries/ont - ontario.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - TGR_mini: `common/history/global/TGR_TAX_PANEL_global.txt`
  - TGR_mini: `common/history/global/TGR_TRADE_global.txt`
  - TGR_mini: `common/history/global/TGR_TRADE_obsessions.txt`
  - BPM: `common/history/global/00_bpm_global.txt`
  - BPM: `common/history/global/zz_bpm_global.txt`
  - BPM: `common/history/global/zzz_bpm_country_specific_global.txt`
  - BPM: `common/history/global/zzzz_bpm_brazil_la_specific_global.txt`
  - BPM: `common/history/global/zzzzzz_bpm_global_last.txt`

### common/laws — 3 duplicates
- `law_canton_system`
  - TGR_mini: `common/laws/TGR_TRADE_trade_policy.txt`
  - BPM: `common/laws/BPM_trade_policy.txt`
- `law_isolationism`
  - TGR_mini: `common/laws/TGR_TRADE_trade_policy.txt`
  - BPM: `common/laws/BPM_trade_policy.txt`
- `law_land_based_taxation`
  - TGR_mini: `common/laws/TGR_TAX_PANEL_taxation.txt`
  - BPM: `common/laws/BPM_taxation.txt`

### common/on_actions — 4 duplicates
- `on_half_yearly_pulse_country`
  - TGR_mini: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TGR_mini: `common/on_actions/TGR_DECREES_on_actions.txt`
  - TGR_mini: `common/on_actions/TGR_MIGRATION_on_actions.txt`
  - TGR_mini: `common/on_actions/TGR_TAX_PANEL_on_tax_law_change.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`
- `on_law_activated`
  - TGR_mini: `common/on_actions/TGR_TAX_PANEL_on_tax_law_change.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_newcab_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`
- `on_monthly_pulse_country`
  - TGR_mini: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TGR_mini: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_bnap_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_france_oa.txt`
  - BPM: `common/on_actions/bpm_hog_top_actions.txt`
- `on_yearly_pulse_country`
  - TGR_mini: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TGR_mini: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
  - TGR_mini: `common/on_actions/TGR_TRADE_code_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_movements_on_actions.txt`
  - BPM: `common/on_actions/bpm_newcab_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`

### common/production_methods — 9 duplicates
- `pm_assembly_lines_building_arms_industry`
  - TGR_mini: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_assembly_lines_building_automotive_industry`
  - TGR_mini: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_assembly_lines_building_motor_industry`
  - TGR_mini: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_automated_bakery`
  - TGR_mini: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_automatic_power_looms`
  - TGR_mini: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_mechanized_looms`
  - TGR_mini: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_rotary_valve_engine_building_arms_industry`
  - TGR_mini: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_rotary_valve_engine_building_motor_industry`
  - TGR_mini: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_watertube_boiler_building_motor_industry`
  - TGR_mini: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **5**
  - `law_graduated_taxation`
    - TGR_mini: `localization/english/TGR_TAX_PANEL_law_l_english.yml`
    - BPM: `localization/braz_por/BPM_laws_l_braz_por.yml`
    - BPM: `localization/english/BPM_laws_l_english.yml`
    - BPM: `localization/french/BPM_laws_l_french.yml`
  - `law_land_based_taxation`
    - TGR_mini: `localization/english/TGR_TAX_PANEL_law_l_english.yml`
    - BPM: `localization/braz_por/BPM_laws_l_braz_por.yml`
    - BPM: `localization/english/BPM_laws_l_english.yml`
    - BPM: `localization/french/BPM_laws_l_french.yml`
  - `law_land_based_taxation_desc`
    - TGR_mini: `localization/english/TGR_TAX_PANEL_law_l_english.yml`
    - BPM: `localization/braz_por/BPM_laws_l_braz_por.yml`
    - BPM: `localization/english/BPM_laws_l_english.yml`
    - BPM: `localization/french/BPM_laws_l_french.yml`
  - `law_per_capita_based_taxation`
    - TGR_mini: `localization/english/TGR_TAX_PANEL_law_l_english.yml`
    - BPM: `localization/braz_por/BPM_laws_l_braz_por.yml`
    - BPM: `localization/english/BPM_laws_l_english.yml`
    - BPM: `localization/french/BPM_laws_l_french.yml`
  - `law_proportional_taxation`
    - TGR_mini: `localization/english/TGR_TAX_PANEL_law_l_english.yml`
    - BPM: `localization/braz_por/BPM_laws_l_braz_por.yml`
    - BPM: `localization/english/BPM_laws_l_english.yml`
    - BPM: `localization/french/BPM_laws_l_french.yml`

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**