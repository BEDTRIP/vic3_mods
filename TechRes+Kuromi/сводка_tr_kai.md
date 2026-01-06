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
