# Аддон к мегапаку: разбор совместимости

Дата разбора: 2026-08-24. Игра 1.13.
Набор: CMF → ETF/Dence UI → TGR → PSC → KAI → E&F → E&F Hotfix → Morgenröte → Tech&Res → PBE → **MegaComPatch**, после него — аддон.

## Итог

Аддон нужен обязательно, и он крупнее, чем выглядело. Из тринадцати модов в `for addon`:

* **шесть** содержательно конфликтуют с пачкой (USU, LLWA + два его компача, grey_food, grey_food_2_ranch, soft_econ, Hail Columbia; частично Gates of Bosphorus и Mandate of Heaven),
* **три** конфликтуют между собой внутри аддона,
* **один** (`_multiline`) не нужен вообще и при включении делает хуже,
* **два** (grey_diplo, grey_subject) почти чистые — как вы и предполагали.

**Вылетов не нашёл.** Товары 111 из 128, id событий не пересекаются ни в одной паре, пропавших `.gui`-виджетов нет. Всё найденное — молчаливые потери: чужой мод продолжает грузиться и просто перестаёт что-то делать, ни строчки в `error.log`. Текущий `error.log` пачки я тоже посмотрел — там штатный спам E&F (`var` / `scope` в `03_economic_scripted_effects`), ничего про загрузку БД.

---

## Допущение о порядке загрузки — прочитать до остального

Все выводы «кто кого перебивает» построены на модели: **порядок модов главный, имя файла — только внутри мода**; для одинаковых относительных путей побеждает более поздний мод. Это то, что записано в вашем промпте («обычное `foo = { }` в моде, загруженном позже, съедает `REPLACE_OR_CREATE:foo` из более раннего»; «порядок файлов *внутри мода* — побайтово по имени»).

Косвенное подтверждение: E&F кладёт `REPLACE:pm_company_headquarter_privately_owned` в `common/production_methods/11_ef_private_infrastructure.txt`, а ваниль определяет этот ключ в `14_companies.txt`. Если бы порядок считался по имени файла через общую виртуальную ФС, E&F делал бы `REPLACE:` несуществующего ключа — то есть ошибку загрузки на каждый из пятнадцати HQ-методов. В `error.log` таких ошибок нет.

**Где это важно.** Есть альтернативная модель (обход общей ФС по имени файла), при которой у трёх модов аддона имена сортируются рано и их правки, наоборот, умирают сами:

| файл | под моделью «порядок модов» | под моделью «имя файла» |
|---|---|---|
| `LLWA_rails.txt` | LLWA перебивает TGR/T&R/мегапак | LLWA грузится сразу после ванили и умирает сам |
| `yMoG_USU_*.txt` | USU перебивает PSC/TGR/E&F | часть правок USU умирает сама |
| `mog_food_industry.txt`, `mog_ranch.txt` | перебивают E&F и T&R | перебивают только E&F, T&R возвращает своё |

**Компач нужен при любой из двух моделей** — разница только в том, чьи правки пропадают. Дешёвая проверка в игре, которая закрывает вопрос за одну загрузку: включить всё, зайти за Британию, открыть железную дорогу и посмотреть вкладку методов. Если у неё есть группа E&F «Market Liquidity» и группа T&R «Transport Infrastructure» — работает модель «имя файла». Если их нет — «порядок модов», и весь список ниже верен как написан.

---

## Состав папки `for addon`

| мод | версия | game | id | зависимости в metadata |
|---|---|---|---|---|
| `gatesofbosphorus` | 4.0.8 | 1.13.* | 3384997867 | CMF 1.* |
| `grey_add_alot_of_things/_grey_soft_econ` | — | — | 3345217364 | — |
| `grey_add_alot_of_things/_multiline` | 1.7.3 | 1.13.* | xyz.1230james.multiline_pms | — |
| `grey_add_alot_of_things/grey_food` | — | — | 3330261506 | — |
| `grey_add_alot_of_things/grey_food_2_ranch` | — | — | 3394847149 | — |
| `grey_add_alot_of_things/grey_usu !!!` | — | — | — | — |
| `grey_add_alot_of_things/llwa !!!` | 2.6.3 | 1.13.* | xyz.1230james.locomotion | — |
| `grey_add_alot_of_things/llwa_morgen compatch` | 1.0.8 | — | xyz…LLWA_morgenrote_compatch | LLWA, Morgenröte |
| `grey_add_alot_of_things/usu_llwa comatch` | — | — | 3387021675 | — |
| `grey_diplo` | — | — | — | — |
| `grey_subject` | — | — | — | — |
| `hailcolumbia` | 8.6-Roosevelt | 1.13.* | *(пусто)* | CMF |
| `mandateofheaven` | 1.4.6.1 | 1.13.* | top.sleepingbed.moh | CMF 1.* |

