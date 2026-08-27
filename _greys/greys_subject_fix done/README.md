# grey_subject trade_states Fix

<!-- meta
мод: внутренний фикс пересечения grey_diplo × grey_subject (GR.14)
статус: done
версии: Game 1.13 (exe 1.13.11) — Grey's Diplomatic Interaction Suite, Grey's Subject Interaction Suite (версии моды не объявляют)
позиция: после grey_subject
файлов: 1
генератор: tools/regen_greys_subject_fix.py
зависит от: —
-->

## Для мастерской

[h1]grey_subject trade_states Fix[/h1]
[b]Game 1.13 (exe 1.13.11) — Grey's Diplomatic Interaction Suite, Grey's Subject Interaction Suite.[/b]

grey_subject переиздаёт то же дипломатическое действие `trade_states`, что и grey_diplo, но своей — более старой — копией: без всех авторских доработок ИИ и с опечаткой в названии триггера. Грузится последним в пачке и выигрывает запись целиком, молча стирая доработки grey_diplo. Этот фикс возвращает тело grey_diplo как есть.

[h2]Load order[/h2]
[list]
[*]Grey's Diplomatic Interaction Suite (часть блока Grey's)
[*]Grey's Subject Interaction Suite (часть блока Grey's)
[*][b]this fix[/b]
[/list]

---

## Подробности

**Game 1.13 (exe 1.13.11). Grey's Diplomatic Interaction Suite; Grey's Subject Interaction Suite (оба не объявляют версию).**

Найдено при разборе GR.14 («Пересечения внутри пачки») — задача, которую `pair_matrix.py` и `content_holes.py` не видят в принципе: оба сравнивают между блоками `blocks.json`, а вся пачка Grey's — один блок. Проверено вручную, побайтово, по плану от 27.08.2026.

## Что теряется

`grey_diplo` (`zzzz04_trade_statez.txt`, `TRY_REPLACE:`) и `grey_subject` (`04_trade_statez.txt`, `REPLACE_OR_CREATE:`) оба переиздают ванильное действие `trade_states` целиком. Порядок пачки: soft_econ → soft_pop → USU → cinosphere → food → ranch → **diplo → subject** — subject грузится последним и выигрывает запись целиком.

Побайтовое сравнение показывает: тело grey_subject — не переспор дизайна (сравните с GR.6/GR.18), а более старая или просто другая копия того же действия, которой не хватает всех авторских правок grey_diplo (помечены в его файле комментарием `# Modded`) и которая несёт одну опечатку:

* **`second_state_trigger` теряет целую альтернативу.** grey_diplo добавляет ещё один путь через `OR`: `scope:country = { any_subject_or_below = { is_adjacent_to_state = root } }`. У grey_subject этой строки нет вовсе — не укорочена, а отсутствует целиком.
* **Три доработки ИИ в `accept_score` пропадают.** grey_diplo вычитает до 100 очков, если полученный порт уже не действует и получатель рангом выше отдающего; добавляет +100, если первый штат — историческая родина культур цели; и несёт целую ветку `else_if` («Modded»), дающую ИИ очки за обмен расщеплённым штатом даже когда подходит только первый штат. Плюс само базовое значение обмена расщеплённым штатом поднято с 25 до 30 (у самого grey_diplo это отмечено хвостовым комментарием `# 25`). Ни одной из этих правок у grey_subject нет.
* **`has_port` → `has_port_country`, опечатка.** И `first_state_trigger`, и `second_state_trigger` grey_diplo проверяют `has_port` в масштабе страны — то же написание, что используется ещё в шести местах по всей пачке Grey's, включая собственные другие файлы grey_subject (`z43_subjects_demand_states.txt`). `has_port_country` встречается ровно один раз во всей пачке — в этом самом файле grey_subject. Не отдельный валидный триггер, опечатка.

Обратное направление тоже проверено: своего содержательного вклада в эту запись у grey_subject нет — разница помимо перечисленного выше сводится к пробелам и укороченному тексту одного комментария (`# is_subject = no` без пояснения «Modded», тоже без функционального значения). Тело grey_diplo — строгое надмножество; поскольку subject грузится позже и выигрывает всю запись целиком, всё перечисленное пропадает молча, ни строчки в error.log.

## Что не здесь

`is_giftable_treaty_article`, второй пункт плана про пару diplo × subject, — ложная тревога: это не общий верхнеуровневый ключ, а один и тот же ванильный триггер, использованный внутри двух разных, не связанных между собой договорных статей (`transfer_state` у diplo, `support_independence` у subject). Не пересечение, файла не требует. Остальные пять пунктов GR.14 (usu × food, usu × ranch, food × ranch, soft_econ × soft_pop) разобраны в `_greys/greys_food_fix done` — там же итоговая сводка по всей задаче.

## Как сделан фикс

`common/diplomatic_actions/zz_greys_subject_fix_trade_states.txt` — `TRY_REPLACE:trade_states` целиком телом grey_diplo, читается живьём из его файла, а не переписано руками.

## Пересборка

`tools/regen_greys_subject_fix.py`; `--check` печатает `SAME`/`DRIFT` и ничего не пишет. Пять проверок на характерные маркеры (`any_subject_or_below` есть у diplo и нет у subject; `has_port_country` есть у subject и нет у diplo; `# Modded` есть у diplo) — генератор падает с сообщением, если любая перестанет совпадать: либо баг поправлен автором выше по цепочке и фикс больше не нужен, либо что-то в записи поменялось настолько, что нужна повторная ручная сверка.
