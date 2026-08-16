# PBE vs BPM — conflict report (heuristic)

- PBE root: `C:/Users/Andrey/Projects/vic3_mods/.PowerBlocksExpanded`
- BPM root: `C:/Users/Andrey/Projects/vic3_mods/.BPM`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **0**
- (no overlapping relative file paths detected)

## common/*: duplicate top-level keys (identifier-level)

### common/modifier_type_definitions — 1 duplicates
- `state_bureaucrats_investment_pool_efficiency_mult`
  - PBE: `common/modifier_type_definitions/kates_power_bloc_modifier_types.txt`
  - BPM: `common/modifier_type_definitions/BPM_functional_modifiers.txt`

### common/on_actions — 2 duplicates
- `on_monthly_pulse_country`
  - PBE: `common/on_actions/kates_power_bloc_on_actions.txt`
  - BPM: `common/on_actions/BPM_CAB_on_actions.txt`
  - BPM: `common/on_actions/BPM_bnap_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`
  - BPM: `common/on_actions/bpm_france_oa.txt`
  - BPM: `common/on_actions/bpm_hog_top_actions.txt`
- `on_wargoal_enforced`
  - PBE: `common/on_actions/kates_power_bloc_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**