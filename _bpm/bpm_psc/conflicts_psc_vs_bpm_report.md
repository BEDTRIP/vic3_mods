# PSC vs BPM — conflict report (heuristic)

- PSC root: `C:/Users/Andrey/Projects/vic3_mods/.PSC`
- BPM root: `C:/Users/Andrey/Projects/vic3_mods/.BPM`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **0**
- (no overlapping relative file paths detected)

## common/*: duplicate top-level keys (identifier-level)

### common/history/global — 1 duplicates

- `GLOBAL`
  - PSC: `common/history/global/PSC_global.txt`
  - BPM: `common/history/global/00_bpm_global.txt`
  - BPM: `common/history/global/zz_bpm_global.txt`
  - BPM: `common/history/global/zzz_bpm_country_specific_global.txt`
  - BPM: `common/history/global/zzzz_bpm_brazil_la_specific_global.txt`
  - BPM: `common/history/global/zzzzzz_bpm_global_last.txt`

### common/on_actions — 1 duplicates

- `on_acquired_technology`
  - PSC: `common/on_actions/PSC_on_actions.txt`
  - BPM: `common/on_actions/BPM_code_on_actions.txt`

## localization: duplicate localization keys

- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)

- Total duplicate event ids: 0

