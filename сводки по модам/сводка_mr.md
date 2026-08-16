### Morgenröte (Morgenroete) — общая сводка, что меняет в игре (приоритет `common/`)

**Версия**: **2.8.3e «Mitsopoulos»**, `supported_game_version` = **1.13.\*** (коммит `Morgenrote 15.08.2026`).
Steam ID: `2889925770`.
**Зависимость в metadata — ровно одна**: `Community Mod Framework` (версия `1.*`). ETF/Dence UI в relationships нет, окна мода идут через CMF.
**Сверено с файлами: 16.08.2026.**

Morgenröte — большой «flavor + механики через Journal Entries»: ветки по персонажам/проектам (Arts / Science / Sports / General), новые здания/ПМ/технологии/товары. Мод **почти целиком аддитивен**: `TRY_INJECT` в ваниль, а полных `REPLACE:` во всём `common/` — единицы (см. ниже).

**Масштаб**: 420 journal entries · 62 своих здания · 264 PM · 112 PMG · 89 ключей технологий · 29 файлов on_actions.

---

### 1) Новые «проекты/персонажи» как каркас контента

**Arts**: Elgar, Gaudi, Klimt, Manzoni, artists.
**Science**: Panum, Tesla, Verrier, Mendelejew, Dubois, Agassiz, Lepsius, Theiler, Ito, **Andersson**, **Curie**, Roy, academics.
**Sports**: Curtiss, Douglas, Vikelas, athletes.
**General**: Dufour, Khaldun, Pius, SWE-NOR union, Rapanui, nationalization, Matsuura Japan, PBI (publishing industry).

Для каждого набора типично: `journal_entries/`, `decisions/`, `technology/`, `buildings/`, `production_methods/`, `scripted_effects/triggers/values/`, traits/templates/DNA, отдельный файл `on_actions`.

---

### 2) Технологии

89 ключей. Собственные tech-файлы по модулям + три файла патчей ванили: `a_vanilla_production_technologies.txt`, `a_vanilla_society_technologies.txt`, `a_vanilla_military_technologies.txt`.

Патчи ванили — почти все `TRY_INJECT:` (electric_telegraph, wargaming, zeppelins, carrier_tech, modern_nursing, atmospheric_engine, chemical_bleaching, improved_fertilizer, camera, film, electrical_generation, combustion_engine, pasteurization, pneumatic_tools, realism, mass_propaganda, organized_sports, modern_sewerage, malaria_prevention, civilizing_mission…).

**`TRY_REPLACE:` только 4 ванильных теха**: `military_aviation`, `romanticism`, `pharmaceuticals`, `antibiotics`.

> С E&F пересечений нет: E&F `REPLACE:`-ит 10 финансовых техов (`banking`, `central_banking`, `joint_stock_companies` и т.д.), Morgenröte их не трогает.

---

### 3) Здания и ПМ

**Собственных зданий — ровно 62** (`common/buildings/`, 19 файлов):

| Линия | Здания |
|---|---|
| Arts / Elgar | `building_elgar_opera` (`bg_opera`), `building_instrument_workshops` (`bg_light_industry`) |
| Arts / Gaudi | 31 постройка: 16 в `bg_monuments`, 15 в `bg_architect` |
| Arts / Klimt | `building_klimt_gallery` (`bg_government`) |
| Arts / Manzoni | `building_manzoni_library` (`bg_technology`), `building_manzoni_publishing_industry` (`bg_light_industry`) |
| Science | `building_agassiz_volcano_observatory`, `building_andersson_institute`, `building_curie_facility`, `building_curie_reactor`, `building_verrier_observatory`, `building_lepsius_archaeological_museum`, `building_panum_asylum`, `building_panum_red_cross`, `building_panum_tuberculosis_sanatorium` (все `bg_technology`); `building_lepsius_needle`, `building_lepsius_obelisk` (`bg_monuments`); `building_dubois_zoo` (`bg_government`), `building_dubois_national_park` (`bg_dubois_national_park`); `building_mendelejew_hydrogenation_plants`, `building_mendelejew_synthetic_rubber_factory` (`bg_heavy_industry`); `building_uranium_mine` (`bg_mining`) |
| Sports | `building_douglas_alpine_club` (`bg_technology`); `building_vikelas_aiacr`, `_circuit`, `_fifa`, `_ioc`, `_sports` (`bg_bureaucracy`); `building_airport` (`bg_private_infrastructure`) |
| Decorative | `building_mr_lyme_regis_cliff`, `building_mr_steamboat_rock` (`bg_monuments_hidden`), `building_rapanui_moai` (`bg_monuments`) |

