### Результат проверки конфликтов PBE → BPM (BPM грузится последним)

- **Жёсткие конфликты (одинаковый относительный путь файла)**: **0**
  - Значит **нет** файлов, которые BPM напрямую перетирает поверх PBE (и наоборот) по одному и тому же пути.
- *`common/*` (эвристика по top-level ключам)**: найдено **3 пересечения**
  - *`common/on_actions`**
    - `on_monthly_pulse_country` — есть и в PBE, и в BPM (и причём BPM определяет его в нескольких своих файлах)
    - `on_wargoal_enforced` — есть и в PBE, и в BPM
  - *`common/modifier_type_definitions`**
    - `state_bureaucrats_investment_pool_efficiency_mult` — у BPM это `REPLACE:...`, у PBE обычное определение; по содержимому блоки выглядят **идентично**.
- **Локализация (duplicate loc keys)**: **0**
- **События (duplicate event id)**: **0**
- **GUI-коллизии по именам/типам (эвристика)**: **0**

### Где лежат отчёты

- Авто-отчёт: `bpm_pbe/conflicts_pbe_vs_bpm_report.md`
- GUI-проверка: `bpm_pbe/gui_ids_pbe_vs_bpm.txt`
- Моя ручная фиксация выводов: `bpm_pbe/conflicts_pbe_vs_bpm_reviewed.md`

Если хочешь, дальше сразу начну собирать каркас компача в `bpm_pbe` (metadata/структура) и добавлю “страховочный” мердж для `on_actions` (на случай если в будущем появится мод, который перезаписывает их неаддитивно).