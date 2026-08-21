# E&F 1.13.10 Hotfix

Fixes for **Economic and Financial**, repository version **04.07.2026**, on Victoria 3 **1.13.10**.
Load it **after E&F**. It does not depend on the E&F + Morgenröte ComPatch and works without it.

Eight independent blocks: **goods limit**, **history**, **GUI**, **alerts**, **local_currency issuance**, **currency laws**, **script guards**, **dev panel**.

---

## 1. The goods limit — the big one

Victoria 3 1.13 cannot digest more than **128** goods. Established empirically with dummy filler goods: 128 loads, 130 and 131 crash on entering the game, without a single script error in the log.

E&F on its own brings **126** (53 vanilla + 73 of its own). That leaves two slots. Any mod adding three or more goods breaks the game:

| build | goods | result |
|---|---:|---|
| E&F | 126 | works |
| E&F + Morgenröte (+5) | 131 | **crash** |
| E&F + Morgenröte + PSC (+4) | 135 | **crash** |

The E&F author seems to have hit the same ceiling: moving to 1.13 he cut 32 goods from the mod and added none, landing on 126.

### What is cut here

Eight currencies are commented out in `common/goods/ef_00_goods.txt`, the same way the author cut his own 32. Laws, production methods, variables and localisation stay behind; they do not count towards the goods total.

| currency | why it is safe |
|---|---|
| `eco_central_african_eco_c` | `currency_identifiers` is always 0 — no country and no tag stands behind it |
| `eco_east_african_eco_c` | same |
| `eco_west_african_eco_c` | same |
| `dinar_c` | the generic base currency, always 0, handed to nobody |
| `peso_c` | the generic base currency, always 0, and there are eight named pesos besides |
| `gulden_indies_guilder_c` | bound to `c:DEI`, but history gives DEI `rupee_indonesian_rupiah` — a duplicate that never fires |
| `dollar_caribbean_dollar_c` | Haiti is moved to "no currency" (see below) |
| `dollar_new_zealand_dollar_c` | New Zealand is moved to "no currency" |

Result: **118** goods instead of 126.

| build | now |
|---|---:|
| E&F + hotfix | 118 |
| + Morgenröte | **123** |
| + Morgenröte + PSC | **127** |

---

## 2. History

### `common/history/global/zz_ef_currency_fix.txt` (new, additive)

`GLOBAL` blocks stack, and `zz_` is processed after `99_ef_history_global_variable.txt`, so this file overrides nothing — it simply appends its `activate_law` calls last.

**Württemberg.** E&F gives it `law_gulden_south_german_gulde_currency` — no trailing `n`. No such law exists, `activate_law` silently does nothing, and WUR ends up with no currency at all even though the good `gulden_south_german_gulden_c` is alive. We hand it the correct law.

**Thirteen countries → `law_no_market_liquidity`.** Eleven of them hold currencies the author cut while forgetting to remove the `activate_law`: Liberia, Costa Rica, Ecuador, El Salvador, Guatemala, Honduras, Nicaragua, Paraguay, Uruguay, Venezuela, Dai Viet. Plus Haiti and New Zealand, whose currencies we cut ourselves.

Why this matters. A named currency law with no good behind it is a worse state than having no currency: the stock `pm_no_currency_type` and `pm_no_market_liquidity` never switch on (`law_no_market_liquidity` is what unlocks them), and the named production methods that run instead point at nothing. The bank mints nothing, buildings pay nothing for liquidity. `law_no_market_liquidity` is the first law in `lawgroup_currency_type`, with no requirements and no effects — most of the world already lives on it.

### `common/history/buildings/00_ef_building.txt` (overrides the E&F file)

Two edits, everything else copied byte for byte.

**`s:STATE_ANDALUSIA` → `s:STATE_LOWER_ANDALUSIA`.** No such state exists in 1.13; Andalusia is split into Lower and Upper. Because of it Spain never got its starting silver mine.

The target state was picked from the deposit, not from history: Spain's `silver_mine_max_level` modifier is granted to `STATE_LOWER_ANDALUSIA` in `common/history/states/01_ef_states.txt:67`. Without it `building_silver_mine` fails its `possible`/`potential` and never appears. The first version of this hotfix used Upper — an in-game check showed an empty Upper Andalusia and a 0/10 deposit in Lower.

**The `#GRE` block is commented out.** It is a character-for-character copy of the `#PRU` block with the tag swapped, `company_PreussischeSeehandlung` included: Greece was handed gold and silver mines in Saxony and Brandenburg. Greece owns neither state, so `region_state:GRE` returns an invalid object and five `create_building` calls run in a NULL state.

---

## 3. GUI

E&F overrides **32** vanilla `.gui` files. Some are genuine reworks for the financial system, but six had fallen hundreds of lines behind 1.13. That is more dangerous than it sounds: the engine looks some widgets up **by name**, and when the name is missing from the overriding file the game does not complain quietly — it crashes.

That is exactly what the crash on opening the world map looked like:

```
[pdx_gui.h:91]: Could not find widget 'enemy_naval_mission_marker'
                in file 'gui/map_markers.gui'
```

Vanilla has that widget (`map_markers.gui:3995`); the E&F copy does not.

### Restored (vanilla 1.13.10 + the `@money!` → currency symbol substitution)

