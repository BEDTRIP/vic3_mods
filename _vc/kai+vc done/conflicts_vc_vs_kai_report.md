# VC × Kuromi's AI (KAI) — разбор пары (VC.4)

Прогон `pair_matrix.py --pair "VC,KAI"` 26.08.2026: **9 общих ключей, 0 общих путей, 0 общих id событий.**

```
common/ai_strategies: 3   ai_strategy_great_reforms, ai_strategy_meiji_restoration, ai_strategy_tanzimat_reforms
common/defines:        1   NAI
common/ship_types:     5   ship_type_aircraft_carrier, ship_type_coastal_defense_ship, ship_type_monitor,
                            ship_type_seaplane_tender, ship_type_troop_ship
```

## common/ship_types — 5 ключей, НЕ конфликт

KAI (`kai_ship_types.txt`) везде делает `INJECT:` и трогает только `ai_weight` (AI-вес корабля при проектировании). VC (`joi_ship_types.txt`) везде тоже `INJECT:`, но трогает только `modifier` (`ship_blockade_strength_add` и т.п.) и `construction_goods`/`materiel_goods` (ребаланс стоимости постройки). Проверено по всем пяти общим записям — под-блоки разные везде, значит и INJECT'ы просто складываются. Компач не нужен.

## common/defines — NAI, НЕ конфликт

Дефайны сливаются **поключево** (правило раздела 3 «Правил работы»), а не блоком. У KAI (`kai_ai.txt`) — 30 констант, все с префиксами `REFORM_GOVERNMENT_*`, `SUPPLY_SHIP_*`, `SHIP_DESIGN_*`, `MAX_INSTITUTION_SPENDING_*`, `MONEY_SPENDING_*`, `PRODUCTION_METHOD_*`, `MILITARY_UNITS_PER_FORMATION_ARMY`. У VC (`joi_ai.txt`) — две другие константы: `BUILDING_PRIVATIZATION_CHANCE`, `CONSTRUCTION_MAX_NUM_PRODUCTION_BUILDING_CONSTRUCTIONS_SCALED_MAX`. Пересечения по именам констант — ноль. `pair_matrix.py` считает это одним «общим ключом» только потому, что оба мода трогают контейнер `NAI`; по факту это не конфликт. Компач не нужен.

## common/ai_strategies — 3 ключа, ВСЕ реальные

VC грузится после KAI, и на всех трёх записях делает `REPLACE_OR_CREATE:` — голое полное тело съедает более ранний `INJECT:`/`REPLACE:` KAI молча, ни строчки в логе (правило «REPLACE_OR_CREATE у VC съедает более ранний INJECT», уже встречавшееся в VC.2 и VC.3).

### `ai_strategy_great_reforms` и `ai_strategy_tanzimat_reforms`

KAI инжектит в обе записи ровно одно и то же: `revolution_aversion = { value = 67.5 }`. Сверка тела VC с ванилью (`.vanillaVIC3/common/ai_strategies/03_political_strategies.txt`) показывает: тело VC побайтово совпадает с ванилью **везде, кроме `possible`** (VC подставляет свой журнал вместо ванильного `je_great_reformer` / `je_sick_man_main`). Значения `revolution_aversion` — 10 и 25 — это ванильные числа, перенесённые в тело VC не как решение автора VC, а просто потому что VC переиздаёт запись целиком по другой причине (замена `possible`). Значит это не спор двух авторов о значении, а чистая потеря вклада KAI: правило «переиздать чужой INJECT: поверх более позднего тела — точное восстановление, если тело той же формы» применяется без оговорок. Восстановлено `INJECT:` обеих записей, `possible` VC не тронут.

### `ai_strategy_meiji_restoration`

Здесь KAI не инжектит, а делает `REPLACE:` всей записи — то есть уже два автора переписали одну и ту же ванильную запись целиком (Анализ 5). Три-стороннее сравнение с ванилью (`.vanillaVIC3/…/03_political_strategies.txt`, строка 1187):

