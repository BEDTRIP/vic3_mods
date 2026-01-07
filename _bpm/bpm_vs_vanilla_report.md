# .BPM vs vanilla — file/key summary (heuristic)

- Mod root: `C:/Users/Andrey/Projects/vic3_mods/.BPM`
- Vanilla game root: `C:/Users/Andrey/Projects/vic3_mods/..vanillaVIC3/game`

## common/* overview

| category | mod files | overrides (same path) | new (no vanilla path) | mod keys | new keys | shared keys |
|---|---:|---:|---:|---:|---:|---:|
| `common` | 1 | 1 | 0 | 1 | 0 | 1 |
| `common/achievements` | 1 | 0 | 1 | 1 | 1 | 0 |
| `common/ai_strategies` | 3 | 0 | 3 | 10 | 3 | 7 |
| `common/alert_types` | 1 | 0 | 1 | 4 | 4 | 0 |
| `common/amendments` | 2 | 0 | 2 | 11 | 1 | 10 |
| `common/character_interactions` | 3 | 0 | 3 | 15 | 5 | 10 |
| `common/character_templates` | 28 | 0 | 28 | 631 | 62 | 569 |
| `common/coat_of_arms/coat_of_arms` | 1 | 0 | 1 | 23 | 15 | 8 |
| `common/country_creation` | 1 | 0 | 1 | 2 | 2 | 0 |
| `common/country_definitions` | 1 | 0 | 1 | 8 | 6 | 2 |
| `common/country_formation` | 1 | 0 | 1 | 4 | 1 | 3 |
| `common/customizable_localization` | 24 | 0 | 24 | 218 | 218 | 0 |
| `common/decisions` | 4 | 1 | 3 | 4 | 2 | 2 |
| `common/defines` | 1 | 0 | 1 | 2 | 0 | 2 |
| `common/diplomatic_plays` | 1 | 0 | 1 | 21 | 0 | 21 |
| `common/dna_data` | 2 | 0 | 2 | 2 | 2 | 0 |
| `common/dynamic_country_map_colors` | 1 | 0 | 1 | 1 | 1 | 0 |
| `common/dynamic_country_names` | 2 | 0 | 2 | 9 | 2 | 7 |
| `common/flag_definitions` | 2 | 0 | 2 | 16 | 7 | 9 |
| `common/game_concepts` | 1 | 0 | 1 | 90 | 90 | 0 |
| `common/game_rules` | 1 | 0 | 1 | 1 | 1 | 0 |
| `common/government_types` | 5 | 0 | 5 | 82 | 22 | 60 |
| `common/history/characters` | 35 | 30 | 5 | 1 | 0 | 1 |
| `common/history/countries` | 7 | 7 | 0 | 1 | 0 | 1 |
| `common/history/global` | 7 | 0 | 7 | 1 | 0 | 1 |
| `common/history/lobbies` | 1 | 1 | 0 | 1 | 0 | 1 |
| `common/history/political_movements` | 1 | 1 | 0 | 1 | 0 | 1 |
| `common/ideologies` | 22 | 0 | 22 | 289 | 194 | 95 |
| `common/institutions` | 2 | 0 | 2 | 5 | 5 | 0 |
| `common/interest_group_traits` | 5 | 0 | 5 | 0 | 0 | 0 |
| `common/interest_groups` | 21 | 0 | 21 | 21 | 13 | 8 |
| `common/journal_entries` | 54 | 1 | 53 | 116 | 64 | 52 |
| `common/journal_entry_groups` | 1 | 0 | 1 | 8 | 8 | 0 |
| `common/law_groups` | 2 | 0 | 2 | 18 | 13 | 5 |
| `common/laws` | 31 | 0 | 31 | 154 | 79 | 75 |
| `common/legitimacy_levels` | 1 | 0 | 1 | 5 | 0 | 5 |
| `common/messages` | 6 | 0 | 6 | 38 | 38 | 0 |
| `common/modifier_type_definitions` | 5 | 0 | 5 | 186 | 166 | 20 |
| `common/on_actions` | 14 | 0 | 14 | 102 | 69 | 33 |
| `common/parties` | 13 | 0 | 13 | 13 | 2 | 11 |
| `common/political_lobbies` | 1 | 0 | 1 | 4 | 0 | 4 |
| `common/political_lobby_appeasement` | 1 | 0 | 1 | 1 | 1 | 0 |
| `common/political_movements` | 9 | 2 | 7 | 30 | 4 | 26 |
| `common/power_bloc_principles` | 1 | 0 | 1 | 2 | 0 | 2 |
| `common/production_methods` | 1 | 0 | 1 | 59 | 0 | 59 |
| `common/script_values` | 20 | 0 | 20 | 299 | 299 | 0 |
| `common/scripted_buttons` | 13 | 0 | 13 | 62 | 46 | 16 |
| `common/scripted_effects` | 51 | 0 | 51 | 416 | 411 | 5 |
| `common/scripted_guis` | 13 | 0 | 13 | 60 | 60 | 0 |
| `common/scripted_progress_bars` | 8 | 0 | 8 | 31 | 28 | 3 |
| `common/scripted_triggers` | 27 | 0 | 27 | 327 | 319 | 8 |
| `common/static_modifiers` | 14 | 0 | 14 | 549 | 537 | 12 |
| `common/technology/technologies` | 3 | 0 | 3 | 10 | 0 | 10 |
| `common/trigger_localization` | 1 | 0 | 1 | 2 | 2 | 0 |

