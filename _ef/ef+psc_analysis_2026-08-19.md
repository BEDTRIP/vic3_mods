# Анализ компача `_ef/ef+psc done` — E&F (4.07.2026) + PSC 1.3.7

Дата: 19.08.2026. Игра 1.13.10.
Проверено по файлам: `vic3_mods_out/E&F`, `vic3_mods_out/PSC`, `vic3_mods_out/.vanillaVIC3`, `vic3_mods/_ef/ef hotfix 1.13`.

---

## 0. Состояние модов

| | версия | дата в репо | что в metadata компача |
|---|---|---|---|
| E&F | metadata пустой | коммит `E&F 4.07.2026` | `v4.1.1`, 2025-12-22 |
| PSC | `1.3.7`, имя `[1.13] Private Sector Construction` | коммит `PSC 2.05.2026` | `1.3.5`, 2026-01-21 |
| компач | `version 1.12.2`, `supported_game_version 1.12.*` | — | — |

Компач помечен `done`, но собирался под E&F v4.1.1 (декабрь 2025) и PSC 1.3.5. С тех пор E&F вырос очень заметно. Сводка по PSC обновлена (`сводки по модам/сводка_psc.md`, шапка с версией 1.3.7 и датой 19.08.2026).

---

## 1. Базовая проверка конфликта (Анализ 2)

`scan_conflicts.py --a E&F --b PSC`:

- пересечений по **путям файлов — ноль** (`common` 101 vs 22, `gui` 89 vs 6, `gfx` 856 vs 7);
- пересечений по ключам — 3, все аддитивные:
  - `BUILDINGS` в `common/history/buildings/` — аддитивно;
  - `GLOBAL` в `common/history/global/` — аддитивно;
  - `on_production_method_changed` в `common/on_actions/` — аддитивно;
- дублей id событий — 0;
- дублей ключей локализации — 2 (`state_building_construction_sector_max_level_add[_desc]`, E&F vs PSC) — косметика, последний выигрывает.

Компач нужен **не** из-за перекрытий, а из-за смысловой несовместимости: оба мода вводят «частный строительный сектор», и E&F видит только свой (`building_ef_private_construction`), не видя PSC-цепочку `building_construction_sector → строительные товары → building_construction_regulator`. Плюс — GUI (см. п. 3).

**Товары / потолок 128** — проверено отдельно, скриптом не ловится:

| | товаров |
|---|---|
| ваниль | 53 |
| E&F новых (`ef_00_goods.txt`, 74 записи из них `INJECT:gold`) | **73** |
| PSC новых (`local = yes`) | 4 |
| **итого E&F + PSC без хотфикса** | **130** |
| E&F новых **с `ef hotfix 1.13`** (66 записей, из них `INJECT:gold`) | 65 |
| **итого E&F + PSC + хотфикс** | **122** |

То есть связка E&F + PSC без `E&F 1.13.10 Hotfix` даёт 130 товаров — за потолком, вылет при входе в игру без единой строки в логе. Хотфикс режет 8 валют (`dinar_c`, `peso_c`, `gulden_indies_guilder_c`, `dollar_caribbean_dollar_c`, `dollar_new_zealand_dollar_c`, `eco_central_african_eco_c`, `eco_east_african_eco_c`, `eco_west_african_eco_c`) и уводит сумму на 122 — запас 6.

**Хотфикс сейчас нигде не заявлен как зависимость ef+psc** — ни в `README.md`, ни в `.metadata/metadata.json`, ни в `BED_TRIP's MEGAPACK.json`. Это надо чинить в первую очередь.

Группы законов — PSC законов не трогает вообще, `list_lawgroups_diff.py` не нужен.
Триггеры по building_group — E&F фильтрует по `bg_ef_private_construction` (свой), PSC по `bg_construction`; наследование тут не спасает, патч по существу нужен.

---

## 2. Прямой конфликт компача с `ef hotfix 1.13` — ломает оба

