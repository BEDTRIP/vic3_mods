# ComPatch: Grey's + addon-LLWA

<!-- meta
пара: Grey's (USU) × addon-LLWA (GR.16)
статус: в работе -- 2 из нескольких кусков (14 компаний/10 методов), см. "Что ещё не сделано" ниже
версии: Game 1.13 (exe 1.13.11) -- Addon: LLWA x MegaComPatch 1.13.11.3, Grey's Urban Synergy Unleashed (declares no version)
позиция: после всей пачки Grey's
файлов: 2
генератор: tools/regen_greys_llwa.py
зависит от: -- (шесть из 14 компаний решаются в _greys/greys+vc done, не здесь)
-->

## Для мастерской

[h1]ComPatch: Grey's + addon-LLWA (WIP)[/h1]
[b]Game 1.13 (exe 1.13.11) -- Addon: LLWA x MegaComPatch, Grey's Urban Synergy Unleashed.[/b]

[b]This is a partial patch, published early on purpose.[/b] GR.16 covers 41 shared keys total (full breakdown in the project plan). This upload covers the two pieces that are pure silent losses with no competing design to weigh: eight railway companies' extension_building_types, and three rail production methods' building_job_attractiveness_mult.

[h2]Load order[/h2]
[list]
[*]...addon-LLWA...
[*]Grey's pack (soft_econ, soft_pop, USU, food, ranch, ...)
[*][b]this ComPatch[/b]
[/list]

---

**Game 1.13 (exe 1.13.11). Addon: LLWA x MegaComPatch 1.13.11.3; Grey's Urban Synergy Unleashed (declares no version).**

Pair GR.16 -- 41 shared keys. grey_usu loads after addon-LLWA and re-issues a number of records with full bodies, silently dropping addon-LLWA's earlier additive contributions on them -- the same class of bug already fixed for TGR and VC in the other Grey's compatches.

## 1. Eight railway companies (extension_building_types)

grey_usu's `TRY_REPLACE:` on `company_cfr`, `company_cordoba_railway`, `company_egyptian_rail`, `company_gwr`, `company_imperial_ethiopian_railways`, `company_iranian_state_railway`, `company_sao_paulo_railway`, and `company_tashkent_railroad` is a full body written before addon-LLWA existed. Each carries its own `extension_building_types` list (`building_motor_industry`, `building_coal_mine`, etc. -- checked per company) that does not include `LLWA_building_roadway`, so addon-LLWA's earlier `TRY_INJECT:` of that building type is silently gone. Re-issued here as a plain `TRY_INJECT:` after the whole Grey's pack -- additive, so grey_usu's own list items are untouched either way.

**Not included: the other six railway companies** (`company_great_indian_railway`, `company_mantetsu`, `company_orient_express`, `company_panama_company`, `company_prussian_state_railways`, `company_suez_company`). These also collide with Victorian Century, which already writes a full-body `REPLACE_OR_CREATE:` for them in `_greys/greys+vc done/common/company_types/zz_gvc_companies.txt`. A second, separate `TRY_INJECT:` here would do nothing -- that file's full body loads at the same position (after the whole Grey's pack) and always wins over an earlier additive inject. The LLWA fix for those six is folded directly into that file instead; see its own generator and README section.

## 2. Three rail production methods (building_job_attractiveness_mult)

`pm_no_passenger_trains`, `pm_steel_passenger_carriages`, and `pm_wooden_passenger_carriages`: grey_usu's `REPLACE_OR_CREATE:` keeps its own numbers on every field it touches, but never had `building_modifiers.unscaled.building_job_attractiveness_mult = 2` -- originally VC's, already restored against LLWA's own body in `_llwa/llwa+vc done`, and dropped again the same way by grey_usu's later full-body rewrite. Restored here on top of grey_usu's current body; nothing else on these three records is touched.

**Not included: the other seven rail production methods** (`pm_early_trains`, `pm_steam_trains`/+ptc3, `pm_electric_trains`/+ptc3, `pm_diesel_trains`/+ptc3). These are a genuine numeric *dispute*, not a silent loss: grey_usu has its own progressively-scaled `state_market_access_price_impact` design across all seven (0.02 → 0.05), while TGR/VC's contributions on the same field are single flat numbers tuned for a different infrastructure model entirely (see the project plan and `_greys/analysis_gr7_tgr_report.md`, section 13, for the quantitative case). Taking one side's number without its whole design would double-count infrastructure. No file.

## What's NOT in this patch yet

* **`building_railway` / `building_airport`** -- shared with GR.9 and GR.17, one winning body determined by three-plus mods at once; handled there, not duplicated here.
* **Six railway companies overlapping Victorian Century** -- see `_greys/greys+vc done` instead (section 1 above).

## Maintenance

`tools/regen_greys_llwa.py`; `--check` reports drift without writing. Every restored value is read live from addon-LLWA's and grey_usu's current files with an assert on the expected shape -- a future update to either mod that changes one of these values makes the generator fail loudly rather than silently write a stale number.
