# Сверка компача `morg+tr+kai` — 21.08.2026

Компач собран **04.05.2026** (единственный коммит `d04b022 t&r morg 4.05.2026`).
С тех пор оба мода обновились:

| Мод | Версия | Коммит в `vic3_mods_out` | Было при сборке компача |
|---|---|---|---|
| Morgenröte | 2.8.3e «Mitsopoulos» | `Morgenrote 15.08.2026` | 2.6.x (`morgenrote 02.02`) |
| Tech & Res | 1.6' | `Tech Res 13.05.2026` | initial commit |
| Kuromi AI | 7.5 | `KAI 24.07.2026` | — (KAI компача не касается) |

Обновление Morgenröte — крупное (2084 файла, +329k/−166k строк), Tech & Res — среднее (321 файл).
`supported_game_version` у всех трёх — `1.13.*`, игра 1.13.10. Метадату компача (`version: 1.6'`) надо синхронизировать с T&R.

---

## Резюме

Компач сейчас — **21 файл**. По итогам сверки:

* **7 файлов удаляются целиком** (~65 KB из 85 KB кода — 75 % объёма);
* ещё **9 отдельных записей** внутри оставшихся файлов стали ненужными;
* **2 настоящих бага** (один — с гарантированной ошибкой в логе);
* **1 новая дыра совместимости**, которой в компаче нет.

После правок остаётся **~8 файлов**.

Главная причина такого сжатия: **Tech & Res сам по себе — полноценный слой совместимости с Morgenröte** (`ztr_mr_*`, `ztr_modified_mr_*`: 20 файлов, все ключевые PM/PMG/здания/техи MR), а Morgenröte 2.8.3e переписал две механики с «жёстко по типу здания» на «по свойству», из-за чего T&R-здания подхватываются сами.

---

## 1. Удалить целиком

### 1.1 `common/buy_packages/zzz_compatch_buy_packages.txt` (38 KB, 45 % компача)

99 блоков `REPLACE:wealth_1..wealth_99`. Проверено программно, все 99 штук:

```
CP[wealth_N] == ваниль[wealth_N] + MR_inject[wealth_N]     — расхождений 0
MR_inject[wealth_N] == TR_inject[wealth_N]                 — расхождений 0
```

То есть файл дословно воспроизводит то, что MR и T&R **уже делают сами** через `TRY_INJECT:popneed_entertainment`, причём с одинаковыми числами в обоих модах. Конфликта нет: два `TRY_INJECT` одного ключа аддитивны и здесь несут идентичные значения.

Вдобавок файл **вреден**: полный `REPLACE` 99 уровней замораживает ванильные числа 1.13.10 внутри компача. Любой патч Paradox, ребалансящий `buy_packages`, будет молча откачен, а любой третий мод, инжектящий свою `popneed_*` до компача в порядке загрузки, потеряет её.

**Удалить.**

### 1.2 Весь блок Агассица — 4 файла, 28 KB

* `common/journal_entries/zzmr_science_agassiz_journal_entries.txt` (22 KB, 6 JE)
* `common/scripted_triggers/zzmr_agassiz_scripted_triggers.txt`
* `localization/english/zmr_agassiz_l_english.yml`
* `localization/english/gui/zmr_gui_science_l_english.yml`

Morgenröte 2.8.3e полностью переделал геолога. Было: по одной JE на ресурс (`je_agassiz_find_coal_project`, `_iron_`, `_lead_`, `_sulfur_`, `_gold_`, `_uranium_`) — компач честно дописал ещё 6 под руды T&R. Стало: одна общая `je_agassiz_improve_mines_project` с окном выбора шахты, гейт —

```
agassiz_mine_valid_for_improvement_trigger = {
    level > 0
    is_building_group = bg_mining
    NOT = { has_modifier = agassiz_building_production_mult_modifier }
}
```

`is_building_group` идёт по цепочке родителей, и все шахты T&R сидят прямо в `bg_mining`:

| Здание T&R | `building_group` | цепочка |
|---|---|---|
| `building_commonores_mine` | `bg_mining` | `bg_mining > bg_extraction` |
| `building_bauxite_mine` | `bg_mining` | то же |
| `building_copper_mine` | `bg_mining` | то же |
| `building_advancedores_mine` | `bg_mining` | то же |
| `building_rare_earths_mine` | `bg_mining` | то же |
| `building_natural_gas_rig` | `bg_mining` | то же |
| `building_uranium_mine` | `bg_mining` | то же (T&R сам сменил `bg_uranium_mining` → `bg_mining` 13.05) |

**Руды и газ T&R уже покрыты Morgenröte из коробки.** Патч не нужен.

Отдельно: 6 JE компача **и так мёртвые** — их никто не добавляет. Активация идёт из `common/scripted_guis/MR_science_agassiz_geologist_sguis.txt` (`mr_geologist_improve_mines_button_effect`), который компач не перекрывает. Проверено grep'ом: `je_agassiz_find_commonores_project` и остальные пять встречаются **только внутри компача**.

Газ: раньше он ехал через кнопку нефти (отсюда локализация `mr_science_geologist_oil_button: "Prospect Oil or Gas"`). Теперь нефтяной гейт — `is_building_type = building_oil_rig` (точный тип, не группа), а `building_natural_gas_rig` попадает в рудную ветку. Переименование кнопки больше не нужно и вводит в заблуждение.

Бонус: JE компача **всё равно устарели** относительно шаблона MR 2.8.3e — в них нет `add_modifier = { name = agassiz_ore_search_cost_modifier multiplier = root.mr_local_project_cost_small_value }` в `immediate` (проекты по рудам T&R были бы бесплатными) и `goal_add_value` захардкожен `18` вместо `agassiz_improvement_progress_cost`. Чинить не нужно — удалять.

### 1.3 `common/mobilization_option_groups/zzz_mr_compatch_mobilization_option_groups.txt`

Наборы групп у модов **не пересекаются вообще**:

* MR: `air_reconaissance`, `aircrafts`, `advanced_weapons`, `advanced_defence`, `advanced_tanks`, `advanced_aircrafts`, `advanced_medical_support`
* T&R: `tactical_weapons`, `air_support`, `extra`, `nuclear_weapons`, `electronic_support`, `remote_support`

Ни одного общего ключа → конфликта нет, компач тут ничего не чинит. Файл только перебивает `weight` (порядок групп в окне мобилизации) — это ребаланс, а не совместимость, и он уже разъехался с обоими модами:

| Группа | компач | стало у автора |
|---|---|---|
| `air_reconaissance` | 2 | 3 (MR) |
| `aircrafts` | 2 | 3 (MR) |
| `air_support` | 1 | 0 (T&R) |
| `tactical_weapons` | 0 | 1 (T&R) |
| `nuclear_weapons` | −2 | −1 (T&R) |
| `remote_support` | −2 | −1 (T&R) |

Плюс компач вообще не упоминает пять `advanced_*` групп MR, так что «единого порядка» он и не задаёт.

**Удалить.** Если порядок в окне всё-таки важен — это отдельное решение, и тогда файл надо переписать заново от текущих весов обоих модов.

### 1.4 `common/technology/technologies/ztr_mr_military.txt` (пустой плейсхолдер)

Файл-заглушка `#Placeholder for compatibility` перекрывает по пути одноимённый файл T&R — грубейший инструмент. Что при этом «спасается»: T&R `REPLACE_OR_CREATE`-ит 6 техов MR, из них **5 байт-в-байт совпадают с MR**. Единственное расхождение — `agassiz_sounding_tech`: T&R добавляет `building_group_bg_fishing_throughput_add = 0.1` и меняет условие `ai_weight` c `has_global_variable = dubois_mid_atlantic_ridge_global_var` на `has_variable = ztr_bolshevik_ideology_var` (похоже на копипасту у автора T&R, но это только вес ИИ).

Ради одного `ai_weight` перекрывать файл целиком не стоит. **Удалить плейсхолдер.**

