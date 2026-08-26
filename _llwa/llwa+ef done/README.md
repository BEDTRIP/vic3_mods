# ComPatch: LLWA + E&F

**Game 1.13 (exe 1.13.11). Locomotion: Land, Water, & Air (LLWA) 2.6.3; Economic and Financial Mod (E&F) - V4.**

The plan called this pair `noneed`. That verdict came from `pair_matrix.py`, which compares keys both mods define — a building only LLWA defines can never show up in that comparison, so it can never show up as a conflict either. This is exactly that class of gap: not a key two mods fight over, but content one mod added that the other's per-building whitelist was written before and has never heard of.

## Load order

1. …E&F → E&F Hotfix…
2. …LLWA…
3. **this ComPatch**

**This patch must load after both.**

## What was missing

LLWA adds six buildings that can be privately owned (`ownership_type = self`): `LLWA_building_roadway`, `LLWA_building_waterway`, `LLWA_building_riverway`, `LLWA_building_airway`, `llwa_building_freight_depot`, `llwa_building_exchange`. (A seventh, `LLWA_building_logistics_hub`, is `ownership_type = no_ownership` — excluded here on purpose, it can't be privately owned at all.)

E&F ties a building into its economy in exactly two places, both hand-written lists of building names, checked live:

* `common/buildings/ef_*.txt` — `INJECT:` adding `pmg_market_liquidity` / `pmg_private_ownership_*_stock` to the building's `production_method_groups`. Private infrastructure coverage: `building_port`, `building_railway`, `building_trade_center`, `building_manor_house`, `building_financial_district`.
* `common/scripted_effects/01_financial_scripted_effects.txt` → `private_ownership_production_stocks` — a yearly check switching each building between "No Stock" and "Majority Stock" production methods based on `private_ownership_fraction`. 49 buildings hand-listed; `railroad_stock` covers exactly one — `building_railway`.

None of LLWA's six buildings are in either list, and — checked across the whole mod set, not just E&F — no mod outside LLWA itself mentions any of the six by name. Without this patch LLWA's entire transport network (roads, canals, rivers, air routes, freight depots, exchanges) sits completely outside E&F's economy: no liquidity, no stock, no private ownership, nothing in error.log to say so.

## What's in this patch

Same four-file shape `_ef/ef+morg done` already uses to wire Morgenroete's 62 custom buildings into E&F — scaled down to LLWA's six, all on the **same** stock type: `pmg_private_ownership_railroad_stock`. LLWA's whole network is road/water/air transport infrastructure, not manufacturing, agriculture, or mining, and `railroad_stock` already exists and already covers `building_railway` — no new production method group, no new localisation (the group's display name is already patched into the chain by `ef+morg done`'s own loc file, present regardless of whether Morgenroete itself is running).

1. **`common/buildings/zz_llwa_ef_buildings_inject.txt`** — `TRY_INJECT:` `pmg_market_liquidity` + `pmg_private_ownership_railroad_stock` onto all six.
2. **`common/scripted_effects/zz_llwa_ef_private_ownership_effects.txt`** — `llwa_private_ownership_production_stocks`, the same shape as E&F's own switch and `ef+morg done`'s `mr_` variant: a yearly per-state check toggling `pm_no_private_ownership_railroad_stock` / `pm_private_ownership_majority_railroad_stock` on `private_ownership_fraction > 0.5`.
3. **`common/on_actions/zz_llwa_ef_on_actions.txt`** — hooks the switch into `on_yearly_pulse_country`. Additive: on_actions of this form stack across mods, nothing is overridden.
4. **`common/history/global/zz_llwa_ef_stocks_init.txt`** — calls the same switch once at game start (`GLOBAL` blocks stack too), so buildings aren't stuck on "No Stock" for the whole first year before the yearly pulse first fires.

No inflation-basket patch: LLWA's two goods (`llwa_market_conn`, `llwa_logi_conn`) are both `tradeable = no` and `fixed_price = yes`, so they never enter E&F's consumer/raw-material baskets.

## How the merge is made

`tools/regen_llwa_ef.py`. Asserts all six buildings are still defined by LLWA, asserts E&F still defines the two railroad-stock production methods and the `pmg_private_ownership_railroad_stock` group, and asserts none of the six buildings are already present in E&F's own `private_ownership_production_stocks` (guards against double-switching if a future E&F version adds LLWA support itself).

## Notes

* **Which stock type LLWA's buildings get was a design decision, not something the files settle** — E&F splits private ownership into `agricultural_stock` / `manufacture_stock` / `mining_stock` / `railroad_stock`, and none of the four is an obvious fit for roads/canals/rivers/air routes/depots/exchanges by content alone. Decided: all six get `railroad_stock`, treating LLWA's whole network as one transport category rather than splitting it.
* **`LLWA_building_logistics_hub` is excluded on purpose**, not an oversight — `ownership_type = no_ownership` means it can never be privately owned, so it has nothing for E&F's stock mechanics to attach to.
* **Maintenance.** Everything is generated by `tools/regen_llwa_ef.py`. Re-run after LLWA or E&F update; `--check` reports drift without writing.

## For Steam

[h1]ComPatch: LLWA + E&F[/h1]
[b]Game 1.13 (exe 1.13.11) — Locomotion (LLWA) 2.6.3, Economic and Financial Mod (E&F) - V4.[/b]

E&F registers buildings for its stock/liquidity mechanics by a hand-written per-building list that predates LLWA. LLWA's six privately-owned buildings — roads, canals, rivers, air routes, freight depots, exchanges — are on nobody's list, so LLWA's whole transport network sits outside E&F's economy entirely. This patch wires all six in, the same way E&F's own compatch with Morgenröte already does for that mod's 62 buildings.

[h2]Load order[/h2]
[list]
[*]…E&F…
[*]LLWA
[*][b]this ComPatch[/b]
[/list]
