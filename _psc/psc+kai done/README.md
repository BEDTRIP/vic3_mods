[h1]ComPatch: Private Sector Construction + Kuromi's AI[/h1]
[b]Game 1.13 (exe 1.13.11) — PSC 1.3.7, Kuromi's AI 7.5.[/b]

One entry, and you only need it if you are running these two without a larger compatibility pack — see [i]Not needed with[/i] below.

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Private Sector Construction (PSC)
[*]Kuromi's AI (KAI)
[*][b]this ComPatch[/b]
[/list]

[h2]What this patch does[/h2]
[i]building_construction_sector[/i] is the only key these two mods share.

[list]
[*]PSC rewrites the building and writes its own [i]ai_value[/i]: base 2500, a bonus for states with iron — credited in PSC's own file to KuromiAK — and an extra push toward a country's very first construction sector.
[*]Kuromi's AI injects [i]ai_value[/i] into the same entry and loads later. Sub-blocks merge into the record, but inside one sub-block the engine reads script-value statements in order, and Kuromi's block opens with [i]value = 1000[/i] — which resets everything accumulated before it.
[*]Result with both mods on: PSC's base drops from 2500 to 1000 and the first-sector push is gone. Nothing is logged. The building works; the AI simply stops preferring to get its first construction sector up, which is most of what PSC exists to make it do.
[/list]

The patch re-issues PSC's whole entry after Kuromi's AI, verbatim. A full body rather than just the [i]ai_value[/i] sub-block on purpose: my own notes disagree about whether [i]REPLACE:[/i] patches the sub-blocks a mod names or swaps the entry outright, and a full body is correct either way. The entry is thirty lines, so it is not worth betting on the answer.

Kuromi's own version of the iron rule also requires [i]state_population >= 250000[/i]. PSC dropped that gate deliberately when it adopted the rule, and PSC is the mod that owns this building, so PSC's version is the one kept.

[h2]Not needed with[/h2]
The [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3640735868]MegaComPatch[/url] already ships a full replacement of this building that names [i]ai_value[/i] and carries the same PSC block, and it loads after Kuromi's AI. Do not run both — you would just be replacing the same sub-block twice.

[h2]Notes[/h2]
[list]
[*][b]Maintenance:[/b] the entry is a verbatim copy of PSC's. Re-diff on every PSC update.
[*]This is a [b]compatibility patch[/b], not a rebalance.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
