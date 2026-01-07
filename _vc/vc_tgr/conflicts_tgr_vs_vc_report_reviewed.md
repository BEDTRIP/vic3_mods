# TGR vs VC — conflict report (reviewed)

Load order: **TGR first → VC last** (so **VC wins** on hard overwrites / REPLACEs).

This file is a reviewed/annotated version of the heuristic report: `conflicts_tgr_vs_vc_report.md`.

## Summary

- **Hard file path overlaps**: **12** (VC overwrites TGR on these paths)
- **`common/*` duplicate top-level keys (heuristic)**: **137**
- **Duplicate localization keys**: **0**
- **Duplicate event ids**: **0**

## 1) Hard conflicts: identical relative file paths (VC overwrites TGR)

All 12 overlapping files are **different by content** (hash/size differs), so these are real overrides.

### 1.1 `common/*` overlaps (10)

- **`common/decisions/manifest_destiny.txt`**
  - TGR: implements `manifest_destiny` decision (real content).
  - VC: file is `#nothing` (disables vanilla MD, and will also disable TGR’s file if VC loads last).
  - **Impact**: without a compatch, **TGR’s Manifest Destiny is completely disabled**.

- **`common/history/countries/*.txt`** (6)
  - `aus - austria.txt`
  - `brz - brazil.txt`
  - `chi - china.txt`
  - `fra - france.txt`
  - `gbr - great britain.txt`
  - `tur - ottoman empire.txt`
  - **Impact**: стартовые переменные/законы/настройки, которые делает TGR в этих странах, будут **переписаны VC** (или наоборот, если поменять порядок).

- **`common/parties/*.txt`** (3)
  - `conservative_party.txt`
  - `liberal_party.txt`
  - `radical_party.txt`
  - **Impact**: партии берутся целиком из **VC**, а TGR-правки в этих файлах не работают без мержа.

### 1.2 Other overlaps (2)

- **`map_data/state_regions/00_west_europe.txt`**
- **`map_data/state_regions/11_east_asia.txt`**
- **Impact**: изменения карты/ресурсов TGR в этих двух файлах будут полностью **переписаны VC**.

## 2) `common/*` duplicate identifiers — “hard” vs “soft”

Ниже — дубликаты по *ID/ключам*, когда оба мода создают/заменяют **одни и те же идентификаторы**.

### 2.1 High priority “hard” identifier conflicts (actual replacement)

#### `common/buy_packages` — **wealth_1 … wealth_99** (99 duplicates)

- TGR: `common/buy_packages/00_buy_packages.txt` defines `wealth_1 = { ... }` etc (без `REPLACE_OR_CREATE:` префикса).
- VC: `common/buy_packages/joi_buy_packages.txt` defines **`REPLACE_OR_CREATE:wealth_1 … REPLACE_OR_CREATE:wealth_99`**.
- **Likely result with load order (VC last)**: VC’s definitions **override** TGR’s wealth packages.
- **Impact**: без мержа вы фактически выбираете **только одну** систему buy_packages (скорее VC).

#### `common/pop_needs` — 3 duplicates

IDs:
- `popneed_basic_food`
- `popneed_luxury_food`
- `popneed_luxury_drinks`

Both mods use `REPLACE_OR_CREATE` for these popneeds:
- TGR: `common/pop_needs/TGR_TRADE_pop_needs.txt`
- VC: `common/pop_needs/joi_pop_needs.txt`

**Impact**: при VC-last будут работать **VC popneeds** (TGR версии этих 3 нужд потеряются).

#### `common/interest_groups` — 8 duplicates (very high impact)

IDs:
- `ig_armed_forces`
- `ig_devout`
- `ig_industrialists`
- `ig_intelligentsia`
- `ig_landowners`
- `ig_petty_bourgeoisie`
- `ig_rural_folk`
- `ig_trade_unions`

Both mods use `REPLACE_OR_CREATE` for these IGs:
- TGR: `common/interest_groups/TGR_POLITICS_*.txt`
- VC: `common/interest_groups/joi_*.txt`

**Impact**:
- В игре останется **только одна версия** каждого IG (при VC-last — VC).
- Это один из самых опасных конфликтов, потому что IG ↔ ideologies ↔ laws/law_groups тесно связаны: если оставить VC-IG, можно потерять “политический движок” TGR (и наоборот).

#### `common/technology/technologies` — `human_rights` (1 duplicate)

- TGR: `common/technology/technologies/TGR_POLITICS_society.txt` — более “ванильная” версия `human_rights` (модификаторы институтов).
- VC: `common/technology/technologies/joi_society.txt` — добавляет **`on_researched`** логику (перепрошивка идеологий у IG и др.) + иные модификаторы.
- **Impact**: при VC-last работает **VC версия `human_rights`**, включая её on_researched-эффекты.

