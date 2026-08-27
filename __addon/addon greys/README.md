# Addon: Grey's pack × MegaComPatch

<!-- meta
сборка: аддон Grey's
статус: собран
версии: —
позиция: после всей пачки Grey's, перед косметикой
файлов: 31
генератор: tools/build_addon_greys.py, tools/regen_addon_greys.py
зависит от: —
-->

## Для мастерской

[h1]Addon: Grey's pack × MegaComPatch[/h1]

Compatibility layer that puts the [b]Grey's pack[/b] (Soft Econ, Soft Pop, Urban Synergy Unleashed, Deeper Sinosphere, Food Industries Rework, Ranch Production Rework, Diplomatic Interaction Suite, Subject Interaction Suite) on top of the [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3640735868]MegaComPatch[/url] set and [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3790590434]addon-LLWA[/url]. Merge of eight ComPatches for this block -- PSC, PBE, E&F+Hotfix, Morgenröte, The Great Revision, Kuromi's AI, addon-LLWA, megapack no-t&r -- plus four fixes for bugs inside the Grey's pack itself.

Also run [b]Victorian Century[/b] or [b]Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven[/b]? Those two branches are alternatives to each other upstream of this addon (see their own addons: [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3790297983]Addon: Victorian Century x MegaComPatch[/url] / [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3790462515]Addon: HC + GoB + MoH x MegaComPatch[/url]). Grab the matching separate compatch -- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3791187670]ComPatch Grey's + VC[/url] (plus [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3791187149]ComPatch Grey's + addon-VC[/url] if you also run that addon) for the VC branch, or [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3791187490]ComPatch Grey's + HC+GoB+MoH[/url] for the HC branch -- and load it right after this addon. This addon itself carries no VC or HC content, on purpose.

[h2]Load order[/h2]
[list]
[*]the whole MegaComPatch set, in its own order
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3790590434]addon-LLWA[/url] (LLWA + its own compatches)
[*]the Grey's pack (soft_econ, soft_pop, usu, cinosphere, food, ranch, diplo, subject)
[*][b]this addon[/b]
[*]then, only in your branch: [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3791187670]ComPatch Grey's + VC[/url] / [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3791187149]+ addon-VC[/url], or [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3791187490]ComPatch Grey's + HC+GoB+MoH[/url]
[/list]

[h2]What it fixes[/h2]
[list]
[*][b]Private Sector Construction's model survives.[/b] Grey's USU rewrites the same construction system and loads last, wiping PSC's goods chain, privatised building group and merged AI weighting whole.
[*][b]Power Blocs Expanded's relaxations survive.[/b] grey_subject renames the same diplomatic action PBE tweaks and drops PBE's game-rule-gated relaxations and infamy incident.
[*][b]E&F's liquidity/stock economy survives on five buildings[/b] Grey's re-declares, and picks up four brand-new USU buildings E&F never heard of.
[*][b]Morgenröte's hospital group, Russian declension for 30 buildings, and a standard-of-living field survive[/b] against USU's rebuilt bodies.
[*][b]The Great Revision's country ranks, four citizenship laws, four defines, trade-center level cap, and seven ownership production methods survive.[/b]
[*][b]Kuromi's AI construction priority and a wargoal-scope bugfix survive[/b] against USU's and grey_diplo's rewrites.
[*][b]addon-LLWA's railway company extensions and job-attractiveness bonus survive[/b] against USU's rail rewrite; the airport and the new USU railway-line building keep both mods' production groups.
[*][b]The no-t&r megapack's airport and national-park wiring survives[/b] against USU's full-body redeclare.
[*][b]Four bugs inside the Grey's pack itself, fixed:[/b] a CMF compatibility-registry flag that silently stayed off, two production methods losing a transport-cost field to a neighbour, a diplomatic action reverting to an older/typo'd body, and three companies with a typo'd double-colon prefix that silently never loaded.
[/list]

[h2]Compatibility[/h2]
[list]
[*]Carries no Victorian Century or Hail, Columbia!+GoB+MoH content -- see above.
[*]Adds no goods. The set stays at 74 of the 128 ceiling.
[/list]
if you need any separate compatch grey's with any mod in pack you can check [url=https://github.com/BEDTRIP/vic3_mods]my github[/url]

---

Built 27.08.2026 for game 1.13 (exe 1.13.11), the day the whole Grey's block (GR.1-21 minus GR.21 itself, which is not a Grey's pair) closed out.

This is the addon layer for the **Grey's pack**. The megapack and addon-LLWA cover their own blocks below it; this is the layer that closes the Grey's block against everything below.

It is a merge of twelve compatches kept separately in the repository:

| compatch | pair | files |
| --- | --- | --- |
| `_greys/greys+psc done` | Grey's × PSC (GR.2) | 4 |
| `_greys/greys+pbe done` | Grey's × PBE (GR.3) | 1 |
| `_greys/greys+ef done` | Grey's × E&F+Hotfix, incl. new-content GR.15 (GR.5) | 6 |
| `_greys/greys+morg done` | Grey's × Morgenröte (GR.6) | 3 |
| `_greys/greys+tgr done` | Grey's × The Great Revision (GR.7) | 8 |
| `_greys/greys+llwa done` | Grey's × addon-LLWA (GR.9 / GR.16) | 4 |
| `_greys/greys+megapack done` | Grey's × megapack no-t&r (GR.17) | 1 |
| `_greys/greys_diplo_fix done` | internal -- bare CMF registry flag (GR.11) | 1 |
| `_greys/greys_food_fix done` | internal -- usu × food cooling-method losses (GR.14) | 1 |
| `_greys/greys_subject_fix done` | internal -- diplo × subject trade_states loss (GR.14) | 1 |
| `_greys/greys_usu_fix done` | internal -- double-colon prefix typo (GR.20) | 1 |
| `_greys/greys_kai_fix done` | Grey's × Kuromi's AI (GR.8) | 2 |

Every file is generated by each pair's own `tools/regen_greys_*.py`, out of the mods themselves, and assembled by `tools/build_addon_greys.py`. Nothing here is hand-edited.

**Deliberately NOT merged in — three branch-specific compatches, mirroring the `_HC+GoB+MoH/hc+vc done` precedent:**

| compatch | pair | why excluded |
| --- | --- | --- |
| `_greys/greys+vc done` | Grey's × VC (GR.1, 129 keys) | VC-branch only |
| `_greys/greys+addon-vc done` | Grey's × addon-VC (GR.18) | VC-branch only |
| `_greys/greys+hc done` | Grey's × HC+GoB+MoH (GR.4) | HC-branch only |

VC and HC+GoB+MoH are alternatives to each other upstream of this addon (see `План проекта.md`, "Целевой порядок запуска") — not layers stacked on top of one another. A player picks one branch, so a compatch against the *other* branch's mod is dead weight at best and, if it named a path the running branch does not have, a wasted file at worst. Since the target load order converges into a common tail before Grey's loads, the Grey's pack and this addon are shared by both branches, but a VC- or HC-specific compatch against Grey's is not: each ships as its own separate compatch, loaded right after this addon, only in its own branch. `tools/build_addon_greys.py` checks at build time (not just asserts) that none of these three collide on a file path with the twelve merged in, so nothing here needs the tag+`.off` treatment either.

## Load order

```
Community Mod Framework
Expanded Topbar Framework (or Dense UI)
The Great Revision
Private Sector Construction
Kuromi's AI
Economic and Financial (E&F)
E&F Hotfix
Morgenröte
Power Blocs Expanded
MegaComPatch (TGR + PSC + KAI + E&F + MR + PBE — the no-T&R build)
LLWA + addon-LLWA
Grey's pack (soft_econ, soft_pop, usu, cinosphere, food, ranch, diplo, subject)
>>> this addon <<<
then, in your branch only:
  ComPatch Grey's + VC (+ ComPatch Grey's + addon-VC, if installed)   -- VC branch
  ComPatch Grey's + HC+GoB+MoH                                        -- HC branch
```

## The one addon-only merge

Two of the twelve compatches touch overlapping records: `greys+ef done`'s `zz_greys_ef_buildings_inject.txt` `TRY_INJECT:`s E&F's production-method groups onto five buildings; `greys+tgr done`'s `zz_greys_tgr_food_industry.txt` / `zz_greys_tgr_trade_center.txt` `REPLACE_OR_CREATE:` two of those same five whole, each naming its own group list without E&F's entries. Copied into the addon as separate files, TGR's full body — naming none of E&F's fields — would sort after E&F's and silently wipe the injection again, the same class of collision documented for addon-VC's `buy_packages` merge (`tools/regen_addon_vc.py`). `tools/regen_addon_greys.py` builds `common/buildings/zzzz_addon_greys_buildings.txt` instead: TGR's body plus E&F's groups folded into the same list for the two contested buildings, and E&F's own injection carried over verbatim for the other three (`building_livestock_ranch`, `building_port`, `building_power_plant`, which no other compatch touches) — so the whole `zz_greys_ef_buildings_inject.txt` and both TGR building files can be excluded from the plain per-compatch copy as one unit without losing anything. Generated fresh every build, never hand-edited.

Two more duplicate top-level keys survive inside the addon and are declared safe in `tools/build_addon_greys.py`'s `DECLARED_DUPS`, both genuinely additive (disjoint fields, no REPLACE on either side): `building_government_administration` (`greys_kai_fix done`'s `ai_value` + `greys+morg done`'s `pmg_panum_hospital` group) and `building_airport` (`greys+llwa done`'s `extension_building_types` + `greys+megapack done`'s production groups).

## Пересборка

`python3 tools/build_addon_greys.py --repo .` — regenerates the merge file (`tools/regen_addon_greys.py`) automatically, then copies the twelve compatches in, moves anything stale to `_to_delete/`, and verifies coverage byte-for-byte plus the internal checks (brace balance, BOM, duplicate keys, localization, goods count). `--check` reports only, changes nothing. Metadata: `python3 tools/addon_greys_metadata.py .`. Re-run both after any of the twelve source compatches changes.
