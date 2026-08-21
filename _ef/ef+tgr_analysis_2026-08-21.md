# E&F + TGR — ревизия компача, 21.08.2026

## Что сверялось

| Мод | Версия / коммит | metadata | Примечание |
|---|---|---|---|
| E&F | `E&F 4.07.2026` | пустой (`version`/`supported_game_version` = "") | сводка сверена 16.08.2026 |
| TheGreatRevision | `TGR 1.3.10 12.08.2026 update` | `2.0`, `1.13.10` | содержит модуль Loans целиком |
| TGR_Loans (отдельный подмод) | `2.0`, `1.13.11` | — | файлы **побайтово равны** одноимённым в основном TGR |
| компач `ef+tgr done` | metadata `1.12.3`, `supported_game_version: 1.12.*` | — | контент датирован 10–23.01.2026 |

Компач не обновлялся ни после июльского E&F, ни после августовского TGR. Отчёт
`conflicts_tgr_vs_ef_report.md` внутри папки — от 23.01.2026, устарел.

Свежий прогон `scan_conflicts.py`: 148 общих ключей, 29 общих категорий,
0 общих loc-ключей, 0 общих id событий.

---

## Главный вывод: `REPLACE:` работает **по под-блокам**, а не по записи целиком

Это меняет половину выводов январского разбора и стоит записать в общие правила.

Доказательство прямо в E&F: все 14 `REPLACE:pm_company_headquarter_*` в
`common/production_methods/11_ef_private_infrastructure.txt` содержат **только**
`building_modifiers`. Если бы `REPLACE:` заменял запись целиком, у E&F в соло
пропали бы `texture`, `is_hidden_when_unavailable`, `unlocking_company_categories`,
`disallowing_laws`, `unlocking_laws`, `unlocking_principles` — то есть PM «рабочий
кооператив» был бы доступен без соответствующего закона, а иконки исчезли бы.
Этого не происходит.

Значит: `REPLACE:key = { X = {...} }` заменяет **только** под-блок `X`;
всё, что мод не перечислил, остаётся от предыдущего слоя (ваниль + моды выше по
порядку загрузки). `INJECT:` отличается тем, что под-блок не заменяется, а
до-мерджится.

Практическое следствие: **конфликт есть только там, где оба мода перечислили
один и тот же под-блок.**

---

## Пофайловый вердикт

### 1. `common/production_methods/ef_tgr_company_hq_pm_compat.txt` (505 строк) — **удалить**

TGR: `REPLACE_OR_CREATE:pm_company_headquarter_*` с полным определением, включая
`state_modifiers`.
E&F: `REPLACE:` тех же ключей, но **только** `building_modifiers`.

Под-блоки не пересекаются → `state_modifiers` от TGR переживает E&F сам по себе.
Компач ничего не чинит.

Хуже того, он сейчас портит баланс — за январь TGR поменял значения:

| | компач | TGR 12.08.2026 |
|---|---|---|
| `state_weekly_trades_add` | 1 | 0.5 |
| `state_trade_capacity_add` | 1 | 1 |
| `state_tax_capacity_add` | нет | 0.25 |

То есть компач удваивает недельные сделки и съедает налоговую ёмкость во всех
14 PM штаб-квартир.

`building_modifiers` в компаче пока совпадают с E&F один в один — то есть эта
половина файла просто дублирует E&F.

> Перед удалением — дешёвая проверка в игре, см. чеклист п.1.

### 2. `common/buy_packages/ef_tgr_buy_packages_inject.txt` — **удалить**

Сравнил построчно с `E&F/common/buy_packages/00_ef_buy_packages.txt`:
99 ключей из 99 совпадают дословно. Это копия файла E&F.

Конфликта нет и не было: TGR перекрывает ванильный `00_buy_packages.txt` (тот же
относительный путь), E&F грузится позже отдельным файлом `00_ef_buy_packages.txt`
и делает `INJECT:` в уже переопределённые TGR записи. Разные имена файлов не
конфликтуют никогда, а `INJECT` в чужое определение отрабатывает штатно.

Побочный риск от дубля: `popneed_currency`/`popneed_financial_products`
инжектятся дважды в один и тот же `goods = {}`.

### 3. `common/static_modifiers/ef_tgr_base_values_compat.txt` — **сократить до одной строки**

`base_values` патчат четверо, и **все через `INJECT:`** — то есть они мерджатся,
конфликта нет:

- `E&F/00_ef_static_modifier.txt`: `country_minting_add = -500`
- `TGR_LOANS_code_static_modifiers.txt`: `country_loan_interest_rate_add = -0.2`
- `TGR_POLITICS_code_static_modifiers.txt`: bureaucracy/authority/influence = 200, `country_officers_pol_str_mult = -2`, `country_soldiers_pol_str_mult = -1`
- `TGR_TRADE_code_static_modifiers.txt`: `country_company_construction_efficiency_bonus_add = 0.20`, `state_max_trade_advantage_from_capacity_add = 0.05`

Компач «пиннит» значения января и потому сейчас переписывает TGR неверными
числами:

| ключ | компач | TGR сегодня |
|---|---|---|
| `country_company_throughput_bonus_add` | **0.40** | закомментирован (нигде нет) |
| `country_company_construction_efficiency_bonus_add` | **−0.05** | **+0.20** |
| `state_max_trade_advantage_from_capacity_add` | нет | 0.05 |

`+0.40` к пропускной способности компаний — подарок из ниоткуда, `−0.05` вместо
`+0.20` — потеря 25 п.п. эффективности стройки.

Оправдана только одна строка — нейтрализация базовой ставки TGR, раз модуль
займов выключен:

```
INJECT:base_values = {
    # TGR_LOANS injects -0.2 as the baseline for its own loan mechanic.
    # This patch disables that mechanic, so the baseline has to go back to 0,
    # otherwise vanilla/E&F loans become almost free.
    country_loan_interest_rate_add = 0
}
```

### 4. `common/technology/technologies/ef_tgr_technology_compat.txt` — **переписать на `INJECT:`**

Здесь конфликт настоящий: TGR добавляет свои модификаторы в блок `modifier`,
а E&F перечисляет `modifier` целиком и потому его затирает.

Разбор по каждой технологии (TGR → E&F → что теряется):

| техно | источник в TGR | E&F трогает `modifier`? | теряется |
|---|---|---|---|
| `banking` | LOANS `REPLACE_OR_CREATE` + TRADE `INJECT` | да | `state_export_advantage_mult = 0.05` |
| `central_banking` | LOANS + TRADE `INJECT` | да | `country_minting_mult = 0.1`, `state_export_advantage_mult = 0.05`, `state_max_trade_advantage_from_capacity_add = 0.05` |
| `mutual_funds` | LOANS + TRADE `INJECT` | да | `state_building_trade_center_max_level_add = 10` |
| `corporate_charters` | TRADE `INJECT` | да | `state_building_trade_center_max_level_add = 10`, `state_export_advantage_mult = 0.05` |
| `joint_stock_companies` | TRADE `REPLACE_OR_CREATE` | да | `state_market_access_price_impact = 0.05`, `state_building_trade_center_max_level_add = 10` |
| `investment_banks` | TRADE `REPLACE_OR_CREATE` | да | `state_max_trade_advantage_from_capacity_add = 0.05`, `state_building_trade_center_max_level_add = 10` |
| `currency_standards` | TRADE `INJECT` | **нет** (у E&F нет блока `modifier`) | ничего |
| `international_exchange_standards` | LOANS | да, но E&F — надмножество TGR | ничего |
| `modern_financial_instruments` | LOANS | да, но E&F — надмножество TGR | ничего |

Что не так с текущим файлом:

- **`corporate_charters` вообще отсутствует** — а он теряется.
- Нигде нет `state_building_trade_center_max_level_add = 10`. По TGR его дают
  `currency_standards`, `stock_exchange`, `corporate_charters`, `mutual_funds`,
  `joint_stock_companies`, `investment_banks` — это ядро масштабирования Trade
  Center. Из них компач глушит 4 → −40 уровней потолка ТЦ к концу игры.
- У `investment_banks` прописан `state_import_advantage_mult = 0.25`, которого
  сегодня нет ни в TGR, ни в E&F. Фантом из старой версии.
- `banking` и `modern_financial_instruments` скопированы из E&F дословно и не
  добавляют ничего — мёртвый груз.
- `mutual_funds`, `joint_stock_companies`, `investment_banks`,
  `international_exchange_standards`: компач возвращает `unlocking_technologies`,
  которые автор E&F осознанно закомментировал (`# central_banking`,
  `# postal_savings`, `# corporate_charters`, `# mutual_funds`). Это не мердж,
  это откат чужого решения.
