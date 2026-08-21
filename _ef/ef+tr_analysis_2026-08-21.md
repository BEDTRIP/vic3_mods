# E&F + Tech & Res (+ Kuromi's AI) — ревизия компача, 21.08.2026

## Что сверялось

| Мод | Версия / коммит | metadata | Примечание |
|---|---|---|---|
| E&F | `E&F 4.07.2026` | пустой (`version`/`supported_game_version` = "") | сводка сверена 16.08.2026 |
| ef hotfix 1.13 | `1.13.10-2` | `1.13.*`, tested_with E&F 04.07.2026 | свой, грузится после E&F |
| Tech & Res | `Tech Res 13.05.2026` | `1.6'`, `1.13.*` | |
| Kuromi's AI | `KAI 24.07.2026` | `7.5`, `1.13.*` | |
| компач `ef+tr+kai out outdate` | — | `1.6`, `1.13.*` | не `1.6'` — на одну ревизию позади T&R |

Компач частично догнал майский T&R: он уже знает про `building_fusion_power_plant`
и `building_power_grid_station`, которых в апрельской версии T&R не было. Но три
`REPLACE:` ванильных зданий и часть покрытия остались от предыдущей ревизии — см. ниже.

Прогоны `scan_conflicts.py`:

- **E&F × T&R**: 34 общих категории, 142 общих ключа, 1 общий loc-ключ, 0 общих id событий.
- **E&F × KAI**: 9 общих категорий, **0** общих ключей, 0 loc, 0 событий.

Пересечений по путям файлов между E&F, T&R, KAI и компачем **нет ни одного**
(единственные пересечения путей в сборке — это осознанные перекрытия хотфиксом
шести `.gui` и пяти `common/`-файлов E&F).

Семантика `REPLACE:` — по под-блокам, а не по записи целиком (доказано в разборе
E&F + TGR от 21.08.2026). Всё ниже разобрано с этим правилом.

---

## Блокер: 157 товаров при потолке 128

Это перекрывает всё остальное. Считано по фактическим файлам, с учётом порядка
загрузки и перекрытия `common/goods/ef_00_goods.txt` хотфиксом:

| слой | новых товаров | накопительно |
|---|---:|---:|
| ваниль 1.13.10 | 53 | 53 |
| E&F + hotfix | 65 | **118** |
| Tech & Res | **39** | **157** |
| Kuromi's AI | 0 | 157 |
| компач | 0 | 157 |

Потолок — 128. То есть E&F и T&R вместе **не запускаются** в принципе, независимо
от компача: вылет при входе в игру, ни одной строки в логе. Компач эту тему не
трогает вообще — у него нет ни одного файла в `common/goods/`.

39 товаров T&R: `advancedores, ai_systems, alloys, aluminium, androids, batteries,
bauxite, business_data, civil_planes, commonores, computer, copper, copperwires,
cosmetics, electroniccomponents, elgar_instruments, elgar_music, gas,
global_electricity, good_uranium, heavy_fuel, homeappliances,
interactive_entertainment, light_fuel, lubricant, manzoni_prints, on_demand_goods,
organized_data, pharmaceuticals, plastics, processors, rare_earths, raw_data,
robotics, softwares, space_assets, telecommunications, televisions, water`.

Весь мегапак (CMF + ETF + TGR + PSC + KAI + E&F/hotfix + MR + T&R + PBE) даёт
**162** товара — T&R там добавляет только 35, потому что `elgar_*`, `manzoni_prints`
и `good_uranium` уже пришли из Morgenröte.

Что с этим можно сделать:

- **Резать валюты E&F.** После хотфикса активны 57 валют-товаров + 9 финансовых
  (`gold, silver, bond, manufacture_stock, agricultural_stock, mining_stock,
  railroad_stock, mutual_funds, local_currency`). Чтобы влезть в 128 вместе с T&R,
  надо снять ещё **29** — то есть оставить ~28 валют. Механика вырезания уже
  отработана в хотфиксе (комментируем товар, законы/PM/переменные/локализация
  остаются, страну переводим на `law_no_market_liquidity`), и там же лежит
  генератор `01_ef_currency_type.txt`. Критерий отбора — тот же: валюта, за
  которой не стоит ни один тег в `99_ef_history_global_variable.txt`, плюс
  дубликаты. Список кандидатов я не привожу: моя попытка вывести связку
  «товар → закон → тег» эвристикой дала заведомо неверный результат, а угадывать
  тут нельзя — это надо гонять твоим генератором.
