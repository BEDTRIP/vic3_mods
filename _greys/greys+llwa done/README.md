# ComPatch: Grey's + addon-LLWA

<!-- meta
пара: Grey's (USU) × addon-LLWA (GR.16) + Grey's (USU) × голый LLWA (GR.9)
статус: done -- закрыто 27.08.2026
версии: Game 1.13 (exe 1.13.11) -- Addon: LLWA x MegaComPatch 1.13.11.3, Grey's Urban Synergy Unleashed (declares no version)
позиция: после всей пачки Grey's
файлов: 4
генератор: tools/regen_greys_llwa.py
зависит от: -- (шесть из 14 компаний решаются в _greys/greys+vc done, не здесь)
-->

## Для мастерской

[h1]ComPatch: Grey's + addon-LLWA[/h1]
[b]Game 1.13 (exe 1.13.11) -- Addon: LLWA x MegaComPatch, Grey's Urban Synergy Unleashed.[/b]

GR.16 covers 41 shared keys total, GR.9 covers 11 more against bare LLWA (see the project plan). grey_usu loads after addon-LLWA and re-issues a number of records with full bodies, silently dropping addon-LLWA's earlier additive contributions on them -- the same class of bug already fixed for TGR and VC in the other Grey's compatches. This upload also supersedes the outdated third-party "USU + LLWA Compatch" (workshop id 3387021675) entirely -- everything it did is either handled here, handled elsewhere already, or fixed upstream by the mods themselves since it was written.

[h2]Load order[/h2]
[list]
[*]...addon-LLWA...
[*]Grey's pack (soft_econ, soft_pop, USU, food, ranch, ...)
[*][b]this ComPatch[/b]
[/list]

---

**Game 1.13 (exe 1.13.11). Addon: LLWA x MegaComPatch 1.13.11.3; Grey's Urban Synergy Unleashed (declares no version).**

## 1. Eight railway companies (extension_building_types)

grey_usu's `TRY_REPLACE:` on `company_cfr`, `company_cordoba_railway`, `company_egyptian_rail`, `company_gwr`, `company_imperial_ethiopian_railways`, `company_iranian_state_railway`, `company_sao_paulo_railway`, and `company_tashkent_railroad` is a full body written before addon-LLWA existed. Each carries its own `extension_building_types` list (`building_motor_industry`, `building_coal_mine`, etc. -- checked per company) that does not include `LLWA_building_roadway`, so addon-LLWA's earlier `TRY_INJECT:` of that building type is silently gone. Re-issued here as a plain `TRY_INJECT:` after the whole Grey's pack -- additive, so it does not matter that grey_usu's REPLACE already ran.

**Not included: the other six railway companies** (`company_great_indian_railway`, `company_mantetsu`, `company_orient_express`, `company_panama_company`, `company_prussian_state_railways`, `company_suez_company`). These also collide with Victorian Century, which already writes a full-body `REPLACE_OR_CREATE:` for them in `_greys/greys+vc done/common/company_types/zz_gvc_companies.txt`. A second, separate `TRY_INJECT:` here would do nothing -- that file's full body loads at the same position (after the whole Grey's pack) and always wins over an earlier additive inject. The LLWA fix for those six is folded directly into that file instead; see its own generator and README section.

## 2. Three rail production methods (building_job_attractiveness_mult)

`pm_no_passenger_trains`, `pm_steel_passenger_carriages`, and `pm_wooden_passenger_carriages`: grey_usu's `REPLACE_OR_CREATE:` keeps its own numbers on every field it touches, but never had `building_modifiers.unscaled.building_job_attractiveness_mult = 2` -- originally VC's, already restored against LLWA's own body in `_llwa/llwa+vc done`, and dropped again the same way by grey_usu's later full-body rewrite. Restored here on top of grey_usu's current body; nothing else on these three records is touched.

