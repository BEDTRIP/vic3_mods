### Общая идея PSC (сверено по файлам мода `PSC` и ванили `.vanillaVIC3`)

**PSC (Private Sector Construction) полностью меняет “источник” и “финансирование” строительства: вместо прямой генерации абстрактных очков строительства Construction Sector’ами, мод вводит локальные (штатные) товары-строительство + служебный “регулятор”, который конвертирует эти товары в `country_construction`, и добавляет модель разделения гос/частных трат (инвестпул ↔ бюджет).**

Ниже — что именно меняется относительно ванили (и какими файлами это сделано).

### 1) Ключевая ванильная точка, которую PSC переназначает

- **Defines** (`common/defines/PSC_defines.txt`)
  - Ванильное `NDefines.NCountry.CONSTRUCTION_CAMP_BUILDING = "building_construction_sector"` меняется на `"building_construction_regulator"`.
  - Это важно, потому что ряд интерфейсных/скриптовых мест в игре опирается на define “главного” здания строительства.

### 2) Приватизация “строительных лагерей” и новое служебное здание

- **Building groups** (`common/building_groups/zz_PSC_building_groups.txt`)
  - `bg_construction` **заменён**: теперь он дочерний от `bg_private_infrastructure` (в ванили был от `bg_public_infrastructure` и `is_government_funded = yes`).
  - Дополнительно в `bg_construction` выставлены правила авторасширения/экономии от масштаба и изменены параметры для ИИ (набор полей в PSC отличается от ванили).
  - Добавлена группа `bg_construction_regulator` (создаётся): служебная группа под регулятор (0 инфраструктуры, фиксированные темпы найма, без регионального лимита уровней).

- **Buildings** (`common/buildings/zz_PSC_construction.txt`)
  - `building_construction_sector` **REPLACE**:
    - меняются визуальные/технические параметры (например `levels_per_mesh = 5` вместо 50 в ванили, другой `background`);
    - меняется стоимость строительства сектора: `required_construction = construction_cost_very_low` (в ванили `construction_cost_construction_sector`);
    - добавлено `ownership_type = self` и `ai_nationalization_desire = 0.25` — сектор становится “приватным” по задумке мода;
    - `ai_value` переработан (скриптовая формула, включая приоритеты по ресурсам и “первый сектор”).
  - `building_construction_regulator` **REPLACE_OR_CREATE**:
    - здание не строится/не расширяется/не уменьшается вручную (`buildable/expandable/downsizeable = no`), владельца менять нельзя;
    - используется только как “конвертер” (см. PM ниже), уровни ему добавляют/удаляют скрипты.

- **History** (`common/history/buildings/PSC_buildings.txt`)
  - На старте кампании для стран с исследованной `urbanization` в **каждом штате** создаётся `building_construction_regulator = 1`.
  - Если в штате уже есть `building_construction_sector`, вызывается `set_new_point_conversion_method` (подбор конверсии по активному PM сектора).
  - Затем вызывается `set_point_conversion_method_from_tech` (подбор/обновление конверсии по технологиям страны).

### 3) “Очки строительства” через локальные товары-строительство (Local goods)

- **Goods** (`common/goods/PSC_goods.txt`)
  - Добавлены 4 новых товара: `wood_construction`, `iron_construction`, `steel_construction`, `arc_welded_construction`.
  - Важно: у всех стоит `local = yes` — это **локальные (штатные) товары**, они не “перетекают” по общему рынку как обычные goods.

- **Production methods (строительный сектор)** (`common/production_methods/zz_PSC_construction.txt`)
  - Ванильные PM `pm_wooden_buildings / pm_iron_frame_buildings / pm_steel_frame_buildings / pm_arc_welded_buildings` **REPLACE**:
    - в ванили эти PM давали `country_construction_add` напрямую;
    - в PSC они вместо этого **производят** соответствующий строительный local good (через `goods_output_*_construction_add`) и меняют структуру занятости.

- **Production methods (регулятор-конвертер)** (`common/production_methods/zz_PSC_construction.txt`)
  - Добавлены `pm_*_point_conversion` (**REPLACE_OR_CREATE**): они
    - потребляют соответствующий строительный товар (`goods_input_*_construction_add`);
    - через `country_modifiers.workforce_scaled.country_construction_add` возвращают “реальные” очки строительства в страну;
    - задают занятость бюрократами (у регулятора).

- **Production method group** (`common/production_method_groups/PSC_construction.txt`)
  - Создан `pmg_construction_regulator` со списком `pm_*_point_conversion`.

- **Modifier type definitions** (`common/modifier_type_definitions/PSC_building_modifier_types.txt`)
  - Добавлены типы модификаторов для новых goods input/output и для `building_construction_regulator_throughput_add` (чтобы эффекты корректно отображались/работали в интерфейсе/модификаторах).

### 4) Скриптовая экономика: разделение гос/частных трат и распределение по штатам

- **Script values** (`common/script_values/PSC_set_values.txt`, `PSC_construction_values.txt`, `PSC_event_values.txt`)
  - Вводится набор переменных и вычислений, которые:
    - оценивают долю “приватизации” строительства (через динамику инвестпула);
    - ограничивают госрасходы на строительство (`max_government_construction_spending`, `limited_government_construction_spending`);
    - распределяют общий спрос/траты по штатам, опираясь на **локальный выпуск** строительных товаров, базовые цены и “эффективность” (включая приближённый `calculate_sqrt`);
    - вычисляют `construction_demand_ratio` — показатель “хватает ли строительства под спрос”, который дальше используется алертом.
  - `PSC_event_values.txt` содержит календарную математику (день недели/длина месяца) для стабильного расписания перерасчётов.