| file | behind by | what was lost |
|---|---|---|
| `map_markers.gui` | −420 lines | `name=`: `enemy_naval_mission_marker`, `coastal_building_marker`, `enemy_frame`; `type=`: `naval_mission_marker_dot` — **crash on map load** |
| `custom_tooltip.gui` | −336 | `type=`: `naval_mission_marker_tooltip_fleet`, `coastal_building_marker_tooltip_row`, `treaty_tooltip_article_entry` — tooltips for those same naval markers |
| `military_formation_panel.gui` | −387 | `type=`: `military_formation_cancel_invasion_button` — a candidate for the crash on opening the military tab |
| `frontend/shared/lists.gui` | −121 | `type=`: `dropdown_menu_round`, pre-1.13 dropdown structure |
| `popups.gui` | −135 | `name=`: `amount_input`, `decommission_supply_ships_window` |
| `right_click_menu.gui` | −71 | `name=`: `enemy_fleets_on_mission_in_sea_region` |

Verified: across all six restored files not a single `name=` and not a single `type=` is missing relative to vanilla 1.13.10.

What is lost from the E&F side is minimal and cosmetic: six `using = tooltip_above` in the markers, one `tooltip = "TOOLTIP_STATE_DEVASTATION"`, one `text = "[MilitaryFormation.GetNameNoIcon]"`, and the `treaty_tooltip_article` variants under `acquire_monopoly_for_company`. Every money string is reproduced automatically by the `@money!` substitution.

### ⚠ Two more files with the same illness — left alone

| file | missing `name=` | when it blows up |
|---|---|---|
| `budget_panel.gui` | `declare_bankruptcy_button`, `bankruptcy_progress_bar`, `bankruptcy_progressbar` | when the bankruptcy interface is shown |
| `construction_panel.gui` | `ship_construction_queue_pages` | when the ship construction queue is opened |

These cannot be swapped for vanilla: they are real E&F reworks (−145/+218 and −113/+105) and hold his entire budget mechanic. They need a manual merge — take vanilla 1.13 and port the E&F changes onto it. A separate job.

---

## 4. Alerts — 70,000 errors per session

`common/alert_types/00_ef_alert_types.txt` holds 32 alerts, 31 of which read variables that are uninitialised in most games:

- **29 `store_release_*`** (ammunition, grain, coal, oil…) read `<good>_store_month_fixe`, `store_<good>_time` and friends. These are national stockpile variables, and the stockpile's production methods and PM groups live in `17_ef_national_stockpile.zip` — the game does not read archives, and no building with the `bg_national_stockpile` group exists in the mod. No data, no variables.
- **2 `selle_bond_maturity_yers_time_*_Y`** read `selle_bond_maturity_yers_time_1..10` in market scope.

The alerts are declared with `script_context = player_country` and `player_market`, meaning they are re-evaluated on every change of played country. Hence the outcome: in a test game those two families produced **on the order of 70,000** entries like

```
Value of wrong type in 'common/alert_types/00_ef_alert_types.txt:1017'. Got value of type 'none'
Failed to fetch variable for 'selle_bond_maturity_yers_time_6' due to no variables in scope
```

and that was the **only** source of errors in the log, discounting noise from the base game.

**What was done.** Every `valid` block got `has_variable` guards for each variable that alert reads — directly and through the `*_time_rest` script values in `00_economic_scripted_value.txt`. No data, no evaluation, no noise. With data present it behaves exactly as before.

31 of 32 alerts are patched. `fso_alert` is untouched: it reads no variables.

**A second fix in the same file.** Two alerts, `selle_bond_maturity_yers_time_5_Y` and `_10_Y`, are declared `script_context = player_market` but read `var:selle_bond_maturity_yers_time_1..10`. Markets in Victoria 3 do not support variables at all — the engine answers `This scope doesn't support variables. Scope: Market ...`. Those two alerts could never have worked.

The variables themselves are set in `common/history/global/00_ef_financial_global_variable.txt` inside `GLOBAL = { every_country = { ... } }`, i.e. they are **country-scoped**. So `script_context` is changed to `player_country` — the error goes away and the alert finally starts doing what it was meant to.

Only live lines are patched: the file also holds 28 commented-out `buy_sell_*_order` drafts with the same `player_market`, and the patch leaves them alone.

One caveat: where an alert reads five variables through an `or`, all five are now required. Previously, with partially populated data, one branch evaluated while the rest threw errors — so the result was undefined either way.

---

## 5. `local_currency` issuance — computed, not handed out flat

**What it was.** E&F puts the `no_money_production` modifier on every country without a monetary system:

```
no_money_production = {
	state_sell_orders_local_currency_add = 2500
}
```

It is a country modifier, so 2500 units landed in **every state** the country owns, with no regard for population, wealth or anything else. About 600 of the game's 724 countries have no monetary system, and their cheap local currency flooded the shared markets: any currency satisfies the currency need, local currency is cheaper, so pops of proper nations covered `popneed_currency` with it instead of their own national money.

**What it is now.** The flat issuance is disabled at the source:

```
REPLACE:no_money_production = {
	icon = gfx/interface/icons/timed_modifier_icons/no_money_production.dds
}
```

The entry stays alive, so every `has_modifier = no_money_production` check in E&F keeps working — it simply cannot print money anymore. In its place the country gets what the formula computes:

```
country demand = population/1000 × f(average standard of living) × 0.0132
per state      = demand / number of states, at least 25
```

> ⚠ **Formula validation mode is currently ON: the calculation applies to ALL countries without a monetary system.** Normal behaviour — throttling only those sitting in someone else's market with a real currency — is restored by uncommenting the `market` block in `common/scripted_triggers/zz_ef_local_currency_triggers.txt`.

### Why at the source rather than by subtracting it back

That is how it worked before — a modifier with a base of `-1` subtracting the excess from E&F's 2500. Dropped for two reasons, both of which showed up in game:

1. **A month of lag.** E&F applies `no_money_production` from the `law_no_monetary_system` effect on its own pulse, while the game spreads `on_monthly_pulse_country` across the days of the month. The state printed the full 2500 in between — which is what "2.5k keeps popping up on random vassals" was. Countries born mid-game (revolts, releases, unifications) started life with the full amount.
2. **A ceiling.** If the computed demand exceeded 2500 per state there was nothing left to subtract and the country kept E&F's number. The grant has no upper bound now beyond a `max = 25000` sanity cap.

### Why not from actual consumption

Tried and abandoned; the knowledge was expensive, so it is written down. Reading `state_goods_consumption` for `local_currency` works technically: the per-state sum accumulates inside a country-scoped script value and stays a country-scoped number, exactly like vanilla's `country_total_urbanization`. It fails on meaning.

**In a flooded market, consumption measures availability, not need.** Currency is plentiful and cheap → pops happily cover `popneed_currency` with it → consumption is high → we allow printing more → there is even more of it. The Ionian Islands on the British market (188k people, ~113 units by the formula) printed the full 2500 that way.

Capping the measurement at 2× the formula killed the runaway but produced the same thing in a milder form: everybody pinned themselves to the cap and steadily ran at twice the computed value.

"They genuinely need this much" cannot be told apart from "they are simply getting it cheap" through consumption. Real demand (`buy_orders`) is only computed by the game at market level, where it is shared across every participant and useless for sizing one small country:

| scope | available |
|---|---|
| market | `market_goods_buy_orders`, `market_goods_consumption`, `market_goods_delta`, production, imports, exports |
| state | `state_goods_consumption`, `state_goods_production`, `state_goods_delta` |
| country | nothing — only a manual sum over states |

Hence a clean formula with no feedback from the market.

### About the flicker in the first month

`on_monthly_pulse_country` is not "once a month for everybody at once": the game spreads it across the days, recomputing roughly a thirtieth of all countries each day. On top of that E&F applies `no_money_production` from its own pulse. Values will jump around the vassals for the first month — that is normal, and the only cure is dropping modifiers in favour of buildings.

### Where the curve f comes from

The need is defined in `common/buy_packages/00_ef_buy_packages.txt` — E&F injects `popneed_currency` into all 99 wealth levels:

| wealth | 1 | 5 | 10 | 15 | 20 | 25 | 30 | 40 | 99 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| £ | 21 | 28 | 37 | 41 | 40 | 46 | 62 | 96 | 6177 |

The shape is lopsided: it climbs briskly up to level 10, sits on a shelf from 10 to 20, accelerates past 20 and goes exponential past 40. In `zz_ef_local_currency_values.txt` it is broken into segments (`zz_ef_lc_curve_a` … `_e`), each clamped to its own bounds and multiplied by its own slope. Agreement with the table: SoL 6.1 → 30.8 (table says 31), 11 → 37.3 (38), 30 → 62.0 (62), 40 → 96.0 (96).

### Calibration

In-game measurements, whole-country consumption:

| country | population | SoL | measured | formula | |
|---|---:|---:|---:|---:|---:|
| New Granada | 1.47M | 7.3 | 1640 | 634 | 39% |
| Circassia | 664k | ~11 | 372 | 327 | 88% |
| Bukhara | 1.47M | 6.1 | 380 | 597 | 157% |

Per capita they differ by a factor of four, and **neither population nor wealth explains it** — by the curve all three should consume almost the same. Something else does the work: pop composition, the price of the good at the moment of measurement, the dependant ratio. So `rate` is the geometric mean of the three fits — a compromise, not a fit to one country.

One knob, and it is linear: `zz_ef_local_currency_rate`, currently `0.0132`. It started at `0.013` plus 25% headroom (`0.01625` in total); after a test run the headroom was folded into the knob and the overall level cut by 19%. Turn it the same way from here: `0.0132` → `0.0099` is another quarter off everyone at once.

### Why the modifier is country-scoped

Applying it per state was tried and does not work, and this is worth remembering. **The `multiplier` in `add_modifier` is not evaluated in the scope the effect sits in.** Inside `every_scope_state` the triggers see the state fine, but the multiplier one line below does not:

```
Value of wrong type in 'zz_ef_local_currency_on_actions.txt:39'. Got value of type 'none'
```

`state_population` and `sg:local_currency` came back as zero, everything bottomed out on the lower bound, and states issued 10 units instead of thousands.

Note this is a limitation **on the modifier, not on reading data**: the per-state sum can be accumulated inside a country-scoped script value (see `country_total_urbanization` above) — it was dropped on meaning, not on technique.

