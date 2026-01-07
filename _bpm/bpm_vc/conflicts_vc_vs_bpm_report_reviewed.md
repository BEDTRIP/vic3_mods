# VC + BPM — conflicts (reviewed)

Load order (as planned): **Victorian Century (VC) → Better Politics Mod (BPM)**, i.e. BPM effectively "wins" when there is an override.

This file is a *manual-reviewed* summary on top of the heuristic reports:

- `bpm_vc/conflicts_vc_vs_bpm_report.md` (file overlaps + `common/*` top-level keys + loc keys + `id = ...` in events)
- `bpm_vc/conflicts_vc_vs_bpm_event_definitions.md` (actual duplicate event *definitions* like `victoria.1 = { ... }`)

> Note on tooling: `scan_conflicts.py` treats `REPLACE:*`, `REPLACE_OR_CREATE:*`, `INJECT:*` as the same identifier (drops the prefix) and only detects top-level `key =` at brace depth 0, so it can miss/false-positive some things. The "reviewed" notes below call out the truly hard conflicts and the biggest merge hotspots.

---

## 1) Hard conflicts: identical file paths (6)

These are real, deterministic overrides in the virtual filesystem.

### `common/decisions/manifest_destiny.txt`
- VC: `#nothing`
- BPM: empty file

**Practical effect**: both mods *effectively blank out* this vanilla file. This overlap is low-risk, but keep an eye on any decisions that depend on it (BPM seems to move/override Manifest Destiny elsewhere).

### `common/journal_entries/00_peoples_springtime_je.txt`
- VC: a large `REPLACE_OR_CREATE:je_springtime_of_the_peoples = { ... }` (+ also `je_red_summer`)
- BPM: empty file

**Practical effect in VC→BPM order**: BPM deletes VC's version of the vanilla file and relies on its own JE implementation elsewhere (see `common/journal_entries/BPM_je_peoples_springtime.txt`).

This is **high-impact**: if we want VC content here, the compatch must merge VC logic into BPM's JE(s), because the VC file won't load at all once BPM is present.

### `common/history/countries/*.txt` (4 files)
Overlapped files:
- `common/history/countries/brz - brazil.txt`
- `common/history/countries/chi - china.txt`
- `common/history/countries/fra - france.txt`
- `common/history/countries/usa - usa.txt`

**Practical effect in VC→BPM order**: BPM replaces VC's starting setup for these countries (laws/variables/journal entries/modifiers/etc.).

This is **high-impact** and almost certainly needs a *merge*, because both mods add important country-specific setup. Quick examples from manual diffing:

- **BRZ**: VC adds `initialise_caciquismo_effect`, intelligentsia ruling IG setup, extra modifiers; BPM adds `je_pedro_brazil`, `brz_regency` modifier under RP1, but removes VC's extra setup.
- **CHI**: VC adds imperial examination / subjecthood / classical learning, many China JEs and variables; BPM sets `bpm_heaven_mandate`, different law mix, different tariffs, much simpler JE set.
- **FRA**: VC sets many variables/JEs (incl. Paris politics, etc.) and more law setup; BPM swaps to `law_laissez_faire`, adds `bpm_amendment_artisanal_economy`, sets BPM-specific variables and JE `je_bpm_july_monarchy`.
- **USA**: VC adds `real_manifest_destiny_var`, `law_protected_speech`, `law_no_womens_rights`, extra JEs/modifiers and triggers `joi_flavor_usa.1`; BPM adds multiple BPM JEs/modifiers and changes some laws (e.g. `law_right_of_assembly`).

---

## 2) `common/*` identifier duplicates (115) — biggest hotspots

The full list is in `bpm_vc/conflicts_vc_vs_bpm_report.md`. Below are the categories that are most likely to require compatch work.

### `common/on_actions` (4 keys)
Duplicates:
- `on_monthly_pulse_country`
- `on_yearly_pulse_country`
- `on_new_ruler`
- `on_diplo_play_war_start`

