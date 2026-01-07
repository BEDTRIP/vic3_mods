### Общая сводка по `TheGreatRevision` (TGR): что именно он меняет (приоритет `common/`)

TGR — это **оверхаул экономики/торговли/политики**, сделанный в основном через **массовые `REPLACE_OR_CREATE`** в `common/` + крупные скриптовые системы (GUI → scripted_gui → scripted_effects → modifiers/on_actions).

---

### Экономика: налоги и бюджет (самое “ломкое” для компачей)

**Ключевая идея:** TGR **разносит налогообложение на независимые компоненты** и **переписывает бюджетный интерфейс**, чтобы игрок (и AI) мог отдельно крутить:
- **Land tax** (`tgr_land_tax`)
- **Per capita tax** (`tgr_per_capita_tax`)
- **Income tax** (`tgr_income_tax`)
- **Dividends tax** (`tgr_dividends_tax`)
- **Consumption tax** (`tgr_consumption_tax`)

Как это реализовано (важно для компачей):
- **GUI-переписка**: `TheGreatRevision/gui/budget_panel.gui` — добавлены контролы +/- и отображение переменных налогов.
- **Scripted GUIs**: `common/scripted_guis/TGR_TAX_PANEL_*_sguis.txt` — кнопки меняют переменные и перевешивают модификаторы.
- **Скриптовая логика**:
  - `common/script_values/TGR_TAX_PANEL_script_values.txt` — расчёт лимитов и “базовых” значений налогов по текущему налоговому закону и состоянию бюджета (gold reserves/debt).
  - `common/scripted_effects/TGR_TAX_PANEL_scripted_effects.txt` — выставляет переменные и (пере)накладывает модификаторы `tgr_*_tax`.
- **Модификаторы**: `common/static_modifiers/TGR_TAX_PANEL_modifiers.txt` — сами `tgr_*_tax` дают `tax_*_add = 1` и масштабируются `multiplier = значение переменной`.
- **Хуки**:
  - `common/history/global/TGR_TAX_PANEL_global.txt` — инициализация налогов всем странам.
  - `common/on_actions/TGR_TAX_PANEL_on_tax_law_change.txt` — пересчёт при смене налогового закона + периодический пересчёт (полугодовой).

При этом **налоговые законы** в `common/laws/TGR_TAX_PANEL_taxation.txt` помечены прямо в комментарии: *“Removes all real tax changes here”* — то есть **законы теперь скорее “рамка” для лимитов/AI**, а реальные цифры живут в переменных+модификаторах.

**Риск конфликтов для компачей:**
- любые моды, которые трогают `gui/budget_panel.gui`, `on_actions`, `taxation laws`, `static_modifiers` по налогам, очень вероятно потребуют ручного мержа.

---

### Экономика: поп-нужды / buy packages

TGR правит **структуру потребления по уровням благосостояния** через `common/buy_packages/00_buy_packages.txt` (видно большие правки `wealth_1..wealth_99` и комментарии про увеличение потребления еды/напитков на высоких уровнях). Это влияет на:
- структуру спроса,
- прибыльность производственных цепочек,
- баланс цен/торговых потоков.

---

### Торговля: “trade rework”, Trade Centers, тарифы/субсидии, компании

TGR очень сильно давит в сторону того, чтобы **торговля реально закрывала цепочки**, и чтобы **AI стабильно строил Trade Centers**.

Что конкретно меняется:

- **Trade Center как ключевая инфраструктура**:
  - `common/building_groups/TGR_TRADE_building_groups.txt` — `bg_trade` (другие параметры, лимиты cash reserves, использование инфраструктуры и т.д.).
  - `common/buildings/TGR_TRADE_private_infrastructure_trade_center.txt` — `building_trade_center` с **очень высоким `ai_value`**, и разрешением строить **и государству, и приватно** (`can_build_government/private`).
  - `common/production_methods/TGR_TRADE_private_infrastructure_trade.txt` — переработанные PM’ы Trade Center: больше `state_trade_capacity_add`, `state_weekly_trades_add`, изменён баланс затрат (например merchant_marine), логика “trade quantity”.

- **“Торговые костыли” для late-game AI**:
  - `common/production_methods/TGR_TRADE_private_infrastructure_investors.txt` — добавляет **trade capacity/trades** даже в “investor buildings” (financial district/manor house/company HQ и т.п.), чтобы рынок не умирал из‑за недостроя ТЦ.

