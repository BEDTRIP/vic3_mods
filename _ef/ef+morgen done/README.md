[h1]E&F + Morgenröte ComPatch [1.12][/h1]
[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3146386373]based on Lord R compatch[/url]
[h2]Load order[/h2]
[list]
[*]Community Mod Framework (CMF)
[*]Expanded Topbar Framework
[*]Economic and Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*]Morgenröte
[*][b]E&F + Morgenröte ComPatch (this mod)[/b]
[/list]

[i]Place your other mods after this only if they do not overwrite the same files in common/.[/i]
[h2]What this patch does[/h2]
[list]
[*][b]Adds E&F financial PM-groups to Morgenröte buildings[/b]
[list]
[*]Injects [i]pmg_market_liquidity[/i] into many custom Morgenröte buildings
[*]Adds private ownership stock PM-groups where relevant (e.g. Airport / Uranium mine / publishing & industry buildings)
[/list]

[*][b]Extends E&F “private ownership → stocks” switching to Morgenröte buildings[/b]
[list]
[*]Adds an additional yearly check so Morgenroete buildings switch correctly based on [i]private_ownership_fraction[/i]
[/list]

[*][b]Makes E&F inflation scripted values account for Morgenröte goods[/b]
[list]
[*]Adds Morgenroete goods to E&F inflation calculations (including: [i]air_travel[/i], [i]elgar_music[/i], [i]manzoni_prints[/i], [i]elgar_instruments[/i], [i]good_uranium[/i])
[/list]

[*][b]Agassiz geology integration (Silver)[/b]
[list]
[*]Adds “Find Silver” support so Agassiz geology can target E&F [i]building_silver_mine[/i] (JE + GUI + triggers)
[/list]

[*][b]Tesla project compatibility[/b]
[list]
[*]Allows Tesla construction-sector improvement to target E&F private construction ([i]building_ef_private_construction[/i])
[*]Prevents Tesla mechanical improvements from targeting E&F financial building groups (banks / financial centres / stockpile / private construction)
[/list]
[/list]

[h2]Notes[/h2]
[list]
[*]This patch is designed to be [b]minimal[/b] and only overrides what’s needed for integration.
[*]It does [b]not[/b] guarantee compatibility with other mods that also heavily edit the same [b]common/[/b] areas.
[/list]