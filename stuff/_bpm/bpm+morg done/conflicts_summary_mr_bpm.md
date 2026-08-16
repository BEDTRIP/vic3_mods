# bpm+morg — master summary конфликтов (MR → BPM → compatch)

Этот файл объединяет **4 отчёта** в один, без повторений (ключи/пути сведены в единые пункты):
- `conflicts_summary_mr_bpm.md` (раньше был “ручной” сводкой — теперь это master)
- `conflicts_morgen_vs_bpm_report.md` (Morgenrote(morgen) vs BPM, включает overlap по путям)
- `conflicts_mr_vs_bpm_report.md` (Morgenrote(out) vs BPM(out), key-level)
- `conflicts_cmf_vs_bpm_report.md` (CMF из MR pack vs BPM, key-level)

Порядок запуска по условию: **Morgenrote → BPM → compatch**.  
Следствие: всё, что BPM делает через `REPLACE*` или совпадает по пути файла, **победит**, если компач не вмешается.

## 1) Жёсткие конфликты по пути файла (hard overlaps)

### `common/achievement_groups.txt`

- **Overlap по пути**: да (есть и в MR, и в BPM).
- **Итог при MR→BPM**: BPM целиком перетирает MR-версию.

**Что делать в компаче**: сделать свой `common/achievement_groups.txt`, собранный так:
- базовые группы **как в ванили**;
- добавить `group = { name = "bpm_achievements" ... }` (из BPM);
- добавить все MR-группы (из MR).

## 2) Подтверждённые конфликты “по смыслу” (REPLACE/ломает совместимость)

### 2.1) Технология `mass_propaganda` (оба трогают один ванильный tech)

- **Ключ**: `mass_propaganda` (`common/technology/technologies/*`)
- **MR**: `TRY_INJECT:mass_propaganda` добавляет prereq `elgar_mass_culture_tech` (“changed from film”).
- **BPM**: `REPLACE:mass_propaganda` задаёт prereq `political_agitation` + `film`.
- **Итог при MR→BPM**: MR-инжект будет **перетёрт** BPM-REPLACE, и `elgar_mass_culture_tech` не окажется в prereq.

**Что делать в компаче** (минимум, безопасно): после BPM сделать `TRY_INJECT:mass_propaganda` и добавить `elgar_mass_culture_tech` в `unlocking_technologies`.  
**Требует решения вручную**: оставлять ли `film` (как в BPM) или убирать (как хотел MR).

### 2.2) Scripted trigger “мод активен”: `morgenrote_is_active`

- **MR (morg/mr)**:
  - `common/scripted_triggers/zz_mr_is_active_trigger.txt` задаёт `REPLACE_OR_CREATE:morgenrote_is_active = { always = yes }`
- **BPM**:
  - `common/scripted_triggers/00_community_mod_compatibility_triggers.txt` задаёт `morgenrote_is_active = { always = no }`
- **Итог при MR→BPM**: BPM-версия (always no) **перетирает** MR, и проверка “MR активен” становится ложной.

**Что делать в компаче**: положить файл `common/scripted_triggers/zzzz_bpm_mr_is_active_trigger.txt` с
`REPLACE_OR_CREATE:morgenrote_is_active = { always = yes }`, чтобы он грузился **после BPM**.

## 3) Потенциально важные конфликты (меняет контент, но не обязательно “ломает”)

### 3.1) `common/character_templates` (шведские правители) — исправлено компачем (возвращаем MR-версии после BPM)

Ключи:
- `swe_charles_bernadotte_template`
- `swe_gustaf_v_bernadotte_template`
- `swe_karl_johan_bernadotte_template`
- `swe_oscar_bernadotte_template`
- `swe_oscar_ii_bernadotte_template`

Файлы:
- **MR**: `common/character_templates/mr_general_rulers.txt` (делает `TRY_REPLACE:` и добавляет **mr_* traits**, местами **mr_* DNA**, IG/идеологию)
- **BPM**: `common/character_templates/zz_bpm_historical_leaders_europe.txt` (делает `REPLACE:` и задаёт **свою** логику IG/идеологий/трейтов)

