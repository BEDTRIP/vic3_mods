# Конфликты TGR ↔ BPM (ручная выжимка + уточнения к scan_conflicts)

Порядок загрузки по задаче: **TGR → BPM (BPM последний)**.
Следствие: без компача любые совпадения **по относительному пути файла** будут жёстко перезаписаны BPM; а совпадения **по key/идентификатору** в большинстве `common/**`-БД будут “побеждать” определением BPM (в зависимости от того, как именно движок сливает конкретный тип БД).

Сырые данные сканера: `bpm_tgr/conflicts_tgr_vs_bpm_report.md` (45 file overlaps, 157 common key dups, 6 loc dups).

## 1) Жёсткие конфликты: одинаковые пути файлов (BPM перезапишет TGR)

Всего: **45** файлов.

### 1.1 Критично (игровая логика)

- `common/decisions/manifest_destiny.txt`
  - В TGR файл содержит `REPLACE_OR_CREATE:manifest_destiny` + доп. эффекты/ивент/модификатор.
  - В BPM файл **пустой** → при загрузке BPM последним это фактически **убирает решение** (и ванильное, и TGR-версию), т.к. мод своим пустым файлом заменяет ванильный `game/common/decisions/manifest_destiny.txt`.
- `common/history/countries/brz - brazil.txt`
- `common/history/countries/chi - china.txt`
- `common/history/countries/fra - france.txt`
  - Это стартовая история стран. Сейчас BPM полностью перезаписывает TGR-изменения в этих странах (и наоборот, если поменять порядок).

### 1.2 Косметика (скорее всего можно просто выбрать победителя)

- `gfx/**` — **41** файл (в основном иконки законов/интерфейса + несколько картинок/CoA).
  - В текущем порядке будет “выглядеть как в BPM” на этих ассетах.

## 2) Конфликты по идентификаторам в `common/**` (одинаковый key в обеих модах)

Всего: **157** совпадений ключей. Ниже — по категориям (взято из отчёта сканера).

### 2.1 Почти гарантированно конфликт (один key = одно определение)

- `**common/country_formation**`: `GER`
  - TGR: `common/country_formation/TGR_GER_UNIFICATION_major_formables.txt`
  - BPM: `common/country_formation/BPM_major_formables.txt`
- `**common/decisions**`: `canada_unite_can`, `canada_unite_gbr`
  - TGR: `common/decisions/canada_australia.txt` (REPLACE_OR_CREATE, своя логика AI/дат)
  - BPM: `common/decisions/zz_bnap_decisions_override.txt` (REPLACE, добавляет `is_player = no`, требует отношения `amicable`, другой тех-триггер для AI)
- `**common/government_types**`: `gov_presidential_democracy`, `gov_presidential_dictatorship`
  - TGR: `common/government_types/TGR_POLITICS_presidential_republics.txt`
  - BPM: `common/government_types/bpm_types_override.txt`
- `**common/ideologies**`: **35** пересечений (`ideology_moderate`, `ideology_traditionalist`, `ideology_communist`, …)
  - TGR: `common/ideologies/TGR_POLITICS_character_ideologies.txt`
  - BPM: `common/ideologies/bpm_leader_ideologies.txt`
- `**common/interest_groups**`: **8** пересечений (`ig_landowners`, `ig_intelligentsia`, …)
  - TGR: `common/interest_groups/TGR_POLITICS_*.txt`
  - BPM: `common/interest_groups/zzzz*.txt`
- `**common/journal_entries**`: `je_german_unification`, `je_north_german_unification`, `je_schleswig_holstein_question`
  - TGR: `common/journal_entries/TGR_GER_UNIFICATION_german_unification.txt`
  - BPM: `common/journal_entries/zz_bpm_00_german_unification.txt`
- `**common/law_groups**`: **7** пересечений (`lawgroup_centralization`, `lawgroup_foreign_policy`, …)
  - TGR: `common/law_groups/TGR_POLITICS_laws.txt`
  - BPM: `common/law_groups/BPM_laws.txt`
