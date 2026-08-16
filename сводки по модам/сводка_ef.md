### Общая сводка: что меняет **Economic and Financial (E&F)** (фокус на `common/`)

**Версия в репозитории**: коммит `E&F 4.07.2026`, игра **1.13.\***.
Steam ID: `3143591632`. `.metadata/metadata.json` **пустой** (`version` и `supported_game_version` — пустые строки), ориентироваться только на дату коммита.
**Сверено с файлами: 16.08.2026.**

**E&F** — крупный «оверлей» на экономику: полноценная **денежно‑финансовая подсистема**, вшитая в ванильные здания/рынки через массовые INJECT-патчи. Сам мод почти ничего не переопределяет целиком — единственный крупный `REPLACE:` это технологии (см. ниже).

---

### Финансы, валюта и законы (самая важная часть)

**Группы законов** (`common/law_groups/01_ef_laws.txt`) — 4 штуки:

| Группа | Законов | Содержимое |
|---|---|---|
| `lawgroup_monetary_system` | 7 | `law_no_monetary_system`, `law_fiat_standard`, `law_silver_standard`, `law_bimetallism_standard`, `law_gold_standard`, `law_gold_exchange_standard`, `law_external_exchange_standard` |
| `lawgroup_currency_type` | **96** | конкретная валюта страны |
| `lawgroup_monetary_policy` | 4 | revaluation / devaluation |
| `lawgroup_bimetalism_ratio` | 4 | соотношение биметаллизма |

**Институт**: `institution_economic_central_bank` (единственный, `common/institutions/00_ef_institutions.txt`).

**Скриптовая платформа** в `script_values/`, `scripted_effects/`, `on_actions/`:
- денежная масса и ликвидность,
- базовая ставка и кредитный рейтинг,
- кризисы (currency crisis / bankruptcy / instability),
- `treaty_articles/`: supply agreement, Latin Monetary Union, Scandinavian Monetary Union,
- `amendments/`, `prestige_goods/` (mexican_silver, russian_gold, usa_oil и биржевые престиж-товары).

---

### Goods: валюта и финансовые инструменты как товары рынка

`common/goods/ef_00_goods.txt` — единственный файл с товарами:

- **`INJECT:gold`** — единственный патч ванильного товара;
- новые товары верхнего уровня: `silver`, `bond`, `manufacture_stock`, `agricultural_stock`, `mining_stock`, `railroad_stock`, `mutual_funds`, `local_currency`;
- **65 валютных товаров** с суффиксом `_c` (`dinar_c`, `pound_sterling_c`, `spe_ruble_c`, …) внутри блока `#begin_tag_1`.

> `war_bond` в актуальной версии **нет** — не путать со старыми описаниями мода.

`common/pop_needs/` — **две** новые потребности: `popneed_currency` и `popneed_financial_products`.

`common/buy_packages/00_ef_buy_packages.txt` — **`INJECT:wealth_1` … `INJECT:wealth_99`**, то есть аддитивно. Другой мод с `TRY_INJECT` в те же `wealth_*` (например Morgenröte) конфликта **не создаёт**, обе потребности применяются.

---

### Здания и производство

**PM-группы E&F** (18 штук, `common/production_method_groups/`):

- **`pmg_market_liquidity`** — привязка к закону валюты; PM добавляют `goods_input_<валюта>_c_add` через `workforce_scaled`. Это ядро спроса на деньги.
- **`pmg_private_ownership_{manufacture,agricultural,mining,railroad}_stock`** — акционирование отраслей.
- `pmg_{manufacture,agricultural,mining,railroad,bond}_..._exchange`, `pmg_stock_exchange`, `pmg_currency_type`, `pmg_subject_currency_type`, `pmg_monetary_policy`, `pmg_minting_type`, `pmg_*_building_silver_mine`.

**INJECT в ваниль** — **48** зданий (`ef_01_industry`, `ef_02_agro`, `ef_03_mines`, `ef_04_plantations`, `ef_06_urban_center`, `ef_09_misc_resource`, `ef_11_private_infrastructure`, `ef_14_private_construction`). 47 из них получают `pmg_market_liquidity`; `building_financial_district` патчится только блоком `investment_scores`.

> Важно для компачей: E&F ставит liquidity **только в производящие/рыночные здания**. Монументы, университеты, art academy, government administration, казармы он **не трогает**.

**Собственные здания:**

- **`building_bank`** — центробанк (`bg_bank`);
- **`building_financial_centre`** + **41** региональный вариант (`building_financial_centre_gbr`, `_usa`, `_rus`, …) — `bg_financial_centre`;
- **`building_ef_private_construction`** — приватное строительство (`bg_ef_private_construction`);
- **`building_silver_mine`** — `bg_silver_mining`.

**Группы зданий** (`common/building_groups/00_ef_building_groups.txt`) — 5 штук:

| Группа | `parent_group` |
|---|---|
| `bg_bank` | **нет** |
| `bg_financial_centre` | **нет** |
| `bg_national_stockpile` | **нет** |
| `bg_ef_private_construction` | **нет** |
| `bg_silver_mining` | **`bg_mining`** |

> Это ключ к двум вещам в компачах:
> 1. Первые четыре группы **не наследуются** ни от чего, поэтому чужие исключения вида `NOR = { is_building_group = bg_government … }` их **не ловят** — надо перечислять явно.
> 2. `bg_silver_mining` — **потомок `bg_mining`**, а `is_building_group` в Vic3 проверяет всю цепочку родителей. Значит любой чужой триггер на `bg_mining` **уже включает** серебряную шахту, патч не нужен.

