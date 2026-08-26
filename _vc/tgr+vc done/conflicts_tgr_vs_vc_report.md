# TGR × VC — разбор пары, 25.08.2026

Прогон на текущих распаковках: `vic3_mods_out/TheGreatRevision` и `vic3_mods_out/VC`, ваниль 1.13.11.
Инструменты: `tools/pair_matrix.py --pair "TGR,VC"`, `tools/scan_conflicts.py`, `tools/compare_gui_names.py`,
плюс разовые скрипты в `_tmp_analysis/` (`tgr_vc_dump.py`, `tgr_vc_short.py`, `bp_cmp.py`).

**Порядок загрузки: TGR (позиция 4) → … → VC. VC грузится последним и выигрывает все жёсткие перекрытия.**

## Числа

| | январь 2026 (старый отчёт) | 25.08.2026 |
| --- | --- | --- |
| общих путей файлов | 12 | **14** |
| общих ключей `common/*` (не-аддитивных) | 137 | **172** |
| дублей локализации | 0 | **0** |
| дублей id событий | 0 | **0** |
| пересечений имён виджетов `.gui` | 0 | **0** (TGR: 1 файл `budget_panel.gui`, VC: 5 файлов, ноль общих имён) |

### Что изменилось с января

* **TGR выбросил папку `map_data/` целиком.** Двух перекрытий `map_data/state_regions/00_west_europe.txt` и `11_east_asia.txt` из старого отчёта больше нет. Карту в этой паре не трогает никто — вся карта остаётся за VC.
* **VC выбросил `common/history/countries/brz - brazil.txt`.** Файл был в старом компаче; сейчас бразильские правки TGR доживают до игры сами.
* **Появились четыре новых перекрытия по путям:** `common/decisions/canada_australia.txt`, плюс `jap - japan.txt`, `net - netherlands.txt`, `spa - spain.txt` в `history/countries` и `common/parties/religious_party.txt`.
* **Старое утверждение про `common/defines` неверно на текущих версиях.** Отчёт января числил столкновения внутри `NAI` (`PRODUCTION_BUILDING_AUTONOMOUS_INVESTMENT_*`). Сейчас у VC в `NAI` всего два ключа, и **ни один define не пересекается** — см. ниже.
* **`common/ideologies/ideology_utilitarian_leader` из пересечения ушёл.**

## Итог по категориям

| категория | ключей | вердикт |
| --- | --- | --- |
| `common/buildings` | 17 | **noneed** |
| `common/technology/technologies` | 6 | **noneed** |
| `common/production_methods` | 3 | **noneed** |
| `common/defines` | 4 группы | **noneed**, 0 общих define |
| `common/decisions` / `manifest_destiny.txt` | путь | **noneed по порядку** (держится на HC) |
| `common/static_modifiers` / `base_values` | 1 | дёшево: переиздать три `INJECT:` TGR |
| `common/decisions` / `canada_australia.txt` | 4 + путь | дёшево: файл TGR целиком |
| `common/interest_groups` | 8 | мердж, механический |
| `common/parties` | 4 + путь | мердж, механический + одна развилка |
| `common/government_types` | 2 | мердж |
| `common/pop_needs` | 8 | мердж + правило |
| `common/company_types` | 12 | мердж по каждой компании |
| `common/history/countries` | 8 путей | мердж, механический |
| `common/buy_packages` | 99 | **развилка**: два разных экономических замысла |
| `common/country_formation` GER + `common/journal_entries` (3) | 4 | **развилка**: чьё объединение Германии |

---

## 1. Не конфликт — с обоснованием

### 1.1 `common/buildings` — 17 ключей, noneed

TGR переиздаёт 17 промышленных зданий `REPLACE_OR_CREATE:` полными телами (длина совпадает с ванильной ±1 строка).
VC по каждому из них делает **`TRY_INJECT:` ровно одного под-блока `can_build_private`**, которого нет ни у ванили, ни у TGR.

`INJECT:` сливает под-блоки в запись; под-блок с именем, которого больше никто не называет, просто добавляется.
Тела TGR остаются базой целиком — `production_method_groups`, `unlocking_technologies`, `building_group`, `ownership_type` не тронуты.

### 1.2 `common/technology/technologies` — 6 ключей, noneed

Обе стороны только `INJECT:`, кроме `mutual_funds` (у TGR ещё и `REPLACE_OR_CREATE:` из `TGR_LOANS_society.txt`, но VC инжектит поверх, тело TGR цело).

