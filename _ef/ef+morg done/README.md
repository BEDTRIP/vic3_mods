This is part of [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3638078714]this MegaComPatch[/url]
[h1]E&F + Morgenröte ComPatch [1.13][/h1]
[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3146386373]based on Lord R compatch[/url]
[h2]Load order[/h2]
[list]
[*]Community Mod Framework (CMF)
[*]Expanded Topbar Framework (or [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3333043079]Dence UI[/url])
[*]Economic and Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3786286962]my E&F Hotfix[/url] — [b]required[/b], see below
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*]Morgenröte
[*][b]E&F + Morgenröte ComPatch (this mod)[/b]
[/list]

[i]Place your other mods after this only if they do not overwrite the same files in common/.[/i]

[h2]The hotfix is not optional[/h2]
Victoria 3 caps the goods database at 128 entries and crashes on entering a campaign above that — silently, with nothing in error.log. Vanilla ships 53, E&F adds 73, Morgenröte adds 5, which lands on [b]131[/b]. The [b]E&F Hotfix[/b] comments out eight dead currency goods and brings the pair down to [b]123[/b]. Run E&F and Morgenröte together without it and the game will not start.
[h2]What this patch does[/h2]
[list]
[*][b]Adds E&F financial PM-groups to Morgenröte buildings[/b]
[list]
[*]Injects [i]pmg_market_liquidity[/i] into all 62 custom Morgenröte buildings
[*]Adds private ownership stock PM-groups to the ones that can actually be privately owned (Airport, Uranium mine, Opera, Instrument workshops, Manzoni publishing, both Mendelejew plants)
[/list]

[*][b]Extends E&F “private ownership → stocks” switching to Morgenröte buildings[/b]
[list]
[*]A yearly check switches those Morgenröte buildings between stock PMs based on [i]private_ownership_fraction[/i], the same way E&F does for its own buildings
[*]The same switch also runs once at game start from [i]common/history/global/[/i], so the buildings are not stuck on “No Stock” for the whole first year
[/list]

[*][b]Makes E&F inflation scripted values account for Morgenröte goods[/b]
[list]
[*]Adds [i]air_travel[/i], [i]elgar_music[/i], [i]elgar_instruments[/i], [i]manzoni_prints[/i] to the consumer-goods basket and [i]good_uranium[/i] to the raw-material basket
[/list]

[*][b]Tesla project compatibility[/b]
[list]
[*]Allows Tesla construction-sector improvement to target E&F private construction ([i]building_ef_private_construction[/i])
[*]Prevents Tesla mechanical improvements from targeting E&F financial building groups (banks / financial centres / stockpile / private construction)
[/list]
[/list]

[h2]Changes in the 1.13 version[/h2]
[list]
[*]Building list resynced with Morgenröte 2.8.3e: added Andersson Institute, both Curie buildings, both Lepsius monuments and the Elgar Opera; removed the deleted [i]building_gaudi_sagrada[/i]
[*]The Agassiz “Find Silver” journal entry, GUI patch, triggers and localization were [b]removed[/b]. Morgenröte 2.8 replaced the per-ore projects with one “Improve Mining” project that targets [i]bg_mining[/i], and the E&F silver mine’s group [i]bg_silver_mining[/i] is a child of [i]bg_mining[/i], so it is picked up with no patch at all. Keeping the old files would have broken the new geologist UI.
[*]The private-ownership switch is no longer wired in by overriding E&F’s [i]financial_center_ef_on_yearly_pulse_country[/i]; it uses its own on_action instead. Besides overriding nothing, this fixes the old behaviour where Morgenröte buildings only switched in countries that owned a financial centre.
[*]Tesla mechanical improvement trigger resynced with Morgenröte 2.8.3e (adds [i]bg_subsistence_ranching[/i] to the exclusion list)
[/list]

[h2]Notes[/h2]
[list]
[*]This patch is designed to be [b]minimal[/b] and only overrides what’s needed for integration.
[*]Four things here are upstream content plus a short list of deliberate additions: the 62-building liquidity list, the two E&F inflation baskets, and the two Morgenröte Tesla triggers. [i]tools/check_ef_morg_drift.py[/i] in the repo re-derives all four from the current mods and reports anything that moved — run it after every E&F or Morgenröte update.
[*][i]buy_packages[/i] need no patch: E&F uses INJECT and Morgenröte uses TRY_INJECT on the same [i]wealth_*[/i] keys, so both pop needs are applied.
[*][i]building_railway[/i] needs no patch either — both mods inject into it rather than replacing it.
[*]It does [b]not[/b] guarantee compatibility with other mods that also heavily edit the same [b]common/[/b] areas.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
