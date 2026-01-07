[h1]ComPatch: Tech & Res + The Great Revision[/h1]
[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]The Great Revision (TGR)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637467628]my TGR RU Localization (if u need)[/url]
[*]Kuromi AI (KAI)
[*]Tech & Res (T&R)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3551090576]Tech & Res RU Localization (if u need)[/url]
[*][b]Tech & Res + TGR ComPatch (this mod)[/b]
[/list]

[i]This patch must be loaded after all required mods. Place other mods after it only if they do not overwrite the same content (especially in [b]common/[/b]).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Fixes “last mod wins” conflicts in common/[/b]
[list]
[*][b]Buildings[/b]: merges overlapping changes to [i]building_automotive_industry[/i] and [i]building_synthetics_plant[/i] (keeps TGR logic, stays compatible with Tech & Res PMG layout).
[*][b]Production methods[/b]: keeps Tech & Res reworked PMs (new goods / new inputs) and adds TGR’s [i]state_market_access_price_impact[/i] for port/train PMs.
[*][b]Laws[/b]:
[list]
[*]Merges Tech & Res extended “destroy building” lists into [i]law_industry_banned[/i] and [i]law_extraction_economy[/i].
[*]Keeps TGR’s centralization swap logic for [i]law_extraction_economy[/i].
[*]Keeps TGR taxation rework and includes Kuromi AI enact weights for [i]law_per_capita_based_taxation[/i] and [i]law_proportional_taxation[/i].
[/list]
[*][b]Company types[/b]: restores TGR versions for overlapping historic companies and extends them with Tech & Res building types where applicable.
[*][b]AI strategies[/b]: restores Tech & Res resource goods stances for Kuromi strategies where they were missing (helps AI use new resources).
[/list]
[/list]

[h2]Notes[/h2]
[list]
[*]This is a [b]compatibility patch[/b], not a rebalance on its own: it only overrides what’s needed to resolve conflicts.
[*]No changes were required in [b]events/[/b] and [b]gui/[/b] for these mods (no overlaps / duplicate IDs found), so this patch focuses on [b]common/[/b].
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]