# Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven  +  Morgenröte ComPatch

<!-- meta
пара: HC+GoB+MoH × Morgenröte
статус: done
версии: —
позиция: —
файлов: 5
генератор: —
зависит от: —
-->

## Для мастерской

This is part of [url=]Addon 1 for the MegaComPatch[/url]
[h1]Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven  +  Morgenröte ComPatch[/h1]

Compatibility patch for using the [b]Hail, Columbia! / Gates of the Bosphorus / Mandate of Heaven[/b] block together with [b]Morgenröte - Dawn of Flavor[/b].

Built 24.08.2026 against [b]Morgenröte 2.8.3e[/b], [b]Hail, Columbia! 8.6-Roosevelt[/b], [b]Gates of the Bosphorus 4.0.8[/b] and [b]Mandate of Heaven 1.4.6.1[/b].

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Morgenröte
[*]Hail, Columbia!
[*]Gates of the Bosphorus
[*]Mandate of Heaven
[*][b]this patch[/b]
[/list]
[i]Mandate of Heaven must load after Hail, Columbia! - that is a requirement of those two mods, not of this patch.[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Gives Gaudí's capital expansion its modifiers back[/b]
[list]
[*]Gates of the Bosphorus ships a stub of [i]gaudi_capital_expansion_level_4_modifier[/i] with nothing in it but an icon, so that its Byzantium journal entry still resolves when Morgenröte is absent. Sensible on its own - but GoB loads later and a bare body replaces the whole entry, so with both mods installed the level 4 modifier loses all eight of its state modifiers.
[*]No error: the modifier still exists, it just does nothing.
[/list]

[*][b]One Olympics instead of two[/b]
[list]
[*]Morgenröte hides the vanilla [i]revive_olympic_games_decision[/i] because it replaces it with a whole mechanic - journal entry, scripted GUI, character traits, production methods. Gates of the Bosphorus rewrites the same decision into a Greek one and loads later, so as shipped you get both.
[*]This patch re-issues Morgenröte's suppression. Greece loses one flavour decision; Morgenröte's Olympics stay.
[/list]

[*][b]Walter Chrysler and Mark Twain keep both jobs[/b]
[list]
[*]Both mods define these two character templates. Morgenröte gives them roles ([i]character_role_tesla_engineer[/i], [i]character_role_manzoni_writer[/i]) and an [i]on_created[/i] that registers them with its own systems; Hail, Columbia! makes Chrysler an executive of Basic Motors and Twain an agitator, with bare bodies that replace the entries outright.
[*]The patch keeps HC's bodies and puts Morgenröte's role, its two mechanic-bearing traits and its [i]on_created[/i] back on top.
[/list]

[*][b]Restores the achievements screen[/b]
[list]
[*][i]common/achievement_groups.txt[/i] has no top-level keys, so it can only be overridden by path, and the last mod takes the whole file. Mandate of Heaven is last, which drops all twelve Morgenröte achievement groups - roughly sixty achievements - and also [i]achievement_exactly_100[/i], which MoH's copy of the vanilla file predates.
[*]The patch ships MoH's file with the vanilla achievement put back and Morgenröte's groups appended.
[/list]
[/list]

[h2]Checked and deliberately left alone[/h2]
[list]
[*][b]Twenty character portraits.[/b] Gates of the Bosphorus carries its own copies of eighteen [i]common/dna_data/mr_*.txt[/i] files and Hail, Columbia! of two [i]ecchi_usa_*.txt[/i]. They win by load order, and the differences are portrait genes only (mostly [i]gene_stubble[/i]) - deliberate variants of Morgenröte's own characters, not stale copies. Nothing to merge.
[*][b]pmg_luxury_building_glassworks.[/b] Morgenröte, Tech & Res and Mandate of Heaven all [i]INJECT:[/i] into it with different production methods. Injections into a list add up.
[*][b]community_framework_is_active.[/b] Every CMF-aware mod declares the fallback; CMF itself overrides it. Normal, not a conflict.
[/list]

---

## Подробности

_Пока только описание для мастерской: подробного разбора для этого компача не писали._
