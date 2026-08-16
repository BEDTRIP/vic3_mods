# BPM + T&R + KAI (+CMF) — master conflict list (manual reviewed)

Порядок загрузки по задаче: **T&R / KAI / CMF → BPM (последний)**.

Ниже перечислены **все обнаруженные пересечения** между модулями сборки `TechRes+Kuromi` (`t&r`, `kai`, `cmf`) и модом `BPM`.

> Важно: `tools/scan_conflicts.py` даёт эвристику по top-level ключам. Я дополнительно проверил руками типы правок (`REPLACE`/`INJECT`) в ключевых местах, чтобы отделить “реальные” конфликты от нормальной аддитивности.

## 1) Жёсткие конфликты по путям файлов

**НЕТ.** Во всех парах модов `file path overlaps = 0`.
Это означает: один мод **не перезаписывает целиком файл** другого по одинаковому относительному пути.

Отчёты:
- `bpm_tr/conflicts_tr_vs_kai.md`
- `bpm_tr/conflicts_tr_vs_cmf.md`
- `bpm_tr/conflicts_kai_vs_cmf.md`
- `bpm_tr/conflicts_tr_vs_bpm.md`
- `bpm_tr/conflicts_kai_vs_bpm.md`
- `bpm_tr/conflicts_cmf_vs_bpm.md`

## 2) Конфликты (или пересечения) по объектам в `common/`

### 2.1 T&R ↔ KAI

**A) `common/script_values` — РЕАЛЬНЫЙ конфликт (оба `REPLACE`)**
- `wanted_army_size_script_value`
  - T&R: `common/script_values/ztr_ai_script_values.txt` (`REPLACE`)
  - KAI: `common/script_values/kai_script_values.txt` (`REPLACE`)
  - **Итог при загрузке**: если KAI после T&R, правка T&R (в т.ч. множители под поздние техи T&R и “superpower” стратегии) будет потеряна.
- `wanted_navy_size_script_value`
  - аналогично (`REPLACE` vs `REPLACE`).

**B) `common/ai_strategies` — “мягкое” пересечение (оба `INJECT`)**
- `ai_strategy_default`
- `ai_strategy_colonial_expansion`
- `ai_strategy_territorial_expansion`
- `ai_strategy_colonial_extraction`
- `ai_strategy_industrial_expansion`
- `ai_strategy_resource_expansion`

Обе стороны используют `INJECT:*` → правки будут применяться последовательно по порядку загрузки; конфликт возможен только если они пишут одни и те же поля.

**C) `common/technology/technologies` — “мягкое” пересечение (оба `INJECT`)**
- `telephone`, `radio`, `steam_turbine`, `mechanical_tools`, `atmospheric_engine`

### 2.2 T&R ↔ BPM

**A) `common/production_methods` — в основном НЕ критично (T&R `REPLACE`, BPM `INJECT`)**
Пересечение по 29 PM, например:
- `pm_steel`: T&R `REPLACE:pm_steel`, BPM `INJECT:pm_steel` (BPM добавляет `disallowing_amendments = { bpm_amendment_artisanal_economy }`)
- `pm_aeroplane_production`: T&R `REPLACE`, BPM `INJECT`
- `pm_tank_production`: T&R `REPLACE`, BPM `INJECT`

**Итог**: обычно совместимо — BPM “накладывает” ограничение-амендмент поверх определения T&R. Тем не менее, это всё равно место для перепроверки (если BPM делает `INJECT` в несуществующие/переименованные узлы).

**B) `common/laws` — РЕАЛЬНЫЙ конфликт (оба `REPLACE`)**
- `law_industry_banned`
  - T&R: `common/laws/ztr_economic_system.txt` (`REPLACE`)
  - BPM: `common/laws/BPM_economic_system.txt` (`REPLACE`)
  - **Факт руками**: BPM-версия не удаляет ряд зданий, которые добавлены/учтены в T&R (например `building_alloys_plant`, `building_electronics_industry` и т.д.), зато добавляет `visible`-ограничение под `bpm_amendment_artisanal_economy`.
  - **Итог**: при BPM последним T&R логика “сноса” части late-game зданий по этому закону теряется.

**C) `common/journal_entries` — РЕАЛЬНЫЙ конфликт (оба `REPLACE`)**
- `je_strike`
  - T&R: `common/journal_entries/ztr_vanilla_je.txt` (`REPLACE`) — расширяет ванильный JE (таймер/фейл/ивент T&R).
  - BPM: `common/journal_entries/BPM_je_general_strike.txt` (`REPLACE`) — **полностью отключает** ванильный `je_strike` и вводит собственную систему `je_bpm_general_strike_*`.
  - **Итог**: T&R-правки `je_strike` не будут работать с BPM (по дизайну BPM).