| тех | TGR инжектит | VC инжектит | пересечение |
| --- | --- | --- | --- |
| `civilizing_mission` | `modifier` | `on_researched` | разные под-блоки |
| `human_rights` | `modifier` | `on_researched` | разные под-блоки |
| `cotton_gin` | `modifier: country_institution_incentive_primary_max_investment_add` | `modifier: goods_output_fabric_mult` | разные ключи модификатора |
| `field_works` | `modifier: country_institution_defense_max_investment_add` | `modifier: battle_casualties_mult` | разные ключи |
| `logistics` | `modifier: country_institution_defense_max_investment_add` | `modifier: state_conscription_rate_mult`, `military_formation_attrition_risk_mult` | разные ключи |
| `mutual_funds` | `modifier: state_building_trade_center_max_level_add` | `modifier: country_free_charters_add` | разные ключи |

Повторяющиеся ключи внутри блока модификаторов складываются, но здесь складывать нечего — наборы ключей не пересекаются.

### 1.3 `common/production_methods` — 3 ключа, noneed

`pm_no_passenger_trains`, `pm_steel_passenger_carriages`, `pm_wooden_passenger_carriages`.
TGR переиздаёт их `REPLACE_OR_CREATE:` полными телами (меняет `goods_output_transportation_add`: 15→30 и 10→20).
VC делает `INJECT: building_modifiers = { unscaled = { building_job_attractiveness_mult = 2 } }`.

У TGR внутри `building_modifiers` названы `workforce_scaled` и `level_scaled`; VC добавляет `unscaled`. Три разных именованных под-блока — складываются, ничего не теряется.

> **Внимание:** эти же три метода есть в парах LLWA × VC (LLWA.3) и Grey's × VC (GR.1). По правилу «один файл — одна пара» файла на них здесь не заводим, но при разборе тех пар помнить, что тело победителя в текущей цепочке — TGR.

### 1.4 `common/defines` — 4 группы, 0 общих define

Defines сливаются поключево. Считано по отдельным ключам внутри групп:

| группа | ключей у TGR | ключей у VC | пересечение |
| --- | --- | --- | --- |
| `NAI` | 93 | 2 | **0** |
| `NCharacters` | 5 | 2 | **0** |
| `NEconomy` | 48 | 15 | **0** |
| `NPops` | 6 | 27 | **0** |

У VC в `NAI` только `BUILDING_PRIVATIZATION_CHANCE` и `CONSTRUCTION_MAX_NUM_PRODUCTION_BUILDING_CONSTRUCTIONS_SCALED_MAX`; TGR ни того, ни другого не называет.
Старый вывод отчёта января («столкновения внутри NAI») на текущих версиях не подтверждается.

### 1.5 `common/decisions/manifest_destiny.txt` — noneed, держится на порядке

* ваниль: решение `manifest_destiny`, 4024 байта;
* TGR: своя редакция, 3961 байт;
* VC: **файл из 11 байт — `#nothing`** (BOM + комментарий), гасит и ваниль, и TGR.

Компач не нужен, потому что **дальше по цепочке Hail Columbia гасит Manifest Destiny ещё раз** — везёт файл по тому же пути с полностью закомментированным решением и заменяет механику журнальной цепочкой на 1100 строк (см. HC.2). Что бы мы здесь ни восстановили, HC съест это следующим слоем.

> **Требование к порядку в README:** обоснование действует, только пока Hail, Columbia! стоит в наборе и грузится после VC. Уберём HC — вернётся вопрос «восстанавливать ли Manifest Destiny от TGR».

---

## 2. Дёшево

### 2.1 `common/static_modifiers` / `base_values`

VC делает `REPLACE_OR_CREATE:base_values` полным телом на 103 строки и уносит три `INJECT:` TGR:

| файл TGR | что инжектит |
| --- | --- |
| `TGR_LOANS_code_static_modifiers.txt` | `country_loan_interest_rate_add = -0.2` |
| `TGR_POLITICS_code_static_modifiers.txt` | `country_bureaucracy_add = 200`, `country_authority_add = 200`, `country_influence_add = 200`, `country_officers_pol_str_mult = -2`, `country_soldiers_pol_str_mult = -1` |
| `TGR_TRADE_code_static_modifiers.txt` | `country_company_construction_efficiency_bonus_add = 0.20`, `state_max_trade_advantage_from_capacity_add = 0.05` |

**Лечение: один файл компача, переиздающий те же три `INJECT:` после VC.** Повторяющиеся ключи внутри блока модификаторов складываются, поэтому переиздание инжекта поверх более позднего тела — точное восстановление вклада TGR: результат = «значение VC + дельта TGR», ровно как у TGR относительно ванили.

Считать «сколько получится» тут не надо и нельзя: цифры TGR — слагаемые, а не итоговые значения. Он и в одиночку даёт не 200 бюрократии, а 300 (100 ванильных + 200 своих).

