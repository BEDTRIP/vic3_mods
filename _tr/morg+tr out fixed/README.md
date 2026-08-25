# Morgenröte + Tech & Res — compatch

**Load order: Morgenröte → Tech & Res → this patch.** All three are required.

Verified 2026-08-21 against Morgenröte `2.8.3e Mitsopoulos`, Tech & Res `1.6'`
(commit *Tech Res 13.05.2026*), Kuromi's AI `7.5`, game `1.13.10`.

Kuromi's AI needs no patching — it shares no key, no localisation key, no event
id and no file path with Morgenröte.

---

## Why the load order is not optional

Both mods define the `technres_is_active` trigger: Morgenröte sets it to
`always = no` in `00_mr_compatibility_triggers.txt` (a stub, so its own scripts
do not spam the error log when Tech & Res is absent), Tech & Res sets it to
`always = yes` in `ztr_compatibility_triggers.txt`. Whichever loads last wins.

If Tech & Res loads *before* Morgenröte the trigger ends up `no`, and the
`potential = { technres_is_active = no }` branch in Morgenröte's
`mr_elgar_company_types.txt` stops suppressing its own Steinway company — you
get Morgenröte's and Tech & Res's version of it side by side.

The dependencies are declared in `.metadata/metadata.json` so the launcher
sorts this correctly on its own.

---

## What Tech & Res already handles

Most of it. Tech & Res ships a full Morgenröte compatibility layer of its own —
20 files under `ztr_mr_*` and `ztr_modified_mr_*` covering Morgenröte's
buildings, production methods, PM groups, goods, pop needs, state traits and
technologies. This patch only covers what that layer cannot express, plus the
places where it had to drop Morgenröte content in order to stay loadable
standalone.

That is why the patch is small, and why it got much smaller on 2026-08-21:
Morgenröte 2.8.3e rewrote two mechanics from "check this exact building type"
to "check this property", and Tech & Res buildings now satisfy them by
themselves. See `отчёт_morg+tr+kai_сверка_2026-08-21.md` for the full audit and
the in-game checklist.

---

## What the patch actually does

### Aviation — the main one

Morgenröte adds the `air_travel` good and builds pop needs, a prestige good and
the whole Curtiss airline branch on top of it. Only the airport produces it.
Tech & Res cannot ship that standalone, so it re-points every airport route PM
at `goods_output_transportation_add`, and since it loads later, with both mods
on the airport produces **zero** `air_travel` and everything above quietly
dies — with no error in the log.

`common/production_methods/` restores the `air_travel` output on the four route
PMs and on `pm_air_passenger_only`, following the instruction the Tech & Res
author left in their own file next to each one:

> `# Morgenrote compatch basta sostituire l'output con`
> `# goods_output_air_travel_add = 12`

Substitution, not addition — Morgenröte's airports also output `air_travel`
only. **Balance note:** in Tech & Res alone the airport is the single biggest
transportation source in the game (120 per level at the top tier, above
high-speed rail). This patch removes that. If late-game transportation goes
short, put a partial `goods_output_transportation_add` back — do not cut
`air_travel`.

Tech & Res also moves aeroplane production out of `building_automotive_industry`
into its own `building_aircraft_industry`. Morgenröte still hardcodes the old
building in three events, one decision and one script value, so those are
re-stated with the new building type:
`common/decisions/`, `common/script_values/`, `events/sports/`.

`common/company_types/` puts `prestige_good_generic_flights` back on the six
Curtiss airline companies — Tech & Res ships that block commented out, so
`je_mr_prestige_goods_flights` could never appear.

`common/pop_needs/` injects `air_travel` back into `popneed_entertainment` and
`popneed_leisure`, which Tech & Res replaces wholesale.
`popneed_free_movement` needs nothing — both mods only inject there.

### Publishing industry

Tech & Res rebuilds `building_manzoni_publishing_industry` with its own media PM
groups and drops Morgenröte's `manzoni_pmg_publisher` / `manzoni_pmg_newspaper`;
its version of the automation group also drops the `manzoni_pm_cylinder_presses`
tier. Both are restored in `common/buildings/` and
`common/production_method_groups/`, merged with the Tech & Res additions rather
than replacing them.