- **Торговые законы**:
  - `common/laws/TGR_TRADE_trade_policy.txt` — `REPLACE_OR_CREATE` для `mercantilism/protectionism/free_trade/isolationism` и даже спец-вариант `law_canton_system` (Китай), с новыми модификаторами по тарифам/субсидиям/advantage и условиями видимости.

- **AI управление тарифами/субсидиями через ивенты**:
  - `events/TGR_TRADE_events.txt` + `common/on_actions/TGR_TRADE_code_on_actions.txt` — периодические ивенты для AI, которые **выставляют tariff/subvention уровни по товарам** (по gold reserves/debt, по странам и т.д.).

- **Defines по экономике/торговле**:
  - `common/defines/TGR_TRADE_defines.txt` — меняет ядро расчётов: `PRICE_RANGE`, дефолтные тарифы (по умолчанию no_tariffs_or_subventions), коэффициенты advantage, авто-даунсайз Trade Centers, и т.д. Это влияет на весь рынок, даже без скриптов.

- **Компании и чартеры**:
  - `common/company_types/TGR_TRADE_companies.txt` — массовые `REPLACE_OR_CREATE` компаний (часто с **очень высоким `ai_weight`**, и конкретными `ai_construction_targets`).
  - `common/company_charter_types/TGR_TRADE_company_charter_types.txt` — меняет AI-условия/вес чартеров (например trade/investment чартерам снижен порог prosperity и сильно поднят `ai_weight`).

**Риск конфликтов:**
- любые моды, которые меняют `building_trade_center`, `bg_trade`, PM’ы trade center/ownership, `defines NEconomy`, или компании/чартеры — почти гарантированный мердж.

---

### Политика: полностью расширенная сетка законов + новые “оси” государства

TGR **пересобирает law groups** и добавляет новые “измерения” политики. Базовый список хорошо отражён в `common/law_groups/TGR_POLITICS_laws.txt`:
- **Foreign policy** (`lawgroup_foreign_policy`)
- **Centralization** (`lawgroup_centralization`)
- **Economic incentives** (несколько групп: `*_primary/secondary/tertiary/public`)
- **Working hours**, **Salary regulation**
- **Retirement age**, **Social security**
- Перенастройка категорий/скорости принятия (`base_enactment_days`) и ideological impact.

Законы под это разнесены по множеству файлов в `common/laws/` (почти каждое направление отдельным `.txt`), включая `TGR_POLITICS_*` и отдельные `TGR_TAX_PANEL_taxation.txt`, `TGR_TRADE_trade_policy.txt`.

---

### Институты (institutions)

`common/institutions/TGR_POLITICS_institutions.txt` добавляет/переопределяет набор институтов под новые law groups (видны, например):
- `institution_pension`, `institution_salary`
- `institution_incentive_*`
- `institution_foreign`
- `institution_propaganda`, `institution_information`
- и т.д.

---

### Interest Groups и идеологии: перенастройка “политического двигателя”

- `common/interest_groups/TGR_POLITICS_*.txt` — `REPLACE_OR_CREATE` для всех основных IG (armed forces/devout/industrialists/…).
- `common/ideologies/TGR_POLITICS_ig_ideologies*.txt` — идеологии IG явно получают **позиции по новым law groups** (centralization/foreign_policy/economic_incentives/соцполитика и т.п.), чтобы AI/движения реально принимали эти законы.

Это важно для компачей с модами, которые меняют IG/ideologies: конфликт будет не только в файлах, но и в смысле (если другой мод добавляет свои law groups, придётся “склеивать” позиции идеологий).

---

### Дипломатия: новые действия/статьи договоров

TGR добавляет/правит дипломатические механики:

- **Migration Agreement**:
  - `common/treaty_articles/TGR_MIGRATION_migration_agreement_treaty.txt`
  - `events/TGR_MIGRATION_migration_agreement_campaign_event.txt`
  - `common/on_actions/TGR_MIGRATION_on_actions.txt`
  - `common/static_modifiers/TGR_MIGRATION_event_modifiers.txt`
  - Логика: при наличии статьи договора запускаются ивенты, которые создают mass migration и бустят привлекательность штата, с задержкой/ценой через модификаторы.

- **International Loans** (как отдельная система):
  - `common/diplomatic_actions/TGR_LOANS_issue_a_loan.txt`, `...apply_for_a_loan.txt`
  - `common/journal_entries/TGR_LOANS_panel.txt` (JE-панель кредитного рейтинга + кнопки)
  - `events/TGR_LOANS_events.txt`
  - `common/script_values/TGR_LOANS_script_values.txt`
  - Плюс куча модификаторов/кнопок в `common/static_modifiers/TGR_LOANS_*.txt`, `common/scripted_buttons/TGR_LOANS_buttons.txt`.
  - По сути: “кредитный рейтинг” → расчёт сумм/процентов → дипломатическое предложение → модификаторы на 10 лет.