- `central_banking.on_researched` в компаче — старая копия E&F: `gdp_view >= 1`
  вместо `var:gdp_view >= 1` и без исключения `c:JAP`. Первое даёт ошибку в
  логе, второе выдаёт Японии новую валюту вопреки явному условию автора.

Правильный вид — не переписывать чужие определения, а до-мерджить потерянные
ключи. Файл сжимается с ~200 строк до ~40 и перестаёт разъезжаться при
обновлении любого из модов:

```
# Vic3 patch semantics: REPLACE: swaps only the sub-blocks a mod lists.
# E&F lists `modifier` on these techs, so TGR's own modifier keys are wiped.
# INJECT: merges into the surviving block instead of restating E&F's definition —
# that way an E&F or TGR value change does not silently drift out of this patch.
# Plain INJECT (not TRY_INJECT): these are vanilla techs, they cannot disappear,
# and a loud log line is better than a silent no-op if that ever changes.

INJECT:banking = { modifier = { state_export_advantage_mult = 0.05 } }
INJECT:central_banking = { modifier = {
    country_minting_mult = 0.1
    state_export_advantage_mult = 0.05
    state_max_trade_advantage_from_capacity_add = 0.05
} }
INJECT:mutual_funds = { modifier = { state_building_trade_center_max_level_add = 10 } }
INJECT:corporate_charters = { modifier = {
    state_building_trade_center_max_level_add = 10
    state_export_advantage_mult = 0.05
} }
INJECT:joint_stock_companies = { modifier = {
    state_market_access_price_impact = 0.05
    state_building_trade_center_max_level_add = 10
} }
INJECT:investment_banks = { modifier = {
    state_max_trade_advantage_from_capacity_add = 0.05
    state_building_trade_center_max_level_add = 10
} }
```

Открытый вопрос по `banking`: TGR_TRADE даёт `state_max_trade_advantage_from_capacity_add = -0.05`,
гася собственный `+0.05` из TGR_LOANS. С выключенным модулем займов у E&F
остаётся свой `+0.05`. Возвращать ли −0.05 — решение по балансу, не по конфликту.

### 5. `common/diplomatic_actions/zz_disable_tgr_international_loans.txt` — **удалить**

`issue_a_loan` и `apply_for_a_loan` не определены нигде: ни в ванили, ни в
текущем TGR (`common/diplomatic_actions/` содержит только
`TGR_ADJUSTMENTS_doctrine_of_lapse`, `TGR_ADJUSTMENTS_power_bloc_force_regime_change`,
`TGR_ADJUSTMENTS_trade_states`, `TGR_TRADE_subjects_request_market_control`), ни в
подмоде `TGR_Loans`. От них остались только иконки в
`TGR_Loans/gfx/interface/icons/lens_toolbar_icons/`.

`REPLACE_OR_CREATE:` на несуществующий ключ **создаёт** его. То есть файл сейчас
не отключает ничего, а порождает два фантомных дипдействия без локализации.

### 6. `common/journal_entries/…` и `common/scripted_buttons/…` — **оставить как есть**

`je_international_loans` и `tgr_loans_button_1..8` живы в текущем TGR
(`TGR_LOANS_panel.txt`, `TGR_LOANS_buttons.txt`), id совпадают, все восемь кнопок
на месте. Отключение работает.

Замечание по замыслу: это единственная часть компача, которая не чинит конфликт,
а принимает решение за игрока. Файловых пересечений между займами TGR и финансами
E&F нет вообще (`journal_entries`, `scripted_buttons`, `scripted_guis`,
`scripted_progress_bars` — пересечение ключей пустое). Отключение оправдано
дублированием механик, и это стоит написать в README прямым текстом, а не как
«fix».

### 7. `gui/budget_panel.gui` — **пересобрать заново, это самое срочное**

Файл в компаче от 10.01.2026 и собран на базе **1.12**. И E&F (04.07.2026), и TGR
(12.08.2026) свои копии на 1.13 уже обновили — устарел только компач.

Что нашёл:

- `blockoverride "is_selected_visibility_very_low" / _low / _medium / _high / _very_high`
  и парные `is_clickable_alpha_*`. В ванили 1.13.10 таких блоков **нет** — там
  `is_selected_visibility_1 … _5`. Проверено: `is_selected_visibility_very_low`
  не встречается ни в одном `gui/*.gui` ванили, `is_selected_visibility_1` есть в
  `budget_panel.gui`, `construction_panel.gui`, `military_formation_panel.gui`.
  Итог — блоковеррайды в никуда, логика выбора уровня налога не применяется.
- Потеряны целые строки бюджета, которые есть и в ванили, и в TGR, и в E&F:
  `BUDGET_TREATIES` (доход от договоров), `GetSupplyShipMaintenanceExpenses`,
  обслуживание военных кораблей, `GetShipConstructionGoodsExpenses`.
- `text = "BUDGET_GOODS_FOR_MILITARY_BUILDINGS"` — ключа в 1.13 нет, ваниль
  использует `[concept_budget_goods_for_military_upkeep]`.
- По именам виджетов: в компаче отсутствует `tutorial_highlight_tax_level`,
  который есть и в ванили, и в E&F. Ровно тот признак, о котором речь в общих
  правилах: пропавшее имя виджета — вылет, а не строчка в логе.

Пересобирать так: **база — текущий `TheGreatRevision/gui/budget_panel.gui`**
(он уже 1.13-корректный и несёт весь налоговый блок TGR), сверху накатить дельту
E&F. Дельта E&F против ванили компактная и вся сводится к:

1. `@money!` → `[GetPlayer.GetCustom('currency_symbol')]` (~16 мест, включая новые
   строки TGR `tgr_land_tax` / `tgr_per_capita_tax`);
2. вкладка `assets` → `ECONOMY` (`SelectTab('economy')` + вызов
   `list_generation_when_player_open_tab`), плюс новые `fourth_button` = `FINANCE`
   и `fifth_button` = `STOCKPILE`;
3. три новых контейнера в конце: `budget_panel_economy_panel_content`,
   `budget_panel_financial_panel_content`, `budget_panel_stockpile_panel_content`;
4. вырезаны ванильные `declare_bankruptcy_button`, `bankruptcy_progress_bar`,
   `bankruptcy_progressbar` и виджет `declared_bankruptcy` — у E&F своя система
   банкротства;
5. `Country.GetMilitaryShipConstructionGoodsExpenses` →
   `Country.GetShipConstructionGoodsExpenses`, убран блок
   `GetSupplyShipConstructionGoodsExpenses`.

Всё остальное в файле E&F совпадает с ванилью — значит должно совпадать с TGR.
После сборки прогнать `compare_gui_names.py` компач vs ваниль: из ванильных имён
допустимо отсутствие только тех, что убрал сам E&F
(`declare_bankruptcy_button`, `bankruptcy_progress_bar`, `bankruptcy_progressbar`,
`tutorial_highlight_assets`). `tutorial_highlight_tax_level` обязан быть.

### 8. `localization/*/zz_ef_tgr_private_ownership_stock_*.yml` — **обрезать до 4 ключей**

Из 12 ключей 8 (`pm_no_private_ownership_*`, `pm_private_ownership_majority_*`)
E&F теперь определяет сам в
`01_ef_production_method_localization_l_english.yml`. Не определены только
четыре групповых:

`pmg_private_ownership_manufacture_stock`, `pmg_private_ownership_agricultural_stock`,
`pmg_private_ownership_mining_stock`, `pmg_private_ownership_railroad_stock`.

Плюс это не про TGR вообще — та же пачка файлов лежит в `stuff/ef+vc done` и
`stuff/_bpm/bpm+ef done`. Логичное место — `ef hotfix 1.13`. Пока хотфикс не
обязателен к установке, оставить здесь обрезанную версию.

### 9. `.metadata/metadata.json` — **обновить**

`version: 1.12.3` → `1.13.0`, `supported_game_version: 1.12.*` → `1.13.*`,
тег `"1.12"` → `"1.13"`, `tested_with`: E&F `4.07.2026`, TGR `2.0 / 1.13.10 (12.08.2026)`.

---

## Отдельно: потолок товаров

Ваниль 53, E&F добавляет 73 новых (65 валют + silver, bond, 4 биржевых, mutual_funds,
local_currency) и патчит только `gold`. TGR новых товаров **не добавляет** —
все 53 его записи это `REPLACE_OR_CREATE:` ванильных.

**Итого 126 из 128.** Запас — два товара. Любой третий мод с новыми товарами в
одной сборке = вылет при входе в игру без единой строки в логе. Это надо написать
в README компача и проверять при каждой сборке мегапака.

