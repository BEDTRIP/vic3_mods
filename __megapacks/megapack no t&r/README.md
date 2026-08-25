[b]NOTE (25.08.2026): this is now the main build, and it now covers Kuromi's AI.[/b] Tech & Res has been dropped from the set; the full MegaComPatch, the no-TGR build and the no-E&F/no-PSC build all carry it and are no longer maintained.
[h1]Compatibility patch for using these big mods together:[/h1]
[list]
    [*][b]The Great Revision (TGR)[/b]
    [*][b]Private Sector Construction (PSC)[/b]
    [*][b]Kuromi's AI (KAI)[/b]
    [*][b]Economic and Financial (E&F)[/b]
    [*][b]Morgenroete[/b]
    [*][b]Power Blocs Expanded (PBE)[/b]
[/list]
[b]Updated for game 1.13 -- TGR 2.0, PSC 1.3.7, Kuromi's AI 7.5, E&F 4.1.7, Morgenroete 2.8.3e, PBE 1.13.[/b]

[h2]The E&F Hotfix is required[/h2]
[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3786286962][b]E&F 1.13 Hotfix[/b][/url] is not optional in this set, and it is [b]not[/b] contained in this megapack -- run it as its own mod, right after E&F.

Victoria 3 1.13 crashes on entering a campaign above [b]128[/b] goods, silently, with nothing in error.log. Vanilla ships 53 and E&F alone brings 126. Add PSC's 4 and Morgenroete's 5 and the game will not start. The hotfix merges E&F's currency goods into one, which puts this whole set at [b]69[/b] of 128. (Counted over the whole chain in load order on 25.08.2026: vanilla 53, hotfix 7, Morgenroete 5, PSC 4. TGR ships a goods file but only replaces vanilla entries, and Kuromi's AI has no goods folder at all.)

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
    [*]Morgenroete
    [*]Power Blocs Expanded (PBE)
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3490395930]PBE RU Localization (if u need)[/url]
    [*][b]MegaComPatch TGR + PSC + KAI + E&F + MR + PBE (this mod)[/b]
[/olist]

[b]This mod must load after the E&F Hotfix.[/b] It carries its own copy of E&F's company list (with the construction sector renamed for PSC), and it re-applies on top of that copy the two things the hotfix adds to the 98 bank companies -- the bank building and the three regime currencies. In the other order that copy would be the one the hotfix injects into, and the megapack would put E&F's untouched list back on top.

Also works with [url=https://steamcommunity.com/workshop/filedetails/?id=3110785319]MMRPA[/url] if you add it after the megacompatch:
--- all mods above ---
- this MegaComPatch
- Make My Railway Profitable Again!
--- other mods ---

[i]This patch must be loaded after all listed mods. Any other mod should be loaded after the ComPatch.[/i]

[h2]What this patch does[/h2]
It is the merge of my standalone ComPatches for this set, which you can also check independently:
[list]
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3640702353]E&F + PSC[/url] -- construction is handed over to PSC: E&F's free private construction sector is disabled and its monetary layer rewired onto PSC's sector, Overbuilt Economy is held at zero on purpose, plus one PSC scope bug.
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637341756]E&F + Morgenroete[/url] -- market liquidity in all 62 Morgenroete buildings, private-ownership stock switching extended to them, Morgenroete goods added to E&F's inflation baskets, Tesla project compatibility.
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637554948]E&F + TGR[/url] -- three-way merge of [i]gui/budget_panel.gui[/i], the TGR tech modifiers E&F was blanking (about 40 levels of Trade Center ceiling), TGR's International Loans module switched off in favour of E&F's credit system, PRICE_RANGE pinned to TGR's 0.85.
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637673379]PBE + TGR[/url] -- merged [i]force_regime_change[/i] diplomatic action.
    [*][b]TGR + Kuromi's AI[/b] -- [i]ai_strategy_default[/i], the strategy every AI country loads before its own. TGR writes it with three injections; Kuromi's AI ships its whole default strategy as a bare body at the vanilla path, and a bare body eats every injection that came before it. TGR's twelve institutions, its 10 -> 500 on police / health system / home affairs, its three naval unit weights, its conscription ratio and its unification-war scenarios all stop working the moment Kuromi's AI is installed, with nothing in the log. Restored here, with the diplomatic-play scenarios of both authors merged into one list. The construction-output formula stays Kuromi's -- both authors rewrote it whole and Kuromi's loads later.
[/list]
[b]Do not run those four alongside this one[/b] -- this mod already contains them, and every key would be defined twice.

The pairs that need nothing are checked too, and stay unpatched on purpose: E&F + PBE, Morgenroete + PBE, Morgenroete + PSC, Morgenroete + TGR, PBE + PSC, PSC + TGR, and -- checked on 25.08.2026 -- Kuromi's AI + E&F, Kuromi's AI + Morgenroete, Kuromi's AI + PBE.

[h2]Merged inside the megapack[/h2]
[list]
    [*][b]Kuromi's AI and the construction sector.[/b] Kuromi's AI injects its own [i]ai_value[/i] into [i]building_construction_sector[/i] and loads after PSC. Inside one sub-block the engine reads script-value statements in order and Kuromi's block opens with [i]value = 1000[/i], which resets what came before -- so on its own it would drop PSC's base of 2500 and PSC's push toward a country's first sector. The megapack's own construction-sector file is a full replacement that names [i]ai_value[/i] and loads last, and it already carries PSC's block -- which is Kuromi's own iron rule, credited to KuromiAK in PSC's file, plus PSC's additions. So nothing is lost and no extra file is needed. [b]This holds only while the megapack loads after Kuromi's AI.[/b]
    [*][b]pmg_private_ownership_* names.[/b] Three of the four patches ship the same localization file. The megapack keeps the E&F + TGR version, which only names the four production method [i]groups[/i] -- E&F has defined the method names itself since the 04.07.2026 build, and localization is won by the first file to define a key, so the older copies were dead weight.
[/list]

[h2]Notes[/h2]
[list]
    [*]This is a [b]compatibility patch[/b], not a rebalance. Where the two authors simply set a different number for the same thing, the patch leaves it alone and the last mod loaded wins. The two deliberate exceptions are PRICE_RANGE and the TGR loan interest baseline, both explained in the E&F + TGR patch.
    [*][b]Known gap[/b] carried over from the E&F + PSC patch: E&F and PSC both redefine the vanilla [i]construction_panel[/i] and the state building list, in different files. One of them loses. This is not merged yet.
    [*]If you use other UI mods that also replace [i]gui/budget_panel.gui[/i], you will need an additional UI merge patch.
    [*]If you use additional mods that replace the same files, you may need another (more specific) merge patch.
[/list]

[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
