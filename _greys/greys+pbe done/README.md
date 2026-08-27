# ComPatch: Grey's + PBE

<!-- meta
пара: Grey's × PBE (GR.3)
статус: done
версии: Game 1.13 (exe 1.13.11) — Power Blocs Expanded (версии мод не объявляет), grey_subject (версии мод не объявляет)
позиция: после всей пачки Grey's
файлов: 1
генератор: tools/regen_greys_pbe.py
зависит от: —
-->

## Для мастерской

[h1]ComPatch: Grey's + PBE[/h1]
[b]Game 1.13 (exe 1.13.11) — Power Blocs Expanded, Grey's pack.[/b]

Grey's Subject Interaction Suite (`grey_subject`) rewrites the same power-bloc diplomatic action as Power Blocs Expanded (`force_become_subject`), loads after it, and names every sub-block PBE does — so it wins outright. PBE's game-rule-gated relaxations and its infamy incident silently disappear; only grey_subject's own border check survives. This patch restores PBE's body and keeps grey_subject's border check.

[h2]Load order[/h2]
[list]
[*]…E&F → E&F Hotfix → Morgenröte → PBE…
[*]…MegaComPatch…
[*]Grey's pack (soft_econ, soft_pop, USU, cinosphere, food, ranch, diplo, subject)
[*][b]this ComPatch[/b]
[/list]

---

**Game 1.13 (exe 1.13.11). Power Blocs Expanded (declares no version); grey_subject (declares no version).**

Pair GR.3 — one shared record.

## Одна запись, два независимых расхождения с ванилью

`force_become_subject` — «force become subject» кнопка лидера powerbloc'а. И PBE (`common/diplomatic_actions/vokaes_power_bloc_actions.txt`, голое тело, то есть по силе как `REPLACE:`), и grey_subject (`common/diplomatic_actions/31_zower_bloc_force_become_subject.txt`, `TRY_REPLACE:`) переписывают её целиком. `groups`, `show_in_lens`, `texture`, `selectable`, `potential`, `ai` у обоих дословно совпадают (генератор это проверяет хешем тела без `possible`/`accept_effect` — расхождение там останавливает прогон). Расхождения — ровно в двух местах, и они не пересекаются:

* **PBE оборачивает три ванильных гейта `possible`** (ранг цели, сплочённость блока, престиж) в `OR = { has_game_rule = vokaes_power_bloc_rule_diplo_action_changes_enabled, <ванильный гейт> }` и добавляет в `accept_effect` `create_incident` (инфейми) под тем же гейтом. **Это правило по умолчанию включено** (`common/game_rules/vokaes_power_bloc_game_rules.txt`: `default = vokaes_power_bloc_rule_diplo_action_changes_enabled`) — то есть у игрока без единой галочки в настройках эта ветка и есть рабочее поведение, а не опциональная надстройка.
* **grey_subject добавляет один гейт, которого нет у PBE:** `custom_tooltip { text = common_border1 }` в `possible` — требует общую границу с целью (прямую или через протекторат/колонию).

## Почему без компача PBE проигрывает целиком

grey_subject грузится последним в блоке Grey's (`tools/blocks.json`, `load_order`), PBE — задолго до Grey's в общей цепочке. `TRY_REPLACE:` патчит по перечисленным под-блокам, а grey_subject называет `possible` и `accept_effect` целиком, своими телами — не только патчит недостающее, а **заменяет оба блока своими версиями без гейтов PBE**. Итог без компача: гейты `has_game_rule` пропадают из `possible` (все три ослабления PBE недоступны), `create_incident` пропадает из `accept_effect` (инфейми за принуждение к вассалитету не начисляется), а border-гейт grey_subject остаётся — ни строчки в логе.

## Как сделан мердж

`common/diplomatic_actions/zz_greys_pbe_force_become_subject.txt` берёт тело PBE целиком и добавляет в `possible` третьим независимым гейтом `custom_tooltip = { text = common_border1 ... }`, взятый дословно из grey_subject. `accept_effect` не трогается — у grey_subject там нет ничего, чего нет у PBE (ни `create_incident`, ни ветки `dominion`, которую оба, кстати, одинаково не называют — не расхождение, оба варианта уже без неё).

## Пересборка

`tools/regen_greys_pbe.py`; `--check` печатает `SAME`/`DRIFT` и ничего не пишет. Генератор на каждом прогоне сверяет: тело записи вне `possible`/`accept_effect` у PBE и grey_subject совпадает побайтово (по хешу без пробелов); `accept_effect` PBE всё ещё содержит `create_incident`, а у grey_subject его по-прежнему нет; border-тултип grey_subject всё ещё называется `custom_tooltip` и всё ещё содержит `common_border1`; в `possible` PBE такого тултипа на верхнем уровне ещё нет (иначе — конфликт имён, чинить руками). Любое из этих условий сорвётся — прогон падает с сообщением, что именно изменилось. Пересобирать после любого обновления PBE или Grey's pack.
