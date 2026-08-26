### Что я нашёл (VC → BPM, BPM последний)

Я прогнал эвристический скан и **дополнительно вручную перепроверил** самые важные места (в т.ч. `events/`, потому что там стандартный сканер пропускает конфликты определений).

**Итог по VC vs BPM:**

- **Жёсткие конфликты (одинаковые пути файлов)**: **6**
- **Пересечения идентификаторов в `common/**` (top-level ключи, эвристика)**: **115** (в 32 категориях)
- **Дубликаты localization keys**: **0**
- **Конфликты определений событий (event definitions)**: **1** (реальный)

### Главные “жёсткие” конфликты (6 одинаковых путей)

(в VC→BPM порядке эти файлы берутся из BPM)

- `common/decisions/manifest_destiny.txt`  
  - VC: `#nothing`  
  - BPM: пустой файл  
  - На практике оба “обнуляют” ванильный файл (низкий риск сам по себе).
- `common/journal_entries/00_peoples_springtime_je.txt`  
  - VC: большой `REPLACE_OR_CREATE:je_springtime_of_the_peoples` (+ `je_red_summer`)  
  - BPM: пустой файл  
  - **Высокий риск**: BPM фактически *удаляет* VC-версию этого ванильного файла и опирается на свою реализацию в `common/journal_entries/BPM_je_peoples_springtime.txt`. Если нужно сохранить VC-логику, её придётся переносить/сливать в BPM-версию.
- `common/history/countries/*.txt` (4 файла)  
  - `brz - brazil.txt`, `chi - china.txt`, `fra - france.txt`, `usa - usa.txt`  
  - **Высокий риск**: BPM заменяет стартовую настройку стран VC (законы/переменные/JE/модификаторы). Эти файлы почти наверняка нужно **сливать вручную**.

### Самые критичные пересечения в `common/**` (что почти точно придётся сливать в компаче)

Полный список — в отчёте, но самые “больные” категории:

- *`common/on_actions` (4 ключа)**: `on_monthly_pulse_country`, `on_yearly_pulse_country`, `on_new_ruler`, `on_diplo_play_war_start`  
Оба мода задают их как полноценные блоки, поэтому легко “вытирают” друг друга. Для компача нужен объединённый `zzzz_*.txt`.
- *`common/journal_entries` (15 ключей)**: пересекаются цепочки Германии/Мэйдзи/Сипаев/Франции + Springtime.
- *`common/interest_groups` (8 ключей)** и *`common/parties` (3 ключа)**: оба мода реально переопределяют базовые сущности.
- *`common/character_templates` (49 ключей)**: одинаковые шаблоны исторических персонажей.
- Плюс важные единичные: `country_formation: GER`, `technology: corporatism`, `defines: NAI`, `ideologies`, `static_modifiers`, `scripted_buttons`, `political_movements`, `dynamic_country_names`, `flag_definitions`.

### Важное: конфликт событий, который стандартный сканер не ловит

Я дополнительно просканировал **определения событий** `victoria.1 = { ... }`), и нашёл реальный конфликт:

- *`victoria.1` определён и в VC, и в BPM**
  - VC: `events/victoria_events.txt`
  - BPM: `events/_victoria_events.txt`

### Куда я положил результаты (в `bpm_vc/`)

- `bpm_vc/conflicts_vc_vs_bpm_report.md` — основной эвристический отчёт (пересечения путей + `common` ключи + loc + “id = …”)
- `bpm_vc/conflicts_vc_vs_bpm_event_definitions.md` — **дубликаты определений событий** (реальный конфликт `victoria.1`)
- `bpm_vc/conflicts_vc_vs_bpm_report_reviewed.md` — **сводка “после ручной проверки”** (что реально критично и что сливать)

Также я добавил маленький вспомогательный сканер:

- `tools/scan_event_definitions.py` (чтобы ловить дубликаты `namespace.id = {}` в `events/*.txt`)

Если ок — следующим шагом можем начинать собирать компач в `bpm_vc/`, начиная с 6 “жёстких” файлов и затем слияния `on_actions`.