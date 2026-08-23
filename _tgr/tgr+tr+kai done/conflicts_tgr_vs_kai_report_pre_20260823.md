# TGR vs KAI — conflict report (key-level heuristic)

- TGR root: `C:/Users/Andrey/Projects/vic3_mods_out/TheGreatRevision`
- KAI root: `C:/Users/Andrey/Projects/vic3_mods_out/TechRes+Kuromi/kai`

This report finds **identifier-level duplicates** (same key/id defined by both mods), even when file paths do not overlap. It is a heuristic and may include a few false positives.

## common/*: duplicate top-level keys

### common/ai_strategies — 7 duplicates
- `ai_strategy_agricultural_expansion`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_colonial_extraction`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_default`
  - TGR: `common/ai_strategies/TGR_ADJUSTMENTS_default_strategy.txt`
  - TGR: `common/ai_strategies/TGR_POLITICS_default_strategy.txt`
  - KAI: `common/ai_strategies/kai_default_strategy.txt`
- `ai_strategy_industrial_expansion`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_placate_population`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_plantation_economy`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`
- `ai_strategy_resource_expansion`
  - TGR: `common/ai_strategies/TGR_TRADE_admin_strategies.txt`
  - KAI: `common/ai_strategies/kai_admin_strategies.txt`

### common/buildings — 1 duplicates
- `building_construction_sector`
  - TGR: `common/buildings/TGR_TRADE_construction.txt`
  - KAI: `common/buildings/kai_buildings.txt`

### common/defines — 1 duplicates
- `NAI`
  - TGR: `common/defines/TGR_ADJUSTMENTS_ai.txt`
  - TGR: `common/defines/TGR_GER_UNIFICATION_ai.txt`
  - TGR: `common/defines/TGR_TAX_PANEL_defines.txt`
  - TGR: `common/defines/TGR_TRADE_ai.txt`
  - KAI: `common/defines/kai_ai.txt`

### common/laws — 23 duplicates
- `law_agrarianism`
  - TGR: `common/laws/TGR_POLITICS_economic_system.txt`
  - KAI: `common/laws/kai_economic_system.txt`
- `law_charitable_health_system`
  - TGR: `common/laws/TGR_POLITICS_health_system.txt`
  - KAI: `common/laws/kai_health_system.txt`
- `law_colonial_exploitation`
  - TGR: `common/laws/TGR_POLITICS_colonial_affairs.txt`
  - KAI: `common/laws/kai_colonial_affairs.txt`
- `law_colonial_resettlement`
  - TGR: `common/laws/TGR_POLITICS_colonial_affairs.txt`
  - KAI: `common/laws/kai_colonial_affairs.txt`
- `law_dedicated_police`
  - TGR: `common/laws/TGR_POLITICS_policing.txt`
  - KAI: `common/laws/kai_policing.txt`
- `law_frontier_colonization`
  - TGR: `common/laws/TGR_POLITICS_colonial_affairs.txt`
  - KAI: `common/laws/kai_colonial_affairs.txt`
- `law_guaranteed_liberties`
  - TGR: `common/laws/TGR_POLITICS_internal_security.txt`
  - KAI: `common/laws/kai_internal_security.txt`
- `law_local_police`
  - TGR: `common/laws/TGR_POLITICS_policing.txt`
  - KAI: `common/laws/kai_policing.txt`
- `law_militarized_police`
  - TGR: `common/laws/TGR_POLITICS_policing.txt`
  - KAI: `common/laws/kai_policing.txt`
- `law_national_guard`
  - TGR: `common/laws/TGR_POLITICS_internal_security.txt`
  - KAI: `common/laws/kai_internal_security.txt`
- `law_old_age_pension`
  - TGR: `common/laws/TGR_POLITICS_welfare.txt`
  - KAI: `common/laws/kai_welfare.txt`
- `law_per_capita_based_taxation`
  - TGR: `common/laws/TGR_TAX_PANEL_taxation.txt`
  - KAI: `common/laws/kai_taxation.txt`
- `law_poor_laws`
  - TGR: `common/laws/TGR_POLITICS_welfare.txt`
  - KAI: `common/laws/kai_welfare.txt`
- `law_private_health_insurance`
  - TGR: `common/laws/TGR_POLITICS_health_system.txt`
  - KAI: `common/laws/kai_health_system.txt`
- `law_private_schools`
  - TGR: `common/laws/TGR_POLITICS_education_system.txt`
  - KAI: `common/laws/kai_education_system.txt`
- `law_proportional_taxation`
  - TGR: `common/laws/TGR_TAX_PANEL_taxation.txt`
  - KAI: `common/laws/kai_taxation.txt`
- `law_public_health_insurance`
  - TGR: `common/laws/TGR_POLITICS_health_system.txt`
  - KAI: `common/laws/kai_health_system.txt`
- `law_public_schools`
  - TGR: `common/laws/TGR_POLITICS_education_system.txt`
  - KAI: `common/laws/kai_education_system.txt`
- `law_regulatory_bodies`
  - TGR: `common/laws/TGR_POLITICS_labor_rights.txt`
  - KAI: `common/laws/kai_labor_rights.txt`
- `law_religious_schools`
  - TGR: `common/laws/TGR_POLITICS_education_system.txt`
  - KAI: `common/laws/kai_education_system.txt`
- `law_secret_police`
  - TGR: `common/laws/TGR_POLITICS_internal_security.txt`
  - KAI: `common/laws/kai_internal_security.txt`
- `law_wage_subsidies`
  - TGR: `common/laws/TGR_POLITICS_welfare.txt`
  - KAI: `common/laws/kai_welfare.txt`
- `law_worker_protections`
  - TGR: `common/laws/TGR_POLITICS_labor_rights.txt`
  - KAI: `common/laws/kai_labor_rights.txt`

## localization: duplicate localization keys
- Total duplicate localization keys: **0**

## events: duplicate event ids (`id = ...` anywhere in events/*.txt)
- Total duplicate event ids: **0**