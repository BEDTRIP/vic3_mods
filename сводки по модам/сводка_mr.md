### Morgenrote (Morgenröte) — общая сводка, что меняет в игре (приоритет `common`)
**Версия мода**: 2.6.1a, **под 1.12.\***.  
**Зависимость**: `Community Mod Framework` (это важно для компачей: часть базовых эффектов/утилит может приходить из CMF).

В целом Morgenrote — это большой “flavor + механики через Journal Entries”: он добавляет **ветки контента по персонажам/проектам** (Arts/Science/Sports/General), новые здания/ПМ/технологии/товары, и при этом **точечно патчит ваниль** через `TRY_INJECT`/`TRY_REPLACE` и прямые переопределения.

---

### 1) Новые “проекты/персонажи” как главный каркас контента
Мод структурирован по наборам вроде **Elgar / Gaudi / Klimt / Manzoni** (искусство), **Panum / Tesla / Verrier / Mendelejew / Dubois / Agassiz / Lepsius / Theiler / Ito** (наука/медицина/экспедиции), **Curtiss / Douglas / Vikelas** (спорт/авиация) и “general” линии (**Dufour, Khaldun, Pius, SWE-NOR union** и т.п.).

Это видно по тому, что почти для каждого набора есть связка папок в `common`:  
- **`journal_entries/`** (крупные JE-цепочки)  
- **`decisions/`**  
- **`technology/technologies/`** (новые технологии и/или правки ванильных)  
- **`buildings/`, `building_groups/`**  
- **`production_methods/`, `production_method_groups/`**  
- **`scripted_effects/`, `scripted_triggers/`, `script_values/`** (логика прогресса/ивентов/ограничений)  
- плюс **traits/templates/DNA** для персонажей.

---

### 2) Технологии: добавляет новые и заметно переразводит часть ванильных
Есть собственные файлы технологий по модулям (например `panum_technologies.txt`, `mr_science_tesla_technologies.txt`, `verrier...`, `elgar...` и т.д.), и **отдельно патчи ванильных технологий**:
- `common/technology/technologies/a_vanilla_production_technologies.txt`
- `.../a_vanilla_society_technologies.txt`
- `.../a_vanilla_military_technologies.txt`

Что делает в ванили (примеры):
- **Сдвиги эпох и категорий**: например, `romanticism` делается `era_2`; `camera`/`film` переносятся в `production`.
- **Новые пререквизиты/триггеры через “unlocking_technologies”**: ванильные техи начинают требовать/ссылаться на новые техи мода (`verrier_physics_tech`, `verrier_chemistry_tech`, `panum_vaccination_tech`, `theiler_microbiology_tech`, `vikelas_sports_clubs_tech`, `curtiss_early_aviation_tech` и т.д.).
- **Правки модификаторов**: часто “снимается престиж” через отрицательный `country_prestige_mult` (т.е. фактически убирается ванильный бонус), и добавляются новые модификаторы (в т.ч. под медицину/болезни).
- **Военные техи**: например `military_aviation` переносится на более раннюю эру и перевязывается на Curtiss-ветку; `electric_telegraph` сдвигается по эре и получает AI-условия под Tesla.

Для компачей это один из главных источников конфликтов, если другой мод тоже правит ванильные технологии/эру/пререквизиты.

---

### 3) Здания и ПМ: добавляет новые и патчит/заменяет часть ванильных
**Новые здания (примеры):**
- **`building_verrier_observatory`** — уникальное/ограниченное здание под науку (требования: техи, университет/ивент, условия “только одно” и т.п.).
- **Manzoni-линия**: `building_manzoni_publishing_industry`, `building_manzoni_library`.
- **Panum-линия**: event-only здания вроде санатория/штаба Красного Креста/психбольницы (`buildable = no`, через события/переменные).

**Патчи ванильных зданий** (явный файл):  
- `common/buildings/mr_vanilla_buildings_replace.txt` делает `TRY_INJECT` в ваниль:
  - `building_government_administration`: добавляет PMG “hospital”
  - `building_university`: добавляет “university focus”
  - `building_art_academy`: добавляет фокусы/скульптуру
  - `building_railway`: добавляет “communication” (телеграф/радио)
  - патчит ряд монументов (Cristo Redentor и др.) условиями/переменными завершения

**Важно: прямые переопределения ванильных building-ключей тоже есть.** Например в `mr_sports_civil_aviation_buildings.txt` задаётся `building_airport = { ... }` (это не `TRY_INJECT`), т.е. высокорисковая точка конфликта с любыми модами, которые тоже трогают аэропорт.

**Производственные методы:**
- Есть файл `production_methods/1_mr_vanilla_inject_production_methods.txt` с `TRY_REPLACE` ванильных PM (пример: `pm_sulfite_pulping` перевязывается на `verrier_chemistry_tech`, добавляет pollution и т.д.).
- Плюс много новых PM/PMG под ветки Arts/Science/Sports.

---

