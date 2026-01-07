# T&R vs BPM — conflict report (heuristic)

- T&R root: `C:/Users/Andrey/Projects/vic3_mods/.TechRes+Kuromi/t&r`
- BPM root: `C:/Users/Andrey/Projects/vic3_mods/.BPM`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **0**
- (no overlapping relative file paths detected)

## common/*: duplicate top-level keys (identifier-level)

### common/history/global — 1 duplicates
- `GLOBAL`
  - T&R: `common/history/global/ztr_global.txt`
  - BPM: `common/history/global/00_bpm_global.txt`
  - BPM: `common/history/global/zz_bpm_global.txt`
  - BPM: `common/history/global/zzz_bpm_country_specific_global.txt`
  - BPM: `common/history/global/zzzz_bpm_brazil_la_specific_global.txt`
  - BPM: `common/history/global/zzzzzz_bpm_global_last.txt`

### common/journal_entries — 1 duplicates
- `je_strike`
  - T&R: `common/journal_entries/ztr_vanilla_je.txt`
  - BPM: `common/journal_entries/BPM_je_general_strike.txt`

### common/laws — 1 duplicates
- `law_industry_banned`
  - T&R: `common/laws/ztr_economic_system.txt`
  - BPM: `common/laws/BPM_economic_system.txt`

### common/on_actions — 3 duplicates
- `on_acquired_technology`
  - T&R: `common/on_actions/ztr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_monthly_pulse_country`
  - T&R: `common/on_actions/ztr_on_actions.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_bnap_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_france_oa.txt`
  - BPM: `common/on_actions/bpm_hog_top_actions.txt`
- `on_yearly_pulse_country`
  - T&R: `common/on_actions/ztr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_movements_on_actions.txt`
  - BPM: `common/on_actions/bpm_newcab_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`

### common/production_methods — 29 duplicates
- `pm_aeroplane_production`
  - T&R: `common/production_methods/ztr_military_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_arc_welding_shipbuilding`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_assembly_lines_building_arms_industry`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_assembly_lines_building_automotive_industry`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_assembly_lines_building_furniture_manufactory`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_assembly_lines_building_motor_industry`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_assembly_lines_building_munition_plant`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_assembly_lines_building_tooling_workshop`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_automatic_power_looms`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_bolt_action_rifles`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_breech_loaders`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_brine_electrolysis`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_diesel_engines`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_elastics`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_electric_arc_process`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_electric_engines`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_electric_sewing_machines`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_houseware_plastics`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_improved_fertilizer`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_mass_automobile_production`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_mechanized_workshops`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_nitrogen_fixation`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_precision_tools`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_radios`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_recoiled_barrels`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_repeaters`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_rubber_grips`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_steel`
  - T&R: `common/production_methods/ztr_vanilla_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `pm_tank_production`
  - T&R: `common/production_methods/ztr_military_production_methods.txt`
  - BPM: `common/production_methods/bpm_industry.txt`

### common/technology/technologies — 2 duplicates
- `feminism`
  - T&R: `common/technology/technologies/ztr_modified_vanilla_society.txt`
  - BPM: `common/technology/technologies/zzzz_bpm_technologies_important.txt`
- `mass_propaganda`
  - T&R: `common/technology/technologies/ztr_modified_mr_society.txt`
  - BPM: `common/technology/technologies/zzzz_bpm_technologies_important.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**