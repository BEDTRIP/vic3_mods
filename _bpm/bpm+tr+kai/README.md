### Что я сделал и где лежит результат

- Прогнал `tools/scan_conflicts.py` по всем парам модулей **T&R / KAI / CMF** (из `@.TechRes+Kuromi`) и **@.BPM**.
- Дополнительно **вручную перепроверил** самые важные найденные пересечения (особенно где `REPLACE` vs `INJECT`).

Все отчёты сохранены в папку `bpm_tr/`:

- `bpm_tr/conflicts_master.md` — **сводный список конфликтов + ручные пометки**
- `bpm_tr/conflicts_tr_vs_kai.md`
- `bpm_tr/conflicts_tr_vs_cmf.md`
- `bpm_tr/conflicts_kai_vs_cmf.md`
- `bpm_tr/conflicts_tr_vs_bpm.md`
- `bpm_tr/conflicts_kai_vs_bpm.md`
- `bpm_tr/conflicts_cmf_vs_bpm.md`

### Главный итог по “всем папкам, не только common”

- **Жёстких конфликтов по путям файлов нет**: во всех сравнениях `file path overlaps = 0`.
  - Это означает, что **ни в `common/`, ни в `events/`, ни в `gui/`, `gfx/`, `localization/` и т.д. нет одинаковых относительных путей файлов**, которые бы перезаписывались по порядку загрузки.

### Реальные конфликты (по ключам/объектам), которые точно важны

Полный список с деталями — в `bpm_tr/conflicts_master.md`. Коротко самое критичное:

- **T&R ↔ KAI**
  - `common/script_values`: `wanted_army_size_script_value`, `wanted_navy_size_script_value` — **оба `REPLACE` ⇒ реальный конфликт** (что загрузится позже, то и победит).
  - `common/ai_strategies` и часть `technology` — оба чаще `INJECT` (мягкое пересечение).
- **T&R ↔ BPM (BPM последний)**
  - `common/journal_entries`: `je_strike` — **оба `REPLACE**`, при этом BPM **отключает** ванильный `je_strike` и вводит свою систему general strike ⇒ дизайн-конфликт.
  - `common/laws`: `law_industry_banned` — **оба `REPLACE**`, BPM затирает расширенный “снос” T&R late-game зданий (я это руками сравнил).
  - `common/technology`: `feminism`, `mass_propaganda` — **оба `REPLACE` ⇒ реальный конфликт**.
  - `common/production_methods`: пересечение большое, но в основном **T&R `REPLACE` vs BPM `INJECT**` (BPM добавляет `disallowing_amendments`) — обычно совместимо, но это всё равно зона для проверки в компаче.
- **KAI ↔ BPM (BPM последний)**
  - `common/laws`: KAI часто `INJECT` (AI-веса), BPM `REPLACE` ⇒ **правки KAI теряются без компача**.
  - `common/ai_strategies`: KAI `INJECT`, BPM `REPLACE` ⇒ **правки KAI теряются**.
  - `common/defines`: оба задают `NAI = { ... }` с пересекающимися ключами и разными значениями ⇒ **реальный конфликт**.
- **CMF ↔ BPM (BPM последний)**
  - `common/parties`, `common/political_movements`, часть `common/laws` — BPM в основном **заменяет** (REPLACE/переопределение) ⇒ реальный конфликт.
  - `common/scripted_triggers` (типа `com_is_active`, `morgenrote_is_active`) — дубликаты **эквивалентны** `always = no`), не критично.

Если хочешь — дальше сразу перейду к следующему шагу: на основе `conflicts_master.md` начнём собирать компач в `bpm_tr/` (с приоритетом `defines/laws/ai_strategies/tech/je`).