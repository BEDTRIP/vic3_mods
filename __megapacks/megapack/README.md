# Compatibility patch for using these big mods together:

<!-- meta
сборка: мегапак полный
статус: собран
версии: Updated for game 1.13 -- TGR 2.0, PSC 1.3.7, E&F 4.1.7 + Hotfix 4.1.7.4, Morgenröte 2.8.3e, Tech & Res 1.6', KAI 7.5, PBE 1.13.
позиция: —
файлов: 176
генератор: —
зависит от: —
-->

## Для мастерской

[b]NOTE (25.08.2026): this build is no longer maintained.[/b] Tech & Res has been dropped from the set these patches are built for, so every file in here that merges Tech & Res with another mod is unsupported. Use [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3640735868]MegaComPatch TGR + PSC + E&F + MR + PBE[/url] instead.

[h1]Compatibility patch for using these big mods together:[/h1]
[list]
[*][b]The Great Revision (TGR)[/b]
[*][b]Private Sector Construction (PSC)[/b]
[*][b]Economic and Financial (E&F)[/b]
[*][b]Morgenröte[/b]
[*][b]Tech & Res + Kuromi's AI[/b]
[*][b]Power Blocs Expanded (PBE)[/b]
[/list]
[b]Updated for game 1.13 -- TGR 2.0, PSC 1.3.7, E&F 4.1.7 + Hotfix 4.1.7.4, Morgenröte 2.8.3e, Tech & Res 1.6', KAI 7.5, PBE 1.13.[/b]

[h2]The E&F Hotfix is required[/h2]
[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3786286962][b]E&F 1.13 Hotfix[/b][/url] is not optional in this set, and it is [b]not[/b] contained in this megapack -- run it as its own mod, right after E&F.

Victoria 3 1.13 crashes on entering a campaign above [b]128[/b] goods, silently, with nothing in error.log. Vanilla ships 53 and E&F alone brings 126 -- add Tech & Res on top and the game will not start. The hotfix merges E&F's currency goods into one, which puts this whole set at [b]106[/b] of 128 (vanilla 53 + PSC 4 + E&F-with-hotfix 8 + Morgenröte 5 + Tech & Res 35 + this patch's concrete_construction 1; TGR adds no goods of its own).

The hotfix also carries E&F's own bug fixes (the divide-by-zero in the stock demand values, the missing scope in the private bank currency sale) that used to live inside these ComPatches.

[h2]Load order[/h2]
[olist]
[*]Community Mod Framework
[*]Expanded Topbar Framework (or [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3333043079]Dence UI[/url])
[*]The Great Revision (TGR)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637467628]my TGR RU Localization (if u need)[/url]
[*]Private Sector Construction (PSC)
[*]Kuromi's AI (KAI)
[*]Economic and Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3786286962][b]my E&F Hotfix -- required[/b][/url]
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*]Morgenröte
[*]Tech & Res
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3551090576]Tech & Res RU Localization (if u need)[/url]
[*]Power Blocs Expanded (PBE)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3490395930]PBE RU Localization (if u need)[/url]
[*][b]MegaComPatch TGR + PSC + E&F + MR + T&R + PBE (this mod)[/b]
[/olist]

[b]This mod must load after the E&F Hotfix.[/b] It carries its own copy of E&F's company list (with the construction sector renamed for PSC), and it re-applies on top of that copy the two things the hotfix adds to the 98 bank companies -- the bank building and the three regime currencies. In the other order that copy would be the one the hotfix injects into, and the megapack would put E&F's untouched list back on top.

Also works with [url=https://steamcommunity.com/workshop/filedetails/?id=3110785319]MMRPA[/url] if you add it after the megacompatch:
--- all mods above ---
- this MegaComPatch
- Make My Railway Profitable Again!
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3648532892]MMRPA + Tech & Res Compatch[/url]
--- other mods ---

[i]This patch should be loaded after all listed mods. Any other mods should be loaded after the ComPatch.[/i]

[h2]What this patch does[/h2]
This is a merge of [url=https://steamcommunity.com/workshop/filedetails/?id=3585473709]all these ComPatches[/url] -- eight of them for this set. You can check them independently.

Four files exist only here, because they fix things that appear only when several of those patches run in one mod, where files load by name and the last one wins:
[list]
[*][b]Manzoni publishing industry[/b] gets E&F's market liquidity and private stock ownership back -- the MR + T&R patch has to REPLACE the whole building and loads later than the E&F + MR patch's INJECT.
[*][b]Automotive industry and synthetics plant[/b] keep TGR's building groups. The E&F + T&R patch and the TGR + T&R patch both REPLACE these two buildings; without this file the E&F copy wins and both buildings silently drop out of TGR's industry decree and economic-incentive laws.
[*][b]malaria_prevention[/b] keeps both restored lines -- TGR's Environment institution investment and Morgenröte's yellow fever mitigation. Each patch restates the technology to put its own line back, and only one of them can survive.
[*][b]Prefabricated Concrete Buildings[/b] issues E&F manufacture stock like every other construction method. The concrete tier comes from PSC + T&R, which knows nothing about E&F, so researching it used to move the whole construction sector onto a method that produced no stock at all.
[/list]

[h2]Notes[/h2]
[list]
[*]This mod is a merge patch. If you use additional mods that also replace the same files, you may need another (more specific) merge patch.
[*]It replaces [b]gui/budget_panel.gui[/b] with a three-way merge of vanilla + TGR + E&F. Other UI mods that replace the same file need their own merge.
[*]The AI's default strategy is a merge: The Great Revision's injections into [i]ai_strategy_default[/i] are restored on top of Kuromi's AI body, which had been silently dropping them. Kuromi's construction-output formula is kept.
[*]The construction sector is PSC's, not TGR's -- PSC loads after TGR and wins on its own, with or without this patch. Nothing here changes that.
[*]Also you can check more lightweight [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3638941732]no-E&F/no-PSC[/url], [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3640735868]no-T&R[/url] and [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3643003863]no-TGR[/url] megacompatches.
[/list]
if you need some separate compatch you can check [url=https://github.com/BEDTRIP/vic3_mods]my github[/url]

---

## Подробности

_Пока только описание для мастерской: подробного разбора для этого компача не писали._