### 2.2 `common/decisions/canada_australia.txt` — 4 ключа + путь

Ни ваниль, ни `common/decisions` их не определяют: в ванили `canada_unite_can` и родня — **журнальные записи** (`common/journal_entries/00_canada_australia.txt`). Оба мода независимо принесли один и тот же сторонний файл, который переносит их в решения.

* **VC везёт этот файл без единой своей правки** (голые тела) и дополнительно гасит ванильный `journal_entries/00_canada_australia.txt` файлом на 11 байт;
* **TGR везёт тот же файл + свои правки**, помеченные `#TGR ADJUSTMENTS`: `REPLACE_OR_CREATE:` на четыре ключа, закомментированное требование `relations:root >= relations_threshold:amicable`, `days = short_modifier_time` вместо `years = 1`, гейт `has_technology_researched = nationalism` + `game_date > 1865.1.1` вместо `pan-nationalism`.

Полный дифф TGR ↔ VC — это ровно эти правки плюс пробелы. **Лечение: положить в компач файл TGR по тому же пути.** Он и есть мердж: база у обоих одна.

> **Проверено и оказалось не багом.** Сначала было записано, что `has_technology_researched = pan-nationalism` через дефис — опечатка VC и молчаливо ложный триггер. Ваниль объявляет технологию именно так: в `common/technology/technologies/30_society.txt` рядом лежат `nationalism` и `pan-nationalism`, дефис настоящий. Значит правка TGR (`nationalism` + `game_date > 1865.1.1`) — осознанное смягчение условия, а не починка. Автору VC писать не о чем.

---

## 3. Мердж, механический

Во всех трёх случаях правки TGR помечены в его файлах комментарными рамками, поэтому мердж выводится скриптом, а не глазами.

### 3.1 `common/interest_groups` — 8 ключей

Оба мода делают `REPLACE_OR_CREATE:` полными телами, VC выигрывает. **Но развилки здесь нет:** VC переписывает ИГ крупно (141–395 изменённых строк против ванили), а TGR — точечно (8–79 строк), и все его правки помечены `##### TGR CHANGES #####` / `##### TGR ADDITION #####`.

| ИГ | строк у TGR vs ваниль | строк у VC vs ваниль |
| --- | --- | --- |
| `ig_armed_forces` | 12 | 395 |
| `ig_devout` | 8 | 254 |
| `ig_industrialists` | 32 | 179 |
| `ig_intelligentsia` | 38 | 333 |
| `ig_landowners` | 9 | 266 |
| `ig_petty_bourgeoisie` | 79 | 278 |
| `ig_rural_folk` | 22 | 141 |
| `ig_trade_unions` | 62 | 50 |

Что несёт TGR (сквозная правка во всех восьми): в блоке `scope:interest_group` — `multiply = 0.0025` → **`0.030`** и снятие `?=`. Это ядро его переработки притяжения попов в ИГ.
Точечно сверх этого: базовые веса (`value = 150 → 250` у интеллигенции и профсоюзов, `200 → 250` / `200 → 150` у крестьян, `250 → 200` и `50 → 100` у промышленников), блок «`law_appointed_bureaucrats` ×2 для академиков/бюрократов/клерков», три множителя за `egalitarianism` / `labor_movement` / `socialism` у профсоюзов, армейские building_group и `law_dedicated_police` у мелкой буржуазии, и удаление у `ig_armed_forces` ванильных `is_in_geographic_region = geographic_region_latin_america` + `add_modifier = age_of_caudillos_modifier`.

**Мердж: тело VC + перенос помеченных блоков TGR.** Генератором.

### 3.2 `common/parties` — 4 ключа, они же 4 перекрытия по путям

TGR везёт все 13 ванильных файлов партий (+ свой `conservative_party_borgez.txt`), VC — четыре. Пересекаются четыре.

**Важно: у TGR и VC общая не-ванильная база.** Оба одинаково добавляют десятки гейтов `exists = c:XXX` в `triggered_desc` и одинаково выпиливают японские `party_taikunate_*` / `party_ezo_*`. Это чужой общий источник, а не совпадение; мерджить надо только собственные дельты.

Дельты TGR (все помечены `########## TGR ADJUSTMENTS ##########`):

1. снято ограничение «ИГ не должна быть маргинальной» в `unlocking`;
2. `+50` веса профильной ИГ в каждую партию (landowners → conservative, intelligentsia → liberal, trade unions → radical, devout → religious);
3. **множитель «3 и более участников» `0.5 → 0.0`** и закомментированная ветка `else_if scope:number = 3` — «максимум 2 ИГ в партии».

