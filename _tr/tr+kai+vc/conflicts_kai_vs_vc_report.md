# KAI vs VC — conflict report (heuristic)

- KAI root: `C:/Users/Andrey/Projects/vic3_mods/TechRes+Kuromi/kai`
- VC root: `C:/Users/Andrey/Projects/vic3_mods/Victorian Century`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **0**
- (no overlapping relative file paths detected)

## common/*: duplicate top-level keys (identifier-level)

### common/defines — 1 duplicates
- `NAI`
  - KAI: `common/defines/kai_ai.txt`
  - VC: `common/defines/joi_ai.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**