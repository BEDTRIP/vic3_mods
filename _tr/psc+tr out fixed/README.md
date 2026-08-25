[h1]PSC + Tech & Res ComPatch[/h1]
Private Sector Construction rebuilds construction from the ground up: construction sectors stop handing out abstract construction points and instead produce a local construction good, which a per-state regulator converts into points, billed to the treasury and the investment pool. Tech & Res rebalances the same vanilla construction methods and adds a fifth tier, [i]Prefab Concrete Buildings[/i], which grants 15 construction points directly.

Run both without a patch and two things break. T&R's rebalance of the wooden, iron, steel and arc welded methods is silently overwritten by PSC, which redefines the same entries and loads later. And T&R's concrete tier bypasses PSC's economy completely: it hands you free construction points that cost no construction goods, are never priced and never reach your budget.

This patch reconnects the two. T&R's balance is re-applied on top of PSC, and the concrete tier is converted into PSC's model with its own local good, its own regulator method and its own price.

[h2]Load order[/h2]
[list]
[*]Tech & Res
[*]Kuromi's AI (optional, no patching needed — see below)
[*]Private Sector Construction (PSC)
[*][b]PSC + Tech & Res ComPatch (this mod)[/b]
[/list]

[i]Place other mods after this only if they do not overwrite the same files in common/.[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Puts T&R's construction balance back[/b]
[list]
[*]Iron frame: wood 40→35, iron 50→45, +5 common ores.
[*]Steel frame: steel 50→40, +10 alloys.
[*]Arc welded: steel 50→40, +10 alloys, and the output cut from 150 to 130 construction goods, matching T&R lowering that tier from 15 construction points to 13.
[*]Applied as additive injections, not as copies of the whole method, so PSC's employment, icons and unlock technologies stay PSC's.
[/list]

[*][b]Converts the concrete tier into PSC's economy[/b]
[list]
[*]Adds a fifth construction good, [i]concrete_construction[/i], local like PSC's other four, with its own price, icon and localization.
[*][i]Prefab Concrete Buildings[/i] no longer grants construction points. It produces 150 concrete construction instead — T&R's 15 points at PSC's 10 goods per point — and keeps T&R's inputs and its electricity requirement.
[*]Adds [i]pm_concrete_point_conversion[/i] to the construction regulator so the new good is converted into points and paid for like every other tier.
[*]Extends PSC's tech-driven and sector-driven method pickers, its per-state construction price lookup and its production sum so the concrete tier is seen everywhere the other four are.
[/list]

[*][b]Raises the construction sector level cap for T&R's later technologies[/b]
[list]
[*]PSC's cap only knows vanilla technologies. Prefabricated concrete buildings, highway systems, freight village and modern urban planning now raise it too.
[/list]
[/list]

[h2]Kuromi's AI[/h2]
Nothing to patch. KAI's only overlap with PSC is an injection into [i]building_construction_sector[/i] that nudges the AI toward states with iron, and PSC already carries the same rule inside its own AI value, plus a bonus for a state's first sector. Loading KAI is safe and needs no compatibility file.

[h2]Localization[/h2]
[list]
[*]English
[*]Other — English placeholder
[/list]

[h2]Notes / Compatibility[/h2]
[list]
[*]Goods count with vanilla + PSC + T&R + this patch is 97 of the engine's 128 limit. Adding another large goods mod on top can still cross it, and the game crashes on entering a campaign with nothing in error.log when it does.
[*]It will conflict with other mods that redefine [i]common/production_methods[/i] for the construction sector, PSC's construction script values or PSC's conversion effects.
[*]The construction goods prices carried by this patch (iron 95, steel 95, arc welded 92, concrete 86) are the original author's tuning and were left untouched. They are the first thing to revisit if construction feels mispriced.
[/list]