Дельты VC: бонусы за идеологии (`ideology_imperialism` +10, `ideology_catholic_church` +5, `ideology_bourgeoisie_capitalism` +10, немецкая партия Центра +50), новые `triggered_desc` (`party_dzp`, `party_constitutional_reform_party`), и **разбиение ванильной ветки «3 и более» на `= 3` (×0.05) и `> 3`**.

Пункты 1 и 2 переносятся без спора. **Пункт 3 — развилка: оба автора правили ровно этот блок.**

### 3.3 `common/government_types` — 2 ключа

`gov_presidential_democracy` и `gov_presidential_dictatorship`, оба `REPLACE_OR_CREATE:`, VC выигрывает.

* TGR добавляет требование избирательного права (`OR` из четырёх законов голосования у демократии, `country_has_voting_franchise = no` у диктатуры) и сворачивает ванильные `NAND` про `je_peru_bolivia` / `ezo_republic_var` в `NOT = { has_journal_entry = je_peru_bolivia }`;
* VC добавляет `NOT = { country_has_primary_culture = cu:yankee }` и запрет для сабджектов GBR/IMP с монархией, меняет `has_law_or_variant` на `has_law`, и **те же ванильные `NAND` удаляет целиком**.

Оба независимо убрали ванильные `NAND` — восстанавливать их нельзя, это было бы поведение, которого не хочет ни один автор.
**Мердж: тело VC + гейты избирательного права от TGR.** Спора нет, требования ортогональны.

### 3.4 `common/history/countries` — 8 файлов

VC перекрывает по пути, вклад TGR теряется целиком. Правки TGR по файлам:

| файл | что несёт TGR |
| --- | --- |
| `aus - austria.txt` | `add_company = company_gebruder_thonet` (STATE_STYRIA, 1830); убран ванильный `ig:ig_intelligentsia ?= { add_ruling_interest_group }` |
| `chi - china.txt` | `add_company = company_ong_lung_sheng_tea_company` (STATE_FUJIAN, 1820) |
| `jap - japan.txt` | `add_company = company_mitsui` (STATE_KANTO, 1817) |
| `net - netherlands.txt` | `add_company = company_philips` (STATE_HOLLAND, 1830) |
| `tur - ottoman empire.txt` | `add_company = company_imperial_arsenal` (STATE_EASTERN_THRACE, 1832) |
| `spa - spain.txt` | крупная переработка: `add_company = company_altos_hornos_de_vizcaya`, дата выборов, снятые техи и законы (`law_latifundias`, `law_national_guard`, `law_elected_bureaucrats`, `law_diplomatic_navy`), снятые поправки, снятый `initialise_caciquismo_effect`, смена правящей ИГ, снятые события карлистской войны |
| `fra - france.txt` | смена правящей ИГ на landowners + industrialists, `law_tenant_farmers` вместо `law_peasant_proprietorship`, снятые `law_professional_navy`, `law_combination_acts`, `law_colonial_slavery`, снятые поправки `amendment_200_franc_suffrage` и `amendment_tradition_of_free_elections`, компания переехала в STATE_LANGUEDOC |
| `gbr - great britain.txt` | снятые `law_professional_navy` и `law_anti_strike_laws`, закомментированные `add_owned_country = c:HBC` и `c:BIC`, снятый `free_elections_var` + поправка |

Правки VC — почти всё аддитивное: поправки к законам (`add_amendment`), журнальные записи, модификаторы, переменные, техи; из вычитающего — только `law_appointed_bureaucrats` → `law_imperial_examination` у Китая, снятый `law_per_capita_based_taxation` у Франции, снятый `law_migration_controls` и добавленный `law_restricted_child_labor` у Британии, `empiricism` → `egalitarianism` у Испании.

Пересечений по одним и тем же строкам почти нет — можно наложить дельты TGR на тело VC файл за файлом.

Два случая, где оба независимо удалили одно и то же (`set_variable = ryukyu_rival_member` у Китая) — не восстанавливать.

> **Внимание на цепочку:** `chi - china.txt` и `tur - ottoman empire.txt` дальше по цепочке перекрываются аддоном-HC (там уже лежат мерджи «тело MoH + компания TGR» и «тело GoB + компания TGR»). Файлы аддона-VC на этих двух путях будут затенены аддоном-HC — это нормально и нужно для сборок без HC. Вклад VC в них дописывается задачей HC.7.

---

## 4. Мердж по каждой записи

### 4.1 `common/company_types` — 12 компаний

Оба `REPLACE_OR_CREATE:`, VC выигрывает. Здесь, в отличие от ИГ, **правок у TGR больше, чем у VC**:

