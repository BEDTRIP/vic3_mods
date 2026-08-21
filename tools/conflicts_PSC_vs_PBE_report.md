# PSC vs PBE — conflict report (key-level heuristic)

- PSC root: `/sessions/rcw-01qhw3t4wktqmagkhglgungv/mnt/Projects/vic3_mods_out/PSC`
- PBE root: `/sessions/rcw-01qhw3t4wktqmagkhglgungv/mnt/Projects/vic3_mods_out/PowerBlocksExpanded`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/on_actions — 1 duplicates
- `on_monthly_pulse`
  - PSC: `common/on_actions/PSC_on_actions.txt`
  - PBE: `common/on_actions/vokaes_power_bloc_on_actions.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**