- `**common/laws**`: **64** пересечения (очень крупный конфликт)
  - TGR: `common/laws/TGR_POLITICS_*.txt` + `common/laws/TGR_TAX_PANEL_taxation.txt` + `common/laws/TGR_TRADE_trade_policy.txt`
  - BPM: `common/laws/BPM_*.txt`
  - **Особо критично**: налоги.
    - В TGR `TGR_TAX_PANEL_taxation.txt` прямо отключает реальные `tax_modifier_*` (они закомментированы) и переводит логику на переменные/модификаторы налоговой панели.
    - В BPM `BPM_taxation.txt` возвращает полноценные `tax_modifier_*` и добавляет свой `modifier`.
    - При загрузке BPM последним высок шанс поломки/обесценивания логики TGR налоговой панели.
- `**common/legitimacy_levels**`: **5** пересечений
  - TGR: `common/legitimacy_levels/TGR_POLITICS_legitimacy_levels.txt`
  - BPM: `common/legitimacy_levels/bpm_legitimacy_levels.txt`
- `**common/modifier_type_definitions**`: `country_shopkeepers_pol_str_mult`
  - TGR: `common/modifier_type_definitions/TGR_POLITICS_todo_sort_into_other_files.txt`
  - BPM: `common/modifier_type_definitions/BPM_functional_modifiers.txt`
- `**common/parties**`: **11** пересечений (`conservative_party`, `liberal_party`, …)
  - TGR: `common/parties/*.txt`
  - BPM: `common/parties/zzzz_*.txt`
- `**common/production_methods**`: **9** пересечений (автоматизация/индустрия)
  - TGR: `common/production_methods/TGR_TRADE_automation.txt`
  - BPM: `common/production_methods/bpm_industry.txt`
- `**common/technology/technologies**`: `democracy`
  - TGR: `common/technology/technologies/TGR_POLITICS_society.txt`
  - BPM: `common/technology/technologies/zzzz_bpm_technologies_important.txt`

### 2.2 “Скорее совместимо, но надо учитывать порядок/эффекты” (аддитивные системы)

- `**common/on_actions**`: `on_monthly_pulse_country`, `on_yearly_pulse_country`, `on_half_yearly_pulse_country`, `on_law_activated`
  - У обеих модов много отдельных блоков с одинаковым on_action-ключом.
  - Для Vic3 это обычно **аддитивно** (все эффекты выполняются), но:
    - порядок выполнения может иметь значение;
    - если оба мода трогают одни и те же переменные/флаги/модификаторы, будет “логический конфликт”, даже если синтаксически всё грузится.

### 2.3 Не считать конфликтом (ложноположительное из-за структуры файлов)

- `common/history/countries`: ключ `COUNTRIES`
- `common/history/global`: ключ `GLOBAL`

Эти ключи повторяются почти во всех history-файлах по дизайну. Реальные конфликты в history здесь — только **file path overlaps** из раздела 1.1.

## 3) `common/defines` — уточнение вручную (внутренние define-ключи)

Сканер показал пересечение верхнего `NAI` и `NPolitics`, но важно именно пересечение *внутренних* define-ключей.

Результат сравнения внутренних ключей (скрипт `bpm_tgr/analyze_defines_overlap.py`):

- `**NAI**`
  - `REFORM_GOVERNMENT_MONTHS_BETWEEN_CHANGES`: TGR=12 (`TGR_ADJUSTMENTS_ai.txt`) vs BPM=20 (`BPM_defines.txt`)
- `**NPolitics**` (8 пересечений)
  - `IG_INFLUENCING_MOVEMENT_MIN_SUPPORTING_CLOUT`: TGR=0.15 vs BPM=0.1
  - `IG_SUPPORTING_MOVEMENT_MIN_SUPPORTING_CLOUT`: совпадает
  - `LEGITIMACY_PENALTY_FOR_EACH_EXCESS_ENTITY`: TGR=30 vs BPM=40
  - `MAX_POP_FRACTION_JOIN_OR_LEAVE_MOVEMENT`: TGR=0.2 vs BPM=0.1
  - `MIN_POP_NUMBER_JOIN_OR_LEAVE_MOVEMENT`: TGR=1000 vs BPM=10
  - `MOVEMENT_DEFAULT_MIN_SUPPORT_TO_CREATE`: TGR=0.055 vs BPM=0.025
  - `MOVEMENT_DEFAULT_MIN_SUPPORT_TO_MAINTAIN`: TGR=0.05 vs BPM=0.01
  - `MOVEMENT_POP_SUPPORT_ATTRACTION_CAP`: TGR=0.20 vs BPM=0.01

