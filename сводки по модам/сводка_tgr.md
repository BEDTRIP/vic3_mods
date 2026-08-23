### Общая сводка по `TheGreatRevision` (TGR): что именно он меняет (приоритет `common/`)

**Версия в репозитории**: коммит `TGR 1.3.10 12.08.2026 update`.
`.metadata/metadata.json`: `version 2.0`, `supported_game_version 1.13.10`, Steam ID `3215078236`.
**Сверено с файлами: 21.08.2026.**

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


---

### Дополнение 2026-08-21 (из сверки MR × TGR)

**Версия**: `2.0`, `supported_game_version` = `1.13.10`, `relationships` пусты. Steam ID `3215078236`.

- **Новое с прошлой сверки**: TGR стал инжектить в три ванильных теха — `INJECT:atmospheric_engine` (`TGR_POLITICS_production.txt`), `INJECT:civilizing_mission` и `INJECT:malaria_prevention` (`TGR_POLITICS_society.txt`). Раньше `common/technology` в пересечениях не всплывал.
- **Товаров TGR не добавляет ни одного**: все 53 записи в `common/goods` — `REPLACE_OR_CREATE` ванильных. Для расчёта потолка 128 TGR даёт ноль.
- **Ванильных файлов перекрывает целиком 496**, но содержательных мало: `common/buy_packages/00_buy_packages.txt`, все 12 `common/parties/*.txt`, 14 файлов `common/history/countries/*` (AUS BRZ CHI FRA GBR JAP MEX NET PER SAR SIC SPA SWE TUR), `common/decisions/manifest_destiny.txt`, `gui/budget_panel.gui`, `localization/languages.yml`. Остальные ~470 — `.dds` иконки законов и PM.
- **`gui/budget_panel.gui` — 2336 строк против ванильных 2112** (переписан, не обрезан), но четыре ванильных имени виджетов пропали: `bankruptcy_progress_bar`, `bankruptcy_progressbar`, `declare_bankruptcy_button`, `tutorial_highlight_tax_level`. Первые три нигде больше не упоминаются — кнопка банкротства, похоже, убрана намеренно под систему займов. А `tutorial_highlight_tax_level` **ссылается ванильный** `common/tutorial_lessons/00_tutorial_lessons_budget_balance.txt` → урок туториала по бюджету ищет несуществующий виджет. Проверять при включённом туториале.
- **`building_groups` TGR переопределяет ровно четыре**: `bg_trade`, `bg_consumer_goods`, `bg_industry_heavy`, `bg_industry_light`. Всё остальное дерево групп ванильное — чужие группы с родителями вне этой четвёрки не задеваются.
- **`pop_needs`**: `REPLACE_OR_CREATE` для восьми — `popneed_basic_food`, `popneed_luxury_food`, `popneed_luxury_drinks`, `popneed_intoxicants`, `popneed_crude_items`, `popneed_simple_clothing`, `popneed_household_items`, `popneed_heating`.
- **`on_actions` TGR трогает всего пять** и без префиксов `REPLACE:`: `on_yearly_pulse_country`, `on_monthly_pulse_country`, `on_half_yearly_pulse_country`, `on_law_activated`, `on_tax_law_change`. Каталог аддитивен, стыкуется с любым модом.

---

### Дополнение 2026-08-21 (из сверки E&F × TGR)

- **Модуль International Loans физически лежит внутри основного TGR.** Отдельный
  подмод `TGR_Loans` (Steam `3452303324`, «TGR Series: International Loans», metadata
  `1.13.11`) — не расширение, а вырезка: все шесть общих файлов
  (`journal_entries/TGR_LOANS_panel.txt`, `scripted_buttons/TGR_LOANS_buttons.txt`,
  `script_values/TGR_LOANS_script_values.txt`, `static_modifiers/TGR_LOANS_modifiers.txt`,
  `scripted_progress_bars/TGR_LOANS_interest_rate_bars.txt`,
  `localization/english/TGR_LOANS_l_english.yml`) **побайтово равны**. Ставить подмод
  вместе с основным TGR бессмысленно; отключать займы приходится скриптом.
  Живые id для отключения: `je_international_loans`, `tgr_loans_button_1..8`.
- **Дипдействий `issue_a_loan` / `apply_for_a_loan` больше нет.** Ни в TGR, ни в
  `TGR_Loans`, ни в ванили; в `TGR_Loans/gfx/interface/icons/lens_toolbar_icons/`
  остались только иконки. Старые компачи с `REPLACE_OR_CREATE:` на эти ключи их не
  отключают, а **создают** — два фантомных действия без локализации.