Заметки по метаданным: у `hailcolumbia` пустой `id` — в `relationships` чужих компачей на него сослаться нельзя. У половины Grey-модов пустые `version` и `supported_game_version` — ориентир только по дате папки, как у E&F.

---

## 1. Критично: USU × PSC и мегапак — строительный сектор

`common/buildings/building_construction_sector`, порядок определений:

```
13_construction.txt                [ваниль]   bare               20L
TGR_TRADE_construction.txt         [TGR]      REPLACE_OR_CREATE  20L
kai_buildings.txt                  [KAI]      INJECT ai_value    14L
zz_PSC_construction.txt            [PSC]      REPLACE            47L
zz_pb_ef_construction_sector.txt   [мегапак]  REPLACE            95L
yMoG_USU_construction.txt          [USU]      REPLACE_OR_CREATE  22L   <-- грузится последним
```

Мегапаковская запись — это ваш трёхсторонний мердж (PSC + PBE + E&F), 95 строк, с `pmg_market_liquidity` и `can_build_private`. USU называет в своём `REPLACE_OR_CREATE` те же под-блоки, включая `production_method_groups`, и оставляет там **только** `pmg_base_building_construction_sector`.

Что теряется: `pmg_market_liquidity` (E&F — выпуск акций стройсектором), `ownership_type`, `can_build_private`, `ai_nationalization_desire` — то есть половина того, ради чего PSC вообще существует. Симптом молчаливый: стройка работает, но частный сектор её не строит и E&F с неё ничего не печатает.

**Это самый дорогой конфликт набора.** Мегапаковский `zz_pb_ef_construction_sector.txt` — файл, который вы собирали дольше всех, и USU сносит его целиком.

## 2. Критично: USU × TGR, E&F, T&R — ещё четыре здания и 92 метода

| ключ | что теряется | кто пострадал |
|---|---|---|
| `building_trade_center` | `pmg_market_liquidity`, `pmg_private_ownership_manufacture_stock` | E&F |
| `building_port` | те же два | E&F |
| `building_urban_center` | `pmg_urban_center_healtcare`, `pmg_recycling_center` | T&R |
| `building_airport` | см. п. 3 | MORG, T&R, мегапак |
| `pm_company_headquarter_*` (15 шт.) | `state_modifiers` от TGR + правки E&F в `building_modifiers` | TGR, E&F |

USU у trade_center даёт `[base, trade_center_port_status, trade_quantity]` — TGR-овские `has_max_level` и `ai_value` он не называет, они выживают, а вот инжект E&F стирается.

Дальше — объём, который в таблицу не влезает: **92 пересечения в `common/production_methods`**, **32 в `common/company_types`** (в том числе `company_Bankenverein` и `company_HandelsBanken` — это те самые банки из хотфикса, и `company_standard_oil` из мегапака), **12 в `common/combat_unit_types`** (все против T&R), **6 в `common/goods`** (против TGR: `electricity`, `transportation`, `clippers`, `fabric`, `wood`, `merchant_marine`), **75 всего против TGR** и **108 против T&R**.

USU — это не «мод, добавляющий производства». Это второй экономический мод поверх ваших четырёх. Компач на пару USU × (TGR+T&R+E&F+PSC) по объёму сравним с любым из восьми, что уже есть в мегапаке. **Здесь стоит остановиться и решить, берём ли мы USU вообще** — это архитектурная развилка, а не деталь.

## 3. Критично: компачи LLWA несут голое тело здания

`llwa_morgen compatch` и `usu_llwa comatch` определяют `building_railway` и `building_airport` **без префикса, полным телом** (176 и 76 строк). Голое определение в более позднем моде съедает всё, что в ключ инжектили раньше.

