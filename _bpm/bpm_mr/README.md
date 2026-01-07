### Что нашёл по конфликтам MR ↔ BPM (порядок: **MR → BPM**, BPM последний)

Я прогнал первичный скан и затем перепроверил руками “опасные” места. Итоги и артефакты лежат в `bpm_mr/`.

### Отчёты (автосканы)

- **MR (реальный корень: `.Morgenrote/morgen`) vs BPM**: `bpm_mr/conflicts_morgen_vs_bpm_report.md`
- **CMF (из пакета MR) vs BPM**: `bpm_mr/conflicts_cmf_vs_bpm_report.md` (важно, потому что MR зависит от CMF)

### Подтверждённые реальные конфликты MR ↔ BPM

- **Жёсткое перетирание файла**: `common/achievement_groups.txt`  
При MR→BPM файл BPM полностью заменяет MR и в итоге **пропадают MR achievement groups** (и у BPM файл ещё и “укорочен” относительно ванили).
- **Технология `mass_propaganda**`:  
MR делает `TRY_INJECT` (добавляет prereq `elgar_mass_culture_tech`), а BPM делает `REPLACE` (prereq `political_agitation` + `film`) — при MR→BPM MR-инжект **теряется**.
- *`scripted_trigger` “MR активен”**: `morgenrote_is_active`  
MR задаёт `always = yes`, но BPM в своём compatibility-файле задаёт `always = no` и при MR→BPM **перетирает** MR → триггер становится ложным.

### Потенциально важный конфликт (по контенту, нужно решить приоритет)

- *`character_templates` для шведских правителей** `swe_*_bernadotte_template`)  
У MR там `TRY_REPLACE` с **mr-traits/DNA**, у BPM `REPLACE` со своей логикой — при MR→BPM BPM **гарантированно выигрывает**, MR-черты/ДНК для этих персон пропадут.

### Сводка “что чинить” для компача

Я оформил это отдельной понятной запиской: *`bpm_mr/conflicts_summary_mr_bpm.md`** (там же — что именно предлагается делать в компаче по каждому пункту).

Дальше можем сразу переходить к сборке компача в `bpm_mr/`, начиная с `achievement_groups.txt`, `morgenrote_is_active`, и `mass_propaganda`.