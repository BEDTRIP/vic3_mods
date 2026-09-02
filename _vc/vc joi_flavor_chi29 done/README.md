# Fix: Victorian Century — Chinese Labor Agreement Event Disabled

<!-- meta
пара: VC (одиночный фикс, не пара)
статус: done
версии: Game 1.13 (exe 1.13.11) — VC unpacked 2026-08-25.
позиция: после Victorian Century
файлов: 1
генератор: —
зависит от: —
-->

## Для мастерской

[h1]Fix: Victorian Century — Chinese Labor Agreement Event Disabled[/h1]
[b]Game 1.13 (exe 1.13.11) — VC unpacked 2026-08-25.[/b]

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Victorian Century (VC)
[*][b]this fix[/b]
[/list]

[h2]What this fix does[/h2]
Victorian Century's China flavor event [i]joi_flavor_chi.29[/i] ("Labor Contract with China") is reachable from a topbar button several colonial powers get ([i]common/scripted_buttons/joi_china_buttons.txt[/i], 15 call sites across different countries, all [i]trigger_event = { id = joi_flavor_chi.29 }[/i]). Accepting it creates a migrant pop of 250,000 (up to 1,000,000 for Brazil/UNL/Netherlands) with Standard of Living 100 — the highest tier in the game — in the receiving state. That one pop wrecks the state's economy outright. It reproduces reliably, around year 4 of every game.

[list]
[*][b]Disabling via the event's own `trigger` field does not work.[/b] `trigger` is only checked when an event is picked from a weighted pool/pulse. This event is fired directly by name (`trigger_event`), which never looks at `trigger` at all.
[*][b]Giving the created pops an explicit `pop_type = laborers` does not fix the Standard of Living 100 symptom either[/b] — tested in-game. Whatever actually sets a freshly created pop's SoL here isn't the missing pop_type; the real mechanism is still unknown.
[/list]

Since the cause isn't pinned down but the symptom is 100% reproducible and economy-breaking, this fix disables the event's game effects outright rather than keep guessing. The popup, its title/description/flavor text and both options still show exactly as Victorian Century wrote them — clicking through does nothing to the game state anymore: no created pop, no mass migration, no modifiers.

## Что тут лежит

`events/zzz_joi_flavor_chi_29_fix.txt` — полное переопределение события
`joi_flavor_chi.29` (голый ключ без префикса; порядок решает позиция мода в
плейсете, а не имя файла). Локализация не тронута.

## !! MAINTENANCE !!

Если Victorian Century когда-нибудь сам починит это событие (или найдётся
настоящая причина SoL 100) — переписать эффекты здесь же, возвращая
`create_pop`/`create_mass_migration` с рабочим фиксом, а не заводить ещё один
файл. Проверить также, не переименовал ли автор `common/scripted_buttons/joi_china_buttons.txt`
или сам код события — тогда голое имя ключа могло не совпасть.

Открытый вопрос (не решённый этим фиксом, только обойдённый) — записан в
`План проекта.md`: что именно даёт новосозданному попу SoL 100 в обход
`pop_type`.
