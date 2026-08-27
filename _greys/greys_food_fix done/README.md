# grey_food Cooling Methods Fix

<!-- meta
мод: внутренний фикс пересечения grey_usu × grey_food (GR.14)
статус: done
версии: Game 1.13 (exe 1.13.11) — Grey's Urban Synergy Unleashed, Grey's Food Industries Rework (версии моды не объявляют)
позиция: после grey_food
файлов: 1
генератор: tools/regen_greys_food_fix.py
зависит от: —
-->

## Для мастерской

[h1]grey_food Cooling Methods Fix[/h1]
[b]Game 1.13 (exe 1.13.11) — Grey's Urban Synergy Unleashed, Grey's Food Industries Rework.[/b]

grey_food переиздаёт два метода охлаждения, которые тем же `TRY_REPLACE:` несёт и grey_usu, и теряет по одному числу на каждом — транспортную добавку, которую grey_usu вносил. Этот фикс возвращает оба числа, читая их живьём из тела grey_usu.

[h2]Load order[/h2]
[list]
[*]Grey's Urban Synergy Unleashed (часть блока Grey's)
[*]Grey's Food Industries Rework (часть блока Grey's)
[*][b]this fix[/b]
[/list]

---

## Подробности

**Game 1.13 (exe 1.13.11). Grey's Urban Synergy Unleashed; Grey's Food Industries Rework (оба не объявляют версию).**

Найдено при разборе GR.14 («Пересечения внутри пачки») — задача, которую `pair_matrix.py` и `content_holes.py` не видят в принципе: оба инструмента сравнивают между блоками `blocks.json`, а вся пачка Grey's — один блок. Проверено вручную, побайтово, по плану от 27.08.2026.

## Что теряется

Девять методов охлаждения объявлены `TRY_REPLACE:` и в grey_usu (`xMoG_USU_trains_misc_resource.txt` / `xMoG_USU_trains_agriculture.txt`), и в grey_food (`mog_ztrains_food_inputs.txt`). Семь синхронизированы побайтово — автор grey_food держал их в актуальном состоянии, тот же класс, что GR.10. Два — нет:

| ключ | что несёт grey_usu | чего нет у grey_food |
| --- | --- | --- |
| `pm_refrigerated_storage_building_fishing_wharf` | `goods_input_transportation_add = 5` рядом с электричеством | только электричество, транспорт пропал |
| `pm_unrefrigerated` | весь блок `building_modifiers` (`goods_input_transportation_add = 1`) | блока `building_modifiers` нет вовсе |

Оба поля — не переспор числа (сравните с GR.6/GR.18, где вторая сторона явно меняет значение с комментарием или новой моделью): тело grey_food — строгое подмножество тела grey_usu без этого поля, ничего своего взамен не добавлено. grey_food грузится после grey_usu и выигрывает всю запись целиком — оба поля пропадают молча, ни строчки в error.log.

## Что не здесь

Остальные семь пересечений из заметки плана про GR.14 проверены отдельно и фикса не требуют:

* **usu × ranch, 2 ключа** (`pm_refrigerated_rail_cars_building_livestock_ranch`, `pm_refrigerated_storage_building_livestock_ranch`) — собственный `TRY_INJECT:` grey_usu несёт только поле `state_modifiers.workforce_scaled...throughput`, и то же число (0.02 / 0.01) уже побайтово стоит в полных телах и grey_food, и grey_food_2_ranch. Синхронизация автора, не потеря.
* **food × ranch, 4 ключа** (`pm_slaughterhouses`, `pm_mechanized_slaughtering`, `pm_butchering_tools`, `pm_open_air_stockyards`) — тела `REPLACE_OR_CREATE:` у grey_food_2_ranch — собственный комплексный передел RPR (новые текстуры `rpr_`/`m1_`, новый `ai_value`, каждое число пересчитано, знак занятости перевёрнут). Решение №12: спор дизайна, ranch выигрывает целиком, файла нет.
* **`_grey_soft_econ` × `_grey_soft_pop`, `peasants`** — `_grey_soft_pop` меняет `start_quality_of_life` с 5 на 105 с собственным комментарием `# 5`, показывающим прежнее значение. Осознанная правка, не потеря.
* **`grey_subject` × `grey_usu`, `total_bureaucracy_need`** — тела побайтово идентичны. Синхронизация автора.
* **`grey_diplo` × `grey_subject`, `is_giftable_treaty_article`** — ложная тревога плана: это не общий верхнеуровневый ключ, а вызов одного и того же ванильного триггера внутри двух разных, не связанных между собой договорных статей (`transfer_state` у diplo, `support_independence` у subject). Не пересечение вовсе.
* **`grey_diplo` × `grey_subject`, `trade_states`** — реальное пересечение, но не сюда: закрыто отдельным фиксом `_greys/greys_subject_fix done`, см. его README.

## Как сделан фикс

`common/production_methods/zz_greys_food_fix_cooling.txt` — `TRY_INJECT:` обоих полей на два ключа, значения читаются живьём из файла grey_usu, а не переписаны руками.

## Пересборка

`tools/regen_greys_food_fix.py`; `--check` печатает `SAME`/`DRIFT` и ничего не пишет. Падает с сообщением, если grey_usu перестанет нести любое из двух полей — тогда фикс либо не нужен, либо нужен по-другому.
