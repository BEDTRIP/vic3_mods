## Шапка

**Версии в репозитории**: `Tech Res 13.05.2026` (`t&r`, metadata `1.6'`, `1.13.*`),
`KAI 24.07.2026` (`kai`, metadata `7.5`, `1.13.*`). Модуль `cmf` лежит отдельно —
`vic3_mods_out/_cmf` (`CMF 13.08.2026`).
**Сверено с файлами: 21.08.2026.**

### Уточнено 21.08.2026 (разбор пары PSC + T&R)

- **Строительные PM: в 13.05 T&R перешёл с `REPLACE:` на `INJECT:`-дельты.**
  `ztr_construction_production_methods.txt` схлопнулся со 157 строк до 38: раньше мод
  целиком переопределял `pm_wooden_buildings / pm_iron_frame_buildings /
  pm_steel_frame_buildings / pm_arc_welded_buildings`, теперь правит их дельтами —
  iron `commonores +5, iron -5, wood -5`; steel `alloys +10, steel -10`;
  arc `alloys +10, steel -10, country_construction_add -2`; wooden не трогает вовсе.
  **Любой компач, скопировавший старые полные блоки, разъехался.**
- **Лестница очков строительства (ваниль + дельты T&R): 2 / 5 / 10 / 13 / 15**
  (wooden / iron frame / steel frame / arc welded / prefab concrete).
  До 13.05 было 2 / 5 / 9 / 11 / 13.
- **`pm_prefabricated_concrete_buildings`** создаётся T&R (в ванили его нет) и
  инжектится в `pmg_base_building_construction_sector`. В 13.05 у него
  `country_construction_add` 13 -> 15 и `goods_input_electricity_add` 40 -> 30.
- **С PSC пересечений ровно три ключа** (`scan_conflicts.py`) — те самые три
  строительных PM. Остальное аддитивно: `BUILDINGS`, `GLOBAL`,
  `on_acquired_technology`. `building_construction_sector` T&R не трогает вообще,
  `common/defines` — только `NWar`, `NEconomy`, `NPops`, без `NCountry`.
- **KAI x PSC: компач не нужен.** Единственное пересечение —
  `INJECT:building_construction_sector { ai_value }` в `kai/common/buildings/kai_buildings.txt`;
  оно затирается `REPLACE:` от PSC (`kai_` грузится раньше `zz_PSC_`), но потери нет:
  PSC уже держит ту же логику у себя, там дословно лежит комментарий
  `# KAI: Prefer states with iron` и та же `add = 500`, плюс бонус за первый сектор.
- **Товаров ваниль 53 + PSC 4 + T&R 39 + KAI 0 = 96**, с `concrete_construction`
  из компача — 97 при потолке 128.

### Что уточнено 21.08.2026 (разбор E&F + T&R)

- **Товаров T&R добавляет 39** поверх ванили: `advancedores, ai_systems, alloys,
  aluminium, androids, batteries, bauxite, business_data, civil_planes, commonores,
  computer, copper, copperwires, cosmetics, electroniccomponents, elgar_instruments,
  elgar_music, gas, global_electricity, good_uranium, heavy_fuel, homeappliances,
  interactive_entertainment, light_fuel, lubricant, manzoni_prints, on_demand_goods,
  organized_data, pharmaceuticals, plastics, processors, rare_earths, raw_data,
  robotics, softwares, space_assets, telecommunications, televisions, water`.
  С Morgenröte пересекаются четыре (`elgar_*`, `manzoni_prints`, `good_uranium`),
  то есть поверх MR это +35. **Ваниль 53 + E&F с хотфиксом 65 + T&R 39 = 157 при
  потолке 128** — E&F и T&R вместе не запускаются без дополнительной резки.
- **Новое в версии 13.05 относительно предыдущей**: здания
  `building_computer_assembly_plant`, `building_fusion_power_plant`,
  `building_power_grid_station`; группа `pmg_power_transmission`
  (`pm_direct_current` / `pm_half_current` / `pm_alternating_current`) в
  `building_power_plant` — законо-зависимая витрина `lawgroup_national_electric_system`,
  сами PM модификаторов не несут; `pmg_data_optimization_light_industry` с
  электростанции **снят**; у `building_automotive_industry` дата-оптимизация
  переведена на `pmg_data_optimization_heavy_industry_algorithmic_dispatch`.