## 4) Localization (дубли ключей)

Всего: **6** ключей, все вокруг налоговых законов/института:

- `institution_workplace_safety`
- `law_graduated_taxation`
- `law_land_based_taxation`
- `law_land_based_taxation_desc`
- `law_per_capita_based_taxation`
- `law_proportional_taxation`

Здесь конфликт обычно “кто последний, тот и текст”. В компаче нужно будет выбрать/объединить строки.

## 5) GUI (доп. проверка)

Отдельно проверил `*.gui` на пересечение идентификаторов `name/icon/type` (скрипт `tools/compare_gui_names.py` → `bpm_tgr/gui_identifiers_tgr_vs_bpm.txt`):

- пересечений **нет**.

# TGR vs BPM — conflict report (key-level heuristic)

- TGR root: `C:/Users/Andrey/Projects/vic3_mods_out/TheGreatRevision`
- BPM root: `C:/Users/Andrey/Projects/vic3_mods_out/BPM`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/country_formation — 1 duplicates
- `GER`

### common/decisions — 2 duplicates
- `canada_unite_can`
  - TGR: `common/decisions/canada_australia.txt`
  - BPM: `common/decisions/zz_bnap_decisions_override.txt`
- `canada_unite_gbr`

### common/defines — 2 duplicates
- `NAI`
  - TGR: `common/defines/TGR_ADJUSTMENTS_ai.txt`
  - TGR: `common/defines/TGR_GER_UNIFICATION_ai.txt`
  - TGR: `common/defines/TGR_TAX_PANEL_defines.txt`
  - TGR: `common/defines/TGR_TRADE_ai.txt`
  - BPM: `common/defines/BPM_defines.txt`
- `NPolitics`
  - TGR: `common/defines/TGR_LEADER_defines.txt`
  - TGR: `common/defines/TGR_POLITICS_defines.txt`

### common/government_types — 2 duplicates
- `gov_presidential_democracy`
- `gov_presidential_dictatorship`

### common/history/countries — 1 duplicates
- `COUNTRIES`
  - TGR: `common/history/countries/aus - austria.txt`
  - TGR: `common/history/countries/brz - brazil.txt`
  - TGR: `common/history/countries/chi - china.txt`
  - TGR: `common/history/countries/fra - france.txt`
  - TGR: `common/history/countries/gbr - great britain.txt`
  - BPM: `common/history/countries/brz - brazil.txt`
  - BPM: `common/history/countries/chi - china.txt`
  - BPM: `common/history/countries/chl - chile.txt`
  - BPM: `common/history/countries/fra - france.txt`
  - BPM: `common/history/countries/ont - ontario.txt`

### common/history/global — 1 duplicates
- `GLOBAL`
  - TGR: `common/history/global/TGR_LOANS_global.txt`
  - TGR: `common/history/global/TGR_POLITICS_global.txt`
  - TGR: `common/history/global/TGR_TAX_PANEL_global.txt`
  - TGR: `common/history/global/TGR_TRADE_global.txt`
  - TGR: `common/history/global/TGR_TRADE_obsessions.txt`
  - BPM: `common/history/global/00_bpm_global.txt`
  - BPM: `common/history/global/zz_bpm_global.txt`
  - BPM: `common/history/global/zzz_bpm_country_specific_global.txt`
  - BPM: `common/history/global/zzzz_bpm_brazil_la_specific_global.txt`
  - BPM: `common/history/global/zzzzzz_bpm_global_last.txt`

