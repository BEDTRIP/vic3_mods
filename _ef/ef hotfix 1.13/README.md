# E&F History Hotfix [1.13]

Мини-мод, который чинит два бага в **Economic and Financial (E&F)**, версия репозитория **04.07.2026**, на Victoria 3 **1.13.10**.

Компача E&F + Morgenröte не касается — работает и без него.

---

## Что чинит

Мод целиком заменяет один файл E&F: `common/history/buildings/00_ef_building.txt`.
Всё остальное содержимое файла скопировано побайтово, изменены ровно две вещи.

### 1. `s:STATE_ANDALUSIA` → `s:STATE_UPPER_ANDALUSIA` (строка 3615)

Такого стейта в игре нет. В ванили 1.13 Андалусия разделена на `STATE_LOWER_ANDALUSIA` и `STATE_UPPER_ANDALUSIA`.

В логе:

```
Error: Failed to scope to state region by key 'STATE_ANDALUSIA'
  Script location: common/history/buildings/00_ef_building.txt:3615
Error: Event target link 's' returned an unset scope
Error: region_state:SPA effect [ Wrong scope for effect: none, expected state_region ]
```

Из-за этого Испания **не получала стартовую серебряную шахту** (`building_silver_mine`, компания `company_basic_gold_and_silver_mining_2`, 5 уровней).

Выбран `UPPER` — это Хаэн/Альмерия, район Линареса и Ла-Каролины, крупнейшая испанская свинцово-серебряная добыча XIX века. Если задумка автора была про Рио-Тинто (Уэльва), правильным был бы `LOWER`.

### 2. Блок `#GRE` закомментирован (строки 3816–3879)

Это побуквенная копия блока `#PRU` с заменой `PRU` → `GRE`, включая `company_PreussischeSeehandlung` — прусский банк, выдающий Греции золотые и серебряные шахты **в Саксонии и Бранденбурге**.

Греция существует на 1836, но этими стейтами не владеет, поэтому `region_state:GRE` возвращает невалидный объект, и все пять `create_building` внутри выполняются в NULL-стейте:

```
Error: Event target link 'region_state' returned an invalid object
  Script location: common/history/buildings/00_ef_building.txt:3818
Error: create_building effect [ Scoped object is not valid. Type: Область NULL_STATE (x000000) ]
  Script location: .../3819, 3830, 3841, 3852, 3867
```

Это **главный подозреваемый по вылету** при старте игры: `create_building` в невалидном стейте.

Блок закомментирован, а не удалён — если автор E&F имел в виду реальные греческие рудники (Лаврион в Аттике), содержимое под рукой.

---

## Чего мод НЕ чинит

`common/history/buildings/00_ef_building.txt:2999` — вызов `financial_center_modifier = yes` внутри `every_country`. Внутри эффекта скриптовые значения `has_building_financial_centre_*` (`common/script_values/00_financial_scripted_value.txt`, строки 7027–7375) и `target_demand_bond_ajusted` (строка 3674) вычисляются в скоупе `none`:

```
Error: any_scope_state trigger [ Wrong scope for trigger: none, expected country, ... ]
Error: is_subject trigger [ Wrong scope for trigger: none, expected country ]
```

**1282 ошибки** за один старт игры — это самый шумный источник в логе, но лечится он внутри `financial_center_modifier` (`common/scripted_effects/09_introduction_building_lvl.txt:22135`), а это ~15 000 строк чужого кода. Копировать их в хотфикс смысла нет — это надо чинить автору E&F.

---

## Известные подозрительные места, оставленные как есть

`region_state:TAG` на страны, которые этим стейтом на 1836 не владеют. В логе ошибок не дают, потому что сама страна на старте не существует (движок молча пропускает ссылку) либо блок закрыт проверкой даты:

| Строки | Что | Почему безопасно |
|---|---|---|
| 850–1447 | `region_state:GER`, `region_state:NGF` в 17 немецких стейтах | GER/NGF на 1836 не существуют |
| 1499–1639 | `region_state:ITA` в Кампании, Ломбардии, Венето, Тоскане, Пьемонте | ITA не существует |
| 1703, 1790 | `region_state:CAN` в Квебеке и Онтарио | CAN не существует |
| 1890 | `region_state:AST` в Новом Южном Уэльсе | AST не существует |
| 2451, 2547, 2733 | `region_state:GBR` в Шаочжоу | внутри `if = { limit = { game_date > 1860 } }` |
| 2899 | `region_state:PEU` в Лиме | PEU на 1836 не существует |

Если E&F когда-нибудь добавит эти страны на старт или появится мод, который их добавляет, каждая строка отсюда превратится во вторую версию бага `#GRE`.

---

## Установка и порядок загрузки

1. Community Mod Framework
2. Expanded Topbar Framework (или Dence UI)
3. Economic and Financial (E&F)
4. **E&F History Hotfix (этот мод)**
5. Morgenröte
6. E&F + Morgenröte ComPatch

Главное — **после E&F**. Относительно Morgenröte и компача порядок не важен, они этот файл не трогают.

---

## ⚠️ Обслуживание

Мод **полностью перезаписывает** `common/history/buildings/00_ef_building.txt`.

Это значит: как только E&F обновится и что-то допишет в стартовую историю (новые финцентры, шахты, компании), **этот мод откатит все правки обратно**. При каждом апдейте E&F надо пересобирать файл заново:

```bash
cd C:/Users/Andrey/Projects/vic3_mods_out
# 1. изменился ли исходник?
diff "E&F/common/history/buildings/00_ef_building.txt" \
     "../vic3_mods/_ef/ef hotfix 1.13/common/history/buildings/00_ef_building.txt"

# 2. проверить, живы ли ещё оба бага
grep -n 'STATE_ANDALUSIA' "E&F/common/history/buildings/00_ef_building.txt"
grep -n -A3 '#GRE' "E&F/common/history/buildings/00_ef_building.txt"
```

Если оба бага исправлены автором — мод надо просто удалить.

Баги стоит отправить автору E&F: тогда хотфикс станет не нужен.
