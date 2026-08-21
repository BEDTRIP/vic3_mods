# Morgenröte × Power Blocs Expanded — отчёт о проверке

- **Дата сверки:** 2026-08-21
- **Вывод:** компач **не нужен**, папка остаётся `noneed`, содержимого не несёт.
- Morgenröte: `C:/Users/Andrey/Projects/vic3_mods_out/Morgenrote` — `2.8.3e Mitsopoulos`,
  `supported_game_version = 1.13.*`, зависимость: Community Mod Framework `1.*`
- PBE: `C:/Users/Andrey/Projects/vic3_mods_out/PowerBlocksExpanded` — `[1.13] Power Blocs Expanded`,
  id `3623185901`, `supported_game_version = 1.13*`, `relationships = []`

Предыдущая версия отчёта была основана на эвристике «одинаковый ключ у обоих = конфликт»
и привела к ложному выводу про on_actions. Здесь — проверка по фактам.

---

## 1. Пересечение по путям файлов

**1 файл: `thumbnail.png`.** Косметика, оба мода задают `picture` в metadata. Не конфликт.

Ни одного общего `.txt`, `.gui` или `.yml`.

## 2. Пересечение по ключам в `common/`

Скан всех топ-левел ключей обоих модов (с нормализацией префиксов
`REPLACE:` / `INJECT:` / `TRY_*`), по категориям:

| категория | общих ключей |
|---|---|
| `common/on_actions` | 2 — `on_monthly_pulse`, `on_monthly_pulse_country` |
| **все остальные** | **0** |

Категории, которые есть у PBE: `cohesion_levels`, `defines`, `diplomatic_actions`,
`diplomatic_plays`, `game_concepts`, `game_rules`, `history/power_blocs`, `messages`,
`modifier_type_definitions`, `on_actions`, `power_bloc_identities`,
`power_bloc_principle_groups`, `power_bloc_principles`, `production_method_groups`,
`production_methods`, `script_values`, `scripted_effects`, `scripted_guis`,
`scripted_rules`, `scripted_triggers`, `static_modifiers`.

Из них у Morgenröte вообще отсутствуют: `defines`, `cohesion_levels`,
`power_bloc_*` (все три), `diplomatic_plays`, `scripted_rules`.
В остальных общих категориях (`game_rules`, `scripted_effects`, `scripted_triggers`,
`script_values`, `scripted_guis`, `static_modifiers`, `modifier_type_definitions`,
`production_methods`, `production_method_groups`, `history`, `messages`, `game_concepts`)
— **ни одного одинакового ключа**.

Отдельно: PBE переопределяет 7 ванильных `modifier_type_definitions`
(`country_influence_add`, оба `state_bureaucrats_investment_pool_*` и др.) —
Morgenröte ни один из этих семи не трогает.

## 3. Локализация и события

- Общих ключей локализации: **0** (у PBE ровно один файл, `vokaes_power_blocs_l_english.yml`)
- Общих id событий: **0**

## 4. On_actions — почему это не конфликт

`common/on_actions/` в 1.13 **аддитивен**: корневой хук, объявленный в разных файлах,
складывается, а не перезаписывается.

Доказательство внутри самого Morgenröte (29 файлов on_actions):

- `on_yearly_pulse_country` объявлен в **19** файлах мода
  (`MFE_main_flavor_pulse`, `mr_ai`, `mr_arts_artists`, `mr_arts_elgar`, `mr_arts_gaudi`,
  `mr_arts_klimt`, `mr_arts_manzoni`, `mr_country_flavor_matsuura_japan`,
  `mr_general_dufour`, `mr_general_pius`, `mr_general_rapanui`, `mr_general_swe_nor_yearly`,
  `mr_general_yearly`, `mr_science_academics`, `mr_science_agassiz`, `mr_science_andersson`,
  `mr_science_dubois`, `mr_science_lepsius`, `mr_science_panum`, `mr_science_theiler`,
  `mr_science_verrier`, `mr_sports_curtiss`, `mr_sports_douglas`, `mr_sports_vikelas`)
