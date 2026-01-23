[h1]ComPatch: Morgenrote + Better Politics Mod (BPM)[/h1]

[h2]Load order[/h2]
[list]
[*]Community Mod Framework (CMF)
[*]Morgenröte
[*]Better Politics Mod (BPM)
[*][b]ComPatch Morgenrote + BPM (this mod)[/b]
[/list]

[i]This patch must be loaded after both mods.[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Fixes the hard file overwrite: achievement groups[/b]
[list]
[*]Both mods have [b]common/achievement_groups.txt[/b]. With load order Morgenrote -> BPM, BPM overwrites Morgenrote and you lose Morgenrote achievement groups (and BPM’s file is also incomplete vs vanilla).
[*]This patch ships a merged [b]common/achievement_groups.txt[/b]: keeps BPM’s [b]bpm_achievements[/b] group, restores full vanilla groups, and keeps all Morgenrote groups.
[/list]

[*][b]Restores Morgenrote “active” scripted trigger after BPM[/b]
[list]
[*]BPM’s community compatibility triggers set [b]morgenrote_is_active[/b] to [b]always = no[/b] (breaks checks that depend on “Morgenrote is active”).
[*]This patch restores it via [b]common/scripted_triggers/zzzz_bpm_mr_is_active_trigger.txt[/b].
[/list]

[*][b]Re-applies Morgenrote tech injection lost to BPM REPLACE[/b]
[list]
[*]Morgenrote injects [b]elgar_mass_culture_tech[/b] into vanilla [b]mass_propaganda[/b], but BPM fully [b]REPLACE[/b]s that tech, so the injection is lost with load order Morgenrote -> BPM.
[*]This patch re-injects it after BPM via [b]common/technology/technologies/zzzz_bpm_mr_society_technologies_patch.txt[/b].
[/list]

[*][b]Fixes Swedish Bernadotte ruler templates overwrite[/b]
[list]
[*]BPM [b]REPLACE[/b]s these templates and overwrites Morgenrote’s flavor. This patch reapplies Morgenrote’s [b]MR traits/DNA[/b] but keeps the [b]interest group / ideology[/b] assignment consistent with BPM:
[*][b]swe_karl_johan_bernadotte_template[/b], [b]swe_oscar_bernadotte_template[/b], [b]swe_charles_bernadotte_template[/b], [b]swe_oscar_ii_bernadotte_template[/b], [b]swe_gustaf_v_bernadotte_template[/b]
[/list]
[/list]

[h2]Notes / scope[/h2]
[list]
[*]This patch is focused on resolving confirmed overwrites (files / REPLACE conflicts). It does not try to rebalance laws, parties, political movements, or interest groups.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
