# LLWA — новый контент против всего набора. Разбор 26.08.2026

Повод — вопрос по собранному аддону-LLWA: «моргенрота файлов не вижу», затем «LLWA + E&F+hotfix = noneed — сомнительно», «по компаниям надо посмотреть», «у PBE вроде есть баффы на жд», «по остальным модам тоже надо глянуть».

Разбор охватывает **весь набор**, а не только три пары аддона.

---

## 0. Класс проблемы, которого машинная матрица не видит

`pair_matrix.py` сравнивает **ключи, которые определяют оба мода**. Здание, которое определяет только LLWA, не может попасть в пересечение **никогда** — не потому, что конфликта нет, а потому, что матрица устроена так.

Отсюда следствие, которое надо записать в правила: **`noneed`, выведенный из матрицы, закрывает ровно один класс — «оба трогают одну запись». Он ничего не говорит про класс «один мод добавил контент, которого нет в чужих списках».**

Второй слепой поход того же рода: `tools/blocks.json` определяет блок `LLWA` как `["../../vic3_mods_out/llwa"]` — **только голый мод**. Ни `_llwa/llwa+morg out`, ни `_greys/usu_llwa out outdate` в матрицу не входят. Всё, что делают чужие компачи на стадии LLWA, для матрицы невидимо.

Ниже — четыре находки, разложенные по классам «реальная потеря / чужой замысел / вкусовщина».

---

## 1. LLWA × E&F — `noneed` неверен. **Реальная потеря.**

### Что добавляет LLWA

Семь новых зданий (не шесть — `LLWA_building_roadway` стоит первым ключом файла под BOM и не ловится наивным грепом по `^`):

| здание | building_group | ownership_type | PM-группы |
| --- | --- | --- | --- |
| `LLWA_building_roadway` | `bg_private_infrastructure` | `self` | `LLWA_pmg_road_base`, `LLWA_pmg_road_traffic`, `LLWA_pmg_private_expansion` |
| `LLWA_building_waterway` | `bg_private_infrastructure` | `self` | `LLWA_pmg_water_base`, `LLWA_pmg_water_traffic`, `LLWA_pmg_private_expansion` |
| `LLWA_building_riverway` | `bg_private_infrastructure` | `self` | то же |
| `LLWA_building_airway` | `bg_private_infrastructure` | `self` | `LLWA_pmg_air_base`, `LLWA_pmg_air_traffic`, `LLWA_pmg_private_expansion` |
| `llwa_building_freight_depot` | `bg_private_infrastructure` | `self` | `LLWA_pmg_shipping_base`, `LLWA_pmg_mapi_comms`, `LLWA_pmg_private_expansion` |
| `llwa_building_exchange` | `bg_private_infrastructure` | `self` | `LLWA_pmg_exchange_base`, `LLWA_pmg_mapi_comms`, `LLWA_pmg_private_expansion` |
| `LLWA_building_logistics_hub` | `LLWA_bg_logihub` | `no_ownership` | `LLWA_pmg_logihub_base` |

**Шесть из семи приватно владеемы** (`ownership_type = self`). `logistics_hub` — `no_ownership`, из экономики E&F выпадает по замыслу автора, его трогать нечего.

### Куда E&F цепляет свою экономику

Два места, **оба — рукописные перечисления по имени здания**, ни одно не работает по `building_group`:

1. **`common/buildings/ef_*.txt`** — `INJECT:` с `pmg_market_liquidity` и `pmg_private_ownership_*_stock`. По частной инфраструктуре покрыто ровно пять зданий: `building_port`, `building_railway`, `building_trade_center`, `building_manor_house`, `building_financial_district`.
2. **`common/scripted_effects/01_financial_scripted_effects.txt` → `private_ownership_production_stocks`** — 1669 строк, **49 зданий**, на каждое рукописная пара `if`-ов (доля > 0.5 → включить stock-PM, ≤ 0.5 → выключить). Разбивка:
   * `agricultural_stock` — 20 зданий
   * `manufacture_stock` — 21 здание (в т.ч. `building_port`, `building_trade_center`)
   * `mining_stock` — 7 зданий
   * **`railroad_stock` — ровно одно здание: `building_railway`**

Здание без PM-группы не производит ликвидность и не выпускает акции. Здание с группой, но без записи в `private_ownership_production_stocks`, навсегда залипает на «No Stock».

