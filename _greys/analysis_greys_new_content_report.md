# Grey's — новый контент и невидимые для матрицы пары. Разбор 26.08.2026

Повод — перед сборкой аддона-Grey's перепроверить обзор тем же взглядом, что дал находки
LLWA.6-8: `pair_matrix.py` меряет только пересечение ключей, которые определяют **оба** мода,
и меряет только голые моды из `tools/blocks.json`.

Все цитаты читались вживую. Метод — тот же, что в `_llwa/analysis_llwa_new_content_report.md`.

---

## 0. Три слепых пятна, а не одно

1. **Новый контент.** Здание/товар/закон, который определяет только Grey's, не может попасть
   в пересечение никогда. Для LLWA это дало LLWA.6 и LLWA.8.
2. **Чужие компачи вне блока.** Блок `Grey's` в `blocks.json` — восемь голых модов.
   `_greys/usu_llwa out outdate` в матрицу не входит (это GR.9, уже знаем).
3. **НОВОЕ и самое дорогое: матрица не знает про уже собранные мегапак и аддоны.**
   `blocks.json` содержит только исходные моды. Grey's грузится **последним во всей цепочке**,
   то есть поверх мегапака, аддона-VC, аддона-HC и аддона-LLWA. Ни одна из этих четырёх пар
   не измерялась ни разу.

Прогон по тем же правилам, что и матрица (аддитивные категории отброшены):

```
Grey's × мегапак no t&r   13 ключей   (5 зданий, 3 компании, 4 метода стройки, NEconomy)
Grey's × аддон-VC          9 ключей   (4 компании, 5 popneed)
Grey's × аддон-HC          0 ключей
Grey's × аддон-LLWA       41 ключ     (2 здания, 29 компаний, 10 ж/д методов)
```

Аддон-LLWA закрыт вчера — и Grey's, грузясь после него, съедает часть только что сделанной работы.
Подробности — раздел 3.

---

## 1. Новый контент Grey's. Инвентарь

Определено только модами Grey's, ни одним другим модом набора (включая ваниль, CMF/ETF и все компачи):

| категория | шт. | что |
| --- | --- | --- |
| `common/buildings` | **5** | `building_usu_railway_line`, `building_river_port`, `ppp_building_power_grid`, `usu_building_hydro_power_plant`, `usu_building_public_green` — все `grey_usu`, все `ownership_type = self` |
| `common/goods` | 3 | `usu_train_paths`, `usu_logistics`, `ppp_hv_power` (уже посчитаны в потолке 74/128) |
| `common/building_groups` | 7 | `bg_usu_rail_infrastructure`, `bg_usu_railway_line`, `usu_bg_port_infrastructure`, `usu_bg_river_port_infrastructure`, `usu_bg_power_grid`, `usu_bg_hydro_power`, `usu_bg_public_greens` |
| `common/company_types` | **114** | 113 `grey_usu` + `company_somali_food_chain` (`grey_food_2_ranch`) |
| `common/production_methods` | 265 | `grey_usu` 200+, `grey_food`/`grey_food_2_ranch`, `pm_default_building_*` у `_grey_soft_pop` |
| `common/production_method_groups` | 28 | |
| `common/state_traits` | 19 | 16 портовых + 3 `state_trait_hydro_potential_*` |
| `common/diplomatic_actions` | 22 | 21 `grey_subject` + `break_truce` (`grey_diplo`) |
| `common/laws` | 1 | `law_forced_labour` (`grey_usu`) — см. раздел 5 |
| `common/pop_types` | 2 | `druids`, `mages` — **ложная тревога**, оба `TRY_REPLACE:` (в наборе нет мода, который их определяет, значит не создаются) |

**Проверка «кто ещё упоминает эти имена»:** пять новых зданий и три новых товара не встречаются
**ни в одном** моде набора, кроме самого `grey_usu` — сверено грепом по `common/` всех тринадцати модов,
мегапака и трёх аддонов. Единственное исключение — `usu_logistics` два раза в `usu_llwa out outdate`
(компач автора, GR.9).

Новые трейты USU назначаются штатам через `common/history/global/zMoG_hydro_traits_global.txt`,
а не через `map_data/state_regions` — **поэтому голые тела 16 файлов `state_regions` от VC их не гасят.**
Это снимает одно подозрение по GR.1 заранее.

---

## 2. USU переносит железную дорогу в новое здание. **Реальная потеря, класс LLWA.6**

`~zzzzMoG_USU_railways.txt`, комментарий автора в первой строке:

```
REPLACE_OR_CREATE:building_railway = {	# Now the Railway Station - re-using this gets around AI subsidy problems
```

То есть в наборе с USU:

