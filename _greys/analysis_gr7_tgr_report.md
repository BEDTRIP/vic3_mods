# GR.7 — Grey's × TGR. Полный разбор 97 ключей. 26.08.2026

Повод — взяться за GR.7 (`План проекта.md`, аддон-Grey's). Пара считалась заблокированной
развилкой №3; развилка закрыта в этой же сессии (раздел 5), но выяснилось, что defines —
не главное в этой паре и даже не десятая её часть.

Метод — «Анализ 5» из `Правила работы с модами Victoria 3.md`: общий предок обеих сторон —
ваниль 1.13, поэтому каждый ключ раскладывался в три тела (ваниль / TGR / Grey's) и
сравнивался **поключево и по под-блокам**, а не «совпало имя — значит конфликт».
Скрипты разбора одноразовые, лежат вне репозитория; все цитаты ниже читались вживую.

Порядок загрузки: TGR идёт в общей части, Grey's — последним блоком цепочки.
**Во всех случаях побеждает Grey's.** Вопрос всегда один: что именно из TGR при этом умирает.

---

## 1. Итог одной таблицей

| класс | ключей | что делать |
| --- | --- | --- |
| **не конфликт**, проверено | 11 | ничего, обосновать в шапке |
| **чистая потеря структуры TGR** (поле, которого в ванили нет вообще) | 91 строка в 38 записях | восстанавливать |
| **правка TGR стёрта, Grey просто повторяет ваниль** | 28 строк | восстанавливать |
| **обе стороны отошли от ванили** — спор баланса | 40 строк | решение по записи, не по строке |
| **развилка** (два define) | 2 | **закрыта: значения soft_econ** |

Три находки ниже в плане не значились вовсе и по цене больше всего остального GR.7 вместе.

---

## 2. Чего не было в плане

### 2.1 Торговый центр теряет потолок — и с ним весь трейд-реворк TGR

`building_trade_center`: TGR ставит `has_max_level = yes` (в ванили этого поля нет).
`grey_usu/common/buildings/yMoG_USU_trade_center.txt` переопределяет здание
`REPLACE_OR_CREATE` полным телом и `has_max_level` **не называет**.

Цена не в самом потолке. **Десять** технологий TGR раздают
`state_building_trade_center_max_level_add = 10` каждая — `tech_bureaucracy`,
`international_trade`, `currency_standards`, `stock_exchange`, `corporate_charters`,
`mutual_funds` (все шесть — `INJECT:`) плюс `joint_stock_companies`, `investment_banks`,
`corporate_management`, `macroeconomics` (`REPLACE_OR_CREATE:`), все в
`TGR_TRADE_society.txt`. Это, по нашей же сводке, «становой хребет trade rework».
*(В `сводки по модам/сводка_tgr.md` названо шесть — сводку поправить, техов десять.)*

**Чего мы НЕ знаем и знать пока не можем.** Наши собственные правила
(`Правила работы с модами Victoria 3.md`, «Компании, здания, товары») говорят про пару
`has_max_level` + `state_building_*_max_level_add` прямо: мод, который переопределяет такое
здание полным телом и `has_max_level` не называет, **либо снимает потолок, либо наследует
его** — вопрос в игре не разрешён. Поэтому здесь два сценария, и оба плохи по-разному:
потолок снят — десять техов раздают прибавку к несуществующему пределу; потолок унаследован —
всё работает, и файл в компаче не нужен вовсе. **Проверяется одной загрузкой:** скриншот
панели торгового центра (есть ли строка максимального уровня) в ветке с Grey's.
До этой проверки файл не писать.

Туда же — `ai_value`: у TGR плоское `2000`, у `grey_usu` скрипт-значение по рангу страны
(1000 + 2000 великой державе и далее). Тут тело Grey богаче, брать его.
И `levels_per_mesh` 10 → 50 (косметика).

Добивает картину `NEconomy.AUTO_DOWNSIZE_BUILDING_MIN_UNUSED_TRADE_CAPACITY`: TGR поднял
20 → 100, `_grey_soft_econ` возвращает ванильные 20 (раздел 5). То есть управление
размером ТЦ у TGR отменяется с двух сторон сразу.

### 2.2 Двадцать одна запись владения теряет торговую ёмкость

`TGR_TRADE_private_infrastructure_investors.txt` навешивает на все методы владения

```
state_modifiers = { level_scaled = {
    state_weekly_trades_add = 0.5
    state_trade_capacity_add = 1
    state_tax_capacity_add   = 0.25
} }
```

`grey_usu/common/production_methods/yMoG_USU_owners_tax_pms.txt` переопределяет их своими
телами, где `state_modifiers` нет вообще. Пропадает на **21 записи**:

* 14 × `pm_company_headquarter_*` (`government_run`, `worker_cooperative`,
  `privately_owned` + 5 вариантов, `principle_divine_economics_2` + 5 вариантов);
* 3 × `pm_financial_district_*` (`privately_owned`, `publicly_traded`,
  `principle_divine_economics_2`);
* 4 × `pm_manor_house_*` (`privately_owned`, `bureaucrat_ownership`, `clergy_ownership`,
  `principle_divine_economics_2`).

`pm_trade_center` и `pm_trade_center_principle_external_trade_2` — случай **не такой**,
и это важно не перепутать: там торговая ёмкость у Grey's есть, но в другом под-блоке и
кратно меньше. TGR: `level_scaled = { state_weekly_trades_add = 10, state_trade_capacity_add = 50 }`.
Grey's (`_grey_soft_econ` и `grey_usu` дают тут одинаковые тела):
`workforce_scaled = { state_weekly_trades_add = 1, state_trade_capacity_add = 10 }`.
То есть и множитель другой (в 5–10 раз меньше), и масштабирование другое —
у TGR по уровням, у Grey's по укомплектованности. Это спор чисел и замысла, а не
выпавший блок; решать вместе с портами и рельсами (раздел 6C).

**Те же 14 записей HQ стоят в GR.5** (там их теряет E&F). Это ровно тот случай, под который
в `Правила — сборка.md` заведено исключение «файл, зависящий сразу от двух пар»: одну и ту
же запись нельзя чинить двумя файлами. Шапка обязана начинаться с «нужны оба мода».

### 2.3 У TGR два файла `country_ranks`, и план знал только про один

`TGR_TRADE_country_ranks.txt` — отдельный файл с `INJECT:` в шесть рангов:

| ранг | `state_export_advantage_mult` | `state_import_advantage_mult` |
| --- | --- | --- |
| major_power / unrecognized_major_power | −0.15 | 0.25 |
| minor_power | −0.25 | 0.50 |
| unrecognized_regional_power | −0.35 | 0.50 |
| insignificant_power | −0.50 | 0.75 |
| unrecognized_power | −0.60 | 0.75 |

Это механика «мелкие страны торгуют выгоднее, крупные платят за размер» — половина
смысла рангов у TGR. `_grey_soft_pop` делает `TRY_REPLACE` полными телами на все восемь
рангов и **уносит все двенадцать строк разом**.

### 2.4 `TGR_POLITICS_country_ranks.txt` — устаревшая копия ванили. Это НЕ наша пара

Признаки ровно те же, что у `grey_deeper_cinosphere` (GR.12) и `03_political_strategies.txt`
у LLWA: шапка файла написана по старой ванили (`diplo_pact_cost ... multiplied by 1 + this
amount` против нынешнего `multiplied by this amount - 1`), нет комментария про
`ai_pool_character_multiplier`, который ваниль 1.13 в шапку добавила. В телах отсутствуют
поля, которые в ванили 1.13 есть: `treaty_article_cost`, `ai_pool_character_multiplier`,
`ai_innovation_critical_threshold`, `country_max_unassigned_generals_add`,
`country_max_unassigned_admirals_add`; `country_support_independence_weekly_liberty_desire_add`
стоит ровно вдвое ниже нынешней ванили на всех четырёх рангах, где он есть.

Следствие, которое надо назвать вслух: **в ветке без Grey's (то есть в текущем мегапаке)
эти поля из рангов выпадают**, потому что `country_ranks` в наборе трогают только двое —
TGR и `_grey_soft_pop` (проверено обходом всех модов, мегапака и трёх аддонов).
`_grey_soft_pop` эту порчу молча лечит: его тела соответствуют ванили 1.13.
Задача не наша, но её надо завести — предлагаю **TGR.1**.

### 2.5 `building_food_industry` уходит из TGR-овской группы зданий

TGR переводит пищепром в `bg_consumer_goods` — **собственную группу TGR**, которой в ванили
нет (`parent_group = bg_manufacturing`, `lens = light_industry`, `cash_reserves_max = 25000`).
На неё завязаны промышленный декрет TGR и его законы экономических стимулов.
`grey_food/common/buildings/mog_food_industry.txt` возвращает `bg_light_industry` — и
пищепром выпадает из обеих механик. Ровно тот случай, про который в правилах написано
«похожие имена `building_group` у двух модов — это РАЗНЫЕ группы».

---

## 3. GR.7a — восемь рангов страны

Тело брать у `_grey_soft_pop` (оно соответствует ванили 1.13, см. 2.4), возвращать в него
правки TGR. Что именно возвращать:

| правка TGR | ранги | статус |
| --- | --- | --- |
| `state_export_advantage_mult` / `state_import_advantage_mult` | шесть (см. 2.3) | **восстановить, безусловно** |
| `country_construction_add = 30 / 20` | great_power, major_power | **восстановить** (в ванили поля нет вообще) |
| убранный `country_loan_interest_rate_mult` на всех рангах | все, где он есть в ванили | **решение**, см. ниже |

Про заём. TGR закомментировал `country_loan_interest_rate_mult` на всех рангах, причём на
great/major/minor — с собственной пометкой `#TGR ADJUSTMENT`, то есть сначала правил число,
потом выключил строку целиком. Это часть его системы займов (`TGR_LOANS` лежит внутри
основного мода, `base_values` даёт `country_loan_interest_rate_add = -0.2`).
`_grey_soft_pop` держит ванильные значения (−0.5 great, −0.25 major, +0.25 insignificant,
+0.5/+0.75/+1.0 непризнанным). Это **не потеря по недосмотру, а спор замыслов**: у TGR
ставка по займу перестаёт зависеть от ранга, у Grey's зависит по-ванильному.

Остальные расхождения ранга — `ai_innovation_critical_threshold`, `country_agitator_slots_add`,
`country_leverage_resistance_add`, `state_migration_pull_mult`, `building_throughput_add` —
это правки `_grey_soft_pop` поверх ванили, TGR их не касался. Не трогать.

## 4. GR.7b — четыре закона гражданства. Закрывается четырьмя строками

Здесь план был прав, а первое подозрение («спор замыслов») снялось сверкой с ванилью.

Ваниль уже задаёт `country_political_strength_full_acceptance_mult` на этих законах:
0.25 / 0.20 / 0.1 / 0.1 (ethnostate / national_supremacy / racial_segregation /
cultural_exclusion). TGR инжектит **ровно те же числа с минусом** — то есть его замысел
«погасить ванильную надбавку в ноль», классический контрвес сложением.
`_grey_soft_pop` в своём `TRY_REPLACE` переписывает `acceptance_modifier` целиком и
ставит там **ванильные** значения — инжект TGR ложится под тело и пропадает.

Раз числа Grey's совпали с ванильными, **переиздание чужого `INJECT:` поверх более
позднего тела даёт точное восстановление** (правило из раздела 1 правил): четыре блока
по одной строке в файле аддона, грузящемся после Grey's, и поле снова нетто-ноль.
Именно потому, что значения совпали, — проверять это при каждом обновлении `_grey_soft_pop`,
`!! MAINTENANCE !!` в шапку.

## 5. GR.7c — defines. Развилка №3 закрыта

Пересечений по отдельным define — **20**, из них 7 совпадают побайтово. Разбор оставшихся:

| define | ваниль | TGR | Grey's | вывод |
| --- | --- | --- | --- | --- |
| `NEconomy.PRICE_RANGE` | 0.75 | 0.85 | 0.9 (soft_econ) | **развилка №3 → soft_econ 0.9** |
| `NEconomy.BUY_SELL_DIFF_AT_MAX_FACTOR` | 2 | 1.65 | 3 (soft_econ) | **развилка №3 → soft_econ 3** |
| `NEconomy.COMPANY_MINIMUM_LEVELS_PER_HQ` | 5 | **1** | 5 | Grey повторяет ваниль → вернуть TGR |
| `NEconomy.AUTO_DOWNSIZE_BUILDING_MIN_UNUSED_TRADE_CAPACITY` | 20 | **100** | 20 | то же → вернуть TGR (см. 2.1) |
| `NPops.MAX_DEMAND_ADJUSTMENT_BASE_AMOUNT` | 0.01 | **0.05** | 0.01 | то же → вернуть TGR |
| `NPops.MAX_DEMAND_ADJUSTMENT_SCALED_AMOUNT` | 0.09 | **0.10** | 0.09 | то же → вернуть TGR |
| `NEconomy.AUTO_DOWNSIZE_BUILDING_MONTHS_TO_WAIT` | 6 | 1 | 2 | обе стороны правили осознанно → оставить Grey's 2 |
| `NEconomy.BUILDING_PROFIT_TARGET_TO_LOWER_WAGES` | 0.15 | 0.05 | 0.1999 | оставить Grey's: 0.1999 сцеплено с его же `..._TO_RAISE_WAGES = 0.2111` |
| `NAI.TRADE_CENTER_MINIMUM_GDP_UNRECOGNIZED_MULT` | 2.0 | 2.0 | 1 | TGR повторяет ваниль → потери нет |
| `NEconomy.BUILDING_PROFIT_TARGET_TO_HIRE_EMPLOYEES` / `..._TO_RAISE_WAGES` | 0.25 | 0.25 | 0.2 / 0.2111 | то же, потери нет |
| `NEconomy.BUILDING_PROFIT_TARGET_TO_WITHDRAW_CASH` | 0.15 | 0.20 | 0.2 | одно и то же число |

**Побочка развилки №3, которую надо помнить:** `_grey_soft_econ` ставит
`GOODS_SHORTAGE_PENALTY_THRESHOLD = 0.4` с комментарием автора «по умолчанию должно быть
1 / BUY_SELL_DIFF_AT_MAX_FACTOR». При выбранном значении 3 это 0.33 — близко, набор
самосогласован. При значении TGR 1.65 было бы 0.61, и порог разошёлся бы с ценовым
механизмом; это и есть причина, по которой брать TGR-овские числа было бы дороже,
чем кажется.

`NPolitics` (`grey_subject` против TGR) в пересечение не попал ни одним ключом — **не конфликт**.

## 6. Пятьдесят шесть производственных методов

Разложены на три класса. Полная построчная выкладка — в конце раздела.

**A. TGR добавил поле, которого в ванили нет; Grey его не несёт — 91 строка.**
Сюда попадает всё из 2.2 (21 запись × 3 строки = 63), торговые центры
(`state_trade_capacity_add`, `state_weekly_trades_add`, `ai_value` 1/5/50000/100000,
`is_hidden_when_unavailable`, `replacement_if_valid`), `state_market_access_price_impact = 0.05`
на портах и поездах (у Grey's свои 0.02–0.04 — не потеря, а спор чисел),
`goods_input_clippers` / `goods_output_merchant_marine` у `pm_anchorage`.
Это не баланс, это выпавшая структура. Восстанавливать.

**Оговорка про счёт.** Класс A считается по **пути** (`state_modifiers.level_scaled.X`),
поэтому в него попадает и случай «Grey даёт то же самое, но в другом под-блоке» —
ровно так вышло с `pm_trade_center` (см. 2.2). Перед тем как переносить строку класса A,
глазами проверить, нет ли того же имени в соседнем под-блоке записи.

**B. Grey просто повторяет ваниль, правка TGR стёрта — 28 строк.**
Чистое восстановление там, где запись целиком в этом классе:

* четыре метода госадминистрации — TGR удваивал бюрократию, Grey вернул ванильные числа:
  `pm_simple_organization` 10→50, `pm_vertical_filing_cabinets` 65→150,
  `pm_horizontal_drawer_cabinets` 50→100, `pm_switch_boards` 100→200;
* `pm_steel_passenger_carriages` 15→30, `pm_wooden_passenger_carriages` 10→20;
* `pm_rail_transport_mine`, `pm_steam_rail_transport` — рабочие и вход транспорта;
* `pm_refrigerated_rail_cars_building_fishing_wharf`,
  `pm_refrigerated_storage_building_fishing_wharf`;
* `pm_trade_center_trade_quantity_normal` / `_high` / `_very_high` —
  `goods_input_merchant_marine_add` и `state_trade_quantity_mult` (0.5→1.0, 1.0→2.0).

**Оговорка, которую нельзя потерять:** строки класса B внутри записи, где есть и класс C,
отдельно не переносятся. У портов `grey_usu` переписал лестницу занятости целиком;
вернуть туда две ванильные строки TGR — значит смешать две лестницы. Решать по записи.
Таких записей шесть: `pm_automated_bakery`, `pm_basic_port`,
`pm_diesel_trains_principle_transport_3`, `pm_flash_freezing_building_fishing_wharf`,
`pm_industrial_port`, `pm_modern_port`. Записей, где класс B встречается **без** класса C
(то есть перенос безопасен), — девять: четыре метода госадминистрации,
`pm_rail_transport_mine`, `pm_steam_rail_transport`, `pm_steel_passenger_carriages`,
`pm_wooden_passenger_carriages`, `pm_refrigerated_rail_cars_building_fishing_wharf`.

**C. Обе стороны отошли от ванили — 40 строк.** Порты (`pm_anchorage`, `pm_basic_port`,
`pm_industrial_port`, `pm_modern_port`), поезда (`pm_early_trains`, `pm_steam_trains`,
`pm_electric_trains`, `pm_diesel_trains` и их `principle_transport_3`), автоматизация
(`pm_automated_bakery`, ограды, охлаждение), занятость торгового центра.
Общая форма: TGR умножал вход/выход и `state_infrastructure_add` (иногда вдвое-втрое),
`grey_usu` перестраивал те же методы под свою железнодорожную и портовую систему.
**Это настоящий спор двух переработок, и решать его надо целиком по подсистемам
(порты / рельсы / охлаждение), а не по строкам.**

Отдельно: `pm_refrigerated_storage_building_*` — TGR перевесил метод с `pasteurization`
на `railways` и сменил текстуру на `rail_transport`. Grey возвращает `pasteurization`.
То есть TGR переносил охлаждение в железнодорожную ветку техов, и этот перенос пропадает.

## 7. Товары, здания, компании, техи, одиночки

| ключ | что происходит | вывод |
| --- | --- | --- |
| `clippers` | оба `REPLACE_OR_CREATE`. `convoy_cost_multiplier` ван 0.15 / TGR 0.25 / Grey 0.05; `traded_quantity` 3.5 / 2 / 7 | спор баланса, замыслы прямо противоположны (TGR — возить клиперы дорого, USU — дёшево). Оставить Grey's, записать причину |
| `fabric`, `wood`, `merchant_marine`, `transportation` | `grey_usu` делает `TRY_INJECT` на три строки (`category = industrial`), тело TGR цело | **не конфликт** |
| `electricity` | оба `REPLACE_OR_CREATE`, ни одного расхождения TGR с ванилью | **не конфликт** |
| `building_trade_center` | см. 2.1 | сперва проверить в игре, снят ли потолок; `ai_value` оставить Grey's. Здание есть и у **E&F** — сцеплено с GR.5 |
| `building_food_industry` | см. 2.5 | вернуть `bg_consumer_goods`; `levels_per_mesh` 5→50 косметика |
| `building_construction_sector` | `required_construction`: TGR `very_low`, `grey_usu` свой `construction_cost_consec` | **это GR.2**, не дублировать файл |
| `bg_trade` | TGR даёт `cash_reserves_max = 500000`, у `grey_usu` поля нет | восстановить |
| `monopoly_charter` | `ai_weight.value`: ван 50 / TGR −1000 / Grey −50. Плюс **GR.10**: `_grey_soft_econ` и `grey_usu` везут файл по одному пути | оба хотят отвадить ИИ; разницу −1000 против −50 решать вместе с GR.10 |
| `company_hbc`, `company_imperial_arsenal`, `company_russian_american_company`, `company_william_cramp` | **Исправлено 27.08.2026 — не конфликт.** Первая версия этой строки утверждала, что `grey_usu` переписывает компании своим телом; на деле `grey_usu` делает `TRY_INJECT:`, добавляя 1-2 записи в `building_types`/`extension_building_types` (`INJECT: в список добавляет, не заменяет` — правило уже проверено на парах E&F/LLWA/VC). Тело TGR остаётся целым, Grey's просто пришивает порт сверху: `hbc` +river_port (порт у TGR уже есть), `imperial_arsenal` +port/+shipyard,river_port (к табачной компании), `russian_american_company` +port,river_port (TGR убирал порт ради шахт Урала — Grey's не «теряет», а тихо возвращает), `william_cramp` +port/+river_port. Файла не нужно ни на одну из четырёх |
| `centralization`, `enclosure`, `stock_exchange`, `urbanization` | обе стороны `INJECT` / `TRY_INJECT` в `modifier`, блок без `value =` | **не конфликт**, инжекты складываются |
| `state_region_pollution_health` | `INJECT` TGR дословно повторяет ваниль; тело `grey_usu` его перекрывает | **не конфликт** (и заодно гасит потенциальное удвоение `state_mortality_mult` у самого TGR) |
| `trade_states` | `ai.accept_score`: ван 25 / TGR 200 / Grey 30. Оба тела полные, ~292–329 строк | спор чисел; **внутри блока Grey's ещё и `grey_diplo` поверх `grey_subject`** — это GR.14 |
| `foreign_investment_rights` | TGR переписал: `contextual_accept_score` (−500 против не-игрока), `inherent_accept_score` −100 вместо +20, `wargoal.execution_priority` 3 вместо 21, масштабирование инфамии по населению. `grey_diplo` возвращает ванильное тело со своей гавайской веткой | крупная потеря; **пересекается с GR.8** (KAI тоже трогает эту статью) |

## 8. Что проверено и признано не конфликтом — 11 ключей

`fabric`, `wood`, `merchant_marine`, `transportation`, `electricity`,
`centralization`, `enclosure`, `stock_exchange`, `urbanization`,
`state_region_pollution_health`, `NPolitics`.

Основание по каждому — в таблицах выше. Ни один не выведен из одного лишь факта
несовпадения имени файла: во всех случаях сверялись тела и префиксы.

## 9. С чем эта пара сцеплена

| задача | общее | как не наступить |
| --- | --- | --- |
| **GR.2** (PSC) | `building_construction_sector` | стройсектор чинится там; из GR.7 туда уходит только `required_construction` |
| **GR.5** (E&F) | 14 `pm_company_headquarter_*`, `building_food_industry` | одна запись — один файл; шапка «нужны оба мода: TGR и E&F» |
| **GR.8** (KAI) | `foreign_investment_rights`, `NAI` | разбирать вместе, как и записано в плане |
| **GR.10** (внутри пачки) | `monopoly_charter` + файл по общему пути | сначала GR.10, потом число `ai_weight` |
| **GR.14** (внутри пачки) | `trade_states` (`grey_diplo` × `grey_subject`) | то же |
| **GR.16** (аддон-LLWA) | десять ж/д методов, `state_market_access_price_impact` | вклад TGR туда уже возвращали в `llwa+tgr done`; здесь его съедает тот же `grey_usu` |
| **GR.18** (аддон-VC) | `company_imperial_arsenal`, `company_russian_american_company`, `company_william_cramp` | три автора на одну компанию; решать один раз на все три задачи |

## 10. Предполагаемый состав компача (черновик, до решений раздела 11)

Один файл — одна тема, все с префиксом пары; имена уточнить при сборке.

1. `common/country_ranks/` — восемь рангов, тело `_grey_soft_pop` + возврат правок TGR (GR.7a);
2. `common/laws/` — четыре `INJECT:` по одной строке (GR.7b), самый дешёвый файл пары;
3. `common/defines/` — четыре define к возврату (раздел 5);
4. `common/production_methods/` владение — 21 запись, **общий с GR.5**, шапка «нужны оба мода»;
5. `common/production_methods/` торговый центр — `pm_trade_center*`, `pm_trade_center_trade_quantity_*`;
6. `common/production_methods/` госадминистрация — четыре записи класса B;
7. `common/production_methods/` рельсы и порты — после решения по разделу 6C;
8. `common/buildings/` — `building_trade_center` (`has_max_level`), `building_food_industry` (`bg_consumer_goods`);
9. `common/building_groups/` — `bg_trade`;
10. `common/treaty_articles/` — `foreign_investment_rights`, **общий с GR.8**;
11. `common/company_types/` — четыре компании, после решения; **общий с GR.18**.

## 11. Что проверить в игре до написания файлов

Одна загрузка закрывает оба вопроса, на которые рассуждением не ответить.

1. **Панель торгового центра** — есть ли строка максимального уровня в ветке с Grey's.
   Ответ решает, нужен ли файл на `building_trade_center` вообще (раздел 2.1).
2. **Число групп методов на торговом центре** — заодно видно, чьё тело выиграло здание
   и не потерялись ли группы E&F (это уже GR.5).

Приём стандартный: «скриншот панели здания — самый дешёвый способ проверить, кто выиграл ключ».

## 12. Что решено (26-27.08.2026)

1. **Заём и ранг страны:** зависимость от ранга убрана — комментируем `country_loan_interest_rate_mult`
   во всех восьми рангах в файле аддона, как задумал TGR со своей системой займов.
2. **`clippers`:** оставлено `grey_usu` (0.05 / 7), файла нет.
3. **`monopoly_charter`:** оставлено Grey's (−50), файла нет — GR.10 закрыт как не конфликт
   (см. правку выше в разделе 7): файлы `_grey_soft_econ` и `grey_usu` побайтово идентичны
   по содержанию (кроме префикса), это намеренная синхронизация автора, а не потеря чартеров.
4. **Четыре компании:** не конфликт (см. правку в разделе 7), файла нет.

## 13. Порты, рельсы, автоматизация, занятость ТЦ — закрыто 27.08.2026: оставляем Grey's

Решался по подсистемам, а не по строкам, с проверкой в игровых файлах, а не на глаз.

* **Порты.** Проверено — LLWA порты вообще не трогает (свои `LLWA_pm_sailing_barges` и т.п.,
  другая система, ни один файл не пересекается по имени с `pm_anchorage`/`basic`/`industrial`/
  `modern_port`). Решается изолированно в GR.7: **оставлено Grey's** (бо́льшая занятость,
  как задумал USU) — согласуется с уже принятыми `clippers` и `monopoly_charter` в этой же паре.
* **Рельсы.** Семь из восьми записей — те же самые, что уже стоят в GR.16 (десять ж/д методов,
  которые тело `grey_usu` съедает поверх восстановленных в `llwa+tgr done`/`llwa+vc done` вкладов
  TGR/VC). Там уже есть прецедент на ровно этот же вопрос: LLWA спорил с TGR за те же PM,
  и решение было — **числа позднего мода (LLWA) оставить, восстановить только отдельную
  добавку TGR** (`state_market_access_price_impact`), редизайн не трогать.
  **Проверено количественно, откуда берётся расхождение в `state_infrastructure_add`:**
  у TGR ровно два источника этого поля во всём моде — порты (5/7.5/10) и рельсы (40…110),
  и рельсы у него единственный по-настоящему крупный. У `grey_usu` источников намного больше:
  рельсы (10-25), порты (5-20), **каналы (по 50 за штуку)**, стройсектор, `urban_other_pms`,
  и **46 речных стейт-трейтов с бонусом 10-40 каждый** в одном только файле трейтов.
  Другими словами: TGR стягивает всю инфраструктуру штата в один канал (рельсы) и поднимает
  его сильно; `grey_usu` размазывает её по многим источникам и держит каждый скромным.
  Взять число TGR для рельсов, не забрав заодно и его отказ от остальных источников, —
  двойной счёт: инфраструктура посыплется откуда угодно. **Оставлено Grey's, файла нет** —
  тот же вывод, что дал прецедент LLWA×TGR, только теперь ещё и подтверждён числами.
  GR.16 своей актуальности не теряет — там остаётся restore именно узкой добавки TGR/VC
  (`state_market_access_price_impact`, `building_job_attractiveness_mult`), не редизайна.
* **Автоматизация/охлаждение и занятость торгового центра.** Расхождения мелкие
  (единицы-десятки, не кратные), решение то же самое: **оставлено Grey's, файла нет.**

Итог: раздел 6C (40 строк «класс C») закрывается без единого файла. Экономика Grey's/USU —
самосогласованная система с распределённой инфраструктурой; переносить отдельные числа TGR
в неё означает ломать баланс, для которого числа TGR не предназначались.

---

**Открытая задача, найденная попутно и к GR.7 не относящаяся:**
`TGR.1` — `TGR_POLITICS_country_ranks.txt` откатывает ранги на старую ваниль (раздел 2.4).
В ветке без Grey's это живая порча текущего мегапака.
