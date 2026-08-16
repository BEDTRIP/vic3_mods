### Morgenrote (Morgenröte) — общая сводка, что меняет в игре (приоритет `common/`)

**Актуальная версия**: **2.8.3e «Mitsopoulos»**, **под 1.13.\*** (коммит `Morgenrote 15.08.2026`).  
Steam ID: `2889925770`.  
**Зависимость**: только **`Community Mod Framework`** (CMF). ETF/Dence UI в metadata **нет**, но окна мода интегрируются с topbar через CMF.

Morgenrote — большой «flavor + механики через Journal Entries»: ветки по персонажам/проектам (Arts/Science/Sports/General), новые здания/ПМ/технологии/товары, точечные патчи ванили через `TRY_INJECT`/`TRY_REPLACE` и прямые переопределения.

---

### 1) Новые «проекты/персонажи» как каркас контента
Наборы **Elgar / Gaudi / Klimt / Manzoni** (искусство), **Panum / Tesla / Verrier / Mendelejew / Dubois / Agassiz / Lepsius / Theiler / Ito / Andersson / Curie** (наука), **Curtiss / Douglas / Vikelas** (спорт/авиация), general-линии (**Dufour, Khaldun, Pius, SWE-NOR union**, Rapanui и т.п.).

Для каждого набора типично: `journal_entries/`, `decisions/`, `technology/`, `buildings/`, `production_methods/`, `scripted_effects/triggers/values/`, traits/templates/DNA.

---

### 2) Технологии
- Собственные tech-файлы по модулям.
- Патчи ванили: `a_vanilla_production_technologies.txt`, `a_vanilla_society_technologies.txt`, `a_vanilla_military_technologies.txt`.
- Сдвиги эр, новые пререквизиты через `unlocking_technologies`, правки модификаторов, военная/aviation-ветки.

---

### 3) Здания и ПМ
**Новые здания (актуальный список — 62 ключа в `common/buildings/`):**

| Линия | Примеры |
|---|---|
| Arts | `building_elgar_opera`, `building_instrument_workshops`, Gaudi-монументы/городские постройки, `building_klimt_gallery`, Manzoni |
| Science | `building_verrier_observatory`, Panum, Dubois, Mendelejew, Agassiz, **Andersson** (`building_andersson_institute`), **Curie** (`building_curie_facility`, `building_curie_reactor`), **Lepsius** (+ `building_lepsius_needle`, `building_lepsius_obelisk`), `building_uranium_mine` |
| Sports | Vikelas, Douglas, `building_airport` |
| Decorative | `building_mr_lyme_regis_cliff`, `building_mr_steamboat_rock`, Rapanui moai |

**Удалено с 2.6.x:** `building_gaudi_sagrada` (больше нет в моде).

**Патчи ванили:** `mr_vanilla_buildings_replace.txt` (railway, university, art_academy, monuments…).  
**Прямые переопределения:** например `building_airport = { ... }` — высокий риск конфликта.

**PM:** `1_mr_vanilla_inject_production_methods.txt` (`TRY_REPLACE` ванильных PM) + новые PM/PMG под ветки.

---

### 4) Экономика потребления
**Goods Morgenrote** (без новых с 2.6.x): `elgar_instruments`, `elgar_music`, `manzoni_prints`, `air_travel`, `good_uranium`.

**Pop needs:** `popneed_entertainment` + инжекты в `popneed_free_movement`, `popneed_leisure`, `popneed_luxury_items`.  
**Buy packages:** `mr_buy_packages.txt` — `TRY_INJECT` в `wealth_*` (конфликт с E&F на уровне ключей).

---

### 5) Agassiz / геология — **сильно переработано в 2.8.x**
Старая система отдельных JE на каждую руду (`je_agassiz_find_coal_project`, `je_agassiz_find_silver_project`, …) **заменена** на единый проект:
- **`je_agassiz_improve_mines_project`**
- GUI: `mr_geologist_improve_mines_button_effect`, окно выбора шахт через variable lists
- Триггеры:
  - `agassiz_can_find_new_vein_trigger` — любая шахта `bg_mining` без модификатора
  - `agassiz_mine_valid_for_improvement_trigger` — то же для выбора целей

**Важно для E&F:** `building_silver_mine` в E&F использует **`bg_silver_mining`**, поэтому **не попадает** в новые agassiz-триггеры Morgenrote без компача.

---

### 6) Tesla / инженерные проекты — расширено
- Новые/переработанные JE (irrigation, power plants, airports, submarine cables, aviation…).
- Триггеры целей:
  - `tesla_construction_sector_valid_for_improvement_trigger` — сейчас только `building_construction_sector`
  - `tesla_building_valid_for_mechanical_improvement_trigger` — исключает service/urban/power/government/infrastructure/military/subsistence/monuments/elgar_opera; добавлено **`bg_subsistence_ranching`**

---

### 7) Прочие крупные изменения 2.6 → 2.8
- **Andersson** — антропология/этнология (institute, fossils, JE-цепочки).
- **Curie** — ядерная ветка (facility, reactor; uranium mine уже был).
- **Lepsius** — расширенные экспедиции/монументы (needle, obelisk).
- **Theiler** — очень большое расширение биологии/сельского хозяйства.
- **GUI**: новые панели science/arts, topbar elements, sorter/building chooser windows.
- **`00_mr_compatibility_triggers.txt`** — заглушки для сторонних модов (CMF, WCR, Tech&Res…); **E&F там нет**.

---

### 8) Journal Entries / Decisions / Military
- Много новых/переписанных JE (Elgar, Gaudi, Tesla, Theiler, Andersson…).
- `vanilla_je_injects.txt`, `Z_overwriting_je.txt`, `vanilla_decisions.txt`.
- Mobilization options: новые + инжекты в ваниль.

---

### Самое важное для компачей (где ждать конфликты)
- **`common/technology/technologies/a_vanilla_*`**
- **`common/buildings/`** — инжекты + прямые overrides (`building_airport`, `building_railway`)
- **`common/production_methods/1_mr_vanilla_inject_production_methods.txt`**
- **`common/pop_needs/` + `common/buy_packages/`**
- **`common/journal_entries/`**, **`decisions/`**, **`mobilization_options/`**
- **`common/on_actions/*`** — пересечение pulse-хуков с E&F
- **Agassiz/Tesla scripted_triggers** — точки интеграции с E&F-зданиями
