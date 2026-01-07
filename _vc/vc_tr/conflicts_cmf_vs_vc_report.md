# CMF vs VC — conflict report (heuristic)

- CMF root: `C:/Users/Andrey/Projects/vic3_mods/TechRes+Kuromi/cmf`
- VC root: `C:/Users/Andrey/Projects/vic3_mods/Victorian Century`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **4**
- Load order note: if `VC` loads after `CMF`, `VC` wins on these files.

### common/* file overlaps — 3
- **common/parties**: 3
  - `common/parties/conservative_party.txt`
  - `common/parties/liberal_party.txt`
  - `common/parties/radical_party.txt`

### other folders file overlaps
- **gui**: 1
  - `gui/00_MDF_frontend_dlc.gui`

## common/*: duplicate top-level keys (identifier-level)

### common/on_actions — 1 duplicates
- `on_new_ruler`
  - CMF: `common/on_actions/com_regency_blocker.txt`
  - VC: `common/on_actions/joi_code_on_actions.txt`

### common/parties — 3 duplicates
- `conservative_party`
  - CMF: `common/parties/conservative_party.txt`
  - VC: `common/parties/conservative_party.txt`
- `liberal_party`
  - CMF: `common/parties/liberal_party.txt`
  - VC: `common/parties/liberal_party.txt`
- `radical_party`
  - CMF: `common/parties/radical_party.txt`
  - VC: `common/parties/radical_party.txt`

### common/political_movements — 2 duplicates
- `movement_bonapartist`
  - CMF: `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - VC: `common/political_movements/joi_country_specific_ideological_movements.txt`
- `movement_utilitarian`
  - CMF: `common/political_movements/ycom_04_country_specific_ideological_movements.txt`
  - VC: `common/political_movements/joi_country_specific_ideological_movements.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**