**Итог при MR→BPM**: BPM гарантированно “победит” (полный `REPLACE`), поэтому MR-уникальные трейты/ДНК у этих персонажей пропадут.

**Что сделано в компаче**: добавлен `common/character_templates/zzzz_bpm_mr_rulers_sweden_patch.txt`, который переопределяет эти 5 шаблонов после BPM (MR-флейвор снова “побеждает”).

## 4) Полный свод “identifier-level duplicates” (объединено из всех 4 файлов)

Важно про эвристику:
- `CHARACTERS`/`COUNTRIES`/`GLOBAL` в `common/history/*` — почти всегда **ложноположительно** (топ-ключ в формате файла).
- `common/on_actions/*` часто **аддитивно**, но всё равно полезно знать, что ключ определяют в нескольких местах.

### 4.1) `common/achievement_groups.txt`: key duplicate

- `group`
  - MR: `common/achievement_groups.txt`
  - BPM: `common/achievement_groups.txt`

### 4.2) `common/history/characters`: key duplicate

- `CHARACTERS`
  - MR: `common/history/characters/mr_swe - sweden.txt`
  - MR: `common/history/characters/mr_tas - tasmania.txt`
  - MR: `common/history/characters/par - parma.txt`
  - MR: `common/history/characters/rap - rapanui.txt`
  - MR: `common/history/characters/z_mr_swi - switzerland.txt`
  - BPM: `common/history/characters/arg - argentina.txt`
  - BPM: `common/history/characters/aus - austria.txt`
  - BPM: `common/history/characters/bad - baden.txt`
  - BPM: `common/history/characters/bav - bavaria.txt`
  - BPM: `common/history/characters/bgm - begemder.txt`

### 4.3) `common/history/countries`: key duplicate

- `COUNTRIES`
  - MR: `common/history/countries/rap - rapanui.txt`
  - MR: `common/history/countries/z_mr_starting_technologies.txt`
  - BPM: `common/history/countries/brz - brazil.txt`
  - BPM: `common/history/countries/chi - china.txt`
  - BPM: `common/history/countries/chl - chile.txt`
  - BPM: `common/history/countries/fra - france.txt`
  - BPM: `common/history/countries/ont - ontario.txt`
  - BPM: `common/history/countries/pco - puerto rico.txt`

### 4.4) `common/history/global`: key duplicate

- `GLOBAL`
  - MR: `common/history/global/0_mr_cmf_initiation.txt`
  - MR: `common/history/global/mr_global.txt`
  - MR: `common/history/global/mr_set_cultures_global.txt`
  - CMF(from MR pack): `common/history/global/enable_example_button.txt`
  - BPM: `common/history/global/00_bpm_global.txt`
  - BPM: `common/history/global/zz_bpm_global.txt`
  - BPM: `common/history/global/zzz_bpm_country_specific_global.txt`
  - BPM: `common/history/global/zzzz_bpm_brazil_la_specific_global.txt`
  - BPM: `common/history/global/zzzzzz_bpm_global_last.txt`

### 4.5) `common/on_actions`: key duplicates (объединено MR + CMF)

- `on_acquired_technology`
  - MR: `common/on_actions/agassiz_on_actions.txt`
  - MR: `common/on_actions/artists_on_actions.txt`
  - MR: `common/on_actions/curtiss_on_actions.txt`
  - MR: `common/on_actions/dubois_on_actions.txt`
  - MR: `common/on_actions/elgar_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_country_formed`
  - MR: `common/on_actions/elgar_on_actions.txt`
  - CMF(from MR pack): `common/on_actions/com_formation_event_blocker.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_country_released_as_independent`
  - MR: `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_consciousness_new_countries.txt`
- `on_country_released_as_overlord_subject`
  - MR: `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_consciousness_new_countries.txt`
- `on_country_released_as_own_subject`
  - MR: `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_consciousness_new_countries.txt`