Заодно: `gold` у TGR побайтово равен ванильному (пустой `REPLACE_OR_CREATE`),
`INJECT:gold` от E&F (`tradeable = yes`, `fixed_price = no`) отрабатывает поверх.
Конфликта нет.

---

## Что проверено и конфликта не даёт

- `common/on_actions` — пересечение по `on_half_yearly_pulse_country`,
  `on_monthly_pulse_country`, `on_yearly_pulse_country`; on_actions аддитивны.
- `common/history/global` (`GLOBAL`) и `common/history/buildings` (`BUILDINGS`) — аддитивны.
- `common/buildings` — 18 общих ключей, но E&F везде `INJECT` (PM-группа
  `pmg_market_liquidity`), TGR — `REPLACE_OR_CREATE` полного определения.
  E&F грузится позже и только дописывает.
- `common/goods` — только `gold`, см. выше.
- localization — 0 общих ключей.
- события — 0 общих id.
- `journal_entries` / `scripted_buttons` / `scripted_guis` /
  `scripted_progress_bars` — пересечение ключей пустое.

---

## Чеклист проверки в игре (по убыванию риска)

1. **Штаб-квартира компании без файла PM-компача.** Убрать
   `ef_tgr_company_hq_pm_compat.txt`, зайти в игру, навести на построенную
   Company HQ. Годно: в тултипе есть `state_trade_capacity_add` и
   `state_tax_capacity_add`, и при этом занятость капиталистов/клерков — из E&F
   (3 / 3.5). Не годно: пропала торговая ёмкость → `REPLACE:` всё-таки заменяет
   запись целиком, файл возвращаем и правим цифры на 0.5 / 1 / 0.25.
2. **Бюджетная панель.** Открыть, пройти все вкладки: Overview / States /
   Economy / Finance / Stockpile. Годно: вкладки переключаются, налоговые +/− TGR
   двигают значения, видны строки Treaties и обслуживания флота, суммы с символом
   валюты E&F. Не годно: пустая вкладка, `@money!` вместо символа, отсутствующие
   строки.
3. **Уровни налогов TGR.** Пощёлкать все пять уровней. Годно: подсветка выбранного
   уровня меняется. Не годно: подсветка не двигается → блоковеррайды `_1.._5`
   всё ещё не совпадают.
4. **Туториал.** Начать игру с включённым туториалом до шага про налоги.
   Годно: подсказка привязывается к контролу. Не годно: вылет →
   `tutorial_highlight_tax_level` не восстановлен.
5. **Займы.** Дипломатия и журнал. Годно: `je_international_loans` не виден,
   кнопок TGR по займам нет, фантомных «Issue a loan» / «Apply for a loan» в
   списке дипдействий тоже нет.
6. **Ставка по кредиту.** Взять заём в 1836. Годно: ставка близка к ванильной
   базе, а не почти нулевая (значит `country_loan_interest_rate_add = 0`
   отработал).
7. **Потолок Trade Center.** Изучить `corporate_charters` + `joint_stock_companies`
   + `investment_banks` + `mutual_funds`. Годно: максимальный уровень Trade Center
   в штате вырос примерно на 40. Не годно: не растёт → INJECT в `modifier` не
   доехал.
8. **Товары.** Просто зайти в игру со всей сборкой. Вылет без ошибок в
   `error.log` = уперлись в 128.
9. **`error.log`.** Пусто по `budget_panel`, по `blockoverride`, по
   `gdp_view`, по `issue_a_loan` / `apply_for_a_loan`.

---

## Что записать в сводки

- `сводка_tgr.md` — добавить шапку с версией и датой сверки (сейчас её нет),
  зафиксировать: модуль Loans физически лежит внутри основного TGR и побайтово
  совпадает с подмодом `TGR_Loans`; `state_building_trade_center_max_level_add = 10`
  раздаётся шестью технологиями; дипдействия `issue_a_loan` / `apply_for_a_loan`
  удалены.
- `сводка_ef.md` — обновить дату сверки; отметить, что `REPLACE:` у E&F
  повсеместно частичный (только нужные под-блоки), и что 8 из 12 loc-ключей
  `private_ownership_*` мод теперь закрывает сам.
- В общие правила по 1.13 — пункт про под-блочную семантику `REPLACE:`.