Side effect of a country-scoped modifier: states of one country get equal shares, even though Circassia's two hold 590k and 74k people. The only cure is dropping modifiers in favour of buildings, which is what the local banks mod does.

### Mechanics

| file | what |
|---|---|
| `common/static_modifiers/zz_ef_no_money_production.txt` | `REPLACE:` — kills E&F's flat 2500 at the source |
| `common/static_modifiers/zz_ef_local_currency_fix.txt` | our grant modifier, base `+1` |
| `common/scripted_triggers/zz_ef_local_currency_triggers.txt` | who it applies to. **Currently everyone with `no_money_production`**; the market condition is commented out |
| `common/script_values/zz_ef_local_currency_values.txt` | the curve and the calculation. One knob — `rate` |
| `common/on_actions/zz_ef_local_currency_on_actions.txt` | monthly recalculation |
| block 4 in `zz_ef_currency_fix.txt` | the initial grant, so the first month is not spent without currency |

Also in `common/pop_needs/00_ef_pop_needs.txt` the weight of `local_currency` inside `popneed_currency` is lowered from `0.25` to `0.1`: a real currency should be more attractive than a generic local one. All 65 real currencies keep `0.25`.

**With the _ZZ EF Local Banks mod installed** it neuters our grant too (`TRY_REPLACE:zz_ef_local_currency_fix`) and prints currency from buildings instead. The hotfix does not depend on it and works fully without it.

---

## 6. Currency laws — a typo removed

All 95 laws in `common/laws/01_ef_currency_type.txt` required:

```
unlocking_technologies = {
    currency_standars
}
```

No technology by that name exists — the real one is `currency_standards`, with a `d`. One letter, 95 times, and the whole `lawgroup_currency_type` was unavailable to anyone, ever.

**It did not affect the intended path**: `introduction_of_<currency>` calls `activate_law` directly, which bypasses requirements. The typo only closed off manual selection by the player.

**It is worth fixing for one case** — a country formed mid-game. Germany inherits Prussia's central bank, Prussia researched `central_banking` long ago, so `on_researched` will never fire again, and GER could never get the mark: not by history (it has none), not by automation (already spent), not by law (the typo). An open law group is the only way out.

Since the laws can now be enacted by hand, a `possible` block was added. It is built from E&F's own data rather than invented:

| | count | rule |
|---|---:|---|
| law bound to tags | 53 | available to whoever E&F itself hands that currency to in history — including the HMM branch, so formable countries are covered |
| ownerless currency | 3 | available to everyone — Tunisian and Yugoslav dinar, South German gulden |
| good commented out | 39 | `always = no` — holding a law with no good is worse than having no currency: the bank mints nothing, the production methods point at nothing |

On top of that **every available law requires `has_modifier = has_central_bank`**. This is the important part: you cannot pick a currency before you have a central bank. Otherwise a Japan player would take the yen in 1836 and walk straight past the Meiji chain that gates it (see below).

The author never intended "one currency per country": there was no `possible` on any of the 95 laws, and he deliberately hands one currency to several tags (Canadian dollar — CAN, ONT, QUE; Prussian thaler — PRU and NGF; Bolivian peso — BOL and PBC).

### How the central bank is actually granted — and why we stay out of it

Worked out while debugging Japan; written down so nobody steps on it again.

The path to a central bank is not a journal entry but `on_researched` on the technologies:

```
banking            → add_technology_researched = currency_standards
currency_standards → activate_law = law_type:law_fiat_standard
central_banking    → currency_standards + metalique_standard
                   → introduction_new_currency = yes
```

`introduction_new_currency` (`09_introduction_building_lvl.txt:38456`) places a level 5 `building_bank` in the capital, applies `central_bank_modifier` and `central_bank_production_methods`, then calls 90+ `introduction_of_<currency>` effects, each handing its law to the right tag.

It is called under this condition:

```
or = {
	is_valid_country = yes
	AND = { var:gdp_view >= 1   NOT = { c:JAP ?= this } }
	AND = { is_player = yes     NOT = { c:JAP ?= this } }
}
```

So **any played country gets a central bank as soon as it researches `central_banking`** — except Japan, explicitly excluded from both open branches. Japan can only come in through `is_valid_country`, and there:

```
is_valid_country_JAP = {
	c:JAP ?= this
	or = {
		has_journal_entry = je_meiji_economy
		has_variable = japan_emperor_restored
		has_variable = japan_restoration_complete
	}
}
```

All three flags are alive in vanilla 1.13 (`00_meiji_restoration.txt:744`, plus the variable is used in achievements, `ai_strategies` and companies). **Japan is not broken — it is gated behind the Meiji Restoration, and that is intentional.**

The other countries "missing" from the main history list are gated the same way, to the historical dates their currencies were introduced — PHI 1851, CUB and CLM 1857, SAF 1860, ARG 1867, CHL 1881, SER 1884, EGY 1898, MOR 1906, KOR 1911.

What follows for the hotfix: **handing these countries banks and currencies at game start is not allowed** — that demolishes the design rather than fixing a bug. It was tried and reverted. `bank_je_central_1` is left alone too: it genuinely cannot complete (it requires an already standing bank while `on_complete` leads to the commented-out `bank_je_central_2`), but it is not the main path, and "fixing" it would open a way around Meiji.

---