Оба **моих** мода кладут файл по одному и тому же относительному пути:

```
common/history/buildings/00_ef_building.txt
```

- хотфикс: 4229 строк = актуальный файл E&F + 2 правки (`STATE_ANDALUSIA` → `STATE_LOWER_ANDALUSIA`, снят блок `GRE` в `STATE_SAXONY`/`STATE_BRANDENBURG`, создававший здания в NULL-штате);
- компач: 2627 строк, копия E&F v4.1.1 с заменой `building_ef_private_construction` → `building_construction_sector`.

Кто загрузится позже — тот и выигрывает **целиком**:

- компач позже → правки хотфикса отменены (возвращается спам и здания в NULL-штате) **и** теряется 1602 строки нового содержимого E&F;
- хотфикс позже → ремап на `building_construction_sector` отменён, E&F снова создаёт `building_ef_private_construction`, который компач отключил (`potential = { always = no }`) → стартовые сектора просто не создаются.

Масштаб потери у копии компача относительно текущего E&F:

| | E&F 4.07.2026 | копия в компаче |
|---|---|---|
| строк | 4222 | 2628 |
| `add_company` | 76 | 52 |
| `create_building` | 218 | 135 |
| `building_ef_private_construction` | 28 | 18 (уже как `construction_sector`) |

24 страны теряют исторические компании, 83 стартовых здания не создаются.

---

## 3. GUI: конфликт E&F ↔ PSC, компачем не закрыт

`compare_gui_names.py --a E&F --b PSC` — пересечение по именам виджетов, **при том что пути файлов разные**:

| виджет | E&F | PSC |
|---|---|---|
| `construction_panel` | `gui/construction_panel.gui` (1311 стр.) | `gui/PSC_construction_panel.gui` (1216 стр.) |
| `construction_queue_pages`, `construction_sector_or_no_sector`, `domestic_queue`, `mutual_pact`, `one_way_pact`, `overlord`, `tutorial_highlight_supply_ship_construction` | там же | там же |
| `state_panel_types::state_panel_buildings_content` | `gui/states_panel_buildings.gui` + `ef_dev_and_custom_windows/maj/NonEssential/` | `gui/PSC_states_panel_buildings.gui` |
| `state_panel_types::state_panel_buildings_fixed_bottom` | там же | там же |
| `urban_building_list` | там же | там же |
| `tutorial_highlight_name` | `gui/budget_panel.gui` | `gui/shared/PSC_construction_spending_options.gui` |

Что каждый мод правит (диффы к ванили, без учёта пробелов):

- E&F в `construction_panel`: +99 строк — блок `pcs_or_no_pcs` (панель частного строительства E&F);
- PSC в `construction_panel`: правит район `construction_sector_or_no_sector` (строки ~988–1025) и добавляет регулятор `construction_spending_level` (кнопки ±, Shift/Ctrl) и вывод `government_construction_spending`;
- обе копии одинаково **потеряли** ванильный блок decommission supply ships (строки 229–261) — то есть обе сняты с более старой ванили. Отдельно проверить, вернулся ли этот блок в 1.13.10 ваниль; если да — у обоих модов это уже баг.

Компач не содержит ни одного `.gui`. Значит один из модов проигрывает целиком: при порядке PSC → E&F выигрывает E&F, и **регулятор расходов PSC (её ключевой элемент интерфейса) из панели строительства исчезает**, вместе со списком локальных товаров в панели штата. Симптом «минус сотни строк, плюс две-три» тут не про количество — оба файла ~1200–1300 строк, но области правок разные и просто не складываются.

Нужен собственный merged `gui/construction_panel.gui` и `gui/states_panel_buildings.gui` в компаче: ваниль 1.13.10 + блок E&F + блок PSC. Разбирать построчно.

---

## 4. Пофайловый разбор компача (Анализ 3)

### Живо и по делу — оставить как есть

