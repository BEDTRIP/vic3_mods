[h1]Economic and Financial Mod (E&F) + Power Blocks Expanded (PBE) ComPatch[/h1]
[h2]Load order[/h2]
[list]
[*]Expanded Topbar Framework
[*]E&F
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*]PBE
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3490395930]PBE RU Localization (if u need)[/url]
[*][b]E&F + Power Blocks Expanded ComPatch (this mod)[/b]
[/list]

[i]Place your other mods after this only if they do not overwrite the same files in [b]common/[/b].[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Fixes a critical on_actions conflict[/b]
[list]
[*]Both E&F and PBE define the vanilla hook [i]on_monthly_pulse_country[/i]. Without a merge, the mod loaded last overwrites the other one.
[*]This patch merges that hook so [b]both[/b] systems keep running:
[list]
[*]PBE: [i]kates_dynamic_modifier_on_action[/i] (runs 4 times per month via delays)
[*]E&F: [i]ef_on_monthly_pulse_country[/i] (monthly financial maintenance)
[/list]
[/list]
[/list]
