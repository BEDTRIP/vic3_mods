# VC vs BPM — conflict report (heuristic)

- VC root: `C:/Users/Andrey/Projects/vic3_mods/.Victorian Century`
- BPM root: `C:/Users/Andrey/Projects/vic3_mods/.BPM`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **6**
- Load order note: if `BPM` loads after `VC`, `BPM` wins on these files.

### common/* file overlaps — 6
- **common/decisions**: 1
  - `common/decisions/manifest_destiny.txt`
- **common/history**: 4
  - `common/history/countries/brz - brazil.txt`
  - `common/history/countries/chi - china.txt`
  - `common/history/countries/fra - france.txt`
  - `common/history/countries/usa - usa.txt`
- **common/journal_entries**: 1
  - `common/journal_entries/00_peoples_springtime_je.txt`

### other folders file overlaps
- (no overlaps outside `common/*`)

## common/*: duplicate top-level keys (identifier-level)

### common/character_templates — 49 duplicates
- `BEL_leopold_saxe_coburg_gotha_template`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_bel.txt`
- `BIC_george_eden`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_bic.txt`
- `BIC_john_lawrence`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_bic.txt`
- `GBR_John_Frost`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_albert_inkpin`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_anthony_ashley-cooper`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_arthur_balfour`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_arthur_james_cook`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_charles_gordon-lennox`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_charles_prestwich_scott`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_david_lloyd_george`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_edward_smith-stanley`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_fitzroy_somerset`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_friedrich_engels`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_george_barnes`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_george_hamilton-gordon`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_john_bedford_leno`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_john_bright`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_john_maynard_keynes`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_john_russell`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_richard_cobden`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_robert_owen`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_robert_peel`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_rotha_lintorn-orman`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_rowland_hill`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_thomas_barnes`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_william_howley`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `GBR_william_lamb`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `RUS_alexander_ii`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_rus.txt`
- `agitator_john_stuart_mill`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `agitator_william_smith_o_brien`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `chi_daoguang_template`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_historical_leaders_asia.txt`
- `gbr_albert_edward_template`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_charles_dickens_character_template`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_disraeli_character_template`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_george_curzon`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_gladstone_character_template`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_o_connor_template`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_pankhurst_character_template`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_queen_victoria_template`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_temple_character_template`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_wellington_character_template`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `gbr_william_hanover_template`
  - VC: `common/character_templates/joi_country_gbr.txt`
  - BPM: `common/character_templates/zz_bpm_country_gbr.txt`
- `pru_wilhelm_IV_hohenzollern_template`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_historical_leaders_europe.txt`
- `rus_admiral_nakhimov`
  - VC: `common/character_templates/joi_commander_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_rus.txt`
- `rus_general_skobelev`
  - VC: `common/character_templates/joi_commander_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_rus.txt`
- `tur_abdulmecid_osmanoglu_template`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_tur.txt`
- `tur_mahmut_osmanoglu_template`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_country_tur.txt`
- `usa_lincoln_character_template`
  - VC: `common/character_templates/joi_templates.txt`
  - BPM: `common/character_templates/zz_bpm_historical_leaders_americas.txt`

### common/country_formation — 1 duplicates
- `GER`
  - VC: `common/country_formation/jol_major_formables.txt`
  - BPM: `common/country_formation/BPM_major_formables.txt`

### common/defines — 1 duplicates
- `NAI`
  - VC: `common/defines/joi_ai.txt`
  - BPM: `common/defines/BPM_defines.txt`

### common/dynamic_country_names — 3 duplicates
- `CAN`
  - VC: `common/dynamic_country_names/joi_dynamic_country_names.txt`
  - BPM: `common/dynamic_country_names/zz_dynamic_country_names.txt`
- `LOM`
  - VC: `common/dynamic_country_names/joi_dynamic_country_names.txt`
  - BPM: `common/dynamic_country_names/bpm_dynamic_country_names.txt`
- `XIN`
  - VC: `common/dynamic_country_names/joi_dynamic_country_names.txt`
  - BPM: `common/dynamic_country_names/bpm_dynamic_country_names.txt`

### common/flag_definitions — 1 duplicates
- `GER`
  - VC: `common/flag_definitions/joi_flag_definitions.txt`
  - BPM: `common/flag_definitions/zz_bpm_00_flag_definitions.txt`

### common/government_types — 17 duplicates
- `gov_absolute_empire`
  - VC: `common/government_types/joi_monarchies.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_constitutional_empire`
  - VC: `common/government_types/joi_monarchies.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_constitutional_kingdom`
  - VC: `common/government_types/joi_monarchies.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_crown_colony`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_crown_colony_india`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_feudal_empire`
  - VC: `common/government_types/joi_monarchies.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_junta`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_kingdom`
  - VC: `common/government_types/joi_monarchies.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_military_dictatorship`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_parliamentary_democracy`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_parliamentary_dictatorship`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types.txt`
