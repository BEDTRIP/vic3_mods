# VC × PBE — компач не нужен (VC.6)

<!-- meta
пара: PBE × VC
статус: noneed
версии: —
позиция: —
файлов: 0
генератор: —
зависит от: —
-->

Прежний статус `noneed` (заготовка `stuff/pbe+vc noneed`, до переезда папок пар из `stuff/` в `_vc/`) подтверждён на текущих версиях 26.08.2026 — и оказался не просто "нет конфликта", а "PBE тут вообще ни на что не влияет, независимо от VC".

## Основание

`pair_matrix.py --pair "VC,PBE"`, прогон 26.08.2026:

```
VC  x  PBE   ключей: 1   общих путей: 0   общих id событий: 0
   common/script_values: 1
        power_bloc_mandate_progress_by_rank
```

Обе стороны определяют ванильный script value `power_bloc_mandate_progress_by_rank` (ваниль: `.vanillaVIC3/common/script_values/01_power_bloc_values.txt`, строка 477):

* **VC** (`joi_power_bloc_values.txt`) — `REPLACE_OR_CREATE:`, база `value = 10 - power_bloc_rank, min 5` (ваниль: `6 - power_bloc_rank, min 1`).
* **PBE** (`vokaes_power_bloc_script_values.txt`) — **голый повтор ключа без префикса**: `power_bloc_mandate_progress_by_rank = { ... }`, без `REPLACE:`/`REPLACE_OR_CREATE:`.

Раздел 3 «Правил работы» фиксирует это явно: **для `scripted_effects` / `scripted_triggers` / `script_values` простой повтор ключа в более позднем файле НЕ переопределяет** — нужен `REPLACE_OR_CREATE:`. Симптом молчаливый: старое определение продолжает работать, новое не зовётся никогда.

**Значит вклад PBE в этот script value не срабатывает вообще, независимо от VC.** Ванильное определение (или VC-шное, если VC грузится и правда переопределяет через `REPLACE_OR_CREATE:`, что синтаксически корректно) остаётся единственным рабочим — тело PBE мёртво уже само по себе, порядок VC/PBE между собой роли не играет.

Дополнительно: содержимое PBE целиком спрятано за `has_game_rule = vokaes_power_bloc_rule_enable_mandate_progress_enabled` — собственным игровым правилом PBE, которое по умолчанию выключено. То есть даже если бы префикс был правильным, эффект по умолчанию был бы нулевым без отдельного включения этого правила игроком.

## Итог

Компач не нужен — ни писать нечего (VC ничего у PBE не отнимает — PBE ничего и не отдавало), ни восстанавливать нечего.

## Что перепроверить при обновлении

* Если PBE в новой версии поправит префикс на `REPLACE_OR_CREATE:` — пересчитать пару заново, тогда это станет настоящим конфликтом (два REPLACE_OR_CREATE на одну запись, побеждает поздний по общему порядку — VC).
* Автору PBE стоит написать про голый повтор ключа script value — тот же класс мелочи, что и `grey_diplo`/`Grey_DIS_is_active` (GR.11) и `_grey_soft_pop`/`com_law_*_alternative_trigger` (GR.13), только для `script_values`, а не `scripted_triggers`.