#### `common/static_modifiers` — `base_values` (1 duplicate, but critical)

- TGR: `common/static_modifiers/TGR_TRADE_code_static_modifiers.txt` uses **`INJECT:base_values`** to add:
  - `country_company_throughput_bonus_add`
  - `country_company_construction_efficiency_bonus_add`
- VC: `common/static_modifiers/joi_code_static_modifiers.txt` uses **`REPLACE_OR_CREATE:base_values`** (огромный блок базовых модификаторов).
- **Impact**: при VC-last **TGR INJECT в base_values будет затёрт** REPLACE’ом VC, если не перенести эти строки в итоговый `base_values`.

#### `common/defines` — group-level duplicates: `NAI`, `NPops` (2 duplicates)

At top-level:
- TGR defines: multiple files contain `NAI = { ... }` and `NPops = { ... }`.
- VC defines: `common/defines/joi_ai.txt` (`NAI`) and `common/defines/joi_defines.txt` (`NPops`).

Manual spot-check shows **inner-key collisions** at least in `NAI`, e.g.:
- `PRODUCTION_BUILDING_AUTONOMOUS_INVESTMENT_RANDOM_FACTOR_MULT`
- `PRODUCTION_BUILDING_AUTONOMOUS_INVESTMENT_STATE_RANDOM_FACTOR_MULT`
- `PRODUCTION_BUILDING_AUTONOMOUS_INVESTMENT_PROFIT_FACTOR_MULT`

**Impact**: нужно решать, какие конкретные параметры внутри `NAI`/`NPops` должны побеждать (часть может быть совместима, часть — нет).

#### `common/company_types` — 10 duplicate companies

IDs (all are duplicated):
- `company_east_india_company`
- `company_gebruder_thonet`
- `company_imperial_arsenal`
- `company_krupp`
- `company_mitsui`
- `company_ong_lung_sheng_tea_company`
- `company_philips`
- `company_russian_american_company`
- `company_united_fruit`
- `company_william_cramp`

Both mods use `REPLACE_OR_CREATE`:
- TGR: `common/company_types/TGR_TRADE_companies.txt` (часто с очень большим `ai_weight` и расширенными building_types)
- VC: `common/company_types/joi_companies.txt`

**Impact**: без мержа для этих 10 компаний победит **VC** (при VC-last).

#### `common/government_types` — 2 duplicates

IDs:
- `gov_presidential_democracy`
- `gov_presidential_dictatorship`

Both mods use `REPLACE_OR_CREATE`:
- TGR: `common/government_types/TGR_POLITICS_presidential_republics.txt`
- VC: `common/government_types/joi_republics.txt`

**Impact**: победит **VC** (при VC-last), при этом условия/ограничения у этих gov types реально различаются.

#### `common/country_formation` — `GER` (1 duplicate)

- TGR: `common/country_formation/TGR_GER_UNIFICATION_major_formables.txt` — `REPLACE_OR_CREATE:GER` с `use_culture_states = yes` и более простой `possible`.
- VC: `common/country_formation/jol_major_formables.txt` — `REPLACE_OR_CREATE:GER` со списком `states = { ... }` + доп. условия.
- **Impact**: победит **VC** (при VC-last).

#### `common/ideologies` — `ideology_utilitarian_leader` (1 duplicate)

- Both use `REPLACE_OR_CREATE`, но отличаются по:
  - деталям по slavery (`law_colonial_slavery` и т.п.),
  - stance по `law_affirmative_action`,
  - весам/триггерам.
- **Impact**: победит **VC** (при VC-last), но это менее критично, чем buy_packages/IG/defines.

### 2.2 Lower risk / likely additive (still worth a quick check when merging)

#### `common/on_actions` — duplicates are **probably not a real conflict**

The heuristic flags duplicates for:
- `on_monthly_pulse_country`
- `on_yearly_pulse_country`

Manual check: both mods define these as plain repeated blocks like:
- `on_monthly_pulse_country = { ... }`
…without `REPLACE:` / `REPLACE_OR_CREATE:` / `INJECT:` prefixes.

This strongly suggests the engine treats them **additively** (multiple definitions append), and both mods can co-exist here.

## 3) What is NOT conflicting (based on scans)

- **Localization keys**: no duplicates detected.
- **Events**:
  - Heuristic `scan_conflicts.py` checks `id = ...` (may miss true event keys).
  - Additional manual scan of **top-level event keys** (`namespace.event = { ... }` at brace depth 0) found **no duplicates between TGR and VC** (only the non-unique header key `namespace`).
- **GUI files**: no path overlaps (`TGR/gui/budget_panel.gui` vs `VC/gui/*`).

