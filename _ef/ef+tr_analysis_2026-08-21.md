# E&F + Tech & Res (+ Kuromi's AI) — ревизия компача, 21.08.2026

> **Поправка 21.08.2026:** ниже в разделе про чеканку золота сказано, что `REPLACE:` компача сохраняет `country_modifiers` диспетчера, потому что не перечисляет их. Это неверно — `REPLACE:` заменяет запись целиком, проверено в игре (центробанк исчез от `REPLACE:building_bank = { ownership_type = self }`, и 285 PM потеряли `unlocking_laws`). Значит дизельный насос золотой шахты тоже терял свои 1000 чеканки; в `ef+tr fix` это исправлено. Подробности — в `ef+tgr_analysis_2026-08-21.md`.

---


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

**Что делать.** Первым делом хотелось заменить `REPLACE:` на три строки
`INJECT:` — тогда патч ничего не переизлагает и не может отстать от T&R. Не
годится: `INJECT:` умеет только дописать недостающую группу, но не убрать
устаревшую, а две пересекающиеся группы дата-оптимизации на одном здании
(`pmg_data_optimization_heavy_industry` и `..._algorithmic_dispatch` отличаются
одним PM из шести) дали бы игроку возможность включить обе.

Значит здание надо переизложить — но не руками. `zzzz_ef_tr_fix_buildings_gen.txt`
в фикс-моде собирается из `ztr_vanilla_modified_buildings.txt` как он есть
сегодня, плюс две группы E&F; пересборка — одна команда
(`tools/regen_ef_tr_copies.py`). Ровно тот же приём, что в
`regen_ef_psc_copies.py`.


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

1. **Решить вопрос 128 товаров** — до этого остальное смысла не имеет. Отложено
   по договорённости.
2. Всё остальное из списка ниже сделано в тот же день — см. раздел
   «Сделано 21.08.2026» и мод `_ef/ef+tr fix`:
   PMG электростанции и автозавода, чеканка золота, `building_gold_mines`,
   Consumer Electronics и Computer Assembly Plant, канонические имена зданий,
   корзины инфляции, локализация, `relationships`, BOM.
3. **Не закрыто снизу**: дубль инъекций в семь зданий Morgenröte — решается при
   сборке мегапака, выкинуть `zztr_mr_buildings.txt` и
   `zztr_modified_mr_buildings.txt` из компача.

Побочно — кандидаты в `ef hotfix 1.13`, к компачу отношения не имеют:
`building_naval_base` и `building_military_shipyard` удалены из ванили в 1.13, а E&F
их ещё зовёт; `building_vineyard_plantation` не существовал никогда;
`hardwood` стоит в знаменателе трёх корзин инфляции, не появляясь ни в одном
числителе.

---

# Сделано 21.08.2026: мод `_ef/ef+tr fix`

Всё, кроме потолка товаров, закрыто отдельным мини-модом, который грузится
**после** компача. Компач при этом не трогается: он остаётся «чужим» в
`out outdate`, а все правки живут в своём моде и переживают его обновление.

`_ef/ef+tr fix` — `[1.13] E&F + Tech & Res ComPatch Fix`, 10 файлов:

| файл | что делает | как |
|---|---|---|
| `common/buildings/zzzz_ef_tr_fix_buildings.txt` | `building_gold_mine` вместо опечатки `..._mines`; ликвидность и stock-группа для `building_computer_assembly_plant` и `building_consumer_electronics_industry` | `INJECT:` |
| `common/buildings/zzzz_ef_tr_fix_buildings_gen.txt` | три ванильных здания, пересобранные от актуального T&R + две группы E&F | `REPLACE:`, генерируется |
| `common/production_methods/zzzz_ef_tr_fix_gold_minting.txt` | чеканка 1250 / 1500 / 1750 трём новым ступеням золотой шахты | `INJECT:` |
| `common/scripted_effects/zzzz_ef_tr_fix_effects.txt` | переключение частной собственности для 12 зданий по каноническим именам | новый ключ |
| `common/scripted_effects/zzzz_ef_tr_fix_effects_gen.txt` | `financial_crash_consequences` и `economic_crisis_consequences` с исправленными именами | `REPLACE:`, генерируется |
| `common/script_values/zzzz_ef_tr_fix_inflation_gen.txt` | корзины `inflation_on_raw_material` и `..._manufactured_goods` сведены | переопределение, генерируется |
| `common/on_actions/zzzz_ef_tr_fix_on_actions.txt` | подключение эффекта к `on_yearly_pulse_country` и `on_production_method_changed` | аддитивно |
| `common/history/global/zzzz_ef_tr_fix_init.txt` | тот же эффект один раз на старте | аддитивный `GLOBAL` |
| `localization/russian/…` | 7 названий PM | — |
| `README.md` | стимовский BBCode + раздел про сопровождение | — |

