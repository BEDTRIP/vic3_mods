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

142 historical and financial companies across the base game and five other mods predate LLWA and know nothing about its roads, canals, rivers, air routes, freight depots, or exchanges — 45 railway/port companies get transport extensions, 97 of E&F's own banks get every LLWA building a company is allowed to own. Pure addition, no company's own design touched.

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

Checked across every mod in the set: **zero companies anywhere mention any LLWA building.** Not a conflict in the usual sense (nothing silently drops, nothing gets overwritten) — LLWA's whole transport network is simply invisible to the historical/financial companies whose entire purpose is building exactly that kind of infrastructure.

**Since 2026-10-03 (LLWA.9) the buildings go into `building_types`, not `extension_building_types`.** An extension building is open to a company only after it grows into it; the user wanted the logistics on these companies from the start. `INJECT:` appends to the list (the E&F hotfix relies on the same for `building_bank` on its 98 banks), nothing overwritten.

## The rule

Applied mechanically, not by picking favourites:

* company has `building_railway` in `building_types` → add `LLWA_building_roadway`
* company has `building_port` in `building_types` → add `LLWA_building_waterway` + `LLWA_building_riverway`
* E&F company has a `building_financial_centre*` building (the country-specific variant E&F uses, matched by prefix; plus the hotfix's generic central bank `zz_ef_cm_central_bank`) → add `llwa_building_exchange`

**143 companies** qualify: 29 get roadway, 16 get waterway/riverway only, 2 (`company_hbc`, `company_yasuda`) get both rail and port, and **98 banks** (97 of E&F's companies + `zz_ef_cm_central_bank`) get the exchange.

### E&F's banks: the exchange only

History: 2026-08-26 the exchange; 2026-09-09 (user decision) widened to every LLWA building a company may own (roads, canals, rivers, airway, freight depot, exchange); **2026-10-02 narrowed back to the exchange** (СТР.5, user decision: banks keep only banking — with ~100 bank companies there was a company for almost every building, and banks took ~30% of all company construction; the hotfix comments railways, trade centres, mines and construction out of the banks' `building_types` too).

`llwa_building_exchange` isn't a literal stock exchange despite its name: its production method groups are `LLWA_pmg_exchange_base` + `LLWA_pmg_mapi_comms`, a telegraph/telephone/press building that reduces market access price impact. LLWA.6 wires it into E&F's stock economy.

The generator verifies every key it hands out against LLWA's own `common/buildings` on every run (`verify_llwa_buildings()`): still defined, still `ownership_type = self`.

Membership is checked against each company's **final** definition in the chain, not whichever mod first wrote it — 11 companies were dropped from an earlier draft for exactly that reason. TGR defines `company_krupp`, `company_east_india_company`, and nine others as railway companies, but VC's own `REPLACE_OR_CREATE:` on the same keys (VC loads after TGR) turns them into something else entirely — `company_krupp` becomes an arms/steel company, `company_east_india_company` becomes a plantation company — with no `building_railway` left anywhere in the final body. Adding a road extension to VC's redesigned version would have been thematically wrong. The generator's own live lookup (`find_company`, searches all sources and keeps the last full definition; a later `INJECT:` adds to it, as the hotfix does) catches this drift on every future re-run, not just this one.

A company defined in more than one source mod that DID keep the relevant building type (`company_orient_express`, `company_yasuda`, etc.) is emitted **once** — this patch loads last, so one `INJECT:` lands on whichever definition is final at merge time regardless of how many earlier mods touched the same key.

## Deliberately not here

* **`LLWA_building_logistics_hub`** — not given to anyone, anywhere. `ownership_type = no_ownership`: not a judgement call, the engine forbids it.
* **`llwa_building_freight_depot` and the airway, for the transport companies in RAIL/PORT** — still not given to them. LLWA's own author puts `freight_depot` on none of his own four companies, which reads as a "one per state utility building, not a company holding" choice, and his `turnpike`/`ship_line` companies get roads and water only. That restraint is kept for everyone historical; it is overridden for E&F's banks it was overridden 2026-09-09 and taken back 2026-10-02 (see above).
* **Grey's/USU's ~70 railway companies** — addon-Grey's own territory (GR.9, `usu_llwa` compatch). Touching them from here would step on that work.

## How the merge is made

`tools/regen_llwa_companies.py`. `find_company()` searches all six source mods live for each candidate key, in the REAL target chain's load order (`SOURCES` is ordered vanilla → TGR → E&F → E&F hotfix → VC → HC → MoH — getting E&F's position wrong once already produced a wrong "final" `building_types` for `company_standard_oil`, caught immediately by the same drift-assert described below), and returns the `building_types` of the LAST definition found; the generator asserts every company still exists and still carries the building type its category expects, and fails loudly (not silently) on drift — see the 11-company correction above, and the `company_standard_oil` note, for why that assert exists.

## Notes

* **Maintenance.** Everything is generated by `tools/regen_llwa_companies.py`. Re-run after vanilla, TGR, E&F, VC, HC, or MoH update their company lists, or after LLWA touches its buildings; `--check` reports drift without writing. Two asserts guard the run: `verify_llwa_buildings()` checks LLWA's side (every key still defined, still `ownership_type = self`), `verify_and_collect()` checks the company side (every target still exists and still carries the building type its rule expects).
* No localisation needed — the buildings are already localised by LLWA.
