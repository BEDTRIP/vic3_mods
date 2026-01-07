# CMF vs BPM — conflict report (heuristic)

- CMF root: `C:/Users/Andrey/Projects/vic3_mods/.TechRes+Kuromi/cmf`
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
  - CMF: `common/history/global/enable_example_button.txt`
  - BPM: `common/history/global/00_bpm_global.txt`
  - BPM: `common/history/global/zz_bpm_global.txt`
  - BPM: `common/history/global/zzz_bpm_country_specific_global.txt`
  - BPM: `common/history/global/zzzz_bpm_brazil_la_specific_global.txt`
  - BPM: `common/history/global/zzzzzz_bpm_global_last.txt`

### common/laws — 4 duplicates
- `law_autocracy`
  - CMF: `common/laws/com_distribution_of_power.txt`
  - BPM: `common/laws/BPM_distribution_of_power.txt`
- `law_hereditary_bureaucrats`
  - CMF: `common/laws/com_bureaucracy.txt`
  - BPM: `common/laws/BPM_bureaucracy.txt`
- `law_monarchy`
  - CMF: `common/laws/com_governance_principles.txt`
  - BPM: `common/laws/BPM_governance_principles.txt`
- `law_oligarchy`
  - CMF: `common/laws/com_distribution_of_power.txt`
  - BPM: `common/laws/BPM_distribution_of_power.txt`

### common/on_actions — 2 duplicates
- `on_country_formed`
  - CMF: `common/on_actions/com_formation_event_blocker.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_new_ruler`
  - CMF: `common/on_actions/com_regency_blocker.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`

### common/parties — 11 duplicates
- `agrarian_party`
  - CMF: `common/parties/agrarian_party.txt`
  - BPM: `common/parties/zzzz_agrarian_party.txt`
- `anarchist_party`
  - CMF: `common/parties/anarchist_party.txt`
  - BPM: `common/parties/zzzz_anarchist_party.txt`
- `communist_party`
  - CMF: `common/parties/communist_party.txt`
  - BPM: `common/parties/zzzz_communist_party.txt`
- `conservative_party`
  - CMF: `common/parties/conservative_party.txt`
  - BPM: `common/parties/zzzz_conservative_party.txt`
- `fascist_party`
  - CMF: `common/parties/fascist_party.txt`
  - BPM: `common/parties/zzzz_fascist_party.txt`
- `free_trade_party`
  - CMF: `common/parties/free_trade_party.txt`
  - BPM: `common/parties/zzzz_free_trade_party.txt`
- `liberal_party`
  - CMF: `common/parties/liberal_party.txt`
  - BPM: `common/parties/zzzz_liberal_party.txt`
- `military_party`
  - CMF: `common/parties/military_party.txt`
  - BPM: `common/parties/zzzz_military_party.txt`
- `radical_party`
  - CMF: `common/parties/radical_party.txt`
  - BPM: `common/parties/zzzz_radical_party.txt`
- `religious_party`
  - CMF: `common/parties/religious_party.txt`
  - BPM: `common/parties/zzzz_religious_party.txt`
- `social_democrat_party`
  - CMF: `common/parties/social_democrats_party.txt`
  - BPM: `common/parties/zzzz_social_democrats_party.txt`

### common/political_movements — 26 duplicates
- `movement_anarchist`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_socialist_movements.txt`
- `movement_anti_slavery`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_bonapartist`
  - CMF: `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/04_country_specific_ideological_movements.txt`
- `movement_communist`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_socialist_movements.txt`
- `movement_corporatist`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_cultural_majority`
  - CMF: `common/political_movements/ycom_02_cultural_movement.txt`
  - BPM: `common/political_movements/zzzz_bpm_cultural_movement.txt`
- `movement_cultural_minority`
  - CMF: `common/political_movements/ycom_02_cultural_movement.txt`
  - BPM: `common/political_movements/zzzz_bpm_cultural_movement.txt`
- `movement_fascist`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_reactionary_movements.txt`
- `movement_feminist`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_india_pan_national`
  - CMF: `common/political_movements/ycom_03_pan_national_movements.txt`
  - BPM: `common/political_movements/03_pan_national_movements.txt`
- `movement_labor`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_socialist_movements.txt`
- `movement_land_reform`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_legitimist`
  - CMF: `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/04_country_specific_ideological_movements.txt`
- `movement_liberal`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_minority_rights`
  - CMF: `common/political_movements/ycom_02_cultural_movement.txt`
  - BPM: `common/political_movements/zzzz_bpm_cultural_movement.txt`
- `movement_modernizer`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_nihilist`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_orleanist`
  - CMF: `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/04_country_specific_ideological_movements.txt`
- `movement_positivist`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_pro_slavery`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_radical`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_reactionary`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_reactionary_movements.txt`
- `movement_royalist_absolutist`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_reactionary_movements.txt`
- `movement_royalist_constitutional`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_socialist`
  - CMF: `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_socialist_movements.txt`
- `movement_utilitarian`
  - CMF: `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`

### common/scripted_triggers — 17 duplicates
- `BPM_is_active_trigger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/zz_bpm_mod_compatibility_triggers.txt`
- `EACP_is_active_trigger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `GGGG_is_active_trigger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `JKFP_is_active_trigger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `PCT_is_active_trigger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `RRK_is_active_trigger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `STMS_is_active_trigger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `WCR_is_active_trigger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `anno1836_is_active`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `anzfp_is_active`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `basileia_is_active`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `com_is_active`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `gilded_age_is_active_trigger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `grefm_is_active`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `is_usfp_active`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `morgenrote_is_active`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `newspapers_is_active_triger`
  - CMF: `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**