- **Резать товары T&R** — путь заведомо хуже: они входы/выходы производственных
  цепочек, каждое удаление тянет за собой PM, здания и техи.
- Либо разнести E&F и T&R по разным сборкам (`megapack no t&r` для этого уже есть).

Пока этот вопрос не решён, всё остальное в этом отчёте — теория: сборка не стартует.

---

## Пофайловый вердикт

### 1. `common/buildings/zzef_vanilla_mines.txt` — **опечатка, здание не патчится**

```
INJECT:building_gold_mines = { production_method_groups = { pmg_data_optimization_primary_sector } }
```

`building_gold_mines` не существует нигде: ваниль 1.13 знает `building_gold_mine`
(без `s`) и `building_gold_field`, алиасов у них нет. `INJECT:` в несуществующий
ключ должен дать строку в `error.log` (`TRY_INJECT:` промолчал бы) — подтвердить
по логу не смог, игровая папка в этой сессии не примонтирована.

Итог: золотая шахта не получает дата-оптимизацию, серебряная (`building_silver_mine`,
определена E&F) получает. Правка на одну букву. Заодно стоит решить, нужен ли тот
же PMG для `building_gold_field` — сам T&R ни золото, ни золотые прииски не трогает,
`pmg_data_optimization_primary_sector` он инжектит только в `ztr_vanilla_optimization_buildings.txt`
(30 зданий, шахт драгметаллов там нет).

### 2. `common/buildings/zztr_vanilla_buildings.txt` — **три `REPLACE:` разъехались с T&R**

T&R делает `REPLACE:` для `building_automotive_industry`, `building_synthetics_plant`,
`building_power_plant`; E&F инжектит в них `pmg_market_liquidity` **до** этого и
потому затирается. Идея файла верная. Но копии сняты со старой ревизии T&R:

**`building_automotive_industry`** — под-блок `production_method_groups` заменяется
целиком, значит подмена реальна:

| | T&R 13.05 | компач |
|---|---|---|
| последний PMG | `pmg_data_optimization_heavy_industry_algorithmic_dispatch` | `pmg_data_optimization_heavy_industry` |

Обе группы существуют и различаются одним PM: `pm_internet_data_algorithmic_dispatch_heavy_industry`
против `pm_internet_data_optimization_heavy_industry`. То есть автозаводы теряют
верхнюю ступень дата-оптимизации.

**`building_power_plant`** — то же место, потери крупнее:

| | T&R 13.05 | компач |
|---|---|---|
| | `pmg_base_building_power_plant` | `pmg_base_building_power_plant` |
| | `pmg_refining_building_power_plant` | `pmg_automation_building_power_plant` |
| | `pmg_automation_building_power_plant` | `pmg_refining_building_power_plant` |
| | **`pmg_power_transmission`** | **`pmg_data_optimization_light_industry`** |

`pmg_power_transmission` (`pm_direct_current` / `pm_half_current` / `pm_alternating_current`)
— это витрина группы законов `lawgroup_national_electric_system`, которую T&R ввёл
вместе с `building_power_grid_station`. Сами три PM модификаторов не несут и нигде
не проверяются через `has_active_production_method` (проверено по всему `TechRes+Kuromi` и `_cmf`),
так что механически потеря невелика — но это откат решения автора, а на её месте
возвращается `pmg_data_optimization_light_industry`, который T&R с электростанции
осознанно снял. `ai_value` в компаче уже совпадает с текущим T&R — эту часть автор обновил.

**`building_synthetics_plant`** — списки PMG совпадают, расхождение только в
`possible`.

Отдельно про `possible`: в `automotive` и `synthetics` компач возвращает
`has_law = law_type:law_industry_banned` / `law_extraction_economy` там, где T&R
перешёл на `has_law_or_variant`. В твоём наборе модов вариантов этих законов нет
ни у кого (проверил `variant_of` в laws у ваниль/TGR/PBE/T&R/E&F/MR/CMF), так что
сегодня это безвредно — но это дрейф, и он сам себя починит, если файл пересобрать.

**Что делать.** Файл нужен, но его надо пересобрать от текущего T&R: взять
`ztr_vanilla_modified_buildings.txt` как есть и дописать в `production_method_groups`
две строки E&F. Ещё лучше — заменить `REPLACE:` на `INJECT:` и оставить только то,
ради чего файл существует:

