# ComPatch: Grey's + PSC

<!-- meta
пара: Grey's × PSC (GR.2)
статус: done
версии: Game 1.13 (exe 1.13.11) — PSC 1.3.7, Grey's Urban Synergy Unleashed (версии мод не объявляет).
позиция: после всей пачки Grey's, но ПЕРЕД компачем `greys+vc done` (см. «Порядок»)
файлов: 4
генератор: tools/regen_greys_psc.py
зависит от: мегапак (тела взяты из `zz_pb_ef_construction_sector.txt` / `zz_pb_ef_construction_pm.txt`), E&F (`pmg_market_liquidity`, `goods_output_manufacture_stock_add`), `_greys/greys+vc done` (слой VC на четырёх методах — там)
-->

## Для мастерской

[h1]ComPatch: Grey's + PSC[/h1]
[b]Game 1.13 (exe 1.13.11) — Private Sector Construction 1.3.7, Grey's Urban Synergy Unleashed.[/b]

Private Sector Construction and Grey's Urban Synergy Unleashed rework the same thing: the construction sector. PSC turns it into a goods factory feeding a construction regulator and privatises it; USU keeps the vanilla model and rebalances it. USU loads later, so its bodies win — and PSC's chain, E&F's liquidity layer and the merged AI weighting go with them, silently. This patch re-issues the winning bodies after the whole Grey's pack, so the construction system stays PSC's.

[h2]Load order[/h2]
[list]
[*]…PSC → Kuromi's AI → E&F → E&F Hotfix…
[*]…MegaComPatch…
[*]Grey's pack (soft_econ, soft_pop, USU, …)
[*][b]this ComPatch[/b]
[*]ComPatch: Grey's + Victorian Century (if used) — must come after this one
[/list]

---

**Game 1.13 (exe 1.13.11). PSC 1.3.7; Grey's Urban Synergy Unleashed (declares no version); the bodies of the sector and of the four methods come from the megapack, so E&F is required too.**

## The decision this compatch rests on

PSC and grey_usu are **two models of one mechanic**, not two sets of edits to one record:

| | PSC | grey_usu |
| --- | --- | --- |
| construction points | building emits `goods_output_*_construction`, a separate `building_construction_regulator` converts them | `country_construction_add` straight off the method, as in vanilla |
| sector size | ~1000 pops/level, `construction_cost_very_low` = 100 | ~2000 pops/level, `construction_cost_consec` = 20 (2/5 of vanilla) |
| level cap | none | `has_max_level = yes`, capped by its own urban-synergy modifier |
| ownership | `bg_private_infrastructure`, `subsidized = no`, `ownership_type = self`, `can_build_private` | `bg_public_infrastructure`, `is_government_funded = yes` |

There is no line-level merge between those. **Decision 27.08.2026 (развилка №13 плана): PSC wins**, and USU's construction layer is switched off. Everything else in USU is untouched.

## What USU takes away, and what this patch puts back

`grey_usu` loads after everything and writes full bodies:

* **`REPLACE_OR_CREATE:building_construction_sector`** (`yMoG_USU_construction.txt`) — a vanilla body plus its own sizing. Gone with it: E&F's `pmg_market_liquidity`, the whole scripted `ai_value` (PSC's base 2500, KAI's iron clause, the capital kickstart, `ai_construction_sector_price_pressure_bonus`), `ownership_type = self`, `can_build_private`, `ai_nationalization_desire`. Restored in **`common/buildings/zz_greys_psc_construction_sector.txt`**, body copied verbatim from the megapack's `zz_pb_ef_construction_sector.txt` plus one explicit `has_max_level = no` (USU sets `yes`; vanilla documents `no` as the default).
* **`REPLACE_OR_CREATE:` on all four construction methods** (`pm_wooden_buildings`, `pm_iron_frame_buildings`, `pm_steel_frame_buildings`, `pm_arc_welded_buildings`) — vanilla's `country_construction_add` back, PSC's `goods_output_*_construction` gone. That does not just rebalance construction: it **decouples PSC's chain**, because the construction regulator loses its only input and PSC's four construction goods lose their only producer. E&F's `goods_output_manufacture_stock_add` line goes the same way. Restored in **`common/production_methods/zz_greys_psc_construction_pm.txt`**.
* **`REPLACE_OR_CREATE:bg_construction`** (`yMoG_USU_building_groups.txt`) — back to `bg_public_infrastructure` / `is_government_funded = yes`, which undoes PSC's privatised construction and leaves the building's own `ownership_type = self` arguing with a government-funded group. Restored in **`common/building_groups/zz_greys_psc_bg_construction.txt`**, verbatim from PSC.
* **`common/history/buildings/MoG_consec_balancer.txt`** — hands +1 construction sector at game start to every incorporated non-treaty-port state with iron potential, to compensate for USU's own sectors being 2/5 of vanilla size. With PSC's model restored that compensates for a shrink that never happened, and PSC places its own starting sectors in `PSC_buildings.txt`. History containers are additive — no prefix can cancel another mod's `BUILDINGS` block — so this compatch ships **an empty file at the same path**, which is the one documented way to do it. `!! MAINTENANCE !!` the override also swallows anything the Grey's author adds to that file later.