### Что получилось

**Ни одно из семи зданий LLWA не встречается ни в одном из двух мест.** Более того — проверено индексом по всем модам набора: **ни один мод, кроме самого LLWA, вообще ни разу не упоминает ни одно из этих семи имён.**

`LLWA_pmg_private_expansion` — не замена: это переключатель `LLWA_pm_yes_private_expansion` / `LLWA_pm_no_private_expansion`, то есть «расширяется частник или государство», к акциям и ликвидности E&F отношения не имеет.

Итог: у игрока с E&F вся транспортная сеть LLWA — дороги, каналы, речные пути, воздушные линии, грузовые депо, биржи — **вне финансовой системы мода**. Ни ликвидности, ни акций, ни дивидендов, ни приватизации. Молча, без строчки в логе.

### Прецедент: ровно эта же задача уже решена для Morgenröte

`_ef/ef+morg done` (в мегапаке) делает для 62 новых зданий Morgenröte именно то, чего нет у LLWA. Четыре файла:

| файл | строк | что делает |
| --- | --- | --- |
| `common/buildings/zz_ef_mr_buildings_inject.txt` | 391 | `TRY_INJECT:` `pmg_market_liquidity` во все 62; stock-группы — тем семи, что реально владеемы |
| `common/scripted_effects/zz_ef_mr_private_ownership_effects.txt` | 257 | свой `mr_private_ownership_production_stocks` — та же пара `if`-ов, что у E&F |
| `common/on_actions/zz_ef_mr_on_actions.txt` | 17 | аддитивный хук в `on_yearly_pulse_country`, **ничего не переопределяет** |
| `common/history/global/zz_ef_mr_stocks_init.txt` | 17 | тот же вызов на старте игры — иначе первый год всё висит на «No Stock» |

Локализация **не нужна**: `zz_ef_tgr_private_ownership_stock_l_*.yml` там же именует четыре PMG-группы, грузится раньше LLWA, работает на всех.

### Объём для LLWA

Та же форма, минус два файла:

* **инфляция не нужна** — LLWA везёт два товара (`llwa_market_conn`, `llwa_logi_conn`), оба `tradeable = no` + `fixed_price = yes`, в корзины инфляции такие не попадают;
* **`_lvl` script values не нужны** — прецедент для Morgenröte без них обошёлся;
* потолок 128 не двигается: два товара LLWA **уже посчитаны** в текущих 74/128.

Остаётся четыре файла на шесть зданий — меньше, чем у Morgenröte на 62.

### Одно решение за тобой

Какой тип акций у «путевых» зданий. E&F раскладывает так: `building_railway` → `railroad_stock`; `building_port`, `building_trade_center` → `manufacture_stock`. Дороги/каналы/речные пути/воздушные линии — транспорт, но не рельсы. Варианты: (а) всем шести `railroad_stock` — «транспорт есть транспорт», группа сейчас обслуживает ровно одно здание; (б) путевым — `railroad_stock`, депо и бирже — `manufacture_stock` (они ближе к торговым узлам); (в) всем `manufacture_stock`. Из файлов это не выводится — это выбор дизайна, поэтому не решал сам.

---

## 2. Компании — **вкусовщина, не потеря.** Но место для работы есть.

### LLWA свои здания компаниями закрыл

Четыре собственные компании в `common/company_types/LLWA_companies.txt`:

| компания | building_types | extension_building_types |
| --- | --- | --- |
| `LLWA_company_turnpike` | roadway, waterway, riverway | `building_railway` |
| `LLWA_company_ship_line` | waterway, riverway, `building_port` | `building_railway`, airway |
| `LLWA_company_railroad` | `building_railway` | roadway, waterway, riverway |
| `LLWA_company_airline` | airway | `building_port` |

То есть roadway / waterway / riverway / airway покрыты. **`freight_depot`, `exchange`, `logistics_hub` не входят ни в одну компанию нигде.** Для `logistics_hub` это правильно (`no_ownership`). Депо и биржа — `has_max_level = yes`, потолочные утилитарные постройки по штуке на штат; похоже на осознанный выбор автора, не на забытьё. Внутри LLWA они прописаны в `ai_strategies`, `history/buildings`, `scripted_effects` и `modifier_type_definitions` — то есть не заброшены.

### Чего нет ни у кого