- `gov_parliamentary_oligarchy`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types.txt`
- `gov_parliamentary_single_party_state`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_presidential_democracy`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_presidential_dictatorship`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_presidential_oligarchy`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `gov_presidential_single_party_state`
  - VC: `common/government_types/joi_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`

### common/history/countries — 1 duplicates
- `COUNTRIES`
  - VC: `common/history/countries/aus - austria.txt`
  - VC: `common/history/countries/bic - british east india company.txt`
  - VC: `common/history/countries/brz - brazil.txt`
  - VC: `common/history/countries/chi - china.txt`
  - VC: `common/history/countries/fra - france.txt`
  - BPM: `common/history/countries/brz - brazil.txt`
  - BPM: `common/history/countries/chi - china.txt`
  - BPM: `common/history/countries/fra - france.txt`
  - BPM: `common/history/countries/ont - ontario.txt`
  - BPM: `common/history/countries/pco - puerto rico.txt`

### common/history/lobbies — 1 duplicates
- `LOBBIES`
  - VC: `common/history/lobbies/joi_lobbies.txt`
  - BPM: `common/history/lobbies/00_lobbies.txt`

### common/ideologies — 5 duplicates
- `ideology_bonapartist`
  - VC: `common/ideologies/joi_leader_ideologies.txt`
  - BPM: `common/ideologies/bpm_leader_ideologies.txt`
- `ideology_corporatist`
  - VC: `common/ideologies/joi_ig_ideologies.txt`
  - BPM: `common/ideologies/zz_00_ig_ideologies.txt`
- `ideology_scholar_paternalistic`
  - VC: `common/ideologies/joi_ig_ideologies.txt`
  - BPM: `common/ideologies/zz_00_ig_ideologies.txt`
- `ideology_utilitarian_leader`
  - VC: `common/ideologies/joi_leader_ideologies.txt`
  - BPM: `common/ideologies/bpm_leader_ideologies.txt`
- `ideology_utilitarian_millian`
  - VC: `common/ideologies/joi_ig_ideologies.txt`
  - BPM: `common/ideologies/zz_00_ig_ideologies.txt`

### common/interest_groups — 8 duplicates
- `ig_armed_forces`
  - VC: `common/interest_groups/joi_armed_forces.txt`
  - BPM: `common/interest_groups/zzzz_armed_forces.txt`
- `ig_devout`
  - VC: `common/interest_groups/joi_devout.txt`
  - BPM: `common/interest_groups/zzzz_devout.txt`
- `ig_industrialists`
  - VC: `common/interest_groups/joi_industrialists.txt`
  - BPM: `common/interest_groups/zzzz_industrialists.txt`
- `ig_intelligentsia`
  - VC: `common/interest_groups/joi_intelligentsia.txt`
  - BPM: `common/interest_groups/zzzz_intelligentsia.txt`
- `ig_landowners`
  - VC: `common/interest_groups/joi_landowners.txt`
  - BPM: `common/interest_groups/zzzz_landowners.txt`
- `ig_petty_bourgeoisie`
  - VC: `common/interest_groups/joi_petty_bourgeoisie.txt`
  - BPM: `common/interest_groups/zzzz_petty_bourgeoisie.txt`
- `ig_rural_folk`
  - VC: `common/interest_groups/joi_rural_folk.txt`
  - BPM: `common/interest_groups/zzzz_rural_folk.txt`
- `ig_trade_unions`
  - VC: `common/interest_groups/joi_trade_unions.txt`
  - BPM: `common/interest_groups/zzzzzz_trade_unions.txt`

### common/journal_entries — 15 duplicates
- `je_cement_the_rightful_dynasty`
  - VC: `common/journal_entries/01_french_monarchism.txt`
  - BPM: `common/journal_entries/zz_bpm_02_french_monarchism.txt`
- `je_german_unification`
  - VC: `common/journal_entries/00_german_unification.txt`
  - BPM: `common/journal_entries/zz_bpm_00_german_unification.txt`
- `je_german_unification_idea`
  - VC: `common/journal_entries/00_german_unification.txt`
  - BPM: `common/journal_entries/zz_bpm_00_german_unification.txt`
- `je_meiji_army`
  - VC: `common/journal_entries/00_meiji_restoration.txt`
  - BPM: `common/journal_entries/zz_bpm_00_meiji_restoration.txt`
