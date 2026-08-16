[h1]Economic and Financial Mod (E&F) - V4 + Victorian Century ComPatch[/h1]

[h2]Load order[/h2]
[list]
[*]Expanded Topbar Framework
[*]Economic and Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*]Victorian Century
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3571131201]Victorian Century RU Localization (if u need)[/url]
[*][b]ComPatch E&F + Victorian Century (this mod)[/b]
[/list]

[i]This patch must be loaded after both mods. Place other mods after it only if they do not overwrite the same content (especially [b]common/buy_packages[/b], [b]common/company_types[/b], [b]common/static_modifiers[/b]).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Restores E&F currency / financial products popneeds in VC wealth packages[/b]
[list]
[*]Both mods define the same keys: [i]wealth_1[/i] … [i]wealth_99[/i] in [i]common/buy_packages[/i]. If Victorian Century loads after E&F, it replaces the packages and the E&F injections are lost.
[*]This patch re-applies E&F values via [i]INJECT[/i]:
[list]
[*][i]wealth_1[/i] … [i]wealth_14[/i]: adds [i]popneed_currency[/i]
[*][i]wealth_15[/i] … [i]wealth_99[/i]: adds [i]popneed_currency[/i] + [i]popneed_financial_products[/i]
[/list]
[/list]

[*][b]Restores E&F additions to [i]company_standard_oil[/i][/b]
[list]
[*]Victorian Century overwrites [i]company_standard_oil[/i] and the E&F extra prestige goods are lost.
[*]This patch injects into [i]possible_prestige_goods[/i]: [i]mining_stock_usa[/i], [i]prestige_good_usa_oil[/i].
[/list]

[*][b]Restores E&F injection into [i]base_values[/i][/b]
[list]
[*]Victorian Century overwrites [i]common/static_modifiers/base_values[/i]; E&F expects its minting change to exist.
[*]This patch injects [i]country_minting_add = -500[/i] (plus the E&F icon).
[/list]
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]