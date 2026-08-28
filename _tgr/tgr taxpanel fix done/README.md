# ComPatch: The Great Revision — Tax Panel Clamp Fix

<!-- meta
пара: TGR (одиночный фикс, не пара)
статус: done
версии: Game 1.13 (exe 1.13.11) — TGR 2.0.
позиция: после The Great Revision
файлов: 1
генератор: —
зависит от: —
-->

## Для мастерской

This is part of [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3640735868]this MegaComPatch[/url]
[h1]ComPatch: The Great Revision — Tax Panel Clamp Fix[/h1]
[b]Game 1.13 (exe 1.13.11) — TGR 2.0.[/b]

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]The Great Revision (TGR)
[*][b]this ComPatch[/b]
[/list]

[h2]What this patch does[/h2]
The Great Revision replaces the budget panel with five independent tax sliders. How high each one may go is set by your taxation law — a script value called [i]calculate_max_..._tax_level[/i]. That cap never applies.

[list]
[*]The clamp is written as [i]change_variable = { name = tgr_land_tax min = calculate_max_land_tax_level }[/i] — a lower bound where an upper bound was meant, in all five taxes. The "−" buttons carry the mirror image of the same typo, [i]max = 0[/i] where [i]min = 0[/i] was meant.
[*]Neither fires at all: [i]change_variable[/i] ignores min/max when no add/subtract/multiply/divide is given — vanilla uses [i]clamp_variable[/i] for this everywhere.
[*]So the cap is enforced by one thing only: the +/− buttons are greyed out on exact equality with the cap. Step by 0.5 or 1.0 and you step over that equality and can keep going with no limit at all.
[*]And switching to a taxation law with a lower cap does not bring an already-set rate down — the modifier stays on the country with its old multiplier.
[/list]

This is not a cosmetic difference. Vanilla's own maximum for the same modifiers, at the "Very High Taxes" level, is [i]tax_land_add = 1.00[/i] and [i]tax_consumption_add = 0.35[/i]. TGR's caps are 3 and 0.75 — three times and twice anything the base game can produce. A country that walks the land tax up to 3 with consumption tax at 0.75 destroys its own peasantry: poll taxes at 44% of lower-strata income plus consumption taxes at 145%, standard of living collapsing, beggars appearing.

The patch re-issues [i]tgr_set_max_taxation_effect[/i] with the five dead clamps replaced by explicit if + set_variable that cut the variable down to the law's cap and up to zero. Everything else in the effect is TGR's own body, verbatim. TGR calls this effect on [i]on_law_activated[/i] and on [i]on_half_yearly_pulse_country[/i], for the player only — the AI has its own branch, untouched. So an overshoot is now pulled back at the next law you pass or the next half-year pulse, whichever comes first.

The buttons themselves still do not clamp their own step; fixing those means re-issuing thirty scripted GUIs (five taxes × six buttons) for the same result with less delay. Judged not worth it. If we ever do it, it is a separate file.

## Что тут лежит

`common/scripted_effects/zz_tgr_taxpanel_clamp_fix.txt` — одна запись,
`REPLACE_OR_CREATE:tgr_set_max_taxation_effect`. Простой повтор ключа для
`scripted_effects` не переопределяет, префикс обязателен.

Как это было найдено: партия за Россию 1836–1840, автосейвы показывают
`tgr_land_tax` 1.5 → 1.75 → 2.0 ровно шагами кнопки +0.25 — то есть кламп
`min = 3` не подтягивал значение к потолку ни на одном полугодовом пульсе,
а `max = 0` на кнопке «−» не обнулял. Оба мертвы.

## !! MAINTENANCE !!

Тело выведено из `TheGreatRevision/common/scripted_effects/TGR_TAX_PANEL_scripted_effects.txt`
(TGR 2.0, 12.08.2026), функция `tgr_set_max_taxation_effect`, строки 176–272.
Изменены ровно первые пять блоков, остальное скопировано дословно.
После обновления TGR: сверить тело; если автор поправил `min` → `max` сам —
файл удалить целиком, а не держать копию. Проверить заодно, не появился ли
шестой налог и не поменялись ли имена `calculate_max_*_tax_level`.