## 7. Two script guards, moved here from the PSC compatch

These fix E&F on its own and have nothing to do with PSC, so they were moved out of the E&F + PSC compatch and into this mod. Both are key-level `REPLACE_OR_CREATE:` overrides — no E&F file is overwritten, so they cost nothing on the next E&F update beyond a re-check.

### `common/script_values/zz_ef_div0_fix.txt` — division by zero

E&F's five stock/bond demand values divide twice by numbers that are legitimately zero:

```
target_demand_<good>_ajusted = {
    value    = target_demand_<good>
    subtract = market.mg:<good>.market_goods_exports
    divide   = building_financial_num   # <-- 0 for anyone without a financial centre
    ...
}
target_demand_<good>_for_modifier = {
    value    = target_demand_<good>_ajusted
    subtract = base_demande_<good>_fix
    divide   = base_demande_<good>_fix  # <-- 0 until the first centre exists
    multiply = 100
}
```

The author knows about the first one — the comment on that very line in `00_financial_scripted_value.txt` reads `---------------> division par zero possible`. `building_financial_num` is a sum of ~90 `has_building_financial_centre_<tag>` flags, so it is 0 for most of the world in 1836. `base_demande_<good>_fix` just reads `var:base_demande_<good>_fix`, which is 0 until a centre is built.

The fix clamps the first divisor with `divide = { value = building_financial_num min = 1 }` and wraps the second in a `> 0` check so the block is skipped rather than divided. Note `min` on a `divide = { }` block clamps the **divisor**, not the result — with one or more centres the arithmetic is bit-identical to E&F's. Ten values patched: bond, manufacture, agricultural, mining and railroad stock, `_ajusted` and `_for_modifier` each.

### `common/scripted_effects/zz_ef_currency_scope_guard_fix.txt` — dereferencing a scope that may not exist

`sell_currency_privat_bank` builds a seller/buyer pair out of an ordered list and then does, unconditionally:

```
scope:seller.owner = { save_scope_as = seller_country }
```

If the list came back empty there is no `scope:seller`. The same holds for `scope:central_bank_site` in the two metal-transfer branches further down. The fix aborts cleanly on a missing seller and adds `exists = scope:central_bank_site` to those two limits. The arithmetic is untouched.

Verified still unguarded in E&F 04.07.2026 on 2026-08-19.

### `common/history/global/zz_ef_init_stockpiling_state_vars.txt` — ⚠ probably redundant, verify and delete

Additive `GLOBAL` block that fills in seven state variables (`stockpiling_{bond,manufacture_stock,agricultural_stock,mining_stock,railroad_stock}_var_state_1`, `financial_center_site_var`, `looted_state`) if they are missing. It was written against E&F v4.1.1 to stop startup spam of `Failed to fetch variable ... due to not being set` and `Invalid left side during comparison 'var'`.

Re-checked against E&F 04.07.2026 and it now looks unnecessary: `common/history/global/01_ef_state_global_variable.txt:1362-1389` already sets all seven inside `GLOBAL = { every_state = { ... } }`, which covers unowned states too, and a sweep of `common/` found no `stockpiling_*` variable that is read via `var:` but never set (552 read, 2303 set, 0 orphans).

It is kept for now only because the original log that showed the spam could not be re-read during this pass. **Start a game with this file disabled, grep `error.log` for those two lines, and if it is clean, delete the file.** Every write is guarded by `NOT = { has_variable = ... }`, so leaving it in cannot do harm in the meantime — it just runs a loop over every state at game start for nothing.

### `common/history/buildings/00_a_ef_history_var_init.txt` — the `country_already_financial_center` spam

```
Failed to fetch variable for 'country_already_financial_center' due to not being set
Invalid left side during comparison 'var'
  common/scripted_effects/09_introduction_building_lvl.txt:22681
  common/history/buildings/00_ef_building.txt:2999
```

`00_ef_building.txt:2999` calls `financial_center_modifier = yes` for the historic financial-centre countries. That effect reads exactly two variables — nothing else:

| where | read |
|---|---|
| `financial_center_modifier` line 43 | `add_modifier = { name = financial_center_place  multiplier = var:gdp_view_fc }` |
| `financial_center_modifier` line 22725 | `not = { var:country_already_financial_center = 1 }` |

Both are initialised in exactly one place at campaign start — `common/history/global/00_ef_economic_global_variable.txt`, line 628 (`= 0`) and line 784 (`= 5`), both under `GLOBAL -> every_country`. And `common/history/buildings/` is processed **before** `common/history/global/`, so when the effect runs neither variable exists.

Checked the rest of what `00_ef_building.txt` calls, and this is the only one affected: `establish_bank_and_ef_compagnie` (9658 lines), `initialize_historic_macro_facilities_bc`, `initialize_historic_macro_facilities_fc` and `is_valid_country_hmm` read no variables at all.

**This one is not just log noise.** The failing read on line 43 is a modifier multiplier — when it comes back `none` the `financial_center_place` modifier is applied with a broken scale, so the historic financial centres start the game mis-sized. The comparison at 22725 failing really is cosmetic: history/global resets that flag to 0 immediately afterwards regardless.

