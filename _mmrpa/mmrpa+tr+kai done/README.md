Works with all [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3638078714]my MegaComPatch[/url]
[h1]Make My Railway Profitable Again! (MMRPA) + Tech & Res ComPatch[/h1]
[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Kuromi's AI
[*]Tech & Res
[*]Make My Railway Profitable Again! (MMRPA)
[*][b]ComPatch MMRPA + Tech&Res (this mod)[/b]
[/list]

[i]This patch should be loaded after both mods. Put other mods after it only if they do not touch the same railway production methods / PM groups.[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Fixes railway PM conflicts (balance)[/b]
[list]
[*]Both mods redefine the same vanilla railway production methods. Without a patch, whichever definition is applied last wins.
[*]This patch pins a single consistent set of values for the overlapping railway PMs so results do not depend on load order.
[*]Affected PMs:
[list]
[*][i]pm_steam_trains[/i]
[*][i]pm_steam_trains_principle_transport_3[/i]
[*][i]pm_electric_trains[/i]
[*][i]pm_electric_trains_principle_transport_3[/i]
[*][i]pm_diesel_trains[/i]
[*][i]pm_diesel_trains_principle_transport_3[/i]
[/list]
[/list]

[*][b]Balances Tech &amp; Res “new trains” PMs[/b]
[list]
[*]This patch also defines the Tech &amp; Res train PMs used for late-game railways, to keep railway progression consistent when both mods are enabled.
[*]Affected PMs:
[list]
[*][i]pm_advanced_express_trains[/i]
[*][i]pm_advanced_express_trains_principle_transport_3[/i]
[*][i]pm_high_speed_trains[/i]
[*][i]pm_high_speed_trains_principle_transport_3[/i]
[/list]
[/list]

[*][b]Defines passenger train PM group[/b]
[list]
[*]Provides a final, explicit [i]pmg_passenger_trains[/i] list so passenger-carriage options are stable with both mods enabled.
[/list]
[/list]

[h2]Notes[/h2]
[list]
[*]If you use other mods that also change railway PMs / railway PM groups, you may need an additional merge patch.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]