```
# T&R does a full REPLACE: of these three vanilla buildings, and its
# production_method_groups sub-block wipes E&F's earlier INJECT.
# INJECT: merges into the surviving list instead of restating T&R's definition,
# so a T&R change to PMGs, possible or ai_value no longer silently drifts out of
# this patch. Load order requirement: after both E&F and T&R.
INJECT:building_automotive_industry = { production_method_groups = { pmg_market_liquidity pmg_private_ownership_manufacture_stock } }
INJECT:building_synthetics_plant   = { production_method_groups = { pmg_market_liquidity pmg_private_ownership_manufacture_stock } }
INJECT:building_power_plant        = { production_method_groups = { pmg_market_liquidity pmg_private_ownership_manufacture_stock } }
```

Файл сжимается со 130 строк до трёх и перестаёт разъезжаться при каждом обновлении T&R.

### 3. `common/production_methods/zef_mines_production_methods.txt` — **новые ступени золота не чеканят**

Компач добавляет золотой и серебряной шахте три верхние ступени
(`electric_fueled_pump` → `heavy_machineries` → `autonomous_and_remote_ops`) и
инжектит их в `pmg_mining_equipment_building_{gold,silver}_mine`.

Для серебра это корректно: у E&F серебряная шахта чеканки не даёт вообще, она
выпускает товар `silver`, и новые PM это повторяют.

Для золота — нет. Ванильная лестница чеканки: picks 250 → atmospheric 500 →
condensing 750 → diesel 1000. У всех трёх новых ступеней `country_minting_add`
отсутствует:

| PM | `country_minting_add` | `goods_output_gold_add` |
|---|---:|---:|
| `pm_picks_and_shovels_building_gold_mine` (ваниль) | 250 | — |
| `pm_atmospheric_engine_pump_…` (ваниль) | 500 | — |
| `pm_condensing_engine_pump_…` (ваниль) | 750 | — |
| `pm_diesel_pump_…` (T&R `REPLACE:`) | 1000 | 30 |
| `pm_electric_fueled_pump_…` (компач) | **нет** | 35 |
| `pm_heavy_machineries_…` (компач) | **нет** | 45 |
| `pm_autonomous_and_remote_ops_…` (компач) | **нет** | 50 |

Сам `REPLACE:pm_diesel_pump_building_gold_mine` в компаче `country_modifiers` не
перечисляет — по под-блочной семантике чеканка 1000 там переживает. Ломается
именно апгрейд: страна исследует `thermal_cracking`, ИИ или игрок переключает
шахту на более производительный PM и теряет всю чеканку с золота. Для E&F, где
чеканка — базовый доход при золотом стандарте, это дорого.

Причина видна: файл собран копированием серебряного блока, а у серебра чеканки
и не было. Похоже на недосмотр, а не на замысел — стоит вернуть
`country_modifiers = { workforce_scaled = { country_minting_add = … } }` с ростом
по ступеням (1250 / 1500 / 1750 — по пропорции к росту `goods_output_gold_add`).

Балансовое, не поломка: компач поднимает у diesel pump `state_pollution_generation_add`
15 → 25 и `goods_input_tools_add` 15 → 20 относительно T&R. Выглядит как
осознанное выравнивание с серебром.

Текстуры всех новых PM (`electric_fueled_pump`, `advanced_mining_systems`,
`pm_autonomous_and_remote_ops_mining`, `prefabricated_concrete_buildings`) в T&R есть.

### 4. `zef_private_construction.txt` + `zef_private_construction_groups.txt` — **годно**

Патчит частный стройсектор E&F под товары T&R: `commonores` вместо части железа,
`alloys` вместо части стали, плюс новая верхняя ступень
`pm_prefabricated_concrete_buildings_private` (+30 к стройке, 225 manufacture_stock).

Заодно это подтверждает, что `INJECT:` в блоки модификаторов **суммирует**, а не
заменяет: у `pm_iron_frame_buildings_private` E&F даёт `goods_input_iron_add = 15`,
компач инжектит `-2` — значение имеет смысл только как дельта. Тот же смысл у
`country_construction_add = -5` в `pm_arc_welded_buildings_private`: 30 → 25,
чтобы новая префаб-ступень с её +30 была шагом вперёд. Если бы `INJECT:`
перезаписывал, arc welded давал бы −5 к стройке — заметили бы сразу.

### 5. `common/script_values/zef_00_economic_scripted_value.txt` — **годно, одна асимметрия**