## events overview

- Files: **157** (overrides by path: **2**, new: **155**)
- Event definition keys (`X = { ... }`): **925** (new vs vanilla: **482**, shared: **443**)
- Namespaces: `1834_additional_act`, `1848`, `BPM_CAB_DEBUG_UTILS`, `BRZ_populism`, `BRZ_vargas`, `CHI_missionaries`, `acw_events`, `agitators_law_events`, `anarchy`, `anti_state_religion`, `bp1_misc`, `bpm_1st_commie_rev`, `bpm_1st_intl`, `bpm_2nd_intl`, `bpm_acw_events`, `bpm_anarchist_potd`, `bpm_anarchist_split`, `bpm_anarchist_utils`, `bpm_bnap_canada_events`, `bpm_bnap_confederation_events`, `bpm_bnap_patriots_events`, `bpm_cabinet_event`, `bpm_china`, `bpm_china_revolts`, `bpm_christdem_flavour`, `bpm_christdem_split`, `bpm_christian_democrats_events`, `bpm_clear_stubbornness_utils`, `bpm_coal_wars_agitators`, `bpm_colony_events`, `bpm_confucian_state`, `bpm_conservative_utils`, `bpm_debug`, `bpm_east_asia_dynamics`, `bpm_election_events`, `bpm_fascism_events`, `bpm_fascist_split`, `bpm_france`, `bpm_france_july_monarchy`, `bpm_frankfurt_parliament_events`, `bpm_general_strike`, `bpm_ideology_soft_compat_events`, `bpm_ig_attraction_utils`, `bpm_japan`, `bpm_law_veto`, `bpm_liberal_utils`, `bpm_lobby`, `bpm_marlib_split`, `bpm_misc`, `bpm_modernizers`, `bpm_movement_splits`, `bpm_movement_takeovers`, `bpm_natlib_split`, `bpm_new_wine_old_wineskins_flavour`, `bpm_papal_encyclicals`, `bpm_patcon_split`, `bpm_provisional_government_events`, `bpm_radlib_utils`, `bpm_reactionary_utils`, `bpm_rev_ripples`, `bpm_revsoc_utils`, `bpm_russia`, `bpm_scandinavia`, `bpm_send_notification`, `bpm_single_party`, `bpm_slavic`, `bpm_socdem_utils`, `bpm_socialist_split`, `bpm_socialist_utils`, `bpm_state_crisis`, `bpm_syndicalism`, `bpm_tutorial`, `bpm_union_laws`, `bpm_union_leadership`, `brazil_monarchy`, `brazilian_minors`, `brazilian_slavery`, `bureaucracy`, `cable_street`, `caste_conflict`, `caucasuswar_end`, `caudillo`, `central_america`, `character_events`, `children_rights_events`, `citizenship_laws`, `coffee_with_milk`, `colonial_administration_events`, `colonization`, `communism`, `communist_elections`, `congo_free_state_events`, `conscription_laws`, `council_republic_law_events`, `coup`, `coup_aftermath_events`, `coup_pulse_events`, `distribution_of_power_laws`, `dual_monarchy`, `economy_laws`, `education_laws`, `election_contextual_events`, `election_liberal_events`, `election_other_parties_events`, `ethiopia`, `famine_events`, `fascism_events`, `free_speech_laws`, `generic_laws`, `german_unification`, `gg_korea`, `healthcare_laws`, `heavenly`, `historical_agitators`, `india_events`, `india_nationalism_events`, `internal_security_events`, `isolation`, `italian_springtime`, `kazakhstan_events`, `korea_monarchy`, `labor_rights`, `land_ownership_law_events`, `law_events`, `laws`, `laws_police`, `liberalism`, `lobby_events`, `manifest_destiny`, `marx_events`, `meiji`, `migration_laws`, `monarchy_law_events`, `mughal`, `natural_borders`, `neighbor_events`, `nihilism`, `paraguay`, `paris_commune`, `paris_commune_pulse_events`, `pedro`, `peoples_springtime`, `persia_events`, `peru_bolivia_events`, `positivism`, `positivism_pulse`, `provisional_government_events`, `raj`, `republic_laws`, `revolution_pulse_events`, `rhine_confederation`, `rights_of_women_laws`, `russia_monarchy`, `sa_migration`, `single_party_state`, `slave_revolt`, `slavery_law_events`, `sol_events`, `state_atheism`, `suffragist_events`, `tax`, `technocracy`, `theocracy`, `unable_to_enact`, `utilitarian`, `victoria`, `warlord_china_events`, `welfare_laws`, `zanzibar`

## other top-level folders (file-level path overrides)

| folder | mod files | overrides (same path) | new |
|---|---:|---:|---:|
| `dlc` | 4 | 0 | 4 |
| `dlc_metadata` | 1 | 0 | 1 |
| `gfx` | 324 | 26 | 298 |
| `gui` | 22 | 1 | 21 |
| `localization` | 940 | 0 | 940 |
| `map_data` | 0 | 0 | 0 |