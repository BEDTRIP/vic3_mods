# Morgenröte + The Great Revision — компач не нужен

**Дата проверки:** 2026-08-21
**Версии:** MR `2.8.3e Mitsopoulos` (`supported_game_version` 1.13.*, зависимость — CMF 1.*) · TGR `2.0` (`supported_game_version` 1.13.10, relationships пусты)
**Вывод:** конфликтов нет. Папка остаётся `noneed`, компач не собираем.

---

## 1. Пересечение по путям файлов

MR — 8210 файлов, TGR — 907. **Общий путь ровно один:**

```
gfx/interface/icons/production_method_icons/aeroplanes.dds
```

Оба мода перекрывают ванильную иконку PM. Победит тот, что ниже в порядке загрузки; на игру не влияет — иконка, не виджет и не запись БД. Патчить нечего.

Отдельно проверено, **какие ванильные файлы каждый мод перекрывает целиком** (самый грубый инструмент, из-за которого обычно и ломается):

* TGR — 496 файлов, из них содержательных немного: `common/buy_packages/00_buy_packages.txt`, все 12 `common/parties/*.txt`, 14 файлов `common/history/countries/*`, `common/decisions/manifest_destiny.txt`, `gui/budget_panel.gui`, `localization/languages.yml`. Остальное — `.dds` (иконки законов и PM).
* MR — 19 файлов: `common/achievement_groups.txt`, `common/history/characters/par - parma.txt`, `events/natural_disasters_events.txt`, `gui/error_deer.gui` и `.dds`/`.asset`.

**Пересечения множеств «перекрытая ваниль» у MR и TGR — нет** (кроме той же `aeroplanes.dds`). То есть ни один мод не откатывает ванильный файл, который правит другой.

## 2. Пересечение по ключам (`scan_conflicts.py`)

```
common_categories_intersection = 29   common_key_dups = 99
loc_key_dups = 0                      event_id_dups = 0
```

99 «дублей» разбираются на четыре безобидные группы:

### 2.1 `common/buy_packages` — 90 ключей `wealth_10..wealth_99`

Не конфликт: **MR пишет через `TRY_INJECT:`**.

* TGR: `common/buy_packages/00_buy_packages.txt` — полная замена ванильного файла, `wealth_1..wealth_99` переписаны (перебалансировка еды/напитков на высоких уровнях благосостояния).
* MR: `common/buy_packages/mr_buy_packages.txt` — 90 записей вида `TRY_INJECT:wealth_NN = { goods = { popneed_entertainment = X } }`.

`INJECT:` дописывает в список, а не заменяет → `popneed_entertainment` ложится поверх пакета TGR. Порядок парсинга внутри каталога тоже в нашу пользу: `00_buy_packages.txt` < `mr_buy_packages.txt` по алфавиту, значит цель инжекта к моменту инжекта уже существует, независимо от порядка модов в плейсете.

### 2.2 `common/pop_needs` — пересечения нет вообще

* MR: добавляет свой `popneed_entertainment`, `TRY_INJECT` в `popneed_free_movement`, `popneed_luxury_items`, `popneed_leisure`.
* TGR: `REPLACE_OR_CREATE` для `popneed_basic_food`, `popneed_luxury_food`, `popneed_luxury_drinks`, `popneed_intoxicants`, `popneed_crude_items`, `popneed_simple_clothing`, `popneed_household_items`, `popneed_heating`.

Списки не пересекаются ни в одном ключе.

### 2.3 `common/technology/technologies` — 3 ключа (это ново с прошлой сверки)

`atmospheric_engine`, `civilizing_mission`, `malaria_prevention` — раньше их в отчёте не было, TGR 2.0 стал их трогать.

```
MR  a_vanilla_production_technologies.txt : TRY_INJECT:atmospheric_engine
MR  a_vanilla_society_technologies.txt    : TRY_INJECT:civilizing_mission , TRY_INJECT:malaria_prevention
TGR TGR_POLITICS_production.txt           : INJECT:atmospheric_engine
TGR TGR_POLITICS_society.txt              : INJECT:civilizing_mission , INJECT:malaria_prevention
```

**Оба мода инжектят, ни один не реплейсит** → оба набора эффектов техов доедут. Это единственное новое пересечение с прошлой проверки, и оно безопасно.

### 2.4 `on_actions`, `GLOBAL`, `BUILDINGS`, `COUNTRIES` — аддитивные категории

* `common/on_actions/`: у MR 27 ванильных on_action в 29 файлах, у TGR — 5 (`on_yearly/monthly/half_yearly_pulse_country`, `on_law_activated`, `on_tax_law_change`). **Ни у одного нет префикса `REPLACE:`** — каталог аддитивен, все хуки складываются.
* `history/global` (`GLOBAL`) и `history/buildings` (`BUILDINGS`) — аддитивны по устройству.
* `history/countries` (`COUNTRIES`) — совпадение только на имени обёртки. По странам пересечения нет: TGR трогает `c:AUS BRZ CHI FRA GBR JAP MEX NET PER SAR SIC SPA SWE TUR`, MR — только `c:RAP` плюс `z_mr_starting_technologies.txt`, который работает через `every_country { add_technology_researched }`, то есть **дописывает**, а не переопределяет блок страны. Имя `z_...` гарантирует парсинг после ванильных/TGR-шных `aus - austria.txt` и т.п., как и задумано автором MR (см. комментарий в шапке файла).

