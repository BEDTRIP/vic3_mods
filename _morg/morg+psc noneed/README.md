# morg+psc noneed

<!-- meta
пара: Morgenröte × PSC
статус: noneed
версии: Проверено: **21.08.2026**, игра 1.13.10
позиция: —
файлов: 0
генератор: —
зависит от: —
-->

### Morgenrote + PSC — компач НЕ НУЖЕН (`noneed`)

- `Morgenrote` 2.8.3e «Mitsopoulos» (`supported_game_version` 1.13.*, зависимость — CMF 1.*)
- `Private Sector Construction` 1.3.7
- Проверено: **21.08.2026**, игра 1.13.10

Папка оставлена пустой намеренно — как запись о том, что пара проверена.
`.metadata/` здесь нет, модом она не грузится.

---

## Вывод

**Конфликтов нет.** Ниже — что именно проверено и почему каждый пункт чист.

### 1. Пути файлов — пересечений нет

MR — 8210 файлов, PSC — 98. Единственное совпадение относительного пути:
`thumbnail.png` (картинка в мастерской, на игру не влияет).

Ни один из модов не перекрывает файл другого целиком, поэтому порядок
загрузки между ними безразличен.

### 2. Ванильные файлы — не пересекаются

Полных копий ванильных файлов:
- MR: `common/achievement_groups.txt`, `common/history/characters/par - parma.txt`, `gui/error_deer.gui`
- PSC: ни одного

Общих ванильных файлов, перекрытых обоими, — нет.

### 3. Ключи в `common/` — совпадения только по аддитивным блокам

`scan_conflicts.py --a Morgenrote --b PSC` даёт 5 дублей, все безопасные:

| Ключ | Категория | Почему не конфликт |
|---|---|---|
| `BUILDINGS` | `common/history/buildings` | блок аддитивен, содержимое обоих модов складывается |
| `GLOBAL` | `common/history/global` | то же |
| `on_monthly_pulse` | `common/on_actions` | список `on_actions = { }` мерджится движком |
| `on_acquired_technology` | `common/on_actions` | то же |
| `on_building_built` | `common/on_actions` | то же |

Дубликатов ключей локализации — 0, дубликатов id событий — 0.

### 4. GUI — пересечений по именам виджетов нет

`compare_gui_names.py`: `name` 61 vs 10 — пересечение 0; `icon` 424 vs 4 — 0;
`type` 70 vs 6 — 0.

Это важнее, чем кажется: PSC переопределяет ванильные окна строительства
(`construction_panel`, `state_panel_types` и т.д.) и с E&F по этим именам
конфликтует. MR своих окон строительства не трогает вообще — он живёт
в собственных панелях (`mr_*_panel.gui`). Пропавших виджетов, а значит
и вылета при открытии панели, тут быть не может.

### 5. Потолок товаров — с большим запасом

Ваниль 53 + MR 5 + PSC 4 = **62** уникальных товара при потолке 128.
Пересечений имён товаров между модами нет, ванильные товары не переопределяет
ни один из них.

### 6. Механика строительства PSC — MR в неё не лезет

PSC перевешивает `bg_construction` на `bg_private_infrastructure`, добавляет
`bg_construction_regulator`, `REPLACE`-ит `building_construction_sector`
и меняет `NDefines.NCountry.CONSTRUCTION_CAMP_BUILDING`.

MR:
- своих `common/defines/` не имеет вообще — переопределение define не отбирается;
- `building_construction_sector` не определяет и не инжектит — только читает
  (`is_building_type`, `create_building`, `building_construction_sector_throughput_add`).
  Ключ здания PSC сохраняет, поэтому все эти ссылки остаются валидными;
- собственная группа `bg_architect` висит под `bg_public_infrastructure` —
  ветка, которую PSC не трогает;
- `bg_construction` упоминает ровно один раз, и то как имя модификатора
  `building_group_bg_construction_laborers_mortality_mult` — группа у PSC
  никуда не делась, только сменила родителя.

Законы не проверялись за отсутствием предмета: ни `common/laws`,
ни `common/law_groups` нет ни у одного из модов.

### 7. Игровые последствия совместной работы (не баги)

- Тесла-проект MR и события Гауди выдают/улучшают `building_construction_sector`.
  Под PSC сектор частный и производит строительные товары вместо очков напрямую —
  подарок остаётся полезным, ничего не ломается.
- `country_construction_add` и `state_construction_mult` от MR продолжают
  работать: PSC меняет источник очков строительства, но не сам ресурс.

---

## Что было удалено 21.08.2026

В папке лежал `common/on_actions/zz_pb_mr_on_actions.txt` — «мердж»
`on_monthly_pulse` из времён MR 2.6.3. Убран по трём причинам:

1. **Он не был нужен изначально.** `common/on_actions/` в 1.13 аддитивен:
   несколько модов, объявляющих `on_monthly_pulse = { on_actions = { ... } }`,
   склеиваются, а не затирают друг друга.
2. **Он ссылался на мертвьё.** В файле вызывался `mr_on_weekly_pulse`,
   которого в MR 2.8.3e нет ни в одном файле (`mr_on_actions.txt` определяет
   только `mr_on_monthly_pulse` и `mr_on_monthly_pulse_country`).
3. **Он давал двойной вызов.** Поверх штатных списков MR и PSC файл
   регистрировал `set_construction_weekly_on_action` и `mr_on_monthly_pulse`
   ещё раз, то есть PSC планировал бы всю свою недельную цепочку
   спроса/расходов на строительство дважды в месяц.

Файл перемещён в `vic3_mods/_to_delete/morg+psc_dead_on_actions_2026-08-21/`.