- `on_five_year_pulse_country`
  - MR: `common/on_actions/artists_on_actions.txt`
  - MR: `common/on_actions/klimt_on_actions.txt`
  - MR: `common/on_actions/lepsius_on_actions.txt`
  - MR: `common/on_actions/verrier_on_actions.txt`
  - MR: `common/on_actions/vikelas_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_half_yearly_pulse_country`
  - MR: `common/on_actions/academics_on_actions.txt`
  - MR: `common/on_actions/ai_on_actions.txt`
  - MR: `common/on_actions/artists_on_actions.txt`
  - MR: `common/on_actions/athletes_on_actions.txt`
  - MR: `common/on_actions/curtiss_on_actions.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`
- `on_monthly_pulse_country`
  - MR: `common/on_actions/academics_on_actions.txt`
  - MR: `common/on_actions/agassiz_on_actions.txt`
  - MR: `common/on_actions/ai_on_actions.txt`
  - MR: `common/on_actions/artists_on_actions.txt`
  - MR: `common/on_actions/curtiss_on_actions.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_bnap_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_france_oa.txt`
  - BPM: `common/on_actions/bpm_hog_top_actions.txt`
- `on_new_ruler`
  - CMF(from MR pack): `common/on_actions/com_regency_blocker.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_revolution_start`
  - MR: `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
- `on_secession_start`
  - MR: `common/on_actions/mr_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_consciousness_new_countries.txt`
- `on_yearly_pulse_country`
  - MR: `common/on_actions/MFE_main_flavor_pulse.txt`
  - MR: `common/on_actions/academics_on_actions.txt`
  - MR: `common/on_actions/agassiz_on_actions.txt`
  - MR: `common/on_actions/ai_on_actions.txt`
  - MR: `common/on_actions/artists_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_movements_on_actions.txt`
  - BPM: `common/on_actions/bpm_newcab_on_actions.txt`
  - BPM: `common/on_actions/bpm_republic_on_actions.txt`

### 4.6) `common/laws`: key duplicates (CMF(from MR pack) vs BPM)

- `law_autocracy`
  - CMF(from MR pack): `common/laws/com_distribution_of_power.txt`
  - BPM: `common/laws/BPM_distribution_of_power.txt`
- `law_hereditary_bureaucrats`
  - CMF(from MR pack): `common/laws/com_bureaucracy.txt`
  - BPM: `common/laws/BPM_bureaucracy.txt`
- `law_monarchy`
  - CMF(from MR pack): `common/laws/com_governance_principles.txt`
  - BPM: `common/laws/BPM_governance_principles.txt`
- `law_oligarchy`
  - CMF(from MR pack): `common/laws/com_distribution_of_power.txt`
  - BPM: `common/laws/BPM_distribution_of_power.txt`

### 4.7) `common/parties`: key duplicates (CMF(from MR pack) vs BPM)

- `agrarian_party`
  - CMF(from MR pack): `common/parties/agrarian_party.txt`
  - BPM: `common/parties/zzzz_agrarian_party.txt`
- `anarchist_party`
  - CMF(from MR pack): `common/parties/anarchist_party.txt`
  - BPM: `common/parties/zzzz_anarchist_party.txt`
- `communist_party`
  - CMF(from MR pack): `common/parties/communist_party.txt`
  - BPM: `common/parties/zzzz_communist_party.txt`
- `conservative_party`
  - CMF(from MR pack): `common/parties/conservative_party.txt`
  - BPM: `common/parties/zzzz_conservative_party.txt`
- `fascist_party`
  - CMF(from MR pack): `common/parties/fascist_party.txt`
  - BPM: `common/parties/zzzz_fascist_party.txt`
- `free_trade_party`
  - CMF(from MR pack): `common/parties/free_trade_party.txt`
  - BPM: `common/parties/zzzz_free_trade_party.txt`
- `liberal_party`
  - CMF(from MR pack): `common/parties/liberal_party.txt`
  - BPM: `common/parties/zzzz_liberal_party.txt`
- `military_party`
  - CMF(from MR pack): `common/parties/military_party.txt`
  - BPM: `common/parties/zzzz_military_party.txt`
- `radical_party`
  - CMF(from MR pack): `common/parties/radical_party.txt`
  - BPM: `common/parties/zzzz_radical_party.txt`
- `religious_party`
  - CMF(from MR pack): `common/parties/religious_party.txt`
  - BPM: `common/parties/zzzz_religious_party.txt`
- `social_democrat_party`
  - CMF(from MR pack): `common/parties/social_democrats_party.txt`
  - BPM: `common/parties/zzzz_social_democrats_party.txt`

### 4.8) `common/political_movements`: key duplicates (CMF(from MR pack) vs BPM)

- `movement_anarchist`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_socialist_movements.txt`
- `movement_anti_slavery`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_bonapartist`
  - CMF(from MR pack): `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/04_country_specific_ideological_movements.txt`
- `movement_communist`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_socialist_movements.txt`
- `movement_corporatist`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_cultural_majority`
  - CMF(from MR pack): `common/political_movements/ycom_02_cultural_movement.txt`
  - BPM: `common/political_movements/zzzz_bpm_cultural_movement.txt`
- `movement_cultural_minority`
  - CMF(from MR pack): `common/political_movements/ycom_02_cultural_movement.txt`
  - BPM: `common/political_movements/zzzz_bpm_cultural_movement.txt`
- `movement_fascist`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_reactionary_movements.txt`
- `movement_feminist`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_india_pan_national`
  - CMF(from MR pack): `common/political_movements/ycom_03_pan_national_movements.txt`
  - BPM: `common/political_movements/03_pan_national_movements.txt`
- `movement_labor`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_socialist_movements.txt`
- `movement_land_reform`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_legitimist`
  - CMF(from MR pack): `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/04_country_specific_ideological_movements.txt`
- `movement_liberal`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_minority_rights`
  - CMF(from MR pack): `common/political_movements/ycom_02_cultural_movement.txt`
  - BPM: `common/political_movements/zzzz_bpm_cultural_movement.txt`
