# TheGreatRevision vs PowerBlocksExpanded — conflict report (key-level heuristic)

- TheGreatRevision root: `/sessions/rcw-01xmxiycnlz45uo14jxa2es1/mnt/Projects/vic3_mods_out/TheGreatRevision`
- PowerBlocksExpanded root: `/sessions/rcw-01xmxiycnlz45uo14jxa2es1/mnt/Projects/vic3_mods_out/PowerBlocksExpanded`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/diplomatic_actions — 1 duplicates
- `force_regime_change`
  - TheGreatRevision: `common/diplomatic_actions/TGR_ADJUSTMENTS_power_bloc_force_regime_change.txt`
  - PowerBlocksExpanded: `common/diplomatic_actions/vokaes_power_bloc_actions.txt`

### common/modifier_type_definitions — 2 duplicates
- `country_influence_add`
  - TheGreatRevision: `common/modifier_type_definitions/TGR_POLITICS_modifier_types.txt`
  - PowerBlocksExpanded: `common/modifier_type_definitions/vokaes_power_bloc_modifier_types.txt`
- `state_bureaucrats_investment_pool_contribution_add`
  - TheGreatRevision: `common/modifier_type_definitions/TGR_LOANS_todo_sort_into_other_files.txt`
  - PowerBlocksExpanded: `common/modifier_type_definitions/vokaes_power_bloc_modifier_types.txt`

### common/on_actions — 1 duplicates
- `on_monthly_pulse_country`
  - TheGreatRevision: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TheGreatRevision: `common/on_actions/TGR_GER_UNIFICATION_code_on_actions.txt`
  - TheGreatRevision: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
  - PowerBlocksExpanded: `common/on_actions/vokaes_power_bloc_on_actions.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**

---

## Разбор от 2026-08-21 (TGR 2.0 / 1.13.10 × PBE 1.13*)

Скрипт даёт 4 совпадения ключей. Из них мерджа требует **одно**.

### 1. `force_regime_change` — мерджим, это весь компач

`common/diplomatic_actions/zz_pbe_tgr_force_regime_change.txt`, `REPLACE_OR_CREATE:`.

PBE определяет ключ **обычным ключом, без `REPLACE:`**, и грузится после TGR — значит без компача версия TGR теряется целиком, молча.

Что вносит каждый:

| | ваниль 1.13 | TGR | PBE |
|---|---|---|---|
| cohesion floor | 0.1 | **0.25** | 0.25 (внутри `OR`) |
| tenure | 5 лет | **1 год** | 5 лет (внутри `OR`) |
| гейт по game rule | — | — | **`OR = { has_game_rule = vokaes_..._diplo_action_changes_enabled ; AND = { cohesion, tenure } }`** |
| prestige | голый триггер | голый триггер | **обёрнут в `custom_tooltip PRESTIGE_THREE_TIMES_POSSIBLE`** |
| `installed_regime` | `days = normal_modifier_time` | **`months = 24`** | `months = normal_modifier_time` |
| infamy incident | — | — | **`vokaes_force_regime_change_infamy`** |
| cohesion cost | есть | есть | **потеряна** |
| блок `ai` | −25/−50 | −50/−100 | −50/−100 (идентично TGR) |
| венгерские `trigger_if` + `NOT ally` | есть | вырезаны | вырезаны |

Решения в мердже:

- **Структура — PBE, числа — TGR.** Числа TGR (0.25 / 1 год) кладём *внутрь* ветки `AND` у PBE, а не рядом с `OR`. Прошлая версия компача поднимала их наружу — из-за этого game rule PBE переставало что-либо значить: игрок платил infamy **и** всё равно упирался в стену требований.
- **`months = 24` от TGR.** `normal_modifier_time = 1825`, ваниль скармливает его `days`. У PBE это `months` → 152 года, то есть навсегда. Берём литерал TGR — заодно фикс.
- **Cohesion cost возвращена.** PBE выкидывает `add_cohesion_percent = scaled_cohesion_cost` целиком; при выключенном правиле действие оказывается вообще бесплатным. Похоже на недосмотр, а не на замысел.
- **Венгерские гейты не восстанавливаем.** Оба мода убрали их независимо друг от друга — вернуть их значило бы придумать поведение, которого не хочет ни один автор.
- **Блок `ai` не мерджится** — у TGR и PBE он совпадает слово в слово.

**Главное за это обновление:** PBE переименовал префикс `kates_` → `vokaes_`. Старый компач ссылался на `kates_power_bloc_rule_diplo_action_changes_enabled` и `kates_force_regime_change_infamy`. Отсутствующие game rule и script value **не дают ошибки в логе** — ветка infamy просто никогда не срабатывала. Проверять такие ссылки грепом по чужому моду при каждом обновлении.

### 2. `country_influence_add` — компач не нужен

Только `decimals`: TGR `0`, PBE `1` (= ваниль). Разница чисто в отображении числа в тултипе. PBE грузится последним → остаётся ванильное `1`. Пин не даёт ничего.

### 3. `state_bureaucrats_investment_pool_contribution_add` — компач не нужен

Только `color`: TGR `neutral`, PBE `good` (= ваниль). Тоже отображение. **Файл `common/modifier_type_definitions/zz_pbe_tgr_modifier_types.txt`, пинивший это значение, удалён** (в `_to_delete/`): он пинил ровно тот результат, который и так получается сам.

### 4. `on_monthly_pulse_country` — конфликта нет

`common/on_actions/` в 1.13 аддитивен, файлы называются по-разному, оба списка складываются. См. сводку по PBE, п. 8.

### Проверено дополнительно (скриптом не ловится)

- **GUI** — пересечения нет: TGR трогает только `gui/budget_panel.gui`, PBE — `gui/power_bloc_panel.gui` и `gui/power_bloc_formation_panel.gui`.
- **Товары** — 53 у пары, ровно ванильный набор: TGR только переопределяет ванильные 53 через `REPLACE_OR_CREATE:`, PBE не добавляет ни одного. До потолка 128 далеко.
- **Power bloc-домены** — у TGR нет ни `power_bloc_principles`, ни `power_bloc_identities`, ни `cohesion_levels`, ни `scripted_rules`. Всё, что PBE переопределяет в них (5 идентичностей, 5 уровней cohesion, 9 ванильных принципов, `can_impose_law_default`, `can_lead_power_bloc`), TGR не трогает.
- **Локализация и id ивентов** — 0 пересечений.
- **TGR_Loans** вынесен в отдельный мод, но `common/modifier_type_definitions/TGR_LOANS_todo_sort_into_other_files.txt` лежит и в самом TGR, содержимое идентично. На вывод не влияет — см. п. 3.