Пять `REPLACE:inflation_on_*`. Построчный диф с текущим E&F: **ни одной удалённой
строки**, только добавления товаров T&R. То есть E&F эти блоки с мая не менял, и
компач ничего не откатывает.

Одна ошибка: в `inflation_on_raw_material` товар `bauxite` добавлен в числитель
(`mg:bauxite = { add = … }`), но забыт в знаменателе (`divide`, где перечислены
`copper, commonores, advancedores, rare_earths, hardwood`). Средневзвешенная цена
сырья из-за этого слегка завышена. Одна строка.

Все упомянутые товары существуют: `global_electricity`, `good_uranium`, `gas`,
`light_fuel`, `heavy_fuel`, `space_assets` — все из T&R (`good_uranium` также есть в MR).

### 6. `common/scripted_effects/zef_01_financial_scripted_effects.txt` — **три реальные проблемы**

Три `REPLACE:`: `private_ownership_production_stocks` (82 КБ), `financial_crash_consequences`,
`economic_crisis_consequences`. Компач добавляет в них 45 зданий T&R/MR.

**6.1. Одиннадцать ванильных зданий переписаны во множественное число.** Компач
подменил имена: `building_textile_mill` → `building_textile_mills`,
`furniture_manufactory` → `furniture_manufacturies`, `tooling_workshop` → `tooling_workshops`,
`paper_mill` → `paper_mills`, `chemical_plant` → `chemical_plants`,
`synthetics_plant` → `synthetics_plants`, `steel_mill` → `steel_mills`,
`shipyard` → `shipyards`, `munition_plant` → `munition_plants`,
`military_shipyard` → `military_shipyards`, `artillery_foundry` → `artillery_foundries`.

Девять из одиннадцати — легальные `aliases` ванильных зданий, и если алиасы
резолвятся в `has_building`/`b:`/`is_building_type`, они отработают. Два — нет:

- `building_artillery_foundries` — у `building_artillery_foundry` алиасов нет ни в
  1.12.3, ни в 1.13.10, ни в TGR;
- `building_military_shipyards` — вместе с самим `building_military_shipyard`
  **удалён из ванили в 1.13** (в 1.12.3 он был, с алиасом).

Значит артиллерийский завод выпадает из механики частной собственности и из
последствий кризисов, а «военная верфь» — мёртвая ссылка в трёх местах.
Проверить, работают ли алиасы в скоупах, дешевле в игре, чем угадывать: см. чеклист п.4.
Безопасный вариант в любом случае — вернуть канонические имена и убрать
`military_shipyard` совсем.

**6.2. Перевёрнутое условие у `building_consumer_electronics_industry`.**
Прогнал все 167 парных `if`-блоков в компаче против 100 в E&F: некорректен ровно один.

```
limit = { … is_production_method_active = { production_method = pm_private_ownership_majority_manufacture_stock } }
activate_production_method = { production_method = pm_private_ownership_majority_manufacture_stock }
```

«если уже majority — включить majority». У всех остальных 166 блоков в этом месте
`pm_no_private_ownership_manufacture_stock`. Блок ничего не делает.

Хуже другое: `building_consumer_electronics_industry` вообще **не получает**
`pmg_private_ownership_manufacture_stock` — его нет ни в одном
`zztr_*_buildings.txt`. То есть `activate_production_method` обращается к PM,
которого у здания нет. Чинится в двух местах: условие + инъекция PMG.

**6.3. Мёртвые ссылки, унаследованные от E&F** (в компаче и в самом E&F одинаково,
это не его вина, но это кандидаты в хотфикс): `building_naval_base` и
`building_military_shipyard` — оба удалены из ванили в 1.13; `building_vineyard_plantation`
(ваниль знает `building_vineyard`) — 18 упоминаний.

### 7. Покрытие зданий T&R — **33 из 38, один пробел настоящий**

Прошёл по всем зданиям, которые T&R вводит поверх ванили, и проверил, получают ли
они `pmg_market_liquidity`:

- **не покрыты и должны быть**: `building_computer_assembly_plant` (`bg_heavy_industry`,
  `ownership_type = self`) — **новое здание в T&R 13.05**, компач про него не знает;
  `building_consumer_electronics_industry` — существовало и в 1.12, пробел давний
  (см. 6.2).
- **не покрыты и правильно**: `building_research_center` (`can_build_private = always no`),
  `building_modern_state_baseline` (`buildable = no`), `building_nuclear_weapons_silo`
  (государственное) — E&F в госздания ликвидность не ставит.