## 3. Что скрипт не ловит — проверено вручную

| Проверка | Результат |
|---|---|
| **Потолок 128 товаров** | ваниль 53 + MR 5 (`air_travel`, `good_uranium`, `elgar_instruments`, `elgar_music`, `manzoni_prints`) + TGR 0 новых = **58**. TGR только `REPLACE_OR_CREATE`-ит все 53 ванильных (цены/категории), своих не заводит. Запас огромный. |
| **Группы законов** | у MR каталогов `common/laws`, `common/law_groups`, `common/institutions`, `common/interest_groups`, `common/defines` **нет вообще**. TGR перестраивает 37 law_groups и все 8 IG — резать нечего, MR туда не лезет. |
| **Идеологии** | MR не добавляет ни одной идеологии (три «ключа» в `common/ideologies` — артефакт разбора, это sgui-кнопки сайдбара). Значит нет ситуации «идеология MR без позиции по новым law group TGR». |
| **Триггеры по building_group** | TGR `REPLACE_OR_CREATE`-ит четыре группы: `bg_trade`, `bg_consumer_goods`, `bg_industry_heavy`, `bg_industry_light`. Собственные группы MR — `bg_opera` (→`bg_arts`), `bg_architect` (→`bg_public_infrastructure`), `bg_uranium_mining` (→`bg_mining`), `bg_dubois_national_park` (→`bg_government`). Ни один `parent_group` MR не указывает на переопределённую TGR группу. Здания MR в `bg_light_industry` наследуют параметры TGR через цепочку родителей — это и есть желаемое поведение, патч не нужен. |
| **PM / PMG** | пересечений по ключам ноль. TGR переписывает PM торговли/инвесторов, MR инжектит в другие ванильные PM и PMG. `TRY_REPLACE:pm_sulfite_pulping` (MR) TGR не трогает. |
| **Компании** | MR 66 своих, TGR 20 (`REPLACE_OR_CREATE` ванильных) — общих ключей нет. Единственный эффект стыковки — конкуренция за AI-веса, это баланс, а не поломка. |
| **`.gui`** | общих `.gui`-файлов у модов нет. TGR перекрывает только `gui/budget_panel.gui`, MR — только `gui/error_deer.gui` и свои `mr_*.gui`. Виджеты MR все под префиксом `mr_`, коллизий имён нет. |
| **Локализация** | 0 общих ключей. |
| **ID событий** | 0 общих. |

## 4. Побочные находки (к компачу не относятся, но записаны, чтобы не искать заново)

Обе — по классу «устаревшая копия ванильного `.gui`», обе **воспроизводятся и без второго мода**.

**TGR, `gui/budget_panel.gui`** (2336 строк против ванильных 2112, то есть не «обрезанная копия», а честно переписанная). Пропали четыре ванильных имени:

```
bankruptcy_progress_bar · bankruptcy_progressbar · declare_bankruptcy_button · tutorial_highlight_tax_level
```

Три первых нигде больше не упоминаются — судя по всему, кнопка банкротства убрана намеренно под систему займов TGR. А вот `tutorial_highlight_tax_level` **ссылается ванильный** `common/tutorial_lessons/00_tutorial_lessons_budget_balance.txt`. То есть урок туториала по бюджету будет искать несуществующий виджет. Проверять только при включённом туториале.

**MR, `gui/error_deer.gui`** — 73 строки против ванильных 148, потеряны `debug_speed_data`, `debug_current_fps`, `low_fps_warning`, `tick_task_speeds`. Классический признак («минус сотни строк, плюс две-три»), но весь файл висит под `visible = "[And(InDebugMode, ...)]"`, поэтому в обычной игре не всплывает.

Ни то, ни другое компачем MR+TGR не чинится — это правки в сторону авторов модов.

## 5. Чеклист проверки в игре

Смысл — не искать конфликт (его нет), а подтвердить, что стык не разъехался. По убыванию риска.

1. **Запуск с обоими модами** — доходит до карты, `error.log` без новых `unknown key` по `wealth_*`, `popneed_*`, `bg_*`. → годно / не годно
2. **Панель бюджета TGR** открывается, ползунки пяти налогов работают, MR-сайдбар (Arts/Science/Sports) рядом жив. → годно / не годно
3. **Потребление**: у попа wealth 20+ в списке нужд есть и `popneed_entertainment` (MR), и перебалансированные TGR еда/напитки одновременно. Это прямая проверка, что `TRY_INJECT` лёг поверх замены TGR. → годно / не годно
4. **Технологии** `atmospheric_engine`, `civilizing_mission`, `malaria_prevention` — в тултипе видны эффекты и от MR, и от TGR. → годно / не годно
5. **Здания MR в лёгкой промышленности** (`building_instrument_workshops`, `building_manzoni_publishing_industry`) строятся, показывают параметры перестроенной TGR `bg_industry_light`. → годно / не годно
6. **Trade Center** TGR строится и AI его ставит; MR-здания в списке постройки не пропали. → годно / не годно
7. **Старт за Австрию / Британию / Китай** (TGR переписывает их history) — стартовые техи MR выданы. → годно / не годно