The fix is a separate additive `BUILDINGS` block. Files in the folder are processed in name order and `BUILDINGS` blocks stack, so `00_a_` lands ahead of `00_ef_building.txt` without overriding it. Both writes are guarded by `has_variable`, so if the author ever moves his init earlier this file quietly becomes a no-op. The values are his: 0 and 5.

Found while digging, **not fixed**: `00_ef_building.txt:117` calls `initialize_historic_macro_facilities_ns = { ... }`, whose only definition is commented out at `09_introduction_building_lvl.txt:23546` — the call resolves to nothing. Removing it would change what the campaign starts with, which is the author's call, not a hotfix's.

---

## 8. The leftover dev panel in the Economy tab

`common/scripted_guis/zz_ef_hide_debug_panel.txt` (new)

E&F ships its own debug UI: a small round **1** button under the budget tabs — widget
`Panel_1` in `gui/00_ef_deported_gui_1.gui`, sitting inside
`type budget_panel_economy_panel_content` — which opens
`gui/ef_dev_and_custom_windows/ef_custom_windows.gui`, a grid of unlabeled test buttons
(`PA PL L E I1 T 14 … 320`).

It is gated on the global variable `EF_debug_mode`, and `gui/01_ef_debug_widget.gui`
(registered through `gui/scripted_widgets/EF_scripted_widgets.txt`) does nothing but
mirror `[InDebugMode]` into that variable. So anyone launching with `-debug_mode` —
which is most people who want the console — gets a dev panel in the middle of the
budget screen.

It stayed invisible for a long time by accident: with E&F + TGR the Economy tab content
was never built at all, because the ComPatch's `budget_panel.gui` was a 1.12-era merge.
Once that was rebuilt on 21.08.2026 the tab started rendering — and brought the dev
panel with it.

```
REPLACE_OR_CREATE:EF_debug_mode_visibility = {
	is_shown = {
		always = no
	}
}
```

The button is hidden rather than the variable cleared: `EF_debug_mode` also gates E&F's
own debug decisions (`Open_Test_Decision` / `Close_Test_Decison` in
`common/decisions/00_ef_debug_decisions.txt`), which read it directly and are harmless
where they are. Removing the variable would be a wider change than this needs.

Comment the block out if you want the dev panel back.

---

## 9. Currencies merged into one good — and given back as prestige goods

This is the block that turned the hotfix from a patch into something bigger, and it
is the reason E&F can now share a build with Tech & Res at all.

### The arithmetic

Vanilla 53, PSC 4, E&F with this hotfix 65, Morgenröte 5, Tech & Res 35 — **162**
against a ceiling of 128. 57 of E&F's 65 goods are currencies, one per monetary
system law.

Collapsing 56 of them into `spe_uni_c` takes the pack to **106**, with 22 slots to
spare and Tech & Res whole — no cutting eras, data goods or androids.

Nothing about the monetary system is removed. All 95 currency laws stay, every
country keeps its own law and its own `pm_currency_*`, the bank still mints, the
buildings still pay for liquidity. Only the good on the belt is shared.

### Why it was safe to do

E&F's exchange rates, money supply, gold and silver standard, stockpiles, imports
and exports run on country and global **variables**, not on the market data of the
currency goods. Of the 36 script-value families E&F defines per currency, 14 are
referenced nowhere at all — including every one that reads
`market.mg:<X>_c.market_goods_*`.

The one live consumer of a currency good's market data was the money-issuance
controller:

```
target_demand_currency              = market.mg:<own currency>.market_goods_buy_orders
target_demand_currency_for_modifier = (target − current output) / current * 100
currency_demande on the bank        = goods_output_<cur>_mult 0.01 * that
```

The bank drives its output until it equals market demand for its currency. That was
self-limiting while every country had its own good — "demand for the pound" was,
near enough, Britain's demand. With one shared good it became the whole market's
demand and every bank chased all of it: six banks on the British market issued
~196K each against ~192K of buy orders, price −99%. Rewritten to split the market's
demand between its issuers by GDP — one field that tracks both halves of the demand,
pops through `popneed_currency` and buildings through `pmg_market_liquidity`.

### The currencies came back as prestige goods

Prestige goods do not count against the 128 — measured with a hundred dummies on one
base good, not assumed. So all 95 currencies return as prestige variants of the
shared good, with their own names, their own icons, a prestige bonus and the
engine's +20% throughput for buildings that consume them.

**The prestige good reuses the old good's key** (`pound_sterling_c`). It stopped
being a good when the merge commented it out, so the name was free — and every
piece of localisation E&F ships for it, in eleven languages, plus the separate
Russian translation mod, keeps working untouched. Zero translation work.

**Which one a company produces is decided by the currency law, not by the company.**
Company → country is not in the files: 6 of E&F's 103 companies name a tag, the rest
go by interest markers. So every bank company is offered all 95 and each prestige
good carries `possible = { has_law = law_type:law_<cur>_currency }`.

### The central bank is now a private business

A company can only produce a prestige good from a building it owns, so three things
had to change on `building_bank`, and each was found the hard way:

| what | why |
|---|---|
| `ownership_type = no_ownership` → `self` | no ownership shares meant nothing to hold. Not enough on its own |
| `bg_bank: is_government_funded = yes` → `no` | a government-funded building is state-run and has no owners at all. This is the one that mattered |
| `ai_nationalization_desire = 0` → `-5` | 0 is exactly the engine's privatise threshold; a company can only hold privatised levels |