Плюс `tools/regen_ef_tr_copies.py` — генератор трёх `_gen`-файлов.

## Решения, которые стоит зафиксировать

**Почему отдельный мод, а не форк компача.** Форк означал бы владение 100 КБ
`zef_01_financial_scripted_effects.txt`, который сам по себе — копия файла E&F.
Каждое обновление E&F пришлось бы сводить руками. Мод сверху владеет 27 КБ, из
которых 23 КБ генерируются одной командой.

**Почему `private_ownership_production_stocks` не переопределён.** Там 82 КБ
ради двенадцати блоков. Вместо этого — свой эффект в своём `on_action`:
`on_actions` аддитивны, так что ни E&F, ни компач, ни `ef+morg` ничего не теряют.
Это ровно тот приём, что уже применён в `ef+morg done`.

**Почему два кризисных эффекта всё-таки переопределены.** Из чужого
`scripted_effect` нельзя дописать элемент в `or`-список. Единственный способ
починить имена — переизложить эффект целиком. Файл генерируется, а не пишется
руками, и в его шапку каждый прогон печатает список подстановок:

```
###   economic_crisis_consequences: building_artillery_foundries -> building_artillery_foundry
###   economic_crisis_consequences: building_financial_centre_TUS -> building_financial_centre_tus
###   economic_crisis_consequences: dropped building_military_shipyards
###   economic_crisis_consequences: added building_computer_assembly_plant
###   …
```

Если после обновления компача список поедет — это видно сразу, без диффа.

**Почему 11 имён продублированы, а не заменены.** Девять из них — настоящие
`aliases` ванильных зданий и, скорее всего, резолвятся. Проверить это дешевле в
игре, чем угадать. Поэтому в `zzzz_ef_tr_fix_effects.txt` переключение
повторено под каноническими именами: если алиасы работают, все блоки —
no-op (условие не сойдётся, здание уже на нужном PM); если нет — они и делают
работу. В кризисных эффектах, где дублировать нельзя, имена именно заменены.

**Чеканка золота: 1250 / 1500 / 1750.** Ваниль держит ~33 единицы чеканки на
единицу выпуска золота (8/250, 15/500, 25/750, 30/1000) и шагает по 250.
Новые ступени дают 35 / 45 / 50 золота — отсюда числа. Через `INJECT:`, потому
что он в блоках модификаторов суммирует: если автор компача когда-нибудь
добавит свою чеканку, значения сложатся, и это будет видно. Если добавит —
файл надо удалить.

## Что вскрылось по ходу правки

**Корзины инфляции разъезжаются у обоих компачей.** Каждое из пяти значений —
средневзвешенное: числитель суммирует отклонение цены на объём заказов,
знаменатель — те же объёмы. Товар только в числителе завышает инфляцию, только
в знаменателе — размывает её к нулю. Состояние на сегодня:

| корзина | E&F | компач T&R | `ef+morg done` |
|---|---|---|---|
| consumer_goods | 21/21 ✔ | 34/34 ✔ | 25/25 ✔ |
| energy | 4/5 — лишний `hardwood` | 9/10 — то же | — |
| raw_material | 6/7 — лишний `hardwood` | 12/12, но нет `bauxite` и `hardwood` дважды | 7/8 — то же, что у E&F |
| manufactured_goods | 8/9 — лишний `hardwood` | 23/23, но нет `alloys` | — |
| military_equipment | 7/7 ✔ | 8/8 ✔ | — |

