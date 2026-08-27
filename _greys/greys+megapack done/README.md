# ComPatch: Grey's + megapack `no t&r`

<!-- meta
пара: Grey's × сборка «мегапак no t&r»
статус: done
версии: Game 1.13 (exe 1.13.11) — MegaComPatch TGR+PSC+KAI+E&F+MR+PBE (no t&r) 1.13.11.2, Grey's pack (версии моды не объявляют).
позиция: после всей пачки Grey's
файлов: 1
генератор: tools/regen_greys_megapack.py
зависит от: `_greys/greys+psc done` (GR.2, закрывает пять из семи затронутых ключей)
-->

## Для мастерской

[h1]ComPatch: Grey's + megapack no t&r[/h1]
[b]Game 1.13 (exe 1.13.11) — MegaComPatch (no t&r), Grey's pack.[/b]

[b]Not for players using addon-LLWA[/b] — install [i]ComPatch Grey's + addon-LLWA[/i] instead, it covers `building_airport` too (with LLWA's own groups added). Use this ComPatch only if you run the megapack + Grey's pack without addon-LLWA.

grey_usu re-declares two buildings the megapack already wired into E&F's economy (E&F × Morgenroete's own ComPatch) with full bodies, dropping that wiring silently: `building_airport` and `building_dubois_national_park`. This patch puts it back.

[h2]Load order[/h2]
[list]
[*]…MegaComPatch (no t&r)…
[*]Grey's pack (soft_econ, soft_pop, USU, food, ranch, …)
[*][b]this ComPatch[/b]
[/list]

---

## Подробности

**Game 1.13 (exe 1.13.11). MegaComPatch TGR+PSC+KAI+E&F+MR+PBE (no t&r) 1.13.11.2; Grey's pack (declares no versions).**

Pair GR.17. Not a raw mod-vs-mod pair like the others in `_greys/` — the megapack is a *build* (all its compatches already merged into single winning bodies), and `pair_matrix.py` only compares blocks in the load-order chain, so it never sees this class of gap. `content_holes.py --only builds` does: it diffs each build (megapack, addon-VC, addon-HC, addon-LLWA) against whatever loads after it and reports 7 keys where the Grey's pack (specifically `grey_usu`) silently drops something the megapack already carries.

## Что теряется без этого компача

Two buildings, both wired into E&F's economy by `_ef/ef+morg done` (folded into the megapack build as `common/buildings/zz_ef_mr_buildings_inject.txt`):

| здание | что несёт мегапак | что делает `grey_usu` |
| --- | --- | --- |
| `building_airport` | `TRY_INJECT:` `pmg_market_liquidity` + `pmg_private_ownership_manufacture_stock` | `TRY_REPLACE:` full body (`zMoG_USU_MR_airports.txt`, "Respecified purely so that the auto-expand rules are properly managed") — neither group named |
| `building_dubois_national_park` | `TRY_INJECT:` `pmg_market_liquidity` only (this building is `can_build_private = { always = no }` in both bodies — never a stock candidate) | `TRY_REPLACE:` full body (`zMoG_USU_MR_nat_park.txt`) — group not named |

Both drop out of E&F's economy silently — no liquidity for either, no stock switching for the airport — nothing in error.log.

## Что не здесь

`content_holes.py` reports 7 keys under "МЕГАПАК × USU", not 2. The other five are already closed elsewhere and are not repeated here:

* `building_construction_sector` and four `pm_*_buildings` construction production methods — `_greys/greys+psc done` (GR.2) already restores the full merged body (PSC's construction model + KAI's iron branch), and that compatch loads after the whole Grey's pack too, so it wins outright regardless of what the megapack itself carried on those records. Writing a second `REPLACE:`/`TRY_INJECT:` here would be redundant at best, a second-compatch-on-one-record risk at worst.

`content_holes.py` also reports `defines: NEconomy` under "МЕГАПАК × soft_econ" (1 key) — this is `PRICE_RANGE` (megapack 0.85 vs soft_econ 0.9), already decided as развилка №3 in the plan (26.08.2026: soft_econ's value wins, no pin needed — `_grey_soft_econ` loads last and defines merge per field, so nothing is silently lost, the later number simply applies). No file.

## Отдельно: `building_airport` и addon-LLWA

`_greys/greys+llwa done` (GR.9/GR.16) restores the same record with **five** groups: addon-LLWA's own three plus these same two E&F groups. If you install addon-LLWA, use that compatch instead — it is the strictly more complete fix. Installing both this compatch and `greys+llwa done` together would `TRY_INJECT:` `pmg_market_liquidity` and `pmg_private_ownership_manufacture_stock` onto `building_airport` twice. `building_dubois_national_park` has no such overlap — addon-LLWA never touches it — so that half of this compatch is always safe regardless of which building_airport fix you use.

## Как сделан мердж

`common/buildings/zz_greys_megapack_buildings_inject.txt` — `TRY_INJECT:` the exact groups read live out of the megapack's own `zz_ef_mr_buildings_inject.txt`, onto both buildings. `TRY_INJECT:` so a building renamed in a future Grey's version does not spam the error log.

## Пересборка

`tools/regen_greys_megapack.py`; `--check` reports drift without writing. Reads the group list from the megapack's own file (not a hand-written copy), reads grey_usu's two bodies, and asserts on every run that each building is still missing exactly the groups the megapack injects — so a fix on the Grey's side, or a group list change on the E&F/Morgenroete side, turns into a failed run with a message. Re-run after any megapack, E&F, Morgenroete or Grey's update.
