This is a compatibility patch for using [b]Better Politics Mod (BPM)[/b] together with [b]The Great Revision (TGR)[/b].

[h2]Load order[/h2]
[list]
[*]The Great Revision
[*]AntiTGR: no Better Politics and German Unification
[*]Better Politics Mod (BPM)
[*][b]ComPatch BPM + TGR (this mod)[/b]
[/list]

[i]This patch is designed for the load order above (TGR -> BPM -> this patch).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Restores/merges starting country history that BPM and TGR both overwrite[/b]
[list]
[*]Ships merged starts for [b]Brazil (BRZ)[/b], [b]China (CHI)[/b], [b]France (FRA)[/b].
[*]Keeps BPM’s country setup variables/effects where needed, while restoring TGR/vanilla parts that would otherwise be lost (e.g. TGR company starts).
[/list]

[*][b]Keeps BPM government types, but makes them work with TGR law variants[/b]
[list]
[*]Replaces BPM’s presidential government types to use [b]has_law_or_variant[/b] checks so TGR’s additional “law variants” still count.
[/list]

[*][b]Adds TGR-only law stances to BPM ideologies (characters + movements)[/b]
[list]
[*]Injects TGR Politics lawgroup stances (election system, legislative process, centralization, working hours, retirement age, salary regulation, etc.) into BPM ideologies.
[*]This makes leaders/agitators and political movements react meaningfully to TGR-only lawgroups/laws, instead of being “neutral by default”.
[/list]

[*][b]Adds TGR “government_*” ideologies to BPM interest groups[/b]
[list]
[*]Injects TGR’s “ideology_government_*” onto BPM IGs on enable, so BPM IGs keep their identity but still have stances for TGR-only law content.
[/list]

[*][b]Restores TGR Tax Panel versions of the base taxation laws[/b]
[list]
[*]Provides the TGR “Tax Panel” definitions for the core taxation laws (consumption / land / per-capita / proportional / graduated), so BPM’s overlap does not break TGR tax panel logic.
[*]Also keeps the relevant tech unlock hook (e.g. [b]currency_standards[/b] unlocking per-capita taxation).
[/list]

[*][b]Fixes BPM UI/script bugs that show up when combined with TGR[/b]
[list]
[*]Fixes BPM cabinet GUI scope for two localized strings so they resolve in all languages (instead of showing raw keys).
[*]Fixes BPM script_value scope errors for IG attraction (reduces error.log spam).
[*]Fixes a division-by-zero edge case during pre-game init in BPM’s “liberal consciousness target” script value.
[/list]
[/list]

[h2]Notes / compatibility[/h2]
[list]
[*]This mod is focused on [b]compatibility (merges + bugfixes)[/b], not on rebalancing BPM or TGR.
[*]If you use other mods that replace the same keys (laws/ideologies/history/government types), you may need an additional merge patch.
[/list]
