[b]NOTE (25.08.2026): this build is no longer maintained.[/b] Tech & Res has been dropped from the set these patches are built for, so every file in here that merges Tech & Res with another mod is unsupported. Use [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3640735868]MegaComPatch TGR + PSC + E&F + MR + PBE[/url] instead.

This is the no-E&F, no-PSC version of [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3638078714]this MegaComPatch[/url].
[h1]Compatibility patch for using these big mods together:[/h1]
[list]
    [*][b]The Great Revision (TGR)[/b]
    [*][b]Kuromi's AI (KAI)[/b]
    [*][b]Morgenroete[/b]
    [*][b]Tech & Res (T&R)[/b]
    [*][b]Power Blocs Expanded (PBE)[/b]
[/list]
[b]Updated for game 1.13 -- TGR 2.0, Kuromi's AI 7.5, Morgenroete 2.8.3e, Tech & Res 1.6, PBE 1.13.[/b]

[h2]Load order[/h2]
[olist]
    [*]Community Mod Framework
    [*]The Great Revision (TGR)
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637467628]my TGR RU Localization (if u need)[/url]
    [*]Kuromi's AI (KAI)
    [*]Morgenroete
    [*]Tech & Res
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3551090576]Tech & Res RU Localization (if u need)[/url]
    [*]Power Blocs Expanded (PBE)
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3490395930]PBE RU Localization (if u need)[/url]
    [*][b]MegaComPatch TGR + MR + T&R + PBE (this mod)[/b]
[/olist]

[b]Morgenroete must load before Tech & Res.[/b] Both define the trigger [i]technres_is_active[/i] and the last one loaded wins; with the wrong order Morgenroete stops suppressing its own Steinway company and you get two of it. The dependencies are declared in the metadata, so the launcher normally sorts this on its own.

Also works with [url=https://steamcommunity.com/workshop/filedetails/?id=3110785319]MMRPA[/url] if you add those mods after the megacompatch:
--- all mods above ---
- this MegaComPatch
- Make My Railway Profitable Again!
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3648532892]MMRPA + Tech & Res Compatch[/url]
--- other mods ---

[i]This patch must be loaded after all listed mods. Any other mod should be loaded after the ComPatch.[/i]

[h2]What this patch does[/h2]
It is the merge of my standalone ComPatches for this set, which you can also check independently:
[list]
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637726287]TGR + Kuromi AI + Tech & Res[/url] -- automotive industry and synthetics plant, Extraction Economy, the three colonial laws, ports and railways, goods trade values, AI export stances, and the AI's default strategy: TGR writes it with three INJECT: files and Kuromi's AI ships a bare body over the top, which had been dropping all three.
    [*][b]Morgenroete + Tech & Res[/b] -- airports produce air travel again, Curtiss aviation content follows the new aircraft industry, prestige flights, publishing industry, Morgenroete's technology mechanics, Gaudi's advanced tank options.
    [*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637673379]PBE + TGR[/url] -- merged [i]force_regime_change[/i] diplomatic action.
[/list]
[b]Do not run those three alongside this one[/b] -- this mod already contains them, and every key would be defined twice.

The pairs that need nothing are checked too, and stay unpatched on purpose: Morgenroete + PBE, Morgenroete + TGR, PBE + Tech & Res, Kuromi's AI + Morgenroete.

[h2]Merged inside the megapack[/h2]
[list]
    [*][b]Malaria Prevention[/b] is the only technology both of my patches touch. Here it carries TGR's Environment institution bonus and Morgenroete's yellow-fever mitigation on top of the Tech & Res version, in one entry instead of two.
[/list]

[h2]Notes[/h2]
[list]
    [*]This is a [b]compatibility patch[/b], not a rebalance. Where the two authors simply set a different number for the same thing, the patch leaves it alone and the last mod loaded wins.
    [*]If you use additional mods that replace the same files, you may need another (more specific) merge patch.
    [*][b]Balance note[/b] carried over from the Morgenroete + Tech & Res patch: with air travel restored, the airport stops being the biggest transportation source in the game, exactly as in Morgenroete alone. If late-game transportation runs short, that is why.
[/list]

[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]