| файл | статус |
|---|---|
| `script_values/zz_pb_ef_psc_scope_fix.txt` | **актуален**. PSC 1.3.7 в `PSC_construction_values.txt` по-прежнему вызывает `b:building_construction_regulator = { … }` без гварда `has_building`. Спам `has_active_production_method [ Wrong scope for trigger: none, expected building ]` сохраняется. Патч минимальный, один ключ. |
| `script_values/zz_pb_ef_remap_pcs_values.txt` | ядро компача. Ремапит 5 значений E&F на `building_construction_sector`. Три из них (`_lvl_state`, `_lvl`, `_lvl_to_build`) существуют в E&F, `pcs_construction_sector_headroom_by_base_rate` — своё. Бонусом чинит `rarity_factor` E&F, который считает через `building_ef_private_construction_lvl` — ремап покрывает его автоматически, отдельного патча не нужно. |
| `scripted_effects/zz_pb_ef_remap_pcs_effects.txt` | E&F по-прежнему зовёт `building_ef_private_construction_modifier = yes` из `00_on_action_main.txt:291`, определение живёт в `09_introduction_building_lvl.txt:22922`. Ремап актуален. |
| `buildings/zz_pb_ef_investment_score_patch.txt` | `INJECT:` в `building_financial_district`, аддитивно, чисто. Старая запись `bg_ef_private_construction_score` от E&F остаётся, но группа пустая → score 0. Безвредно. |
| `modifier_type_definitions/zz_pb_ef_psc_construction_mult_modifier_types.txt` | нужен: PSC определяет только `_add`, а `overbuilt_economy_modifier` требует `_mult`. |
| `static_modifiers/zz_pb_ef_overbuilt_economy_modifier_patch.txt` | замысел корректный (знаки объяснены в комментарии). Но работает только вместе с исправным `speculative_share_13_button` — см. ниже. |
| `script_values/zz_pb_ef_ai_construction_values.txt` | своё, конфликтов нет. |
| `production_methods/zz_pb_ef_construction_pm.txt` | **совпадает с PSC 1.3.7 строка в строку**, кроме добавленного `goods_output_manufacture_stock_add`. Дрейфа нет. Но это 4 полных `REPLACE:` — при следующем изменении PSC (цифры входа/занятости) компач молча откатит их. Проверять при каждом апдейте PSC. |

### Не работает / устарело — чинить

**4.1. `speculative_share_13_button` не отремаплен — механика «сдувания пузыря» мертва.**

E&F определяет его дважды: `common/scripted_buttons/00_ef_buttons.txt` и `common/scripted_guis/00_financial_scripted_guis.txt`. В обоих:

```
random_scope_state = {
    limit = { has_building = building_ef_private_construction }
    remove_building = building_ef_private_construction
}
```

Здание компачем отключено (`potential = { always = no }`), значит `has_building` никогда не истинно → сектор никогда не сносится → `speculative_share_2` не падает, «Overbuilt Economy» не сдувается. Это ровно то, что README обещает как работающее.

**4.2. Компач патчит только `common/scripted_buttons/`, но не `common/scripted_guis/`.**

E&F дублирует `speculative_share_9..13_button` в двух БД. Компач переопределяет 9–12 только в `scripted_buttons`. Версии в `scripted_guis` (`is_valid` вместо `possible`, есть `ai_chance = 1000`) остались нетронутыми и по-прежнему делают `start_privately_funded_building_construction = building_ef_private_construction` — то есть ИИ-ветка спекуляции ничего не строит.

**4.3. Компач откатывает намеренное решение E&F.**

Текущий E&F в `00_ef_buttons.txt` для кнопок 9–12:

```
visible = { var:speculative_share_1 = 0   var:speculative_share_2 = 0   is_ai = yes }
```

то есть кнопки сделаны **только для ИИ**. Копия в компаче ставит `visible = { var:speculative_share_1 < 20 }` — старое поведение, кнопки снова видны игроку. Надо решить сознательно, а не унаследовать по недосмотру.

