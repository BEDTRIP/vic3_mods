# Конфликты TechRes+Kuromi (T&R + KAI + CMF) vs Victorian Century (VC)

Порядок загрузки по задаче: **T&R → KAI → CMF → VC (VC последний)**.

Ниже — “что точно конфликтует” и почему это важно именно при таком порядке. Детальные авто‑отчёты лежат рядом:

- `conflicts_tr_vs_vc_report.md`
- `conflicts_kai_vs_vc_report.md`
- `conflicts_cmf_vs_vc_report.md`
- GUI‑пересечения: `conflicts_tr_vs_vc_gui_ids.txt`, `conflicts_cmf_vs_vc_gui_ids.txt`

## 1) Жёсткие конфликты: одинаковые пути файлов (VC перезапишет CMF)

Найдено **4** совпадения путей (см. `conflicts_cmf_vs_vc_report.md`):

- **`common/parties/*` (3 файла)**:
  - `common/parties/conservative_party.txt`
  - `common/parties/liberal_party.txt`
  - `common/parties/radical_party.txt`
- **`gui/00_MDF_frontend_dlc.gui` (1 файл)**

Следствие в игре: при текущем порядке **всегда будут активны версии VC** этих файлов.

## 2) “Тихие” конфликты в `common/*`: одинаковые идентификаторы (самое важное)

Это не совпадение путей, а совпадение **ключей/объектов** в одной категории `common/...`.
Для Vic3 это означает: **последняя загрузка побеждает**, и более ранние правки либо теряются, либо остаются “мертвым кодом”.

### 2.1 T&R vs VC — критичные зоны

Источник: `conflicts_tr_vs_vc_report.md` (всего common‑дубликатов: **137**).

- **`common/buy_packages` (90 дубликатов `wealth_10 … wealth_99`)**
  - T&R делает `TRY_INJECT:wealth_X` (инжектит “entertainment” и т.п.)
  - VC делает `REPLACE_OR_CREATE:wealth_X` (полная замена пакетов)
  - **Итог при load order**: VC **перезатирает** пакеты, и инжекты T&R **пропадают**.
  - Риск: новые goods/экономика T&R получают меньше спроса/не тот спрос (слом баланса цепочек).

- **`common/pop_needs` (10 дубликатов `popneed_*`)**
  - T&R: `INJECT:*` + местами `REPLACE:*` (в т.ч. добавляет `water`, `gas`, `homeappliances`, `pharmaceuticals`, `batteries`, `copperwires` и др.)
  - VC: `REPLACE_OR_CREATE:*` (полная замена потребностей)
  - **Итог**: VC **перезатирает** pop needs → потребление новых goods из T&R **с высокой вероятностью исчезает**.

- **`common/on_actions` (2 дубликата: `on_monthly_pulse_country`, `on_yearly_pulse_country`)**
  - T&R содержит списки on_actions на месячный/годовой пульс (экономика/идеологии/деколонизация/healthcare и т.д.)
  - VC тоже определяет эти блоки (в т.ч. headlines, монархические цепочки, monthly events)
  - **Итог**: VC **заменяет** `on_monthly_pulse_country` и `on_yearly_pulse_country` → большинство скриптов T&R, которые “подцеплялись” через эти on_actions, перестают срабатывать.

- **`common/defines` (дубликат верхнего блока `NPops`)**
  - T&R: `NPops` про **кривые рождаемости/смертности по SoL** (и другие derived‑значения)
  - VC: `NPops` про **WORKING_ADULT_RATIO / колонизацию / cultural communities**
  - **Итог**: VC **перезатирает** весь `NPops`, и поп‑рост/демография T&R **теряются** (END_DATE у T&R задаётся в `NGame`, это отдельный блок и не обязан конфликтовать с VC).

- **`common/company_types` (32 дубликата `company_*`)**
  - Оба мода определяют часть исторических компаний теми же id.
  - **Итог**: для этих компаний будут активны версии VC; различия в условиях появления/эффектах T&R теряются.
  - Это почти наверняка потребует ручного решения “чью версию компании берём” или объединения условий/модификаторов.

- **Прочее (менее критично, но реально конфликтует)**:
  - `common/technology/technologies`: `organized_sports` (T&R `REPLACE`, VC `REPLACE_OR_CREATE`)
  - `common/modifier_type_definitions`: `goods_output_grain_mult` (разные параметры UI/ai_value)

### 2.2 KAI vs VC — критичная зона

Источник: `conflicts_kai_vs_vc_report.md`.

- **`common/defines` (дубликат верхнего блока `NAI`)**
  - KAI — большая перенастройка AI‑параметров
  - VC — тоже правит `NAI` (в т.ч. автономные инвестиции/рандом и т.п.)
  - **Итог**: VC **перезатирает** `NAI`, и значительная часть Kuromi AI **не работает как задумано** без компача (нужно объединять константы в одном `NAI`).

### 2.3 CMF vs VC — важные зоны

Источник: `conflicts_cmf_vs_vc_report.md`.

- **`common/on_actions`: `on_new_ruler`**
  - CMF добавляет блокировку регентств (переменная `com_no_regencies`) и поддерживает цепочки наследований.
  - VC тоже активно использует `on_new_ruler` для своих монархических/событийных цепочек.
  - **Итог**: VC **перезаписывает** `on_new_ruler` → CMF‑блокировка регентств может пропасть.

- **`common/political_movements`: `movement_bonapartist`, `movement_utilitarian`**
  - Оба мода задают эти movement‑типы по‑разному (`REPLACE` vs `REPLACE_OR_CREATE`, разные идеологии/триггеры/веса).
  - **Итог**: будет версия VC.

## 3) GUI‑идентификаторы

Итог по эвристике `compare_gui_names.py`:

- T&R vs VC: пересечений GUI‑`name/icon/type` **нет** (см. `conflicts_tr_vs_vc_gui_ids.txt`).
- CMF vs VC: пересечения есть только потому, что **один и тот же файл** `gui/00_MDF_frontend_dlc.gui` присутствует в обоих модах и имеет одинаковые `type` (см. `conflicts_cmf_vs_vc_gui_ids.txt`).

## 4) Что это означает для будущего компача в `vc_tr/` (приоритет)

Если цель — чтобы **оба набора механик реально работали вместе** при порядке с VC последним, то “первый эшелон” компат‑патчей почти наверняка будет такой:

- `common/buy_packages`: заново **добавить** правки T&R поверх VC (после того как VC заменил wealth‑пакеты).
- `common/pop_needs`: **встроить** добавленные goods T&R в popneeds VC (или наоборот — выбрать единую модель).
- `common/on_actions`: **объединить** `on_monthly_pulse_country` и `on_yearly_pulse_country` (чтобы не потерять ни T&R‑пульсы, ни VC‑headlines/ивенты).
- `common/defines`:
  - собрать `NPops` как “супер‑блок” (демография T&R + рабочая доля/колонизация/communities VC),
  - собрать `NAI` (Kuromi + VC).
- `common/on_actions` → `on_new_ruler`: решить, сохраняем ли CMF‑блокировку регентств и как встроить её в VC‑логику.