### common/ideologies — 35 duplicates
- `ideology_abolitionist`
- `ideology_anarchist`
- `ideology_authoritarian`
- `ideology_communist`
- `ideology_corporatist_leader`
- `ideology_despotic_utopian`
- `ideology_ethno_nationalist`
- `ideology_fascist`
- `ideology_feminist`
- `ideology_humanitarian`
- `ideology_humanitarian_royalist`
- `ideology_integralist`
- `ideology_jacksonian_democrat`
- `ideology_jingoist_leader`
- `ideology_land_reformer`
- `ideology_liberal_leader`
- `ideology_luddite`
- `ideology_market_liberal`
- `ideology_moderate`
- `ideology_nihilist`
- `ideology_pacifist`
- `ideology_positivist`
- `ideology_protectionist`
- `ideology_radical`
- `ideology_reformer`
- `ideology_republican_leader`
- `ideology_royalist`
- `ideology_slaver`
- `ideology_social_democrat`
- `ideology_sovereignist_leader`
- `ideology_theocrat`
- `ideology_traditionalist`
- `ideology_traditionalist_minoritarian`
- `ideology_utilitarian_leader`
- `ideology_vanguardist`

### common/interest_groups — 8 duplicates
- `ig_armed_forces`
  - TGR: `common/interest_groups/TGR_POLITICS_armed_forces.txt`
  - BPM: `common/interest_groups/zzzz_armed_forces.txt`
- `ig_devout`
  - TGR: `common/interest_groups/TGR_POLITICS_devout.txt`
  - BPM: `common/interest_groups/zzzz_devout.txt`
- `ig_industrialists`
  - TGR: `common/interest_groups/TGR_POLITICS_industrialists.txt`
  - BPM: `common/interest_groups/zzzz_industrialists.txt`
- `ig_intelligentsia`
  - TGR: `common/interest_groups/TGR_POLITICS_intelligentsia.txt`
  - BPM: `common/interest_groups/zzzz_intelligentsia.txt`
- `ig_landowners`
  - TGR: `common/interest_groups/TGR_POLITICS_landowners.txt`
  - BPM: `common/interest_groups/zzzz_landowners.txt`
- `ig_petty_bourgeoisie`
  - TGR: `common/interest_groups/TGR_POLITICS_petty_bourgeoisie.txt`
  - BPM: `common/interest_groups/zzzz_petty_bourgeoisie.txt`
- `ig_rural_folk`
  - TGR: `common/interest_groups/TGR_POLITICS_rural_folk.txt`
  - BPM: `common/interest_groups/zzzz_rural_folk.txt`
- `ig_trade_unions`
  - TGR: `common/interest_groups/TGR_POLITICS_trade_unions.txt`
  - BPM: `common/interest_groups/zzzzzz_trade_unions.txt`

### common/journal_entries — 3 duplicates
- `je_german_unification`
- `je_north_german_unification`
- `je_schleswig_holstein_question`

### common/law_groups — 7 duplicates
- `lawgroup_centralization`
- `lawgroup_distribution_of_power`
- `lawgroup_foreign_policy`
- `lawgroup_governance_principles`
- `lawgroup_labour_associations`
- `lawgroup_land_reform`
- `lawgroup_slavery`

### common/laws — 61 duplicates
- `law_agrarianism`
  - TGR: `common/laws/TGR_POLITICS_economic_system.txt`
  - BPM: `common/laws/BPM_economic_system.txt`
- `law_anarchy`
  - TGR: `common/laws/TGR_POLITICS_distribution_of_power.txt`
  - BPM: `common/laws/BPM_distribution_of_power.txt`
- `law_appointed_bureaucrats`
  - TGR: `common/laws/TGR_POLITICS_bureaucracy.txt`
  - BPM: `common/laws/BPM_bureaucracy.txt`
- `law_autocracy`
- `law_canton_system`
  - TGR: `common/laws/TGR_TRADE_trade_policy.txt`
  - BPM: `common/laws/BPM_trade_policy.txt`
- `law_censorship`
  - TGR: `common/laws/TGR_POLITICS_free_speech.txt`
  - BPM: `common/laws/BPM_free_speech.txt`