**4.4. `scripted_effects/zz_financial_scripted_effects.txt` — самая тяжёлая проблема.**

Два ключа:

- `economic_crisis_consequences` — **побайтово совпадает с E&F**, отличается только префиксом `REPLACE_OR_CREATE:`. Чистый мусор, удалить.
- `establish_bank_and_ef_compagnie` — **3713 строк против 9659 у текущего E&F**. E&F вырос в 2.6 раза. Компач откатывает ~6000 строк: банковские компании и стартовые сектора для доброй половины стран (в E&F 77 блоков `create_building = building_ef_private_construction` с `add_ownership`, в копии компача — заметно меньше).

**4.5. `journal_entries/zz_ef_financial_center_je.txt` — 217-строчный `REPLACE:` ради одной правки.**

Единственное содержательное отличие от E&F — клемп:

```
set_variable = { name = speculative_share_2 value = { value = var:speculative_share_2 max = 100 } }
```

Побочно теряется:

- два блока `widget = { … widget_je_ef_fc_fso_situation / widget_je_ef_pcs_fso_situation … }`, добавленных E&F;
- `scripted_button = speculative_share_13_button`;
- `should_be_pinned_by_default_uninvolved_or_context` заменён на устаревшее `should_be_pinned_by_default`.

По твоему же правилу — заменить аддитивным `on_action` на `on_monthly_pulse_country` в `common/on_actions/` (`on_actions` аддитивны), который делает только клемп. Минус 217 строк копипасты и минус зависимость от версии JE. Помнить про парный вызов из `history/global/` для первого года, если клемп должен работать сразу.

**4.6. `company_types/00_ef_companies.txt` — полное перекрытие файла (181 КБ).**

Смысловых правок мало (замена `building_ef_private_construction` → `building_construction_sector` в `building_types` и `ai_construction_targets`), остальное — пробелы. Но перекрытие по пути = файл E&F не читается вообще. Сейчас дрейф небольшой (~132/133 строки диффа, в основном пробелы), но это мина: любая новая компания в E&F пропадёт молча.

**4.7. Локализация: 11 полных перекрытий `01_ef_je_localization_l_*.yml`.**

Для english: E&F 241 ключ, копия компача 178. **73 ключа теряются**, в том числе `fc_fso_situation`, `current_situation`, `active`, `critical`, `*_bankruptcy_*`, `currency_crisis_*` — ровно те, что нужны новым виджетам JE из п. 4.5. Собственных ключей у компача всего 10 (`goods_output_*_construction_mult[_desc]`, `concept_maximum_pcs_capacity_desc`, `concept_building_urban_center_lvl_by_base_rate_desc`), изменённых — 15 (english) / 148 (russian, там своя правка перевода).

Лечится тривиально: не класть файл по пути E&F, а сделать `localization/<lang>/zz_ef_psc_je_l_<lang>.yml` только с 10 новыми + нужными изменёнными ключами. Последний загруженный ключ выигрывает, остальные 73 остаются от E&F.

**4.8. `scripted_effects/zz_ai_strategies.txt` — мёртвый файл.**

`ai_buy_building_gold_mine_2` не определён и не вызывается **нигде**: ни в ванили, ни в E&F 4.07.2026, ни в PSC. `$FC_SIZE$` в теле — след старой версии E&F (сейчас параметр живёт в `initialize_historic_macro_facilities_fc` / `financial_center_respawn_after_crisis`). Удалить целиком.

**4.9. `production_methods/zz_pb_ef_point_conversion_ui.txt` — косметика ценой 4 полных копий PM.**

Единственное отличие от PSC 1.3.7 — `texture` (иконка `construction_bureaucrats.dds` заменена на иконки строительных методов). Ради иконки продублированы четыре PM, которые придётся синхронизировать при каждом апдейте PSC. Плюс `REPLACE:` вместо `REPLACE_OR_CREATE:` — если PSC отключат, четыре ошибки в лог. Либо оставить с явным комментарием «синхронизировать с PSC», либо выкинуть.

