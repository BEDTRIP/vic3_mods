[h1]ComPatch: The Great Revision + Tech & Res[/h1]
[b]Updated for game 1.13.10 — TGR 2.0, Tech & Res 1.6.[/b]

[i]Split 25.08.2026. This used to be one patch for three mods. The Kuromi's AI half moved out: TGR × Kuromi's AI is now [b]ComPatch The Great Revision + Kuromi's AI[/b], and Kuromi × Tech & Res is [b]ComPatch Kuromi's AI + Tech & Res[/b]. Nothing in this patch depends on Kuromi's AI any more — run it with or without.[/i]

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]The Great Revision (TGR)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637467628]my TGR RU Localization (if u need)[/url]
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
[/list]

[h2]Removed in this update[/h2]
[list]
[*][b]Company types[/b] — no longer needed. Tech & Res 1.6 injects its building types instead of replacing whole companies, so the merge happens by itself. The old file also carried outdated copies of TGR companies.
[*][b]Industry Banned[/b] — no longer needed, Tech & Res now injects its demolition list.
[*][b]Taxation laws[/b] — removed; the old override was silently deleting TGR's capitalist political-strength modifier.
[*][b]Colonial Extraction (AI)[/b] — Tech & Res ships the merged version itself now.
[*][b]The two AI-strategy entries[/b] — moved out in the 25.08.2026 split, see the note at the top. Neither of them was about The Great Revision.
[/list]

[h2]Notes[/h2]
[list]
[*]This is a [b]compatibility patch[/b], not a rebalance: it only overrides what would otherwise be lost.
[*]No changes needed in [b]events/[/b] or [b]gui/[/b] — no overlapping IDs or widget names between these mods.
[*]Where both authors set a different number for the same thing (pop needs, women's/children's rights, army-size AI values, AI money-spending defines), the patch leaves it alone: last mod loaded wins, and picking a side would be a rebalance.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