**building_railway** — в пачке в него инжектят четверо:

| мод | что инжектит |
|---|---|
| E&F | `pmg_market_liquidity`, `pmg_private_ownership_railroad_stock` |
| Morgenröte | `pmg_gaudi_communication` |
| Tech&Res | `pmg_transport_infrastructure_building_railway`, `pmg_data_optimization_light_industry_no_shopkeepers` |
| LLWA | `LLWA_pmg_private_expansion` |

Что остаётся после компачей LLWA:

* `usu_llwa comatch` (грузится последним из двух): `base`, `passenger_trains`, `logistics_services_railway`, `automation`, `gaudi_communication`, `LLWA_private_expansion` — **потеряны обе группы E&F и обе группы T&R**;
* `llwa_morgen compatch` (если usu_llwa не включён): `base`, `passenger_trains`, `gaudi_communication`, `LLWA_private_expansion` — потеряны те же четыре **плюс** ванильные `logistics_services_railway` и `automation`.

**building_airport** — та же картина:

| источник | группы |
|---|---|
| Morgenröte (bare) | `base`, `cargo`, `tourism` |
| Tech&Res (REPLACE_OR_CREATE) | + `fuel_airport`, `data_optimization_light_industry_no_shopkeepers` |
| мегапак (два INJECT) | + `market_liquidity`, `private_ownership_manufacture_stock`, `tourism` |
| `usu_llwa comatch` (bare, побеждает) | `LLWA_air_base`, `LLWA_air_traffic`, `tourism`, `LLWA_private_expansion` |
| `llwa_morgen compatch` (bare) | `LLWA_air_base`, `LLWA_air_traffic`, `LLWA_private_expansion` |

Замена аэропорта на систему LLWA — это замысел мода, спорить не с чем. Но вместе с ней уходят оба инжекта мегапака (акции E&F) и обе группы T&R, и `llwa_morgen` вдобавок уносит `pmg_tourism_airport` самого Morgenröte, ради стыковки с которым он и написан.

Лечится файлом аддона `zzzz_addon_llwa_buildings.txt` с телом, выведенным из победившего сейчас файла компача LLWA плюс недостающие строки. По вашему правилу: тело выводить из того файла, который сейчас побеждает, а не писать заново.

## 4. LLWA × TGR, T&R, мегапак — десять железнодорожных методов

`LLWA_rails.txt` делает `REPLACE:` на `pm_steam_trains`, `pm_electric_trains`, `pm_diesel_trains` и их `_principle_transport_3`-варианты, плюс `pm_early_trains`, `pm_no_passenger_trains`, `pm_steel_passenger_carriages`, `pm_wooden_passenger_carriages`.

Ровно эти же записи `REPLACE:`-ит ваш `zz_tr_kai_tgr_production_methods.txt`. Обе стороны называют одни и те же под-блоки (`building_modifiers`, `state_modifiers`), так что выживает целиком один.

Что в мегапаке есть, а у LLWA нет (на примере `pm_steam_trains`):

```
building_modifiers.workforce_scaled:
    goods_input_steel_add = 1        <- T&R, у LLWA нет
state_modifiers:
    unscaled = { state_market_access_price_impact = 0.05 }   <- TGR, у LLWA нет
```

Остальные числа у LLWA и мегапака совпадают (транспорт 30, инфраструктура 30) — LLWA пришёл к тем же значениям независимо. Поэтому мердж дешёвый: взять мегапаковское тело и добавить то немногое, что LLWA меняет сверху.

Отдельно: у `pm_steel_passenger_carriages` LLWA добавляет под-блок `unlocking_production_methods`, которого нет ни у ванили, ни у TGR. Под-блок, который никто больше не называет, при `REPLACE:` должен пережить чужой `REPLACE:` — но это ровно тот случай, где ваша заметка про «REPLACE патчит по под-блокам» помечена как непроверенная. В спорном месте писать полное тело.

## 5. LLWA подменяет ванильный файл AI-стратегий устаревшей копией

`llwa !!!/common/ai_strategies/03_political_strategies.txt` — **перекрытие ванильного пути**, единственное во всём LLWA. Слова «LLWA» в файле не встречается ни разу: это копия ванильного файла от более старой версии игры, попавшая в мод по недосмотру.

