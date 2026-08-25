This is part of [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3638078714]this MegaComPatch[/url]
[h1]ComPatch: The Great Revision + Kuromi AI + Tech & Res[/h1]
[b]Updated for game 1.13.10 — TGR 2.0, Kuromi AI 7.5, Tech & Res 1.6.[/b]

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]The Great Revision (TGR)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637467628]my TGR RU Localization (if u need)[/url]
[*]Kuromi AI (KAI)
[*]Tech & Res (T&R)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3551090576]Tech & Res RU Localization (if u need)[/url]
[*][b]this ComPatch[/b]
[/list]
[i]This patch must be loaded after all required mods. Place other mods after it only if they do not overwrite the same content (especially in [b]common/[/b]).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Buildings[/b] — [i]building_automotive_industry[/i] and [i]building_synthetics_plant[/i] are the only two buildings Tech & Res still replaces outright. Merged: Tech & Res PMG layout, TGR building groups (so both keep working with TGR's industry decree and economic-incentive laws).
[*][b]Laws — Extraction Economy[/b] — Tech & Res replaces the on_activate block, which would drop TGR's forced switch from centralization to Local Autonomies. Merged: Tech & Res demolition list + TGR's law swap.
[*][b]Laws — Colonial Affairs[/b] — Tech & Res's UN human-rights rewrite of Colonial Exploitation / Colonial Resettlement / Frontier Colonization drops TGR's [i]institution_modifier[/i]. Restored on top of the Tech & Res versions.
[*][b]Production methods[/b] — ports and railways keep Tech & Res's reworked inputs plus TGR's [i]state_market_access_price_impact[/i].
[*][b]Goods[/b] — aeroplanes, automobiles and clothes keep Tech & Res prices but TGR's traded quantity / convoy cost, so they don't fall out of TGR's trade overhaul.
[*][b]Technologies[/b] — Malaria Prevention keeps TGR's Environment institution bonus alongside the Tech & Res version.
[*][b]AI strategies — the default strategy[/b] — [i]ai_strategy_default[/i] is the entry every AI country loads before its own. The Great Revision writes it with three INJECT: files; Kuromi's AI then ships its own body at the vanilla path with no prefix at all, and a bare body eats every earlier injection. TGR's twelve institutions, its three naval unit weights, its conscription ratio and its diplomatic-play scenarios all stop working the moment KAI is installed, with nothing in the log. Restored, and the diplomatic-play scenarios of both authors merged into one list. The construction-output formula stays Kuromi's -- both authors rewrote it whole and KAI loads later.
[*][b]AI strategies — Resource Expansion[/b] gets the Tech & Res resource goods back into Kuromi's export stances.
[/list]

[h2]Removed in this update[/h2]
[list]
[*][b]Company types[/b] — no longer needed. Tech & Res 1.6 injects its building types instead of replacing whole companies, so the merge happens by itself. The old file also carried outdated copies of TGR companies.
[*][b]Industry Banned[/b] — no longer needed, Tech & Res now injects its demolition list.
[*][b]Taxation laws[/b] — removed; the old override was silently deleting TGR's capitalist political-strength modifier.
[*][b]Colonial Extraction (AI)[/b] — Tech & Res ships the merged version itself now.
[/list]

[h2]Notes[/h2]
[list]
[*]This is a [b]compatibility patch[/b], not a rebalance: it only overrides what would otherwise be lost.
[*]No changes needed in [b]events/[/b] or [b]gui/[/b] — no overlapping IDs or widget names between these mods.
[*]Where both authors set a different number for the same thing (pop needs, women's/children's rights, army-size AI values, AI money-spending defines), the patch leaves it alone: last mod loaded wins, and picking a side would be a rebalance.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
