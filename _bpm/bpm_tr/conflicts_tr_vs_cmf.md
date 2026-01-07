# T&R vs CMF — conflict report (heuristic)

- T&R root: `C:/Users/Andrey/Projects/vic3_mods/.TechRes+Kuromi/t&r`
- CMF root: `C:/Users/Andrey/Projects/vic3_mods/.TechRes+Kuromi/cmf`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **0**
- (no overlapping relative file paths detected)

## common/*: duplicate top-level keys (identifier-level)

### common/history/global — 1 duplicates
- `GLOBAL`
  - T&R: `common/history/global/ztr_global.txt`
  - CMF: `common/history/global/enable_example_button.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**