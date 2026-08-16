### Общая сводка: что меняет **Economic and Financial (E&F)** (фокус на `common/`)

**Актуальная версия в репозитории**: коммит `E&F 4.07.2026` (август 2026), игра **1.13.\***.  
Steam ID: `3143591632`. Метadata в локальной копии почти пустой — ориентироваться на дату коммита и содержимое файлов.

**E&F** — крупный «оверлей» на экономику: полноценная **денежно‑финансовая подсистема**, вшитая в ванильные здания/рынки через массовые патчи.

---

### Финансы, валюта и законы (самая важная часть)
- **Новые группы законов**:
  - `lawgroup_monetary_system` — монетарный стандарт (fiat / silver / gold / bimetallism / gold exchange и т.д.).
  - `lawgroup_monetary_policy` — монетарная политика (revaluation / devaluation).
  - `lawgroup_currency_type` — тип/конкретная валюта страны.
  - `lawgroup_bimetalism_ratio` — соотношение биметаллизма.
- **Институт**: `institution_economic_central_bank`.
- **Скриптовая платформа** в `script_values/`, `scripted_effects/`, `on_actions/`:
  - денежная масса и ликвидность,
  - базовая ставка и кредитный рейтинг (AAA…D),
  - кризисы (currency crisis / bankruptcy / instability).

---

### Goods: валюта и финансовые инструменты как товары рынка
- `common/goods/ef_00_goods.txt`:
  - **INJECT** ванильного `gold`,
  - `silver`,
  - финансовые товары: `bond`, отраслевые stocks, `mutual_funds`, `war_bond` и др.,
  - десятки currency-goods (dinar/mark/peso/…).
- `common/pop_needs/00_ef_pop_needs.txt` — pop need **`currency`**.

---

### Здания и производство
Ключевые PM-группы E&F:
- **`pmg_market_liquidity`** — привязка к закону валюты.
- **`pmg_private_ownership_*_stock`** — акционирование отраслей.

E&F **массово INJECT-патчит ванильные здания** (`ef_01_industry.txt`, `ef_02_agro.txt`, `ef_03_mines.txt`, `ef_04_plantations.txt`, `ef_06_urban_center.txt`, `ef_09_misc_resource.txt`, `ef_11_private_infrastructure.txt`).

Собственные здания:
- **`building_bank`** — центробанк.
- **`building_financial_centre`** (+ региональные варианты).
- **`building_ef_private_construction`** — приватное строительство.
- **`building_silver_mine`** — серебряная шахта; **важно для компачей**: группа **`bg_silver_mining`**, не `bg_mining`.

Группы зданий E&F (точки для компачей с другими модами):
- `bg_bank`, `bg_financial_centre`, `bg_national_stockpile`, `bg_ef_private_construction`, `bg_silver_mining`.

---

### Технологии
- `common/technology/technologies/ef_technology.txt` — много **`REPLACE:`** ванильных tech (`banking`, `currency_standards`, `central_banking`, `corporate_charters`, `joint_stock_companies`, …).
- Главная зона конфликтов с модами, которые тоже правят те же технологии.

---

### Инфляция (изменилось в 1.13-обновлении)
В `common/script_values/00_economic_scripted_value.txt` инфляция разбита на **несколько корзин**:
- `inflation_on_consumer_goods`
- `inflation_on_energy` *(новая)*
- `inflation_on_raw_material`
- `inflation_on_manufactured_goods` *(новая)*
- `inflation_on_military_equipment` *(новая)*

Для компачей с модами, добавляющими goods: нужно понимать, **в какую корзину** попадает товар, а не только дописывать в consumer/raw.

---

### Прочее
- **Stockpile**: PM и переменные (часть файлов упакована в `.zip`).
- **Companies**: расширенная система (`company_types`, `01_economic_company_value.txt`).
- **Treaty articles**, **events/JE/GUI**, **on_actions** — регулярные пульсы пересчёта финансов.
- **GUI**: крупный рефакторинг панелей (budget, construction, companies, custom windows).

---

### Для компачей: где ждать конфликты
- **`common/technology/technologies/*`** (REPLACE ванилы).
- **`common/goods/*`**, **`common/pop_needs/*`**.
- **`common/buildings/*`** (INJECT в ваниль).
- **`common/production_methods*`**, **`production_method_groups*`**.
- **`common/buy_packages/*`** — полное переопределение `wealth_*` (конфликт с Morgenrote).
- **`common/script_values/*`**, **`scripted_effects/*`**, **`on_actions/*`**, **`static_modifiers/*`**.
- **`common/building_groups/*`** — особенно E&F-специфичные группы для исключений в чужих триггерах (Tesla и т.п.).
