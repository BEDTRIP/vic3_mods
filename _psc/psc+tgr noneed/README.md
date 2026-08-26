# psc+tgr noneed

<!-- meta
пара: PSC × TGR
статус: noneed
версии: —
позиция: —
файлов: 0
генератор: —
зависит от: —
-->

### PSC + The Great Revision (TGR) — вывод: компач не нужен (`noneed`)

Пересверено: 21.08.2026 (предыдущая проверка — январь 2026, `TGR 20.01 update compatch check`).

### Единственное пересечение

Оба мода переопределяют здание `building_construction_sector`:
- TGR (`common/buildings/TGR_TRADE_construction.txt`) — `REPLACE_OR_CREATE:`, почти дословная копия ванили. Единственное содержательное изменение — `required_construction = construction_cost_very_low` (в ванили `construction_cost_construction_sector`).
- PSC (`common/buildings/zz_PSC_construction.txt`) — `REPLACE:`, приватизирует сектор (`ownership_type = self`, `ai_nationalization_desire = 0.25`, свой `ai_value`), но **тоже** ставит `required_construction = construction_cost_very_low` — значение у обоих модов совпадает дословно.

Порядок загрузки: TGR → PSC (PSC грузится позже как более узкий мод).

### Почему это не конфликт

1. Единственное содержательное значение, которое меняет TGR (`required_construction`), у PSC совпадает дословно — терять нечего.
2. `REPLACE:` в 1.13 патчит по перечисленным полям, а не заменяет запись целиком (подтверждено 21.08.2026 на живом примере в E&F, см. `сводки по модам/сводка_ef.md`, раздел «REPLACE: работает по под-блокам»). PSC не упоминает `has_max_level` — вопреки прежнему предположению этого README, флаг **не пропадает**, он наследуется от TGR-слоя (у TGR тоже `yes`, как в ванили). Прямого теста именно на `common/buildings` (а не на `common/production_methods`, где правило подтверждено) в этом раунде не делалось — см. оговорку ниже.
3. `bg_construction` — TGR его вообще не трогает (переопределяет только `bg_trade`, `bg_consumer_goods`, `bg_industry_heavy`, `bg_industry_light`). Приватизация `bg_construction`, которую делает PSC, ничем не оспаривается.
4. GUI не пересекается: у TGR всего один `.gui`-файл в моде — `gui/budget_panel.gui`; PSC его не трогает. Свои экраны (`construction_panel.gui`, `states_panel_buildings.gui`, `construction_expense_widget.gui`, `goods_texticons.gui`, `shared/construction_spending_options.gui`) TGR не трогает вовсе — в TGR этих файлов просто нет.
5. Законы/институты/идеологии не пересекаются: PSC их не трогает вообще.
6. `BUILDINGS` (history/buildings) и `GLOBAL` (history/global) пересекаются по ключу у обоих модов, но это аддитивные категории — не конфликт (см. общие факты по 1.13).
7. `scan_conflicts.py`: 0 дублей локализации, 0 дублей id событий.

### Caveat — что проверить в игре, если сектор ведёт себя странно

Пункт 2 — перенос вывода, подтверждённого на `production_methods`, на `common/buildings` без прямой проверки. Если движок всё же ведёт себя иначе для простых building-записей, симптом будет однозначным: построенный `building_construction_sector` не расширяется выше 1 уровня (потому что `has_max_level` без компенсирующего модификатора фактически обнуляет потолок). При таком симптоме — смотреть сюда в первую очередь, а не искать в другом месте.

### Когда пересматривать

- Если TGR перестанет ставить `construction_cost_very_low` (снова разойдётся с PSC по стоимости).
- Если TGR начнёт трогать `bg_construction` или любой из перечисленных `.gui` файлов PSC.
- Если PSC уберёт `ownership_type = self` из `REPLACE:` — тогда сначала смотреть, что случилось с самим PSC, а не чинить компачом.

Полный разбор — `_psc/psc+tgr_analysis_2026-08-21.md`. Отчёт `scan_conflicts.py` от 21.08.2026 — `conflicts_psc_vs_tgr_report_2026-08-21.md` в этой папке.
