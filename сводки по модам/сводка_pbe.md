# Сводка по `PowerBlocksExpanded` (PBE)

- **Версия мода:** `1.13*` (`.metadata/metadata.json`: `name = "[1.13] Power Blocs Expanded"`, id `3623185901`, `supported_game_version = 1.13*`, `relationships = []`)
- **Дата сверки:** 2026-08-19
- **Эталон сравнения:** `.vanillaVIC3` (1.13)
- **Объём:** 67 файлов, из них 23 в `common/`, 1 в `events/`, 2 в `gui/`, 1 файл локализации, остальное — `gfx` (иконки принципов и дипло-действий)

> **Главное изменение с прошлой сверки: весь префикс мода переименован `kates_` → `vokaes_`.**
> Затронуты имена файлов, on_action'ов, scripted_effects, script_values, static_modifiers, модификаторов и game rules. Любой компач, ссылавшийся на `kates_*`, теперь ссылается в пустоту — молча, ошибка вылезет только как «функционал не работает».
>
> Второе: **`common/buildings/` из мода исчезла**, `localization/replace/` тоже. Старая сводка утверждала обратное — это было верно для версии под 1.12.

---

## Что мод меняет

### Дефайны — `common/defines/vokaes_power_bloc_defines.txt`

Блок `NPowerBlocs` целиком:

```
POWER_BLOC_INFLUENCE_COST = 0
MAX_PRINCIPLES            = 12
MAX_MANDATES              = 100
INITIAL_PRINCIPLE_LEVELS  = 1
MAX_MANDATE_PROGRESS      = 750
```

### Игровые правила — `common/game_rules/vokaes_power_bloc_game_rules.txt` (14 групп)

Переключатели: `enable_new_principles`, `enable_new_cohesion`, `enable_mandate_progress`, `enable_identity_switch`, `diplo_action_changes`, `holy_wars_gp`, `principle_restrictions`.
Параметры: `principle_slots` (4–12), `mandate_progress_speed`, `mandate_cost_growth`, `max_saved_mandates`, `free_founding_mandates`, `late_founding_mandates`, `low_member_penalty`.

Почти весь контент мода закрыт условием `has_game_rule = vokaes_power_bloc_rule_enable_new_principles_enabled` — при выключенном правиле принципы невидимы и невыбираемы.

### Принципы — `common/power_bloc_principles/` (117 записей) и `common/power_bloc_principle_groups/` (37 групп)

Новые группы по идентичностям:

- **Trade League** — deregulation, unified_bond_market, collective_bargaining_power, **currency_union**, member_council, private_tax_collectors
- **Sovereign Empire** — economic_imperialism, leviathan, imperial_prerogative, colonial_manpower, pax_imperia, preferential_colonial_trade
- **Ideological Union** — entrenched_elite, status_quo, economic_consensus, direct_oversight, international_criminal_court, righteous_cause
- **Military Treaty Organization** — conventions_of_war, logistics_network, your_country_needs_you, chivalrous_pursuit, wonder_weapons, joint_training_exercises
- **Religious** — holy_wars, champion_the_true_faith, henotheism, organised_religion, alms_for_the_poor, people_of_faith
- **Общие** — propaganda, unity, development_fund, sovereign_wealth_fund, settlement_drive, antitrust_commission, creative_legislature

**Переопределяет 9 ванильных принципов** (обычным ключом, без `REPLACE:` — полная замена записи): `principle_advanced_research_1..3`, `principle_internal_trade_1..3`, `principle_vassalization_1..3`.

### Идентичности — `common/power_bloc_identities/vokaes_power_bloc_identities.txt`

`REPLACE:` для всех пяти ванильных: `identity_trade_league`, `identity_sovereign_empire`, `identity_ideological_union`, `identity_military_treaty_organization`, `identity_religious`.

### Cohesion — `common/cohesion_levels/vokaes_cohesion_levels.txt`

Переопределены все пять ванильных уровней (`cohesion_level_very_low` … `very_high`) — пороги и эффекты на leverage generation / поддержку объединения у ИИ.

### Мандаты — `common/script_values/vokaes_power_bloc_script_values.txt` (39 значений)

Переработанная формула прогресса (вклад членов + вклад cohesion + штраф за малое число членов + множители правил) и «diminishing returns»: `power_bloc_diminishing_multiplier`, `power_bloc_diminishing_return_exponent_base`, `power_bloc_mandates_plus_principle_levels`.

### Смена идентичности без роспуска

