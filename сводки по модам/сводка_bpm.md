### Общая сводка: что меняет **Better Politics Mod (BPM)** относительно ванили (сверено по файлам `.BPM` и `..vanillaVIC3/game`, фокус на `common/`)

**BPM (Better Politics Mod)** — это большой оверлей на политику: он добавляет и “расщепляет” политические силы на отдельные **идеологические IG/партии/движения**, переписывает значимые куски **законов и закон‑групп**, расширяет **лобби** и их логику, вводит **кабинет/главу правительства** как отдельную механику, и подкрепляет всё большим количеством событий/JE и интерфейсных правок в политических панелях.

Ниже — что именно сделано файлами мода (и какие зоны наиболее конфликтные для компачей).

### 1) Interest Groups: новые IG + перепрошивка ванильных IG под “идеологические фракции”

- **Новые IG‑типы** (пример): `ig_anarchists` в `common/interest_groups/zzzzz_BPM_anarchists.txt` (и аналогичные файлы для “liberals / fascists / socialists / reactionaries / …”).
  - Эти IG имеют собственную логику **pop_potential/pop_weight**, привязки к технологиям (например, анархисты учитывают `anarchism`, `labor_movement`, `egalitarianism`) и наборы идеологий для персонажей.
- **Переписаны ванильные IG через `REPLACE:`** (пример): `REPLACE:ig_armed_forces` в `common/interest_groups/zzzz_armed_forces.txt`.
  - Включает динамическое **переименование/варианты** (например, “Samurai” для Японии, “National Guard” для Франции) и скриптовую инициализацию/хуки, которые BPM использует как “ранний” старт своих систем.

### 1.5) Defines: правки базовых констант политической модели и поведения AI

- `common/defines/BPM_defines.txt` меняет блоки `NAI` и `NPolitics`:
  - поведение AI при реформе правительства/законов, веса одобряемых/неодобряемых IG;
  - стоимость bolster/suppress IG, пороги “powerful/marginal” IG;
  - множество констант по политическим движениям (минимальная поддержка, радикализм, вклад грамотности, и т.д.).

### 2) Законы: крупная переработка law_groups + новые lawgroup’ы + отдельные новые законы

- **Law groups** (`common/law_groups/`):
  - BPM **REPLACE’ит** базовые ванильные группы (пример: `REPLACE:lawgroup_distribution_of_power` в `common/law_groups/BPM_laws.txt`) и меняет параметры вроде `base_enactment_days`, вероятности движений и т.п.
  - Добавляет новые группы законов, которых в ванили нет (например: `lawgroup_executive_principles`, `lawgroup_legislative_principles`, `lawgroup_party_laws`, `lawgroup_foreign_policy`, `lawgroup_centralization`, и др.).
  - Добавляет отдельные **repeatable‑law groups** (`common/law_groups/BPM_repeatable_laws.txt`): `lawgroup_repeatable_*` (политика/религия/национальность/экономика/культура/армия).
- **Сами законы** (`common/laws/`, 31 файл):
  - Много ванильных законов переписаны через `REPLACE:` (пример: `REPLACE:law_autocracy` в `common/laws/BPM_distribution_of_power.txt`).
  - Есть новые законы (пример: `law_military_junta` в `common/laws/BPM_distribution_of_power.txt`).
  - Ванильный `law_single_party_state` **отключён/спрятан** (`is_visible = { always = no }`) и помечен как “replaced by BPM's bespoke system” (см. тот же файл) — BPM ведёт однопартийность/партии своим способом.

### 2.2) Government types: новые формы правления и переопределения “особых” режимов

- `common/government_types/` добавляет множество типов правительства, завязанных на новые/переписанные законы:
  - новые варианты (пример): `gov_supreme_parliament`, `gov_ceremonial_kingdom`, `gov_ceremonial_empire`, `gov_semi_presidential_democracy` в `common/government_types/bpm_types.txt`;
  - отдельные ветки под синдикализм/анархию/технократию (пример: `gov_anarchist_syndicalism`, `gov_syndicalism_*` в `common/government_types/bpm_types_syndicalism.txt`);
  - переопределения ванильных “особых” режимов через `REPLACE:` (пример: `REPLACE:gov_shogunate` в `common/government_types/bpm_types_override.txt`).

### 2.5) Amendments: система “поправок к законам” (конституционные/правовые надстройки)

- `common/amendments/` добавляет отдельный слой **amendment’ов**, которые “прикрепляются” к конкретным законам:
  - структура/поля описаны в `common/amendments/amendments.md` (allowed laws, modifiers, institution modifiers, триггеры `possible`, логика “спонсорства” `would_sponsor` и т.д.);
  - примеры поправок: `bpm_amendment_artisanal_economy` в `common/amendments/bpm_france_amendments.txt` (условия/спонсоры/неотменяемость и т.п.).

### 3) Институты: новые “политические” institutions для управления/модификаторов

- `common/institutions/bpm_institutions.txt` добавляет (или переопределяет визуально/логически) такие институты как:
  - `institution_centralization`, `institution_suffrage`, `institution_culture`, `institution_diplomacy` (у дипломатии есть модификатор `country_influence_mult`).
- `common/institutions/00_bpm_institutions.txt`: `institution_economy`.

### 3.5) Технологии: BPM переопределяет ряд society‑tech под новые институты/идеологии