### 1.5 `common/journal_entries/zzz_compatch_journal_entries.txt`

Оба ключа (`je_curtiss_lindbergh_generic`, `je_curtiss_lindbergh_usa`) отличаются от MR 2.8.3e **ровно одной строкой**:

```
компач:  is_building_type = building_aircraft_industry
MR 2.8.3e: modifier:goods_output_aeroplanes_add > 0
```

MR перешёл на проверку по свойству. `building_aircraft_industry` T&R крутит `pm_aeroplane_production` (T&R его `REPLACE`-ит, `goods_output_aeroplanes_add` на месте) → условие MR выполняется само. **Файл целиком не нужен.**

### 1.6 `events/MFE/ztr_MFE_trade_good_events.txt`

`MFE_trade_good_events.7`: MR теперь проверяет `has_active_production_method = pm_aeroplane_production` (без привязки к типу здания) — авиапром T&R подходит. Плюс компач тащит устаревшую ссылку на видео `"gfx/event_pictures/unspecific_airPlane.bk2"`, тогда как MR перешёл на короткое имя `"unspecific_airplane"`. **Удалить.**

### 1.7 `common/technology/technologies/ztr_mr_production.txt` (плейсхолдер) — на решение

Что теряется при удалении плейсхолдера (т.е. побеждает версия T&R):

* `verrier_physics_tech`, `verrier_chemistry_tech`, `verrier_astronomy_tech` — T&R **добавляет** `country_tech_research_speed_mult = 0.05` (осознанный ребаланс под длинное дерево T&R);
* `verrier_astronomy_tech`, `verrier_electromagnetism_tech` — T&R **срезает** MR-овские условия `ai_weight` (Dubois formation, `tesla_has_electrical_engineer_trigger`);
* `manzoni_linotype_tech` — вес ИИ 2 → 1;
* `manzoni_rotary_press_tech` — идентично.

Потери — только веса ИИ. Приобретения — бонусы к скорости исследования, которые T&R закладывал в свой темп. **Рекомендую удалить плейсхолдер** (в пользу T&R). Если веса ИИ MR важны — вернуть их точечным `REPLACE:` на два теха, а не файлом.

---

## 2. Удалить отдельные записи

| Где | Запись | Почему |
|---|---|---|
| `common/buildings/zztr_compatch_buildings.txt` | `REPLACE:building_uranium_mine` | **Байт-в-байт совпадает** с `ztr_mr_buildings.txt` T&R 13.05. T&R сам сменил `bg_uranium_mining` → `bg_mining`, `has_law` → `has_law_or_variant` и убрал `has_max_level`/`potential`. Компач теперь дублирует T&R. |
| `common/script_values/zzz_compatch_script_values.txt` | `REPLACE:curtiss_aeroplane_production_score` | MR перешёл на `modifier:goods_output_aeroplanes_add > 0` — авиапром T&R считается сам. |
| `events/sports/ztr_mr_curtiss_events.txt` | `curtiss.510`, `curtiss.513` | То же: MR теперь `modifier:goods_output_aeroplanes_add > 0`. |
| `common/technology/technologies/zzz_compatch_mr_society.txt` | `REPLACE:curtiss_tourism_tech` | T&R этот тех **не трогает вообще** — коллизии нет. Компач отличается от MR ровно одной строкой: `country_free_charters_add = 1` против нового `country_max_companies_add = 1`. То есть запись сейчас просто откатывает балансное решение MR. (Оба модификатора в 1.13.10 валидны, ошибки в логе не будет — но и смысла нет.) |
| `common/technology/technologies/zzz_compatch_mr_society.txt` | `REPLACE:elgar_mass_culture_tech` | Совпадает с MR **дословно**. Пока `ztr_mr_society.txt` заглушен — чистый no-op; после отказа от заглушки (см. §3.4) станет осмысленным, но тогда его надо будет писать заново от версии T&R. |

**Что в этих файлах остаётся и почему:**