**Not included: the other seven rail production methods** (`pm_early_trains`, `pm_steam_trains`/+ptc3, `pm_electric_trains`/+ptc3, `pm_diesel_trains`/+ptc3). These are a genuine numeric *dispute*, not a silent loss: grey_usu has its own progressively-scaled `state_market_access_price_impact` design across all seven (0.02 → 0.05), while TGR/VC's contributions on the same field are single flat numbers tuned for a different infrastructure model entirely (see the project plan and `_greys/analysis_gr7_tgr_report.md`, section 13, for the quantitative case). Taking one side's number without its whole design would double-count infrastructure. No file. `pair_matrix.py --pair "Grey's,LLWA"` confirms this is the full set: exactly 11 shared keys against bare LLWA, one building (below) plus these ten production methods -- nothing else, GR.9 closed.

## 3. building_railway (station + line) and building_airport

grey_usu's 2026-08-27 update (`~zzzzMoG_USU_railways.txt`, 459 lines, was 226 when the project plan was first written) **split `building_railway` into two buildings.** `building_railway` is now the railway *station* (an AI-subsidy mechanism -- grey_usu's own comment says "Now the Railway Station" -- carrying only `pmg_base_building_rail_terminal` + `pmg_logistics_services_railway`), and the actual railway is new content, `building_usu_railway_line` (`pmg_base_building_railway` + `pmg_passenger_trains` + `pmg_automation_building_railway`; `pmg_gaudi_communication` is listed but commented out). grey_usu has zero awareness of LLWA anywhere in its files, and `building_usu_railway_line` did not exist when addon-LLWA's own merged `building_railway` (Morgenröte's `pmg_gaudi_communication` + LLWA's `LLWA_pmg_private_expansion` + E&F's `pmg_market_liquidity` / `pmg_private_ownership_railroad_stock`) was built -- none of that survives the split.

**Decided with the user 2026-08-27:** `building_usu_railway_line` gets the whole private-ownership economy (`LLWA_pmg_private_expansion` + both E&F groups) -- the same building [GR.15](../../План%20проекта.md) already proposes `railroad_stock` for, so this closes that part of GR.15 too. `building_railway` (the station) gets only `pmg_gaudi_communication` back. grey_usu's own file carries a **commented-out** `TRY_INJECT:building_railway = { production_method_groups = { pmg_gaudi_communication } }` at the very bottom, disabled by the author over a same-mod "PDX REPLACE/INJECT sequence problem" -- a separate, later-loading file (this one) doesn't hit that problem, so their own intended fix is restored verbatim, on the exact record they targeted.

`building_airport` is a plain full-body `TRY_REPLACE:` by grey_usu (`zMoG_USU_MR_airports.txt`) -- no split, no dispute. It silently drops the same three LLWA groups plus E&F's two groups (`pmg_private_ownership_manufacture_stock` this time, not `railroad_stock` -- this is the E&F × Morgenröte pairing, same as how E&F already treats `building_power_plant`). Restored the same way, additively.

*Not this pack's job:* the megapack-only (no addon-LLWA) variant of `building_airport` -- open as part of GR.17 -- needs its own, separate fix (E&F/Morgenröte groups only, no LLWA groups, since LLWA isn't loaded in that build at all). Referencing addon-LLWA's pmg names from a file that can load without addon-LLWA present would be a load error, not a fix.

## 4. GR.9 -- the old third-party "USU + LLWA Compatch" is fully superseded

Audited 2026-08-27 key by key (see `_greys/usu_llwa out outdate noneed/README.md` for the full writeup): every one of its 11 keys is now either done here (§3 above), fixed upstream by LLWA or grey_usu themselves since it was written, or already covered by other compatches in this pack that didn't exist when it was written. Nothing carried over from it unmodified.

## Maintenance

`tools/regen_greys_llwa.py`; `--check` reports drift without writing. Every restored value is read live from addon-LLWA's and grey_usu's current files with an assert on the expected shape -- a future update to either mod that changes one of these values makes the generator fail loudly rather than silently write a stale number.
