# TGR vs PBE — conflict report (key-level heuristic)

- TGR root: `C:/Users/Andrey/Projects/vic3_mods_out/TheGreatRevision`
- PBE root: `C:/Users/Andrey/Projects/vic3_mods_out/PowerBlocksExpanded`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/diplomatic_actions — 1 duplicates
- `force_regime_change`
  - TGR: `common/diplomatic_actions/TGR_ADJUSTMENTS_power_bloc_force_regime_change.txt`
  - PBE: `common/diplomatic_actions/kates_power_bloc_actions.txt`

### common/modifier_type_definitions — 1 duplicates
- `state_bureaucrats_investment_pool_contribution_add`
  - TGR: `common/modifier_type_definitions/TGR_LOANS_todo_sort_into_other_files.txt`
  - PBE: `common/modifier_type_definitions/kates_power_bloc_modifier_types.txt`

### common/on_actions — 1 duplicates
- `on_monthly_pulse_country`
  - TGR: `common/on_actions/TGR_ADJUSTMENTS_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_GER_UNIFICATION_code_on_actions.txt`
  - TGR: `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`
  - PBE: `common/on_actions/kates_power_bloc_on_actions.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**