- `law_census_voting`
- `law_collectivized_agriculture`
  - TGR: `common/laws/TGR_POLITICS_land_reform.txt`
  - BPM: `common/laws/BPM_land_reform.txt`
- `law_colonial_administration`
  - TGR: `common/laws/TGR_POLITICS_governance_principles.txt`
- `law_command_economy`
- `law_commercialized_agriculture`
- `law_cooperative_ownership`
- `law_corporate_state`
  - BPM: `common/laws/BPM_governance_principles.txt`
- `law_council_republic`
- `law_dedicated_police`
  - TGR: `common/laws/TGR_POLITICS_policing.txt`
  - BPM: `common/laws/BPM_police.txt`
- `law_elder_council`
- `law_elected_bureaucrats`
- `law_guaranteed_liberties`
  - TGR: `common/laws/TGR_POLITICS_internal_security.txt`
  - BPM: `common/laws/BPM_internal_security.txt`
- `law_hereditary_bureaucrats`
- `law_homesteading`
- `law_industry_banned`
- `law_interventionism`
- `law_isolationism`
- `law_laissez_faire`
  - TGR: `common/laws/TGR_TAX_PANEL_taxation.txt`
  - BPM: `common/laws/BPM_taxation.txt`
- `law_landed_voting`
- `law_limited_work_hours`
  - TGR: `common/laws/TGR_POLITICS_working_hours.txt`
  - BPM: `common/laws/BPM_work_time_regulations.txt`
- `law_local_police`
- `law_militarized_police`
- `law_monarchy`
- `law_multicultural`
  - TGR: `common/laws/TGR_POLITICS_citizenship.txt`
  - BPM: `common/laws/BPM_citizenship.txt`
- `law_national_guard`
- `law_neo_absolutism`
- `law_no_police`
- `law_no_workers_rights`
  - TGR: `common/laws/TGR_POLITICS_labor_rights.txt`
  - BPM: `common/laws/BPM_labor_laws.txt`
- `law_oligarchy`
- `law_organic_regulation`
- `law_outlawed_dissent`
- `law_parliamentary_republic`
- `law_presidential_republic`
- `law_private_health_insurance`
  - TGR: `common/laws/TGR_POLITICS_health_system.txt`
  - BPM: `common/laws/BPM_health_system.txt`
- `law_private_schools`
  - TGR: `common/laws/TGR_POLITICS_education_system.txt`
  - BPM: `common/laws/BPM_education_system.txt`
- `law_protected_leisure`
- `law_protected_speech`
- `law_public_schools`
- `law_regulatory_bodies`
- `law_religious_schools`
- `law_right_of_assembly`
- `law_secret_police`
- `law_serfdom`
- `law_single_party_state`
- `law_technocracy`
- `law_tenant_farmers`
- `law_theocracy`
- `law_token_time_regulations`
- `law_traditionalism`
- `law_universal_suffrage`
- `law_unregulated_work_time`
- `law_wealth_voting`
- `law_womens_suffrage`
  - TGR: `common/laws/TGR_POLITICS_rights_of_women.txt`
  - BPM: `common/laws/BPM_rights_of_women.txt`
- `law_worker_protections`

### common/legitimacy_levels — 5 duplicates
- `legitimacy_level_contested`
- `legitimacy_level_illegitimate`
- `legitimacy_level_legitimate`
- `legitimacy_level_righteous`
- `legitimacy_level_unacceptable`

### common/modifier_type_definitions — 5 duplicates
- `country_shopkeepers_pol_str_mult`
- `state_engineers_investment_pool_contribution_add`
  - TGR: `common/modifier_type_definitions/TGR_LOANS_todo_sort_into_other_files.txt`
  - BPM: `common/modifier_type_definitions/zz_BPM_00_modifier_types.txt`
- `state_laborers_investment_pool_contribution_add`
- `state_machinists_investment_pool_contribution_add`
- `state_shopkeepers_investment_pool_contribution_add`

