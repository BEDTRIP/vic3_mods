# E&F + BPM — сводка конфликтов (load order: **E&F → BPM**)

Цель: подготовить основу для компача между:
- **E&F**: `@.E&F/e&f`
- **E&F topbar framework**: `@.E&F/expanded_topbar_framework`
- **BPM**: `@.BPM`

Порядок загрузки по условию: **E&F сначала, BPM последним** (значит при конфликте “по ключу/типу” чаще выигрывает BPM).

## Что я прогнал автоматически

Авто-отчёты (эвристика, но хорошо ловит реальные “перетирания” через `REPLACE*`):
- `bpm_mr/conflicts_ef_vs_bpm_report.md` — **E&F (e&f) vs BPM**
  - **0** совпадений по пути файла (hard overwrite)
  - **15** дублей top-level ключей в `common/**`
  - **58** дублей ключей локализации
  - **0** дублей `event id`
- `bpm_mr/conflicts_ef_topbar_vs_bpm_report.md` — **topbar framework vs BPM**
  - пересечений не найдено

Доп. проверка (важно для Windows/FAT/NTFS): **case-insensitive** совпадений путей файлов между `e&f` и `BPM` тоже **0**.

GUI-эвристика (по `*.gui`): пересечения минимальные:
- `name` совпадения: `ideologies_box`, `traits_box` (оба в тултипе IG)
- `type` совпадение: `pinnable_outliner_items::interest_group_item`

## Подтверждённые конфликты E&F ↔ BPM (реально перетирают смысл)

### 1) `common/ideologies/*`: BPM `REPLACE:` сносит E&F `INJECT:` (монетарные предпочтения)

Ключи:
- `ideology_hierarchic`
- `ideology_laissez_faire`
- `ideology_liberal`
- `ideology_meritocratic`
- `ideology_paternalistic`
- `ideology_populist`
- `ideology_proletarian`
- `ideology_reactionary`
- `ideology_socialist`

Файлы:
- E&F: `common/ideologies/00_ef_ig_ideologies.txt` — **`INJECT:`** добавляет блоки `lawgroup_monetary_system = { ... }` в ванильные идеологии.
- BPM: `common/ideologies/zz_00_ig_ideologies.txt` — **`REPLACE:`** пересоздаёт эти идеологии (в основном задаёт `icon = ...`).

Итог при порядке **E&F→BPM**: E&F-инжекты по монетарному закону **пропадают**, потому что BPM делает полный `REPLACE:...`.

Что делать в компаче: после BPM повторить E&F-инжекты (в отдельном файле компача в `common/ideologies/`).

### 2) `common/technology/technologies`: `currency_standards` — оба делают `REPLACE:`

Ключ:
- `currency_standards`

Файлы:
- E&F: `common/technology/technologies/ef_technology.txt` — `REPLACE:currency_standards` (era=2, `unlocking_technologies = { banking }`, `on_researched` активирует `law_fiat_standard` и т.п.)
- BPM: `common/technology/technologies/zzzz_bpm_technologies_important.txt` — `REPLACE:currency_standards` (era=1, `unlocking_technologies = { international_trade centralization }`, свои модификаторы)

Итог при порядке **E&F→BPM**: BPM-версия `currency_standards` **перетирает** E&F-версию (а для E&F это ключевая часть финансовой системы).

Что делать в компаче: сделать собственный `REPLACE:currency_standards`, который **сохраняет E&F логику** (особенно `on_researched`/активацию закона) и при желании включает элементы BPM (например prereq/era/модификаторы) — это ручное решение по балансу.

## Пересечения, которые чаще всего аддитивны, но требуют внимания (на случай “не мерджится”)

### 3) `common/on_actions`: одинаковые ключи пульсов

Ключи:
- `on_monthly_pulse_country`
- `on_half_yearly_pulse_country`
- `on_yearly_pulse_country`
- `on_five_year_pulse_country`

Файлы:
- E&F: `common/on_actions/00_ef_on_action.txt`
- BPM: несколько файлов в `common/on_actions/*` (например `BPM_code_on_actions.txt`, `BPM_CAB_on_actions.txt`, `bpm_republic_on_actions.txt` и др.)

Обычно `on_actions` в Vic3 **мерджатся** (в таком случае всё ок), но если в вашей версии/сборке вдруг окажется “последний победил”, то E&F потеряет свои ежемесячные/годовые хуки (финансовые пересчёты).  
Страховка для компача: после BPM **добавить** `ef_on_*` в соответствующие `on_*_pulse_country` списки.

### 4) `common/history/global`: `GLOBAL`

Файлы:
- E&F: `common/history/global/00_ef_*_global_variable.txt` (инициализация множества переменных)
- BPM: `common/history/global/00_bpm_global.txt` и другие `zz*.txt` (свои эффекты)

Как правило, такие блоки тоже **сосуществуют**, но это место стоит держать в уме при отладке.

## Локализация (58 дублей ключей)

Тут в основном пересекаются **ванильные UI/контент-ключи** (например `ENACT_LAW`, `LOYALISTS_TOOLTIP`, `communism.1.*`, `meiji.*` и т.д.).  
При порядке **E&F→BPM** эти ключи будут браться из BPM для тех языков, где BPM их определяет/replace’ит.