### Не про PSC вообще — вынести в хотфикс

Три файла чинят баги E&F, никак не связанные с PSC. Им место в `_ef/ef hotfix 1.13`, а не в компаче:

- `script_values/zz_pb_ef_ef_div0_fix.txt` — деление на `building_financial_num` и `base_demande_*_fix`, которые бывают нулём;
- `scripted_effects/zz_pb_ef_ef_currency_scope_guard_fix.txt` — гварды `exists = scope:seller` / `exists = scope:central_bank_site` в `sell_currency_privat_bank`. **Проверено: в E&F 4.07.2026 гвардов по-прежнему нет, фикс актуален**;
- `history/global/zz_pb_ef_init_ef_stockpiling_state_vars_fix.txt` — инициализация `stockpiling_*_var_state_1`. Внутри дублирование: верхний `every_scope_state` уже покрывает все штаты, вложенный `every_country = { every_scope_state = { … } }` — та же работа второй раз.

Побочный эффект переноса: тот, кто ставит E&F + PSC, эти фиксы получит только вместе с хотфиксом — а хотфикс всё равно обязателен из-за потолка товаров (п. 1).

### Не покрыто, но, похоже, и не надо

- `building_ef_private_construction_max_level` (static_modifier) и `state_building_ef_private_construction_max_level_add` — вешаются на мёртвое здание. Их роль (потолок уровней) компач берёт на себя через `can_build_private` в `zz_pb_ef_construction_sector.txt`. Проверить в игре, что потолок реально работает: `can_build_private` считается вне скоупа здания, комментарий в файле это оговаривает.
- `building_ef_private_construction_max_level_var` — считает от `var:gdp_view_fc`, здание не упоминает. Трогать не надо.

---

## 5. Мелочи

- 14 из 15 `.txt` компача **без BOM** (все ASCII, так что сейчас безвредно, но правило есть правило). Баланс скобок — 0 во всех файлах, порядок.
- `.metadata/metadata.json` компача: `version 1.12.2`, `supported_game_version "1.12.*"`, `tested_with` — E&F v4.1.1 / PSC 1.3.5. Обновить на 1.13.10, PSC 1.3.7, E&F 04.07.2026 и добавить зависимость от хотфикса.
- `BED_TRIP's MEGAPACK.json` тоже на 1.12 и без хотфикса; в `__megapacks/megapack/.metadata` то же самое. Отдельная задача.
- `zz_pb_ef_construction_sector.txt` не разошёлся с PSC 1.3.7 по существу: у PSC в `ai_value` нет блока «Kickstart первого сектора в столице» и `ai_construction_sector_price_pressure_bonus` — это добавки компача. Остальное совпадает. Но `REPLACE:` полного здания придётся сверять при каждом апдейте PSC.

---

## 6. Что делать, по убыванию важности

