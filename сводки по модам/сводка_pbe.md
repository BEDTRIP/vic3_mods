### Общая сводка по `PowerBlocksExpanded` (PBE)

Мод **почти целиком посвящён системе Power Bloc’ов** (DLC-фича `power_bloc_features`): расширяет лимиты/прогрессию мандатов, добавляет много новых **principles**, частично **переписывает ванильные identities**, добавляет новые **дипло-экшены/плеи**, и патчит **UI** панели Power Bloc’ов.

---

### Что именно меняется в игре (по `common/`)

- **Лимиты/дефайны Power Bloc’ов** (`common/defines/kates_power_bloc_defines.txt`)
  - **стоимость влияния на создание блока = 0**
  - **MAX_PRINCIPLES = 12**
  - **MAX_MANDATES = 100**
  - **MAX_MANDATE_PROGRESS = 750**
  - (и т.п.)

- **Игровые правила (настройки мода в rules)** (`common/game_rules/kates_power_bloc_game_rules.txt`)
  - включение/выключение: **новые принципы**, **новая “cohesion” логика**, **переработанный mandate progress**, **переключение identity без роспуска**, **правки дипло-действий**, **Holy Wars на GP**
  - параметры: **кол-во слотов принципов (4–12)**, **скорость прогресса**, **рост стоимости мандатов**, **лимит сохранённых мандатов**, и т.д.

- **Новые/изменённые principles и principle groups** (`common/power_bloc_principles/*`, `common/power_bloc_principle_groups/*`)
  - добавлено **очень много новых принципов (117 уровней/записей)**, включая уникальные для:
    - **Trade League** (дерегуляция/единый рынок облигаций/валютный союз/совет членов/и т.п.)
    - **Sovereign Empire** (economic imperialism, leviathan, pax imperia, preferential colonial trade…)
    - **Ideological Union** (entrenched elite, status quo, direct oversight, international criminal court…)
    - **Military Treaty Organization** (logistics network, wonder weapons, joint exercises…)
    - **Religious** (holy wars, champion the true faith, henotheism…)
  - часть ванильных принципов **модифицирована** (в файле прямо есть секция `###### GENERIC MODIFIED`).

- **Переписанные identities (REPLACE)** (`common/power_bloc_identities/kates_power_bloc_identities.txt`)
  - `REPLACE:` для **5 ванильных идентичностей**:
    - `identity_trade_league`
    - `identity_sovereign_empire`
    - `identity_ideological_union`
    - `identity_military_treaty_organization`
    - `identity_religious`
  - меняются их базовые модификаторы, логика **cohesion** (формулы), штрафы за членов, доступные перки лидера и т.д.

- **Cohesion levels** (`common/cohesion_levels/kates_cohesion_levels.txt`)
  - новые пороги: 0/20/40/60/80 и эффекты на **leverage generation**, AI unification support и т.п.

- **Mandate progress — перерасчёт и “diminishing returns”** (`common/script_values/kates_power_bloc_script_values.txt`)
  - переработанная формула прогресса мандатов: вклад **членов** + вклад **cohesion** + штраф за мало членов + множители правил
  - “diminishing returns”: стоимость новых мандатов растёт с каждым использованным уровнем принципов/мандатом (настраивается правилами)

- **Переключение identity без роспуска (reform)** (`common/scripted_effects/kates_power_bloc_scripted_effects.txt`, `common/scripted_guis/kates_power_bloc_scripted_gui.txt`)
  - “реформирование” блока: временно “распускает”/пересобирает членство, **сбрасывает cohesion в 0**, режет leverage, даёт временные free mandates, ухудшает отношения с членами, поднимает liberty desire у субъектов (это отражено и в локализации)

- **Новые дипломатические действия/пакты и дипломатическая игра** (`common/diplomatic_actions/*`, `common/diplomatic_plays/*`)
  - для **лидера блока**:
    - `force_become_subject` (внутри блока, при условиях стажа/престижа/кохезии)
    - `force_regime_change`
    - `force_state_religion`
  - **Holy War**:
    - дипло-экшен `holy_war_action` → создаёт дипло-плей `dp_holy_war`
    - события `events/kates_power_bloc_events.txt` зовут сторонников по религии
    - при enforced: может **поменять гос.религию и конвертить население**
  - **Foreign investment**:
    - скрытый пакт `kates_foreign_investment_agreement`: авто-выдача mutual foreign investment rights **между всеми членами блока**, пока активен соответствующий принцип
  - **Forced privatization**:
    - пакт/экшен `force_privatization` как overlord action, включает `country_force_privatization_bool`/`country_disable_nationalization_bool`

