## Шапка

**Версии в репозитории**: `Tech Res 13.05.2026` (`t&r`, metadata `1.6'`, `1.13.*`),
`KAI 24.07.2026` (`kai`, metadata `7.5`, `1.13.*`). Модуль `cmf` лежит отдельно —
`vic3_mods_out/_cmf` (`CMF 13.08.2026`).
**Сверено с файлами: 21.08.2026.**

### Что уточнено 21.08.2026 (разбор E&F + T&R)

- **Товаров T&R добавляет 39** поверх ванили: `advancedores, ai_systems, alloys,
  aluminium, androids, batteries, bauxite, business_data, civil_planes, commonores,
  computer, copper, copperwires, cosmetics, electroniccomponents, elgar_instruments,
  elgar_music, gas, global_electricity, good_uranium, heavy_fuel, homeappliances,
  interactive_entertainment, light_fuel, lubricant, manzoni_prints, on_demand_goods,
  organized_data, pharmaceuticals, plastics, processors, rare_earths, raw_data,
  robotics, softwares, space_assets, telecommunications, televisions, water`.
  С Morgenröte пересекаются четыре (`elgar_*`, `manzoni_prints`, `good_uranium`),
  то есть поверх MR это +35. **Ваниль 53 + E&F с хотфиксом 65 + T&R 39 = 157 при
  потолке 128** — E&F и T&R вместе не запускаются без дополнительной резки.
- **Новое в версии 13.05 относительно предыдущей**: здания
  `building_computer_assembly_plant`, `building_fusion_power_plant`,
  `building_power_grid_station`; группа `pmg_power_transmission`
  (`pm_direct_current` / `pm_half_current` / `pm_alternating_current`) в
  `building_power_plant` — законо-зависимая витрина `lawgroup_national_electric_system`,
  сами PM модификаторов не несут; `pmg_data_optimization_light_industry` с
  электростанции **снят**; у `building_automotive_industry` дата-оптимизация
  переведена на `pmg_data_optimization_heavy_industry_algorithmic_dispatch`.
- **`REPLACE:` ванильных зданий у T&R ровно три**: `building_automotive_industry`,
  `building_synthetics_plant`, `building_power_plant` (`ztr_vanilla_modified_buildings.txt`).
  Всё остальное — `INJECT:` (17 зданий там же + 30 в `ztr_vanilla_optimization_buildings.txt`)
  и `REPLACE_OR_CREATE:` для семи зданий Morgenröte. Золото
  (`building_gold_mine`, `building_gold_field`) T&R не трогает вообще.
- **Законы шахт работают поимённо, не по `building_group`**:
  `law_polluting_mining_banned` сносит `building_coal_mine`, `building_lead_mine`,
  `building_sulfur_mine`; `possible`-фильтры в зданиях тоже перечисляют законы
  поимённо. Чужие шахты в дочерних группах `bg_mining` (например `bg_silver_mining`
  у E&F, `bg_uranium_mining`, `bg_water_farms`) под запреты не попадают — компач не нужен.
- **`common/defines/NEconomy`**: T&R задаёт один ключ, KAI — ноль. С тремя ключами
  E&F пересечения нет.
- **`common/buy_packages/`**: T&R патчит `wealth_10…wealth_99` через `TRY_INJECT:`
  (90 записей) — уживается с `INJECT:` кого угодно.
- **Kuromi's AI**: с E&F пересечение ключей, loc-ключей, id событий и путей файлов —
  нулевое. Правит `ai_strategies`, `common/defines/kai_ai.txt` и `ai_weight` техов.

---

