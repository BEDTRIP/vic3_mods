# PBE → BPM (BPM last) — ручная проверка конфликтов

Контекст: моды будут грузиться в порядке **PBE**, затем **BPM** (BPM последний и “побеждает” при перезаписи).

Сгенерированные отчёты:
- `bpm_pbe/conflicts_pbe_vs_bpm_report.md` — авто-отчёт (пересечения путей файлов + эвристика по `common/*.txt`, локализации и event id).
- `bpm_pbe/gui_ids_pbe_vs_bpm.txt` — эвристическая проверка коллизий GUI `name = "..."`, `icon = ...`, `types ... { type ... = ... }`.

## 1) Жёсткие конфликты по пути файла (hard overwrite)

По авто-отчёту: **0** пересечений относительных путей файлов.

Вывод: **нет ситуаций**, когда BPM напрямую перетирает файл PBE (или наоборот) по одинаковому пути.

## 2) `common/on_actions/*` — дубликаты ключей on_action

Авто-сканер нашёл 2 “дубликата” top-level ключей:

- **`on_monthly_pulse_country`**
  - PBE: `common/on_actions/kates_power_bloc_on_actions.txt`
  - BPM: несколько файлов, включая `common/on_actions/BPM_code_on_actions.txt`, `BPM_CAB_on_actions.txt`, `BPM_bnap_on_actions.txt`, и др.

- **`on_wargoal_enforced`**
  - PBE: `common/on_actions/kates_power_bloc_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`

### Что это значит на практике

BPM **сам** определяет `on_monthly_pulse_country` в нескольких файлах. Если бы движок воспринимал повторное определение как “полный overwrite”, BPM сломал бы сам себя (оставался бы только последний по порядку файл).

Вывод: для `common/on_actions` повторные определения **аддитивно склеиваются** (по крайней мере в рамках BPM), поэтому PBE + BPM **должны сосуществовать**, и эффекты обоих модов должны вызываться.

Риск остаётся только “логический”:
- порядок срабатывания on_actions может отличаться от ожидаемого (обычно не критично);
- если когда-то появится третий мод/компач, который *заменяет* `on_actions` через `REPLACE:`/`REPLACE_OR_CREATE:` (или перезаписывает файл целиком), он может выбить часть поведения.

## 3) `common/modifier_type_definitions/*` — дубликат modifier type

Найден 1 дубликат ключа:

- **`state_bureaucrats_investment_pool_efficiency_mult`**
  - PBE: `common/modifier_type_definitions/kates_power_bloc_modifier_types.txt`
  - BPM: `common/modifier_type_definitions/BPM_functional_modifiers.txt` (как `REPLACE:state_bureaucrats_investment_pool_efficiency_mult`)

Сравнение по содержимому: блоки выглядят **идентично** (decimals=0, color=good, percent=yes, game_data.ai_value=0).

Вывод: даже если BPM заменяет определение через `REPLACE:`, это **не меняет** итоговую форму модификатора относительно PBE → реального конфликта баланса/типа тут нет.

## 4) Локализация и события

По авто-отчёту:
- **duplicate localization keys**: 0
- **duplicate event ids**: 0

## 5) GUI-коллизии (имена/типы)

По `bpm_pbe/gui_ids_pbe_vs_bpm.txt` пересечений нет:
- `name`: 0
- `icon`: 0
- `type`: 0

## Итог

На текущем этапе для пары **PBE → BPM**:
- **жёстких конфликтов файлов нет**;
- единственные пересечения в `common/` — это аддитивные `on_actions` и один `modifier_type`, который совпадает по определению.

Следствие: компач для “устранения конфликтов” между PBE и BPM, скорее всего, **не потребуется** (может понадобиться только для будущих правок/баланс-подстроек или если появятся другие моды в сборке).

