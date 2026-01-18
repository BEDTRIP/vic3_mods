This is part of [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3638078714]this MegaComPatch[/url]
[h1]Economic and Financial (E&F) + The Great Revision (TGR) ComPatch[/h1]

Compatibility patch for using [b]Economic and Financial (E&F)[/b] together with [b]The Great Revision (TGR)[/b].

[h2]Load order[/h2]
[list]
[*]Expanded Topbar Framework (or [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3333043079]Dence UI[/url])
[*]The Great Revision (TGR)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637467628]my TGR RU Localization (if u need)[/url]
[*]Economic and Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*][b]E&F + TGR ComPatch (this mod)[/b]
[/list]

[i]This patch should be loaded after both mods. Place other mods after it only if they do not overwrite the same files (especially UI files like [b]gui/budget_panel.gui[/b]).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Fixes the Budget Panel UI conflict[/b]
[list]
[*]Both mods overwrite [i]gui/budget_panel.gui[/i]. Without a merge, the mod loaded last wins and the other UI changes disappear.
[*]This patch ships a merged [i]budget_panel.gui[/i]: it keeps TGR's tax controls and keeps E&F's extra tabs ([i]Economy[/i] / [i]Finance[/i] / [i]Stockpile[/i]).
[/list]

[*][b]Disables TGR “International Loans” module[/b]
[list]
[*]TGR includes its own loan / interest rate system (same content as the standalone “TGR International Loans” module).
[*]This patch disables that module to avoid overlapping mechanics with E&F:
[list]
[*]Journal Entry: [i]je_international_loans[/i]
[*]Diplomatic actions: [i]issue_a_loan[/i], [i]apply_for_a_loan[/i]
[*]Buttons: [i]tgr_loans_button_*[/i]
[/list]
[/list]

[*][b]Merges overlapping technologies[/b]
[list]
[*]Both mods redefine the same tech IDs. This patch merges the key overlaps so you keep the intended effects from both sides where possible:
[list]
[*][i]banking[/i]
[*][i]central_banking[/i]
[*][i]mutual_funds[/i]
[*][i]joint_stock_companies[/i]
[*][i]investment_banks[/i]
[*][i]international_exchange_standards[/i]
[*][i]modern_financial_instruments[/i]
[/list]
[/list]

[*][b]Merges company HQ production methods[/b]
[list]
[*]Both mods touch the same [i]pm_company_headquarter_*[/i] production methods. This patch merges them so you keep TGR trade-capacity additions while preserving E&F employment/share rebalancing.
[/list]

[*][b]Keeps E&F pop needs in TGR buy packages[/b]
[list]
[*]Re-injects [i]popneed_currency[/i] and [i]popneed_financial_products[/i] into [i]wealth_1 .. wealth_99[/i].
[/list]

[*][b]Defines stability[/b]
[list]
[*]Pins key [i]NEconomy[/i] settings so results do not depend on which mod loads last.
[/list]
[/list]

[h2]Notes[/h2]
[list]
[*]If you use other UI mods that also replace [i]gui/budget_panel.gui[/i], you will need an additional UI merge patch.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]