### 4) Экономика потребления: новые товары + новый pop need + инжекты в ванильные нужды
**Новые goods (минимум):**
- `elgar_instruments`, `elgar_music`
- `manzoni_prints`
- `air_travel` (локальный luxury good)
- `good_uranium`

**Новый pop need:**  
- `popneed_entertainment` (в `common/pop_needs/mr_pop_needs.txt`), который потребляет `manzoni_prints`, `elgar_music`, `fine_art`, `air_travel`, `services` с весами/долями.

**Инжекты в ванильные pop needs:**
- добавляет `air_travel` в `popneed_free_movement` и `popneed_leisure`
- добавляет `fine_art` / `elgar_instruments` и т.п. в `popneed_luxury_items`

**Инжекты в buy_packages:**  
- `common/buy_packages/mr_buy_packages.txt` добавляет `popneed_entertainment` в уровни wealth (через `TRY_INJECT:wealth_*`).

---

### 5) Медицина/болезни (Panum) — отдельная большая система
Это одна из крупнейших “механических” добавок:
- `common/harvest_condition_types/panum_harvest_condition_types.txt` добавляет **набор disease conditions** (cholera, tuberculosis, typhus, yellow fever, measles, plague, etc.) с шансами, длительностью, интенсивностью, несовместимостью и модификаторами по штату.
- `common/on_actions/panum_on_actions.txt` навешивает **регулярные пульсы и события**:
  - реакции на старт harvest condition
  - `on_acquired_technology` (события при открытии медицинских техов)
  - ежемесячные/ежегодные пульсы (пандемии, eradication, прогресс систем лечения и т.п.)
  - эффекты на бой/постройку зданий (например asylum)
- Ванильные технологии получают дополнительные modifiers, которые уменьшают impact конкретных болезней (например `modern_sewerage`, `pasteurization`, `modern_nursing` и т.д.).

---

### 6) Journal Entries / Decisions: новый контент + правки ванили
**Новые JE — много**, плюс собственная “интро” JE с кнопками открытия окон:
- `je_mr_morgenrote_introduction` (кнопки “science/arts/sports window”, закрепляется игроку).

**Инжекты в ванильные JE:**
- `common/journal_entries/vanilla_je_injects.txt` добавляет события Dubois в ванильные экспедиции (Центральная Африка/Конго/Нигер и т.д.) через `on_monthly_pulse -> random_events`.

**Отключение/замена некоторых ванильных JE/decisions:**
- `common/journal_entries/Z_overwriting_je.txt`: `TRY_REPLACE:je_cristo_redentor` фактически делает JE невозможной.
- `common/decisions/vanilla_decisions.txt`: `TRY_REPLACE` отключает `revive_olympic_games_decision` и `italy_move_capital_to_rome`.

---

### 7) Военные штуки: мобилизация и ограничения
- `common/mobilization_options/mr_mobilization_option.txt` добавляет **новые мобилизационные опции** (например bicycle recon, balloon/zeppelin recon, bomber squadron, advanced weapons tiers и т.п.).
- `common/mobilization_options/vanilla_mobilization_option.txt` делает `TRY_INJECT` в ваниль:
  - ограничение химоружия, если есть модификатор “geneva convention”
  - перестановка опций по группам (air recon и т.п.)

---

### 8) Персонажи, трейты, GUI/alerts/messages
Мод добавляет:
- **много character_templates / character_traits / dna_data / genes** (включая болезни и исторических персонажей).
- **game_rules** (например шанс исторических персонажей, “tech bonus rule” и т.п.).
- **новые окна/кнопки/прогресс-бары** через `scripted_guis`, `scripted_buttons`, `scripted_progress_bars`.
- **alert_types/messages/alert_groups** для уведомлений по системам мода.

Также `common/on_actions/mr_on_actions.txt` на старте кампании **создаёт артистов/учёных** в странах в зависимости от game rules (исторические/случайные), и включает AI-веса/вероятности через `mr_ai_script_values.txt`.

---

### Самое важное для компачей (где ждать конфликты)
- **`common/technology/technologies/a_vanilla_*`**: правки ванильных технологий (эра/категория/пререквизиты/модификаторы).
- **`common/buildings/`**:
  - `mr_vanilla_buildings_replace.txt` (инжекты в ванильные здания/монументы),
  - и особенно файлы, где **переопределяются ванильные building-ключи напрямую** (пример: `building_airport`).
- **`common/production_methods/1_mr_vanilla_inject_production_methods.txt`**: `TRY_REPLACE` ванильных PM (перевязка на новые техи/эффекты).
- **`common/pop_needs/` + `common/buy_packages/`**: новая нужда + инжекты в ванильные нужды/пакеты.
- **`common/journal_entries/vanilla_je_injects.txt` и `Z_overwriting_je.txt`**, **`common/decisions/vanilla_decisions.txt`**, **`common/mobilization_options/vanilla_mobilization_option.txt`**: явные изменения ванильных JE/решений/мобилизации.
