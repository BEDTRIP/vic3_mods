# Addon: LLWA x MegaComPatch

**Game 1.13 (exe 1.13.11). Locomotion: Land, Water, & Air (LLWA) 2.6.3; The Great Revision 2.0; Kuromi's AI 7.5; Victorian Century (declares no version); Economic and Financial Mod (E&F) - V4; vanilla; Hail, Columbia!; Mandate of Heaven; LLWA + Morgenröte Compatch 1.0.8.**

LLWA loads last in the target chain — after the megapack, Victorian Century, addon-VC, HC+GoB+MoH, and addon-HC. Two separate mechanisms in LLWA silently drop earlier mods' contributions on 19 records, plus a hand-written per-building whitelist in E&F that predates LLWA entirely and never mentions LLWA's new content, plus a gap in the author's own LLWA+Morgenröte compatch, plus ~200 historical companies across the set that have never heard of LLWA's buildings:

* `common/ai_strategies/03_political_strategies.txt` sits at the **exact vanilla relative path**. Per the engine's file-resolution model, an identical path is a file-level override — the single latest mod's file wins entirely, and vanilla's own file at that path drops out of the merge, not just gets patched key-by-key. LLWA's copy is a stale pre-1.13 vanilla file (125-line diff, zero LLWA content), so loading last it reverts nine `ai_strategy_*` records to their pre-1.13 shape and, being bare (no prefix), wipes every earlier `INJECT:` on them along the way.
* `LLWA_rails.txt` does a bare `REPLACE:` on ten rail production methods — a full body that doesn't declare sub-blocks it doesn't rebalance itself, silently dropping other mods' additions to the same records.
* E&F registers buildings for its stock/liquidity economy through a **hand-written per-building whitelist** that predates LLWA — none of LLWA's six privately-owned buildings are on it, and `pair_matrix.py`'s key-overlap matrix can't catch this class of gap at all (a key only one mod ever defines can never show up as a "shared key").
* `_llwa/llwa+morg out` (the author's own LLWA+Morgenröte compatch) bare-redefines `building_railway`/`building_airport` without knowing E&F exists, dropping E&F's contribution to both.
* ~200 historical railway/port companies across vanilla/TGR/VC/HC/MoH predate LLWA and don't extend into any of its buildings.

This addon puts all of it back, on top of LLWA's own numbers and design choices — never overruling them, only restoring what LLWA's overwrite ate, and extending E&F's economy and the set's historical companies to cover content that simply didn't exist when they were written.

## Load order

1. …CMF → ETF → TGR → PSC → Kuromi's AI → E&F → E&F Hotfix → Morgenröte → PBE…
2. …megapack → Victorian Century → addon-VC → HC+GoB+MoH → addon-HC…
3. **LLWA**
4. `_llwa/llwa+morg out` (if you run Morgenröte — the author's own compatch, not built by this project)
5. **this addon**

**This addon must load after LLWA** (and after `llwa+morg out` if that's in your set), and needs TGR, Kuromi's AI, Victorian Century, and E&F all present (see "Running it without one of the mods" below).

## What this addon does

Assembled from seven closed pair compatches by `tools/build_addon_llwa.py`. None of the seven write the same relative path as another, so this is a straight copy-and-verify, no addon-only merge file needed (unlike addon-VC's `buy_packages`).

### The Great Revision's market-access modifier comes back on seven rail methods

`common/production_methods/zz_llwa_tgr_rails.txt` (from `_llwa/llwa+tgr done`). TGR's `state_modifiers.unscaled = { state_market_access_price_impact = 0.05 }` (`building_modifiers.unscaled` on one record — `pm_diesel_trains_principle_transport_3` — reproducing what looks like a slip in TGR's own file, not "corrected"), restored on top of LLWA's own body. LLWA's own numeric rebalance is untouched — LLWA loads last, its numbers are what actually ends up in the game either way.

### Victorian Century's job-attractiveness modifier comes back on three rail methods

`common/production_methods/zz_llwa_vc_rails.txt` (from `_llwa/llwa+vc done`). VC's `building_modifiers.unscaled.building_job_attractiveness_mult = 2`, restored on top of LLWA's own body — including LLWA's own `pm_steel_passenger_carriages.unlocking_production_methods` addition, carried forward unchanged.

### Current vanilla, Kuromi's AI's agenda tuning, and the closed KAI x VC three-way merge come back on nine ai_strategies records

From `_llwa/llwa+kai done`: `common/ai_strategies/03_political_strategies.txt` (current-vanilla restore at LLWA's own overridden path), `zzz_llwa_kai_political_strategies.txt` (KAI's five `*_agenda` `INJECT:`s), `zzzz_llwa_kai_vc_reforms.txt` (the three keys shared with VC too — `great_reforms`, `tanzimat_reforms`, `meiji_restoration` — reusing addon-VC's already-closed `_vc/kai+vc done` merge verbatim rather than re-deriving it). `ai_strategy_default` is untouched by this file at all (confirmed absent from both LLWA's copy and current vanilla at this path) and needs no restoration — LLWA's only touch to it is a separate, purely additive `INJECT:subsidies`. `ai_strategy_maintain_mandate_of_heaven` is fixed by the vanilla restore alone; nobody else touches it.

### E&F's contribution comes back on building_railway and building_airport when running the author's Morgenröte compatch

`common/buildings/zz_llwa_morg_ef_buildings.txt` (from `_llwa/llwa+morg+ef done`). `_llwa/llwa+morg out` bare-redefines both buildings reconciling LLWA's and Morgenröte's own content by hand, but its own metadata declares no dependency on E&F and both buildings lose E&F's `pmg_market_liquidity` + private-ownership stock group as a result — restored on top of that compatch's current body, its own reconciliation untouched. Only relevant if you run `llwa+morg out`; harmless if you don't (the target keys simply won't exist for the `REPLACE_OR_CREATE:` to matter — see that pair's own README for the one edge case, `LLWA_building_airway`, worth knowing about).

### LLWA's own six buildings get wired into E&F's stock/liquidity economy

Four files from `_llwa/llwa+ef done`: `common/buildings/zz_llwa_ef_buildings_inject.txt` adds `pmg_market_liquidity` + `pmg_private_ownership_railroad_stock` to LLWA's roadway/waterway/riverway/airway/freight_depot/exchange (not `logistics_hub` — `no_ownership`, can't be privately owned); `common/scripted_effects/zz_llwa_ef_private_ownership_effects.txt` is LLWA's own yearly private-ownership switch, the same shape E&F uses for its own buildings; `common/on_actions/` and `common/history/global/` hook that switch in additively. All six get the SAME stock type (`railroad_stock`) — LLWA's whole network is transport infrastructure, not manufacturing/agriculture/mining, and the group already exists (covers vanilla `building_railway`) so no new production method group or localisation is needed.

### 142 historical and financial companies across the set can now expand into LLWA's buildings

`common/company_types/zz_llwa_companies_extensions.txt` (from `_llwa/llwa+companies done`). Companies with `building_railway` in `building_types` (29, checked against each one's FINAL definition in the chain — see that pair's README for the 11 that were dropped because a later mod redesigned them away from railways) get `LLWA_building_roadway` added to `extension_building_types`; companies with `building_port` (16, +2 that have both) get `LLWA_building_waterway` + `LLWA_building_riverway`. Pure `INJECT:`, no company's own design touched.

Follow-up, same day (user question: what's happening with `llwa_building_exchange`?) — **97 of E&F's 103 banks** get `llwa_building_exchange` added too. That building isn't a literal stock exchange despite the name (it's LLWA's MAPI-communications building — telegraph/telephone/press, reduces market access price impact), but the theme fits E&F's diversified financial companies the same way railways already do. Matched by `building_financial_centre_*` (E&F suffixes the key per country) rather than an exact key.

## Open items carried over, not closed here

* **`mobilization_option_chemical_weapons` (Morgenröte x VC)** — whether repeated `_add` fields inside one sub-block sum or the second overwrites the first is not established from the files (`_vc/morg+vc done` README, VC.3). Unrelated to LLWA, listed here only because it's part of the same overall chain.
* **`ai_strategy_meiji_restoration`'s `anti_interest_groups`/`interest_group_government_weight` (KAI x VC)** — left open in `_vc/kai+vc done` (depends on vanilla journal entries whose reachability under VC's own Meiji rework isn't established from the files). This addon reuses that merge as-is, open item included; closing it is addon-VC's decision to make, not this addon's.
* **Which E&F stock category LLWA's buildings should use** was a design decision (settled here as `railroad_stock` uniformly), not something the files dictate on their own — see `_llwa/llwa+ef done`'s README.
* **`llwa_building_freight_depot`, `llwa_building_exchange`, `LLWA_building_logistics_hub`** are not given to any company (see `_llwa/llwa+companies done`'s README for why) — not a bug, LLWA's own author doesn't give them to its own four companies either.
* **Grey's/USU's ~70 railway companies** don't get LLWA buildings — addon-Grey's own territory (GR.9). (E&F's banks DO get `llwa_building_exchange` now — see `_llwa/llwa+companies done`'s README for that follow-up.)

## Checks run against the assembly

`tools/build_addon_llwa.py`: **11 files, ALL CHECKS PASS**, `--check` idempotent. Coverage: 7/7 pairs byte-for-byte, 0 missing, 0 different, 0 undeclared addon-only files. 8 duplicate top-level keys, all declared (the intentional bare-floor-then-explicit-override chain inside `llwa+kai done` — see `tools/build_addon_llwa.py`'s `DECLARED_DUPS`). Brace balance and encodings clean. No `common/goods` files (128 ceiling unchanged at 74).

`scan_conflicts.py` against each direct participant and the wider chain (raw reports in `_scan_raw/`):

| against | common key overlaps | expected? |
| --- | --- | --- |
| LLWA itself | 26 | yes — the original 19 restored records + the 6 buildings wired into E&F + `building_railway` again via the morg+ef fix |
| TGR | 22 | yes — 10 rail PMs + 10 historical companies TGR also defines + 2 additive GLOBAL/on_action blocks |
| Kuromi's AI | 8 | yes — five agenda strategies + three reform strategies |
| Victorian Century | 28 | yes — 3 ai_strategies + 3 production_methods (unchanged since LLWA.3) + 21 historical companies + 1 additive GLOBAL block |
| addon-VC | 6 | yes, intentional — the three reform strategies this addon deliberately reissues on top of addon-VC's own merge, plus 3 companies (`company_russian_american_company`, `company_standard_oil`, `company_united_fruit`) addon-VC also touches — additive `INJECT:`, no real conflict |
| addon-HC | 0 | — |
| megapack (no t&r) | 101 | yes — `building_airport`, 98 companies (97 E&F banks + `company_standard_oil`), and the additive `GLOBAL`/`on_yearly_pulse_country` pattern, all vs the megapack's own E&F+Morgenröte compatch and its bundled copy of E&F's company list |
| E&F | 101 | yes — `building_railway` (the morg+ef restore), 98 companies (97 banks getting `llwa_building_exchange` + `company_standard_oil`), additive `GLOBAL`/`on_yearly_pulse_country` |
| llwa+morg out | 3 | yes — `building_railway`/`building_airport` (the restore) + `LLWA_building_airway` (harmless no-op when that compatch is active, see `llwa+ef done`'s README) |

Every number matches what the individual pair compatches' own machine matrices and live checks predicted — nothing unaccounted for.

## Running it without one of the mods

Victorian Century, Kuromi's AI, TGR, and E&F are all treated as permanent blocks in this set (not optional, per the plan's decisions #6/#7), so this addon does not carry the `.off`-pair / tag convention used for genuinely optional dependencies (rules file, section 8, decision #9) — unlike addon-HC's handling of Victorian Century. If any of them ever becomes optional here: `zzzz_llwa_kai_vc_reforms.txt` depends on `_vc/kai+vc done` existing; `llwa+ef done` and `llwa+morg+ef done` depend on E&F; `llwa+companies done`'s roadway/waterway/riverway additions depend on TGR/VC/HC/MoH respectively for the companies each contributes (harmless if any one is absent — `INJECT:` on a company that doesn't exist just does nothing, doesn't error).

## Rebuilding

`python3 tools/build_addon_llwa.py --repo <path to vic3_mods>` (add `--check` to verify without writing). Rebuilds from the seven pair compatches — run each pair's own `regen_llwa_*.py` first if LLWA, TGR, KAI, VC, E&F, or any of the five company-source mods updated.

## For Steam

[h1]Addon: LLWA x MegaComPatch[/h1]
[b]Game 1.13 (exe 1.13.11) — Locomotion (LLWA) 2.6.3, The Great Revision 2.0, Kuromi's AI 7.5, Victorian Century (declares no version), Economic and Financial Mod (E&F) - V4.[/b]

LLWA loads last and silently drops 19 records' worth of earlier mods' contributions — a stale pre-1.13 vanilla file at an exact game path, and bare rail-method overwrites. E&F's stock/liquidity system also predates LLWA and never registered its six new buildings, and ~200 historical companies across the set have never heard of them either. This addon restores all of it, without touching LLWA's own balance or design choices.

[h2]Load order[/h2]
[list]
[*]…rest of your set, including The Great Revision, Kuromi's AI, Victorian Century, and E&F…
[*]LLWA
[*][b]this addon[/b]
[/list]