| компания | строк у TGR vs ваниль | строк у VC vs ваниль |
| --- | --- | --- |
| `company_united_fruit` | 58 | 11 |
| `company_russian_american_company` | 52 | 16 |
| `company_east_india_company` | 50 | 16 |
| `company_william_cramp` | 43 | 5 |
| `company_compania_sansinena_de_carnes_congeladas` | 35 | 4 |
| `company_mitsui` | 35 | 17 |
| `company_imperial_arsenal` | 31 | 17 |
| `company_ong_lung_sheng_tea_company` | 31 | 11 |
| `company_philips` | 26 | 14 |
| `company_gebruder_thonet` | 25 | 9 |
| `company_kablin` | 19 | 12 |
| `company_krupp` | 9 | 5 |

Что делает TGR: переписывает `building_types`, снимает ванильные `prerequisite`/`possible`/`attainable` условия (уровни 5 → 1, регионы → конкретный штат), и **ставит `ai_weight = 9999` вместо ванильных `value = 3`** — это его способ заставить ИИ действительно основывать флейворные компании.
Что делает VC: свои `prosperity_modifier` / `country_modifiers` (например `goods_output_meat_mult` вместо `building_port_throughput_add`), смена `category`, добавление зданий в список.

Разбирать по каждой компании отдельно: у части спор идёт за один и тот же под-блок (`building_types`, `ai_weight`), у части — за разные.

### 4.2 `common/pop_needs` — 8 ключей

Оба `REPLACE_OR_CREATE:`, VC выигрывает. Структура записей одинаковая (`default` + `entry`), спор идёт по числам, и **замыслы разные, но почти ортогональные:**

* **TGR правит `max_supply_share` и `min_supply_share`** — сужает потолок доли одного товара (0.75–1.0 → 0.3–0.5) и поднимает пол (0.0 → 0.2–0.3). Это его система «попы обязаны потреблять разнообразно»;
* **VC правит `weight`** — вес товара внутри потребности (и в трёх местах ещё `max_supply_share`).

| потребность | что несёт TGR | что несёт VC | спор |
| --- | --- | --- | --- |
| `popneed_basic_food` | max 0.9→0.3, min 0→0.2 по всем entry; weight 0.85→1, 1.15→1 | weight 1.15→1.5 | weight последнего entry |
| `popneed_crude_items` | min 0→0.3 у второго entry | weight 2→3 | нет |
| `popneed_heating` | max 0.8/1.0→0.5, min 0→0.25, weight 3→2 | нет правок вообще | нет |
| `popneed_household_items` | max 0.75→0.6 / 0.5, min → 0.25–0.3 | weight 1→2, max 0.75→0.9 | `max_supply_share` первого entry |
| `popneed_intoxicants` | max 0.75→0.3, min 0→0.25, weight 0.25→1 | `prestige_goods_demand_increase` 0.75→1.0, max 0.75→0.9 и 0.25→0.5, weight 0.9→1 | `max_supply_share` по всем entry |
| `popneed_luxury_drinks` | max 0.75/0.33→0.35, min 0→0.3, weight 0.45→1 | weight 0.45→0.5, max 0.33→0.75 | последний entry |
| `popneed_luxury_food` | max →0.3, min →0.2, **добавлен entry `fish`** | weight 1.25→1, 0.75→1, 1.5→3, max 0.75→0.5 и 0.5→0.25 | почти по всем entry |
| `popneed_simple_clothing` | min 0→0.3 у второго entry | weight 2→3 | нет |

Правило, которое закрывает семь случаев из восьми: **`min_supply_share` и `max_supply_share` — за TGR, `weight` — за VC там, где VC отклоняется от ванили, иначе за TGR.** Плюс перенести добавленный TGR entry `fish` в `popneed_luxury_food`.

---

## 5. Развилки — нужно решение

### 5.1 `common/buy_packages` — 99 пакетов `wealth_1` … `wealth_99`

TGR везёт файл по ванильному пути `common/buy_packages/00_buy_packages.txt` голыми телами; VC — `joi_buy_packages.txt` с `REPLACE_OR_CREATE:` на все 99. **VC выигрывает всё.**

Как и с партиями, **у обоих общая не-ванильная база**: в низких пакетах их числа совпадают друг с другом и оба отличаются от ванили (`wealth_7`: ваниль basic_food 115, оба — 118; crude_items ваниль 27, оба — 26).

Собственные замыслы:

* **TGR** (написано в шапке его файла): `+25%` потребления `popneed_basic_food` / `popneed_luxury_food` / `popneed_luxury_drinks` с `wealth_10` по `wealth_20` и `+50%` с `wealth_21` по `wealth_99`; плюс поднятые `popneed_intoxicants` и `popneed_stimulants`.
* **VC**: переписаны `popneed_services` (в среднем вдвое вниз), `popneed_luxury_items`, `popneed_free_movement`, `popneed_communication`, `popneed_leisure`, `popneed_standard_clothing`, `popneed_heating`.