**Why critical**: both mods define these as top-level blocks (not additive lists), so one definition can easily wipe the other depending on load/file order.

Example: VC uses `on_monthly_pulse_country` for headlines + "great man"/monarchy logic; BPM uses it to drive a large chunk of its systems (`on_bpm_monthly_pulse_country`, etc.). A compatch almost certainly needs a merged `on_actions` file (usually named `zzzz_...`), explicitly including both sets of `on_actions` / `random_events` / `events`.

### `common/journal_entries` (15 keys)
Many vanilla JE keys are replaced by both mods, notably:
- German unification chain (`je_german_unification`, north/south, schleswig-holstein, idea)
- Meiji restoration chain
- Sepoy mutiny chain
- French monarchism JE (`je_cement_the_rightful_dynasty`)
- Peoples' Springtime JE (`je_springtime_of_the_peoples`)

**Why critical**: both mods rework the same story chains and conditions. BPM tends to use `zz_bpm_*.txt` with `REPLACE:` (intended to be late-loading), VC uses `REPLACE_OR_CREATE:` in its own vanilla-named files. Expect logic conflicts and missing variables if only one side survives.

### `common/interest_groups` (8 keys)
All major IGs (`ig_armed_forces`, `ig_industrialists`, etc.) are overridden by both mods.

**Why critical**: this affects ideology sets, traits, and on-enable initialization logic. BPM uses `REPLACE:` in `zzzz_*.txt`; VC uses `REPLACE_OR_CREATE:` in `joi_*.txt`. If BPM wins, VC's country-specific IG trait logic is lost; if VC wins, BPM’s internal ideology systems may break.

### `common/parties` (3 keys)
`conservative_party`, `liberal_party`, `radical_party` are replaced by both mods.

**Why critical**: parties tie directly into BPM’s political systems and VC’s flavor/national party naming. Needs an explicit decision for which schema is "base" and how to merge naming rules.

### `common/character_templates` (49 keys)
Large overlap of historical character templates (GBR, RUS, TUR, etc.).

**Why critical**: event/journal logic often references templates. If the template is overwritten with incompatible traits/IGs, event chains can behave differently or fail assumptions.

### Other important duplicates
- `common/country_formation`: `GER` is changed by both mods (VC has explicit state list and extra restrictions; BPM uses `use_culture_states` and adds its own gating via global vars).
- `common/technology/technologies`: `corporatism` differs (VC shifts Devout ideologies; BPM shifts Industrialists/Trade Unions ideologies).
- `common/ideologies`: overlaps include `ideology_bonapartist`, `ideology_corporatist`, `ideology_scholar_paternalistic`, etc.
- `common/static_modifiers`: `modifier_india_company_rule`, `modifier_india_crown_rule` differ (VC has larger effect sets, BPM has smaller).
- `common/dynamic_country_names`: CAN/LOM/XIN.
- `common/flag_definitions`: GER.
- `common/defines`: `NAI` (AI defines differ).
- `common/history/lobbies`: `LOBBIES`.
- `common/scripted_buttons`: `je_the_eastern_border_treaty_of_aigun`.
- `common/political_movements`: `movement_bonapartist`, `movement_utilitarian`.

---

## 3) Events folder: duplicate *event definitions* (missed by scan_conflicts.py)

Heuristic event-definition scan output: `bpm_vc/conflicts_vc_vs_bpm_event_definitions.md`

Found:
- `victoria.1` is defined in both:
  - VC: `events/victoria_events.txt`
  - BPM: `events/_victoria_events.txt`

**Why critical**: two different definitions for the same `namespace.id` event key is a classic hard conflict (one overwrites the other depending on load order).

---

## 4) Checked other folders

- **No identical file path overlaps outside `common/*`** were detected by `scan_conflicts.py`.
- **Localization key overlaps**: 0 (per report).
- **GUI quick check**: VC uses `gui/headlines_texticons.gui` (defines `headlines_newsicon`), BPM uses `gui/BPM_modded_texticons.gui` and does *not* define `headlines_newsicon` → no obvious collision found.

