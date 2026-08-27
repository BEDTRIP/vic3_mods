# ComPatch: Grey's + E&F

<!-- meta
пара: Grey's × E&F+hotfix (GR.5)
статус: done
версии: Game 1.13 (exe 1.13.11) — E&F V4 + Hotfix 4.1.7.4, Grey's pack (версии моды не объявляют), TGR 2.0.
позиция: после всей пачки Grey's
файлов: 6
генератор: tools/regen_greys_ef.py
зависит от: TGR (в тело 14 методов ШК перенесён его блок state_modifiers)
-->

## Для мастерской

[h1]ComPatch: Grey's + E&F[/h1]
[b]Game 1.13 (exe 1.13.11) — Economic and Financial Mod (E&F) V4 + Hotfix, Grey's pack.[/b]

E&F wires a building into its economy by `INJECT:`ing two production method groups into it. Five buildings that the Grey's pack re-declares with full bodies — food industry, livestock ranch, port, power plant, trade center — therefore drop out of E&F's economy entirely: no liquidity, no stock, no private-ownership switching, and nothing in the log. The same pack rewrites all fourteen company-headquarter methods and undoes E&F's cut to headquarter employment. Grey's USU module also adds four brand-new privately-owned buildings — river port, power grid, hydro power plant, public green — that E&F's whitelist has never heard of at all. This patch puts all three back.

[h2]Load order[/h2]
[list]
[*]…TGR → PSC → Kuromi's AI → E&F → E&F Hotfix…
[*]…MegaComPatch…
[*]Grey's pack (soft_econ, soft_pop, USU, food, ranch, …)
[*][b]this ComPatch[/b]
[/list]

---

**Game 1.13 (exe 1.13.11). E&F V4 + Hotfix 4.1.7.4; Grey's pack (declares no versions); The Great Revision 2.0.**

Pair GR.5 — 24 shared keys, in four groups.

## 1. Six buildings, five of them fixed here

E&F ties a building into its economy with `INJECT:` of `pmg_market_liquidity` + `pmg_private_ownership_*_stock` (`common/buildings/ef_*.txt`). A later mod that re-declares the same building with a **full body** wins over that inject and the groups are gone. The Grey's pack does exactly that six times:

| здание | тело от | префикс | что теряется |
| --- | --- | --- | --- |
| `building_food_industry` | grey_food | `REPLACE_OR_CREATE:` | liquidity + manufacture stock |
| `building_livestock_ranch` | grey_food_2_ranch | `REPLACE_OR_CREATE:` | liquidity + agricultural stock |
| `building_port` | grey_usu | `REPLACE_OR_CREATE:` | liquidity + manufacture stock |
| `building_power_plant` | grey_usu | `REPLACE:` | liquidity + manufacture stock |
| `building_trade_center` | grey_usu | `REPLACE_OR_CREATE:` | liquidity + manufacture stock |
| `building_railway` | grey_usu | `REPLACE_OR_CREATE:` | **не здесь**, см. ниже |

`common/buildings/zz_greys_ef_buildings_inject.txt` re-issues the same two groups per building with `TRY_INJECT:`, reading the group names out of E&F itself rather than from a list of our own. Nothing else is needed: all five buildings are already in E&F's hand-written `private_ownership_production_stocks` switch (they are vanilla buildings), only the group list on the building was lost.