- **`REPLACE:` ванильных зданий у T&R ровно три**: `building_automotive_industry`,
  `building_synthetics_plant`, `building_power_plant` (`ztr_vanilla_modified_buildings.txt`).
  Всё остальное — `INJECT:` (17 зданий там же + 30 в `ztr_vanilla_optimization_buildings.txt`)
  и `REPLACE_OR_CREATE:` для семи зданий Morgenröte. Золото
  (`building_gold_mine`, `building_gold_field`) T&R не трогает вообще.
- **Законы шахт работают поимённо, не по `building_group`**:
  `law_polluting_mining_banned` сносит `building_coal_mine`, `building_lead_mine`,
  `building_sulfur_mine`; `possible`-фильтры в зданиях тоже перечисляют законы
  поимённо. Чужие шахты в дочерних группах `bg_mining` (например `bg_silver_mining`
  у E&F, `bg_uranium_mining`, `bg_water_farms`) под запреты не попадают — компач не нужен.
- **`common/defines/NEconomy`**: T&R задаёт один ключ, KAI — ноль. С тремя ключами
  E&F пересечения нет.
- **`common/buy_packages/`**: T&R патчит `wealth_10…wealth_99` через `TRY_INJECT:`
  (90 записей) — уживается с `INJECT:` кого угодно.
- **Kuromi's AI**: с E&F пересечение ключей, loc-ключей, id событий и путей файлов —
  нулевое. Правит `ai_strategies`, `common/defines/kai_ai.txt` и `ai_weight` техов.

---

### Уточнено 21.08.2026 (разбор пары Morgenröte + T&R)

- **Порядок загрузки: T&R обязан идти после Morgenröte.** Оба определяют
  `technres_is_active` (MR — `always = no` в `00_mr_compatibility_triggers.txt`,
  T&R — `always = yes` в `ztr_compatibility_triggers.txt`), побеждает загруженный
  позже. При обратном порядке ломается ветка `potential = { technres_is_active = no }`
  в `mr_elgar_company_types.txt` — Steinway у MR полезет одновременно с версией T&R.
- **Товаров с Morgenröte суммарно 93 при потолке 128** (ваниль 53 + 39 T&R +
  единственный уникальный у MR `air_travel`). Запас 35, вылета нет.
- **В 13.05 переименованы дата-группы**: `pmg_data_optimization_light_industry` /
  `_heavy_industry` → варианты **`_no_shopkeepers`** во всех `ztr_mr_modified_buildings.txt`.
  Старые группы ещё существуют — ошибки не будет, но модель занятости другая.
  Любой компач, копировавший список PMG у зданий MR, разъехался.
- **`building_uranium_mine` в 13.05**: `bg_uranium_mining` → **`bg_mining`**,
  `has_law` → `has_law_or_variant`, убраны `has_max_level` и `potential`.
  Следствие: шахта попала под механику геолога Агассица из MR 2.8.3e
  (`is_building_group = bg_mining`) — как и все остальные шахты T&R и `building_natural_gas_rig`.
- **`pop_needs` в 13.05**: `popneed_entertainment` (`REPLACE_OR_CREATE`) — выкинут
  `radios`, перетасованы доли `televisions` / `interactive_entertainment`;
  `popneed_leisure` (`REPLACE`) — **выкинут `elgar_music`** и перетасованы почти все доли.
  `popneed_free_movement` и `popneed_luxury_items` — `INJECT`, уживаются с MR.
- **Дыра совместимости с MR**: T&R `REPLACE_OR_CREATE`-ит шесть авиакомпаний MR
  (`curtiss_company_DLR/_KLM/_air_france/_imperial_airways/_swissair/_basic_air_travel`)
  и **закомментировал** в них `possible_prestige_goods = { prestige_good_generic_flights }`
  (у самого T&R этот prestige good тоже закомментирован — без MR нет товара `air_travel`).
  С MR товар есть, но производить его некому → `je_mr_prestige_goods_flights` никогда
  не показывается. Ошибки в логе нет, просто пропавший контент.