`common/scripted_effects/vokaes_power_bloc_scripted_effects.txt` (`power_bloc_reform_action`, `power_bloc_reform_action_2`) + `common/scripted_guis/vokaes_power_bloc_scripted_gui.txt` (`power_bloc_prereform`, `power_bloc_reform`, `power_bloc_reform_2`, `vokaes_power_bloc_rule_enable_identity_switch_gui`).

Реформа обнуляет cohesion, режет leverage, выдаёт временные free mandates, портит отношения с членами, поднимает liberty desire у субъектов.

### Дипломатия — `common/diplomatic_actions/` (6) и `common/diplomatic_plays/` (1)

- `force_become_subject`, `force_regime_change`, `force_state_religion` — действия лидера блока внутри блока
- `holy_war_action` → дипло-плей `dp_holy_war`; `events/vokaes_power_bloc_events.txt` созывает единоверцев; при enforced — смена госрелигии и конверсия населения
- `vokaes_foreign_investment_agreement` — скрытый пакт, автоматически выдаёт mutual foreign investment rights между всеми членами блока, пока активен соответствующий принцип
- `force_privatization` — overlord action, включает `country_force_privatization_bool` / `country_disable_nationalization_bool`

### Навязывание законов — `common/scripted_rules/vokaes_power_bloc_scripted_rules.txt` (12)

`REPLACE:unlock_power_bloc_principle_slot_3` … `_12` (десять слотов), плюс полное переопределение ванильных `can_lead_power_bloc` и `can_impose_law_default`.
Опирается на `common/scripted_triggers/vokaes_power_bloc_triggers.txt`: `vokaes_custom_law_imposition_trigger` + варианты `_economy`, `_home_affairs`, `_welfare`.

### On-actions — `common/on_actions/vokaes_power_bloc_on_actions.txt`

| ванильный хук | что вешает |
|---|---|
| `on_diplomatic_play_started` | `vokaes_power_bloc_revolution_on_action` — автопомощь против революций при принципе |
| `on_wargoal_enforced` | `vokaes_power_bloc_holy_war_enforced_on_action` |
| `on_monthly_pulse_country` | `vokaes_dynamic_modifier_on_action` ×4 через `delay = { days = 7/14/21 }` |
| `on_monthly_pulse` | `vokaes_weekly_global_on_action` ×4 через те же задержки |

### Типы модификаторов — `common/modifier_type_definitions/` (37)

Новые: `country_can_declare_holy_wars_bool`, `power_bloc_members_auto_help_against_revolutions_bool`, `country_can_impose_same_lawgroup_{economy,home_affairs,welfare}_in_power_bloc_bool`, `mandate_progress_from_{cohesion,members}_mult`, `country_*_from_bloc_members_mult` (influence, trade, minting, bureaucracy, interest_rate) с парными `_max`.

**Переопределяет 7 ванильных типов:** `country_force_privatization_bool`, `country_influence_add`, `country_institution_cost_institution_home_affairs_mult`, `country_institution_cost_institution_social_security_mult`, `power_bloc_cohesion_per_member_add`, `state_bureaucrats_investment_pool_contribution_add`, `state_bureaucrats_investment_pool_efficiency_mult`.

### Статические модификаторы — `common/static_modifiers/` (20)

`vokaes_*_modifier` (influence/minting/legitimacy/trade/bureaucracy/interest per bloc member или per subject) плюс `*_vanilla_modifier` на каждую из пяти идентичностей — они возвращают ванильное поведение, когда правила мода выключены (`vokaes_set_rule_modifier`).

### История — `common/history/power_blocs/zzz_vokaes_power_blocs.txt`

Единственный ключ `POWER_BLOCS`. Условная замена стартовых принципов у GBR/AUS/PRU/RUS/TUR в зависимости от правил и free founding mandates. Префикс `zzz_` — грузится последним.

### Production methods — определены, но никуда не подключены

`common/production_method_groups/` определяет `pmg_entrenched_building_manor_house` и `pmg_sovereign_wealth_fund_company_headquarter`, `common/production_methods/` — четыре PM к ним (`pm_manor_house_entrenched_interests_3` / `_no_effect`, `pm_company_headquarter_swg_3` / `_no_effect`, все с `unlocking_principles`).

**Но `common/buildings/` в моде нет, и ни один `INJECT:building_*` эти PMG не подключает** — поиск по всему моду даёт только определение и строку локализации. То есть в версии 1.13 эти два PMG — мёртвый код: принципы Entrenched Elite и Sovereign Wealth Fund через PM не работают.

