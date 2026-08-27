# ComPatch: Grey's + The Great Revision

<!-- meta
пара: Grey's × TGR (GR.7)
статус: done
версии: Game 1.13 (exe 1.13.11) -- The Great Revision 2.0, Grey's pack (soft_pop/soft_econ/usu declare no version)
позиция: после всей пачки Grey's
файлов: 8
генератор: tools/regen_greys_tgr.py
зависит от: --
-->

## Для мастерской

[h1]ComPatch: Grey's + The Great Revision[/h1]
[b]Game 1.13 (exe 1.13.11) -- The Great Revision 2.0, Grey's pack.[/b]

TGR and the Grey's pack share 97 keys (full breakdown in `_greys/analysis_gr7_tgr_report.md`). This patch covers everything in that overlap that turned out to need a file: country ranks, four citizenship laws, four defines, building_trade_center's level cap, the 7 remaining ownership production methods, building_food_industry/bg_trade, and the class A/B production-method fields that survived checking against the current source. Everything else in the 97 keys was either already closed elsewhere (14 ownership records via GR.5, four defines via decision point #3), decided to need no file at all (ports/rails/automation/trade-center employment, four companies, GR.10's file sync), or belongs to a different pair entirely (`foreign_investment_rights`/GR.8, `trade_states`/GR.14, `building_construction_sector`/GR.2) -- see the plan and report for the full accounting.

[h2]Load order[/h2]
[list]
[*]...The Great Revision...
[*]Grey's pack (soft_econ, soft_pop, USU, food, ranch, ...)
[*][b]this ComPatch[/b]
[/list]

---

**Game 1.13 (exe 1.13.11). The Great Revision 2.0; Grey's pack (declares no versions).**

Pair GR.7 -- 97 shared keys. Full analysis: `_greys/analysis_gr7_tgr_report.md`.

## 1. Country ranks (GR.7a)

`_grey_soft_pop`'s `TRY_REPLACE:` on all eight ranks matches current 1.13 vanilla (TGR's own copy of these ranks, in `TheGreatRevision/common/country_ranks/TGR_POLITICS_country_ranks.txt`, is stale -- see TGR.1 in the plan's open questions, a bug internal to the TGR pairing, not this one). Because soft_pop's body is a full replace, two things TGR adds are silently dropped:

* `state_export_advantage_mult` / `state_import_advantage_mult` on six ranks (major/minor/insignificant powers and their unrecognized counterparts, from `-0.15`/`0.25` up to `-0.60`/`0.75`) -- TGR's "small countries trade more favourably" mechanic;
* `country_construction_add = 30` (great_power) / `20` (major_power) -- a field vanilla and soft_pop never had at all.

Both are restored here, read live out of TGR's files rather than hand-copied.

**Decision 27.08.2026: `country_loan_interest_rate_mult` is commented out wherever soft_pop carries it (six ranks).** TGR's own loan system drops rank-dependent loan interest entirely on purpose (its own file comments the field out on every rank, tagged `#TGR ADJUSTMENT`); soft_pop keeps the vanilla rank-dependent value. This is a genuine design dispute between the two loan systems, not a bug, and the decision was to follow TGR's design here. `decentralized_power` has neither field touched by either side and is not included.

## 2. Four citizenship laws (GR.7b)

Vanilla gives `country_political_strength_full_acceptance_mult` = 0.25/0.20/0.1/0.1 on `law_ethnostate`/`law_national_supremacy`/`law_racial_segregation`/`law_cultural_exclusion`. TGR `INJECT`s the exact same numbers negated -- a counterweight that nets the vanilla bonus to zero. `_grey_soft_pop`'s later `TRY_REPLACE` restates the vanilla (positive) values, and TGR's `INJECT` lands under a body that no longer has anything to receive it: the classic "counterweight with the opposite sign gets silently resurrected" (`Правила работы с модами Victoria 3`, section 1). Since Grey's numbers still match vanilla exactly, re-issuing TGR's own `INJECT` after the whole Grey's pack is an exact restoration -- four one-line blocks.

## 3. Four defines (GR.7c)

| define | vanilla | TGR | Grey's | why |
| --- | --- | --- | --- | --- |
| `NEconomy.COMPANY_MINIMUM_LEVELS_PER_HQ` | 5 | 1 | 5 | Grey's just restates vanilla -- restore TGR |
| `NEconomy.AUTO_DOWNSIZE_BUILDING_MIN_UNUSED_TRADE_CAPACITY` | 20 | 100 | 20 | same |
| `NPops.MAX_DEMAND_ADJUSTMENT_BASE_AMOUNT` | 0.01 | 0.05 | 0.01 | same |
| `NPops.MAX_DEMAND_ADJUSTMENT_SCALED_AMOUNT` | 0.09 | 0.10 | 0.09 | same |

Defines merge per key, last mod loaded wins. On these four, Grey's isn't making a decision -- it's a no-op restatement of vanilla -- while TGR made a deliberate change on each, and that change is silently gone. `NEconomy.PRICE_RANGE` / `BUY_SELL_DIFF_AT_MAX_FACTOR` are **not** in this list: that's decision point #3 of the plan, soft_econ's own values (0.9 / 3) were kept on purpose because soft_econ's `GOODS_SHORTAGE_PENALTY_THRESHOLD = 0.4` is tuned against them (`1 / 3 ≈ 0.33`; TGR's 1.65 would give 0.61 and break that internal relationship).

## 4. `building_trade_center`'s level cap (GR.7d)

**Resolved 27.08.2026 by an in-game screenshot check (report section 11):** the Grey's-branch trade center panel showed no max-level row -- `grey_usu`'s full-body override drops `has_max_level` entirely (vanilla trade centers have no cap at all; `has_max_level` is a TGR-only addition), so the building has been unlimited from turn one and TGR's ten trade techs (`state_building_trade_center_max_level_add = 10` each, `TGR_TRADE_society.txt`) were restoring nothing.

None of those ten techs are overridden by Grey's (only `stock_exchange` gets an unrelated `TRY_INJECT`), so the +10 grants are intact -- `has_max_level = yes` is the only field restored. The earliest of the ten, `international_trade`, is era_1 and two hops from the very first society tech (`urbanization` -> `tech_bureaucracy` -> `international_trade`) -- in practice a handful of years into most campaigns, not a late-game gate. Before researching any of the ten, the trade center's max level is 0 (can't be built at all) -- the same has_max_level-starts-at-0 pattern vanilla itself uses on `building_construction_sector`.

## 5. Seven remaining ownership production methods (GR.7e)

14 of the original 21 `state_modifiers`-losing ownership PMs are already closed via `_greys/greys+ef done` (GR.5, a file shared between this pair and E&F). These are the remaining 7 from `TGR_TRADE_private_infrastructure_investors.txt` / `yMoG_USU_owners_tax_pms.txt`.

Five carry no `state_modifiers` at all in `grey_usu` -- a clean loss, all three TGR fields restored: `pm_financial_district_privately_owned`, `pm_financial_district_publicly_traded`, `pm_financial_district_principle_divine_economics_2`, `pm_manor_house_bureaucrat_ownership`, `pm_manor_house_clergy_ownership`.

**Correction to the report while writing this generator:** `pm_manor_house_privately_owned` and `pm_manor_house_principle_divine_economics_2` are not a clean loss -- `grey_usu` already gives them their own `state_modifiers` (`workforce_scaled { state_tax_capacity_add = -1 }`), a genuine design choice, not silence. Decision 27.08.2026: restore only TGR's two fields with no Grey's equivalent in any sub-block (`state_weekly_trades_add`, `state_trade_capacity_add`), added as a sibling `level_scaled` block; Grey's own `state_tax_capacity_add` is left alone -- the same call already made on `pm_trade_center` (report section 2.2).

## 6. `building_food_industry` and `bg_trade` (GR.7f)

`building_food_industry`'s `building_group` is restored to `bg_consumer_goods` (TGR's own group, which its industrial decree and economic-stimulus laws are keyed to). `levels_per_mesh` and `production_method_groups` are left as Grey's.

**Found while writing this, unrelated to TGR:** `grey_food` also swaps the vanilla/TGR `pmg_automation_building_food_industry` production-method group for its own `pmg_preservation` (a whole canning/preservation content addition). That's Grey's own deliberate content dropping a vanilla mechanic, not a TGR loss -- noted in the plan, left untouched, no file.

`bg_trade` gets TGR's `cash_reserves_max = 500000` back -- `grey_usu`'s copy has the field commented out (with a stale value of `5000`, not TGR's number). `infrastructure_usage_per_level` and `urbanization` are deliberate Grey's changes and stay as-is.

## 7. Class A/B production-method restores

The report catalogued 91 lines/38 records of class A ("TGR added a field, Grey doesn't carry it") and 28 lines/9 records of safe class B ("Grey reverted to vanilla, TGR's edit is gone"). 63 of the class A lines were the 21 ownership records covered above (GR.5 + GR.7e). Checking what remained against the live source while writing this generator found most of it wasn't a clean restore after all:

* **Restored:** four government-administration PMs get TGR's doubled `country_bureaucracy_add` back (`pm_simple_organization`, `pm_horizontal_drawer_cabinets`, `pm_vertical_filing_cabinets`, `pm_switch_boards`); `pm_rail_transport_mine`/`pm_steam_rail_transport` get TGR's automation-efficiency numbers back (less transport input, more labor saved) plus vanilla's `state_pollution_generation_add = 10`, which `grey_usu` drops outright on both (not a TGR change -- just structurally missing); `pm_refrigerated_rail_cars_building_fishing_wharf` gets the same automation numbers, but its `state_modifiers` is left alone (`grey_usu` swaps vanilla's pollution field for its own `building_food_industry_throughput_add` there -- a deliberate choice, not a loss).
* **Correction, excluded:** `pm_steel_passenger_carriages`/`pm_wooden_passenger_carriages` and `pm_trade_center_trade_quantity_normal/high/very_high` looked like clean class B restores in the report, but both turned out to carry `grey_usu`'s own parallel mechanic in the same field (a shared `goods_input_usu_train_paths_add`/`goods_input_usu_logistics_add` baseline on every tier, with the report's "missing" number already present as Grey's own second value on the same key). Restoring the tier number on top would double-count against USU's own baseline -- left as Grey's, no file, same treatment as class C.
* **Correction, already covered:** `pm_anchorage`'s `goods_input_clippers_add`/`goods_output_merchant_marine_add` live in the same `TGR_TRADE_private_infrastructure_ports.txt` file as the already-closed port employment ladder (report section 13, "Порты... оставлено Grey's, файла нет") -- not a separate item.

Ports, rails proper, automation/cooling, and trade-center employment (class C) were already decided 27.08.2026 with no file needed (report section 13) -- Grey's/USU's numbers are kept everywhere; rails overlaps GR.16 for the addon-LLWA layer specifically, not this pair. `foreign_investment_rights`, `trade_states`, `monopoly_charter`, `building_construction_sector`, and the 14 `pm_company_headquarter_*` are cross-task with GR.8, GR.14, GR.10 (closed as not-a-conflict), GR.2, and GR.5 respectively -- handled in those pairs, not duplicated here.

## Maintenance

`tools/regen_greys_tgr.py`; `--check` reports drift without writing. Every restored value is read live from TGR's and Grey's current files with an assert on the expected shape -- a future update to any of the four mods that changes one of these values makes the generator fail loudly rather than silently write a stale number.