Диф против текущей ванили — 125 строк. Пропадает:

* весь учёт `je_colonize_korea` в весах (два блока),
* ветка `c:FRA` + `ideology_legitimist`,
* блок `AND = { has_technology_researched = egalitarianism … }` в условии реставрации,
* правки весов у landowners/devout.

И вдобавок: KAI правит восемь из этих стратегий (`INJECT:` в семь и `REPLACE:ai_strategy_meiji_restoration`) из файла `kai_political_strategies.txt`. LLWA грузится после KAI и определяет ключи голыми телами — **вся работа KAI по политическим стратегиям стирается**.

Это баг автора LLWA, а не конфликт как таковой. В аддоне лечится дёшево: положить по тому же пути текущую ванильную версию файла и следом `zzz_addon_kai_political_strategies.txt` с копиями `INJECT:`/`REPLACE:` из KAI. Автору LLWA стоит написать — файл в моде лишний целиком.

## 6. grey_food × E&F и T&R

`mog_food_industry.txt`, `REPLACE_OR_CREATE:building_food_industry`, называет `production_method_groups`:

| источник | группы |
|---|---|
| ваниль / TGR | `base`, `canning`, `distillery`, `automation_building_food_industry` |
| E&F (INJECT) | + `market_liquidity`, `private_ownership_manufacture_stock` |
| T&R (INJECT) | + `delivery_building_food_industry`, `data_optimization_light_industry` |
| grey_food (побеждает) | `base`, `canning`, **`preservation`**, `distillery` |

Потеряны обе группы E&F и обе группы T&R; `pmg_automation_building_food_industry` убран автором намеренно (его заменяет `pmg_preservation`).

Плюс шесть пересечений в `common/production_methods` с TGR (`pm_automated_bakery`, четыре `pm_refrigerated_*`, `pm_flash_freezing_*`) и три в `production_method_groups` с T&R.

## 7. grey_food_2_ranch × E&F и T&R

Тот же рисунок, `mog_ranch.txt`:

| источник | группы |
|---|---|
| ваниль | `base`, `sheep_ranch`, `fencing`, `refrigeration` |
| E&F (INJECT) | + `market_liquidity`, `private_ownership_agricultural_stock` |
| T&R (INJECT) | + `breeding_livestock_ranch`, `data_optimization_primary_sector` |
| ranch (побеждает) | `base`, `automation_ranch`, `sheep_ranch`, `dairy_products`, `fencing`, `refrigeration` |

Потеряны те же четыре чужих группы. Дополнительно: `popneed_basic_food` и `popneed_luxury_food` пересекаются с TGR и T&R, `company_basic_food` — с T&R, `enclosure` — с TGR, `pm_electric_fencing` — с обоими.

Оба Grey-мода лечатся одним файлом `zzzz_addon_grey_food_buildings.txt`, который берёт их тело и дописывает четыре группы обратно.

## 8. soft_econ × TGR, E&F и мегапак — defines

Defines сливаются поключево, побеждает последний, аддон последний. Совпадающих ключей 21, из них реально расходятся значения:

| define | ваниль | TGR | E&F | мегапак | soft_econ (победит) |
|---|---|---|---|---|---|
| `NEconomy.PRICE_RANGE` | 0.75 | 0.85 | 0.99 | **0.85** | **0.9** |
| `NEconomy.BUY_SELL_DIFF_AT_MAX_FACTOR` | 2 | **1.65** | — | — | **3** |
| `NEconomy.COMPANY_MINIMUM_LEVELS_PER_HQ` | 5 | **1** | — | — | **5** |
| `NEconomy.AUTO_DOWNSIZE_BUILDING_MIN_UNUSED_TRADE_CAPACITY` | 20 | **100** | — | — | **20** |
| `NEconomy.AUTO_DOWNSIZE_BUILDING_MONTHS_TO_WAIT` | 6 | 1 | — | — | 2 |
| `NEconomy.BUILDING_PROFIT_TARGET_TO_LOWER_WAGES` | 0.15 | 0.05 | — | — | 0.1999 |
| `NEconomy.BUILDING_PROFIT_TARGET_TO_RAISE_WAGES` | 0.25 | 0.25 | — | — | 0.2111 |
| `NEconomy.BUILDING_PROFIT_TARGET_TO_HIRE_EMPLOYEES` | 0.25 | 0.25 | — | — | 0.2 |
| `NEconomy.GOODS_SHORTAGE_PENALTY_MAX` | 0.5 | — | **0.9** | — | **0.7** |
| `NAI.TRADE_CENTER_MINIMUM_GDP_UNRECOGNIZED_MULT` | 2.0 | 2.0 | — | — | 1 |
| `NWar.DEVASTATION_INCREASE_RATE` | 0.1 | — | — | — | 0.05 |