## Порядок относительно `greys+vc done`

Victorian Century `INJECT:`s extra goods inputs and a `state_construction_mult` into the same four construction methods, and those injects die under USU's bodies like everything else. They are restored **not here** but in `_greys/greys+vc done` (GR.1), which re-issues VC's own inject verbatim — so this compatch carries the base body only. Two restorations of one inject would add VC's numbers twice.

That split only works if this file's `REPLACE:` comes **before** that `INJECT:`. Inside the assembled addon the names sort that way by themselves (`zz_greys_…` < `zz_gvc_…`, `r` < `v`); as separate mods in a playset, this compatch must stand **before** `ComPatch: Grey's + Victorian Century`. The generator asserts on every run that `greys+vc done` still re-issues all four injects — if that compatch is removed, the run fails and says so, instead of silently dropping VC's numbers.

## Why one file serves more than one pair here

`Правила — сборка`, section 3, keeps one file to one pair, with an explicit exception for records that two pairs both have to write — and this is that case. `building_construction_sector` is written by PSC, by KAI (`INJECT: ai_value`), by E&F through the megapack merge, and by USU; the four methods by PSC, by the megapack and by USU. Two compatches must never `REPLACE:` one record, so all of it lives in one body here. Consequently these plan items are closed by **this** file and must not get files of their own:

* **GR.17** — `building_construction_sector` losing `pmg_market_liquidity`, and the four `pm_*_buildings`;
* **GR.8** — `building_construction_sector` [KAI vs grey_usu].

## Checked and left alone

* **`NCountry`** — PSC sets `CONSTRUCTION_CAMP_BUILDING`, USU sets `RAILWAY_BUILDING`. Defines merge per key, not per block: different keys, no conflict. (USU's comment says misdirecting the AI is the intended outcome of its own rework — left as the author wrote it.)
* **`my_trigger_event`** — the same CMF helper (`trigger_event = { on_action = $on_action_name$ days = $num_days$ }`) copied verbatim by both mods, and by CMF itself. For `scripted_effects` a bare repeat does not override anyway, and the bodies are identical.
* **`default_auto_expand_rule`** — USU `REPLACE_OR_CREATE`s it with its own auto-expand system. PSC's `bg_construction` only *calls* the trigger by name, so the name still resolves and USU's rule applies to construction the same way it applies to everything else. Not a loss; not restored.
* **`mog_construction_max_level_adjustment`** — USU's urban-synergy modifier keeps being applied on `on_acquired_technology`. With `has_max_level = no` on the sector it has nothing to cap and does nothing. Deliberately not touched.
* **`bg_construction`, field `urbanization`** — PSC's body does not name it (vanilla 5, USU 2). If `REPLACE:` turns out to patch by named field rather than replace the record (the question is still open in the rules), USU's `2` would survive our body here. Left as is on purpose: PSC never stated an intent for that field, and inventing one would be a compatch making up behaviour no author asked for.

## What this pair says about the open `REPLACE:` question

`Правила работы с модами Victoria 3`, section 1, has two contradicting notes on whether `REPLACE:` replaces a record or patches its named sub-blocks. PSC is a data point for "replaces": vanilla's four construction methods all carry `country_modifiers = { workforce_scaled = { country_construction_add = … } }`, PSC's `REPLACE:` bodies name no `country_modifiers` at all, and PSC's whole design depends on that block being gone — if it were merely left alone, every player of PSC would be getting construction points twice, from the chain and from vanilla. Not proof, but the strongest evidence in the set so far. The four methods here still carry an explicit empty `country_modifiers` guard: a no-op under that reading, and the thing that clears USU's block under the other one.

## Maintenance

Everything is generated by `tools/regen_greys_psc.py`; `--check` reports drift without writing. The generator asserts, on every run, the four things this merge assumes about USU (no liquidity group on the sector, `has_max_level = yes`, `bg_construction` back to public infrastructure, `country_construction_add` back in all four methods) and the one thing it assumes about GR.1 (VC's injects re-issued in `greys+vc done`) — if the Grey's author fixes any of them himself, the run fails and says which one. Re-run after **any** of: a PSC update, a Grey's update, or a change to the megapack's two construction files.