* `building_railway` — **вокзал** (`bg_usu_rail_infrastructure`, PMG `pmg_base_building_rail_terminal`, `pmg_logistics_services_railway`);
* `building_usu_railway_line` — **собственно железная дорога** (`bg_usu_railway_line`, PMG `pmg_base_building_railway`, `pmg_passenger_trains`, `pmg_automation_building_railway`).

Дальше — ровно механизм LLWA.6, но злее. E&F цепляет экономику **рукописным списком по имени здания**
(`common/buildings/ef_*.txt` — `INJECT:` групп; `private_ownership_production_stocks` в
`01_financial_scripted_effects.txt` — 49 зданий, `railroad_stock` ровно на одно: `building_railway`).

Что происходит:

* тело USU на `building_railway` **не содержит** `pmg_market_liquidity` и `pmg_private_ownership_railroad_stock` —
  оба инжекта E&F съедены (это уже числится в GR.5);
* `building_usu_railway_line` — новое имя, **E&F про него не знает вообще**, и не узнает: список рукописный;
* итог: акции железных дорог E&F висят на вокзале, у которого больше нет stock-группы, а настоящая
  железная дорога вне финансовой системы E&F целиком.

**То же самое для четырёх остальных новых зданий** (`building_river_port`, `ppp_building_power_grid`,
`usu_building_hydro_power_plant`, `usu_building_public_green`) — все `ownership_type = self`,
ни одного нет ни в `ef_*.txt`, ни в `private_ownership_production_stocks`.

Прецедент и форма компача — те же, что уже дважды применены: `_ef/ef+morg done` (62 здания Morgenröte)
и `_llwa/llwa+ef done` (6 зданий LLWA). Четыре файла: инжект групп в здания, свой
`*_private_ownership_production_stocks`, аддитивный хук в `on_yearly_pulse_country`,
инициализация из `history/global`.

**Решение за пользователем — тип акций** (из файлов не выводится):
`building_usu_railway_line` → `railroad_stock` очевиден; `building_river_port` → `manufacture_stock`
по аналогии с `building_port`; электростанции (`ppp_building_power_grid`,
`usu_building_hydro_power_plant`) — у E&F `building_power_plant` числится в `manufacture_stock`;
`usu_building_public_green` — парк, `ownership_type = self`, но приватные акции на городской парк
могут быть не нужны вовсе.

---

## 3. Grey's съедает уже собранные аддон-LLWA и мегапак. **Реальная потеря, пары не существовало**

### 3a. Здания: чьи PMG теряются под телами Grey's

Механическая сверка: для каждого здания, которое Grey's определяет замещающим префиксом,
собраны PMG, которые вносили моды **раньше по цепочке**, и вычтены из тела Grey's.

| здание | тело | потеряно | чьё |
| --- | --- | --- | --- |
| `building_railway` | `g_usu` `REPLACE_OR_CREATE` | `pmg_market_liquidity`, `pmg_private_ownership_railroad_stock` | E&F |
| | | `pmg_gaudi_communication` | **Morgenröte** |
| | | `LLWA_pmg_private_expansion` | LLWA |
| | | `pmg_base_building_railway`, `pmg_passenger_trains` | аддон-LLWA (перенесены в `building_usu_railway_line`) |
| `building_airport` | `g_usu` `TRY_REPLACE` (`zMoG_USU_MR_airports.txt`) | `pmg_market_liquidity`, `pmg_private_ownership_manufacture_stock` | E&F × MR из **мегапака** |
| | | `LLWA_pmg_air_base`, `LLWA_pmg_air_traffic`, `LLWA_pmg_private_expansion` | аддон-LLWA / `llwa+morg out` |
| `building_food_industry` | `g_food` `REPLACE_OR_CREATE` | `pmg_market_liquidity`, `pmg_private_ownership_manufacture_stock` | E&F |
| | | `pmg_automation_building_food_industry` | **TGR** |
| `building_trade_center` | `g_usu` `REPLACE_OR_CREATE` | `pmg_market_liquidity`, `pmg_private_ownership_manufacture_stock` | E&F |
| `building_livestock_ranch` | `g_ranch` `REPLACE_OR_CREATE` | `pmg_market_liquidity`, `pmg_private_ownership_agricultural_stock` | E&F |
| `building_power_plant` | `g_usu` `REPLACE` | `pmg_market_liquidity`, `pmg_private_ownership_manufacture_stock` | E&F |
| `building_port` | `g_usu` `REPLACE_OR_CREATE` | `pmg_market_liquidity`, `pmg_private_ownership_manufacture_stock` | E&F |
| `building_construction_sector` | `g_usu` `REPLACE_OR_CREATE` | `pmg_market_liquidity` | **мегапак** |
| `building_government_administration` | `g_usu` `REPLACE_OR_CREATE` | `pmg_panum_hospital` | **Morgenröte** |
| `building_dubois_national_park` | `g_usu` `TRY_REPLACE` (`zMoG_USU_MR_nat_park.txt`) | `pmg_market_liquidity` | **мегапак** |

