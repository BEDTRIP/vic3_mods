# ComPatch: Grey's + HC+GoB+MoH

<!-- meta
пара: Grey's × HC+GoB+MoH (GR.4)
статус: done
версии: Game 1.13 (exe 1.13.11) — Hail, Columbia! 8.6-Roosevelt, Gates of the Bosphorus (declares no version), Mandate of Heaven (declares no version), Grey's pack (declares no versions).
позиция: после всей пачки Grey's
файлов: 7
генератор: tools/regen_greys_hc.py
зависит от: —
-->

## Для мастерской

[h1]ComPatch: Grey's + HC+GoB+MoH[/h1]
[b]Game 1.13 (exe 1.13.11) — Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven, Grey's pack.[/b]

The Grey's pack REPLACEs eleven vanilla records that Hail Columbia, Gates of the Bosphorus or Mandate of Heaven also touch, and ships a file at the same relative path as Gates of the Bosphorus. Most seriously, Grey's own defensive fallback for a CMF mod-detection flag switches Hail Columbia off entirely, silently. This patch restores every layer that gets dropped.

[h2]Load order[/h2]
[list]
[*]…Hail Columbia → Gates of the Bosphorus → Mandate of Heaven…
[*]…addon-HC…
[*]Grey's pack (soft_econ, soft_pop, USU, cinosphere, food, ranch, …)
[*][b]this ComPatch[/b]
[/list]

---

**Game 1.13 (exe 1.13.11). Hail, Columbia! 8.6-Roosevelt; Gates of the Bosphorus and Mandate of Heaven (declare no versions); Grey's pack (declares no versions).**

Pair GR.4 — 11 shared keys plus one shared file path.

## 1. `is_usfp_active` — critical, three lines, switches off the whole mod

`_grey_soft_pop` ships `REPLACE_OR_CREATE:is_usfp_active = { always = no }` as a defensive fallback "in case Hail Columbia isn't installed" — a `com_law_compat`-style guess at load order, not a check of it. Grey's loads after the whole HC+GoB+MoH block, so this wins outright over Hail Columbia's own `always = yes`, and **every `is_usfp_active = yes` gate inside Hail Columbia goes false**, with nothing in error.log. `common/scripted_triggers/zz_greys_hc_is_usfp_active.txt` re-issues `always = yes`, loaded after the whole Grey's pack.

## 2. Five cultures — `han`, `hakka`, `manchu`, `min`, `yue`

`grey_deeper_cinosphere` TRY_REPLACEs (REPLACEs for `manchu`) all five cultures with full bodies. Mandate of Heaven also touches all five — INJECT for four, REPLACE for `manchu` — adding its own names to the same name-pool sub-blocks cinosphere restates (`male_common_first_names`, `female_common_first_names`, `common_last_names`; `noble_last_names` for `manchu`). A full body wins over the earlier INJECT, so MoH's additions are gone.

`common/cultures/zz_greys_hc_cultures.txt` rebuilds all five: cinosphere's body as the base (it is the richer redesign for four of the five, and for `manchu` both sides moved the same direction — authentic Manchu clan surnames over generic Han names — with cinosphere's EANI-sourced set far larger), MoH's name-pool tokens unioned in wherever cinosphere's list doesn't already carry them (exact-string dedup; both sides' custom tokens have working localization, checked against `EANI_names_l_english.yml` and `moh_names_l_english.yml`), and `noble_last_names` — a sub-block cinosphere never names for any of the five — carried forward from MoH as-is.

Separately, and checked as part of this pair rather than left to GR.12: cinosphere's body is a stale copy that predates 1.13's `seal_and_signature_texture` field, for all five cultures. Restored from vanilla in every case.

| culture | MoH names unioned in | notes |
| --- | --- | --- |
| `han` | 346 first (male) + 15 first (female) + 53 last | `noble_last_names` (90 names) carried from MoH |
| `hakka` | same 346/15/53 (MoH injects an identical pool into all three Han-descended cultures) | `noble_last_names` (90 names) carried from MoH |
| `yue` | same 346/15/53 | `noble_last_names` (90 names) carried from MoH |
| `min` | same 346/15/53 | `noble_last_names` (90 names) carried from MoH |
| `manchu` | 275 first (male) + 2 first (female) + 27 last, plus `obsessions` — MoH's `porcelain` unioned into cinosphere's `tea` | `noble_last_names` (6 names) carried from MoH; cinosphere's own `male_regal_first_names`/`regal_last_names` (imperial-clan-only fields, not in vanilla or MoH) kept as-is |

## 3. `decree_greener_grass_campaign`