**This is a design decision, not a fix.** A private central bank pays its dividends
to its owners instead of the treasury — about 6K a month on a 1836 British save —
and the treasury no longer pays for its gold and paper either. If that is not
wanted, run the generator without `--private-bank` and drop the prestige currencies;
the goods ceiling is closed either way.

### The company that owns it always exists

Every country with a central bank gets a bank company, keeps it, and does not pay a
company slot for it:

* **spawned** monthly and once at game start — a country that owns a central bank
  and holds no bank company is given `company_BasicBank`;
* **free** — a country modifier with `country_max_companies_add = 1` while the
  central bank stands. E&F's own +1 sat inside `prosperity_modifier`, so it only
  ever reached a prosperous generic company;
* **undeletable** — no such flag exists in the engine, so it is imitated: delete it
  and the monthly pass puts it back;
* **replaced by the flavoured one** where E&F has it. It cannot be picked for the
  country, so the generic one is granted and withdraws itself the moment any of
  E&F's 96 flavoured bank companies appears.

### A rule worth writing down

`REPLACE:key = { ... }` is a **complete definition of the entry. Everything not
listed disappears.** The difference from `INJECT:` is not "list versus block", it is
"replace everything versus append".

Proved twice, both times by breakage: `REPLACE:building_bank = { ownership_type =
self }` made the central bank vanish from the game, and 285 production methods
restated with only `building_modifiers` lost their `unlocking_laws` — the central
bank started offering all 95 currencies in a dropdown meant to show one.

So everything here that changes one field in an E&F entry restates the whole entry,
taken from E&F by the generator rather than copied by hand.


## Left undone

- 34 orphaned modifier type sets (from the cut goods) — the 140 `defined in script but not in code` warnings.
- The Tunisian and Yugoslav dinars are left in: tags `c:TUN` and `c:YUG` stand behind them, and if a player forms those countries they land in the same state block 2 fixes.
- `bank_je_central_1` cannot complete (see section 6). A bug report for the E&F author, not something to patch here.

All of this is worth sending to the E&F author — it is far cheaper to fix on his side.

---

## ⚠️ Maintenance

The mod overrides four E&F files (`ef_00_goods.txt`, `00_ef_building.txt`, `00_ef_alert_types.txt`, `01_ef_currency_type.txt`) plus `00_ef_pop_needs.txt` and six vanilla `.gui` files. Which means:

- **after every E&F update** the edits have to be re-applied, otherwise the hotfix rolls his changes back;
- **after every game patch** the `.gui` files have to be re-copied from the new vanilla.

The three files in section 7 override **keys**, not files (`REPLACE_OR_CREATE:`), so an E&F update cannot silently roll them back — but it can make them obsolete. Re-check with:

```bash
cd C:/Users/Andrey/Projects/vic3_mods_out

# is the div/0 still there? (the author's own comment marks it)
grep -n -A3 'target_demand_bond_ajusted' "E&F/common/script_values/00_financial_scripted_value.txt"

# is the seller scope still dereferenced unguarded?
grep -n -A2 'scope:seller.owner' "E&F/common/scripted_effects/01_economic_scripted_effects.txt"

# does E&F still init the stockpile state vars itself? (if yes, drop 7c)
grep -n -B2 'stockpiling_bond_var_state_1' "E&F/common/history/global/01_ef_state_global_variable.txt"
```

```bash
cd C:/Users/Andrey/Projects/vic3_mods_out

# did the goods source change?
diff "E&F/common/goods/ef_00_goods.txt" \
     "../vic3_mods/_ef/ef hotfix 1.13/common/goods/ef_00_goods.txt"

# are both history bugs still alive?
grep -n 'STATE_ANDALUSIA' "E&F/common/history/buildings/00_ef_building.txt"
grep -n -A3 '#GRE'        "E&F/common/history/buildings/00_ef_building.txt"

# is the typo still there? (if not, the laws override can be dropped)
grep -c 'currency_standars' "E&F/common/laws/01_ef_currency_type.txt"

# has the goods count crept up? (must stay <= 128 with every mod loaded)
# is the dev panel still gated on EF_debug_mode? (if the key is renamed, block 8 silently creates a dead entry)
```

---

### Блоки 9 — генерируются целиком

```
python3 tools/regen_ef_currency_merge.py --private-bank --check   # разъехалось ли
python3 tools/regen_ef_currency_merge.py --private-bank           # пересобрать
```

Гонять после каждого обновления E&F. Рукописные оригиналы двух перекрываемых файлов
лежат в `_gen_source/` — игра эту папку не читает, и править надо именно их:
`common/goods/ef_00_goods.txt` и `common/pop_needs/00_ef_pop_needs.txt` в моде это
выход генератора, он их перезаписывает.

Без `--private-bank` центробанк остаётся казённым, а престижные валюты не работают
(компания не может владеть казённым зданием). Лимит товаров при этом всё равно закрыт.

Генератор после каждой сборки прогоняет самопроверку: имена под-блоков на верхнем
уровне, дубли ключей, баланс скобок с учётом комментариев, совпадение прочитанного и
записанного ключа. Две ошибки, каждая из которых роняла игру до меню, ловятся именно ей.

## For Steam

Short description in Steam BBCode — paste as is into the workshop page.

