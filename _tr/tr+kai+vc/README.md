## vc_tr — ComPatch: TechRes+Kuromi + Victorian Century

### Порядок загрузки

**TechRes+Kuromi → Victorian Century → vc_tr (этот компач)**

> Примечание: если компач не последний — смысл части правок пропадёт (VC перезапишет merged-блоки).

### Отчёты конфликтов (эвристика + ручная проверка)

- `conflicts_tr_vs_vc_report.md` — T&R vs VC
- `conflicts_kai_vs_vc_report.md` — KAI vs VC
- `conflicts_cmf_vs_vc_report.md` — CMF vs VC
- GUI:
  - `conflicts_tr_vs_vc_gui_ids.txt`
  - `conflicts_cmf_vs_vc_gui_ids.txt`
- Сводный приоритетный итог:
  - `conflicts_tr_kai_cmf_vs_vc_master.md`

### Что делает компач (реализовано)

- **`common/buy_packages/zz_vc_tr_buy_packages.txt`**
  - возвращает T&R `TRY_INJECT:wealth_10..wealth_99` (добавляет `popneed_entertainment` в buy packages VC).
- **`common/pop_needs/zz_vc_tr_pop_needs.txt`**
  - встраивает в VC pop-needs потребление новых товаров TechRes+Kuromi (вода/газ/ПО/электроника/фарма/и т.п.), чтобы экономика T&R реально получала спрос при VC последним.
- **`common/company_types/zz_vc_tr_company_types.txt`**
  - для 32 пересекающихся `company_*` берёт VC как базу и добавляет недостающие `building_types` / `extension_building_types` / `prosperity_modifier` из T&R (без перезаписи одинаковых ключей).
- **`common/modifier_type_definitions/zz_vc_tr_modifier_types.txt`**
  - фиксирует конфликт `goods_output_grain_mult` (оставляем VC-определение, чтобы не терять UI-метаданные).
- **`common/technology/technologies/zz_vc_tr_technologies.txt`**
  - фиксирует конфликт `organized_sports` (VC как база + добавлены T&R ai_weight бонусы для FRA/GRE и доп. unlock `pan-nationalism`).
- **`common/on_actions/zz_vc_tr_on_actions.txt`**
  - объединяет `on_monthly_pulse_country` и `on_yearly_pulse_country` (VC headlines + VC monarchy sub-actions + T&R monthly/yearly sub-actions),
  - сохраняет VC `on_new_ruler`, но **возвращает ванильный блок триггера регентства** (который исчезает, когда VC переопределяет `on_new_ruler`).
- **`common/defines/zz_vc_tr_defines.txt`**
  - “супер‑блок” `NAI` (VC как база + добавлены ключи Kuromi AI, без перезаписи совпадающих),
  - “супер‑блок” `NPops` (модель роста населения из TechRes+Kuromi + ключи VC про рабочую долю/колонизацию/культурные общины).

### Что намеренно НЕ мерджится (пока)

- Жёсткие совпадения путей (CMF vs VC): `common/parties/*`, `gui/00_MDF_frontend_dlc.gui` — остаются VC (без ручного мержа).