- **Trade States**:
  - `common/diplomatic_actions/TGR_ADJUSTMENTS_trade_states.txt` — универсальная дипло-опция обмена штатами (с проверками связности/побережья).

- **Force Regime Change для Power Bloc**:
  - `common/diplomatic_actions/TGR_ADJUSTMENTS_power_bloc_force_regime_change.txt` — режимная смена внутри блока при выполнении условий (cohesion, разница progressiveness по law groups и т.д.).

---

### Персонажи: новые interactions (пропаганда / отставки)

`common/character_interactions/TGR_LEADER_character_interactions.txt` добавляет/заменяет interactions:
- **propaganda_campaign** (за/против персонажа)
- **resign_from_office_politician** (события/скоупы на лидера/партию)
и т.п. Это завязано на `events/TGR_LEADER_propaganda_campaign.txt` и модификаторы/defines.

---

### Декреты (decrees)

`common/decrees/TGR_DECREES_decree.txt`:
- новая/переписанная версия **Greener Grass** для неинкорпорированных территорий,
- и “жёсткий” декрет **population replacement** (через mortality/migration pull), оба с ограничениями на совместимость и выбор AI.

---

### Исторический контент / “Campaign Adjustments” (унификации и прочее)

TGR очень сильно “подкручивает” кампанию через JEs + scripted buttons + events:

- **Germany**: `common/journal_entries/TGR_GER_UNIFICATION_german_unification.txt`, `events/TGR_GER_UNIFICATION_german_unification.txt`, `common/on_actions/TGR_GER_UNIFICATION_code_on_actions.txt`, `common/scripted_buttons/TGR_GER_UNIFICATION_scripted_buttons.txt`.
  - Есть прямые annex/protectorate/DP-инициирования и глобальные переменные — цель “почти всегда формируется”.

- **Italy**: `common/journal_entries/TGR_ITA_UNIFICATION_italian_unification.txt` + пачка дополнительных JE-файлов по итальянским веткам, `events/TGR_ITA_UNIFICATION_italian_unification.txt`, `common/on_actions/TGR_ITA_UNIFICATION_code_on_actions.txt`, кнопки в `common/scripted_buttons/...`.

- **США и прочее**:
  - `common/decisions/manifest_destiny.txt`
  - `common/journal_entries/TGR_ADJUSTMENTS_oregon.txt`, `...borders.txt`
  - и связанные `events/TGR_ADJUSTMENTS_*.txt`, `common/scripted_buttons/TGR_ADJUSTMENTS_*`.

---

### AI: стратегии и defines

- `common/ai_strategies/*` — новые/переписанные админ/политические стратегии, встречается “must_have” субсидирование `building_trade_center`.
- `common/defines/*` — правки поведения AI (частота реформ правительства, spending thresholds, etc.), а также системные параметры экономики/попов/политики.

---

### Для компачей: что считать “точками конфликта №1”

- **GUI**: `TheGreatRevision/gui/budget_panel.gui`
- **Tax system цепочка**: `common/scripted_guis/` + `common/scripted_effects/` + `common/script_values/` + `common/on_actions/TGR_TAX_PANEL_on_tax_law_change.txt` + `common/history/global/TGR_TAX_PANEL_global.txt` + `laws/TGR_TAX_PANEL_taxation.txt`
- **Trade Center + trade PMs + defines NEconomy**: `common/buildings/*trade_center*`, `common/production_methods/TGR_TRADE_private_infrastructure_trade*.txt`, `common/defines/TGR_TRADE_defines.txt`
- **Law groups / laws / ideologies / IGs**: `common/law_groups/TGR_POLITICS_laws.txt`, `common/laws/TGR_POLITICS_*.txt`, `common/ideologies/*`, `common/interest_groups/*`
- **Унификации**: `common/journal_entries/TGR_*UNIFICATION*`, `events/TGR_*UNIFICATION*`, `common/on_actions/TGR_*UNIFICATION*`, `common/scripted_buttons/TGR_*UNIFICATION*`
- **Дипломатия (loans/migration/trade_states/regime_change)**: `common/diplomatic_actions/*`, `common/treaty_articles/*`, соответствующие `events/` и `on_actions/`.