- **Scripted effects** (`common/scripted_effects/PSC_scripted_effects.txt` + служебные)
  - `set_construction_point_demand` — центральный еженедельный перерасчёт: считает производство/цены/лимиты, обновляет переменные и раздаёт модификаторы штатам/регуляторам.
  - `set_construction_regulator_level` — синхронизирует уровни регулятора с уровнем `building_construction_sector` (уровни создаются/удаляются скриптом).
  - `set_new_point_conversion_method`, `set_point_conversion_method_from_tech` — выбирают правильный `pm_*_point_conversion` по активному методу сектора и/или по технологиям (urban_planning / steel_frame_buildings / arc_welding).
  - `PSC_delay_event_switch.txt` + `PSC_my_trigger_event.txt` — служебная “задержка вызова on_action” по дням внутри месяца.
  - `PSC_production_method_building_switch.txt` — создание регулятора нужного уровня с нужным PM по switch-таблице.

### 5) On_actions: ежемесячный триггер → недельные перерасчёты

- **History/global** (`common/history/global/PSC_global.txt`)
  - На старте кампании запускается on_action `set_construction_start`.

- **On actions** (`common/on_actions/PSC_on_actions.txt`)
  - На `on_monthly_pulse` запускается `set_construction_weekly_on_action`, который “раскладывает” вызовы по дням месяца:
    - `set_construction_country` (пересчёт страны) вызывается регулярно;
    - `set_spending_value` обновляет “видимое” значение расходов игрока.
  - Есть хуки на смену PM, постройку сектора и получение технологий — чтобы обновлять выбранный метод конверсии.

### 6) Модификаторы, алерты, концепты

- **Static modifiers** (`common/static_modifiers/PSC_modifiers.txt`)
  - `construction_throughput_mult`: даёт `building_construction_regulator_throughput_add` (через множитель), т.е. регулирует “мощность” конверсии в конкретном штате.
  - `country_private_construction_allocation_add`: хранит/передаёт `country_private_construction_allocation_mult`.
  - `state_construction_efficiency_increase`: даёт `state_construction_mult` (штатная эффективность строительства).

- **Alert types** (`common/alert_types/PSC_alert_types.txt`)
  - `insufficient_construction_for_investment` **REPLACE**:
    - в ванили второе условие было `investment_pool_net_income >= 40000`;
    - в PSC оно заменено на `construction_demand_ratio > define:NEconomy|BUY_SELL_DIFF_AT_MAX_FACTOR`.

- **Game concepts** (`common/game_concepts/PSC_game_concepts.txt`)
  - Добавлен `concept_construction_spending` (пустой концепт под локализацию/tooltip’ы и UI).

### 7) Интерфейс (GUI), текст-иконки и служебные scripted GUI

- **Construction panel** (`gui/PSC_construction_panel.gui`, `gui/shared/PSC_construction_spending_options.gui`)
  - Заменяется/переопределяется окно строительства: добавляется процентный регулятор `construction_spending_level` (кнопки ±, Shift/Ctrl шаги) и вывод расходов по строительству через переменную `government_construction_spending`.

- **Служебный виджет расходов** (`gui/PSC_construction_expense_widget.gui` + `gui/scripted_widgets/PSC_scripted_widgets.txt`)
  - Невидимый виджет периодически сохраняет фактические расходы на строительные товары в переменную (`psc_save_real_construction_cost`), чтобы скрипты могли отталкиваться от “реального” расхода.

- **State panel** (`gui/PSC_states_panel_buildings.gui` + `common/scripted_guis/com_local_goods_sgui.txt`)
  - Переопределён блок в панели штата, чтобы выводить список **локальных товаров** (в т.ч. строительных) через переменный список `com_local_goods` и scripted gui `com_add_local_good`.

- **Texticons** (`gui/PSC_goods_texticons.gui`)
  - Добавлены текст-иконки (`@wood_construction!` и т.п.) для новых строительных товаров.

- **Scripted GUIs (кнопки)** (`common/scripted_guis/PSC_construction_sguis.txt`)
  - `psc_button_*` меняют `construction_spending_level` (±0.01/0.05/0.1), пересчитывают лимит госстроительства.
  - `psc_save_real_construction_cost` / `psc_test_show` — служебные для обновления переменных расходов.

### 8) Графика и локализация

- **GFX** (`gfx/interface/icons/...`): добавлены иконки здания регулятора, иконки 4 строительных товаров, иконка для PM-конверсии и иконки модификаторов.
- **Localization** (`localization/*/*.yml`): строки для новых товаров/PM/модификаторов/интерфейсных элементов (несколько языков).

### Итого “по геймплею” в 1 абзац

В ванили Construction Sector напрямую даёт очки строительства и является госинфраструктурой. В PSC Construction Sector становится приватной инфраструктурой, вместо прямых очков он производит локальные строительные товары, которые затем конвертируются в `country_construction` через служебный регулятор в штатах. Общая сумма и распределение трат на строительство рассчитываются скриптами, с разделением “часть от инвестпула / часть от бюджета” и с отдельным управляемым параметром `construction_spending_level` в интерфейсе.