**D) `common/technology/technologies` — РЕАЛЬНЫЙ конфликт (оба `REPLACE`)**
- `feminism` (T&R `REPLACE` vs BPM `REPLACE`) — различаются era/встроенная логика.
- `mass_propaganda` (T&R `REPLACE` vs BPM `REPLACE`) — T&R включает MR-совместимость (`elgar_mass_culture_tech`) и дополнительные модификаторы; BPM оставляет ванильный `film` и другой набор модификаторов.

**E) `common/on_actions` — вероятно аддитивно (не критично)**
- `on_acquired_technology`
- `on_monthly_pulse_country`
- `on_yearly_pulse_country`

У BPM и у T&R это оформлено как `on_actions = { ... }` и даже внутри BPM встречаются множественные определения одного и того же `on_*` → практически наверняка движок это **мерджит** (иначе BPM ломался бы сам на себе).

**F) `common/history/global` — скорее аддитивно**
- `GLOBAL` (есть в T&R и во множестве BPM файлов).

### 2.3 KAI ↔ BPM

**A) `common/laws` — РЕАЛЬНЫЙ конфликт (KAI `INJECT`, BPM `REPLACE`)**
Совпадают ключи (13 шт.), например:
- `law_public_schools`: KAI `INJECT` добавляет/правит `ai_enact_weight_modifier`, BPM делает `REPLACE`

**Итог**: при BPM последним KAI правки AI-весов законов будут утеряны, если их не повторить/не перенести в компач.

**B) `common/ai_strategies` — РЕАЛЬНЫЙ конфликт (KAI `INJECT`, BPM `REPLACE`)**
- `ai_strategy_conservative_agenda`, `ai_strategy_progressive_agenda`, `ai_strategy_egalitarian_agenda`, `ai_strategy_nationalist_agenda`, `ai_strategy_reactionary_agenda`

**C) `common/defines` — РЕАЛЬНЫЙ конфликт (оба задают `NAI = { ... }`)**
- KAI: `common/defines/kai_ai.txt` задаёт/переписывает множество AI-дефайнов.
- BPM: `common/defines/BPM_defines.txt` тоже задаёт `NAI` (и плюс `NPolitics`).
- Есть пересечения по конкретным ключам (например `REFORM_GOVERNMENT_PRO_IG_CLOUT_FACTOR`), значения разные.

### 2.4 CMF ↔ BPM

**A) `common/parties` — РЕАЛЬНЫЙ конфликт (BPM `REPLACE`)**
11 партий (`conservative_party`, `liberal_party`, …) — BPM делает `REPLACE:*`, CMF — базовые определения.

**B) `common/political_movements` — РЕАЛЬНЫЙ конфликт**
26 движений (`movement_*`) определяются в обоих; BPM явно правит/заменяет многие определения.

**C) `common/laws` — РЕАЛЬНЫЙ конфликт**
- `law_autocracy`, `law_oligarchy`, `law_monarchy`, `law_hereditary_bureaucrats` (BPM заменяет/правит собственными файлами).

**D) `common/scripted_triggers` — НЕ критично (одинаковые заглушки)**
Ключи вроде `com_is_active`, `morgenrote_is_active`, `BPM_is_active_trigger` и т.п. в обеих сторонах просто `always = no` → дубликаты по сути эквивалентны.

**E) `common/on_actions`, `common/history/global` — скорее аддитивно**
- `on_country_formed`, `on_new_ruler` (CMF добавляет блокеры/regency; BPM добавляет свои обработчики)
- `GLOBAL` (см. выше)

## 3) Что это значит для будущего компача (высокий приоритет)

Если BPM грузится последним, то для сохранения “фишек” T&R/KAI/CMF придётся решать прежде всего:
- **`common/defines` (NAI)**: свести вместе KAI AI-дефайны и BPM AI/политические дефайны.
- **`common/laws/*`**: перенести KAI `ai_enact_weight_modifier` в BPM-версии законов (или сделать `INJECT`-патч после BPM).
- **`common/ai_strategies/*`**: перенести KAI изменения в BPM `REPLACE`-стратегиях (или пост-инжект).
- **`je_strike`**: выбрать дизайн (оставляем BPM-замену strike-системы как есть, либо интегрируем T&R эффекты в BPM JE).
- **`feminism` / `mass_propaganda`**: совместить нужные куски (era/разлочки/модификаторы/MR-ветка).