**Изменения списка с 2.6.x:**
- **добавлены**: `building_andersson_institute`, `building_curie_facility`, `building_curie_reactor`, `building_lepsius_needle`, `building_lepsius_obelisk`;
- **удалён**: `building_gaudi_sagrada`.

> Все пять новых — `can_build_private = { always = no }`, то есть чисто государственные.

**Собственные группы зданий** (важно для чужих триггеров — все с родителями):

| Группа | `parent_group` |
|---|---|
| `bg_opera` | `bg_arts` → `bg_urban_facilities` |
| `bg_architect` | `bg_public_infrastructure` → `bg_infrastructure` |
| `bg_uranium_mining` | `bg_mining` |
| `bg_dubois_national_park` | `bg_government` |

**Патчи ванильных зданий** (`mr_vanilla_buildings_replace.txt`, вопреки названию):

- `TRY_INJECT:` — `building_government_administration`, `building_university`, `building_art_academy`, `building_railway`, `building_cristo_redentor`, `building_eiffel_tower`, `building_statue_of_liberty`, `building_big_ben`, `building_machu_picchu`;
- **`REPLACE:`** — только `building_sagrada_familia_cathedral_1/2/3` (три стадии переписаны под фасады: Nativity / Passion / Glory).

> `building_airport` — **собственное** здание Morgenröte, а не переопределение ванили. Конфликтовать по нему не с чем.

**PM:** `1_mr_vanilla_inject_production_methods.txt` + `mr_vanilla_production_method_groups_inject.txt` — инжекты в ванильные PM/PMG. Единственный `TRY_REPLACE:` — `pm_sulfite_pulping`.

---

### 4) Экономика потребления

**Goods Morgenröte — 5** (без новых с 2.6.x):

| Товар | category | Примечание |
|---|---|---|
| `air_travel` | luxury | `local = yes`, cost 125 |
| `elgar_instruments` | staple | cost 40 |
| `elgar_music` | luxury | **`tradeable = no`**, cost 80 |
| `manzoni_prints` | staple | cost 60 |
| `good_uranium` | industrial | cost 40 |

**Pop needs** (`common/pop_needs/mr_pop_needs.txt`):
- новая `popneed_entertainment` (manzoni_prints, elgar_music, fine_art, air_travel, services);
- `TRY_INJECT:` в `popneed_free_movement`, `popneed_leisure`, `popneed_luxury_items`.

**Buy packages:** `mr_buy_packages.txt` — **`TRY_INJECT:wealth_10` … `wealth_99`**, добавляет `popneed_entertainment`.

> С E&F **конфликта нет**: E&F использует `INJECT:` в те же `wealth_*`, оба мода дописывают свои потребности. Скан «дублирующихся ключей» показывает 90 совпадений, но это ложное срабатывание — он не смотрит на префикс операции.

---

### 5) Agassiz / геология — переработано в 2.8.x

Старая система отдельных JE на каждую руду **выведена из обращения**:

- `je_agassiz_find_coal/iron/lead/sulfur/gold/uranium_project` **всё ещё определены** в `mr_science_agassiz_journal_entries.txt` и упоминаются в `agassiz_geologist_project_active_trigger`, но **ни один эффект их больше не выдаёт** — легаси;
- отдельные `agassiz_can_find_<ore>_vein_trigger` тоже остались, но снаружи файла триггеров не используются;
- фактически работают два проекта: **`je_agassiz_improve_mines_project`** (шахты) и `je_agassiz_find_oil_project` (нефть).

Новый контур:
- GUI: `MR_general_sorter_building_sguis.txt` — окно выбора шахт через variable lists, кнопка `je_agassiz_improve_mines_project_change_list_button`;
- триггеры:
  - `agassiz_can_find_new_vein_trigger` — `any_scope_building { level > 0 · is_building_group = bg_mining · NOT has_modifier = agassiz_building_production_mult_modifier }`
  - `agassiz_mine_valid_for_improvement_trigger` — то же, но в скоупе здания
  - `agassiz_oil_rig_valid_for_improvement_trigger` — `building_oil_rig`
- AI использует те же триггеры (`mr_ai_geology_scripted_effects.txt`).

