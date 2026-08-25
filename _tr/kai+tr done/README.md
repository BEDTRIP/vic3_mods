[h1]ComPatch: Kuromi's AI + Tech & Res[/h1]
[b]Kuromi's AI 7.5, Tech & Res 1.6.[/b]

Split out of the old three-mod TGR + Kuromi + Tech & Res patch on 25.08.2026. This half has nothing to do with The Great Revision — if you run TGR as well, take [i]ComPatch The Great Revision + Tech & Res[/i] and [i]ComPatch The Great Revision + Kuromi's AI[/i] too.

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Kuromi's AI (KAI)
[*]Tech & Res (T&R)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3551090576]Tech & Res RU Localization (if u need)[/url]
[*][b]this ComPatch[/b]
[/list]

[h2]What this patch does[/h2]
One entry: [i]ai_strategy_resource_expansion[/i].

Kuromi's AI rewrites the strategy and gives every resource good an export stance gated on its own [i]kai_has_high_supply[/i] trigger. That list predates Tech & Res, so the seven resource goods T&R adds — uranium, bauxite, copper, common ores, advanced ores, rare earths and gas — are not in it, and the AI never forms an export stance on any of them. Nothing is logged; the stance is simply absent.

The patch re-issues Kuromi's strategy with those seven appended, using the same trigger and the same seven goods T&R itself uses in its colonial-extraction strategy.

[h2]Checked and deliberately not patched[/h2]
[list]
[*][b]ai_strategy_colonial_extraction[/b] — removed from this patch on 23.08.2026. Tech & Res 1.6 ships the merged version itself and loads after Kuromi's AI, so the entry only re-stated what T&R already does.
[*][b]ai_strategy_industrial_expansion[/b] — both authors write a complete, deliberately different strategy. T&R keeps the industry-banned / extraction-economy gate Kuromi's version had, so nothing structural is lost; merging the rest would be a rebalance.
[/list]

[h2]Notes[/h2]
[list]
[*][b]Maintenance:[/b] the whole file rests on Kuromi's [i]kai_has_high_supply[/i] trigger. If KAI renames it, the strategy loads and silently does nothing.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