Компаний, у которых в `building_types` есть `building_railway` / `building_port` / `building_trade_center`, по набору **больше двухсот**:

| мод | таких компаний | заметки |
| --- | --- | --- |
| Grey's (USU) | ~70 | почти весь исторический железнодорожный корпус |
| E&F | ~100 | все банки везут `building_railway` + `building_trade_center` |
| ваниль | 27 | Orient Express, GWR, Mantetsu, Suez, Panama… |
| VC | 23 | |
| TGR | 20 | |
| HC / MoH / Morgenröte / CMF | 1 + 1 + 1 + 0 | |

**Ни одна из них не знает ни одного здания LLWA.** Ничего при этом не теряется — просто исторические железнодорожные компании строят ванильные рельсы и не замечают сети LLWA.

Это и есть «кому раздать». Естественные кандидаты — `extension_building_types` (не `building_types`, чтобы не менять чужой профиль компании):

* железнодорожным (Orient Express, GWR, Prussian State Railways, Mantetsu, Deutsche Reichsbahn, ~70 USU-шных) → `LLWA_building_roadway`;
* судоходным и портовым (White Star Line, AP Møller, Sudamericana de Vapores, USU-шные верфи) → `LLWA_building_waterway`, `LLWA_building_riverway`;
* каналам (Suez, Panama) → `LLWA_building_waterway`;
* банкам E&F (у них уже `building_railway` + `building_trade_center`) → скорее `llwa_building_exchange`, если решим давать биржу компаниям вообще.

**Но:** править `extension_building_types` чужой компании — это `INJECT:` в чужую запись, то есть новая пара «аддон-LLWA × <мод>» на каждый мод. Плюс USU-шный корпус — территория GR.9, туда лезть отсюда нельзя. Предлагаю не хвататься за всё, а решить объём отдельно (см. раздел 5).

---

## 3. PBE — `noneed` подтверждается, но по другой причине. **Потери нет.**

Проверено содержательно, не по ключам. Вся инфраструктурная поверхность PBE — два места:

* `common/power_bloc_principles/vokaes_power_bloc_principles.txt` — `state_infrastructure_mult = 0.1` в `principle_internal_trade_2` и `_3`;
* `common/static_modifiers/vokaes_power_bloc_modifiers.txt` — `state_market_access_price_impact = 1` в `vokaes_mapi_per_leader_subject_modifier`.

Оба — **общие модификаторы штата, а не списки зданий.** `state_infrastructure_mult` множит всю инфраструктуру штата, включая ту, что произвели здания LLWA. То есть баффы PBE на LLWA **работают сами**, чинить нечего — это синергия, а не потеря.

Файл PBE лежит по своему пути (`vokaes_*`), ванильный `00_power_bloc_principles.txt` не перекрывает — файлового конфликта тоже нет.

Отдельно стоит записать наблюдение: `state_market_access_price_impact` трогают оба — PBE (за подчинённых в блоке) и LLWA (`LLWA_pmg_mapi_comms` у депо и биржи). Это разные источники одного стата, складываются, потери нет.

Остальные упоминания `building_*` в PBE — **имена модификаторов** (`building_arms_industry_throughput_add` и т.п.), а не ссылки на типы зданий; списков зданий, куда LLWA должен был попасть, у PBE нет вообще.

---

## 4. `ai_strategy_default` — `noneed` подтверждается на более твёрдых основаниях

Цепочка по этому ключу оказалась длиннее, чем записано в плане:

1. ваниль `common/ai_strategies/00_default_strategy.txt`;
2. **KAI везёт файл по тому же самому пути** — файловое перекрытие, ванильный файл выпадает целиком, тело KAI побеждает;
3. MoH `moh_default_strategy.txt` — `REPLACE:ai_strategy_default` полным телом;
4. LLWA `LLWA_default_strategy.txt` — `INJECT:ai_strategy_default = { subsidies = { … 6 зданий … } }`.

LLWA грузится последним, а его записи внутри `subsidies` — **именованные** (по имени здания). По правилу из раздела правил («`INJECT:` сливает под-блоки в запись, именованные записи переопределяют одноимённые, остальные выживают») инжект LLWA кладёт свои шесть приоритетов, ничего не стирая. Требование «LLWA после MoH» в плане (строка 46) — и есть то, что это держит.