### common/on_actions — 4 duplicates
- `on_half_yearly_pulse_country`
  - TGR: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_DECREES_on_actions.txt`
  - TGR: `common/on_actions/TGR_MIGRATION_on_actions.txt`
  - TGR: `common/on_actions/TGR_TAX_PANEL_on_tax_law_change.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`
- `on_law_activated`
  - BPM: `common/on_actions/bpm_newcab_on_actions.txt`
- `on_monthly_pulse_country`
  - TGR: `common/on_actions/TGR_GER_UNIFICATION_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
  - BPM: `common/on_actions/BPM_bnap_on_actions.txt`
  - BPM: `common/on_actions/bpm_france_oa.txt`
  - BPM: `common/on_actions/bpm_hog_top_actions.txt`
- `on_yearly_pulse_country`
  - TGR: `common/on_actions/TGR_POLITICS_gain_ideology.txt`
  - TGR: `common/on_actions/TGR_TRADE_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_movements_on_actions.txt`

### common/parties — 11 duplicates
- `agrarian_party`
  - TGR: `common/parties/agrarian_party.txt`
  - BPM: `common/parties/zzzz_agrarian_party.txt`
- `anarchist_party`
  - TGR: `common/parties/anarchist_party.txt`
  - BPM: `common/parties/zzzz_anarchist_party.txt`
- `communist_party`
  - TGR: `common/parties/communist_party.txt`
  - BPM: `common/parties/zzzz_communist_party.txt`
- `conservative_party`
  - TGR: `common/parties/conservative_party.txt`
  - BPM: `common/parties/zzzz_conservative_party.txt`
- `fascist_party`
  - TGR: `common/parties/fascist_party.txt`
  - BPM: `common/parties/zzzz_fascist_party.txt`
- `free_trade_party`
  - TGR: `common/parties/free_trade_party.txt`
  - BPM: `common/parties/zzzz_free_trade_party.txt`
- `liberal_party`
  - TGR: `common/parties/liberal_party.txt`
  - BPM: `common/parties/zzzz_liberal_party.txt`
- `military_party`
  - TGR: `common/parties/military_party.txt`
  - BPM: `common/parties/zzzz_military_party.txt`
- `radical_party`
  - TGR: `common/parties/radical_party.txt`
  - BPM: `common/parties/zzzz_radical_party.txt`
- `religious_party`
  - TGR: `common/parties/religious_party.txt`
  - BPM: `common/parties/zzzz_religious_party.txt`
- `social_democrat_party`
  - TGR: `common/parties/social_democrats_party.txt`
  - BPM: `common/parties/zzzz_social_democrats_party.txt`

### common/production_methods — 9 duplicates
- `pm_assembly_lines_building_arms_industry`
- `pm_assembly_lines_building_automotive_industry`
- `pm_assembly_lines_building_motor_industry`
- `pm_automated_bakery`
- `pm_automatic_power_looms`
- `pm_mechanized_looms`
- `pm_rotary_valve_engine_building_arms_industry`
- `pm_rotary_valve_engine_building_motor_industry`
- `pm_watertube_boiler_building_motor_industry`

### common/technology/technologies — 1 duplicates
- `democracy`

## localization: duplicate localization keys
- Total duplicate localization keys: **6**
    - TGR: `localization/english/TGR_POLITICS_l_english.yml`
    - BPM: `localization/braz_por/BPM_institutions_l_braz_por.yml`
    - BPM: `localization/english/BPM_institutions_l_english.yml`
    - BPM: `localization/french/BPM_institutions_l_french.yml`
    - TGR: `localization/english/TGR_TAX_PANEL_law_l_english.yml`
    - BPM: `localization/braz_por/BPM_laws_l_braz_por.yml`
    - BPM: `localization/english/BPM_laws_l_english.yml`
    - BPM: `localization/french/BPM_laws_l_french.yml`

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**

  - BPM: `common/history/countries/pco - puerto rico.txt`

### common/laws — 64 duplicates
- `law_no_womens_rights`
- `law_women_in_the_workplace`
- `law_women_own_property`

### common/modifier_type_definitions — 1 duplicates

== name ==
TGR count: 16
BPM count: 38
Intersect: 0

== icon ==
TGR count: 0
BPM count: 31

== type ==
BPM count: 6
