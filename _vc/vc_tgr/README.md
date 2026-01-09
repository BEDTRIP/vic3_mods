## vc_tgr — ComPatch: The Great Revision + Victorian Century

### Отчёты

- **Сырой (эвристика)**: `conflicts_tgr_vs_vc_report.md`
- **Перепроверенный/с приоритетами**: `conflicts_tgr_vs_vc_report_reviewed.md`

### Ключевые результаты конфликтов (самое важное)

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

### Что уже делает этот компач (реализовано в `common/`)

- **`common/decisions/manifest_destiny.txt`**: восстанавливает решение TGR (у VC на этом пути `#nothing`).
- **`common/buy_packages/zz_vc_tgr_buy_packages.txt`**: итоговые `wealth_1..wealth_99` (агрессивный мердж “по максимуму” по количествам).
- **`common/pop_needs/zz_vc_tgr_pop_needs.txt`**: выбирает TGR версии для `popneed_basic_food`, `popneed_luxury_food`, `popneed_luxury_drinks`.
- **`common/defines/zz_vc_tgr_defines.txt`**: “супер-блок” `NAI` + `NPops` (VC как база, плюс добавлены недостающие ключи TGR; для дублей оставлены значения VC).
- **`common/static_modifiers/zz_vc_tgr_static_modifiers.txt`**: возвращает TGR `INJECT:base_values` (иначе его сносит VC `REPLACE_OR_CREATE:base_values`).
- **`common/on_actions/zz_vc_tgr_on_actions.txt`**: объединяет списки событий/под-экшенов в `on_monthly_pulse_country` и `on_yearly_pulse_country`.
- **`common/technology/technologies/zz_vc_tgr_technologies.txt`**: `human_rights` = VC `on_researched` + добавлены TGR-cap’ы институтов (`pension`/`salary`).
- **`common/country_formation/zz_vc_tgr_country_formation.txt`**: `GER` = VC state list, но убран VC-лок на их переменную JE, чтобы не блокировать TGR-унификацию.
- **`common/government_types/zz_vc_tgr_government_types.txt`**: мердж `gov_presidential_democracy` и `gov_presidential_dictatorship` (VC условия + TGR `has_law_or_variant`/safety-ограничения).

### Что пока намеренно НЕ мерджится (оставляем победу VC при порядке TGR → VC)

- **`map_data/state_regions/*`**: VC полностью заменяет карту/ресурсы; TGR-правки отдельных файлов не переносим.
- **`common/history/countries/*`**: **мерджим частично** (берём VC как базу и точечно возвращаем TGR-добавки там, где они не конфликтуют: стартовые компании/JE/инициализации).
- **`common/parties/*`**: остаются VC-версии (без ручного мержа партийных шаблонов).
- **`common/company_types`**, **`common/interest_groups`**, **`common/ideologies`**: на текущем этапе не перепрошиваем (слишком рискованно без отдельного “политического дизайна”, т.к. эти системы у обоих модов масштабные).