### Technologies

Tech & Res has to strip Morgenröte-only modifier types from shared technologies,
or they would error out standalone. With Morgenröte present those mechanics are
alive, so `common/technology/technologies/` puts back:

* the Elgar/Klimt decorative tradition counters on `romanticism`,
  `elgar_classicism_tech`, `elgar_irrationalism_tech`;
* smallpox mitigation on `panum_vaccination_tech` and yellow-fever mitigation on
  `malaria_prevention` (Tech & Res commented both out by name);
* `elgar_modern_art_tech` as a non-researchable gate plus the matching
  `elgar_mass_culture_tech` prerequisites — Tech & Res makes the gate
  researchable, which lets all three modern-art branches be taken at once;
* `verrier_nuclear_physics_tech` back onto Morgenröte's
  `verrier_radioactivity_tech` chain.

`vikelas_international_sports_tech` is a real three-way collision — both mods
define it plainly. Resolved as Morgenröte's placement (era 4, `organized_sports`
only, full AI weighting so France and Greece chase the 1896 Games) with Tech &
Res's modifiers, since Morgenröte ships an empty modifier block there.

Tech & Res keeps its own redaction of `dubois_nature_protection_tech`,
`malaria_prevention`'s colonial branch, `pharmaceuticals` and the whole
`ztr_mr_military` / `ztr_mr_production` sets.

### Mobilization

Morgenröte's three Gaudi advanced-tank options only accept the vanilla armour
line, so an army upgraded to Tech & Res units stops qualifying.
`common/mobilization_options/` re-states them with the six Tech & Res successor
unit types added.

### Vanilla trigger

`goods_is_industrial` is replaced by both mods and cannot be injected into.
`common/scripted_triggers/` carries Tech & Res's current list plus `air_travel`.

---

## Known limits

* `popneed_leisure` keeps Tech & Res's `civil_planes` entry alongside
  `air_travel`. Removing it would require replacing the whole need and
  rebuilding it by hand every Tech & Res update.
* `pm_travel_agencies` unlocks from Morgenröte's `curtiss_tourism_tech` (era 2),
  which is early inside Tech & Res's much longer tree. Left as the mod author
  wrote it.
* Group weights in the mobilization window are each mod's own; this patch does
  not reorder them.

---

## For Steam

[h2]Morgenröte + Tech & Res — Compatch[/h2]

[b]Load order: Morgenröte → Tech & Res → this patch.[/b] All three required.
Kuromi's AI needs no patch.

Tech & Res already ships a large Morgenröte compatibility layer. This patch only
covers what that layer cannot do on its own:

[list]
    [*][b]Airports produce air travel again.[/b] Tech & Res re-points every airport route to generic transportation because it cannot depend on Morgenröte's [i]air travel[/i] good. With both mods on, that silently killed Morgenröte's pop needs, prestige flights and airline journal entries. Restored following the Tech & Res author's own instructions.
    [*][b]Curtiss aviation content works with the new aircraft industry.[/b] Tech & Res moved aeroplane production out of the automotive industry; three events, one decision and one score still looked for it there.
    [*][b]Prestige flights are obtainable.[/b] The six Curtiss airline companies can produce the prestige good again.
    [*][b]Publishing industry keeps both mods' methods[/b] — Morgenröte's publisher, newspaper and cylinder press tiers alongside the Tech & Res broadcast and digital lines.
    [*][b]Morgenröte's technology mechanics stay alive[/b] — Elgar/Klimt traditions, smallpox and yellow fever mitigation, and the modern-art gate that keeps the three art branches exclusive.
    [*][b]Gaudi's advanced tank options accept Tech & Res armour[/b], instead of greying out once you upgrade past vanilla tanks.
[/list]

[b]Balance note:[/b] in Tech & Res alone the airport is the game's biggest transportation source. Once air travel is restored it stops being that, exactly as in Morgenröte. If late-game transportation runs short, that is why.

[b]Not included on purpose:[/b] this patch does not rebalance either mod. Where the two authors simply disagree on numbers, Tech & Res wins.