> **Про E&F silver mine.** `is_building_group` в Vic3 проверяет цепочку родителей (доказательство в ванили 1.13: `is_building_group = bg_military # Derives from barracks and naval bases`). У E&F `bg_silver_mining` задан `parent_group = bg_mining`, поэтому `building_silver_mine` **уже попадает** в «Improve Mining» и в выбор целей — **компач тут не нужен**. Старый патч с отдельным `je_agassiz_find_silver_project` теперь только ломает GUI и логику занятости геолога.

Мелкая нестыковка самого мода: `agassiz_geologist_project_active_trigger` перечисляет мёртвые пер-рудные JE и **не** содержит `je_agassiz_improve_mines_project`, а `agassiz_geologist_project_with_busy_geologist_active_trigger` — наоборот, содержит только его.

---

### 6) Tesla / инженерные проекты

Триггеры целей (`mr_science_tesla_scripted_triggers.txt`):

| Триггер | Что берёт |
|---|---|
| `tesla_construction_sector_valid_for_improvement_trigger` | только `building_construction_sector` |
| `tesla_building_valid_for_mechanical_improvement_trigger` | всё, кроме `NOR`: `bg_service`, `bg_urban_facilities`, `bg_power`, `bg_government`, `bg_infrastructure`, `bg_military`, `bg_subsistence_agriculture`, **`bg_subsistence_ranching`** (новое в 2.8), `building_elgar_opera`, `bg_monuments`, `bg_monuments_hidden` |
| `tesla_railway_building_valid_for_civil_improvement_trigger` | `building_railway` |
| `tesla_power_plant_valid_for_improvement_trigger` | `building_power_plant` |

> Для компача с E&F: четыре группы E&F (`bg_bank`, `bg_financial_centre`, `bg_national_stockpile`, `bg_ef_private_construction`) **не имеют `parent_group`**, поэтому исключения по `bg_government`/`bg_urban_facilities` их не ловят — надо дописывать явно. Плюс разрешить `building_ef_private_construction` в construction-триггер.

---

### 7) Прочие крупные изменения 2.6 → 2.8

- **Andersson** — антропология/этнология (institute, fossils, JE-цепочки).
- **Curie** — ядерная ветка (facility, reactor; uranium mine был раньше).
- **Lepsius** — расширенные экспедиции/монументы (needle, obelisk).
- **Theiler** — очень большое расширение биологии/сельского хозяйства; свои триггеры по `bg_agriculture`/`bg_ranching`/`bg_plantations`.
- **GUI**: панели science/arts, topbar-элементы, универсальное окно-сортировщик зданий.

---

### 8) Journal Entries / Decisions / Military / совместимость

- 420 JE в 30 файлах; `vanilla_je_injects.txt` и `Z_overwriting_je.txt`.
- Полных `REPLACE:` среди JE — два: `je_sagrada_familia`, `je_cristo_redentor`.
- `TRY_REPLACE:` в остальном `common/`: `revive_olympic_games_decision`, `italy_move_capital_to_rome`, `mobilization_option_chemical_weapons`, несколько character templates (Einstein, Mark Twain, Bernadotte).
- Mobilization options: новые + инжекты в ваниль.
- **`REPLACE_OR_CREATE:morgenrote_is_active`** (`zz_mr_is_active_trigger.txt`) — мод отдаёт наружу триггер собственного присутствия, удобно для компачей.
- **`00_mr_compatibility_triggers.txt`** — заглушки `always = no` для CMF, WCR, ECCHI Redux, Basileia, IEX, JKFP, Tech&Res. **E&F там нет** — нативной совместимости с E&F мод не завёз.

---

### Самое важное для компачей (где ждать конфликты)

- **`common/buildings/`** — 9 `TRY_INJECT:` в ваниль (аддитивно) + `REPLACE:` трёх стадий Sagrada Família (единственный реальный overwrite здания).
- **`common/technology/technologies/a_vanilla_*`** — 4 `TRY_REPLACE:`, остальное инжекты.
- **`common/production_methods/1_mr_vanilla_inject_production_methods.txt`** — инжекты + `TRY_REPLACE:pm_sulfite_pulping`.
- **`common/pop_needs/` + `common/buy_packages/`** — только `TRY_INJECT`, с E&F не конфликтует.
- **`common/on_actions/*`** — 29 файлов, все аддитивные; пересечение пульсов с E&F безопасно.
- **Agassiz / Tesla scripted_triggers** — единственные места, где чужие здания надо явно вписывать (и то Agassiz теперь сам справляется через иерархию `bg_mining`).
- **`common/journal_entries/Z_overwriting_je.txt`** — смотреть при конфликте JE.