- `movement_modernizer`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_nihilist`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_orleanist`
  - CMF(from MR pack): `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/04_country_specific_ideological_movements.txt`
- `movement_positivist`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_pro_slavery`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`
- `movement_radical`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_reactionary`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_reactionary_movements.txt`
- `movement_royalist_absolutist`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_reactionary_movements.txt`
- `movement_royalist_constitutional`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_liberal_movements.txt`
- `movement_socialist`
  - CMF(from MR pack): `common/political_movements/ycom_00_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_socialist_movements.txt`
- `movement_utilitarian`
  - CMF(from MR pack): `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - BPM: `common/political_movements/zzzz_bpm_ideological_uncategorized_movements.txt`

### 4.9) `common/scripted_triggers`: key duplicates (объединено CMF + MR)

- `BPM_is_active_trigger`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/zz_bpm_mod_compatibility_triggers.txt`
- `EACP_is_active_trigger`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `GGGG_is_active_trigger`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `JKFP_is_active_trigger`
  - MR: `common/scripted_triggers/00_mr_compatibility_triggers.txt`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `PCT_is_active_trigger`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `RRK_is_active_trigger`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `STMS_is_active_trigger`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `WCR_is_active_trigger`
  - MR: `common/scripted_triggers/00_mr_compatibility_triggers.txt`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `anno1836_is_active`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `anzfp_is_active`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `basileia_is_active`
  - MR: `common/scripted_triggers/00_mr_compatibility_triggers.txt`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `com_is_active`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `gilded_age_is_active_trigger`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `grefm_is_active`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `is_usfp_active`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `morgenrote_is_active`
  - MR: `common/scripted_triggers/zz_mr_is_active_trigger.txt`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`
- `newspapers_is_active_triger`
  - CMF(from MR pack): `common/scripted_triggers/0_community_mod_triggers.txt`
  - BPM: `common/scripted_triggers/00_community_mod_compatibility_triggers.txt`

## 5) Нулевые дубликаты (для полноты)

- localization duplicate keys: **0** (во всех отчётах)
- events duplicate ids: **0** (во всех отчётах)
