# pbe+psc noneed

<!-- meta
пара: PBE × PSC
статус: noneed
версии: —
позиция: —
файлов: 1
генератор: —
зависит от: —
-->

### PSC + PBE compatch (`pb+pbe`)

Совместимость для:
- `private_construction_sector` (PSC)
- `PowerBlocksExpanded` (PBE)

### Что фиксит

Оба мода добавляют свои хуки в `common/on_actions` и **оба определяют `on_monthly_pulse`**.
Если игра/загрузчик в текущей версии **не мерджит** два определения одного и того же on_action, то один из модов может “перезатереть” второй и его ежемесячная логика перестанет запускаться.

Этот компач **объединяет** содержимое `on_monthly_pulse`, сохраняя:
- PSC: `set_construction_weekly_on_action`
- PBE: `kates_weekly_global_on_action` + задержки 7/14/21

Файл: `common/on_actions/zz_pb_pbe_on_actions.txt`

### Порядок загрузки

1. `private_construction_sector`
2. `PowerBlocksExpanded`
3. `pb+pbe` (этот компач)



---

### Verification note (2026-08-21)

Re-checked PSC 2.05.2026 vs PBE (renamed `kates_*` → `vokaes_*`, common/buildings removed in 1.13 — see `сводка_pbe.md`). No changes since 2026-08-19 review (git log clean for both mod paths).

The premise above ("if the loader doesn't merge two `on_monthly_pulse` definitions") does not hold for 1.13: `common/on_actions/` is additive — every file's `on_actions = { ... }` list under a given hook is concatenated, not overwritten by load order. Confirmed by `scan_conflicts.py --a PSC --b PBE`: the only key-level hit across all of `common/*` is `on_monthly_pulse` (PSC: `PSC_on_actions.txt`, PBE: `vokaes_power_bloc_on_actions.txt`), and it is not a conflict for the reason above.

`zz_pb_pbe_on_actions.txt` in this folder is also stale on its own terms — it still calls `kates_weekly_global_on_action`, which no longer exists in PBE (renamed to `vokaes_weekly_global_on_action`). It was never applied (not present in the game `mod/` folder). Kept here only as a record of the old (incorrect) reasoning; safe to move to `_to_delete/` next time this folder is touched.

No other overlap found: 0 shared file paths (`gui`: construction panels vs power-bloc panels; PSC has no `power_bloc_*`, PBE has no `buildings/building_groups/goods/laws/technology`), 0 shared GUI widget names (`compare_gui_names.py`), 0 shared PM/PMG identifiers, 0 shared event ids, 0 shared localization keys.

**Conclusion: still `noneed`.**