- **Удалено в 13.05**: `common/combat_unit_types/ztr_navy_combat_unit_types.txt`,
  `common/ai_strategies_vanilla/`, `decisions/ztr_international_decisions.txt`,
  `ztr_main_decisions.txt`. Добавлены ветки ООН и гражданской войны в Китае.
- **GUI**: у T&R всего 2 файла `.gui`, пересечений путей с Morgenröte (42 файла) нет,
  общих `name`/`type` — ноль. Риска «пропавший виджет = вылет» в этой паре нет.
  Пересекаются только 5 texticon'ов товаров — дубль иконки, максимум строка в логе.

---

### Что такое `TechRes+Kuromi` по структуре
Это **сборка из 3 модулей**:

- **`t&r/` = Tech & Res (основной контент)**: новые ресурсы/товары/здания/ПМ, расширение тех-дерева до XXI века, демография/медицина, атомная механика, куча ивентов/решений.
- **`kai/` = Kuromi AI**: правки поведения ИИ (стройка/рынок/армия/законы/тех-приоритеты, дипломатия).
- **`cmf/` = “фреймворк”**: вспомогательные скрипты/GUI/идеологии/партии/движения/JE-инфраструктура (в этой сборке лежит отдельно, но может быть требованием/базой для части контента).

Ниже — сводка **что меняется в игре**, с приоритетом `common/`.

---

### Экономика: новые стратегические ресурсы и товары (цепочки производства)
Главное изменение: мод **добавляет большой пласт новых goods**, которые становятся входами/выходами для ПМ и новых заводов.

- **Новые сырьевые/промышленные товары** (примерный список из `t&r/common/goods/ztr_new_goods.txt`):
  - **руды/сырьё**: `copper`, `commonores`, `advancedores`, `rare_earths`, `bauxite`, `gas`, `water`
  - **материалы**: `alloys`, `aluminium`, `plastics`
  - **нефтефракции**: `light_fuel`, `heavy_fuel`, `lubricant`
  - **электроника**: `copperwires`, `batteries`, `electroniccomponents`, `processors`, `robotics`
  - **потребителька/услуги**: `homeappliances`, `televisions`, `computer`, `telecommunications`, `softwares`, `interactive_entertainment`, `cosmetics`, `on_demand_goods`
  - **фарма**: `pharmaceuticals`
  - **гражданская авиация/космос**: `civil_planes`, `space_assets`
  - **data-товары**: `raw_data`, `organized_data`, `business_data`

- **Меняются параметры некоторых ванильных goods** (через `REPLACE_OR_CREATE` в `t&r/common/goods/ztr_vanilla_goods.txt`): например, правки баланса/торгуемости для `clothes`, `automobiles`, `aeroplanes` и т.п.

---

### Новые здания (производственные узлы)
В `t&r/common/buildings/` мод **добавляет и/или заменяет** много building types:

- **Добыча/ресурсные здания** (`ztr_resources_buildings.txt`):
  - `building_bauxite_mine`, `building_copper_mine`, `building_commonores_mine`, `building_advancedores_mine`
  - `building_natural_gas_rig`
  - `building_water_plant` (вода как отдельная экономика/потребление)

- **Энергетика** (`ztr_energy_buildings.txt`):
  - `building_hydroelectric_power_plant`
  - `building_renewable_energy_power_plant`
  - `building_geothermal_power_plant`

- **Электроника/высокая промышленность** (`ztr_industrial_buildings.txt`):
  - `building_alloys_plant`, `building_electronics_industry`, `building_battery_plant`
  - `building_processors_foundry`, `building_robotics_industry`
  - `building_aircraft_industry`, `building_pharmaceuticals_industry`, `building_consumer_electronics_industry`

- **“Data Revolution” здания** (`ztr_digital_buildings.txt`):
  - `building_office` (конверсия/производство data)
  - `building_datacenter_industry`
  - `building_software_industry`, `building_telecommunications_industry`, `building_interactive_media_industry`
  - `building_ecommerce_logistics`