- `common/technology/technologies/*bpm*.txt` содержит `REPLACE:` на ванильные технологии (примеры: `centralization`, `currency_standards`, `democracy`, `identification_documents`, `corporatism`, `anarchism`):
  - добавляются/меняются модификаторы, в т.ч. на **max investment** для новых институтов (`institution_centralization`, `institution_economy`, `institution_suffrage`);
  - в `on_researched` местами есть скриптовые корректировки идеологий IG (пример: `corporatism`).

### 4) Партии и выборы: переписанные партии + “polhook” (снятие результатов по партиям)

- **Parties** (`common/parties/`, 13 файлов):
  - Пример: `REPLACE:anarchist_party` в `common/parties/zzzz_anarchist_party.txt`:
    - динамическое имя партии по стране/культуре;
    - сложная логика доступности (бан партий, условия для IG);
    - “липкость”/лояльность и учёт “party establishment”.
- **Polhook (интерфейс + скрипты)**:
  - Скрипты: `common/scripted_effects/bpm_polhook_effects.txt` сохраняют результаты голосования по партиям в переменные `bpm_party_*_voting_power`.
  - On actions: `common/on_actions/000_bpm_polhook.txt` заводит хук на конец кампании/выборов.
  - GUI: `gui/polhook_main.gui`, `gui/polhook_afterthedark.gui` + `common/scripted_guis/bpm_polhook_gui.txt`.

### 5) Political movements и lobbies: расширение идеологических движений и “умные” веса лобби

- **Political movements** (`common/political_movements/`):
  - BPM переписывает/добавляет большое количество идеологических движений, включая **country‑specific** (пример: `REPLACE:movement_orleanist` и др. в `common/political_movements/04_country_specific_ideological_movements.txt`).
  - Триггеры и веса поддержки сильно детализированы (страта/поп‑типы/урбанизация/грамотность/законы/идеологии/болстер‑саппресс).
- **Political lobbies** (`common/political_lobbies/bpm_political_lobbies.txt`):
  - `REPLACE:lobby_pro_country`, `REPLACE:lobby_anti_country`, и варианты для overlord’а.
  - В `join_weight` учитываются **законы, культура, религия, идеологии правящих IG, ранги, отношения, участие в power bloc, funding lobbies** и т.п.

### 6) Кабинет и “глава правительства”: отдельная механика назначения (CAB)

- В `common/script_values/bpm_CAB_values.txt` и множестве `common/scripted_effects/BPM_CAB_*` реализована система:
  - расчёта “скилла” персонажей по трейтом (пример: `bpm_traits_skill_level`);
  - формирования/очистки пулов кандидатов (в т.ч. через “void”‑механику);
  - выбора/назначения министров, взаимодействия с институтами и мандатами.
- UI/скриптовые кнопки для кабинета: `common/scripted_guis/BPM_CAB_effect_gui.txt` (+ связанная кастом‑локализация `common/customizable_localization/bpm_CAB_interface.txt`).

### 7) Контент: события/JE/скриптовая “платформа”

- **Events** (`events/`, 157 файлов):
  - Определений событий (`X = { ... }`) в моде: **925**.
  - Из них **~443 совпадают с ванильными ключами событий** (то есть BPM фактически **переопределяет** множество ванильных event definition’ов по ключу, даже если файлы лежат под другими путями).
  - Ещё **~482 ключа событий** — новые относительно ванили.
- **Journal entries** (`common/journal_entries/`, 54 файла): множество новых/переработанных JE под политические цепочки.
- **Script layer**: большой объём `script_values/`, `scripted_triggers/`, `scripted_effects/`, `static_modifiers/`, `on_actions/` — это фундамент BPM (переменные стабильности/мандатов/лояльности партий, “активация” IG, вычисления весов и т.д.).

### 8) История (стартовые правки): страны/персонажи/движения/лобби

- `common/history/countries/` — **7 файлов совпадают по пути с ванилью** (BRZ/CHI/FRA/USA и др.), т.е. BPM меняет стартовые настройки этих стран.
- `common/history/characters/` — **часть файлов совпадает по пути с ванилью**, плюс есть дополнительные “bpm_*” персонажные файлы.
- Есть точечные override’ы по пути для `common/history/lobbies` и `common/history/political_movements`.

### 9) Интерфейс/графика/локализация (кратко)

- **GUI** (`gui/`): BPM добавляет/меняет политические панели (`BPM_country_politics_panel.gui`, `BPM_politics_panel_*`), а также outliner‑типы и текст‑иконки.
- **GFX** (`gfx/`): много новых иконок/артов под новые IG/законы/институты/панели.
- **Localization** (`localization/`): очень большой пакет локализаций на множество языков (в т.ч. `russian/`).

### Для компачей: где почти наверняка будут конфликты

- **`common/laws/*` и `common/law_groups/*`**: BPM массово `REPLACE`‑ит ванильные законы/группы и добавляет новые.
- **`common/interest_groups/*`, `common/ideologies/*`, `common/parties/*`**: новые IG/идеологии/партии и одновременные переопределения ванильных по ключам.
- **`common/political_movements/*`, `common/political_lobbies/*`**: много `REPLACE:` на ванильные определения.
- **`events/*`**: огромная зона конфликтов, потому что **сотни ванильных event definition keys переопределены по ключу**.
- **`common/history/*`**: если другой мод тоже трогает стартовые настройки (особенно BRZ/CHI/FRA/USA), будут прямые path‑конфликты.
- **`gui/*`**: политические панели/выборы/кабинет — частый источник UI‑конфликтов.