1. **Потолок товаров.** Прописать `E&F 1.13.10 Hotfix` (`3786286962`) зависимостью в `.metadata/metadata.json` и первой строкой в разделе Load order в README. Без него E&F + PSC = 130 товаров = вылет без лога.
2. **Развести компач и хотфикс по `common/history/buildings/00_ef_building.txt`.** Проще всего — пересобрать копию компача из **хотфиксовой** версии (она же актуальный E&F + 2 правки) механической заменой имени здания, и завести для этого скрипт в `tools/`, чтобы шаг был воспроизводимым. Либо: не отключать `building_ef_private_construction` полностью (оставить `potential`, убрать PM и `buildable`), тогда `create_building` из истории E&F отработает вхолостую и перекрытие файла станет не нужным — но это надо проверить в игре, здание без единой PM-группы может не инстанцироваться.
3. **`speculative_share_13_button`** — ремапить в обеих БД (`scripted_buttons` и `scripted_guis`), иначе пузырь не сдувается.
4. **`speculative_share_9..12_button` в `common/scripted_guis/`** — ремапить (сейчас ИИ строит несуществующее здание).
5. **`establish_bank_and_ef_compagnie`** — пересобрать из текущего E&F (9659 строк) или отказаться от перекрытия по схеме из п. 2.
6. **JE `financial_center_je_2`** — заменить 217-строчный `REPLACE:` на аддитивный `on_action`, делающий только клемп `speculative_share_2 ≤ 100`.
7. **Локализация** — 11 перекрытий по пути заменить на `zz_ef_psc_je_l_*.yml` только с нужными ключами.
8. **Удалить** `scripted_effects/zz_ai_strategies.txt` (мёртвый ключ) и `economic_crisis_consequences` из `zz_financial_scripted_effects.txt` (идентичен E&F).
9. **GUI** — собрать merged `construction_panel.gui` и `states_panel_buildings.gui` (ваниль 1.13.10 + блок E&F + блок PSC).
10. **Вынести** три E&F-фикса (`div0`, `currency scope guard`, `init stockpiling vars`) в `ef hotfix 1.13`.
11. **`company_types/00_ef_companies.txt`** — пересобрать из текущего E&F; в идеале скриптом.
12. BOM в 14 `.txt`; `.metadata/metadata.json` на 1.13.

---

## 7. Чеклист проверки в игре (по убыванию риска)

| # | что | как проверить | годно / не годно |
|---|---|---|---|
| 1 | Запуск со всей связкой (E&F + PSC + хотфикс + компач) | новая игра, вход в кампанию | не вылетает при входе — **годно**; мгновенный вылет без строк в `error.log` → упёрлись в потолок товаров |
| 2 | `error.log` первые 30 сек | искать `Wrong scope for trigger: none, expected building`, `Failed to fetch variable`, `Invalid left side during comparison 'var'` | чисто — **годно** |
| 3 | Панель строительства | открыть; смотреть одновременно регулятор `construction_spending_level` (PSC) **и** блок `pcs_or_no_pcs` (E&F) | оба на месте — **годно**; один пропал → GUI-конфликт п. 3 |
| 4 | Панель штата | список локальных товаров (`wood_construction` и т.д.) в блоке зданий | список есть — **годно** |
| 5 | Стартовые здания и компании | Пруссия / США / Франция 1836: наличие исторических компаний E&F и стартовых `building_construction_sector` | компании на месте — **годно**; пусто → сработала стальная копия `00_ef_building.txt` |
| 6 | Порядок компач ↔ хотфикс | `STATE_LOWER_ANDALUSIA` существует; нет зданий в NULL-штате в логе | **годно** |
| 7 | Строительство работает | построить сектор, проверить выпуск `*_construction` и рост `country_construction` через регулятор | **годно** |
| 8 | E&F видит сектор | JE Financial Center: счётчик частного строительства меняется при постройке `building_construction_sector` | реагирует — **годно** |
| 9 | Пузырь надувается | довести `speculative_share_2` > 0, увидеть `overbuilt_economy_modifier` на секторах | висит — **годно** |
| 10 | Пузырь **сдувается** | дождаться срабатывания `speculative_share_13_button` у ИИ | сектор сносится, `speculative_share_2` падает — **годно**; стоит на месте → п. 4.1 подтверждён |
| 11 | Клемп 100% | `speculative_share_2` не уходит выше 100 | **годно** |
| 12 | Потолок секторов | строить сверх `building_urban_center_lvl_by_base_rate` | кнопка блокируется — **годно**; строит без ограничения → `can_build_private` не работает вне скоупа здания |
| 13 | Иконки PM конверсии | панель регулятора | иконки дерева/железа/стали — **годно** (косметика) |
| 14 | Локализация JE | открыть Financial Center JE | нет `MISSING`/сырых ключей — **годно** |