- **Особые/уникальные** (`ztr_unique_buildings.txt`):
  - например `building_nuclear_weapons_silo` (яд. арсенал) и `building_research_center` (уникальный R&D-объект под триггеры).

---

### Production Methods: массовые “вшивки” в ванильные здания + новые ПМ-группы
Это **одна из самых конфликтных зон для компачей**: мод не только добавляет ПМ, он **инжектит новые PMG/PM в ванильные здания**.

- **Замены/инжекты в ванильные здания**: `t&r/common/buildings/ztr_vanilla_modified_buildings.txt` и `ztr_vanilla_optimization_buildings.txt`
  - `REPLACE` для: `building_power_plant`, `building_automotive_industry`, `building_synthetics_plant`
  - `INJECT` PMG (в т.ч. `pmg_data_optimization_*`) в кучу зданий (шахты, заводы, порты, ж/д, урбан-центр и т.д.)

- **Data layer**:
  - PMG определены в `t&r/common/production_method_groups/ztr_data_production_method_groups.txt`
  - PM — в `t&r/common/production_methods/ztr_data_production_methods.txt`
  - логика: здания начинают **выдавать/потреблять `raw_data/organized_data/business_data`**, а “офисы/датасентры” — ключевые конвертеры/усилители.

- **Энергетика/нефть**:
  - `t&r/common/production_methods/ztr_energy_production_methods.txt` меняет power-plant PM (вводит новые входы вроде `batteries`, `copperwires`, `water`, `telecommunications`, `robotics` и т.п.), плюс поддерживает “умные сети”.

---

### Тех-дерево и временные рамки
- **Добавлены новые эры**: вплоть до **`era_11 (2032–2051)`** в `t&r/common/technology/eras/00_eras.txt`.
- **Продлено окончание игры**: `END_DATE = "2036.1.1"` в `t&r/common/defines/ztr_defines.txt`.
- **Новые технологии** (огромные файлы): `t&r/common/technology/technologies/ztr_new_production.txt`, `ztr_new_society.txt`, `ztr_new_military.txt`
  - открывают новые цепочки: электроника/микроэлектроника, дата-инфра, новые источники энергии, современная/пост-современная армия, атомка и т.д.
- **Модификации ванильных технологий**: `ztr_modified_vanilla_*` (подгонка под новую прогрессию/зависимости).

---

### Население: потребности, демография, медицина (очень влияет на баланс)
- **Новые pop needs и включение новых goods в потребление**:
  - `t&r/common/pop_needs/ztr_pop_needs.txt`: добавляет `water` в базовую еду, расширяет `heating` (включая `gas`, `homeappliances`), добавляет `softwares` в коммуникацию и т.п.
  - `t&r/common/pop_needs/ztr_mr_pop_needs.txt`: расширяет развлечения (`televisions`, `interactive_entertainment`, и т.д.)

- **Переписаны параметры роста населения в defines**: `t&r/common/defines/ztr_defines.txt` (birthrate/mortality кривая по SoL).
- **Система “демографических стадий”**:
  - JE-цепочка: `t&r/common/journal_entries/ztr_je_demographic.txt`
  - модификаторы стадий + “modern medicine”: `t&r/common/static_modifiers/ztr_pop_modifiers.txt`
  - отдельные ивенты медицины по эпохам: `t&r/events/ztr_healthcare_events.txt`

---

### Военка: новые юниты, новые моб-опции, атомная механика
- **Новые/заменённые combat unit types**:
  - `t&r/common/combat_unit_types/*`
  - появляются поздние уровни (мехпех/соврем. мехпех/дальше), **MBT**, **rocket artillery**, **nuclear submarine**, **modern carrier**, и даже **`combat_unit_type_giant_death_robot`** (требует `robotics/processors/uranium`).

- **Мобилизационные опции**:
  - `t&r/common/mobilization_options/ztr_new_mobilization_option.txt` добавляет авиа-поддержку, парашютистов, медподдержку с `pharmaceuticals` и т.п.