| поле | ваниль | VC | KAI |
| --- | --- | --- | --- |
| `revolution_aversion.value` | 10 | 10 (= ваниль) | **67.5** |
| `max_regressiveness.value` | 25 | 25 (= ваниль) | **50** |
| `anti_interest_groups` | `ig_landowners`, `ig_armed_forces` | = ваниль | **без `ig_armed_forces`** |
| `interest_group_government_weight` | нет | нет | **новый блок**, условие `has_journal_entry = je_meiji_army` |
| `possible` | `has_journal_entry = je_meiji_main` | **своя (см. ниже)** | `OR{je_meiji_restoration, je_meiji_main} + ruler ?= JAP_meiji_yamato` |

Собственный вклад VC во всей записи — только `possible`. Собственный вклад KAI — все четыре остальные строки.

**Восстановлено:** `revolution_aversion` (10 → 67.5) и `max_regressiveness` (25 → 50) — чистые числовые правки без структурных последствий, восстановлены поверх тела VC полным `REPLACE_OR_CREATE:`.

**Оставлено открытым (не патчится):** `anti_interest_groups` (убрать `ig_armed_forces`) и `interest_group_government_weight` (добавить блок) — это одно связанное решение KAI (статичная неприязнь заменяется на условную), и условие завязано на `has_journal_entry = je_meiji_army` — ванильный журнал. VC полностью переписывает механику Реставрации Мэйдзи своими журналами (`meiji_restoration`, `meiji_restoration_mil/dip/eco/law/lad/ray`, группа `je_group_meiji_restoration` переиздана `REPLACE_OR_CREATE:`), файл `je_meiji_army` не трогает вовсе — но VC зачем-то сам расставляет `set_variable = completed_je_meiji_army` (та же переменная, что и в ванильном `je_meiji_army`), не добавляя сам ванильный журнал `je_meiji_army`. Не установлено:
* добавляет ли что-либо в игре ванильный `je_meiji_army` при активном VC (VC его не трогает, но и не гасит явно — цепочка запуска не прослежена до конца);
* остаётся ли живым `possible` KAI (`je_meiji_restoration` / `je_meiji_main` / шаблон `JAP_meiji_yamato`) — `je_meiji_main` у VC не тронут вообще, `je_meiji_restoration` VC переиздаёт `REPLACE_OR_CREATE:` другим содержимым.

Если `je_meiji_army` под VC не срабатывает никогда, блок `interest_group_government_weight` безвреден (мёртвая ветка, `value = 0` без штрафа) — но тогда снятие `ig_armed_forces` из `anti_interest_groups` без работающей замены — чистая потеря вклада KAI (нейтралитет вместо продуманной условной неприязни), хуже и ванильного поведения, и намерения KAI. Оба сценария правдоподобны, и молчание в логах не подтверждает ни один. Писать это вслепую опасно в обе стороны — та же логика, что и у `mobilization_option_chemical_weapons` в VC.3.

**Дешёвая проверка в игре:** Япония при активных VC + KAI, довести реставрацию Мэйдзи до завершения `je_meiji_army`-эквивалента (или посмотреть в консоли/логе, добавляется ли стране журнал `je_meiji_army`), и сверить панель отношения Армии к политике «Реставрация Мэйдзи» — враждебность должна быть либо статичной (снят компач не нужен), либо появляться только после завершения военной ветки (компач можно дописывать).

## Итог

Компач: `tools/regen_vc_kai.py` → `_vc/kai+vc done/common/ai_strategies/zz_vc_kai_ai_strategies.txt`, 1 файл, 3 записи (`INJECT:` × 2, `REPLACE_OR_CREATE:` × 1), самопроверка `0 problem(s)`, `--check` сходится.

Пары VC.5 (PSC) и VC.6 (PBE) в этот компач не входят — трогают другие блоки, см. отдельные разборы.