Остальные десять совпадают значение в значение — не конфликт.

Жирным — то, где надо принимать решение, а не мерджить. Три штуки болезненные:

* **`PRICE_RANGE`.** У вас в `ef_tgr_defines.txt` записана явная развилка с обоснованием: держим 0.85, потому что вся торговая переработка TGR настроена на узкий коридор. soft_econ ставит 0.9 — не 0.99, но и не ваш выбор. Решать вам; файл аддона должен либо повторить 0.85, либо переписать шапку `ef_tgr_defines.txt`, потому что иначе комментарий будет врать.
* **`BUY_SELL_DIFF_AT_MAX_FACTOR`.** TGR сузил до 1.65, soft_econ расширяет до 3 — почти вдвое против ванили и вдвое против TGR. Вместе с `PRICE_RANGE = 0.9` это заметно более дикий рынок, чем тот, под который TGR настраивал торговые события ИИ.
* **`COMPANY_MINIMUM_LEVELS_PER_HQ`.** TGR ставит 1, soft_econ возвращает ванильные 5. У вас на компаниях висит и E&F (98 банковских типов), и TGR — это тот самый параметр, который у вас уже вылезал.

Плюс `REPLACE_OR_CREATE:monopoly_charter` (TGR тоже правит, 16 строк против 34 у soft_econ) и `TRY_REPLACE:pm_trade_center` / `pm_trade_center_principle_external_trade_2` — оба против TGR.

## 9. Hail Columbia × TGR и T&R

Два независимых конфликта.

**Группы интересов.** Hail Columbia кладёт `common/interest_groups/00_landowners.txt` (788 строк) и `00_rural_folk.txt` (560) — перекрытие ванильных путей голыми телами. TGR правит те же две группы через `REPLACE_OR_CREATE` в `TGR_POLITICS_landowners.txt` / `_rural_folk.txt` (772 и 563 строки). Hail грузится позже — **все правки TGR у землевладельцев и сельских жителей пропадают**: идеологии, трейты, `on_enable`, `priority_cultures`. Инжект Mandate of Heaven в rural_folk аддитивен и выживает.

**Законы рабства.** `usfp_law_slavery_overrides.txt` делает `REPLACE:` на `law_slave_trade`, `law_debt_slavery`, `law_legacy_slavery`, `law_colonial_slavery`. T&R делает `REPLACE:` на те же законы из `ztr_un_updated_slavery.txt` (128 строк против 119 у Hail). Hail позже — переработка рабства у T&R пропадает.

Остальные законы Hail трогает через `INJECT:` (`is_visible`, `on_activate`) — это аддитивно и безопасно. `ideology_jacksonian_democrat` — `REPLACE_OR_CREATE`, но TGR инжектит туда под-блоки, которые Hail не называет, так что они должны выжить.

Мелочь: Hail перекрывает `common/decisions/manifest_destiny.txt`, который правит и TGR; и две DNA-записи Morgenröte (`ecchi_usa_chrysler`, `ecchi_usa_lindbergh`) — косметика.

## 10. Gates of the Bosphorus × Morgenröte и TGR

