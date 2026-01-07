# Morgenrote(morgen) vs BPM — conflict report (heuristic)

- Morgenrote(morgen) root: `C:/Users/Andrey/Projects/vic3_mods/.Morgenrote/morgen`
- BPM root: `C:/Users/Andrey/Projects/vic3_mods/.BPM`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **1**
- Load order note: if `BPM` loads after `Morgenrote(morgen)`, `BPM` wins on these files.

### common/* file overlaps — 1
- **common/achievement_groups.txt**: 1
  - `common/achievement_groups.txt`

### other folders file overlaps
- (no overlaps outside `common/*`)

## common/*: duplicate top-level keys (identifier-level)

### common — 1 duplicates
- `group`
  - Morgenrote(morgen): `common/achievement_groups.txt`
  - BPM: `common/achievement_groups.txt`

### common/character_templates — 5 duplicates
- `swe_charles_bernadotte_template`
  - Morgenrote(morgen): `common/character_templates/mr_general_rulers.txt`
  - BPM: `common/character_templates/zz_bpm_historical_leaders_europe.txt`
- `swe_gustaf_v_bernadotte_template`
  - Morgenrote(morgen): `common/character_templates/mr_general_rulers.txt`
  - BPM: `common/character_templates/zz_bpm_historical_leaders_europe.txt`
- `swe_karl_johan_bernadotte_template`
  - Morgenrote(morgen): `common/character_templates/mr_general_rulers.txt`
  - BPM: `common/character_templates/zz_bpm_historical_leaders_europe.txt`
- `swe_oscar_bernadotte_template`
  - Morgenrote(morgen): `common/character_templates/mr_general_rulers.txt`
  - BPM: `common/character_templates/zz_bpm_historical_leaders_europe.txt`
- `swe_oscar_ii_bernadotte_template`
  - Morgenrote(morgen): `common/character_templates/mr_general_rulers.txt`
  - BPM: `common/character_templates/zz_bpm_historical_leaders_europe.txt`

### common/history/characters — 1 duplicates
- `CHARACTERS`
  - Morgenrote(morgen): `common/history/characters/mr_swe - sweden.txt`
  - Morgenrote(morgen): `common/history/characters/mr_tas - tasmania.txt`
  - Morgenrote(morgen): `common/history/characters/par - parma.txt`
  - Morgenrote(morgen): `common/history/characters/rap - rapanui.txt`
  - Morgenrote(morgen): `common/history/characters/z_mr_swi - switzerland.txt`
  - BPM: `common/history/characters/arg - argentina.txt`
  - BPM: `common/history/characters/aus - austria.txt`
  - BPM: `common/history/characters/bad - baden.txt`
  - BPM: `common/history/characters/bav - bavaria.txt`
  - BPM: `common/history/characters/bgm - begemder.txt`

### common/history/countries — 1 duplicates
- `COUNTRIES`
  - Morgenrote(morgen): `common/history/countries/rap - rapanui.txt`
  - Morgenrote(morgen): `common/history/countries/z_mr_starting_technologies.txt`
  - BPM: `common/history/countries/brz - brazil.txt`
  - BPM: `common/history/countries/chi - china.txt`
  - BPM: `common/history/countries/fra - france.txt`
  - BPM: `common/history/countries/ont - ontario.txt`
  - BPM: `common/history/countries/pco - puerto rico.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - Morgenrote(morgen): `common/history/global/0_mr_cmf_initiation.txt`
  - Morgenrote(morgen): `common/history/global/mr_global.txt`
  - Morgenrote(morgen): `common/history/global/mr_set_cultures_global.txt`
  - BPM: `common/history/global/00_bpm_global.txt`
  - BPM: `common/history/global/zz_bpm_global.txt`
  - BPM: `common/history/global/zzz_bpm_country_specific_global.txt`
  - BPM: `common/history/global/zzzz_bpm_brazil_la_specific_global.txt`
  - BPM: `common/history/global/zzzzzz_bpm_global_last.txt`

### common/on_actions — 11 duplicates
- `on_acquired_technology`
  - Morgenrote(morgen): `common/on_actions/agassiz_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/artists_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/curtiss_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/dubois_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/elgar_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_country_formed`
  - Morgenrote(morgen): `common/on_actions/elgar_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_country_released_as_independent`
  - Morgenrote(morgen): `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_consciousness_new_countries.txt`
- `on_country_released_as_overlord_subject`
  - Morgenrote(morgen): `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_consciousness_new_countries.txt`
- `on_country_released_as_own_subject`
  - Morgenrote(morgen): `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_consciousness_new_countries.txt`
- `on_five_year_pulse_country`
  - Morgenrote(morgen): `common/on_actions/artists_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/klimt_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/lepsius_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/verrier_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/vikelas_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_half_yearly_pulse_country`
  - Morgenrote(morgen): `common/on_actions/academics_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/ai_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/artists_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/athletes_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/curtiss_on_actions.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`
- `on_monthly_pulse_country`
  - Morgenrote(morgen): `common/on_actions/academics_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/agassiz_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/ai_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/artists_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/curtiss_on_actions.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_bnap_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_france_oa.txt`
  - BPM: `common/on_actions/bpm_hog_top_actions.txt`
- `on_revolution_start`
  - Morgenrote(morgen): `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_secession_start`
  - Morgenrote(morgen): `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_consciousness_new_countries.txt`
- `on_yearly_pulse_country`
  - Morgenrote(morgen): `common/on_actions/MFE_main_flavor_pulse.txt`
  - Morgenrote(morgen): `common/on_actions/academics_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/agassiz_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/ai_on_actions.txt`
  - Morgenrote(morgen): `common/on_actions/artists_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_movements_on_actions.txt`
  - BPM: `common/on_actions/bpm_newcab_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`

### common/scripted_triggers — 4 duplicates
- `JKFP_is_active_trigger`
  - Morgenrote(morgen): `common/scripted_triggers/00_mr_compatibility_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `WCR_is_active_trigger`
  - Morgenrote(morgen): `common/scripted_triggers/00_mr_compatibility_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `basileia_is_active`
  - Morgenrote(morgen): `common/scripted_triggers/00_mr_compatibility_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `morgenrote_is_active`
  - Morgenrote(morgen): `common/scripted_triggers/zz_mr_is_active_trigger.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`

### common/technology/technologies — 1 duplicates
- `mass_propaganda`
  - Morgenrote(morgen): `common/technology/technologies/a_vanilla_society_technologies.txt`
  - BPM: `common/technology/technologies/zzzz_bpm_technologies_important.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**