# E&F + TGR — ревизия и пересборка компача, 21.08.2026

## Что сверялось

| Мод | Версия / коммит | metadata | Примечание |
|---|---|---|---|
| E&F | `E&F 4.07.2026` | пустой (`version`/`supported_game_version` = "") | сводка сверена 21.08.2026 |
| E&F 1.13.10 Hotfix | `1.13.10-2`, `1.13.*` | Steam `3786286962` | грузится сразу после E&F, всегда |
| TheGreatRevision | `TGR 1.3.10 12.08.2026 update` | `2.0`, `1.13.10` | модуль Loans лежит внутри |
| TGR_Loans (подмод) | `2.0`, `1.13.11` | Steam `3452303324` | файлы **побайтово равны** одноимённым в основном TGR |
| компач `ef+tgr done` до правки | `1.12.3`, `supported_game_version: 1.12.*` | — | контент датирован 10–23.01.2026 |

Компач не обновлялся ни после июльского E&F, ни после августовского TGR.
Прогон `scan_conflicts.py` на 21.08.2026: 148 общих ключей, 29 общих категорий,
0 общих loc-ключей, 0 общих id событий (отчёт сохранён в папку компача).

**Хотфикс с компачем не пересекается вообще** — ни по одному файлу и ключу.
У него нет `technology`, `defines`, `production_methods`, `buy_packages`,
`localization`, а из `gui` он трогает `custom_tooltip`, `frontend/shared/lists`,
`map_markers`, `military_formation_panel`, `popups`, `right_click_menu` — но не
`budget_panel`. Порядок между хотфиксом и компачем значения не имеет.

---

## Главный вывод: `REPLACE:` работает **по под-блокам**, а не по записи целиком

Это переворачивает половину январского разбора и стоит держать в общих правилах.

Доказательство прямо в E&F: все 14 `REPLACE:pm_company_headquarter_*` в
`common/production_methods/11_ef_private_infrastructure.txt` содержат **только**
`building_modifiers`. Если бы `REPLACE:` заменял запись целиком, у E&F в соло
пропали бы `texture`, `is_hidden_when_unavailable`, `unlocking_company_categories`,
`disallowing_laws`, `unlocking_laws`, `unlocking_principles` — PM «рабочий
кооператив» стал бы доступен без соответствующего закона, а иконки исчезли бы.
Этого не происходит.

Значит: `REPLACE:key = { X = {...} }` заменяет **только** под-блок `X`;
всё, что мод не перечислил, остаётся от предыдущего слоя. `INJECT:` отличается
тем, что под-блок не заменяется, а до-мерджится.

**Конфликт есть только там, где оба мода перечислили один и тот же под-блок.**
Совпадение ключа в отчёте `scan_conflicts.py` само по себе не значит ничего.

---

## Что сделано

### Удалено (в git, папка `_to_delete` была затёрта параллельной работой — восстанавливать через `git log --diff-filter=D`)

**`common/production_methods/ef_tgr_company_hq_pm_compat.txt`** (505 строк).
TGR даёт `REPLACE_OR_CREATE:pm_company_headquarter_*` с полным определением,
включая `state_modifiers`; E&F делает `REPLACE:` тех же ключей, но перечисляет
только `building_modifiers`. Под-блоки не пересекаются → `state_modifiers`
переживает E&F сам. Плюс файл вносил устаревшие числа:

| | компач | TGR 12.08.2026 |
|---|---|---|
| `state_weekly_trades_add` | 1 | 0.5 |
| `state_trade_capacity_add` | 1 | 1 |
| `state_tax_capacity_add` | нет | 0.25 |

То есть он удваивал недельные сделки и съедал налоговую ёмкость во всех 14 PM.

**`common/buy_packages/ef_tgr_buy_packages_inject.txt`.** Построчно сравнил с
`E&F/common/buy_packages/00_ef_buy_packages.txt` — 99 ключей из 99 совпадают
дословно. Это копия файла E&F. Конфликта нет и не было: TGR перекрывает ванильный
`00_buy_packages.txt`, E&F грузится позже отдельным именем и делает `INJECT:` в уже
переопределённые записи. Побочный риск дубля — двойной инжект
`popneed_currency` / `popneed_financial_products` в один `goods = {}`.

