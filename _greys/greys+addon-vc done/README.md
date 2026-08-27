# ComPatch: Grey's + addon-VC

<!-- meta
пара: Grey's × сборка «аддон-VC»
статус: done
версии: Game 1.13 (exe 1.13.11) — Addon: VC x MegaComPatch, Grey's pack (версии моды не объявляют).
позиция: после всей пачки Grey's
файлов: 1
генератор: tools/regen_greys_addonvc.py
зависит от: —
-->

## Для мастерской

[h1]ComPatch: Grey's + addon-VC[/h1]
[b]Game 1.13 (exe 1.13.11) — Addon: VC x MegaComPatch, Grey's pack.[/b]

grey_usu's own redesign of `popneed_leisure` carries an `air_travel` entry commented out, with a note that Morgenroete's own contribution should still apply — it doesn't, because grey_usu's `REPLACE:` wipes it, and the author's own follow-up fix only restores a different good. This patch closes the gap the author left.

[h2]Load order[/h2]
[list]
[*]…[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3790297983]Addon: VC x MegaComPatch[/url]…
[*]Grey's pack (soft_econ, soft_pop, USU, food, ranch, …)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3791186618]Addon: Grey's x MegaComPatch[/url]
[*][b]this ComPatch[/b]
[/list]

---

## Подробности

**Game 1.13 (exe 1.13.11). Addon: VC x MegaComPatch; Grey's pack (declares no versions).**

Pair GR.18. Not the same pair as GR.1 (`_greys/greys+vc done`, 129 keys against raw Victorian Century) — addon-VC is a *build*, VC merged with its own TGR- and Morgenroete-compat layers, and it carries content raw VC alone does not. `content_holes.py --only builds` is what catches this class of gap (the same reason GR.17 exists for the megapack): it reports 8 keys under "АДДОН-VC", most of which are not Grey's business at all (`interest_groups` vs HC/addon-HC, `ai_strategies` vs LLWA/addon-LLWA) or already settled.

## Четыре `pop_needs`, one at a time

`popneed_basic_food` was the fifth key `content_holes.py` originally listed here — already closed in GR.1 (`_greys/greys+vc done` restores addon-VC's groceries weight plus two ranch injects). The other four, checked against grey_usu's and grey_food_2_ranch's actual bodies rather than against raw VC:

* **`popneed_free_movement` — not a loss.** addon-VC's own Morgenroete-compat file (`zz_vc_morg_pop_needs.txt`) re-applies an `air_travel` entry (weight 4, max_supply_share 0.01) that grey_usu's `REPLACE:` wipes — but grey_usu's own file (`yMoG_USU_pop_needs.txt`) already `TRY_INJECT:`s the exact same entry, byte-for-byte, right after its own `REPLACE:`. Checked, no file.
* **`popneed_heating` — a genuine two-design dispute, not a silent loss.** addon-VC's body here is TGR's real rebalance (every entry commented `# TGR (N vanilla)`, not a vanilla copy the way GR.1 found for `popneed_basic_food`). grey_usu's `REPLACE:` touches every one of TGR's five goods with its own commented before/after numbers and adds a sixth (`services`) — a superset, not an omission. Same rule as GR.1's decision №12 (Grey's wins fields it actually moved): USU wins, no file.
* **`popneed_luxury_food` — same shape as heating.** addon-VC's body is TGR's real rebalance; grey_food_2_ranch's `TRY_REPLACE:` is RPR's own considered redesign (explicit "RPR - Added" / "RPR: …" comments on every entry, including a deliberate `default` change from `meat` to `groceries`). Two designs, ranch wins, no file.
* **`popneed_leisure` — the one real loss.** grey_usu's `REPLACE:` (`mMoG_USU_pop_needs.txt`) is its own deliberate leisure redesign (fine_art / wine / transportation / usu_logistics / merchant_marine / small_arms / aeroplanes / clippers / steamers — several vanilla goods explicitly commented "Remove Double Counted"), but it carries an `air_travel` entry commented OUT with the note *"Gets added with Morgenrote"* — the author expected Morgenroete's own `TRY_INJECT:` to still apply. It doesn't: the `REPLACE:` wipes it, and grey_usu's own follow-up `TRY_INJECT:` (`zzzMoG_USU_MR_pop_needs.txt`) restores only `elgar_music`, never `air_travel`. addon-VC's own Morgenroete-compat file carries the exact entry that fills the gap the author left — restored here, read live from that file.

## Что не здесь

Four companies (`company_imperial_arsenal`, `company_russian_american_company`, `company_standard_oil`, `company_william_cramp`) round out the plan's original count of interest for this pair, but none show up as a builds conflict at all — `content_holes.py --only builds` reports zero `company_types` keys for "АДДОН-VC". Consistent with GR.1/GR.5/GR.7: USU only `TRY_INJECT:`s these, additive, nothing of addon-VC's is displaced. No file.

## Как сделан мердж

`common/pop_needs/zz_greys_addonvc_pop_needs.txt` — `TRY_INJECT:` the `air_travel` entry read live out of addon-VC's own `zz_vc_morg_pop_needs.txt`, onto `popneed_leisure`.

## Пересборка

`tools/regen_greys_addonvc.py`; `--check` reports drift without writing. Reads the entry from addon-VC's own file (not a hand-written copy) and asserts on every run that grey_usu's body still mentions `air_travel` only inside a comment — so a fix on the Grey's side, or an addon-VC rebalance, turns into a failed run with a message rather than a silently redundant file. Re-run after any addon-VC or Grey's update.