```
[h1]E&F Hotfix [1.13][/h1]
Fixes for [b]Economic and Financial[/b] (repo version 04.07.2026) on Victoria 3 [b]1.13.10[/b].
Load [b]after E&F[/b]. Independent of the [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637341756]E&F + Morgenröte ComPatch[/url] — works with or without it.

[h2]Load order[/h2]
[list]
[*]Community Mod Framework (CMF)
[*]Expanded Topbar Framework (or Dence UI)
[*]Economic and Financial (E&F)
[*][b]E&F Hotfix (this mod)[/b]
[/list]

[h2]What it fixes[/h2]
[list]
[*][b]The 128 goods limit — the reason E&F + any goods mod crashes[/b]
[list]
[*]Vic3 1.13 crashes on entering a game above 128 goods, with nothing in the log. E&F alone brings 126, so two free slots
[*]Eight dead currencies are commented out — ones with no country behind them, or duplicates. Down to [b]118[/b], which leaves room for Morgenröte (123) and PSC (127)
[/list]

[*][b]The crash when the world map appears[/b]
[list]
[*]Six vanilla GUI files E&F still ships in their 1.12 form are restored to 1.13.10, keeping the [i]@money![/i] → currency symbol substitution
[*][i]map_markers.gui[/i] was missing [i]enemy_naval_mission_marker[/i] — the engine looks that widget up by name and crashes when it is gone
[*]Also restored: [i]custom_tooltip[/i], [i]military_formation_panel[/i], [i]popups[/i], [i]right_click_menu[/i], [i]frontend/shared/lists[/i]
[/list]

[*][b]~70,000 script errors per session[/b]
[list]
[*]31 of 32 E&F alerts read variables that are never initialised — the national stockpile they belong to ships inside a .zip the game does not read
[*]Every alert now checks [i]has_variable[/i] first. No data, no evaluation, no log spam
[*]Two bond alerts ran with [i]script_context = player_market[/i] while reading country variables — markets have no variables in Vic3, so those two could never work. Fixed to [i]player_country[/i]
[/list]

[*][b]History bugs[/b]
[list]
[*]Spain got no starting silver mine: E&F points at [i]STATE_ANDALUSIA[/i], which 1.13 split into Lower and Upper
[*]Greece got gold and silver mines in Saxony and Brandenburg — a copy-paste of the Prussian block, running in a NULL state
[*]Württemberg got no currency at all: its law is spelled [i]gulde[/i] without the n
[*]Thirteen countries held a named currency law whose good does not exist — worse than having no currency. Moved to [i]law_no_market_liquidity[/i]
[/list]

[*][b]Local currency flooding every market[/b]
[list]
[*]E&F handed countries without a monetary system a flat 2500 local currency [b]per state[/b], regardless of size. ~600 of 724 countries qualify, and their cheap currency crowded real national currencies out of [i]popneed_currency[/i]
[*]Replaced with an amount computed from population and standard of living, using E&F's own [i]buy_packages[/i] table as the curve
[/list]

[*][b]Three script guards[/b]
[list]
[*]E&F's stock and bond demand values divide by [i]building_financial_num[/i], which is zero for any country without a financial centre — the author's own comment on that line says "division par zero possible"
[*][i]sell_currency_privat_bank[/i] dereferences a seller scope that may not exist when the source list comes back empty
[*]The historic financial centres are set up from [i]history/buildings[/i], which runs before [i]history/global[/i] — so the two variables that setup reads do not exist yet. Besides the log spam, one of them is a modifier multiplier, so those centres started the game mis-sized
[/list]

[*][b]Currency laws were unavailable to everyone[/b]
[list]
[*]All 95 laws required a technology named [i]currency_standars[/i] — the real one has a d. One letter, 95 times, and the whole law group could never be enacted
[*]Fixed, with a restriction: a law is available only to the tags E&F itself assigns it to, and only once you actually have a central bank
[/list]

[*][b]E&F's dev panel showing up in the budget screen[/b]
[list]
[*]The round [b]1[/b] button under the budget tabs opens E&F's grid of unlabeled test buttons. It is tied to [i]-debug_mode[/i], so anyone playing with the console open sees it
[*]Hidden. Comment out [i]common/scripted_guis/zz_ef_hide_debug_panel.txt[/i] if you want it back
[/list]
[/list]

[h2]Currencies are one good now[/h2]
E&F ships one market good per currency — 57 of them — against a hard ceiling of 128 for the whole game. That is what kept it out of any build with another large mod. They are merged into a single good, which takes a full megapack from 162 goods to 106 and lets Tech & Res run alongside E&F untouched.
Nothing is lost: every country keeps its own currency law, its own mint and its own exchange rate. The currencies come back as [b]prestige goods[/b] with their own names and icons, produced by the central bank's company — which means the central bank is now privately owned and pays dividends rather than being a line in the state budget.

[h2]Not fixed[/h2]
[list]
[*][i]budget_panel.gui[/i] and [i]construction_panel.gui[/i] are equally out of date but hold real E&F reworks — they need a manual merge, not a vanilla swap. Expect trouble at bankruptcy and in the ship construction queue
[/list]

[i]Overrides five E&F files and six vanilla .gui files, so it has to be rebuilt after every E&F update and every game patch.[/i]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
```