**`common/diplomatic_actions/zz_disable_tgr_international_loans.txt`.**
`issue_a_loan` и `apply_for_a_loan` не определены нигде: ни в ванили, ни в текущем
TGR, ни в подмоде `TGR_Loans` — остались только иконки в
`TGR_Loans/gfx/interface/icons/lens_toolbar_icons/`. `REPLACE_OR_CREATE:` на
несуществующий ключ его **создаёт**, то есть файл не отключал ничего, а порождал
два фантомных дипдействия без локализации.

**Январские отчёты** `conflicts_tgr_vs_ef_report.md` и `..._pre_b5525.md` →
`_to_delete/ef+tgr_stale_reports_2026-08-21/`, вместо них
`conflicts_tgr_vs_ef_report_2026-08-21.md`.

### Переписано

**`common/technology/technologies/ef_tgr_technology_compat.txt`** — с ~200 строк
переписанных чужих определений на 6 точечных `INJECT:`.

Разбор по каждой технологии:

| техно | источник в TGR | E&F перечисляет `modifier`? | теряется |
|---|---|---|---|
| `banking` | LOANS `REPLACE_OR_CREATE` + TRADE `INJECT` | да | `state_export_advantage_mult = 0.05` |
| `central_banking` | LOANS + TRADE `INJECT` | да | `country_minting_mult = 0.1`, `state_export_advantage_mult = 0.05`, `state_max_trade_advantage_from_capacity_add = 0.05` |
| `mutual_funds` | LOANS + TRADE `INJECT` | да | `state_building_trade_center_max_level_add = 10` |
| `corporate_charters` | TRADE `INJECT` | да | `state_building_trade_center_max_level_add = 10`, `state_export_advantage_mult = 0.05` |
| `joint_stock_companies` | TRADE `REPLACE_OR_CREATE` | да | `state_market_access_price_impact = 0.05`, `state_building_trade_center_max_level_add = 10` |
| `investment_banks` | TRADE `REPLACE_OR_CREATE` | да | `state_max_trade_advantage_from_capacity_add = 0.05`, `state_building_trade_center_max_level_add = 10` |
| `currency_standards` | TRADE `INJECT` | **нет блока `modifier`** | ничего |
| `international_exchange_standards` | LOANS | да, но E&F — надмножество | ничего |
| `modern_financial_instruments` | LOANS | да, но E&F — надмножество | ничего |

Что было не так со старым файлом:

- `corporate_charters` вообще отсутствовал, хотя теряется.
- Нигде не было `state_building_trade_center_max_level_add`. По TGR его дают шесть
  технологий по +10; компач глушил четыре из них → ≈40 уровней потолка Trade Center
  к концу игры.
- У `investment_banks` был прописан `state_import_advantage_mult = 0.25`, которого
  нет ни в TGR, ни в E&F. Фантом из старой версии.
- `banking` и `modern_financial_instruments` были скопированы из E&F дословно и не
  добавляли ничего.
- `mutual_funds`, `joint_stock_companies`, `investment_banks`,
  `international_exchange_standards` возвращали `unlocking_technologies`, которые
  автор E&F осознанно закомментировал. Это откат чужого решения, а не мердж.
- `central_banking.on_researched` был старой копией E&F: `gdp_view >= 1` вместо
  `var:gdp_view >= 1` (ошибка в логе) и без исключения `c:JAP` — Япония получала
  новую валюту вопреки явному условию автора.

Открытый вопрос по балансу: TGR_TRADE даёт `banking`
`state_max_trade_advantage_from_capacity_add = -0.05`, гася собственный `+0.05` из
TGR_LOANS. С выключенным модулем займов у E&F остаётся свой `+0.05`; возвращать
`−0.05` не стал — это решение по балансу, не по конфликту.

**`common/static_modifiers/ef_tgr_base_values_compat.txt`** — до одной строки.
`base_values` патчат четверо и **все через `INJECT:`**, то есть мерджатся:

- `E&F/00_ef_static_modifier.txt`: `country_minting_add = -500`
- `TGR_LOANS_code_static_modifiers.txt`: `country_loan_interest_rate_add = -0.2`
- `TGR_POLITICS_code_static_modifiers.txt`: bureaucracy/authority/influence = 200, `country_officers_pol_str_mult = -2`, `country_soldiers_pol_str_mult = -1`
- `TGR_TRADE_code_static_modifiers.txt`: `country_company_construction_efficiency_bonus_add = 0.20`, `state_max_trade_advantage_from_capacity_add = 0.05`

Компач «пиннил» значения января и потому переписывал TGR неверными числами:

| ключ | было в компаче | TGR сегодня |
|---|---|---|
| `country_company_throughput_bonus_add` | **0.40** | закомментирован (нигде нет) |
| `country_company_construction_efficiency_bonus_add` | **−0.05** | **+0.20** |
| `state_max_trade_advantage_from_capacity_add` | нет | 0.05 |

Осталась одна оправданная строка — обнуление базовой ставки TGR, раз модуль займов
выключен, иначе ванильные/E&F кредиты почти бесплатны всю игру.

**`common/defines/ef_tgr_defines.txt`** — оставлен только `PRICE_RANGE = 0.85`.
`GOODS_SHORTAGE_PENALTY_MAX` и `GOLD_RESERVE_RETURNS_FACTOR` TGR не трогает, а E&F
грузится позже — дублировать их было незачем. В комментарии зафиксировано, что
`PRICE_RANGE` — это решение по балансу (ваниль 0.75, TGR 0.85, E&F 0.99), и что при
жалобах на беззубые валютные кризисы E&F первым делом надо пробовать 0.99.

**`localization/*/zz_ef_tgr_private_ownership_stock_*.yml`** (11 языков) — с 12
ключей до 4. Восемь `pm_*` E&F с 04.07.2026 определяет сам в
`01_ef_production_method_localization`. Остались только групповые
`pmg_private_ownership_{manufacture,agricultural,mining,railroad}_stock`.
В шапку каждого файла добавлена пометка, что к TGR это отношения не имеет и логичное
место — хотфикс (та же пачка лежит в `stuff/ef+vc done` и `stuff/_bpm/bpm+ef done`).

**`.metadata/metadata.json`** — `1.12.3 / 1.12.*` → `1.13.0 / 1.13.*`, тег `1.13`,
`tested_with` обновлён под TGR 12.08.2026, E&F 04.07.2026 и хотфикс.

**`README.md`** — пересобран: хотфикс добавлен в порядок загрузки с пометкой, что
его позиция относительно компача не важна; расписано, что именно чинится и что
удалено и почему; предупреждение про потолок товаров.

### Пересобрано с нуля: `gui/budget_panel.gui`

Старый файл (10.01.2026) был собран на базе **1.12**, тогда как и E&F (04.07.2026),
и TGR (12.08.2026) свои копии на 1.13 уже обновили. Что в нём было:

- `blockoverride "is_selected_visibility_very_low / _low / _medium / _high / _very_high"`
  и парные `is_clickable_alpha_*`. В ванили 1.13.10 таких блоков **нет** — там
  `is_selected_visibility_1 … _5` (проверено: `_very_low` не встречается ни в одном
  `gui/*.gui` ванили). Блоковеррайды в никуда — логика выбора уровня налога не
  применялась.
- Потеряны строки бюджета, которые есть и в ванили, и в TGR, и в E&F:
  `BUDGET_TREATIES`, `GetSupplyShipMaintenanceExpenses`, обслуживание военных
  кораблей, `GetShipConstructionGoodsExpenses`.
- `text = "BUDGET_GOODS_FOR_MILITARY_BUILDINGS"` — ключа в 1.13 нет, ваниль
  использует `[concept_budget_goods_for_military_upkeep]`.
- Отсутствовало имя виджета `tutorial_highlight_tax_level`.

Сборка сделана трёхсторонним мерджем `git merge-file` (база — ваниль 1.13.10,
стороны — E&F и TGR). Шесть конфликтов, все разобраны построчно:

- четыре — там, где TGR перестроил налоговые ряды и вставил свои +/−, а E&F в тех же
  местах менял только `@money!`; взята сторона TGR, символ валюты доехал глобальной
  заменой;
- два — чистое `@money!` против `[GetPlayer.GetCustom('currency_symbol')]`; взята
  сторона E&F.

Затем `@money!` заменён на `[GetPlayer.GetCustom('currency_symbol')]` по всему файлу
(46 мест, включая новые строки TGR `tgr_land_tax` / `tgr_per_capita_tax`).

Отдельно восстановлено имя `tutorial_highlight_tax_level`. Ваниль и E&F вешают его
через `blockoverride "tutorial_highilight_name"` на `tax_exp_frame_coin`, но TGR
заменил этот ряд своим типом `tax_exp_frame_fiscal_reform`, у которого такого блока
нет — поэтому имя проставлено напрямую атрибутом `name` на виджете, с комментарием
почему именно так.

Результат — 2500 строк, скобки сходятся, `@money!` не осталось. Проверка имён
виджетов:

- `E&F − компач`: **пусто**;
- `TGR − компач`: `tutorial_highlight_assets` — вкладку Assets заменяет вкладка
  Economy от E&F, у самого E&F этого имени тоже нет;
- `ваниль − компач`: `bankruptcy_progress_bar`, `bankruptcy_progressbar`,
  `declare_bankruptcy_button`, `tutorial_highlight_assets` — ровно те четыре, что
  убирает сам E&F под свою систему банкротства;
- в компаче нет ни одного имени, которого нет ни у кого из троих.

Всё содержимое обеих сторон на месте: `tgr_land_tax` / `tgr_per_capita_tax` /
`tgr_income_tax` / `tgr_dividends_tax` / `tgr_consumption_tax` — по 9 вхождений
(как в TGR); `SelectTab('economy'|'finance'|'stockpile')`,
`budget_panel_{economy,financial,stockpile}_panel_content`,
`list_generation_when_player_open_tab` — как в E&F.

---

## Итоговый состав компача

```
.metadata/metadata.json
README.md
common/defines/ef_tgr_defines.txt                                  PRICE_RANGE
common/journal_entries/zz_disable_tgr_international_loans.txt      je_international_loans
common/scripted_buttons/zz_disable_tgr_international_loans_buttons.txt  tgr_loans_button_1..8
common/static_modifiers/ef_tgr_base_values_compat.txt              country_loan_interest_rate_add = 0
common/technology/technologies/ef_tgr_technology_compat.txt        6 x INJECT
gui/budget_panel.gui                                               трёхсторонний мердж
localization/<11 языков>/zz_ef_tgr_private_ownership_stock_*.yml   4 ключа
conflicts_tgr_vs_ef_report_2026-08-21.md
```

Было 9 файлов `common/` + gui + loc на 12 ключей, стало 5 файлов `common/`, из них
два — отключение займов.

---

## Отдельно: потолок товаров

Ваниль 53, E&F добавляет 73 новых и патчит только `gold`. TGR новых товаров **не
добавляет** — все 53 его записи это `REPLACE_OR_CREATE:` ванильных, причём `gold` у
него побайтово равен ванильному, а `INJECT:gold` от E&F (`tradeable = yes`,
`fixed_price = no`) отрабатывает поверх.

- E&F + TGR без хотфикса: **126 из 128** — запас два товара;
- E&F + TGR с хотфиксом (он режет 8 валют): **118** — запас десять.

Это записано в README компача.

---

## Что проверено и конфликта не даёт

- `common/on_actions` — пересечение по `on_half_yearly_pulse_country`,
  `on_monthly_pulse_country`, `on_yearly_pulse_country`; каталог аддитивен.
- `common/history/global` (`GLOBAL`) и `common/history/buildings` (`BUILDINGS`) — аддитивны.
- `common/buildings` — 18 общих ключей, но E&F везде `INJECT` (PM-группа
  `pmg_market_liquidity`), TGR — `REPLACE_OR_CREATE` полного определения; E&F грузится
  позже и только дописывает.
