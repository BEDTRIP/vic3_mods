# KAI × E&F+hotfix — компач не нужен

<!-- meta
пара: E&F × KAI
статус: noneed
версии: —
позиция: —
файлов: 0
генератор: —
зависит от: —
-->

Статус поставлен 25.08.2026 при разделении компача `ef+tr+kai` на T&R-половину и KAI-половину.
T&R-половина уехала в `_tr/ef+tr out fixed`; KAI в ней не было ни одной строки.

## Основание

`pair_matrix.py --pair "KAI,E&F+hotfix"`, прогон 25.08.2026:

```
KAI  x  E&F+hotfix   ключей: 0   общих путей: 0   общих id событий: 0
```

Ноль по всем трём осям. Проверено дополнительно то, чего скрипт не ловит:

* **Товары.** KAI не везёт `common/goods` вообще — потолок 128 не трогает.
* **Что KAI вообще правит:** `common/ai_strategies`, `common/defines/kai_ai.txt`, `ai_weight` техов, `ai_enact_weight_modifier` законов, `ai_value` двух зданий, `ai` у двух статей договоров, `common/ship_types`, свои `scripted_triggers` и `script_values`. E&F не трогает ничего из этого списка: его предмет — деньги, банки, компании и производственные методы.
* **`.gui`.** У KAI папки `gui/` нет.
* **Порядок загрузки.** Вывод от порядка не зависит: пересечения нет ни в одну сторону.

Прежняя формулировка того же вывода — в README компача `_tr/ef+tr out fixed`, раздел про Kuromi's AI: «zero shared keys, localisation keys, event ids or file paths. The "kai" in the compatch's folder name does not correspond to anything inside it».

## Что перепроверить при обновлении

Если KAI начнёт трогать `common/production_methods`, `common/companies` или `common/buildings` шире, чем `ai_value`, — пересчитать пару.
