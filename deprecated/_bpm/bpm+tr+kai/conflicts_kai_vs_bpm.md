# KAI vs BPM — conflict report (heuristic)

- KAI root: `C:/Users/Andrey/Projects/vic3_mods/.TechRes+Kuromi/kai`
- BPM root: `C:/Users/Andrey/Projects/vic3_mods/.BPM`

## How to read this report

- **File path overlaps**: identical relative file paths in both mods. This is a **hard conflict**: the later-loaded mod replaces the earlier one's file.
- **Identifier-level duplicates**: same script key / localization key / event id used by both mods (even if file paths differ). This is a heuristic and may include a few false positives.

## file path overlaps (hard conflicts by load order)

- Total overlapping files: **0**
- (no overlapping relative file paths detected)

## common/*: duplicate top-level keys (identifier-level)

### common/ai_strategies — 5 duplicates
- `ai_strategy_conservative_agenda`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
  - BPM: `common/ai_strategies/BPM_political_strategies.txt`
- `ai_strategy_egalitarian_agenda`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
  - BPM: `common/ai_strategies/BPM_political_strategies.txt`
- `ai_strategy_nationalist_agenda`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
  - BPM: `common/ai_strategies/BPM_political_strategies.txt`
- `ai_strategy_progressive_agenda`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
  - BPM: `common/ai_strategies/BPM_political_strategies.txt`
- `ai_strategy_reactionary_agenda`
  - KAI: `common/ai_strategies/kai_political_strategies.txt`
  - BPM: `common/ai_strategies/BPM_political_strategies.txt`

### common/defines — 1 duplicates
- `NAI`
  - KAI: `common/defines/kai_ai.txt`
  - BPM: `common/defines/BPM_defines.txt`

### common/laws — 13 duplicates
- `law_agrarianism`
  - KAI: `common/laws/kai_economic_system.txt`
  - BPM: `common/laws/BPM_economic_system.txt`
- `law_dedicated_police`
  - KAI: `common/laws/kai_policing.txt`
  - BPM: `common/laws/BPM_police.txt`
- `law_guaranteed_liberties`
  - KAI: `common/laws/kai_internal_security.txt`
  - BPM: `common/laws/BPM_internal_security.txt`
- `law_local_police`
  - KAI: `common/laws/kai_policing.txt`
  - BPM: `common/laws/BPM_police.txt`
- `law_militarized_police`
  - KAI: `common/laws/kai_policing.txt`
  - BPM: `common/laws/BPM_police.txt`
- `law_national_guard`
  - KAI: `common/laws/kai_internal_security.txt`
  - BPM: `common/laws/BPM_internal_security.txt`
- `law_private_health_insurance`
  - KAI: `common/laws/kai_health_system.txt`
  - BPM: `common/laws/BPM_health_system.txt`
- `law_private_schools`
  - KAI: `common/laws/kai_education_system.txt`
  - BPM: `common/laws/BPM_education_system.txt`
- `law_public_schools`
  - KAI: `common/laws/kai_education_system.txt`
  - BPM: `common/laws/BPM_education_system.txt`
- `law_regulatory_bodies`
  - KAI: `common/laws/kai_labor_rights.txt`
  - BPM: `common/laws/BPM_labor_laws.txt`
- `law_religious_schools`
  - KAI: `common/laws/kai_education_system.txt`
  - BPM: `common/laws/BPM_education_system.txt`
- `law_secret_police`
  - KAI: `common/laws/kai_internal_security.txt`
  - BPM: `common/laws/BPM_internal_security.txt`
- `law_worker_protections`
  - KAI: `common/laws/kai_labor_rights.txt`
  - BPM: `common/laws/BPM_labor_laws.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**