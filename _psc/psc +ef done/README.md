[h1]PSC + E&F ComPatch[/h1]
I noticed that E&F’s “private construction sector” mechanics can behave in a strange way: once your economy is strong enough, you can delete all government construction sectors and build [b]for free[/b], because private construction becomes self-sustaining and effectively grants “free construction”, which completely breaks the economy.

This compatch is made to solve that problem. PSC mod turns construction sectors into a separate, fully-fledged market, and E&F now interacts with that market the same way it previously interacted with its own private construction sectors. The “market stimulation” mechanics and the “Overbuilt Economy” crisis mechanics also work properly.

[h2]Load order[/h2]
[list]
[*]Expanded Topbar Framework
[*]Private Sector Construction (PSC)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*]Economic & Financial (E&F)
[*][b]PSC + E&F ComPatch (this mod)[/b]
[/list]

[i]Place other mods after this only if they do not overwrite the same files in common/.[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Unifies the “private construction” building[/b]
[list]
[*]Disables E&F’s separate [i]building_ef_private_construction[/i] (not buildable).
[*]Uses PSC’s [i]building_construction_sector[/i] as the single construction-sector building for both mods.
[*]Injects E&F [i]pmg_market_liquidity[/i] into [i]building_construction_sector[/i].
[*]Keeps PSC construction-sector behavior, but allows E&F monetary/financial mechanics to “see” the construction sector.
[*]Adds an investment score entry so E&F financial district logic can target [i]bg_construction[/i] (since we no longer use [i]bg_ef_private_construction[/i]).
[*]Adds an AI helper value to increase construction-sector priority when construction goods are overpriced.
[/list]

[*][b]Overbuilt Economy debuff extension[/b]
[list]
[*]The "Overbuilt Economy" modifier now affects construction sector outputs differently:
[list]
[*][b]Reduces[/b] PSC construction goods output (wood/iron/steel/arc-welded construction).
[*][b]Increases[/b] E&F [i]manufacture_stock[/i] output.
[/list]
[*]This creates a realistic scenario where overbuilding leads to resource waste while financial speculation intensifies.
[*]The Overbuilt Economy progress is [b]capped at 100%[/b] to prevent excessive penalties.
[*]Pay close attention to this parameter, as it can significantly impact your construction sector productivity.
[/list]

[h2]Localization[/h2]
[list]
[*]English
[*]Russian
[*]Other - English placeholder
[/list]

[h2]Notes / Compatibility[/h2]
[list]
[*]This patch is designed to be [b]minimal[/b] and only overrides what’s needed for PSC + E&F integration.
[*]It will conflict with other mods that heavily overwrite the same areas (especially [i]common/buildings[/i], [i]common/scripted_buttons[/i], [i]common/journal_entries[/i], [i]common/script_values[/i]).
[/list]