Это либо баг PBE, либо расчёт на то, что PMG подключит какой-то другой мод. Для компачей важно: **PBE ничего не делает с `building_manor_house` и `building_company_headquarter`**, старое утверждение сводки об обратном устарело.

---

## GUI

Перекрывает два ванильных файла целиком: `gui/power_bloc_panel.gui`, `gui/power_bloc_formation_panel.gui`.

Копии сделаны с 1.13 — диффы против ванили `−32/+169` и `−7/+45`. Признака устаревшей копии («минус сотни строк») нет, `interface/` мод не трогает, все `using =` шаблоны берутся из ванили.

Добавлено: кнопка Switch Identity / Reform, кнопка Invite в двух вариантах (с реформой и без, переключаются через `GetScriptedGui('vokaes_power_bloc_rule_enable_identity_switch_gui')`), поддержка 12 слотов принципов, `reform_power_bloc` в панели формирования.

**Что PBE при этом теряет из ванили 1.13** (проверить при следующем обновлении — возможно, автор чинил под старую базу):

- в `power_bloc_panel.gui` вырезана вся секция `### SEARCH` — `search_bar` с `blockoverride "editbox_name" { name = "member_search_edit" }`, вместе с `visible = "[... Country.MatchesSearchQuery(...)]"` у строк списка и `ignoreinvisible = yes`. **Поиск по членам блока в панели пропадает.**
- вырезана кнопка сортировки `[PowerBloc.SortMembers('leverage_advantage')]`
- вместо ванильных `[PowerBloc.GetShips|v]` / `@ships!` стоит `[PowerBloc.GetFlotillas|v]` / `@flotillas!`, а также `[Country.GetNumShips|0]` заменено в двух местах. В ванильных `.gui` 1.13 функции `GetFlotillas` нет ни разу — если её нет и в движке, панель будет писать в `error.log` при каждом открытии. **Проверить по `error.log` при следующем прогоне.**
- `OpenCharacterPanel` заменено на `OpenCommanderPanel` в пяти местах

Файлы PBE имеют смешанные CR/CRLF-окончания строк — `grep` по ним из bash молча ничего не находит, искать через `python3`.

---

## Локализация

Один файл: `localization/english/vokaes_power_blocs_l_english.yml` — принципы, правила, тултипы, holy war, смена идентичности. Папки `localization/replace/` в версии 1.13 нет.

---

## Точки конфликтов для компачей

Отсортировано по вероятности.

1. **`REPLACE:` пяти идентичностей + переопределение 5 уровней cohesion.** Любой мод, трогающий identity или формулу cohesion, конфликтует наглухо.
2. **Полное переопределение 9 ванильных принципов** (`advanced_research`, `internal_trade`, `vassalization`) — обычным ключом, так что побеждает загруженный последним.
3. **`can_impose_law_default` и `can_lead_power_bloc`** — переопределены целиком. Мод, который тоже их патчит, требует ручного мерджа.
4. **7 переопределённых ванильных `modifier_type_definitions`** — в частности `country_influence_add` и оба `state_bureaucrats_investment_pool_*`. Экономические моды, трогающие investment pool, — первые кандидаты на конфликт.
5. **`gui/power_bloc_panel.gui` и `gui/power_bloc_formation_panel.gui`** — любой UI-мод панелей блока.
6. **`NPowerBlocs` в `common/defines`** — моды, меняющие лимиты и стоимости блоков.
7. **`common/history/power_blocs/`** — `zzz_` грузится последним, но `POWER_BLOCS` в history аддитивен, так что здесь обычно обходится.
8. **On-actions — конфликта нет.** `common/on_actions/` в 1.13 аддитивен: файл PBE называется `vokaes_power_bloc_on_actions.txt`, чужой файл называется иначе, оба списка складываются. Не писать мерджащие компачи под это.

## Чего у PBE точно нет (не проверять заново)

`common/goods` (0 товаров — потолок 128 не двигает), `common/laws`, `common/law_groups`, `common/buildings`, `common/building_groups`, `common/technology`, `common/institutions`, `common/companies`, `interface/`, `localization/replace/`.

## Статус пар

| пара | статус | дата |
|---|---|---|
| E&F + PBE | `noneed` — подтверждено, см. `_ef/ef+pbe noneed/conflicts_ef_vs_pbe_report.md` | 2026-08-19 |
| Morgenröte + PBE | `noneed` | — |
| PBE + PSC | `noneed` | — |
| PBE + TR+Kuromi | `noneed` | — |
| PBE + VC | `noneed` | — |