- `common/goods` — только `gold`, см. выше.
- localization — 0 общих ключей; события — 0 общих id.
- `journal_entries` / `scripted_buttons` / `scripted_guis` /
  `scripted_progress_bars` — пересечение ключей пустое, то есть займы TGR и финансы
  E&F не конфликтуют технически вообще. Отключение займов — решение по механикам,
  и в README это названо своим именем.

---

## Хвост: мегапаки

В `__megapacks/megapack` и `__megapacks/megapack no t&r` лежат копии удалённых
файлов (`ef_tgr_company_hq_pm_compat.txt`, `ef_tgr_buy_packages_inject.txt`).
Мегапаки надо пересобрать, иначе в сборке останутся старые значения PM
штаб-квартир и двойной инжект buy packages.

---

## Чеклист проверки в игре (по убыванию риска)

1. **Бюджетная панель.** Открыть, пройти вкладки Overview / States / Economy /
   Finance / Stockpile. Годно: вкладки переключаются, налоговые +/− TGR двигают
   значения, видны строки Treaties и обслуживания флота, суммы с символом валюты
   E&F. Не годно: пустая вкладка, `@money!` вместо символа, отсутствующие строки.
2. **Уровни налогов TGR.** Пощёлкать все пять уровней. Годно: подсветка выбранного
   уровня меняется (значит `is_selected_visibility_1..5` теперь совпадают с 1.13).
3. **Туториал.** Начать игру с включённым туториалом до шага про налоги.
   Годно: подсказка привязывается к контролу, вылета нет.
4. **Штаб-квартира компании.** Навести на построенную Company HQ. Годно: в тултипе
   есть торговая ёмкость и налоговая ёмкость от TGR, занятость капиталистов/клерков
   от E&F (3 / 3.5). Не годно: торговой ёмкости нет → `REPLACE:` всё-таки заменяет
   запись целиком, файл PM-мерджа надо вернуть из git и переписать цифры на
   0.5 / 1 / 0.25.
5. **Потолок Trade Center.** Изучить `corporate_charters` + `joint_stock_companies` +
   `investment_banks` + `mutual_funds`. Годно: максимальный уровень Trade Center в
   штате вырос примерно на 40. Не годно: не растёт → `INJECT` в `modifier` не доехал.
6. **Займы.** Дипломатия и журнал. Годно: `je_international_loans` не виден, кнопок
   TGR по займам нет, фантомных «Issue a loan» / «Apply for a loan» в списке
   дипдействий тоже нет.
7. **Ставка по кредиту.** Взять заём в 1836. Годно: ставка близка к ванильной базе,
   а не почти нулевая.
8. **Потребности попов.** Тултип нужд попа: `popneed_currency` и
   `popneed_financial_products` присутствуют и в разумных числах (не удвоены).
9. **Товары.** Просто зайти в игру со всей сборкой — вылет без ошибок в `error.log`
   означает потолок 128.
10. **`error.log`.** Пусто по `budget_panel`, по `blockoverride`, по `gdp_view`,
    по `issue_a_loan` / `apply_for_a_loan`.

---

## Что записано в сводки

- `сводка_tgr.md` — добавлена шапка с версией и датой сверки (её не было) +
  раздел «Дополнение 2026-08-21»: модуль Loans внутри основного TGR и его
  побайтовое равенство подмоду `TGR_Loans`; исчезнувшие дипдействия;
  `state_building_trade_center_max_level_add` по шести технологиям; разделение
  технологий по LOANS/TRADE; актуальные значения `base_values`; новые числа PM
  штаб-квартир; нейтральность по товарам; признаки 1.13-корректного
  `budget_panel.gui`.
- `сводка_ef.md` — дата сверки 21.08.2026 + раздел «Дополнение 2026-08-21»:
  под-блочная семантика `REPLACE:` с доказательством; отсутствие `modifier` у
  `currency_standards`; изменение `central_banking.on_researched`; список
  закомментированных `unlocking_technologies`; закрытые модом loc-ключи;
  безопасность `buy_packages`; товары 126 / 118 с хотфиксом и полное отсутствие
  пересечений хотфикса с компачами.
- В общие правила по 1.13 просится пункт про под-блочную семантику `REPLACE:` —
  без него отчёт `scan_conflicts.py` читается неверно.
