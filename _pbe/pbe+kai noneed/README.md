# KAI × Power Blocs Expanded — компач не нужен

<!-- meta
пара: PBE × KAI
статус: noneed
версии: —
позиция: —
файлов: 0
генератор: —
зависит от: —
-->

Статус поставлен 25.08.2026 при разделении компача `pbe+tr+kai`.
T&R-половина уехала в `_tr/pbe+tr noneed` (она тоже `noneed`).

## Основание

`pair_matrix.py --pair "KAI,PBE"`, прогон 25.08.2026:

```
KAI  x  PBE   ключей: 0   общих путей: 0   общих id событий: 0
```

Сырой вывод `scan_conflicts.py` от 21.08.2026 — `conflicts_kai_vs_pbe_report.md` рядом.

Проверено дополнительно:

* **`common/on_actions`** — единственное место, где эти два мода теоретически встречались бы. У PBE это `vokaes_dynamic_modifier_on_action` в `vokaes_power_bloc_on_actions.txt`; KAI своих `on_actions` не везёт вообще. Даже если бы вёз — категория аддитивна в 1.13: разные файлы, один ключ, оба списка отрабатывают.
* **Товары.** Ни KAI, ни PBE не создают ключей в `common/goods`.
* **`.gui`.** У KAI папки `gui/` нет; у PBE — `power_bloc_panel.gui` и `power_bloc_formation_panel.gui`.
* **Что правит KAI** (`ai_strategies`, `defines/kai_ai.txt`, `ai_weight`, `ai_enact_weight_modifier`, `ai_value`, `ship_types`, свои триггеры) — PBE не трогает ничего из этого: его предмет — блоки держав.

## Историческая заметка

Файл `_tr/pbe+tr noneed/common/on_actions/zz_technres_pbe_on_actions.txt` — остаток 1.12-эпохи, собранный на предположении (позже опровергнутом), что Vic3 не сливает одноимённые `on_actions` из разных файлов. Он не загружается ни в одну сборку и относится к T&R, не к KAI.