Спорное: `building_fusion_power_plant` строится только государством
(`can_build_government` + сайт-модификатор), а компач вешает на него
`pmg_private_ownership_manufacture_stock` — доля частника там всегда 0, PM-группа
будет вечно на `pm_no_private_ownership`. Мёртвый груз, не поломка.

### 8. `zztr_modified_mr_buildings.txt` + `zztr_mr_buildings.txt` — **дублируют твой `ef+morg done`**

Оба файла инжектят `pmg_market_liquidity` + `pmg_private_ownership_*_stock` ровно в
те же семь зданий Morgenröte, что и `_ef/ef+morg done/common/buildings/zz_ef_mr_buildings_inject.txt`:
`airport`, `elgar_opera`, `instrument_workshops`, `manzoni_publishing_industry`,
`mendelejew_hydrogenation_plants`, `mendelejew_synthetic_rubber_factory`, `uranium_mine`.

При одновременной загрузке PM-группы попадут в список дважды. Оставить надо один
источник — логичнее твой `ef+morg` (он на `TRY_INJECT:`, то есть переживёт удаление
здания в MR), а эти два файла из сборки E&F+T&R выкинуть. Важно: T&R делает
`REPLACE_OR_CREATE:` этих зданий, поэтому любая инъекция должна грузиться **после** T&R.

### 9. Локализация — **только английская**

`zef_production_methods_mines_l_english.yml` — единственный файл. Восемь новых PM
шахт и `pm_prefabricated_concrete_buildings_private` в остальных языках покажут
сырые ключи. Кандидат в `__translations`.

### 10. `.metadata/metadata.json` — **`relationships` пустой**

Ни зависимости от `3143591632` (E&F), ни от T&R. `version: 1.6` при `1.6'` у самого
T&R. Технические мелочи: в 8 из 15 файлов нет BOM (содержимое чистый ASCII, так что
на практике сегодня не стреляет, но по нашим правилам BOM обязателен), скобочный
баланс во всех файлах нулевой.

---

## Проверено — конфликта нет (чтобы не проверять это снова)

- **`common/buy_packages/`**: 90 общих ключей `wealth_*`. E&F — `INJECT:` (99 штук),
  T&R — `TRY_INJECT:` (90 штук). Дописывания уживаются, обе потребности применяются.
- **`common/law_groups/`**: группы не пересекаются. E&F — `lawgroup_monetary_system`,
  `currency_type`, `monetary_policy`, `bimetalism_ratio`. T&R — `national_electric_system`,
  `mining_policy`, `uranium_usage`, `bioethics`, `data_policy`, `lgbtq_rights`,
  `environmental_policy`, `advanced_education`.
- **`common/defines/`**: оба правят `NEconomy`, но пересечение ключей внутри —
  **0** (E&F: 3 ключа, T&R: 1, KAI: 0). `END_DATE`/поп-рост T&R и `PRICE_RANGE`/
  `GOLD_RESERVE_RETURNS_FACTOR` E&F не мешают друг другу.
- **`common/on_actions/`**, **`history/global` (`GLOBAL`)**, **`history/buildings` (`BUILDINGS`)**
  — аддитивные категории, общие ключи ожидаемы и безвредны.
- **События**: 0 общих id.
- **Локализация**: один общий ключ `je_end_strike_tt` (E&F `content_1_l_english.yml`
  ↔ T&R `000_buildings_l_english.yml`). Косметика, побеждает тот, кто грузится позже.
- **`.gui`**: пересечений по путям между E&F и T&R нет вообще. `compare_gui_names.py`
  гонять не по чему.
- **`company_standard_oil`**: оба `INJECT:`, разные поля (E&F — `possible_prestige_goods`,
  T&R — `building_types`, `extension_building_types`, `prosperity_modifier`). Мерджатся.
- **Техно `mutual_funds`**: E&F `REPLACE:` (полное определение), T&R `INJECT:` только
  `ai_weight`. При порядке E&F → T&R инжект ложится поверх. Если E&F когда-нибудь
  окажется ниже T&R по порядку — `ai_weight` от T&R пропадёт.
- **Законы шахт T&R не трогают серебро E&F**: `law_polluting_mining_banned` сносит
  здания по именам (`coal_mine`, `lead_mine`, `sulfur_mine`), а не по
  `building_group`; `possible`-фильтры T&R тоже поимённые. `bg_silver_mining`
  (`parent_group = bg_mining`) под них не попадает — патч не нужен.
