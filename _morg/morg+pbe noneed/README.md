# Morgenröte + Power Blocs Expanded — NO COMPATCH NEEDED

<!-- meta
пара: Morgenröte × PBE
статус: noneed
версии: —
позиция: —
файлов: 1
генератор: —
зависит от: —
-->

**Status:** `noneed` — verified 2026-08-21 against
Morgenröte `2.8.3e Mitsopoulos` (game 1.13.*) and
Power Blocs Expanded `[1.13]` (Steam id 3623185901).

This folder ships **no content**. It exists only as a record of the check,
so the same pair is not re-analysed from scratch in six months.
See `conflicts_mr_vs_pbe_report.md` for the full evidence.

## Why no patch

The two mods do not touch the same ground at all:

* PBE has no `common/buildings`, `common/building_groups`, `common/goods`,
  `common/laws`, `common/law_groups`, `common/technology`, `interface/`.
  Morgenröte's entire footprint (62 buildings, 264 PMs, 89 techs, 5 goods)
  therefore cannot collide with it.
* Zero overlapping file paths (except `thumbnail.png`, cosmetic).
* Zero overlapping localization keys, zero overlapping event ids.
* Zero overlapping `common/*` keys except the two root on_action hooks below.
* Goods total 53 vanilla + 5 Morgenröte + 0 PBE = **58**, far under the 128 cap.
* No shared `.gui` file, and Morgenröte never references a power-bloc widget,
  so PBE's full overwrite of `power_bloc_panel.gui` /
  `power_bloc_formation_panel.gui` is invisible to Morgenröte.
* Morgenröte only *reads* power-bloc state via vanilla triggers
  (`is_in_same_power_bloc`, `num_power_bloc_members`, `any_power_bloc_member`)
  and never defines a principle, identity or cohesion level — exactly the
  things PBE replaces.

## The on_actions "conflict" is not one

Both mods define `on_monthly_pulse` and `on_monthly_pulse_country`.
`common/on_actions/` is **additive** in 1.13: root hooks declared in different
files are merged, not overwritten.

Proof from Morgenröte itself: it declares `on_yearly_pulse_country` in **19**
of its own on_actions files and `on_monthly_pulse_country` in **6**.
If the engine kept only the last declaration, 18 of Morgenröte's 19 content
branches would silently never fire and the mod would be visibly broken.
It is not — so cross-mod merging works the same way.

## Removed 2026-08-21: `common/on_actions/zz_morgenrote_pbe_on_actions.txt`

An earlier version of this folder shipped a "merged" on_actions file built on
the wrong assumption that the last mod wins. It had become actively harmful:

1. It redeclared both root hooks with an explicit list, which *would* have
   dropped every other mod's entry had the engine behaved as assumed — and,
   loaded last, it added its own list on top of two already-correct ones,
   double-firing PBE's handlers.
2. It referenced `kates_weekly_global_on_action` and
   `kates_dynamic_modifier_on_action`. PBE renamed its whole prefix
   `kates_` → `vokaes_`. Those names now resolve to nothing — silently, with
   no error in `error.log`, because an unknown on_action entry is skipped.
3. Its source comment pointed at `Morgenrote/morgen/common/on_actions/...`,
   a path that no longer exists (Morgenröte moved `common/` to the mod root).

The file was moved to `vic3_mods/_to_delete/morg+pbe_2026-08-21/`.

## Do not re-check

* on_actions pulse overlap — additive, settled (see above).
* PBE building / PM interaction — PBE's `pmg_entrenched_building_manor_house`
  and `pmg_sovereign_wealth_fund_company_headquarter` are dead code in 1.13:
  defined, never injected into any building. Nothing for Morgenröte to collide with.
* Goods cap — 58 with both mods.

## Re-check only if

* PBE re-adds `common/buildings/` or `common/building_groups/`
  (it had them under 1.12; they are gone in the 1.13 build).
* PBE starts overriding vanilla `modifier_type_definitions` that Morgenröte
  also defines — today PBE overrides 7 and Morgenröte overlaps with none.
* Morgenröte adds power-bloc content (principles, identities, cohesion levels)
  or its own `common/defines`.