- `je_meiji_diplomacy`
  - VC: `common/journal_entries/00_meiji_restoration.txt`
  - BPM: `common/journal_entries/zz_bpm_00_meiji_restoration.txt`
- `je_meiji_economy`
  - VC: `common/journal_entries/00_meiji_restoration.txt`
  - BPM: `common/journal_entries/zz_bpm_00_meiji_restoration.txt`
- `je_meiji_main`
  - VC: `common/journal_entries/00_meiji_restoration.txt`
  - BPM: `common/journal_entries/zz_bpm_00_meiji_restoration.txt`
- `je_meiji_restoration`
  - VC: `common/journal_entries/00_meiji_restoration.txt`
  - BPM: `common/journal_entries/zz_bpm_00_meiji_restoration.txt`
- `je_north_german_unification`
  - VC: `common/journal_entries/00_german_unification.txt`
  - BPM: `common/journal_entries/zz_bpm_00_german_unification.txt`
- `je_schleswig_holstein_question`
  - VC: `common/journal_entries/00_german_unification.txt`
  - BPM: `common/journal_entries/zz_bpm_00_german_unification.txt`
- `je_sepoy_mutiny`
  - VC: `common/journal_entries/04_sepoy_mutiny.txt`
  - BPM: `common/journal_entries/zz_bpm_08_sepoy_mutiny.txt`
- `je_south_german_unification`
  - VC: `common/journal_entries/00_german_unification.txt`
  - BPM: `common/journal_entries/zz_bpm_00_german_unification.txt`
- `je_springtime_of_the_peoples`
  - VC: `common/journal_entries/00_peoples_springtime_je.txt`
  - BPM: `common/journal_entries/BPM_je_peoples_springtime.txt`
- `je_terakoya`
  - VC: `common/journal_entries/00_meiji_restoration.txt`
  - BPM: `common/journal_entries/zz_bpm_00_meiji_restoration.txt`
- `je_uneasy_raj`
  - VC: `common/journal_entries/04_sepoy_mutiny.txt`
  - BPM: `common/journal_entries/zz_bpm_08_sepoy_mutiny.txt`

### common/on_actions — 4 duplicates
- `on_diplo_play_war_start`
  - VC: `common/on_actions/headlines_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_monthly_pulse_country`
  - VC: `common/on_actions/headlines_on_actions.txt`
  - VC: `common/on_actions/joi_code_on_actions.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_bnap_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_france_oa.txt`
  - BPM: `common/on_actions/bpm_hog_top_actions.txt`
- `on_new_ruler`
  - VC: `common/on_actions/joi_code_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_yearly_pulse_country`
  - VC: `common/on_actions/modlc_on_actions_monthly.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_movements_on_actions.txt`
  - BPM: `common/on_actions/bpm_newcab_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`

### common/parties — 3 duplicates
- `conservative_party`
  - VC: `common/parties/conservative_party.txt`
  - BPM: `common/parties/zzzz_conservative_party.txt`
- `liberal_party`
  - VC: `common/parties/liberal_party.txt`
  - BPM: `common/parties/zzzz_liberal_party.txt`
- `radical_party`
  - VC: `common/parties/radical_party.txt`
  - BPM: `common/parties/zzzz_radical_party.txt`

### common/political_movements — 2 duplicates
- `movement_bonapartist`
  - VC: `common/political_movements/joi_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/04_country_specific_ideological_movements.txt`
- `movement_utilitarian`
  - VC: `common/political_movements/joi_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`

### common/scripted_buttons — 1 duplicates
- `je_the_eastern_border_treaty_of_aigun`
  - VC: `common/scripted_buttons/joi_russia_buttons.txt`
  - BPM: `common/scripted_buttons/zzz_04_russia_buttons.txt`

### common/static_modifiers — 2 duplicates
- `modifier_india_company_rule`
  - VC: `common/static_modifiers/joi_modifiers.txt`
  - BPM: `common/static_modifiers/zz_BPM_content_304_modifiers.txt`
- `modifier_india_crown_rule`
  - VC: `common/static_modifiers/joi_modifiers.txt`
  - BPM: `common/static_modifiers/zz_BPM_content_304_modifiers.txt`

### common/technology/technologies — 1 duplicates
- `corporatism`
  - VC: `common/technology/technologies/joi_society.txt`
  - BPM: `common/technology/technologies/bpm_technologies_less_important.txt`
  - BPM: `common/technology/technologies/zzzzzzzz_bpm_technologies_less_important.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **1**
  - `victoria.2`
    - VC: `events/victoria_events.txt`
    - BPM: `events/_victoria_events.txt`