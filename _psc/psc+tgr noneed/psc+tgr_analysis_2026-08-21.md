# PSC + TGR — ревизия компача, 21.08.2026 (вывод: noneed подтверждён)

## Что сверялось

| Мод | Версия | metadata | Примечание |
|---|---|---|---|
| PSC | `PSC 2.05.2026`, репо `1.3.7` | `supported_game_version` пустой | сводка сверена 19.08.2026, изменений с тех пор нет (0 файлов новее 19.08) |
| TheGreatRevision | `TGR 1.3.10 12.08.2026 update` | `2.0`, `1.13.10` | сводка сверена 21.08.2026 (сегодня), изменений с тех пор нет |
| компач `psc+tgr noneed` до правки | без версии; README называл себя `pb+tgr` (копипаста из чужого шаблона) и описывал merged-файл, которого физически не было в папке | — | последний прогон `scan_conflicts.py` — январь 2026, коммит `TGR 20.01 update compatch check` |

## Прогон scan_conflicts.py 21.08.2026

`common_categories_intersection=14 common_key_dups=3 loc_key_dups=0 event_id_dups=0` — по сути идентично январскому отчёту. Единственная разница: TGR к 12.08 переименовал часть `history/buildings/*_setup.txt` (теперь Austria/Ottomans/Spain вместо UK/company_buildings/trade_center) — косметическая реорганизация, `BUILDINGS` всё равно аддитивен.

3 дубля ключей:
1. `building_construction_sector` (common/buildings) — разобрано ниже, единственный содержательный кандидат.
2. `BUILDINGS` (history/buildings) — аддитивная категория, не конфликт.
3. `GLOBAL` (history/global) — аддитивная категория, не конфликт.

## building_construction_sector — построчный разбор

**TGR** (`REPLACE_OR_CREATE`, грузится первым):
```
building_group = bg_construction
icon = "gfx/interface/icons/building_icons/construction_camp.dds"
city_type = city
levels_per_mesh = 50
has_max_level = yes
required_construction = construction_cost_very_low   # единственное отличие от ванили
unlocking_technologies = { urbanization }
production_method_groups = { pmg_base_building_construction_sector }
ai_value = 1000
background = ".../building_panel_bg_farming.dds"
```
Сравнение с ванилью (`.vanillaVIC3/common/buildings/13_construction.txt`): TGR меняет только `required_construction` (`construction_cost_construction_sector` → `construction_cost_very_low`). Всё остальное — дословная копия ванили, включая `has_max_level = yes`.

**PSC** (`REPLACE`, грузится вторым):
```
building_group = bg_construction
icon = "gfx/interface/icons/building_icons/construction_camp.dds"
city_type = city
levels_per_mesh = 5
ai_nationalization_desire = 0.25
unlocking_technologies = { urbanization }
production_method_groups = { pmg_base_building_construction_sector }
ai_value = { ...KAI-формула... }
required_construction = construction_cost_very_low
ownership_type = self
background = ".../building_panel_bg_light_industry.dds"
```
PSC не упоминает `has_max_level` вообще.

### Что значит has_max_level

Из `buildings.md` (документация в поставке ванили): `has_max_level = yes` → «a dynamic country modifier is created to determine max level». Для construction_sector это `state_building_construction_sector_max_level_add`, который раздают только технологии: `urbanization +10`, `urban_planning +5`, `modern_sewerage +5`, `steel_frame_buildings +5`, `elevator +5` (потолок 30 без urbanization, 40 с ней). Без этого модификатора уровень сектора жёстко привязан к 0 — здание физически не расширяется выше 1 уровня. Значит `has_max_level` — не косметика, а обязательная часть работоспособности здания.

### Почему компач не нужен

1. **Единственная содержательная правка TGR (`required_construction`) уже продублирована в PSC дословно.** Даже при полной перезаписи компачу нечего было бы мержить по этому полю.
2. **`REPLACE:` патчит по перечисленным полям, а не по записи целиком** — подтверждено 21.08.2026 на живом примере E&F/TGR (`common/production_methods/11_ef_private_infrastructure.txt`: 14 `REPLACE:pm_company_headquarter_*` содержат только `building_modifiers`, но `texture`/`unlocking_company_categories`/`disallowing_laws`/`unlocking_laws`/`unlocking_principles` не пропадают — мод не ломается в соло, подробности в `сводки по модам/сводка_ef.md`). PSC не перечисляет `has_max_level`, значит по той же логике он наследуется из TGR-слоя (там `yes`, как в ванили) и не обнуляется.
   - Оговорка: прямого теста именно на `common/buildings` (а не на `common/production_methods`) в этом раунде не делалось. Если движок всё же ведёт себя по-разному для разных категорий БД, следствие будет однозначным и быстро заметным в игре — см. caveat в README компача.
3. **`bg_construction` (building_group) TGR не трогает вовсе** — переопределяет только `bg_trade`, `bg_consumer_goods`, `bg_industry_heavy`, `bg_industry_light` (см. `сводка_tgr.md`, дополнение MR×TGR). Приватизация группы, которую делает PSC (родитель `bg_private_infrastructure` вместо `bg_public_infrastructure`), ничем не оспаривается.
4. **GUI не пересекается.** У TGR всего один `.gui` файл в моде — `gui/budget_panel.gui`. PSC его не трогает; свои экраны (`construction_panel.gui`, `states_panel_buildings.gui`, `construction_expense_widget.gui`, `goods_texticons.gui`, `shared/construction_spending_options.gui`) у TGR просто отсутствуют.
5. **Законы/институты/идеологии не пересекаются** — PSC их не трогает вообще, вся политическая часть — исключительно домен TGR.
6. **`BUILDINGS` и `GLOBAL`** — аддитивные категории, дубль ключа не значит конфликт (см. общие факты по 1.13).
7. **0 дублей локализации, 0 дублей id событий.**

## Что было не так в старом README

Заголовок называл компач `pb+tgr` (не `psc+tgr` — копипаста из другого шаблона) и описывал merged-файл `common/buildings/zz_pb_tgr_psc_construction.txt`, которого физически никогда не было в папке (в папке лежали только README и два отчёта). Судя по всему, план мержа был написан до анализа, а по факту после проверки решили, что компач не нужен, но текст README не обновили. Переписан.

## Итог

`noneed` подтверждён повторно, дата сверки актуализирована на 21.08.2026. Пересматривать при изменении любого из пунктов в разделе «Когда пересматривать» README компача.
