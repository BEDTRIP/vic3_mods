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