* `curtiss.228`, `curtiss.229`, `curtiss.506` — MR всё ещё хардкодит `building_automotive_industry` + `pm_aeroplane_production`. А T&R **выкинул** `pmg_aeroplanes` из `building_automotive_industry` (в его `REPLACE` остались только `pmg_automobile_production`, `pmg_tanks`, `pmg_automation_*`, `pmg_data_optimization_*`). Проверка MR мертва → патч нужен.
* `curtiss_schneider_trophy_before_race_points_score`, `curtiss_found_pilot_school_decision` — по той же причине (три и два вхождения `building_automotive_industry` соответственно). Обе записи в остальном совпадают с MR 2.8.3e — переписывать не надо.
* `REPLACE:verrier_nuclear_physics_tech` — от версии T&R отличается **одной строкой**: пререк `verrier_radioactivity_tech` (цепочка MR) вместо `verrier_modern_physics_tech` (перемаршрутизация T&R). Оставить, но в комментарии зафиксировать, что это осознанный выбор в пользу цепочки MR, иначе через полгода запись будет выглядеть случайной.
* `REPLACE:vikelas_international_sports_tech` — **настоящая тройная коллизия**: MR определяет его в `mr_sports_vikelas_technologies.txt`, T&R — обычным (без префикса) блоком в `ztr_new_society.txt`. Компач сейчас держит era_5 + пререк `international_organizations` + три модификатора; MR 2.8.3e переехал на era_4, оставил один пререк `organized_sports` и **пустой** блок модификаторов. Запись оставить, но пересобрать: решить, чья эра/пререки побеждают, и записать почему.

---

## 3. Починить

### 3.1 БАГ: несуществующий модификатор в `mobilization_options` (в лог падает ошибка)

`common/mobilization_options/zzz_mr_compatch_mobilization_option.txt`, все три `mobilization_option_advanced_tanks_1/2/3`:

```
unit_modifier = {
    ...
    military_formation_movement_speed_mult = 0.1     # <- такого модификатора в 1.13.10 НЕТ
}
```

Проверено по ванили 1.13.10: `military_formation_movement_speed_mult` — **0 вхождений** в `common/modifier_type_definitions/00_modifier_types.txt` и в `localization/english/modifiers_l_english.yml`. Правильное имя — `military_formation_army_movement_speed_mult` (1 и 2 вхождения соответственно). MR 2.8.3e у себя уже исправил.

Итог: бонус к скорости движения у всех трёх опций **не работает**, плюс ошибка при загрузке.

### 3.2 `mobilization_options`: устаревший `ai_weight`

MR 2.8.3e сделал вес условным — если игроку доступен тир выше, текущий получает `-1000`:

```
ai_weight = {
    if = {
        limit = { has_variable = gaudi_military_engineer_advanced_tanks
                  var:gaudi_military_engineer_advanced_tanks > 1 }
        value = -1000
    }
    else = { value = 1 }
}
```

В компаче — плоская `value = 1` на всех трёх тирах, то есть ИИ навсегда залипает на первом.

**Что делать:** пересобрать файл от тела MR 2.8.3e и наложить единственную реальную правку компача — расширенный список юнитов T&R в `possible`. Все девять типов существуют:

| Юнит | Источник |
|---|---|
| `combat_unit_type_light_tanks` | ваниль (T&R `INJECT`) |
| `combat_unit_type_heavy_tank` | ваниль (T&R `INJECT`) |
| `combat_unit_type_mechanized_infantry` | ваниль (T&R `INJECT`) |
| `combat_unit_type_modern_light_tanks` | T&R |
| `combat_unit_type_modern_heavy_tank` | T&R |
| `combat_unit_type_main_battle_tanks` | T&R |
| `combat_unit_type_advanced_mechanized_infantry` | T&R |
| `combat_unit_type_modern_mechanized_infantry` | T&R |
| `combat_unit_type_giant_death_robot` | T&R |

### 3.3 `pop_needs`: разъехались с T&R 13.05