---

### National stockpile — частично не загружается

`common/production_methods/17_ef_national_stockpile.zip` и `common/production_method_groups/17_ef_national_stockpile.zip` лежат **в архивах**, а Vic3 содержимое `.zip` внутри мода не читает. Здания с группой `bg_national_stockpile` в `common/buildings/` **нет** — группа определена, но пуста. Скрипты (`01_stockpile_scripted_effects.txt`, `00_stockpile_scripted_value.txt`, `has_modifier = has_national_stockpile`) при этом на месте.

Практический вывод для компачей: исключения по `bg_national_stockpile` писать можно (на будущее), но проверить их в игре сейчас нельзя.

Так же зазипованы: `99_ai_strategies.zip`, `99_ai_buy_sell_currency_effect.zip`, `events/old.zip`.

---

### Технологии

`common/technology/technologies/ef_technology.txt` — единственный файл, 19 ключей:

- **`REPLACE:`** 10 ванильных: `banking`, `currency_standards`, `central_banking`, `mutual_funds`, `corporate_charters`, `investment_banks`, `international_exchange_standards`, `joint_stock_companies`, `postal_savings`, `modern_financial_instruments`;
- 9 собственных: `debt_currency_exchange_regime`, `gold_exchange_standard`, `stockpiling_goods`, `national_stockpile`, `metalique_standard`, `financial_center`, `monetary_policy_tools`, `private_liquidity_provision`, `advanced_interbank_refinancing`.

Зона конфликтов — только моды, которые сами трогают эти 10 ванильных техов. **Morgenröte к ним не относится** (пересечение множеств пустое).

---

### Инфляция — 5 корзин

`common/script_values/00_economic_scripted_value.txt`, все пять по одной схеме `add{market{mg:X{add=market_goods_pricier multiply=market_goods_buy_orders}}} divide{...}`:

| Значение | Товары |
|---|---|
| `inflation_on_consumer_goods` | grain, fish, fabric, clothes, furniture, paper, services, transportation, porcelain, meat, fruit, wine, tea, tobacco, opium, automobiles, telephones, radios, luxury_clothes, luxury_furniture, fine_art |
| `inflation_on_energy` | wood, electricity, coal, oil (+hardwood только в делителе) |
| `inflation_on_raw_material` | silk, dye, sulfur, iron, lead, rubber (+hardwood только в делителе) |
| `inflation_on_manufactured_goods` | clippers, steamers, engines, steel, glass, fertilizer, tools, explosives |
| `inflation_on_military_equipment` | ammunition, small_arms, artillery, tanks, aeroplanes, manowars, ironclads |

У каждой есть спутники `*_market_value` и `*_market_value_abs`.

Для компачей с модами, добавляющими goods: определить корзину по назначению товара, а не по `category` в определении good.

---

### On_actions

`common/on_actions/00_ef_on_action.txt` цепляется к: `on_monthly_pulse_country`, `on_half_yearly_pulse_country`, `on_yearly_pulse_country`, `on_five_year_pulse_country`, `on_decade_pulse_country`, `on_game_started_after_lobby`, `on_production_method_changed`, `on_battle_ended`.

Важная деталь для компачей: **`financial_center_ef_on_yearly_pulse_country` вызывается под условием `has_modifier = has_financial_center`**. Всё, что в него дописывают, работает только в странах с финцентром. Если нужен безусловный хук — вешать свой `on_action` (они складываются аддитивно), а не переопределять этот эффект.

`private_ownership_production_stocks` (1670 строк, `01_financial_scripted_effects.txt:30400`) вызывается из трёх мест: yearly pulse через финцентр, `ef_on_production_method_changed` и history на старте игры. Покрывает **49** ванильных/E&F зданий (включая `building_silver_mine`); зданий чужих модов там нет.

---

### Прочее

- **Companies**: `common/company_types/00_ef_companies.txt` — исторические банки (Barclays, Amsterdamsche Bank, Banco de Londres y México…) + `company_private_construction` + «basic mining» компании.
- **GUI**: крупный рефакторинг панелей (budget, construction, companies, custom windows) — требует topbar-фреймворк (ETF или Dence UI).
- **Локализация**: 11 языков. Имена `pm_*_stock` есть, **а вот ключей `pmg_private_ownership_*` нет** — в loc лежат несовпадающие `pmg_mining_stock`, `pmg_agricultural_stock`, `pmg_railroad_stock`. То есть сами PM-группы в игре показываются сырым ключом, пока их не подпишет компач.

---

### Для компачей: где ждать конфликты

- **`common/technology/technologies/*`** — 10 `REPLACE:` ванильных техов.
- **`common/buildings/*`** — 47 `INJECT:` (аддитивно, конфликт только с чужим `REPLACE:` того же здания).
- **`common/buy_packages/*`** — `INJECT:`, с чужими `TRY_INJECT:` **не конфликтует**.
- **`common/script_values/*`** — инфляционные корзины (их обычно и переопределяет компач).
- **`common/scripted_effects/*`**, **`on_actions/*`** — пульсы; вешаться add-on'ом, не override.
- **`common/building_groups/*`** — 4 группы без родителя нужно явно перечислять в чужих исключениях; `bg_silver_mining` наоборот наследуется от `bg_mining`.
- **`common/modifier_type_definitions/*`** — дубли `goods_output_grain_mult`, `goods_output_wood_mult` с другими модами; низкий риск.
