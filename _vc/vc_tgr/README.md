## vc_tgr — ComPatch: The Great Revision + Victorian Century

### Отчёты

- **Сырой (эвристика)**: `conflicts_tgr_vs_vc_report.md`
- **Перепроверенный/с приоритетами**: `conflicts_tgr_vs_vc_report_reviewed.md`

### Ключевые результаты (самое важное)

- **Жёсткие конфликты по одинаковым путям файлов (12 шт.)** — VC полностью перезапишет TGR:
  - `common/decisions/manifest_destiny.txt` (у VC это `#nothing`, т.е. убивает решение TGR)
  - `common/history/countries/*` (6 стран: AUS/BRZ/CHI/FRA/GBR/TUR)
  - `common/parties/*` (3 файла)
  - `map_data/state_regions/00_west_europe.txt`, `11_east_asia.txt`
- **Жёсткие конфликты по одинаковым ID в `common/` (VC заменяет TGR на этих ID)**:
  - `common/buy_packages`: **wealth_1…wealth_99**
  - `common/pop_needs`: `popneed_basic_food`, `popneed_luxury_food`, `popneed_luxury_drinks`
  - `common/interest_groups`: 8 базовых IG `ig_armed_forces` и т.д.) — очень высокий риск
  - `common/technology/technologies`: `human_rights`
  - `common/static_modifiers`: `base_values` (у TGR `INJECT`, у VC `REPLACE_OR_CREATE` → без мержа инжект TGR пропадёт)
  - `common/defines`: `NAI`, `NPops` (есть пересечения по внутренним ключам в `NAI`)
  - `common/company_types`: 10 компаний (Krupp/EIC и др.)
  - `common/country_formation`: `GER`
  - `common/government_types`: `gov_presidential_democracy`, `gov_presidential_dictatorship`
  - `common/ideologies`: `ideology_utilitarian_leader` (меньше по приоритету, но тоже замена)
- **“Дубликаты”, которые на практике выглядят аддитивными**:
  - `common/on_actions` `on_monthly_pulse_country`, `on_yearly_pulse_country`) — у обоих модов это обычные повторяющиеся блоки без `REPLACE*`, похоже **суммируются**, а не конфликтуют.
- **События/локализация**:
  - дублей loc-ключей нет;
  - отдельно проверил **top-level event keys** вида `namespace.event = {}` — дублей между TGR и VC **нет**.

Если ок — дальше можем переходить к сборке компача в `vc_tgr/`, начиная с самых “ломающих” точек: **buy_packages + pop_needs + IG + defines + base_values + human_rights + manifest_destiny + GER/JEs**.