* **18 файлов `common/dna_data/mr_*.txt`** — GoB везёт свои копии файлов Morgenröte, под теми же именами. Он грузится позже и заменяет их. Скорее всего намеренная совместимость (файлы названы по схеме MR), но редакция может отставать от текущей Morgenröte 2.8.3e — стоит передиффить.
* `common/history/countries/tur - ottoman empire.txt` — перекрывают и TGR, и GoB. GoB позже, история османов от TGR пропадает.
* Ещё 10 перекрытий ванильной истории Балкан и Египта, `events/sick_man_events.txt`, `events/romania_events.txt`, `common/decisions/romania_decision.txt`, `montenegro_decision.txt` — с пачкой не пересекаются, но это полная замена ванильных файлов: при следующем патче игры их надо передиффить.
* `revive_olympic_games_decision` — общий ключ с Morgenröte.

## 11. Mandate of Heaven × TGR и Morgenröte

* `common/history/countries/chi - china.txt` — перекрывают TGR и MoH; MoH позже, история Китая от TGR пропадает.
* `common/achievement_groups.txt` — общий с Morgenröte, MoH побеждает; косметика.
* `gui/frontend/frontend_main.gui` и `map_data/province_terrains.txt` + `map_data/state_regions/` — MoH это ещё и картографический мод. Из пачки карту не трогает никто, конфликта нет, но это стоит знать: любой будущий мод на карту с MoH встанет плохо.
* Законы и группы интересов — везде `INJECT:`, аддитивно, безопасно.

---

## Конфликты внутри самого аддона

Вы писали, что между собой они не конфликтуют. Четыре места, где это не так:

1. **USU ↔ soft_econ — одинаковое имя файла.** Оба везут `common/company_charter_types/yMoG_company_charter_types.txt`, содержимое разное. Это перекрытие по пути: тот, кто грузится позже, полностью отменяет файл другого. Один из двух модов молча потеряет свои правки чартеров.
2. **USU ↔ Gates of Bosphorus.** Оба везут `common/history/countries/mon - montenegro.txt` (94 и 102 строки против 93 ванильных). Позже загруженный побеждает целиком.
3. **`llwa_morgen compatch` ↔ `usu_llwa comatch`.** Оба голым телом определяют `building_railway` и `building_airport`, и наборы групп у них разные. Вместе их включать нельзя — надо выбрать один и объяснить выбор в README аддона, либо сделать один общий.
4. **grey_diplo: `Grey_DIS_is_active` без префикса.** CMF объявляет этот триггер в `0_community_mod_triggers.txt`, grey_diplo переопределяет его в `zz_MoG_DIS_mod_compatibility_triggers.txt` **голым ключом**. Для `scripted_triggers` простой повтор ключа не переопределяет — нужен `REPLACE_OR_CREATE:`, как это правильно сделано во всех остальных Grey-модах (USU, SEA, FIR, RPR, SIS) и у MoH, GoB, Hail. То есть флаг «grey_diplo включён» с большой вероятностью остаётся `no`, и любая чужая интеграция с этим модом молча не срабатывает. Баг автора; в аддоне чинится тремя строками.

---

## `_multiline` — не включать

`_multiline` (Multi-line Production Methods Framework 1.7.3) везёт шесть файлов `gui/00_MPM_*.gui` и `MPM_custom_types.gui`. **Ровно эти же шесть файлов уже входят в CMF 1.63.0**, и версия в CMF новее:

| файл | сравнение |
|---|---|
| `00_MPM_building_details_panel.gui` | побайтово одинаковы |
| `00_MPM_map_list_panel.gui` | побайтово одинаковы |
| `MPM_custom_types.gui` | побайтово одинаковы |
| `00_MPM_building_browser_panel.gui` | у CMF `EXPAND_TOOLTIP_BUILDING_TYPE` вместо `EXPAND` |
| `00_MPM_goods_state_panel.gui` | у CMF добавлена поддержка `IsPiracyLoss` |
| `00_MPM_production_methods.gui` | у CMF **на 94 строки больше**: блоки `section_header_interactable`, `expand_onclick`, `expand_showmore_visible`, `expanded_list_visible`, `blockoverride "building_progressbars"` |

Отдельный `_multiline` грузится после CMF, перекрывает эти пути и **откатывает CMF на старую редакцию**. Всё, что цепляется к CMF-овским `block`-хукам, после этого молча перестаёт работать: `blockoverride` на блок, которого в старом файле нет, ничего не делает и ничего не пишет в лог.

Второе, более неприятное. Эти шесть файлов переопределяют восемь ванильных виджетов, и семь из восьми правит ещё и E&F:

| виджет | ваниль | E&F | хотфикс | MPM |
|---|---|---|---|---|
| `buildings_production_method_item` | 234L | 265L | — | 283L |
| `old_buildings_production_method_item` | 236L | 176L | — | 258L |
| `condensed_building_information` | 202L | 233L | 233L | 227L |
| `condensed_building_information_pms` | 120L | 151L | **151L, своя редакция** | 120L |
| `building_browser_building_item` | 272L | 272L (изменён) | — | 294L |
| `building_browser_building_type_item` | 319L | 350L | — | 279L |
| `goods_state_panel_input_output_item` | 304L | 335L | — | 313L |
| `construction_interaction_item_full` | 541L | = ванили | — | 619L |

Сейчас CMF стоит **первым** в порядке загрузки, поэтому в споре с E&F выигрывает E&F, и панели остаются E&F-овскими. Если поставить `_multiline` после E&F — выиграет MPM, и пять панелей E&F (детали здания, методы производства, браузер зданий, товары штата, список строек) откатятся на ванильные с косметикой MPM. В том числе панель, в которой E&F одной строкой `visible` прячет группу «какую валюту печатает банк».

Вылета не будет: E&F сам определяет эти же типы дважды (в `gui/building_details_panel.gui` и в `gui/ef_dev_and_custom_windows/maj/Essential/…`), и мод работает — значит движок дубли типов терпит.

**Вывод:** `_multiline` из аддона убрать. Многострочные методы у вас и так есть — через CMF, в более свежей редакции. Если захочется, чтобы MPM реально работал поверх E&F, это отдельная большая задача: мердж семи виджетов E&F с изменениями MPM, и делать её надо один раз, в файле, который грузится после обоих.

---

## Что проверено и оказалось не конфликтом

* **Товары: 111 из 128.** Считал по виртуальной ФС на всей цепочке, включая аддон: ваниль 53 + T&R 35 + E&F-с-хотфиксом 8 + Morgenröte 5 + PSC 4 + **USU 3** + **LLWA 2** + мегапак 1. Запас 17. Ни один другой мод аддона товаров не добавляет.
* **id событий.** Ни одного пересечения — ни между модами аддона, ни с пачкой. `namespace` пересекаются, но это не конфликт.
* **`.gui`-виджеты.** Кроме истории с MPM выше — ни один мод аддона не выпиливает виджет, который нужен другому. У `llwa !!!` в `gui/` только `LLWA_texticons.gui`, у Gates of Bosphorus один файл, у MoH — `frontend_main.gui`.
* **`common/on_actions`.** Пересечений много (`on_monthly_pulse_country` встречается у семи модов сразу), но категория аддитивная — это не конфликт, только нагрузка.
* **`BUILDINGS` в `history/buildings` и `GLOBAL` в `history/global`.** Тоже аддитивны.
* **`modifier_type_definitions`.** У ranch, LLWA и USU пересекаются `goods_output_grain_mult`, `goods_output_meat_mult`, `goods_input_services_add`, `goods_input_luxury_clothes_add`, `goods_input_luxury_furniture_add`. Расхождение там только по `decimals` / `color` / `percent` — это отображение, пин-файл не нужен.
* **Локализация.** Аддон грузится последним, а в локализации побеждает первый объявивший ключ, поэтому «конфликт» здесь всегда в пользу пачки. Пересечений мало и все безобидные: USU 20 ключей из 290 (в основном описания модификаторов, которые уже дали MORG и T&R), Hail 21 из 3304, MoH 14 из 2050 (названия партий, они же в CMF), GoB 7 из 8613, LLWA 2, у остальных 0. По каждому языку отдельно — дублей внутри одной языковой папки нет.
* **Триггеры `*_is_active` из CMF.** CMF заранее объявляет флаги для двух десятков известных модов (`Grey_USU_is_active`, `Grey_SEA_is_active`, `is_usfp_active`, `mandate_o_h_is_active`, `grefm_is_active` и т.д.), а мод переопределяет свой через `REPLACE_OR_CREATE:`. Штатная схема, не конфликт — кроме grey_diplo, см. выше.
* **Ванильные фолбэки `community_framework_is_active = { always = no }`** у Hail и MoH — их перекрывает `zz_com_detection_trigger.txt` самого CMF (`REPLACE_OR_CREATE`, `always = yes`), имя сортируется позже. Работает.
* **grey_diplo и grey_subject** — почти чистые, как вы и думали. У diplo: `trade_states` с TGR, `foreign_investment_rights` с TGR и KAI, `goods_transfer` с T&R — три записи в `common/treaty_articles` и `diplomatic_actions`, их надо посмотреть глазами, но масштаб несопоставим с остальным. У subject: `force_become_subject` с PBE, `trade_states` с TGR, `liberty_desire_weekly_change` с T&R, `NPolitics` с TGR, остальное — аддитивные `on_actions` и `scripted_effects` из набора CMF/ETF (`add_com_topbar_element`, `fix_variable_error`), которые все моды объявляют одинаково.