`common/pop_needs/zztr_mr_compatch_pop_needs.txt` собран от T&R 04.05. С тех пор T&R:

* `popneed_entertainment` — выкинул `radios`, `televisions` 0.5 → 0.2 max_supply_share, `interactive_entertainment` вес 1.25 → 1.75;
* `popneed_leisure` — выкинул `elgar_music`, перетасовал доли у fine_art/automobiles/radios/opium/clippers/steamers/televisions, убрал дубль `interactive_entertainment`.

Реальная задача компача здесь всего одна и она не изменилась:
* T&R `REPLACE_OR_CREATE:popneed_entertainment` затирает определение MR, в котором был `air_travel`;
* T&R `REPLACE:popneed_leisure` затирает `TRY_INJECT` MR, которым тот добавлял `air_travel`.

**Рекомендую переписать на `INJECT:` вместо `REPLACE:`** — по одной записи `air_travel` в каждую потребность. Это аддитивно, переживает любые будущие правки T&R и убирает необходимость пересобирать файл при каждом обновлении:

```
# T&R REPLACE-ит обе потребности целиком и тем самым сносит air_travel,
# который Morgenröte кладёт в popneed_entertainment напрямую и инжектит в popneed_leisure.
# INJECT, а не REPLACE: иначе балансные числа T&R приходится пересобирать каждое обновление.
INJECT:popneed_entertainment = { entry = { goods = air_travel weight = 0.25 max_supply_share = 0.1 min_supply_share = 0.0 } }
INJECT:popneed_leisure       = { entry = { goods = air_travel weight = 1.0  max_supply_share = 0.25 min_supply_share = 0.0 } }
```

Цена решения: `civil_planes` останется в `popneed_leisure` рядом с `air_travel` (нынешний `REPLACE` его вычищал — «попы покупают билеты, а не самолёты»). Если это принципиально — оставить `REPLACE`, но тогда пересобрать оба блока от тела T&R 13.05 и держать в голове, что файл придётся обновлять и дальше. Проверить в игре: не даёт ли соседство двух записей заметного перекоса в спросе на `civil_planes`.

`popneed_free_movement` и `popneed_luxury_items` трогать не нужно: там оба мода делают `INJECT` — уживаются.

### 3.4 `building_manzoni_publishing_industry`: устаревшее имя PMG

`common/buildings/zztr_compatch_buildings.txt` ссылается на `pmg_data_optimization_heavy_industry`. T&R 13.05 повсеместно переехал на `pmg_data_optimization_heavy_industry_no_shopkeepers` (и `..._light_industry_no_shopkeepers`). Старая группа в T&R **ещё существует** — вылета не будет, но здание теперь работает по другой модели занятости, чем все остальные здания T&R.

Заменить на `pmg_data_optimization_heavy_industry_no_shopkeepers`.

Сама запись **нужна** — компач возвращает в список `manzoni_pmg_publisher` и `manzoni_pmg_newspaper` (PMG Morgenröte, которые T&R выкинул из своей версии здания), плюс `city_type = city` и `levels_per_mesh = 50`.

### 3.5 `manzoni_pmg_building_publishing_industry_automation`: текстура

Компач ставит `mixed_icon_refining.dds`, T&R 13.05 — `mixed_icon_automation.dds`. Подтянуть иконку T&R.
Сама запись **нужна**: она возвращает `manzoni_pm_cylinder_presses`, который T&R вырезал из группы.

### 3.6 Заглушка `ztr_mr_society.txt` — единственная обоснованная из трёх

Здесь перекрытие файла действительно спасает контент MR. T&R в своей версии:

* `romanticism`, `elgar_classicism_tech`, `elgar_irrationalism_tech` — **срезает** `country_elgar_decorative_musical_tradition_add` / `country_klimt_decorative_painting_tradition_add`, то есть ломает механику традиций Элгара/Климта;
* `panum_vaccination_tech` — срезает `state_harvest_condition_panum_smallpox_condition_impact_mult = -0.25`;
* `elgar_modern_art_tech` — era_3 → era_4 и снимает `can_research = no` (MR его выдаёт событием, а не исследованием);
* `malaria_prevention` — переписывает целиком: era_4, `country_institution_colonial_affairs_max_investment_add`, пререк `civilizing_mission`, вместо MR-овских `state_harvest_condition_panum_yellow_fever_condition_impact_mult` / `country_institution_health_system_max_investment_add`;
* `dubois_nature_protection_tech` — **добавляет** `country_institution_environmental_policy_max_investment_add = 1` (это T&R теряет при заглушке);
* `pharmaceuticals` — −0.1 против −0.2, мелочь;
* `theiler_microbiology_tech` — идентично.

Заглушка оправдана (традиции Элгара/Климта — несущая механика MR), но она блунт: заодно откатывает `dubois_nature_protection_tech` и колониальную ветку `malaria_prevention` у T&R.

**Минимальная альтернатива:** убрать заглушку и добавить в `zzz_compatch_mr_society.txt` точечные `REPLACE:` на `romanticism`, `elgar_classicism_tech`, `elgar_irrationalism_tech`, `elgar_modern_art_tech`, `panum_vaccination_tech` — тело от T&R + вернуть модификаторы MR. Тогда `dubois_nature_protection_tech`, `malaria_prevention` и `pharmaceuticals` остаются в редакции T&R.

Это правка на ~5 записей вместо перекрытия файла с 10. Стоит того — но перед ней надо решить (см. §2), кто побеждает по `elgar_mass_culture_tech`, он тоже в этом файле.

### 3.7 BOM

Из 21 файла компача BOM есть только в **пяти**. По правилу проекта BOM обязателен во всех `.txt` и `.yml`. Пока не стреляло (файлы чисто ASCII), но исправить при следующей правке — заодно с удалением половины из них.

---

## 4. Новая дыра: призовые товары авиакомпаний Morgenröte

Не покрыто компачем и не было покрыто раньше.

T&R `REPLACE_OR_CREATE`-ит шесть авиакомпаний Morgenröte — `curtiss_company_DLR`, `_KLM`, `_air_france`, `_imperial_airways`, `_swissair`, `curtiss_company_basic_air_travel` — и **закомментировал** в них блок

```
# possible_prestige_goods = {
# 	prestige_good_generic_flights
# }
```

(логично: в T&R без MR нет товара `air_travel`, и `prestige_good_generic_flights` у него тоже закомментирован в `ztr_generic_prestige_goods.txt`).

С MR товар и prestige good существуют, но версии компаний T&R побеждают → **ни одна компания не может производить `prestige_good_generic_flights`**. Следствие: `je_mr_prestige_goods_flights` гейтится на

```
any_company = { can_potentially_produce_prestige_goods = prestige_good_generic_flights ... }
```

и никогда не показывается. Вся ветка призовых полётов Morgenröte мертва. Ошибки в логе нет — просто отсутствующий контент, поэтому и не заметили.

**Минимальный фикс** — новый файл `common/company_types/zz_compatch_curtiss_prestige.txt`, шесть `INJECT:` с блоками `possible_prestige_goods` + `prestige_goods_trigger` (взять из `Morgenrote/common/company_types/mr_curtiss_company_types.txt`). Требует проверки: создаёт ли `INJECT:` отсутствующий список `possible_prestige_goods` или только дописывает в существующий. Если только дописывает — придётся `REPLACE:` шести компаний с телом T&R плюс блок MR, что заметно хуже по поддержке.

---

## 5. Порядок загрузки и метадата

* Оба мода определяют `technres_is_active`: MR — `always = no` (заглушка от спама в логе, `00_mr_compatibility_triggers.txt`), T&R — `always = yes` (`ztr_compatibility_triggers.txt`). Побеждает тот, кто позже. **T&R обязан грузиться после Morgenröte**, иначе `technres_is_active` = no и в `mr_elgar_company_types.txt` не сработает ветка `potential = { ... technres_is_active = no }` — Steinway у MR полезет одновременно с версией T&R. Компач — третьим.
* `.metadata/metadata.json` компача: `"relationships": []`. Прописать зависимости от `2889925770` (Morgenröte) и `tech.res`, чтобы порядок не приходилось держать в голове. Заодно поднять `version` до текущей T&R и обновить `short_description`.
* README у компача **нет вообще** (ни BBCode, ни markdown). Завести — хотя бы список того, что патч чинит и почему; после сжатия он будет коротким.