- **Kuromi's AI не требует компача с E&F вообще**: 0 общих ключей, 0 общих loc-ключей,
  0 общих событий, 0 общих путей. KAI трогает `ai_strategies`, `defines/kai_ai.txt`
  и `ai_weight` техов; у E&F собственные `99_ai_strategies` лежат в `.zip`, то есть
  выключены. Буква «kai» в имени компача ничего не означает.
- **Хотфикс и компач не пересекаются**: ни по путям, ни по ключам. Хотфикс правит
  `goods`, `laws`, `history`, `alert_types`, `pop_needs`, `.gui`; компач —
  `buildings`, `production_method*`, `script_values`, `scripted_effects`.

---

## Что делать, по убыванию

1. **Решить вопрос 128 товаров** — до этого остальное смысла не имеет.
2. **`zztr_vanilla_buildings.txt` → три строки `INJECT:`** (п. 2). Убирает откат
   PMG электростанции и автозавода и снимает проблему на будущее.
3. **Вернуть чеканку новым золотым PM** (п. 3).
4. **Починить `building_gold_mines` → `building_gold_mine`** (п. 1).
5. **`building_consumer_electronics_industry`**: перевёрнутое условие + недостающая
   инъекция PMG; **`building_computer_assembly_plant`**: добавить инъекцию (п. 6.2, 7).
6. **Вернуть канонические имена одиннадцати зданий**, убрать `military_shipyard`
   и `artillery_foundries` (п. 6.1).
7. **Выкинуть `zztr_mr_buildings.txt` и `zztr_modified_mr_buildings.txt`**, оставить
   `ef+morg done` (п. 8).
8. `bauxite` в знаменатель `inflation_on_raw_material` (п. 5).
9. Локализация, `relationships`, BOM (п. 9, 10).

Побочно — кандидаты в `ef hotfix 1.13`, к компачу отношения не имеют:
`building_naval_base` и `building_military_shipyard` удалены из ванили в 1.13, а E&F
их ещё зовёт; `building_vineyard_plantation` не существовал никогда.

---

## Чеклист проверки в игре

Порядок загрузки для всех пунктов: CMF → … → E&F → **ef hotfix** → T&R → KAI → компач.
Компач обязан быть ниже и E&F, и T&R — иначе `REPLACE:` T&R снесёт его инъекции.

1. **Старт вообще** — годно / не годно. Сборка с E&F+hotfix+T&R сейчас должна
   вылетать при входе в игру без единой ошибки в логе (157 товаров). Если она
   почему-то стартует — значит моя арифметика по потолку неверна, и это надо знать
   до всего остального.
2. **Электростанция, панель здания** — есть ли вкладка «Power Transmission»
   (DC / half / AC) и вкладка дата-оптимизации. Ожидаемо сейчас: transmission нет,
   дата-оптимизация есть. После правки п. 2 — наоборот. Годно / не годно.
3. **Золотая шахта, США или Трансвааль, после `compression_ignition` и дальше** —
   смотреть `country_minting` при переключении PM вверх по группе Mining Equipment.
   Падение до нуля на `Electric Fueled Pump` — подтверждение п. 3.
4. **Алиасы в скоупах** — самый дешёвый способ: выставить любой стране
   `law_council_republic`/национализацию так, чтобы `private_ownership_fraction`
   текстильной фабрики перешла 0.5, и посмотреть, переключился ли PM частной
   собственности. Переключился → алиасы (`building_textile_mills`) резолвятся, и
   из п. 6.1 остаются только два имени; не переключился → ломаются все одиннадцать.
5. **`error.log` после 5 игровых лет** — искать `building_gold_mines`,
   `building_artillery_foundries`, `building_military_shipyards`,
   `building_naval_base`, `building_vineyard_plantation`,
   `pm_private_ownership_majority_manufacture_stock`.
6. **Здания MR** (`building_airport`, `building_uranium_mine` и остальные пять) при
   одновременно включённых `ef+morg` и компаче — не задвоилась ли PM-группа в панели
   здания. Годно / не годно.
7. **Частный стройсектор E&F** — на `Arc Welded Buildings` страновая стройка должна
   вырасти на **25**, не на 30 и не упасть на 5. Это проверка семантики `INJECT:`
   в блоках модификаторов, от неё зависит вся п. 4.
