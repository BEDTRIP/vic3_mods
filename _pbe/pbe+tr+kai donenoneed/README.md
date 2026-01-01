[h1]ComPatch TechRes+Kuromi + Power Blocks Expanded[/h1]
[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Kuromi AI (KAI)
[*]Tech & Res (T&R)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3551090576]Tech & Res RU Localization (if u need)[/url]
[*]Power Blocks Expanded (PBE)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3490395930]PBE RU Localization (if u need)[/url]
[*][b]TechRes+Kuromi + PBE ComPatch (this mod)[/b]
[/list]

[i]This patch must be loaded after both mods. Place other mods after it only if they do not overwrite the same files (especially [b]common/on_actions[/b]).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Merges conflicting on_actions[/b]
[list]
[*]Both mods define the same root on_action key: [i]on_monthly_pulse_country[/i].
[*]Victoria 3 does not merge these automatically — the last loaded mod wins, and the other mod’s monthly country pulse logic stops running.
[*]This patch ships a merged [i]on_monthly_pulse_country[/i] so [b]both[/b] mods keep working:
[list]
[*]Tech & Res: keeps [i]un_intervention_on_monthly_pulse_country[/i] and [i]yeet_pops_on_monthly_pulse_country[/i].
[*]PBE: keeps its dynamic modifier updates via [i]kates_dynamic_modifier_on_action[/i] (with delays across the month).
[/list]
[/list]
[/list]

[h2]Notes[/h2]
[list]
[*]This is a [b]minimal[/b] compatibility patch: it only overrides what is needed to resolve the [i]on_actions[/i] conflict.
[/list]