**`building_railway` is deliberately absent.** USU turns `building_railway` into a station (`pmg_base_building_rail_terminal`) and moves the actual line to a new `building_usu_railway_line`, and the body that has to win on that record is the merged one from the LLWA addon (it already carries Morgenröte's `pmg_gaudi_communication`, LLWA's `LLWA_pmg_private_expansion` and E&F's two groups). That is one record for three open tasks — GR.9, GR.16, GR.17 — and two compatches must never `REPLACE:` one record, so it is left to them.

## 2. Fourteen company-headquarter methods

Three mods rewrite all fourteen `pm_company_headquarter_*` in a row:

* **TGR** — `REPLACE_OR_CREATE:`, vanilla employment plus its own `state_modifiers` (`state_weekly_trades_add`, `state_trade_capacity_add`, `state_tax_capacity_add`);
* **E&F** — `REPLACE:` naming `building_modifiers` and nothing else: headquarter employment drops from vanilla's 50 per level to about 10, and shopkeepers get a share;
* **grey_usu** — `REPLACE_OR_CREATE:` with a full body: its own rebalance back to 50 per level (25 capitalists / 15 shopkeepers / 10 clerks), share numbers derived from its own dividend math, and it loads last.

Both authors moved the same way (fewer people in ownership buildings, shopkeepers added with a share) — only the scale differs, and E&F's is 5× smaller. **Decision 27.08.2026: E&F's scale wins, USU's structure stays.** `common/production_methods/zz_greys_ef_company_hq.txt` re-issues USU's own body for each of the fourteen with E&F's `building_modifiers` block put back into it.

**TGR's `state_modifiers` are carried in the same body on purpose.** USU never names that sub-block, so whether it survives USU today depends on the `REPLACE:` semantics question still open in `Правила работы с модами Victoria 3`, section 1. A full body that names it is correct under both readings — and it is why TGR is listed as a dependency of this compatch even though the pair is Grey's × E&F.

## 3. Three companies — nothing to fix

`company_Bankenverein`, `company_HandelsBanken` (E&F hotfix) and `company_standard_oil` (E&F) are all touched by USU with `TRY_INJECT:` only — `extension_building_types`, `building_types`, a `prosperity_modifier`. Injects into a list add to it. E&F's own `building_types` and `possible_prestige_goods` on the same three are untouched. Checked, no file.

## 4. `NEconomy` — a decision, not a patch

Two defines overlap, and `_grey_soft_econ` loads later, so it wins both:

* `PRICE_RANGE` — megapack 0.85 vs soft_econ 0.9 (это развилка №3 плана, «потом подумаю»);
* `GOODS_SHORTAGE_PENALTY_MAX` — E&F 0.9 vs soft_econ 0.7.

Defines merge per key, both are single numbers, and no third mod touches either. Nothing is silently lost — the later number simply applies. Left to развилка №3.

## 5. Four brand-new USU buildings — GR.15

The Grey's USU module adds five buildings E&F has never heard of at all, none of them vanilla, none on anyone else's list — checked across the whole set, no mod but USU itself names any of them: `building_river_port`, `ppp_building_power_grid`, `usu_building_hydro_power_plant`, `usu_building_public_green`, and `building_usu_railway_line`. All five are `ownership_type = self`, so all five are candidates for E&F's stock mechanics — E&F's whitelist simply predates them, the same class of gap `_llwa/llwa+ef done` closed for LLWA's six buildings and `_ef/ef+morg done` closed for Morgenröte's.

`building_usu_railway_line` is **not** here — it is the record USU split `building_railway` into (GR.9/GR.16/GR.17), and it already got `railroad_stock` inside `_greys/greys+llwa done`, folded in there because the LLWA merge on that same record had to happen in one place.

The other four get `manufacture_stock`, all four:

| здание | почему manufacture_stock |
| --- | --- |
| `building_river_port` | прямой аналог `building_port` (уже manufacture_stock) |
| `ppp_building_power_grid` | прямой аналог `building_power_plant` |
| `usu_building_hydro_power_plant` | тот же класс, что `building_power_plant` — второй способ производить электричество |
| `usu_building_public_green` | не очевидно по имени, но тело здания — реальная фабрика услуг: `usu_pmg_public_space_management` / `usu_pmg_public_parklands` дают `goods_output_services_add` / `goods_output_transportation_add` и занятость (laborers, clerks, shopkeepers, bureaucrats), то есть обычное производственное здание. Тот же довод E&F уже применяет к Opera / инструментальным мастерским / изданию Manzoni у Morgenröte — тоже manufacture_stock. Отдельного типа акций для «гражданских удобств» у E&F нет, и среди его собственных 49 зданий ни одного чисто аменити-здания тоже нет.

`common/buildings/zz_greys_ef_new_buildings_inject.txt` adds `pmg_market_liquidity` + `pmg_private_ownership_manufacture_stock` to all four. Because none of the four is on E&F's own switch (`common/scripted_effects/01_financial_scripted_effects.txt` → `private_ownership_production_stocks`), this compatch also needs its own copy of that machinery — same four-file shape as `ef+morg done` / `llwa+ef done`:

* `common/scripted_effects/zz_greys_ef_new_buildings_stocks.txt` — `greys_ef_new_buildings_production_stocks`, the yearly per-state switch;
* `common/on_actions/zz_greys_ef_new_buildings_on_actions.txt` — hooks it into `on_yearly_pulse_country`, additive;
* `common/history/global/zz_greys_ef_new_buildings_init.txt` — runs it once at game start so the buildings are not stuck on "No Stock" for the first year.

## Отдельно: ложная тревога плана

План говорил, что `grey_food` заодно роняет `pmg_automation_building_food_industry`. Проверено: не роняет. Группа автоматизации у ванили состоит из `pm_manual_dough_processing` + `pm_automated_bakery`, и `grey_food` перенёс `pm_automated_bakery` внутрь собственной `pmg_base_building_food_industry`. Автоматизация на месте, просто в другой группе; выпадает только `pm_manual_dough_processing` — «ручной» вариант, то есть балансное решение автора, а не потеря. Ничего не восстанавливаем.

## Maintenance

`tools/regen_greys_ef.py`; `--check` reports drift without writing. The generator reads the group names from E&F, the fourteen keys from E&F's own file, and asserts on every run that E&F still names only `building_modifiers`, that USU still names no `state_modifiers`, that TGR still carries them, and that each of the five buildings is still missing exactly the groups E&F injects — so a fix on the Grey's side turns into a failed run with a message, not a silently pointless file. For the four GR.15 buildings it additionally asserts E&F still defines the manufacture_stock group and PMs, that none of the four is already on E&F's own switch (guards against double-switching if a future E&F version adds native support), that each still carries `ownership_type = self`, and that none already lists E&F's groups. Re-run after any E&F, hotfix, TGR or Grey's update.