Статистика расхождений (94 пакета, где TGR отличается от ванили; 98 — где отличается VC):

| потребность | пакетов правит TGR | пакетов правит VC | пакетов, где спорят оба |
| --- | --- | --- | --- |
| `popneed_luxury_drinks` | 85 | 85 | **85** |
| `popneed_basic_food` | 23 | 23 | **23** |
| `popneed_intoxicants` | 23 | 38 | **22** |
| `popneed_luxury_food` | 80 | 20 | **20** |
| `popneed_services` | 19 | 90 | **19** |
| `popneed_household_items` | 16 | 35 | **16** |
| `popneed_stimulants` | 25 | 16 | **16** |
| `popneed_luxury_items` | 15 | 85 | **15** |
| `popneed_standard_clothing` | 13 | 30 | **13** |
| `popneed_free_movement` | 11 | 84 | **10** |
| `popneed_crude_items` | 8 | 8 | **8** (значения совпадают — общая база) |
| `popneed_simple_clothing` | 7 | 7 | **7** (совпадают) |
| `popneed_leisure` | 6 | 80 | **6** |
| `popneed_heating` | 0 | 19 | 0 |
| `popneed_communication` | 0 | 80 | 0 |

Механическое правило есть, и оно закрывает большую часть: **где обе стороны совпадают — общая база, брать как есть; где отклоняется только одна — брать её; где обе отклоняются по-разному — нужно решение.**
Спорных ячеек порядка 230, и почти все — это `popneed_luxury_drinks`, `popneed_basic_food` и `popneed_intoxicants`, то есть ровно тот множитель TGR.

**Предлагаемое решение: база — числа VC, поверх них применить множители TGR (+25% с wealth_10, +50% с wealth_21) к трём потребностям, которые он в шапке и называет.** Тогда обе переработки живут: у VC остаются его услуги/досуг/связь, у TGR — его «богатые едят больше». Генератором, из шапки TGR, а не руками.

### 5.2 Объединение Германии: `country_formation/GER` + три журнальные записи

Это единственное место в паре, где два мода не тюнингуют одно и то же, а несут **две разные механики одного события**, и вместе они не складываются.

| | TGR | VC |
| --- | --- | --- |
| `GER` в `country_formation` | `use_culture_states = yes`, `required_states_fraction 0.73 → 0.75`; сняты `custom_tooltip` про дуалистическую монархию, `NOT = { c:KUK }`, `max_num_formation_candidates = 3`, `can_be_formation_candidate`, `can_be_unification_target` | явный список **31 штата** (включая Богемию, Моравию, Австрию, Тироль, Штирию, Словению, Истрию), плюс гейт `deutsch_frankfurter_nationalversammlung_journal_has_finish_var` |
| `je_german_unification` | своя группа `je_group_historical_content`, две `scripted_button` (`je_badem_baviera_button`, `je_war_france_button`), убран `is_shown_in_lobby` | `c:PRU = THIS` → `c:PRU ?= THIS` (страховка от несуществующей Пруссии) |
| `je_north_german_unification` | полная переработка: `any_country` вместо `any_country_in_german_confederation`, ветка `has_modifier = great_revision_german_unification_stallmate`, `on_monthly_pulse` с событием `german_unification.3` (Бисмарк), `hidden_effect` с `change_infamy = -60` и аннексией **21 немецкого государства**, рассылка `great_revision_german_unification.6` | `any_country_in_german_confederation` → `any_country` (та же правка, что у TGR) |
| `je_schleswig_holstein_question` | своя группа, две `scripted_button`, снят `is_in_geographic_region`, `days = long_modifier_time` → `months = 120` | снят `is_in_geographic_region` в двух местах (та же правка) |

Сейчас **выигрывает VC, и вся немецкая переработка TGR мертва**: `great_revision_german_unification.*` не зовётся никогда, кнопки не рисуются, аннексия 21 государства не происходит. Ни строчки в логе.

Три варианта:

1. **TGR выигрывает Германию** — тело TGR + две правки VC (`?=` и `any_country`, обе безобидны). Гейт VC про Франкфуртское собрание при этом пропадёт вместе с его журнальной цепочкой;
2. **VC выигрывает** — не делать ничего, записать потерю явно и убрать TGR-овские `great_revision_german_unification.*` события из головы;
3. **Сшить**: список штатов от VC (он честнее описывает Великую Германию), кнопки и аннексию от TGR, гейт Франкфурта от VC. Дороже всего и рискованно: `has_variable` от VC ссылается на его журнальную цепочку, которую TGR не знает.