- `on_monthly_pulse_country` — в **6** (`mr_ai`, `mr_arts_artists`, `mr_arts_manzoni`,
  `mr_on_actions`, `mr_science_academics`, `mr_science_agassiz`, `mr_science_lepsius`)

Если бы движок оставлял только последнее объявление, почти весь контент Morgenröte
молча не запускался бы. Мод работает — значит хуки мерджатся.
Межмодовое поведение то же самое: файлы называются по-разному
(`mr_*.txt` против `vokaes_power_bloc_on_actions.txt`), полного перекрытия файла нет.

Итог: Morgenröte сохраняет `mr_on_monthly_pulse`, `mr_on_monthly_pulse_country` и все
19 годовых хуков; PBE сохраняет `vokaes_weekly_global_on_action` ×4 и
`vokaes_dynamic_modifier_on_action` ×4. Мерджить нечего.

## 5. Что скрипт не ловит — проверено вручную

| проверка | результат |
|---|---|
| **Потолок 128 товаров** | ваниль 53 + Morgenröte 5 (`air_travel`, `good_uranium`, `elgar_instruments`, `elgar_music`, `manzoni_prints`) + PBE 0 = **58**. Запас огромный |
| **Группы законов** | у PBE нет ни `common/laws`, ни `common/law_groups` — сверять нечего |
| **Триггеры по building_group** | у PBE нет ни `common/buildings`, ни `common/building_groups`. Триггеры Morgenröte (Tesla, Agassiz, Theiler) фильтруют по `bg_*`, но PBE в эти иерархии ничего не добавляет |
| **`.gui`** | общих файлов нет. PBE перекрывает `power_bloc_panel.gui` и `power_bloc_formation_panel.gui`; Morgenröte в своих 43 gui-файлах не упоминает `power_bloc` / `principle` / `cohesion` ни разу. Пропавших виджетов у Morgenröte не возникает |
| **`common/defines`** | у Morgenröte их нет вообще — блок `NPowerBlocs` от PBE вне конкуренции |
| **PM/PMG PBE** | `pmg_entrenched_building_manor_house` и `pmg_sovereign_wealth_fund_company_headquarter` в 1.13 никуда не подключены (в моде нет `common/buildings`, инжектов нет). Мёртвый код — Morgenröte с ним пересечься не может |
| **Ссылки Morgenröte на механику блоков** | только чтение ванильными триггерами: `is_in_same_power_bloc` (×4, Vikelas scripted_effects), `is_power_bloc_leader` / `num_power_bloc_members = 4` / `any_power_bloc_member` (Vikelas scripted_gui). Всё это работает и с переписанными PBE идентичностями |

## 6. Что было удалено

`common/on_actions/zz_morgenrote_pbe_on_actions.txt` → `vic3_mods/_to_delete/morg+pbe_2026-08-21/`

Файл был вреден:

1. Построен на неверной посылке «последний мод выигрывает» и мерджил то, что и так мерджится.
2. Ссылался на `kates_weekly_global_on_action` / `kates_dynamic_modifier_on_action`.
   **PBE переименовал весь префикс `kates_` → `vokaes_`** — обе строки теперь указывают
   в пустоту, молча (неизвестный вход в списке on_action пропускается без записи в `error.log`).
3. Загружаясь последним, он не заменял списки Morgenröte и PBE, а добавлялся к ним —
   то есть в лучшем случае дублировал вызовы PBE, а после переименования просто ничего не делал.
4. Комментарий указывал на `Morgenrote/morgen/common/on_actions/` — такого пути больше нет,
   `common/` у Morgenröte лежит в корне мода.

## 7. Когда пересматривать

- PBE вернёт `common/buildings/` или `common/building_groups/` (в 1.12-версии они были)
- PBE начнёт переопределять `modifier_type_definitions`, которые есть у Morgenröte
- Morgenröte заведёт `common/defines` или собственный power-bloc контент
  (принципы, идентичности, cohesion levels)