- **Ядерная система**:
  - JE: `t&r/common/journal_entries/ztr_je_atomic.txt`
  - решения: `t&r/common/decisions/ztr_atomic_decisions.txt` (старт программы, термояд, ДНЯО)
  - ивенты и скрипты: `t&r/events/ztr_atomic.txt`, `t&r/common/scripted_effects/ztr_atomic_scripts.txt`
  - ключевое здание: `building_nuclear_weapons_silo` + закон `law_uranium_full_usage` (см. `t&r/common/laws/ztr_uranium_usage.txt`).

---

### Карта/ресурсы по штатам: новые state traits и скриптовая раздача месторождений
Это вторая критичная зона конфликтов для компачей.

- **Новые state traits** под новые месторождения (и max level зданий):
  - `t&r/common/state_traits/ztr_extraction_state_traits.txt` (+ hidden-варианты)
  - включает water/hydro, copper/bauxite/commonores/advancedores/rare earths/uranium/gas и т.д.
- **Скрипты, которые массово назначают traits штатам (по спискам state_region)**:
  - `t&r/common/scripted_effects/ztr_state_traits*.txt` (очень длинные hardcoded списки регионов).

---

### Законы (новые law groups)
Мод добавляет новые группы законов, которые завязаны на богатство/развитие и новые технологии:

- `t&r/common/law_groups/ztr_laws.txt` + `t&r/common/laws/*.txt`
  - **mining policy**: вплоть до запрета “грязных” шахт (может даже удалять здания в штатах)
  - **uranium usage**: гражданское/полное/запрет (влияет на ядерку)
  - **data policy**, **environmental policy**, **bioethics**, **LGBTQ rights**, **advanced education**.

---

### Game rules
Есть переключатели контента в `t&r/common/game_rules/ztr_game_rules.txt`:
- **decolonization content**
- **historical content**
- **pop lag fix** (настройки оптимизационных скриптов/популяции)

---

### Kuromi AI (`kai/`): что меняет отдельно от “Tech & Res”
`kai/README.md` и `kai/common/*` — это **не про новые товары**, а про ИИ и его скриптовые веса:

- **ai_strategies**: переписаны веса стройки/ПМ/армии/законов/дипломатии (чтобы ИИ адекватнее развивался).
- **defines** (`kai/common/defines/kai_ai.txt`): серьёзная перенастройка AI-констант (ценность PM, лимиты трат, приоритеты).
- **technology ai_weight** (`kai/common/technology/technologies/kai_technologies.txt`): ИИ сильнее тянется к ключевым prereq (например, под ж/д, электричество, радио/телефон).
- **дипломатия**: например, правка knowledge sharing (`kai/common/diplomatic_actions/40_subjects_knowledge_sharing.txt`).

---

### Особый момент: встроенная совместимость/контент под Morgenröte (“MR”)
В `t&r/common/*` много файлов с префиксом **`ztr_mr_*`** (например, `ztr_mr_modified_buildings.txt`, `ztr_mr_goods.txt`) — это **слой интеграции с Morgenröte/их товарами (Elgar/Manzoni/Mendelejew и т.п.)**, включая оперу/издательство/часть “культурной” экономики и “нефтехимию”.

---

### Для компачей: где самые жёсткие точки конфликтов (priority)
Если ты будешь делать compatibility-патчи, чаще всего придётся разруливать:

- **`common/defines/`**: меняет END_DATE и поп-рост (любые моды с defines будут конфликтовать).
- **`common/goods/`**: новые goods + ребаланс ванильных.
- **`common/buildings/` + `common/production_methods*`**: много `REPLACE` и особенно `INJECT`.
- **`common/technology/`**: новые эры/техи + правки ванильных.
- **`common/state_traits/` + scripted раздача traits**: новые месторождения и их распределение.
- **`common/pop_needs/` и `pop_types/`**: новые потребности и ребаланс квалификаций инженеров/капиталистов.
- **`common/combat_unit_types/` + `mobilization_options/`**: новые юниты/опции и новые goods в военном снабжении.
- **`common/laws/` + `law_groups/`**: новые группы законов (особенно mining/uranium/data/env).