Шесть зданий из GR.5 подтверждаются. **Новое, чего в плане нет:** `pmg_gaudi_communication` (MR)
на рельсах, `pmg_automation_building_food_industry` (TGR) на пищевой, `pmg_panum_hospital` (MR)
на администрации, `building_airport` и `building_dubois_national_park` против мегапака.

### 3b. Компании: 14 записей, где USU отменяет вчерашнюю работу

Аддон-LLWA (`__addon/addon llwa/common/company_types/zz_llwa_companies_extensions.txt`) — чистые
`INJECT:` в `extension_building_types` 142 компаний. USU трогает 48 из общих с кем-то компаний;
из них **33 через `TRY_INJECT:` (безопасно, складывается)**, а **14 через `TRY_REPLACE:` полным телом**
(`yMoG_USU_companies_rail_overwrite.txt`, `yMoG_USU_panama_suez.txt`). USU грузится позже — инжект аддона пропадает:

| компания | что теряется |
| --- | --- |
| `company_cfr`, `company_cordoba_railway`, `company_egyptian_rail`, `company_great_indian_railway`, `company_gwr`, `company_imperial_ethiopian_railways`, `company_iranian_state_railway`, `company_mantetsu`, `company_orient_express`, `company_prussian_state_railways`, `company_sao_paulo_railway`, `company_tashkent_railroad` | `LLWA_building_roadway` |
| `company_panama_company`, `company_suez_company` | `LLWA_building_waterway`, `LLWA_building_riverway` |

Лечится дёшево: аддон-Grey's переиздаёт те же 14 `INJECT:` поверх тел USU. Тела USU уже содержат
`building_usu_railway_line` — их замысел не трогаем.

### 3c. Десять железнодорожных методов

`pm_early_trains`, `pm_steam_trains`(+ptc3), `pm_electric_trains`(+ptc3), `pm_diesel_trains`(+ptc3),
`pm_no_passenger_trains`, `pm_steel_passenger_carriages`, `pm_wooden_passenger_carriages` —
их определяют и аддон-LLWA (`llwa+tgr done`, `llwa+vc done`: восстановленный
`unscaled = { state_market_access_price_impact = 0.05 }` от TGR и `building_job_attractiveness_mult = 2` от VC),
и USU. USU позже → восстановленное вчера съедается.

Это GR.9, но масштаб теперь другой: чинить надо не «USU против LLWA», а «USU против аддона-LLWA»,
то есть с уже сведёнными вкладами TGR и VC.

---

## 4. Компании: 114 новых у USU, раздача — вкусовщина

USU свои новые здания компаниями закрыл сам и щедро: **163 записи компаний USU** называют новые здания
(`building_usu_railway_line`, `building_river_port`, электростанции). Это противоположность LLWA,
который своих зданий чужим компаниям не раздал.

Обратное направление: **ни одна компания вне Grey's** (ваниль, TGR, VC, E&F, HC, MoH, Morgenröte, LLWA,
аддоны) не знает ни одного нового здания USU. Потери тут нет — исторические компании строят
`building_railway`, который в наборе с USU всё ещё существует (как вокзал). Это раздача, а не починка,
и решать её объём стоит отдельно, как решали для LLWA.8.

---

## 5. Мелочи того же класса, которых нет в плане

* **`law_forced_labour`** — `grey_usu/common/laws/000_USU_laws+_compat.txt` объявляет **голым ключом**
  чужой закон (из мода Laws+, которого в наборе нет) телом-заглушкой `can_enact = { 0 = 1 }`,
  `is_visible = { 0 = 1 }`. Без префикса — значит запись создаётся, **закон без `group`**.
  Того же класса, что GR.11/GR.13; надо проверить в логе игры, не сыплет ли ошибкой.
* **GR.13 недосчитал вдвое.** `com_law_compat_spa_triggers.txt` объявляет **12** ключей,
  а не шесть: шесть `com_law_*_trigger` (с телом `NOT = { has_variable = com_hide_law_* }`)
  **и** шесть `com_law_*_alternative_trigger = { always = no }`. Проверено: в нашем наборе эти
  ключи объявляет только CMF, так что вывод «безвредно» остаётся — но цифру в плане поправить.
* **`druids` / `mages`** — не новые pop_types: `TRY_REPLACE:`, срабатывают только при наличии
  чужого мода. В инвентаре «нового» это ложная тревога, в план не идут.
