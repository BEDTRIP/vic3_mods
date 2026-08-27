# usu_llwa out outdate noneed

<!-- meta
пара: USU × LLWA
статус: noneed -- проверено 27.08.2026 обоими инструментами (pair_matrix.py + content_holes.py), не нужен
версии: —
позиция: —
файлов: 13 (источник, не наши)
генератор: —
зависит от: —
-->

Чужой компач автора Grey's (`USU + LLWA Compatch`, id 3387021675), распакован как источник. `version` и
`supported_game_version` в его `metadata.json` пустые -- явный признак заброшенности.

11 ключей, все голыми телами без префиксов: `building_railway`, `building_airport`, `LLWA_building_roadway`,
`LLWA_building_waterway`, `LLWA_building_airway`, `pmg_gaudi_communication`, `pmg_tourism_airport`,
`pm_gaudi_no_communication`, `pm_luxury_requisitions`, `pm_travel_agencies`, `LLWA_active`.
`LLWA_building_riverway` не покрыт вовсе.

## Разобрано задачей GR.9, 27.08.2026 -- компач полностью не нужен

Пересобирать было нечего: каждый из 11 ключей закрыт либо в `_greys/greys+llwa done`, либо починен выше по
цепочке самими авторами с тех пор, как этот компач был написан, либо уже закрыт другой нашей парой, которой
не существовало на момент его написания.

* **`building_railway`, `building_airport`** -- полностью перекрыты `_greys/greys+llwa done` (раздел 3
  README) заново, против текущих тел grey_usu и аддона-LLWA -- версия оттуда куда полнее (несёт ещё и обе
  группы E&F, которых в этом старом компаче никогда не было).
* **`LLWA_building_roadway`, `LLWA_building_waterway`** -- комментарий "Respecified purely so that the
  auto-expand rules are properly managed" был актуален, когда писался этот компач. Сейчас сама LLWA несёт
  собственный `should_auto_expand` на всех четырёх транспортных зданиях (roadway/waterway/riverway/airway,
  сверено по `llwa/common/buildings/LLWA_buildings.txt`) -- почин**е**но выше по цепочке самим автором.
* **`pmg_gaudi_communication`, `pm_gaudi_no_communication`, `pmg_tourism_airport`** -- побайтово совпадают с
  текущими телами самой Morgenröte (`civil_aviation_production_method_groups.txt`,
  `mr_science_tesla_production_method_groups.txt` / `..._production_methods.txt`). Устаревшие дубликаты для
  сценария "USU+LLWA без Morgenröte", которого в нашей сборке не бывает.
* **`pm_luxury_requisitions`, `pm_travel_agencies`** -- grey_usu сам теперь несёт `TRY_REPLACE:` обоих в
  `mMoG_USU_MR_civil_aviation_pms.txt`, с теми же тех-гейтами, что у Morgenröte (`curtiss_tourism_tech`, а не
  запасной `mass_propaganda` этого старого компача для сценария без Morgenröte) и с тем же добавленным полем
  `goods_input_usu_logistics_add`, что вручную прописывал автор этого компача. USU усвоил это нативно --
  делать нечего.
* **`LLWA_active`** (`has_game_rule = LLWA_grs_*`) -- вытеснен официальным механизмом самой LLWA,
  `LLWA_is_active_trigger` (`llwa/common/scripted_triggers/00_LLWA_active_trigger.txt` /
  `zz_LLWA_active_trigger.txt`) -- другое имя, другой механизм, появился позже этого компача.
* **`LLWA_building_riverway`** ("отсутствует вовсе" в этом компаче) -- полностью закрыт нашими же
  `_llwa/llwa+ef done` (акции) и `_llwa/llwa+companies done` (доступ компаниям), которых на момент написания
  usu_llwa тоже не существовало.

**Не тронуто, но не потеря:** `LLWA_building_airway` сейчас не несёт гейта-исключения против
`building_airport` (старое `NOT = { morgenrote_is_active = yes }` из этого компача тоже пропало) -- то есть
при LLWA + Morgenröte вместе можно построить и airway, и airport одновременно. Ничего не пропадает молча --
это вопрос баланса/дизайна, не наш класс багов, поэтому файла нет и решение не форсировано; если в игре
окажется заметно, вернуться отдельной задачей.

Проверено `pair_matrix.py --pair "Grey's,LLWA"` (11 ключей, все учтены -- см. `_greys/greys+llwa done/README.md`
§2) и `content_holes.py --only builds` (26 ключей АДДОН-LLWA × USU, все учтены -- там же, §1 и §3).