---

## Предлагаемый состав аддона

Если брать всё, аддон получается из шести файлов-мерджей плюс два перекрытия по пути:

| файл аддона | что делает |
|---|---|
| `zzzz_addon_construction_sector.txt` | возвращает мегапаковское тело стройсектора поверх USU |
| `zzzz_addon_usu_buildings.txt` | trade_center, port, urban_center: чужие группы обратно в тело USU |
| `zzzz_addon_llwa_buildings.txt` | railway + airport: группы E&F/T&R/MORG обратно в тело компача LLWA |
| `zzzz_addon_rails_pm.txt` | десять железнодорожных методов: мегапаковское тело + правки LLWA |
| `zzzz_addon_grey_food_buildings.txt` | food_industry + livestock_ranch: четыре чужие группы обратно |
| `zzzz_addon_defines.txt` | решение по одиннадцати расходящимся defines soft_econ |
| `zzzz_addon_usfp_igs.txt` | landowners + rural_folk: правки TGR поверх тела Hail Columbia |
| `common/ai_strategies/03_political_strategies.txt` | текущая ваниль вместо устаревшей копии LLWA |
| `zzz_addon_kai_political_strategies.txt` | копии `INJECT:`/`REPLACE:` из KAI обратно поверх неё |
| `zzz_addon_grey_dis_trigger.txt` | `REPLACE_OR_CREATE:Grey_DIS_is_active` |

Плюс решения, которые надо принять до кода, а не в процессе:

1. **Берём ли USU.** Он один даёт больше конфликтов, чем все остальные вместе. Если да — это работа масштаба ещё одного компача в мегапак, включая законы рабства, боевые юниты и 32 типа компаний.
2. **Какой из двух компачей LLWA включаем.** Вместе нельзя.
3. **PRICE_RANGE и BUY_SELL_DIFF_AT_MAX_FACTOR** — чей мир: TGR или soft_econ.
4. **Законы рабства** — Hail Columbia или Tech&Res.
5. **`_multiline`** — не включать (см. выше).

---

## Открытые вопросы

* **Модель порядка загрузки.** Описана в начале. Влияет на то, чья сторона проигрывает в пп. 1–7; на сам факт «компач нужен» не влияет. Закрывается одной загрузкой игры.
* **`REPLACE:` и под-блоки.** У `pm_steel_passenger_carriages` LLWA добавляет под-блок, которого нет ни у кого другого. Переживёт ли он чужой `REPLACE:` — зависит от того, патчит ли `REPLACE:` по под-блокам или заменяет запись целиком. В вашем промпте это помечено как неразрешённое противоречие (шапка `zzzz_ef_tr_fix_gold_minting.txt` утверждает обратное основному правилу). Пока не разрешено — писать полное тело.
* **Свежесть копий Morgenröte внутри Gates of Bosphorus.** 18 DNA-файлов надо передиффить против текущей Morgenröte 2.8.3e; если автор GoB собирал их против более старой версии, часть портретов молча откатится.
* **`hailcolumbia` без `id` в metadata.** Сослаться на него в `relationships` компача нельзя. Стоит либо взять id из мастерской, либо просто не ссылаться.
* Синхронизация в игровую папку в этой сессии не делалась — примонтированы `Projects` и `Documents/Paradox Interactive/Victoria 3`, так что `mod/` доступен; но пока нечего синхронизировать, аддон ещё не написан.
