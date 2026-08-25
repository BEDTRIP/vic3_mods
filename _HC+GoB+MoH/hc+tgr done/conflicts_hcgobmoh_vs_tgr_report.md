# HC + GoB + MoH × The Great Revision — разбор пары

Дата разбора: 2026-08-24. Игра 1.13 (exe 1.13.11).
Версии: TGR 2.0 (1.13.10, 12.08.2026), Hail, Columbia! 8.6-Roosevelt, Gates of the Bosphorus 4.0.8, Mandate of Heaven 1.4.6.1.
Порядок: CMF → TGR → … → HC → GoB → MoH → **компач**.

Машинный прогон `pair_matrix.py --pair "HC+GoB+MoH,TGR"`: **16 общих ключей, 3 общих пути, 0 общих id событий.**
Содержательных — пять. Две записи, которые прогон показывает как конфликт, закрыты обоснованием.

## Требуют работы — сделано

### 1. `ig_landowners` и `ig_rural_folk` — переработка TGR пропадает целиком

| | `ig_landowners` | `ig_rural_folk` |
| --- | --- | --- |
| ваниль | 769 строк, голое тело, `00_landowners.txt` | 556 строк, голое тело, `00_rural_folk.txt` |
| TGR | 772, `REPLACE_OR_CREATE:` из `TGR_POLITICS_landowners.txt` | 563, `REPLACE_OR_CREATE:` из `TGR_POLITICS_rural_folk.txt` |
| Hail, Columbia! | 788, **голое тело по ванильному пути** `00_landowners.txt` | 560, то же по `00_rural_folk.txt` |
| Mandate of Heaven | — | 316, `INJECT:` из `moh_rural_folk.txt` |

HC грузится позже TGR и кладёт голое тело по ванильному пути — переработка TGR исчезает вся. Молча: группа на месте, у неё просто ванильные числа.

Что TGR на самом деле меняет — четыре числа, всё остальное в его 772 и 563 строках дословная ваниль:

| | ваниль | TGR |
| --- | --- | --- |
| `pop_weight` → `LEADER_POPULARITY` множитель (обе группы) | 0.0025 | **0.030** |
| `pop_weight` → `POP_FARMERS` (rural folk) | 200 | **250** |
| `pop_weight` → `POP_PEASANTS` (rural folk) | 200 | **150** |

Что меняет HC: `usfp_country_is_american` в `on_enable` обеих групп, правило «южные плантаторы не считаются вне рабовладельческих штатов во время Гражданской» в `pop_weight` у landowners, и исключение американских культур из аристократов в `pop_potential` у rural folk.

**Решение:** база — тело HC, числа TGR вмерджены в `pop_weight` трёхсторонним мерджем против ванили (чтобы будущая правка любого из авторов дала конфликт, а не пропала). Изменение TGR `scope:interest_group ?= {` → `= {` НЕ переносится: и ваниль, и HC пользуются безопасной формой, у TGR это выглядит побочным, а строгая форма — та, что может выстрелить.

### 2. Копия ванили внутри `moh_rural_folk.txt` — попутная находка

Из пятнадцати под-блоков, которые MoH инжектит в `ig_rural_folk`, **своих у него ровно два**:

* `character_ideologies` → `ideology_moh_kmt`;
* `on_enable` → переименование группы в *Nongmin* для китайских культур.

Остальные тринадцать — копия **до-1.13** ванильного тела:

| под-блок | что не так |
| --- | --- |
| `monarch_weight`, `female_politician_chance`, `female_agitator_chance` | `has_law` вместо `has_law_or_variant` |
| `female_politician_chance` | нет ветки `law_stance`, которую ваниль 1.13 добавила |
| `on_character_ig_membership` | **пустой**, у ванили там правило религии Занзибара на 18 строк |
| `priority_cultures` | нет ванильного правила ZAN |
| `agitator_weight` | `owner.ig:ig_rural_folk = {` вместо `?= {` |
| `commander_leader_chance` | 1.13 переименовала поле в `commander_leader_weight` |
| `pop_potential`, `pop_weight`, `commander_weight`, `noble_chance`, `on_disable`, `female_commander_chance` | дословная ваниль, ноль своих идентификаторов |

