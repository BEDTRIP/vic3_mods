This is a compatibility patch for using [b]Better Politics Mod (BPM)[/b] together with [b]Economic and Financial Mod (E&F)[/b].

[h2]Load order[/h2]
[list]
[*]Expanded Topbar Framework (or [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3333043079]Dence UI[/url])
[*]Economic and Financial Mod (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*]Better Politics Mod (BPM)
[*][b]ComPatch BPM + E&F (this mod)[/b]
[/list]

[i]This patch should be loaded after both mods. Place other mods after it only if they do not overwrite the same UI/script keys (especially IG tooltip GUI and law UI localization).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Fixes Interest Group tooltip UI conflict (icons/layout)[/b]
[list]
[*]Both mods touch the IG tooltip type [b]FancyTooltip_IG[/b]. With load order E&F -> BPM, BPM overwrites E&F's tooltip layout.
[*]This patch re-applies the E&F layout while keeping BPM’s ideology visibility filter.
[/list]

[*][b]Fixes law/UI localization conflicts overwritten by BPM[/b]
[list]
[*]Adds compatibility localization overrides for all languages.
[*]Includes a merged [b]ENACT_LAW[/b] tooltip (E&F checkpoint chances + BPM \"Rigidity\" info) and restores/clarifies several UI keys that had different meaning in E&F vs BPM.
[/list]

[*][b]Merges the key technology conflict: currency_standards[/b]
[list]
[*]Both mods do [b]REPLACE:currency_standards[/b]. Without a merge, E&F's monetary system can break.
[*]This patch ships a merged [b]REPLACE:currency_standards[/b] that keeps E&F's [i]on_researched[/i] hook (fiat activation) and includes BPM prerequisites/modifiers.
[/list]

[*][b]Restores E&F monetary stances after BPM REPLACE ideologies[/b]
[list]
[*]BPM recreates several vanilla ideologies via [b]REPLACE:ideology_*[/b], which wipes E&F's earlier [b]INJECT[/b] blocks.
[*]This patch re-injects E&F monetary law stances for vanilla ideologies and also extends them to BPM-added ideologies, so E&F monetary laws have proper ideology support.
[/list]

[*][b]Integrates E&F monetary ideologies into BPM gameplay[/b]
[list]
[*]Ensures monetary ideologies are assigned via BPM country setup and also when [b]currency_standards[/b] is researched mid-game.
[*]Adds a neutral ideology [b]ideology_monetary_no_policy[/b] for groups that otherwise have no monetary stance, and removes it automatically when a “real” monetary ideology is present (prevents double-stacking).
[/list]

[*][b]Adds E&F monetary ideologies to BPM-style character ideology pools[/b]
[list]
[*]Injects [b]ideology_monetary_*[/b] into [b]character_ideologies[/b] pools so newly generated characters can spawn with them like other BPM ideologies.
[/list]

[*][b]BPM-style icons for monetary ideologies[/b]
[list]
[*]Adds custom icons in [i]gfx/interface/icons/ideology_icons/[/i] ([i]mon_left.dds[/i], [i]mon_liberal.dds[/i], [i]mon_right.dds[/i], [i]mon_placeholder.dds[/i]) and redirects E&F monetary ideology icons to match BPM’s icon style.
[/list]
[/list]

[h2]Notes / compatibility[/h2]
[list]
[*]If you use other UI mods that also redefine the IG tooltip types, you may need an additional UI merge.
[*]If you use other mods that replace [b]currency_standards[/b] (or E&F monetary laws/ideologies), you may need another compatibility patch.
[*]This patch is focused on compatibility (preventing overwrites / missing UI / missing monetary stances), not on rebalancing BPM or E&F.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