- **`state_building_trade_center_max_level_add = 10` — становой хребет trade rework.**
  Раздаётся шестью технологиями в `TGR_TRADE_society.txt`: `currency_standards`,
  `stock_exchange`, `corporate_charters`, `mutual_funds`, `joint_stock_companies`,
  `investment_banks` (плюс `tech_bureaucracy` и `international_trade` через
  `state_building_trade_center_max_level_add` в тех же INJECT). Любой мод, который
  переопределяет блок `modifier` этих техно, срезает потолок ТЦ по 10 уровней за штуку.
- **Технологии TGR разложены по двум файлам с разной стратегией.**
  `TGR_LOANS_society.txt` — `REPLACE_OR_CREATE` для `banking`, `central_banking`,
  `mutual_funds`, `international_exchange_standards`, `modern_financial_instruments`.
  `TGR_TRADE_society.txt` — `INJECT` в `tech_bureaucracy`, `international_trade`,
  `currency_standards`, `stock_exchange`, `banking`, `central_banking`,
  `corporate_charters`, `mutual_funds` и `REPLACE_OR_CREATE` для
  `joint_stock_companies`, `investment_banks`, `corporate_management`, `macroeconomics`.
  Загружается LOANS раньше TRADE, поэтому INJECT ложится поверх собственного
  REPLACE_OR_CREATE.
- **`base_values` TGR патчит тремя файлами и все через `INJECT:`** — они мерджатся,
  конфликта с чужими INJECT нет. Актуальные значения (12.08.2026):
  LOANS `country_loan_interest_rate_add = -0.2`;
  POLITICS bureaucracy/authority/influence `= 200`, `country_officers_pol_str_mult = -2`,
  `country_soldiers_pol_str_mult = -1`;
  TRADE `country_company_construction_efficiency_bonus_add = 0.20`,
  `state_max_trade_advantage_from_capacity_add = 0.05`,
  `country_company_throughput_bonus_add` **закомментирован**.
- **PM штаб-квартир компаний** (`TGR_TRADE_private_infrastructure_investors.txt`,
  21 запись): `state_modifiers { level_scaled { state_weekly_trades_add = 0.5
  state_trade_capacity_add = 1 state_tax_capacity_add = 0.25 } }`. До 08.2026 было
  `state_weekly_trades_add = 1` и без `state_tax_capacity_add`.
- **Новых товаров TGR не добавляет.** Все 53 записи в `common/goods/TGR_TRADE_goods.txt` —
  `REPLACE_OR_CREATE` ванильных, `gold` при этом побайтово равен ванильному.
  Для лимита 128 TGR нейтрален.
- **`gui/budget_panel.gui` у TGR соответствует 1.13.10**: `is_selected_visibility_1..5`,
  `[concept_budget_goods_for_military_upkeep]`, строки `BUDGET_TREATIES`,
  `GetSupplyShipMaintenanceExpenses`, `GetShipConstructionGoodsExpenses` на месте.
  Если в чужом мердже вместо `_1.._5` стоят `_very_low.._very_high`, а
  `BUDGET_TREATIES` нет — мердж собран на базе 1.12 и его надо пересобирать.
  TGR при этом заменяет ванильный ряд `tax_exp_frame_coin` («Taxation level») своим
  `tax_exp_frame_fiscal_reform`, и вместе с ним теряется имя виджета
  `tutorial_highlight_tax_level`.

---

### Дополнение 2026-08-21 (из сверки PSC × TGR)

- **Компач `psc+tgr noneed` пересверен, вывод не изменился.** Единственное пересечение — `building_construction_sector` (`REPLACE_OR_CREATE` у TGR, `REPLACE` у PSC). Единственная содержательная правка TGR (`required_construction = construction_cost_very_low`) у PSC совпадает дословно, терять нечего. Полный разбор — `_psc/psc+tgr_analysis_2026-08-21.md`.
- **Старое README компача было ошибочным**: называло себя `pb+tgr` (копипаста) и описывало merged-файл, которого не существовало в папке. Переписано.
- Пересечения `BUILDINGS`/`GLOBAL` с PSC — те же аддитивные категории, что и с E&F/MR, не конфликт.

### Дополнение 2026-08-21 (из сверки PBE × TGR)

