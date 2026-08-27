# ComPatch: Grey's + The Great Revision (WORK IN PROGRESS)

<!-- meta
пара: Grey's × TGR (GR.7)
статус: в работе -- 3 из ~10 файлов, см. "Что ещё не сделано" ниже
версии: Game 1.13 (exe 1.13.11) -- The Great Revision 2.0, Grey's pack (soft_pop/soft_econ/usu declare no version)
позиция: после всей пачки Grey's
файлов: 3
генератор: tools/regen_greys_tgr.py
зависит от: --
-->

## Для мастерской

[h1]ComPatch: Grey's + The Great Revision (WIP)[/h1]
[b]Game 1.13 (exe 1.13.11) -- The Great Revision 2.0, Grey's pack.[/b]

[b]This is a partial patch, published early on purpose.[/b] TGR and the Grey's pack share 97 keys (full breakdown in `_greys/analysis_gr7_tgr_report.md`). This upload covers the three pieces that are fully resolved and don't depend on another pair or an in-game check: country ranks, four citizenship laws, and four defines. The rest -- ownership production methods, bg_consumer_goods/bg_trade, the production-method restores, and the trade-center question -- follow in later versions of this same patch.

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

## What's NOT in this patch yet

* **GR.7d, `building_trade_center` (`has_max_level`)** -- blocked on an in-game screenshot check (does the Grey's-branch trade center panel show a max-level row?). Also touches E&F (GR.5).
* **GR.7e, remaining 7 ownership production methods** (`pm_financial_district_*` × 3, `pm_manor_house_*` × 4) -- 14 of the original 21 are already closed via `_greys/greys+ef done` (GR.5); these seven still need their own restore.
* **GR.7f, `bg_consumer_goods` / `bg_trade`** -- `building_food_industry` needs its building group restored; `bg_trade` needs TGR's `cash_reserves_max = 500000` back.
* **Class A/B production-method restores** (report section 6) -- 91 lines / 38 records of "TGR added a field Grey doesn't carry" and 28 lines / 9 safe records of "Grey reverted to vanilla, TGR's change is gone".
* **Ports, rails, automation, trade-center employment (class C)** -- decided 27.08.2026, **no file needed**: Grey's/USU's numbers are kept everywhere (see report section 13 and the plan). Rails overlaps GR.16 for the addon-LLWA layer specifically, not this pair.
* **`foreign_investment_rights`, `trade_states`, `monopoly_charter`, `building_construction_sector`, the 14 `pm_company_headquarter_*`** -- cross-task with GR.8, GR.14, GR.10 (already closed as not-a-conflict), GR.2, and GR.5 respectively; handled in those pairs, not duplicated here.

## Maintenance

`tools/regen_greys_tgr.py`; `--check` reports drift without writing. Every restored value is read live from TGR's and Grey's current files with an assert on the expected shape -- a future update to any of the four mods that changes one of these values makes the generator fail loudly rather than silently write a stale number.
