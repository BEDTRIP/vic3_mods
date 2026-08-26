# VC × PSC — компач не нужен (VC.5)

<!-- meta
пара: PSC × VC
статус: noneed
версии: —
позиция: —
файлов: 0
генератор: —
зависит от: —
-->

Прежний статус `noneed` (заготовка `stuff/psc+vc noneed`, до переезда папок пар из `stuff/` в `_vc/`) подтверждён на текущих версиях 26.08.2026.

## Основание

`pair_matrix.py --pair "VC,PSC"`, прогон 26.08.2026:

```
VC  x  PSC   ключей: 4   общих путей: 0   общих id событий: 0
   common/production_methods: 4
        pm_arc_welded_buildings   pm_iron_frame_buildings   pm_steel_frame_buildings   pm_wooden_buildings
```

Все четыре — в `common/production_methods`, оба мода правят одни и те же ванильные методы стройки.

* **PSC** (`zz_PSC_construction.txt`) — везде `REPLACE:`, перечисляет `texture`, `is_default`/`unlocking_technologies`, и `building_modifiers` целиком (`workforce_scaled` с полями `goods_input_*_add`/`goods_output_*_add`, `level_scaled`, `unscaled`).
* **VC** (`joi_methods.txt`) — везде `INJECT:`, трогает только `building_modifiers.workforce_scaled` (теми же `goods_input_*_add` полями, что и PSC — `fabric`, `wood`, `iron`, `tools`, `steel`, `glass`, `explosives`) и отдельно `state_modifiers.workforce_scaled.state_construction_mult`, которого PSC не касается вовсе.

PSC грузится раньше VC (основная пачка → мегапак → VC), поэтому к моменту INJECT'а VC запись уже переписана PSC. Значит вопрос ровно тот, что раздел 3 «Правил работы» решает явно: **повторяющиеся `_add`-ключи внутри одного блока модификаторов складываются**, а не перезаписываются. И PSC, и VC используют исключительно `_add`-суффиксы (`goods_input_fabric_add`, `goods_input_wood_add` и т.д.) в одном и том же под-блоке `workforce_scaled` — числа PSC и числа VC суммируются, а не конфликтуют. Ни один вклад не теряется.

`state_modifiers` — под-блок, которого PSC вообще не объявляет в этих четырёх записях: VC добавляет его с нуля, тоже без пересечения.

## Дополнительно проверено

* Ни у PSC, ни у VC эти четыре PM не открываются сбросом `value =` — только суммируемые `_add` поля, ловушка «блок, который автор открывает `value =`, забирает целиком» здесь не применяется.
* Порядок важен только для того, чья `REPLACE:`/`INJECT:` запись «видит» чужую первой — но поскольку итог одинаков при сложении в любом порядке, вывод от порядка не зависит.

## Что перепроверить при обновлении

Если PSC или VC начнут использовать не `_add`, а `add =`-блок со сбросом (`value = X`) в `workforce_scaled`, или если один из них начнёт `REPLACE:` уносить весь `building_modifiers` без переиздания чужих полей — пересчитать пару и написать компач.
