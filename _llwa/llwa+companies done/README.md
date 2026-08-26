# ComPatch: LLWA + historical companies

<!-- meta
пара: LLWA × компании
статус: done
версии: Game 1.13 (exe 1.13.11) — Locomotion (LLWA) 2.6.3, vanilla, The Great Revision, Victorian Century, Hail Columbia!, Mandate of Heaven.
позиция: —
файлов: 1
генератор: tools/regen_llwa_companies.py
зависит от: —
-->

## Для мастерской

[h1]ComPatch: LLWA + historical companies[/h1]
[b]Game 1.13 (exe 1.13.11) — Locomotion (LLWA) 2.6.3, vanilla, The Great Revision, Victorian Century, Hail Columbia!, Mandate of Heaven.[/b]

142 historical and financial companies across the base game and five other mods predate LLWA and know nothing about its roads, canals, rivers, air routes, or communications building — 45 railway/port companies get transport extensions, 97 of E&F's own banks get llwa_building_exchange. Pure addition, no company's own design touched.

[h2]Load order[/h2]
[list]
[*]…vanilla, The Great Revision, E&F, Victorian Century, Hail Columbia!, Mandate of Heaven…
[*]LLWA
[*][b]this ComPatch[/b]
[/list]

---

**Game 1.13 (exe 1.13.11). Locomotion: Land, Water, & Air (LLWA) 2.6.3; vanilla; The Great Revision 2.0; Victorian Century; Hail, Columbia!; Mandate of Heaven; Economic and Financial Mod (E&F) - V4.**

Not a two-mod pair — one addition applied across the whole set. LLWA closes its own four companies over its own seven buildings (`LLWA_companies.txt`: turnpike, ship_line, railroad, airline). Every historical company written by anyone else — vanilla, TGR, VC, HC, MoH — predates LLWA and has never heard of its roads, canals, rivers, or air routes.

## Load order

1. …vanilla → TGR → E&F → E&F Hotfix → Morgenröte → PBE → megapack → VC → addon-VC → HC+GoB+MoH…
2. …LLWA…
3. **this ComPatch**

**This patch must load after all of the above and after LLWA.**

## What was missing

`extension_building_types` is the field that lets a historical company expand into a related building once it grows — it's declared (even if empty) on every single company record checked across all six source mods, so this is a pure `INJECT:`, nothing overwritten.

Checked across every mod in the set: **zero companies anywhere mention any LLWA building.** Not a conflict in the usual sense (nothing silently drops, nothing gets overwritten) — LLWA's whole transport network is simply invisible to the ~300 historical/financial companies whose entire purpose is building exactly that kind of infrastructure.

## The rule

Applied mechanically, not by picking favourites:

* company has `building_railway` in `building_types` → add `LLWA_building_roadway` to `extension_building_types`
* company has `building_port` in `building_types` → add `LLWA_building_waterway` + `LLWA_building_riverway`
* E&F company has a `building_financial_centre_*` building (the country-specific variant E&F uses; matched by prefix, not exact key) → add `llwa_building_exchange`

**142 companies** qualify: 29 get roadway, 16 get waterway/riverway only, 2 (`company_hbc`, `company_yasuda`) get both rail and port, and **97 of E&F's 103 companies** get `llwa_building_exchange` (added as a follow-up to the original 45 — the user asked directly what was happening with `llwa_building_exchange`, since LLWA.6 wires it into E&F's stock economy but nothing gave it to any company).

### E&F's banks and llwa_building_exchange

Decided separately from the transport-company rule above, and later — the original pass left E&F's ~100 banks out on purpose as an undecided question. `llwa_building_exchange` isn't a literal stock exchange despite its name: its own production method groups are `LLWA_pmg_exchange_base` + `LLWA_pmg_mapi_comms`, a telegraph/telephone/press building that reduces market access price impact. Decided: give it to E&F's banks anyway — the theme (a diversified financial company investing in the infrastructure that moves markets) fits the same way railways already do for the same companies.

97 of E&F's 103 companies qualify (any company with a `building_financial_centre_<country>` building — checked by prefix, since E&F suffixes the key per country, e.g. `building_financial_centre_usa`, not a bare `building_financial_centre`). The six that don't: `company_private_construction`, three basic mining-only companies, `company_PennsylvaniaRailroad` (a plain railway company with no financial building — already covered by the RAIL rule instead, since E&F's copy of it isn't the chain's final definition, see below), and `company_standard_oil` (E&F's own entry for it has an empty `building_types` — a stub; the real definition further down the chain, in VC, is what the RAIL rule actually targets).

Membership is checked against each company's **final** definition in the chain, not whichever mod first wrote it — 11 companies were dropped from an earlier draft for exactly that reason. TGR defines `company_krupp`, `company_east_india_company`, and nine others as railway companies, but VC's own `REPLACE_OR_CREATE:` on the same keys (VC loads after TGR) turns them into something else entirely — `company_krupp` becomes an arms/steel company, `company_east_india_company` becomes a plantation company — with no `building_railway` left anywhere in the final body. Adding a road extension to VC's redesigned version would have been thematically wrong. The generator's own live lookup (`find_company`, searches all five sources and keeps the last match) catches this drift on every future re-run, not just this one.

A company defined in more than one source mod that DID keep the relevant building type (`company_orient_express`, `company_yasuda`, etc.) is emitted **once** — this patch loads last, so one `INJECT:` lands on whichever definition is final at merge time regardless of how many earlier mods touched the same key.

## Deliberately not here

* **`llwa_building_freight_depot`, `LLWA_building_logistics_hub`** — not given to any company. `logistics_hub` is `ownership_type = no_ownership`, can't be company-owned at all. `llwa_building_freight_depot` looks like a deliberate "one per state utility building, not a company holding" choice by LLWA's own author (it's in none of LLWA's own four companies either) — not second-guessed here.
* **Grey's/USU's ~70 railway companies** — addon-Grey's own territory (GR.9, `usu_llwa` compatch). Touching them from here would step on that work.

## How the merge is made

`tools/regen_llwa_companies.py`. `find_company()` searches all six source mods live for each candidate key, in the REAL target chain's load order (`SOURCES` is ordered vanilla → TGR → E&F → VC → HC → MoH — getting E&F's position wrong once already produced a wrong "final" `building_types` for `company_standard_oil`, caught immediately by the same drift-assert described below), and returns the `building_types` of the LAST definition found; the generator asserts every company still exists and still carries the building type its category expects, and fails loudly (not silently) on drift — see the 11-company correction above, and the `company_standard_oil` note, for why that assert exists.

## Notes

* **Maintenance.** Everything is generated by `tools/regen_llwa_companies.py`. Re-run after vanilla, TGR, E&F, VC, HC, or MoH update their company lists, or after LLWA renames a building; `--check` reports drift without writing.
* No localisation needed — `extension_building_types` has no display text of its own; the buildings it lists are already localised by LLWA.