---

## 6. Проверено — конфликта нет

Чтобы через полгода не проверять заново:

* **Потолок товаров.** Ваниль 53 + T&R 39 новых + `air_travel` (единственный уникальный у MR) = **93**. `elgar_instruments`, `elgar_music`, `good_uranium`, `manzoni_prints` определены обоими, но у T&R через `REPLACE_OR_CREATE` — это одни и те же товары, не новые. До потолка 128 — запас 35. Вылета при входе в игру не будет.
* **Группы законов.** MR не добавляет ни одного `law_group` и ни одного `law` (0 и 0). T&R — 8 групп и 41 закон. Пересечений нет.
* **GUI.** Пересечение путей `.gui` между MR (42 файла) и T&R (2 файла) — **пусто**. Ваниль перекрывает только MR и только `gui/error_deer.gui`. `compare_gui_names.py`: общих `name` — 0, общих `type` — 0. Риска «пропавший виджет = вылет» нет. Единственное пересечение — 5 texticon'ов (`air_travel`, `elgar_instruments`, `elgar_music`, `good_uranium`, `manzoni_prints`) в разных файлах: MR `gui/texticons/*.gui`, T&R `gui/01_goods_texticons.gui`. Дубль иконки, максимум строчка в логе.
* **ID событий.** `scan_conflicts.py`: `event_id_dups = 0`.
* **Ключи локализации.** `loc_key_dups = 0`.
* **`common/on_actions/`, `history/global/GLOBAL`, `history/buildings/BUILDINGS`** — оба мода пишут туда, но эти категории аддитивны. Патч не нужен.
* **`decisions`, `journal_entries`, `combat_unit_types`, `static_modifiers`, `defines`, `institutions`** — пересечений ключей между MR и T&R **ноль**.
* **`goods_is_industrial`** (`zztr_compatch_vanilla_scripted_triggers.txt`) — по-прежнему актуален и минимален: список компача = список T&R (62 товара) **плюс ровно `air_travel`**. Ни одного несуществующего товара ни в одном из двух списков. Оставить как есть. (Побочно: T&R завёл товар `androids` с `category = industrial`, но не внёс его в свой же триггер — это его баг, не наш.)
* **Дубли `modifier_type_definitions`** (19 штук: `goods_*_elgar_music_*`, `building_uranium_mine_throughput_add` и т.п.) — определения одинаковых модификаторов в обоих модах. Безвредно.
* **`prestige_good_generic_instruments`** — MR сам гасит свой Steinway при активном T&R через `technres_is_active = no` в `potential`. Патч не нужен.

---

## 7. Чеклист проверки в игре

По убыванию риска. После каждого пункта — явное «годно / не годно».

**A. Загрузка (без этого дальше нет смысла)**

1. Игра стартует, вход в 1836 год не вылетает. → годно / не годно
2. `logs/error.log` чист по `military_formation_movement_speed_mult` (после фикса §3.1 не должно быть ни одной строки). → годно / не годно
3. `logs/error.log` чист по `pmg_data_optimization_heavy_industry`, `manzoni_pmg_publisher`, `manzoni_pmg_newspaper`, `manzoni_pm_cylinder_presses`. → годно / не годно
4. Порядок в плейсете: Morgenröte → Tech & Res → компач. Проверить консолью `effect = { if = { limit = { technres_is_active = yes } ... } }` или косвенно: компания Steinway у MR не должна предлагаться. → годно / не годно

**B. То, что удалили — убедиться, что не сломали**

