This is part of [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3638078714]this MegaComPatch[/url]
[h1]Economic and Financial (E&F) + The Great Revision (TGR) ComPatch[/h1]

Compatibility patch for using [b]Economic and Financial (E&F)[/b] together with [b]The Great Revision (TGR)[/b].

Rebuilt 21.08.2026 against [b]TGR 2.0 (1.13.10, 12.08.2026)[/b] and [b]E&F 04.07.2026[/b].

[h2]Load order[/h2]
[list]
[*]Expanded Topbar Framework (or [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3333043079]Dence UI[/url])
[*]The Great Revision (TGR)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637467628]my TGR RU Localization (if u need)[/url]
[*]Economic and Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3786286962]my E&F 1.13.10 Hotfix (strongly recommended)[/url]
[*][b]E&F + TGR ComPatch (this mod)[/b]
[/list]

[i]Load this patch after both mods. The E&F Hotfix and this patch do not touch a single common file or key, so their relative order does not matter.[/i]
[i]Place other mods after this one only if they do not overwrite the same files - especially [b]gui/budget_panel.gui[/b].[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Merges the Budget Panel UI[/b]
[list]
[*]Both mods overwrite [i]gui/budget_panel.gui[/i]. Whichever loads last wins and the other mod's UI silently disappears.
[*]This patch ships a three-way merge of vanilla 1.13.10 + TGR + E&F: TGR's per-tax +/- controls and its fiscal-reform rows, E&F's [i]Economy[/i] / [i]Finance[/i] / [i]Stockpile[/i] tabs and currency symbols, and every 1.13 budget row both mods kept (treaty income, ship construction and maintenance, military upkeep).
[/list]

[*][b]Restores the TGR modifiers that E&F overwrites on shared techs[/b]
[list]
[*]E&F redefines the [i]modifier[/i] block of [i]banking[/i], [i]central_banking[/i], [i]mutual_funds[/i], [i]corporate_charters[/i], [i]joint_stock_companies[/i] and [i]investment_banks[/i], which wipes what TGR put there.
[*]Most importantly [i]state_building_trade_center_max_level_add[/i]: TGR gives +10 on six techs, and four of them were being blanked - about 40 levels of Trade Center ceiling lost by the late game.
[*]The patch re-adds only the missing keys, so a value change on either side no longer drifts out of the patch.
[/list]

[*][b]Disables the TGR "International Loans" module[/b]
[list]
[*]TGR bundles the same loan / interest-rate system as the standalone "TGR International Loans" module. It overlaps E&F's own credit system, so this patch switches it off: journal entry [i]je_international_loans[/i] and buttons [i]tgr_loans_button_1..8[/i].
[*]Its baseline [i]country_loan_interest_rate_add = -0.2[/i] is reset to 0, otherwise vanilla/E&F loans would be handed out at nearly no interest.
[*]This is a design call, not a conflict fix - the two systems do not share a single file or key.
[/list]

[*][b]Pins PRICE_RANGE[/b]
[list]
[*]The one define both mods set (TGR 0.85, E&F 0.99). TGR's trade rework is tuned for the narrow band, so 0.85 wins.
[/list]

[*][b]Adds four missing production method group names[/b]
[list]
[*][i]pmg_private_ownership_*[/i] - E&F names the methods but not the groups.
[/list]
[/list]

[h2]No longer needed (removed 21.08.2026)[/h2]
[list]
[*][b]Company HQ production methods.[/b] Vic3 1.13 database prefixes patch per sub-block: E&F's [i]REPLACE:[/i] only lists [i]building_modifiers[/i], so TGR's [i]state_modifiers[/i] survives on its own. The old merge file was also feeding stale numbers.
[*][b]Buy packages.[/b] The two mods use different file names and E&F only injects, so nothing was ever lost. The patch was shipping a byte-for-byte copy of E&F's file.
[*][b]base_values.[/b] All four patches of it use [i]INJECT:[/i] and merge cleanly.
[*][b]issue_a_loan / apply_for_a_loan.[/b] These diplomatic actions no longer exist in TGR; the old file was creating them from scratch instead of disabling them.
[/list]

[h2]Notes[/h2]
[list]
[*]If you use other UI mods that also replace [i]gui/budget_panel.gui[/i], you will need an additional UI merge patch.
[*][b]Goods ceiling.[/b] Victoria 3 1.13 crashes on entering the game above 128 goods, with nothing in the log. TGR adds no goods; E&F alone brings the build to 126 of 128, and the E&F Hotfix trims that to 118. Count before adding a third mod with new goods.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]