### 5.3 Партии: «максимум 2 ИГ в партии»

TGR обнуляет множитель за третьего и последующих участников (`0.5 → 0.0`) и комментирует ветку `= 3`. VC, наоборот, разводит `= 3` (×0.05) и `> 3`. Оба правили ровно этот блок намеренно.

* за TGR: «максимум 2 ИГ» — заявленная часть его политической переработки, вместе с `+50` профильной ИГ;
* за VC: он оставляет коалиции из трёх ИГ возможными, просто очень дорогими.

---

## 6. Что проверено и конфликтом не является

* **локализация — 0 дублей ключей** (и по каждой языковой папке отдельно тоже 0);
* **id событий — 0 пересечений**;
* **`.gui` — 0 общих имён виджетов и типов.** TGR везёт один файл (`budget_panel.gui`), VC — пять (`00_MDF_frontend_dlc.gui`, `add_wargoal_panel.gui`, `headlines_texticons.gui`, `sway_country_panel.gui`, `uboy_wargoal_country_filter.gui`), пересечения путей нет;
* **`common/goods` — у VC папки нет вообще**, потолок 128 эта пара не двигает;
* **`common/on_actions`, `common/named_colors`, `common/modifier_type_definitions`, `common/history/*` контейнерные ключи** — аддитивные категории, из подсчёта исключены;
* **`map_data` — TGR больше не везёт эту папку**, вся карта за VC.

## 7. Открытое

* **Развилки 5.1, 5.2, 5.3** — без решения файлы не пишутся.
* **`REPLACE:` и под-блоки.** В этой паре ни один новый `REPLACE:` не нужен — всё либо `REPLACE_OR_CREATE:` полным телом, либо переиздание чужого `INJECT:`. Вопрос из правил на эту пару не влияет.
* **Письмо автору VC** — по этой паре добавить нечего. Единственный кандидат (`pan-nationalism` через дефис) оказался ванильным именем, см. 2.2.

---

## 8. Что собрано — 25.08.2026

Компач лежит в `_vc/tgr+vc done`, генератор — `tools/regen_vc_tgr.py` поверх `tools/vic3merge3.py`.
`python3 regen_vc_tgr.py` пишет, `--check` только сверяет и возвращает 1, если файлы на диске разошлись с текущими распаковками.

**20 файлов, 141 top-level ключ, самопроверка `0 problem(s)`** (баланс скобок, BOM в некомментарных строках, дубли ключей по категориям, удвоенные префиксы).

| файл | что несёт |
| --- | --- |
| `common/buy_packages/zz_vc_tgr_buy_packages.txt` | 99 пакетов: числа VC, множители TGR |
| `common/interest_groups/zz_vc_tgr_interest_groups.txt` | 8 ИГ |
| `common/parties/zz_vc_tgr_parties.txt` | 4 партии |
| `common/company_types/zz_vc_tgr_company_types.txt` | 12 компаний |
| `common/pop_needs/zz_vc_tgr_pop_needs.txt` | 8 потребностей, мердж по полям |
| `common/government_types/zz_vc_tgr_government_types.txt` | 2 типа правительства |
| `common/country_formation/zz_vc_tgr_country_formation.txt` | GER |
| `common/journal_entries/zz_vc_tgr_german_unification.txt` | 3 журнальные записи |
| `common/static_modifiers/zz_vc_tgr_base_values.txt` | один `INJECT:` из трёх TGR-овских |
| `common/decisions/canada_australia.txt` | побайтовая копия файла TGR (перекрытие по пути) |
| `common/history/countries/*.txt` (8) | перекрытие по пути, мердж целых файлов |
| `common/ideologies/zz_vc_tgr_stances_on_tgr_laws.txt` | 56 идеологий VC, 1245 позиций по законам TGR |
| `common/ideologies/zz_vc_tgr_stances_on_vc_laws.txt` | 48 идеологий TGR, 480 позиций по законам VC |

### Позиции идеологий — единственная часть, которая не мердж

Всё остальное возвращает написанное одним из авторов. Здесь наоборот: это контент, которого нет ни у одного, и вывести его неоткуда.

TGR добавляет 13 групп законов и 60 законов, VC — 56 идеологий и 10 законов. **Ни одна идеология VC не высказывалась ни по одному закону TGR и ни одна идеология TGR — ни по одному закону VC.** ИГ во главе с персонажем VC был нейтрален ко всему политическому слою TGR: не продвигал его законы, не сопротивлялся им.

