# ComPatch: LLWA+Morgenroete x E&F

**Game 1.13 (exe 1.13.11). Locomotion: Land, Water, & Air (LLWA) 2.6.3; Morgenroete; LLWA + Morgenroete Compatch (author id `xyz.1230james.LLWA_morgenrote_compatch`) 1.0.8; Economic and Financial Mod (E&F) - V4.**

Not one of the addon's original three pairs (LLWA.1-3/plan). Found while re-checking the finished addon: the plan's LLWA.4 calls LLWA x Morgenroete `noneed` / "closed by the author's own compatch" (`_llwa/llwa+morg out`) — true at the raw-mod level (`pair_matrix.py`: 1 shared key, additive, no real conflict) — but the author's compatch itself introduces a loss the machine matrix can't see, because `tools/blocks.json`'s "LLWA" block is defined as the raw mod only and never measures this third-party compatch at all.

`_llwa/llwa+morg out/common/buildings/zz_LLWAMR_buildings.txt` bare-redefines `building_railway` and `building_airport` — full bodies, no prefix, by hand reconciling LLWA's and Morgenroete's own `production_method_groups`. Its own `.metadata/metadata.json` declares only Locomotion and Morgenroete as dependencies — E&F isn't mentioned. Two groups E&F contributes earlier in the chain via plain `INJECT:` get silently dropped as a result, on both buildings, with nothing in any log.

This matches an in-game finding already on record in the project's rules file (section 3): "в панели железной дороги остаются три группы вместо девяти — ни pmg_market_liquidity от E&F..." — that passage names LLWA's compatches collectively, not raw LLWA alone. This is that finding's fix.

## Load order

1. …E&F → E&F Hotfix → Morgenröte…
2. …megapack (bundles the closed E&F x Morgenroete pair) → Victorian Century → addon-VC → HC+GoB+MoH → addon-HC…
3. LLWA
4. **`_llwa/llwa+morg out`** (the author's LLWA + Morgenroete compatch — run alongside LLWA and Morgenroete, not instead of them)
5. **this ComPatch**

**This patch must load after `llwa+morg out`, LLWA, Morgenroete, and E&F.**

## What was being lost

* **`building_railway`** — E&F's own `common/buildings/ef_11_private_infrastructure.txt`: `INJECT:building_railway = { production_method_groups = { pmg_market_liquidity pmg_private_ownership_railroad_stock } }`. `llwa+morg out`'s bare body keeps `pmg_base_building_railway`, `pmg_passenger_trains`, Morgenroete's `pmg_gaudi_communication`, and LLWA's own `LLWA_pmg_private_expansion` — E&F's two groups are simply absent.
* **`building_airport`** — the already-closed E&F x Morgenroete pair, folded into the megapack's `common/buildings/zz_ef_mr_buildings_inject.txt`: `TRY_INJECT:building_airport = { production_method_groups = { pmg_market_liquidity pmg_private_ownership_manufacture_stock } }`. `llwa+morg out`'s bare body keeps only LLWA's own three air groups (`LLWA_pmg_air_base`, `LLWA_pmg_air_traffic`, `LLWA_pmg_private_expansion`) — same loss.

Both are restored on top of `llwa+morg out`'s current body: its own reconciliation of LLWA's and Morgenroete's contributions is carried through unchanged, only E&F's two groups per building are appended.

## What this does NOT fix, on purpose

`llwa+morg out`'s `building_airport` also completely drops Morgenroete's **own** aviation redesign — `pmg_base_building_airport`, `pmg_cargo_airport`, `pmg_tourism_airport`, from Morgenroete's own `mr_sports_civil_aviation_buildings.txt` — in favour of LLWA's own air production method groups. That is not an additive `INJECT:` silently eaten by a bare override the way E&F's contribution is; it's two mods each proposing a full, mutually exclusive redesign of the same building, and the compatch's author already made a choice between them (LLWA's design wins). Second-guessing which design should win, or trying to make both coexist, is not established from the files and isn't this patch's job (rules file: "не чинить чужой замысел, не разобравшись"). Left open — see "Open items" in the addon's own README.

## How the merge is made

`tools/regen_llwa_morg_ef.py`. Reads `llwa+morg out`'s current bodies for both buildings live, asserts `pmg_market_liquidity` is not already present in either (guards against double-counting if the source compatch is ever updated to include E&F itself, or if this file is mistakenly run without `llwa+morg out`), reads E&F's and the megapack's INJECT bodies live and asserts each still contains exactly the two expected groups, then appends the missing groups to the existing `production_method_groups` list and reissues the whole record as `REPLACE_OR_CREATE:`.

## Notes

* **Depends on `_llwa/llwa+morg out` existing and being run.** Without it, raw LLWA already leaves E&F's `INJECT:` untouched (LLWA.4's original `noneed` finding) — running this patch without `llwa+morg out` would add E&F's groups a second time. The generator's own assert (E&F's groups must not already be present) catches this at generation time, but the folder itself is not marked `.off`/optional the way genuinely-optional dependencies are (rules section 8, decision #9), since `llwa+morg out` is treated as a permanent part of this set once LLWA and Morgenroete coexist, same as VC/KAI/TGR elsewhere in this project.
* **Not part of `build_addon_llwa.py`'s original three pairs** — added as a fourth `PAIR` once found. See the addon's own README for the updated coverage table.
* **Maintenance.** Everything is generated by `tools/regen_llwa_morg_ef.py`. Re-run after `llwa+morg out`, E&F, or the megapack's E&F x Morgenroete pair update; `--check` reports drift without writing.

## For Steam

[h1]ComPatch: LLWA+Morgenroete x E&F[/h1]
[b]Game 1.13 (exe 1.13.11) — Locomotion (LLWA) 2.6.3, Morgenroete, LLWA + Morgenroete Compatch 1.0.8, Economic and Financial Mod (E&F) - V4.[/b]

The author's own LLWA + Morgenroete compatch bare-redefines two buildings without declaring E&F as a dependency, silently dropping E&F's contribution to both. This patch restores it, without touching anything else the compatch already reconciled between LLWA and Morgenroete.

[h2]Load order[/h2]
[list]
[*]…E&F, Morgenroete…
[*]LLWA
[*]LLWA + Morgenroete Compatch
[*][b]this ComPatch[/b]
[/list]
