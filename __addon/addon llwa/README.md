# Addon: LLWA x MegaComPatch

**Game 1.13 (exe 1.13.11). Locomotion: Land, Water, & Air (LLWA) 2.6.3; The Great Revision 2.0; Kuromi's AI 7.5; Victorian Century (declares no version).**

LLWA loads last in the target chain — after the megapack, Victorian Century, addon-VC, HC+GoB+MoH, and addon-HC. Two separate mechanisms in LLWA silently drop earlier mods' contributions on 19 records total, with nothing in any log:

* `common/ai_strategies/03_political_strategies.txt` sits at the **exact vanilla relative path**. Per the engine's file-resolution model, an identical path is a file-level override — the single latest mod's file wins entirely, and vanilla's own file at that path drops out of the merge, not just gets patched key-by-key. LLWA's copy is a stale pre-1.13 vanilla file (125-line diff, zero LLWA content), so loading last it reverts nine `ai_strategy_*` records to their pre-1.13 shape and, being bare (no prefix), wipes every earlier `INJECT:` on them along the way.
* `LLWA_rails.txt` does a bare `REPLACE:` on ten rail production methods — a full body that doesn't declare sub-blocks it doesn't rebalance itself, silently dropping other mods' additions to the same records.

This addon puts all of it back, on top of LLWA's own numbers and design choices — never overruling them, only restoring what LLWA's overwrite ate.

## Load order

1. …CMF → ETF → TGR → PSC → Kuromi's AI → E&F → E&F Hotfix → Morgenröte → PBE…
2. …megapack → Victorian Century → addon-VC → HC+GoB+MoH → addon-HC…
3. **LLWA**
4. **this addon**

**This addon must load after LLWA**, and needs TGR, Kuromi's AI, and Victorian Century all present (see "Running it without one of the mods" below).

## What this addon does

Assembled from three closed pair compatches — `_llwa/llwa+tgr done`, `_llwa/llwa+vc done`, `_llwa/llwa+kai done` — by `tools/build_addon_llwa.py`. None of the three write the same relative path as another, so this is a straight copy-and-verify, no addon-only merge file needed (unlike addon-VC's `buy_packages`).

### The Great Revision's market-access modifier comes back on seven rail methods

`common/production_methods/zz_llwa_tgr_rails.txt`. TGR's `state_modifiers.unscaled = { state_market_access_price_impact = 0.05 }` (`building_modifiers.unscaled` on one record — `pm_diesel_trains_principle_transport_3` — reproducing what looks like a slip in TGR's own file, not "corrected"), restored on top of LLWA's own body. LLWA's own numeric rebalance is untouched — LLWA loads last, its numbers are what actually ends up in the game either way.

### Victorian Century's job-attractiveness modifier comes back on three rail methods

`common/production_methods/zz_llwa_vc_rails.txt`. VC's `building_modifiers.unscaled.building_job_attractiveness_mult = 2`, restored on top of LLWA's own body — including LLWA's own `pm_steel_passenger_carriages.unlocking_production_methods` addition, carried forward unchanged.

### Current vanilla, Kuromi's AI's agenda tuning, and the closed KAI x VC three-way merge come back on nine ai_strategies records

`common/ai_strategies/03_political_strategies.txt` (current-vanilla restore at LLWA's own overridden path), `zzz_llwa_kai_political_strategies.txt` (KAI's five `*_agenda` `INJECT:`s), `zzzz_llwa_kai_vc_reforms.txt` (the three keys shared with VC too — `great_reforms`, `tanzimat_reforms`, `meiji_restoration` — reusing addon-VC's already-closed `_vc/kai+vc done` merge verbatim rather than re-deriving it). `ai_strategy_default` is untouched by this file at all (confirmed absent from both LLWA's copy and current vanilla at this path) and needs no restoration — LLWA's only touch to it is a separate, purely additive `INJECT:subsidies`. `ai_strategy_maintain_mandate_of_heaven` is fixed by the vanilla restore alone; nobody else touches it.

## Open items carried over, not closed here

* **`mobilization_option_chemical_weapons` (Morgenröte x VC)** — whether repeated `_add` fields inside one sub-block sum or the second overwrites the first is not established from the files (`_vc/morg+vc done` README, VC.3). Unrelated to LLWA, listed here only because it's part of the same overall chain.
* **`ai_strategy_meiji_restoration`'s `anti_interest_groups`/`interest_group_government_weight` (KAI x VC)** — left open in `_vc/kai+vc done` (depends on vanilla journal entries whose reachability under VC's own Meiji rework isn't established from the files). This addon reuses that merge as-is, open item included; closing it is addon-VC's decision to make, not this addon's.

## Checks run against the assembly

`tools/build_addon_llwa.py`: **5 files, ALL CHECKS PASS**, `--check` idempotent. Coverage: 3/3 pairs byte-for-byte, 0 missing, 0 different, 0 undeclared addon-only files. 8 duplicate top-level keys, all declared (the intentional bare-floor-then-explicit-override chain inside `llwa+kai done` — see `tools/build_addon_llwa.py`'s `DECLARED_DUPS`). Brace balance and encodings clean. No `common/goods` files (128 ceiling unchanged at 74).

`scan_conflicts.py` against each direct participant and the wider chain (raw reports in `_scan_raw/`):

| against | common key overlaps | expected? |
| --- | --- | --- |
| LLWA itself | 19 | yes — exactly the 19 records this addon patches |
| TGR | 10 | yes — all ten rail PMs TGR also defines |
| Kuromi's AI | 8 | yes — five agenda strategies + three reform strategies |
| Victorian Century | 6 | yes — exactly LLWA.3's machine matrix |
| addon-VC | 3 | yes, intentional — the three reform strategies this addon deliberately reissues on top of addon-VC's own merge |
| addon-HC | 0 | — |
| megapack (no t&r) | 0 | expected — the megapack bundles pair-compatches, not full copies of TGR's/KAI's own mod files, so there's nothing at the raw-mod key level to collide with here |

Every number matches what the individual pair compatches' own machine matrices predicted — nothing unaccounted for.

## Running it without one of the mods

Victorian Century, Kuromi's AI, and TGR are all treated as permanent blocks in this set (not optional, per the plan's decisions #6/#7), so this addon does not carry the `.off`-pair / tag convention used for genuinely optional dependencies (rules file, section 8, decision #9) — unlike addon-HC's handling of Victorian Century. If any of the three ever becomes optional here, `zzzz_llwa_kai_vc_reforms.txt` in particular would need that treatment, since it depends on `_vc/kai+vc done` existing.

## Rebuilding

`python3 tools/build_addon_llwa.py --repo <path to vic3_mods>` (add `--check` to verify without writing). Rebuilds from the three pair compatches — run each pair's own `regen_llwa_*.py` first if LLWA, TGR, KAI, or VC updated.

## For Steam

[h1]Addon: LLWA x MegaComPatch[/h1]
[b]Game 1.13 (exe 1.13.11) — Locomotion (LLWA) 2.6.3, The Great Revision 2.0, Kuromi's AI 7.5, Victorian Century (declares no version).[/b]

LLWA loads last and silently drops 19 records' worth of earlier mods' contributions — a stale pre-1.13 vanilla file at an exact game path, and bare rail-method overwrites. This addon restores all of it, without touching LLWA's own balance or design choices.

[h2]Load order[/h2]
[list]
[*]…rest of your set, including The Great Revision, Kuromi's AI, and Victorian Century…
[*]LLWA
[*][b]this addon[/b]
[/list]
