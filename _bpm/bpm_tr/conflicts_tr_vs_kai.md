# T&R vs KAI — conflict report (heuristic)

- T&R root: `C:/Users/Andrey/Projects/vic3_mods/.TechRes+Kuromi/t&r`
- KAI root: `C:/Users/Andrey/Projects/vic3_mods/.TechRes+Kuromi/kai`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **0**
- (no overlapping relative file paths detected)

## common/*: duplicate top-level keys (identifier-level)

### common/ai_strategies — 6 duplicates
- `ai_strategy_colonial_expansion`
  - T&R: `common/ai_strategies/ztr_diplomatic_strategies.txt`
  - KAI: `common/ai_strategies/kai_diplomatic_strategies.txt`
- `ai_strategy_colonial_extraction`
  - T&R: `common/ai_strategies/ztr_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_default`
  - T&R: `common/ai_strategies/ztr_default_strategy.txt`
  - KAI: `common/ai_strategies/kai_default_strategy.txt`
- `ai_strategy_industrial_expansion`
  - T&R: `common/ai_strategies/ztr_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_resource_expansion`
  - T&R: `common/ai_strategies/ztr_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_territorial_expansion`
  - T&R: `common/ai_strategies/ztr_diplomatic_strategies.txt`
  - KAI: `common/ai_strategies/kai_diplomatic_strategies.txt`

### common/script_values — 2 duplicates
- `wanted_army_size_script_value`
  - T&R: `common/script_values/ztr_ai_script_values.txt`
  - KAI: `common/script_values/kai_script_values.txt`
- `wanted_navy_size_script_value`
  - T&R: `common/script_values/ztr_ai_script_values.txt`
  - KAI: `common/script_values/kai_script_values.txt`

### common/technology/technologies — 5 duplicates
- `atmospheric_engine`
  - T&R: `common/technology/technologies/ztr_modified_vanilla_production.txt`
  - KAI: `common/technology/technologies/kai_technologies.txt`
- `mechanical_tools`
  - T&R: `common/technology/technologies/ztr_modified_vanilla_production.txt`
  - KAI: `common/technology/technologies/kai_technologies.txt`
- `radio`
  - T&R: `common/technology/technologies/ztr_modified_vanilla_production.txt`
  - KAI: `common/technology/technologies/kai_technologies.txt`
- `steam_turbine`
  - T&R: `common/technology/technologies/ztr_modified_vanilla_production.txt`
  - KAI: `common/technology/technologies/kai_technologies.txt`
- `telephone`
  - T&R: `common/technology/technologies/ztr_modified_vanilla_production.txt`
  - KAI: `common/technology/technologies/kai_technologies.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**