Both Hail Columbia and `_grey_soft_pop` REPLACE this vanilla decree with full bodies. HC's only change from vanilla is a `NOR` gate added to `state_trigger`, against stacking Greener Grass with HC's own Homestead Act / Gold Rush decrees; `_grey_soft_pop`'s is an unrelated rebalance (migration-pull numbers, three `ai_weight` branches removed, one added) that never touches `state_trigger` — its copy is verbatim vanilla. Grey's loads later, so its full body wins and HC's gate disappears silently.

`common/decrees/zz_greys_hc_greener_grass.txt` is soft_pop's body with HC's `state_trigger` merged in. soft_pop's own rebalance and ai_weight redesign are untouched.

## 4. `common/history/countries/mon - montenegro.txt` — a shared file path, not a by-key conflict

`grey_usu` and Gates of the Bosphorus both ship a file at this exact relative path. Neither is `REPLACE:`-prefixed — this is a raw virtual-filesystem path collision, and the game reads only the later mod's copy; the earlier one isn't merged, it's invisible. `grey_usu` (Grey's block) loads after the whole HC+GoB+MoH block, so its 94-line body (vanilla is 93) wins outright, and GoB's 102-line body — three new starting techs, a new journal entry (`je_balkfm_mon_prince_bishopric`), GoB's own IP3 state-formation integration, and an else-branch event (`balkfm_montenegro.001`/`.019`) — never runs at all.

`common/history/countries/mon - montenegro.txt` (perekрытие by path, same relative path as both sources) is GoB's body — the substantial, deliberate rework — with USU's own two changes layered on top: the first Trade Center import-tariff good redirected from `g:merchant_marine` to USU's own `g:usu_logistics` (Montenegro is landlocked, per USU's own comment), and `set_military_wage_level = low` added.

## 5. `pm_religious_bureaucrats`

`grey_usu`'s `REPLACE_OR_CREATE` halves clergy/bureaucrat employment (250 → 125) and restates `disallowing_laws` verbatim from vanilla's two laws. Hail Columbia's `INJECT` adds a third, `law_usfp_nominal_separation` — dropped when USU's full body wins.

`common/production_methods/zz_greys_hc_religious_bureaucrats.txt` is USU's body with HC's third law added back into `disallowing_laws`.

## 6. `state_trait_columbia_river`

`grey_usu`'s `TRY_REPLACE` restates the `modifier` block; Hail Columbia's `INJECT` adds `building_group_bg_logging_throughput_add = 0.30` to the same block and loads earlier, so it's dropped.

`common/state_traits/zz_greys_hc_state_traits.txt` is USU's body with HC's modifier field added back — the HC-only version of this record.

**This same record already carries VC's layer for GR.1**, in `_greys/greys+vc done/common/state_traits/zz_gvc_state_traits.txt`. That file does not (yet) carry HC's layer, and this file does not carry VC's. Per decision №11, HC+GoB+MoH and VC are alternative branches for the standard setup, so each file is correct on its own branch. The "both together" branch ("for madmen") is not covered by either file alone — defining the fully merged record in both loaded compachs at once would just recreate the same last-write-wins conflict this fix exists to close. Left as a follow-up in the plan, not solved here.

## 7. `NAI` — checked, not a conflict

`_grey_soft_econ` (5 keys, all `TRADE_CENTER_MINIMUM_GDP_*`), `grey_usu` (5 keys, `SUBSIDIZE_SHARE_OF_INFRA_FACTOR` and four `OWNER_BUILDING_LOCATION_*`) and Hail Columbia (`NUM_GROWING_COLONIES_MAX`, one key) all define `NAI`, and `pair_matrix.py` flags the block as shared — but defines merge per key, not per block (`Правила работы с модами Victoria 3`, section 1), and all eleven keys across the three mods are disjoint. No file.

## 8. `law_ethnostate`

`_grey_soft_pop`'s `TRY_REPLACE` (progressiveness −100, a CMF `is_visible` gate, its own `acceptance_modifier` rebalance) never names `on_activate`. Hail Columbia's `INJECT:on_activate` switches the USA's primary culture from `cu:afro_american` to `cu:dixie` on enactment — under a strict "REPLACE only patches named sub-blocks" reading this already survives untouched, but that reading is still an open question (`Правила работы с модами Victoria 3`, section 1), so `common/laws/zz_greys_hc_ethnostate.txt` carries it explicitly: soft_pop's full body with HC's `on_activate` inserted. Correct either way.

## Maintenance

`tools/regen_greys_hc.py`; `--check` reports drift without writing. Every merge asserts the specific text it depends on is still there before touching it — a changed HC anchor line, a Grey's author fixing GR.12's stale culture bodies, or a renamed USU good all fail the run with a message instead of silently writing a stale or wrong file. Re-run after any Hail Columbia, Gates of the Bosphorus, Mandate of Heaven or Grey's update.