* **`blocks.json`: `load_order` содержит два несуществующих пути** —
  `grey_add_alot_of_things/llwa_morgen compatch` и `grey_add_alot_of_things/usu_llwa comatch`.
  Реально компачи лежат в `_llwa/llwa+morg out` и `_greys/usu_llwa out outdate`.
  `vfs_order.py` их молча пропускает — любой прогон по цепочке считался без них.
* **`usu_llwa out outdate` покрывает не всё.** 11 ключей: `building_railway`, `building_airport`,
  `LLWA_building_roadway`, `LLWA_building_waterway`, `LLWA_building_airway`, `pmg_gaudi_communication`,
  `pmg_tourism_airport`, `pm_gaudi_no_communication`, `pm_luxury_requisitions`, `pm_travel_agencies`,
  `LLWA_active`. **`LLWA_building_riverway` в нём нет вовсе**, и все тела — голые, без префиксов.
  `metadata.json`: `version` и `supported_game_version` пустые.
* **USU везёт собственный компач к Morgenröte** — `zMoG_USU_MR_airports.txt`, `_nat_park.txt`,
  `_synthetics.txt`, `zMoG_USU_MR_company_overwrites.txt`, `_company_updates.txt`,
  `zzzMoG_USU_MR_pop_needs.txt`, `mMoG_USU_MR_*_pms.txt`. Часть пары GR.6 автор уже сделал —
  разбирать GR.6 надо с этого, а не с нуля.

---

## 6. Что предлагаю сделать с планом

**Снять формулировки, опирающиеся только на матрицу.** У Grey's нет ни одного `noneed`, так что
переворачивать статусы не приходится — но в GR.5/GR.6/GR.9 надо дописать то, чего матрица не видела.

**Добавить четыре задачи** (нумерация продолжает существующие):

* **GR.15 × E&F, новый контент** — пять новых зданий USU вне акций и ликвидности E&F, плюс перенос
  железной дороги в `building_usu_railway_line`. Прецеденты `_ef/ef+morg done` и `_llwa/llwa+ef done`.
  Нужно решение по типу акций.
* **GR.16 × аддон-LLWA** — 41 общий ключ. 14 компаний с `TRY_REPLACE`, десять ж/д методов,
  `building_railway` и `building_airport`. Пары не существовало, потому что матрица не знает аддонов.
* **GR.17 × мегапак** — `building_airport`, `building_construction_sector`,
  `building_dubois_national_park`, `pm_*_buildings` стройки, три компании, `NEconomy`.
  Частично уже внутри GR.2/GR.5, но проверялось против голого E&F, а не против сведённого мегапака.
* **GR.18 × аддон-VC** — 9 ключей: четыре компании и пять `popneed_*`.
  Самый мелкий, но проверить надо.

**Поправить существующие:**

* **GR.5** — дописать `pmg_automation_building_food_industry` (TGR) на `building_food_industry`;
  отметить, что шесть зданий проверены против голого E&F, а `building_airport` и
  `building_dubois_national_park` — против мегапака (GR.17).
* **GR.6** — начинать с того, что USU уже везёт свой компач к Morgenröte (список файлов выше);
  дописать `pmg_gaudi_communication` на `building_railway` и `pmg_panum_hospital` на
  `building_government_administration`.
* **GR.9** — расширить: чинить надо против **аддона-LLWA**, а не голого LLWA;
  `LLWA_building_riverway` в чужом компаче отсутствует.
* **GR.13** — 12 ключей вместо шести.
* **GR.1** — снять подозрение по трейтам: новые трейты USU назначаются из `history/global`,
  голые `state_regions` VC их не гасят. Остаётся вопрос про 60 общих **определений** трейтов.
* **Внутри блока** — добавить `law_forced_labour` (голая заглушка чужого закона без `group`).

**Правила** — к уже записанному по итогам LLWA выводу добавить третий:
блок в `blocks.json` меряется только против других **блоков**, но не против уже собранных
мегапака и аддонов; для блока, который грузится последним, это и есть главный слепой участок.

---

## Приложение: как проверялось

* Инвентарь ключей `common/**` по 28 источникам (13 модов набора, ваниль, CMF/ETF, оба чужих
  компача LLWA, мегапак `no t&r`, три аддона, восемь модов Grey's) — `_tmp_analysis/greys/`.
* Парсер `common/buildings` по всем источникам: `production_method_groups`, `building_group`,
  `ownership_type`, префикс, файл — вычитание PMG по порядку цепочки.
* Парсер `common/company_types` по всем источникам: `building_types`, `extension_building_types`,
  префикс — 401 компания.
* Греп по именам новых зданий и товаров Grey's по `common/` каждого источника отдельно.
* Порядок цепочки взят из `blocks.json` → `load_order` (с поправкой на два битых пути).