Тот же класс, что стухший `03_political_strategies.txt` у LLWA: что бы движок ни делал с под-блоком, инжектнутым поверх уже существующего, такая копия может только отнять. Мердж несёт два реальных добавления MoH и текущую ваниль во всём остальном. Автору написать.

### 3. `ideology_jacksonian_democrat` — две позиции по законам

| | тело | под-блоки |
| --- | --- | --- |
| ваниль | 125 строк | …`lawgroup_slavery`, `lawgroup_citizenship`… |
| TGR | 19, `INJECT:` | `lawgroup_election_system`, `lawgroup_legislative_process` |
| Hail, Columbia! | 119, `REPLACE_OR_CREATE:` | governance_principles, distribution_of_power, bureaucracy, **colonization**, **land_reform** — ни election_system, ни legislative_process |

`REPLACE` меняет запись целиком, а не под-блоки, которые мод перечислил (проверено в игре 21.08.2026, см. `zzzz_ef_tr_fix_gold_minting.txt`). Значит обе позиции TGR теряются: джексоновский лидер не имеет мнения ни об избирательной системе, ни о законодательном процессе. Читается как «нейтрально» и не логируется.

**Решение:** тело HC без изменений + два блока TGR в хвост. Пересечения нет — HC этих групп не называет.

### 4. Две стартовые компании

| путь | кто везёт | ваниль | что теряется |
| --- | --- | --- | --- |
| `common/history/countries/chi - china.txt` | TGR (41 строка) и MoH (82) | 36 | MoH выигрывает путь → не основывается `company_ong_lung_sheng_tea_company` |
| `common/history/countries/tur - ottoman empire.txt` | TGR (51) и GoB (99) | 45 | GoB выигрывает путь → не основывается `company_imperial_arsenal` |

Компания, которую не основали, ошибки не даёт.

**Решение:** файл победителя + блок `add_company` от TGR внутрь эффекта страны.

## Не конфликты

| ключ / путь | почему |
| --- | --- |
| `common/decisions/manifest_destiny.txt` | HC везёт этот файл **с полностью закомментированным решением** — он намеренно убирает ванильное решение и заменяет его журнальной цепочкой на 1112 строк (`usfp_manifest_destiny.txt`). Переработка TGR уходит вместе с файлом, `great_revision_events.5` и `great_revision_usa_manifest_destiny` становятся недостижимы (в TGR на них не ссылается больше ничего). Вернуть решение TGR — значит дать игроку две Manifest Destiny. Это замысел HC, а не конфликт |
| `je_oregon`, `je_conquer_oregon` | HC переписывает оба из `common/journal_entries/00_oregon.txt` и выигрывает путь. Единственное содержательное у TGR — перенос из `je_group_usa_manifest_destiny` в `je_group_historical_content`, а группой владеет HC. **Плюс: файл TGR — копия старой ванили** (синтаксис `region_pacific_coast` без `sr:`, строгие скоупы вместо `?=`, нет блока хомленда Британской Колумбии, `months = normal_modifier_time` = 152 года). Автору написать |
| `ig_armed_forces`, `ig_intelligentsia`, `ig_petty_bourgeoisie` | TGR `REPLACE_OR_CREATE`, затем MoH `INJECT` в `character_ideologies` / `on_enable`. Аддитивно |
| `ideology_communist` | TGR `INJECT` в `lawgroup_working_hours`, MoH `INJECT` в `interest_group_leader_weight`. Разные под-блоки |
| `law_ethnostate`, `law_freedom_of_conscience`, `law_protectionism` | последним по каждому идёт `INJECT:` HC (`on_activate` / `is_visible`), TGR — раньше и в другие под-блоки |
| `law_canton_system`, `law_theocracy` | последним идёт `INJECT:` MoH (`modifier` / `is_visible`) |
| `NAI` | дефайны сливаются поключево. HC ставит один `NUM_GROWING_COLONIES_MAX = 7`; ни TGR, ни KAI его не трогают |
| `ai_strategy_default` | пересечение реальное, но чинится в паре с T&R+KAI — см. `conflicts_hcgobmoh_vs_trkai_report.md` |

## Проверки

* товаров компач не добавляет — набор остаётся 111 из 128;
* id событий: 0 пересечений;
* локализацию не трогает;
* `.gui` не трогает.
