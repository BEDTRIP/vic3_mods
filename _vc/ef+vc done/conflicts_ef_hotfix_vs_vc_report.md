# VC vs ef_hotfix — conflict report (key-level heuristic)

- VC root: `/sessions/rcw-011ez4rtnjrhyy9msxxbherq/mnt/Projects/vic3_mods_out/VC`
- ef_hotfix root: `/sessions/rcw-011ez4rtnjrhyy9msxxbherq/mnt/Projects/vic3_mods/_ef/ef hotfix 1.13`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/history/global — 1 duplicates
- `GLOBAL`
  - VC: `common/history/global/joi_global.txt`
  - ef_hotfix: `common/history/global/zz_ef_cm_init.txt`
  - ef_hotfix: `common/history/global/zz_ef_currency_fix.txt`
  - ef_hotfix: `common/history/global/zz_ef_init_stockpiling_state_vars.txt`

### common/on_actions — 1 duplicates
- `on_monthly_pulse_country`
  - VC: `common/on_actions/headlines_on_actions.txt`
  - VC: `common/on_actions/joi_code_on_actions.txt`
  - ef_hotfix: `common/on_actions/zz_ef_cm_on_actions.txt`
  - ef_hotfix: `common/on_actions/zz_ef_local_currency_on_actions.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**