Фикс-мод чинит `raw_material` и `manufactured_goods`. `hardwood` в знаменателе
трёх корзин без числителя — это E&F, в файлах E&F, и место ему в хотфиксе, а не
здесь; в `raw_material` вопрос уже закрыт самим компачем, который добавил
`hardwood` в числитель.

**Компач и `ef+morg done` переопределяют одни и те же значения.**
`inflation_on_consumer_goods` и `inflation_on_raw_material` определены обоими.
Позже загруженный побеждает целиком, товары проигравшего из корзины выпадают —
сегодня выпадают `air_travel` и `good_uranium`. Фикс-мод грузится последним и
поэтому может свести их: `regen_ef_tr_copies.py --morg`. В репозиторий положена
версия без Morgenröte (мод объявляет зависимости только на E&F и T&R) —
**для мегапака пересобрать с `--morg`**.

## Что осталось нерешаемым снизу

- **Строка `building_gold_mines` в `error.log`.** Добавить правильный ключ можно,
  удалить чужой неправильный — нет. Уйдёт только правкой самого компача.
- **Двойная инъекция в семь зданий Morgenröte.** `ef+morg done` и компач
  инжектят одни и те же группы. Убрать дубль сверху = переизложить семь
  определений зданий T&R, то есть завести ровно тот дрейф, от которого мы
  избавляемся. Правильное место — сборка мегапака: выкинуть
  `zztr_mr_buildings.txt` и `zztr_modified_mr_buildings.txt`.
- **Потолок 128 товаров.** По договорённости отложено.

## Синхронизация

Игровая папка `mod/` в этой сессии не примонтирована — в неё ничего не
скопировано. После проверки `diff -rq` между репозиторием и `mod/` обязателен.

## Чеклист проверки в игре (заменяет прежний)

Порядок загрузки: CMF → ETF → E&F → **ef hotfix** → T&R → KAI → компач → **ef+tr fix**.

1. **Старт вообще** — годно / не годно. Пока потолок товаров не решён, сборка
   должна вылетать при входе в игру (157 товаров). Если стартует — арифметика
   потолка неверна, и это надо знать до всего остального.
2. **Электростанция, панель здания** — должны быть и вкладка Power Transmission
   (DC / half / AC), и Market Liquidity, и Private Ownership. Дата-оптимизации
   быть не должно (T&R её оттуда убрал). Годно / не годно.
3. **Автозавод** — верхняя ступень дата-оптимизации называется Algorithmic
   Dispatch, не Internet Data Optimization.
4. **Золотая шахта, США или Трансвааль** — вести вверх по группе Mining
   Equipment после `compression_ignition`: `country_minting` должен расти
   1000 → 1250 → 1500 → 1750, а не падать в ноль.
5. **Алиасы в скоупах** — довести `private_ownership_fraction` текстильной
   фабрики выше 0.5 и посмотреть, переключился ли PM частной собственности.
   Переключился → алиасы резолвятся и половина `zzzz_ef_tr_fix_effects.txt` —
   страховка; не переключился → она и есть механика.
6. **Consumer Electronics и Computer Assembly Plant** — в панели есть Market
   Liquidity и Private Ownership, и PM переключается по доле частника.
7. **`error.log` после 5 игровых лет** — ожидаемо остаётся только
   `building_gold_mines`. Появление `building_artillery_foundries`,
   `building_military_shipyards`, `building_naval_base`,
   `building_vineyard_plantation` или
   `pm_private_ownership_majority_manufacture_stock` означает, что фикс-мод
   грузится не последним.
8. **Здания MR** при одновременно включённых `ef+morg` и компаче — не задвоилась
   ли PM-группа в панели. Годно / не годно.
9. **Частный стройсектор E&F** — на `Arc Welded Buildings` страновая стройка
   должна вырасти на **25**, не на 30 и не упасть на 5. Это проверка семантики
   `INJECT:` в блоках модификаторов, от неё зависит файл чеканки золота.
