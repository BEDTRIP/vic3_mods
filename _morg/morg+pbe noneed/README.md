[h1]Morgenröte + Power Blocs Expanded ComPatch[/h1]

Compatibility patch for running [b]Morgenröte[/b] together with [b]Power Blocs Expanded[/b] (PBE).

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Morgenröte
[*]Power Blocs Expanded
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3490395930]PBE RU Localization (if u need)[/url]
[*][b]Morgenröte + PBE ComPatch (this mod)[/b]
[/list]

[i]This patch must be loaded after both mods. Place other mods after it only if they do not overwrite the same files (especially [b]common/on_actions[/b]).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Merges conflicting on_actions[/b]
[list]
[*]Both mods define the same root on_actions keys: [i]on_monthly_pulse[/i] and [i]on_monthly_pulse_country[/i].
[*]Victoria 3 does not merge these automatically — the last loaded mod wins, and the other mod’s pulse logic stops running.
[*]This patch ships merged versions so [b]both[/b] mods keep working:
[list]
[*]Morgenröte: keeps [i]mr_on_monthly_pulse[/i], [i]mr_on_weekly_pulse[/i], and [i]mr_on_monthly_pulse_country[/i].
[*]PBE: keeps its weekly global handler and its dynamic modifier updates (via delayed on_actions).
[/list]
[/list]
[/list]

[h2]Notes[/h2]
[list]
[*]This is a [b]minimal[/b] compatibility patch: it only overrides what is needed to resolve the on_actions conflict.
[/list]