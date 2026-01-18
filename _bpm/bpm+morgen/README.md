### ComPatch `Morgenrote` + `BPM` (порядок: **Morgenrote → BPM → этот компач**)

Это **примерный компатч** для связки:
- `C:\Users\Andrey\Projects\vic3_mods_out\Morgenrote\morgen`
- `C:\Users\Andrey\Projects\vic3_mods_out\BPM`

Порядок в плейсете по условию: **Morgenrote сначала, BPM вторым, компач последним**.

### Что конкретно исправлено (по конфликтам из `conflicts_morgen_vs_bpm_report.md`)

- **`common/achievement_groups.txt` (жёсткий конфликт по пути файла)**  
  - **Проблема**: при MR→BPM файл BPM целиком заменяет MR и в итоге теряются группы достижений Morgenröte, а также часть “ванильных” достижений (т.к. у BPM файл укорочен).  
  - **Исправление в компаче**: добавлен файл `common/achievement_groups.txt`, который:
    - включает **`group = { name = "bpm_achievements" ... }`** из BPM;
    - берёт **полный набор “vanilla groups + MR groups”** из MR (в т.ч. `lepsius_achievement_group`, `verrier_achievement_group`, …).

- **`morgenrote_is_active` (scripted trigger “мод активен”)**  
  - **Проблема**: BPM задаёт `morgenrote_is_active = { always = no }` (community compatibility triggers) и при MR→BPM “перетирает” MR, из-за чего проверки “MR активен” становятся ложными.  
  - **Исправление в компаче**: добавлен `common/scripted_triggers/zzzz_bpm_mr_is_active_trigger.txt` с  
    `REPLACE_OR_CREATE:morgenrote_is_active = { always = yes }`.

- **`mass_propaganda` (технология)**  
  - **Проблема**: MR делает `TRY_INJECT:mass_propaganda` и добавляет prereq `elgar_mass_culture_tech`, но BPM делает `REPLACE:mass_propaganda`, поэтому при MR→BPM MR‑инжект теряется.  
  - **Исправление в компаче**: добавлен `common/technology/technologies/zzzz_bpm_mr_society_technologies_patch.txt` с повторным  
    `TRY_INJECT:mass_propaganda` → добавляет `elgar_mass_culture_tech` в `unlocking_technologies`.

### Какие конфликты ещё остались (не исправлял в этом “примерном” компаче)

- **`common/character_templates` (шведские правители `swe_*_bernadotte_template`)**  
  - MR делает `TRY_REPLACE` (mr‑traits/DNA), BPM делает `REPLACE` (свою полит‑логику лидеров).  
  - При порядке MR→BPM **побеждает BPM**, MR‑черты/ДНК у этих персон пропадают.  
  - Это конфликт “по дизайну”: чинится только ручным слиянием (нужно выбрать, что важнее — MR‑flavor или BPM‑логика).

- **Слой CMF (в `Morgenrote\\cmf`) vs BPM**  
  - В твоём `vic3_mods_out\\Morgenrote` отдельно лежит `cmf\\` и там много пересечений с BPM по ключам (laws/parties/political_movements/scripted_triggers).  
  - Этот компач **целенаправленно чинит только подтверждённые “ломающие” MR↔BPM пункты выше**; CMF↔BPM слить отдельно можно, но это уже другой объём работ.
