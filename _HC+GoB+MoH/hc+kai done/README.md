# Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven  +  Kuromi's AI ComPatch

<!-- meta
пара: HC+GoB+MoH × KAI
статус: done
версии: —
позиция: —
файлов: 7
генератор: —
зависит от: —
-->

## Для мастерской

This is part of [url=]Addon 1 for the MegaComPatch[/url]
[h1]Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven  +  Kuromi's AI ComPatch[/h1]

Compatibility patch for using the [b]Hail, Columbia! / Gates of the Bosphorus / Mandate of Heaven[/b] block together with [b]Kuromi's AI[/b]. [b]The Great Revision[/b] is a dependency too - see below.

Built 24.08.2026, rebuilt 25.08.2026 without Tech & Res, against [b]Kuromi's AI 7.5[/b], [b]The Great Revision 2.0[/b], [b]Hail, Columbia! 8.6-Roosevelt[/b], [b]Gates of the Bosphorus 4.0.8[/b] and [b]Mandate of Heaven 1.4.6.1[/b].

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]The Great Revision
[*]Kuromi's AI
[*]Hail, Columbia!
[*]Gates of the Bosphorus
[*]Mandate of Heaven
[*][b]this patch[/b]
[/list]

[h2]What this patch does[/h2]
[list]
[*][b]Puts Kuromi's AI back into ai_strategy_default[/b] - the largest single thing this patch fixes
[list]
[*]This is the entry every AI country loads before its own strategy. Kuromi's AI rewrites it from [i]common/ai_strategies/00_default_strategy.txt[/i] (42 changed passages); Mandate of Heaven then [i]REPLACE:[/i]s it with a 9075-line body built on vanilla, and Kuromi's rework disappears.
[*]An AI mod being switched off by a flavour mod produces no error at all - the AI simply plays vanilla again.
[*]The patch ships a three-way merge of Kuromi's AI and Mandate of Heaven against vanilla, so each keeps what it actually changed.
[/list]

[*][b]Puts The Great Revision's three injections back on top of that merge[/b]
[list]
[*]TGR writes the same entry with three [i]INJECT:[/i] files - twelve institutions of its own, three naval unit-group weights, a higher conscription ratio under National Militia, its own diplomatic-play scenarios, and 10 -> 500 on vanilla's police, health system and home affairs. Kuromi's AI ships a bare body at the vanilla path and loads after TGR, so all three are gone before this patch is in the picture; the merged body above would drop them again.
[*]They are re-issued in a second file that sorts after the merge. [i]diplomatic_play_support[/i] is merged (the winning list minus its German Leadership War block, which TGR ships its own version of, plus TGR's scenarios); [i]wanted_construction_output[/i] is left to Kuromi's AI, because both authors rewrote the formula whole and the later mod owns it.
[*]This is why The Great Revision is a dependency of this patch.
[/list]
[/list]

[h2]Checked and deliberately left alone[/h2]
[list]
[*][b]pmg_luxury_building_glassworks.[/b] Both mods inject, injections into a list add up.
[*][b]NAI.[/b] Defines merge per key, and HC's [i]NUM_GROWING_COLONIES_MAX[/i] is not a key Kuromi's AI sets.
[/list]

[h2]Tech & Res[/h2]
[list]
[*]Until 25.08.2026 this patch also covered [b]Tech & Res[/b]: the four slavery laws, [i]je_warlord_china[/i], the Greener Grass decree and T&R's own 1360-line injection into [i]ai_strategy_default[/i]. Tech & Res left the set and those four files went to [i]_to_delete/tr_removed_2026-08-25/[/i]. Each of them carried a T&R body merged into an HC or MoH one, so without Tech & Res installed they would put content from a missing mod into the game.
[*]With T&R gone, TGR's 10 -> 500 on police / health system / home affairs is now restored as well. It used to be left out on purpose: Tech & Res re-stated all seven vanilla institutions at 10 in an injection that loaded later, so restoring TGR's values here would have decided the TGR x T&R pair rather than this one.
[/list]

---

## Подробности

_Пока только описание для мастерской: подробного разбора для этого компача не писали._
