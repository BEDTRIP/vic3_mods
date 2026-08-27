# ComPatch: Grey's + Morgenroete

<!-- meta
пара: Grey's × Morgenroete (GR.6)
статус: done
версии: Game 1.13 (exe 1.13.11) — Morgenroete 2.8.3e Mitsopoulos, grey_usu (версии мод не объявляет)
позиция: после всей пачки Grey's
файлов: 3
генератор: tools/regen_greys_morg.py
зависит от: —
-->

## Для мастерской

[h1]ComPatch: Grey's + Morgenroete[/h1]
[b]Game 1.13 (exe 1.13.11) — Morgenroete, Grey's pack.[/b]

35 общих ключей. `grey_usu` уже несёт собственный компат к Morgenroete (файлы `zMoG_USU_MR_*.txt` / `mMoG_USU_MR_*.txt`), и 31 из 35 ключей там уже верно слиты. Остаются три настоящие потери: `building_government_administration` молча теряет PM-группу Morgenroete `pmg_panum_hospital` (автор `grey_usu` даже оставил исправление закомментированным в собственном файле), пять таблиц русского склонения `RU_BL_*` теряют 30 зданий Morgenroete, когда голое тело `grey_usu` целиком съедает `REPLACE:` Morgenroete, и `pm_nr_national_park` молча теряет поле прибавки к уровню жизни при пересборке тела. Восстанавливает все три, читая оба мода живьём.

[h2]Load order[/h2]
[list]
[*]…E&F → E&F Hotfix → Morgenröte → PBE…
[*]…MegaComPatch…
[*]Grey's pack (soft_econ, soft_pop, USU, cinosphere, food, ranch, diplo, subject)
[*][b]this ComPatch[/b]
[/list]

---

**Game 1.13 (exe 1.13.11). Morgenroete (2.8.3e Mitsopoulos); grey_usu (declares no version).**

Пара GR.6 — 35 общих ключей.

## Что уже смержено самим grey_usu

31 из 35 ключей закрыты собственным компатом `grey_usu` к Morgenroete (`zMoG_USU_MR_*.txt` / `mMoG_USU_MR_*.txt`, часть под именами `mMoG_...`/`zzzMoG_...`): аддитивные `TRY_INJECT:` (сливаются в список, не заменяют), задокументированные ребалансы (`mMoG_USU_MR_elgar_pms.txt` помечает каждое изменённое число `# было N`), две побайтово идентичные заглушки (`add_com_topbar_element`, `fix_variable_error`), и уже переставленный автором на `building_usu_railway_line` триггер `tesla_building_is_railway_building` (верно — USU разносит вокзал и дорогу на два отдельных здания). Здесь эти 31 не трогаются.

## Три настоящие потери

1. **`building_government_administration`.** Morgenroete добавляет `pmg_panum_hospital` в список групп производственных методов через `TRY_INJECT:`. `grey_usu` переиздаёт здание целиком (`yMoG_USU_government.txt`, `REPLACE_OR_CREATE:`) и не называет эту группу — она пропадает молча. Автор `grey_usu` сам оставил исправление закомментированным в этом же файле: `"Done within morgenrote - needs to be re-done because this overwrites morgenrote"`, но так и не применил. Восстановлено `TRY_INJECT:`, ровно то, что говорит комментарий.

2. **Пять таблиц `RU_BL_{DP,PP,RP,TP,VP}`** (дательный/предложный/родительный/творительный/винительный падежи для русского склонения названий зданий). Morgenroete делает `REPLACE:` со списком на 124 здания. `grey_usu`'s `999_MoG_USU_railway_ru_custom_loc.txt` — голое (без префикса) тело тех же пяти ключей со своим списком на 96 зданий; голое полное тело в позже грузящемся моде съедает более ранний `REPLACE:` целиком. Склонение для 30 зданий, которые знает только Morgenroete (её монументы, здания заповедника Dubois, опера Elgar, ванильные `building_airport`/`building_railway`), пропадает. Это чистая текстовая маршрутизация, не зависящая от того, чьё тело здания в итоге побеждает, поэтому все 30 восстановлены здесь независимо от исхода GR.9/GR.16/GR.17 — включая `building_railway`, хотя его тело здания этой парой намеренно не чинится (см. ниже). Исправлено `TRY_INJECT:`, один файл, все пять ключей, блоки `text` скопированы дословно из файла Morgenroete, чтобы `localization_key` не разъехался при ручном перепечатывании.

3. **`pm_nr_national_park`.** Morgenroete ставит `state_modifiers.unscaled.state_standard_of_living_add = 0.05`. `TRY_REPLACE:` `grey_usu` в `mMoG_USU_MR_dubois_pms.txt` добавляет свои `building_modifiers`/`country_modifiers` поверх, но этот `unscaled`-блок пропадает без единого комментария (для сравнения — файл elgar в том же моде помечает каждый ребаланс `# было N`). Восстановлено `TRY_INJECT:`.

## Что намеренно не тронуто

* **Тело `building_railway`.** `grey_usu` разносит его на вокзал и `building_usu_railway_line` — победившее тело относится к мерджу аддона-LLWA (GR.9/GR.16/GR.17), не к этой паре. Здесь чинится только маршрутизация `RU_BL_*` (пункт 2 выше).
* **`pm_nr_royal_reserve.state_modifiers.unscaled.state_upper_strata_standard_of_living_add`** — сосед `pm_nr_national_park` по тому же файлу. Morgenroete 0.1, пересборка `grey_usu` — 0.2, без комментария ни с одной стороны. **Решение №15 от 27.08.2026 (спрошено у пользователя, не выведено): оставлено число USU** — тело этого PM пересобрано целиком (добавлены `ai_value = 500000`, `building_modifiers` под солдат), похоже на намеренный, просто незадокументированный ребаланс. Файла на эту запись нет.
* **Остальные 27 из 35 ключей** (здания 4/6, типы компаний 1/1, потребности населения 2/2, производственные методы 27/29 — авиация 9 + elgar 7 + dubois 1 из 2, скриптовые эффекты 2/2, скриптовые триггеры 1/1) — проверено тело за телом, уже корректны: аддитивный `TRY_INJECT:`, задокументированный ребаланс, побайтово идентичная заглушка с обеих сторон, либо собственный компат-триггер `grey_usu` уже указывает на правильный ключ.

## Пересборка

`tools/regen_greys_morg.py`; `--check` печатает `SAME`/`DRIFT` и ничего не пишет. Самопроверка `0 problem(s)`. Пересобирать после любого обновления Morgenroete или Grey's pack.
