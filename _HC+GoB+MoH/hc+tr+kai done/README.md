This is part of [url=]Addon 1 for the MegaComPatch[/url]
[h1]Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven  +  Tech & Res + Kuromi's AI ComPatch[/h1]

Compatibility patch for using the [b]Hail, Columbia! / Gates of the Bosphorus / Mandate of Heaven[/b] block together with [b]Tech & Res[/b] and [b]Kuromi's AI[/b].

Built 24.08.2026 against [b]Tech & Res 1.6'[/b], [b]Kuromi's AI 7.5[/b], [b]Hail, Columbia! 8.6-Roosevelt[/b], [b]Gates of the Bosphorus 4.0.8[/b] and [b]Mandate of Heaven 1.4.6.1[/b].

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Kuromi's AI
[*]Tech & Res
[*]Hail, Columbia!
[*]Gates of the Bosphorus
[*]Mandate of Heaven
[*][b]this patch[/b]
[/list]

[h2]What this patch does[/h2]
[list]
[*][b]Puts Kuromi's AI and Tech & Res back into ai_strategy_default[/b] - the largest single thing this patch fixes
[list]
[*]This is the entry every AI country loads before its own strategy. Kuromi's AI rewrites it from [i]common/ai_strategies/00_default_strategy.txt[/i] (42 changed passages); Tech & Res injects 1360 lines into it; Mandate of Heaven then [i]REPLACE:[/i]s it with a 9075-line body built on vanilla, and both of the others disappear.
[*]An AI mod being switched off by a flavour mod produces no error at all - the AI simply plays vanilla again.
[*]The patch ships a three-way merge of Kuromi's AI and Mandate of Heaven against vanilla, so each keeps what it actually changed, and re-issues Tech & Res's injection in a second file that loads after it.
[/list]

[*][b]Merges the four slavery laws[/b]
[list]
[*]Tech & Res rewrites [i]law_slave_trade[/i], [i]law_debt_slavery[/i], [i]law_legacy_slavery[/i] and [i]law_colonial_slavery[/i]; Hail, Columbia! rewrites the same four and loads later, so T&R's slavery rework is not in the game.
[*]They barely overlap: T&R writes [i]on_activate[/i] and a [i]can_enact[/i] gate tied to its UN human-rights vote, HC writes a [i]can_enact[/i] gate for the gag rule and the Corwin amendment. [i]can_enact[/i] is a conjunction, so the two sets of conditions simply hold together.
[/list]

[*][b]je_warlord_china[/b]
[list]
[*]Both mods rewrite it, MoH is later. T&R's two additions - the entry can also complete after 1940, and completing it after 1940 fires [i]the_future_of_china.201[/i] instead - are merged back into MoH's version, which builds the completion conditions around its own Chinese content.
[/list]

[*][b]The Greener Grass decree[/b]
[list]
[*]T&R injects a [i]country_trigger[/i] that retires the decree once modern urban planning is researched; HC rewrites the decree without it, so it stays available forever. The trigger is put back.
[/list]
[/list]

[h2]Checked and deliberately left alone[/h2]
[list]
[*][b]pmg_luxury_building_glassworks.[/b] Both mods inject, injections into a list add up.
[*][b]NAI.[/b] Defines merge per key, and HC's [i]NUM_GROWING_COLONIES_MAX[/i] is not a key Kuromi's AI sets.
[/list]

[h2]Known, not fixed here[/h2]
[list]
[*][b]TGR's three injections into ai_strategy_default[/b] are already lost before this patch is in the picture: Kuromi's AI ships its body at the vanilla path and loads after TGR. That belongs to the TGR + Kuromi's AI pair, not to this one.
[/list]