5. Геолог Агассица: кнопка «улучшить шахту» открывает окно выбора, **и в списке есть шахты T&R** (медь, боксит, редкозёмы, обычные/продвинутые руды, газовая вышка). Это главная проверка §1.2 — если T&R-шахт в списке нет, значит `is_building_group = bg_mining` не сработал как ожидалось и блок Агассица надо возвращать. → годно / не годно
6. Проект по T&R-шахте вешает на неё модификатор стоимости (`agassiz_ore_search_cost_modifier`) и завершается модификатором производства. → годно / не годно
7. Потребности попов: `air_travel` присутствует в тултипах `popneed_entertainment` и `popneed_leisure`. → годно / не годно
8. Спрос на `civil_planes` не улетел вверх после того, как `air_travel` встал рядом (§3.3). Смотреть цену `civil_planes` на крупном рынке ~1930. → годно / не годно
9. Уровни `wealth_*`: тултип потребления богатого попа содержит `popneed_entertainment` (значит `TRY_INJECT` MR/T&R отработал и удалённый `zzz_compatch_buy_packages.txt` был лишним). → годно / не годно

**C. Авиация Кёртисса (то, что осталось)**

10. JE «Линдберг» (`je_curtiss_lindbergh_generic` / `_usa`) появляется при наличии аэропорта и авиапрома T&R — без записи в компаче. → годно / не годно
11. Решение «основать лётную школу» доступно при 3+/5+ уровнях `building_aircraft_industry` (это осталось в компаче). → годно / не годно
12. Кубок Шнейдера начисляет очки за уровни `building_aircraft_industry` и аэропорты (осталось в компаче). → годно / не годно
13. События `curtiss.228`, `curtiss.229`, `curtiss.506` срабатывают (остались в компаче), `curtiss.510`, `curtiss.513` — тоже (удалены, работают за счёт `modifier:goods_output_aeroplanes_add`). → годно / не годно
14. `MFE_trade_good_events.7` («частные самолёты») срабатывает при 3+ уровнях авиапрома. Заодно проверить, что видео проигрывается (после удаления файла компача идёт короткое имя MR). → годно / не годно

**D. Издательство и уран**

15. `building_manzoni_publishing_industry`: в списке ПМ есть **и** `manzoni_pmg_publisher` / `manzoni_pmg_newspaper` (MR), **и** `pmg_broadcast_media_industry` / `pmg_digital_media_industry` (T&R), **и** `manzoni_pm_cylinder_presses` внутри группы автоматизации. → годно / не годно
16. `building_uranium_mine` строится (не заперт `has_max_level`), сидит в `bg_mining`, запрещён при `law_mining_strategic` / `law_polluting_mining_banned` и их вариантах. → годно / не годно

**E. Техи и мобилизация**

17. `verrier_nuclear_physics_tech` открывается после `verrier_radioactivity_tech`, а не после `verrier_modern_physics_tech`. → годно / не годно
18. `vikelas_international_sports_tech` в дереве ровно один раз, эра и пререки соответствуют принятому решению (§2). → годно / не годно
19. Традиции Элгара/Климта растут при исследовании `romanticism`, `elgar_classicism_tech`, `elgar_irrationalism_tech` (проверка §3.6, независимо от выбранного варианта). → годно / не годно
20. Опции мобилизации «Advanced Tanks» I/II/III доступны для юнитов T&R (`main_battle_tanks`, `modern_mechanized_infantry` и т.д.), бонус к скорости движения виден в тултипе, ИИ переключается на старший тир при апгрейде. → годно / не годно

**F. Призовые полёты (после фикса §4)**

21. Авиакомпания (KLM / Imperial Airways / базовая) показывает `prestige_good_generic_flights` в списке возможных призовых товаров. → годно / не годно
22. JE `je_mr_prestige_goods_flights` появляется в группе технологий. → годно / не годно

**G. Синхронизация**

23. Репозиторий и игровая папка `mod/` совпадают: `diff -rq`. Игровая папка в этой сессии не была подключена — проверить вручную. → годно / не годно