KAI × MoH на том же ключе — **уже закрыто** в `_HC+GoB+MoH/hc+kai done/common/ai_strategies/zz_hctr_ai_strategy_default.txt`. Ложной тревоги нет.

---

## 5. Что уже сделано по ходу разбора

**`_llwa/llwa+morg+ef done`** — компач на дыру, с которой начался разговор (генератор `tools/regen_llwa_morg_ef.py`, 1 файл, 2 записи, самопроверка `0 problem(s)`, `--check` сходится).

`_llwa/llwa+morg out` (компач автора LLWA, id `xyz.1230james.LLWA_morgenrote_compatch` 1.0.8) переопределяет **голыми полными телами** `building_railway` и `building_airport`, сводя руками вклад LLWA и Morgenröte. E&F в его `metadata.json` не заявлен вовсе — и обе пары групп E&F молча выпадают:

* `building_railway` — `pmg_market_liquidity` + `pmg_private_ownership_railroad_stock` (собственный `INJECT:` E&F);
* `building_airport` — `pmg_market_liquidity` + `pmg_private_ownership_manufacture_stock` (закрытая пара E&F × Morgenröte, в мегапаке).

Это ровно та находка, что уже записана в правилах по итогам игры: «в панели железной дороги остаются три группы вместо девяти — ни `pmg_market_liquidity` от E&F…». Формулировка там говорит «LLWA **и его компачи**» — то есть про этот случай, а не про голый LLWA.

Восстановлено поверх тела компача автора; его собственное сведение LLWA и Morgenröte перенесено без изменений.

**Не чинится намеренно:** тот же `building_airport` у `llwa+morg out` выбрасывает и **собственную** авиацию Morgenröte (`pmg_base_building_airport`, `pmg_cargo_airport`, `pmg_tourism_airport`) в пользу воздушных групп LLWA. Это не съеденный `INJECT:`, а выбор между двумя взаимоисключающими редизайнами одного здания, который автор компача уже сделал. «Не чинить чужой замысел, не разобравшись».

Заодно проверено и снято подозрение: `LLWA_building_airway = {}` (пустышка) в том же файле выглядит как поломка `LLWA_company_airline`, у которой это единственное здание. Но автор компача переопределяет и саму компанию — `common/company_types/zz_LLWA_companies.txt` переводит её на `building_airport`. Сделано аккуратно.

---

## 6. Что предлагаю решить

**Первое — LLWA × E&F.** Дыра реальная, прецедент есть, объём понятен (4 файла на 6 зданий). Нужен твой выбор типа акций (вариант а/б/в из раздела 1). Статус `noneed` в LLWA.4 в любом случае надо снимать и переписывать — он выведен из матрицы, а матрица этот класс не видит.

**Второе — компании.** Тут развилка по объёму:
* *ничего* — LLWA свои здания своими компаниями закрыл, набор играбелен;
* *минимум* — раздать `LLWA_building_roadway` / `waterway` / `riverway` в `extension_building_types` ванильным железнодорожным и судоходным компаниям (один файл, `INJECT:`, ванильные записи — чужих модов не трогаем);
* *широко* — то же по TGR / VC / E&F / HC / MoH, это отдельная пара на каждый мод;
* USU-шные ~70 компаний в любом случае мимо — это GR.9.

**Третье — правила.** Два вывода стоит дописать: (1) `noneed` из матрицы закрывает только класс «оба трогают одну запись», для нового контента нужна отдельная проверка «кто ещё перечисляет здания по имени»; (2) блок в `blocks.json`, определённый одним голым модом, не измеряет чужие компачи, которые грузятся на той же стадии.

**Четвёртое — аддон.** `llwa+morg+ef done` в `build_addon_llwa.py` пока не включён (сборка стоит на трёх парах). Включать сейчас или дождаться решения по E&F и собрать один раз — тоже вопрос к тебе.

---

## Приложение: как проверялось

* Индекс всех токенов `building_*` по 13 модам набора (`~/idx/scan.py`, кэш JSON) — из него список «кто вообще перечисляет здания по имени».
* Отсев имён модификаторов от настоящих типов зданий: собран список реально определённых зданий по всем `common/buildings/` набора — **236 штук**, дальше сверка только по нему.
* `common/company_types` разобраны парсером по `building_types = { … }` во всех модах.
* Все цитаты из файлов читались вживую, не по памяти.
