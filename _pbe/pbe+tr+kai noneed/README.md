[h1]ComPatch TechRes+Kuromi + Power Blocks Expanded[/h1]
[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]Kuromi AI (KAI)
[*]Tech & Res (T&R)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3551090576]Tech & Res RU Localization (if u need)[/url]
[*]Power Blocks Expanded (PBE)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3490395930]PBE RU Localization (if u need)[/url]
[*][b]TechRes+Kuromi + PBE ComPatch (this mod)[/b]
[/list]

[i]This patch must be loaded after both mods. Place other mods after it only if they do not overwrite the same files (especially [b]common/on_actions[/b]).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Merges conflicting on_actions[/b]
[list]
[*]Both mods define the same root on_action key: [i]on_monthly_pulse_country[/i].
[*]Victoria 3 does not merge these automatically — the last loaded mod wins, and the other mod’s monthly country pulse logic stops running.
[*]This patch ships a merged [i]on_monthly_pulse_country[/i] so [b]both[/b] mods keep working:
[list]
[*]Tech & Res: keeps [i]un_intervention_on_monthly_pulse_country[/i] and [i]yeet_pops_on_monthly_pulse_country[/i].
[*]PBE: keeps its dynamic modifier updates via [i]kates_dynamic_modifier_on_action[/i] (with delays across the month).
[/list]
[/list]
[/list]

[h2]Notes[/h2]
[list]
[*]This is a [b]minimal[/b] compatibility patch: it only overrides what is needed to resolve the [i]on_actions[/i] conflict.
[/list]



---

### Verification note (2026-08-21)

Re-checked T&R 1.6 (build 13.05.2026) + Kuromi AI 7.5 vs PBE (renamed `kates_*` -> `vokaes_*`,
`common/buildings/` removed in 1.13 -- see `сводки по модам/сводка_pbe.md`).

`scan_conflicts.py` T&R vs PBE and KAI vs PBE separately (reports: `conflicts_tr_vs_pbe_report.md`,
`conflicts_kai_vs_pbe_report.md`):

- The only shared `common/` key across both pairs is `on_monthly_pulse_country`
  (T&R: `common/on_actions/ztr_on_actions.txt`, now three hooks -- `un_intervention_on_monthly_pulse_country`,
  `yeet_pops_on_monthly_pulse_country`, `eu_membership_enforcement_on_monthly_pulse_country` --
  vs PBE: `common/on_actions/vokaes_power_bloc_on_actions.txt`, `vokaes_dynamic_modifier_on_action` x4).
  `common/on_actions/` is additive in 1.13 (different files, same key -> both lists fire), so this is not a conflict.
- Zero localization key or event id duplicates in either pair.
- PBE has no `common/goods`, `common/buildings`, `common/building_groups`, `common/laws`,
  `common/law_groups` -- nothing for T&R's building/PM/law content to collide with.
- `.gui`: T&R ships `01_goods_texticons.gui` / `ztr_texticons.gui`, PBE ships
  `power_bloc_panel.gui` / `power_bloc_formation_panel.gui` -- no path or widget-name overlap.

**Conclusion unchanged: no compatch needed.**

Note on the merge file above (`common/on_actions/zz_technres_pbe_on_actions.txt`) and `.metadata/metadata.json`
(`version 1.12.2`, `supported_game_version 1.12.*`): both are leftovers from when this folder was an active
1.12-era patch, built on the (now disproven) assumption that Vic3 does *not* merge same-key `on_actions` across
files. The merge file also references the dead `kates_*` prefix and is missing T&R's third hook added since.
It is not synced to any active mod folder. Left in place for history, per this repo's convention for `noneed`
folders (compare `_pbe/pbe+psc noneed/README.md`) -- do not resurrect or load it.