- **On-actions / “движок обслуживания”** (`common/on_actions/kates_power_bloc_on_actions.txt`)
  - хуки на:
    - старт дипло-плея (авто-помощь против революций при принципе)
    - enforced wargoal (holy war enforcement)
    - регулярные пульсы (динамические модификаторы, авто-пакты foreign investment, переключение “ванильных” модификаторов при отключённых правилах)

- **Новые типы модификаторов** (`common/modifier_type_definitions/kates_power_bloc_modifier_types.txt`)
  - добавлены кастомные bool/скейлящиеся модификаторы (например, “can declare holy wars”, “auto help vs revolutions”, скейл по числу членов/субъектов, лимит-максы и т.п.)

- **Патчи к зданиям/ПМ** (`common/buildings/*`, `common/production_methods/*`, `common/production_method_groups/*`)
  - переопределяет/добавляет сущности вроде `building_manor_house`, `building_company_headquarter`, `building_company_regional_headquarter` (указаны как **non-buildable/non-expandable**)
  - добавляет PM/PMG, завязанные на новые принципы (например **Entrenched Elite** для manor house, **Sovereign Wealth Fund** для company HQ)

- **Стартовые правки истории power blocs** (`common/history/power_blocs/zzz_kates_power_blocs.txt`)
  - условные замены стартовых принципов для некоторых стран (GBR/AUS/PRU/RUS/TUR) в зависимости от правил/“free founding mandates”.

---

### UI / локализация (важно для компачей)

- **GUI-патчи** (`gui/power_bloc_panel.gui`, `gui/power_bloc_formation_panel.gui`)
  - расширяют ширину панелей и, главное, **поддерживают до 12 слотов принципов** + кнопки **Switch Identity/Reform**
- **Локализация**
  - `localization/english/kates_power_blocs_l_english.yml`: почти вся текстовка мода (принципы, правила, тултипы, holy war, identity switching)
  - `localization/replace/english/kates_power_bloc_l_english.yml`: точечные **replace**-ключи ванили (в т.ч. тултипы прогресса мандатов)

---

### Главные точки конфликтов для компачей

- **`REPLACE:` identities**: любой мод, который тоже трогает `power_bloc_identities` (или баланс cohesion/перк-лидера) будет конфликтовать.
- **GUI**: любые UI-моды Power Bloc’ов/панелей почти наверняка пересекутся с `power_bloc_panel.gui` и `power_bloc_formation_panel.gui`.
- **Defines NPowerBlocs**: моды, меняющие лимиты/стоимости power bloc’ов, будут конфликтовать по `common/defines`.
- **Scripted rules (`can_impose_law_default`)**: если другой мод тоже патчит правила навязывания законов — нужен мердж.
- **Buildings/PM**: моды, меняющие `building_manor_house` или company HQ / их PMG — потенциальный конфликт.
- **On-actions**: если другой мод “перезаписывает” те же on_actions-блоки вместо добавления — может отвалиться функционал PBE.

---

### Ключевые файлы (куда смотреть в первую очередь)

- **Power Bloc ядро**:  
  - `common/power_bloc_principles/kates_power_bloc_principles.txt`  
  - `common/power_bloc_principle_groups/kates_power_bloc_principle_groups.txt`  
  - `common/power_bloc_identities/kates_power_bloc_identities.txt`  
  - `common/script_values/kates_power_bloc_script_values.txt`  
  - `common/scripted_effects/kates_power_bloc_scripted_effects.txt`  
  - `common/on_actions/kates_power_bloc_on_actions.txt`
- **Дипломатия**:  
  - `common/diplomatic_actions/kates_power_bloc_actions.txt`  
  - `common/diplomatic_plays/kates_power_bloc_plays.txt`  
  - `events/kates_power_bloc_events.txt`
- **UI**:  
  - `gui/power_bloc_panel.gui`, `gui/power_bloc_formation_panel.gui`