- **Компач `pbe+tgr done` переписан.** Единственная точка мерджа — `force_regime_change` в `common/diplomatic_actions/`: TGR правит его через `REPLACE_OR_CREATE:`, PBE — обычным ключом и грузится позже, так что без компача версия TGR теряется молча.
- Вклад TGR в это действие: cohesion floor 0.1 → 0.25, tenure 5 лет → 1 год, `installed_regime` на `months = 24`, AI-пороги −25/−50 → −50/−100 (у PBE ровно те же), сохранена ванильная `add_cohesion_percent = scaled_cohesion_cost`. Венгерские `trigger_if` и `NOT ally` TGR вырезал.
- В мердже структура взята у PBE (гейт `OR = { has_game_rule ... }`), числа — у TGR внутрь ветки `AND`. Прошлая версия компача поднимала требования TGR наружу и тем самым обнуляла game rule PBE.
- **`country_influence_add`** (TGR `decimals = 0` против ванильного `1` у PBE) и **`state_bureaucrats_investment_pool_contribution_add`** (TGR `color = neutral` против ванильного `good`) — различия только в отображении, PBE грузится последним и даёт ванильный результат. Пин-файл в компаче удалён как бесполезный.
- TGR не трогает `power_bloc_principles`, `power_bloc_identities`, `cohesion_levels`, `scripted_rules` — весь основной домен PBE. GUI не пересекается (`budget_panel.gui` против панелей блока). Товаров TGR не добавляет: 53 ключа, все ванильные, через `REPLACE_OR_CREATE:`.
- Разбор целиком — `_pbe/pbe+tgr done/conflicts_tgr_vs_pbe_report.md`.

### Дополнение 2026-08-23 (из сверки пары TGR × T&R × KAI, компач `_tgr/tgr+tr+kai done`)

**Статус пары: `done`, компач переписан.** Отчёты — `_tgr/tgr+tr+kai done/conflicts_tgr_vs_tr_report.md`
и `conflicts_tgr_vs_kai_report.md` (в шапке каждого — таблица «почему это конфликт / почему нет»).
Порядок загрузки: CMF → TGR → KAI → **T&R** → компач. В старом компаче в комментарии было
написано, что последним грузится KAI, — неверно, исправлено.

Что TGR теряет молча и что за это отвечает в компаче:

- **`law_extraction_economy`** — T&R 1.6 делает `INJECT:` только на `on_activate`. `on_activate` —
  блок, а не список, поэтому инъекция встаёт на место TGR-овского, и **своп
  `law_administrative_centralism` → `law_local_autonomies` исчезает**. В логе — ничего.
  Патч оставлен, тело пересобрано на нынешнем TGR (у старого компача был `can_enact = is_subject = yes`
  без защиты по дате 1836, лишние `disallowing_laws` и `state_bureaucrats_investment_pool_efficiency_mult`).
- **Колониальные законы** (`law_colonial_exploitation`, `law_colonial_resettlement`,
  `law_frontier_colonization`) — **новая точка конфликта**: UN-система T&R переписывает их целиком
  `REPLACE:` и не имеет ключа `institution_modifier`, а у TGR там `country_engineers_pol_str_mult` /
  `country_farmers_pol_str_mult = 0.20`. Перенесено в компач. `progressiveness` (TGR 25 против T&R 0)
  не переносим — там оба автора выставили значение осознанно.
- **Товары** — TGR правит все 53 ванильных товара, срезая `traded_quantity` и поднимая
  `convoy_cost_multiplier`. T&R переиздаёт три (`aeroplanes`, `automobiles`, `clothes`) с
  околованильными числами и грузится позже, то есть **три товара выпадают из торгового оверхола TGR**.
  Новый файл `common/goods/` в компаче. У `aeroplanes` заодно возвращён `obsession_chance` — T&R
  просто не переносит ключ, и товар молча перестаёт быть obsession.
- **`malaria_prevention`** — TGR вешает `country_institution_environment_max_investment_add = 1`
  через `INJECT:`, T&R пересоздаёт технологию `REPLACE_OR_CREATE:` и грузится позже. Строка TGR
  теряется, институт Environment TGR теряет уровень вложений. Новый файл `common/technology/technologies/`.
- **`bg_industry_heavy` / `bg_industry_light`** — TGR вешает на них декрет
  (`common/decrees/TGR_POLITICS_decree.txt`) и законы экономических стимулов
  (`TGR_POLITICS_economic_incentives_industry.txt`). `bg_heavy_industry` у T&R — **сестринская**
  группа (обе дочерние к `bg_manufacturing`), `is_building_group` до неё не дотягивается.
  Поэтому в двух зданиях, которые T&R всё ещё перекрывает целиком, группа берётся у TGR.

Что **не** патчится осознанно (и почему — чтобы через полгода не проверять заново):

- `buy_packages` `wealth_1..99` — TGR определяет их обычным ключом, T&R сверху `TRY_INJECT:`.
  Аддитивно, порядок правильный, 90 «дубликатов» в машинном отчёте — ложное срабатывание.
- `popneed_heating` — T&R `REPLACE:` с новыми товарами (`gas`, `homeappliances`), TGR правит
  доли снабжения. Сохранить схему TGR = придумать доли для товаров, которых TGR не видел.
- `law_no_womens_rights`, `law_women_own_property`, детские законы — расхождение чисто числовое.
- `wanted_army_size_script_value`, `NAI` `MONEY_SPENDING_*` (8 подключей, пересечение с KAI),
  `ai_strategy_industrial_expansion` / `plantation_economy` / `placate_population` — у обоих
  авторов полные осознанно разные версии.
