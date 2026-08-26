# KAI × Morgenröte — компач не нужен

<!-- meta
пара: Morgenröte × KAI
статус: noneed
версии: —
позиция: —
файлов: 0
генератор: —
зависит от: —
-->

Статус поставлен 25.08.2026 (задача МП.2) при разделении компача `morg+tr+kai`.
T&R-половина уехала в `_tr/morg+tr out fixed`.

## Основание

`pair_matrix.py --pair "KAI,Morgenrote"`, прогон 25.08.2026: **2 ключа, 0 общих путей, 0 общих id событий.**

| ключ | KAI | Morgenröte | вывод |
| --- | --- | --- | --- |
| `building_government_administration` | `INJECT:` → под-блок `ai_value` | `TRY_INJECT:` → под-блок `production_method_groups` | разные под-блоки, обе правки — инжекты. Складываются |
| `atmospheric_engine` | `INJECT:` → под-блок `ai_weight` | `TRY_INJECT:` → под-блок `unlocking_technologies` | то же. Сюда же инжектит TGR (`modifier`) — три автора, три разных под-блока, никто никого не задевает |

Ни один из двух ключей не переписывается телом: `INJECT:` сливает под-блоки в запись, а называют они разное.

Дополнительно:

* **Товары.** KAI не везёт `common/goods` — пять товаров Morgenröte в опасности не были.
* **`.gui`.** У KAI папки `gui/` нет, сравнивать нечего.
* **Порядок загрузки.** Вывод от него не зависит: пересечение только по именам записей, не по под-блокам.

Прежняя формулировка того же вывода — в README компача `_tr/morg+tr out fixed`: «Kuromi's AI needs no patching — it shares no key, no localisation key, no event id». На 25.08.2026 это уже не совсем так по букве (два ключа есть), но по существу верно, и теперь записано поимённо.

## Что перепроверить при обновлении

Если Morgenröte начнёт писать `ai_value` / `ai_weight`, а KAI — `production_method_groups` / `unlocking_technologies`, пара перестаёт быть аддитивной.
