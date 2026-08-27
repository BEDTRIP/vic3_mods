# grey_diplo Grey_DIS_is_active Fix

<!-- meta
мод: свой фикс флага grey_diplo (GR.11)
статус: done
версии: Game 1.13 (exe 1.13.11) — Grey's Diplomatic Interaction Suite (версия мод не объявляет)
позиция: после CMF, после grey_diplo
файлов: 1
генератор: tools/regen_greys_diplo_fix.py
зависит от: —
-->

## Для мастерской

[h1]grey_diplo Grey_DIS_is_active Fix[/h1]
[b]Game 1.13 (exe 1.13.11) — Grey's Diplomatic Interaction Suite.[/b]

grey_diplo объявляет свой флаг реестра CMF (`Grey_DIS_is_active`) голым ключом вместо `REPLACE_OR_CREATE:` — регистрационное значение CMF (`always = no`) молча побеждает, и флаг никогда не читается как `yes` чужими интеграциями. Этот файл переопределяет его правильно.

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Grey's Diplomatic Interaction Suite (часть блока Grey's)
[*][b]this fix[/b] (в любом месте после обоих)
[/list]

---

**Game 1.13 (exe 1.13.11). Grey's Diplomatic Interaction Suite (declares no version).**

Найдено при разборе аддона-Grey's — не пара, внутренний баг одного мода блока. Тот же класс, что уже описан как каноничный пример в `Правила работы с модами Victoria 3.md`: «CMF держит реестр флагов `*_is_active`… Мод обязан переопределить свой флаг через `REPLACE_OR_CREATE:` — голый ключ для `scripted_triggers` не переопределяет, и флаг молча остаётся `no`. Реальный случай: `grey_diplo` объявляет `Grey_DIS_is_active` голым ключом».

## Что сломано

CMF (`0_community_mod_triggers.txt`) регистрирует флаг для сторонних модов, которые хотят проверить, стоит ли Diplomatic Interaction Suite:

```
Grey_DIS_is_active = { # Diplomatic Interaction Suite
	always = no
}
```

grey_diplo (`zz_MoG_DIS_mod_compatibility_triggers.txt`) переиздаёт тот же ключ, тоже голым:

```
Grey_DIS_is_active = { # Diplomatic Interaction Suite
	always = yes
}
```

Для `scripted_triggers` голая повторная декларация не переопределяет предыдущую — побеждает первая, CMF-овская `no`, вне зависимости от порядка файлов. Любая чужая интеграция, проверяющая `Grey_DIS_is_active = yes`, молча не сработает, ни строчки в error.log.

Проверено: сейчас в нашем наборе ничего не опирается на этот флаг — ни один установленный мод его не читает, поэтому видимой поломки прямо сейчас нет. Но это ровно тот сценарий, ради которого реестр и существует — любая будущая интеграция с grey_diplo молча не увидит его присутствия, тем же образом, что `is_usfp_active` не видела Hail Columbia! в другом месте этой пачки, пока не была исправлена.

## Как сделан фикс

`common/scripted_triggers/zz_greys_diplo_fix_dis_flag.txt` — три строки, `REPLACE_OR_CREATE:Grey_DIS_is_active = { always = yes }`.

## Пересборка

`tools/regen_greys_diplo_fix.py`; `--check` печатает `SAME`/`DRIFT` и ничего не пишет. Проверяет, что тело grey_diplo всё ещё содержит `always = yes` — если автор сам поправит префикс, генератор не заметит несоответствие сам по себе (тело останется тем же), тогда компач станет просто избыточным, не вредным.

## Автору

Не отправлено — накапливается вместе с остальными находками по Grey's pack (см. `План проекта.md`, GR.20: письмо готовится одним пакетом по всем находкам сразу).
