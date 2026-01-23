# MR + BPM — сводка конфликтов (load order: MR → BPM)

Цель: сделать компач для **`.Morgenrote/morgen` (MR)** и **`.BPM` (BPM)**.  
Порядок запуска по условию: **MR сначала, BPM последним** (значит при “жёстких” совпадениях BPM выигрывает).

## Что я прогнал автоматически

Отчёты-черновики (эвристика):
- `bpm_mr/conflicts_morgen_vs_bpm_report.md` — **Morgenrote(morgen) vs BPM**
- `bpm_mr/conflicts_cmf_vs_bpm_report.md` — **CMF (из пакета MR) vs BPM** (важно, т.к. MR зависит от CMF)

Важно про эвристику:
- дубликаты ключей в `common/history/*` часто ложные (там везде `CHARACTERS`/`COUNTRIES`/`GLOBAL`);
- дубликаты `common/on_actions/*` чаще всего **аддитивны** и не означают конфликт, если нет `REPLACE*`.

## Подтверждённые конфликты MR ↔ BPM (реально ломают/перетирают)

### 1) Жёсткий конфликт по пути файла (BPM перетирает MR целиком)

- **`common/achievement_groups.txt`**
  - MR: содержит **ванильные группы** + дополнительные **Morgenröte achievement groups** (Lepsius/Verrier/Elgar/…).
  - BPM: содержит укороченный набор ванильных групп + добавляет `bpm_achievements`, но при этом **теряет часть ванильных достижений** (сравнение с `..vanillaVIC3/game/common/achievement_groups.txt`) и **теряет все MR-группы**.
  - **Итог при порядке MR→BPM**: пропадут MR achievement groups (и часть ванили из MR-файла).

**Что делать в компаче**: в `bpm_mr` сделать свой `common/achievement_groups.txt`, собранный так:
- базовые группы **как в ванили**;
- добавить `group = { name = "bpm_achievements" ... }` (из BPM);
- добавить все MR-группы (из MR).

### 2) Конфликт по идентификатору технологии (оба трогают один ванильный tech)

- **`mass_propaganda`** (`common/technology/technologies/...`)
  - MR: `TRY_INJECT:mass_propaganda` добавляет prereq `elgar_mass_culture_tech` и комментом говорит “changed from film”.
  - BPM: `REPLACE:mass_propaganda` задаёт prereq `political_agitation` + `film`.
  - **Итог при MR→BPM**: MR-инжект будет **перетёрт** BPM-REPLACE, и `elgar_mass_culture_tech` не окажется в prereq.

**Что делать в компаче** (минимум, безопасно): после BPM сделать `TRY_INJECT:mass_propaganda` и добавить `elgar_mass_culture_tech` в `unlocking_technologies`.  
**Требует решения вручную**: оставлять ли `film` (как в BPM) или убирать (как хотел MR) — это уже про баланс/ветку техов.

### 3) Конфликт scripted trigger “мод активен”

- **`morgenrote_is_active`**
  - MR: `REPLACE_OR_CREATE:morgenrote_is_active = { always = yes }` (файл `common/scripted_triggers/zz_mr_is_active_trigger.txt`)
  - BPM: в `common/scripted_triggers/00_community_mod_compatibility_triggers.txt` задаёт `morgenrote_is_active = { always = no }`
  - **Итог при MR→BPM**: BPM-версия (always no) **перетирает** MR, и проверка “MR активен” становится ложной.

**Что делать в компаче**: положить в компач файл `common/scripted_triggers/zz_mr_is_active_trigger.txt` (или другой `zz_...`) с
`REPLACE_OR_CREATE:morgenrote_is_active = { always = yes }`, чтобы он грузился **после BPM**.

## Потенциально важные конфликты MR ↔ BPM (не “падает сразу”, но реально меняет контент)

### 4) Дубликаты `character_templates` (шведские правители) — BPM перетирает MR-черты/ДНК

Ключи:
- `swe_karl_johan_bernadotte_template`
- `swe_oscar_bernadotte_template`
- `swe_charles_bernadotte_template`
- `swe_oscar_ii_bernadotte_template`
- `swe_gustaf_v_bernadotte_template`

Файлы:
- MR: `common/character_templates/mr_general_rulers.txt` (делает `TRY_REPLACE:` и добавляет **mr_* traits**, местами **mr_* DNA**, IG/идеологию)
- BPM: `common/character_templates/zz_bpm_historical_leaders_europe.txt` (делает `REPLACE:` и задаёт **свою** логику IG/идеологий/трейтов)

**Итог при MR→BPM**: BPM гарантированно “победит” (полный `REPLACE`), поэтому MR-уникальные трейты/ДНК у этих персонажей пропадут.

**Что делать в компаче**: это конфликт “по дизайну” — нужно решить, чью версию считать приоритетной:
- если важнее MR-flavor (mr-traits/DNA) → в компаче вернуть MR-версии (или слить в одну);
- если важнее BPM-логика лидеров → оставить BPM, но понимать, что часть MR-flavor по этим персонажам будет обрезана.

## Не-конфликты / ожидаемые совпадения (можно не чинить)

- `common/history/characters`: `CHARACTERS` (ложноположительно)
- `common/history/countries`: `COUNTRIES` (ложноположительно)
- `common/history/global`: `GLOBAL` (ложноположительно)
- `common/on_actions/*`: совпадения ключей `on_monthly_pulse_country` и т.п. **аддитивны** (в BPM файл без `REPLACE*`).

## Важно: слой CMF ↔ BPM (т.к. MR зависит от CMF)

Даже если мы делаем компач только MR+BPM, в реальном плейсете MR обычно означает ещё и CMF.
Скан показал большие пересечения CMF↔BPM по:
- `common/laws/*` (например `law_autocracy`, `law_monarchy`, ...)
- `common/parties/*` (vanilla party keys)
- `common/political_movements/*`
- `common/scripted_triggers/*` (community compatibility triggers)

См. детали в `bpm_mr/conflicts_cmf_vs_bpm_report.md`.  
Это нужно будет либо подтвердить “BPM уже включает CMF-правки”, либо реально сливать (иначе CMF-изменения будут частично потеряны, т.к. BPM грузится последним).