Автоматика не сработала намеренно: ближайший донор по сходству совпадает с целью на 25–50% выборки из 4–10 законов, и у самого донора покрыто 1–2 группы из 13. Поэтому **1725 позиций расставлены руками** в `vc_tgr_ideology_grid.xlsx`, который лежит рядом с компачем и служит источником для генератора. Правится таблица — перегоняется генератор.

Проверено после сборки: 1725 ячеек, ноль несуществующих идеологий, ноль несуществующих групп законов, **ноль законов, попавших не в свою группу** (сверено с `group =` в самих модах), ноль недопустимых ключевых слов.

Оба файла — `INJECT:`, а не полное тело: задача добавить группу, которую идеология никогда не называла. Именованные записи внутри инжектируемого под-блока переопределяют одноимённые, новые дописываются, поэтому `lawgroup_taxation = { law_askeri_tax = approve }` в идеологию, которая уже объявляет `lawgroup_taxation`, добавляет одну строку и не трогает остальное.

**Одна позиция не доживает в наборе с Hail, Columbia!**: `ideology_jacksonian_democrat` HC переобъявляет полным телом ниже по цепочке. Генератор проверяет это assert'ом и печатает предупреждение — переносить в `zz_hct_jacksonian_democrat.txt` аддона-HC.

### Как решались конфликты

Ваниль 1.13.11 — общий предок обоих модов по каждой записи, поэтому мердж трёхсторонний. Хунки, которых коснулась одна сторона, применяются обе. Кластеры, где обе стороны переписали одни и те же строки, — 38 штук, каждый напечатан прогоном.

Три правила понадобились сверх «кто победил»:

1. **Чистая вставка не конфликт.** VC вставляет свой контент внутрь кусков, которые TGR удалил (Франция: TGR снимает четыре ванильных закона, VC вставляет пять поправок ровно между ними). Считать это конфликтом и выбирать победителя означало выбросить вклад одного из авторов целиком.
2. **Объединение проверяется на скобки и на поля.** Британия: `ig:ig_intelligentsia = {` против `ig:ig_intelligentsia ?= {` — объединение выдаёт строку дважды и скобки перестают сходиться. Проверка ловит это и откатывается на VC. Отдельно: если обе стороны вносят одно и то же поле, объединение запрещено — `multiply = 2.0` следом за `multiply = 2` умножает дважды, а `limit` с обоими `scope:number > 3` и `= 3` не истинен никогда.
3. **Списковые элементы не приписываются.** East India Company: TGR закрывает `building_types` и открывает `extension_building_types`; допись `building_sugar_plantation` от VC после этого молча подшивает здание не в тот список, а скобки сходятся.

### Что осталось за бортом сознательно

* `radical_party`, кластер 312..327 — снятие ограничения «ИГ не должна быть маргинальной» у TGR не переносится: VC правил ровно эти строки. В трёх остальных партиях снятие перенесено.
* `ig_industrialists`, `multiply = 2.0` (TGR) против `multiply = 2` (VC) — взято VC.
* 100 ячеек `buy_packages` расходятся с собственными числами TGR больше чем на шаг округления. Это цена решения «база VC»: у `popneed_luxury_drinks` и `popneed_luxury_food` собственная база TGR ниже VC-шной. У `popneed_basic_food` производные числа совпадают с TGR ровно.

### Проверки после сборки

| против чего | общих ключей | комментарий |
| --- | --- | --- |
| мегапак `no t&r` | **0/0** | пересечений нет, аддон-VC ляжет поверх сборки чисто |
| TGR | 143 | это и есть работа компача |
| VC | 143 | то же |
| Hail Columbia | 4 | `ig_landowners`, `ig_rural_folk`, `ideology_jacksonian_democrat` + контейнер `COUNTRIES` |
| Mandate of Heaven | 6 | `ig_armed_forces`, `ig_intelligentsia`, `ig_petty_bourgeoisie`, `ig_rural_folk`, `ideology_communist` (там `INJECT:`, складывается) + контейнер |

Локализация и id событий — ноль пересечений со всеми пятью.

> **Следствие для HC.7, которого в плане не было.** HC везёт `common/interest_groups/00_landowners.txt` и `00_rural_folk.txt` голыми телами по ванильным путям и грузится ПОСЛЕ аддона-VC. Значит вклад этого компача в `ig_landowners` и `ig_rural_folk` до игры не доживает — его съедает HC, а дальше базой становятся `zz_hct_ig_landowners.txt` / `zz_hct_ig_rural_folk.txt` из аддона-HC. Правки TGR там уже есть (HC.1), а правок VC нет — это и есть задача HC.7. Для MoH ситуация мягче: он инжектит, а не переписывает, так что наши тела `ig_armed_forces`, `ig_intelligentsia`, `ig_petty_bourgeoisie` выживают и инжекты MoH ложатся сверху.
