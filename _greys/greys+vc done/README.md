# ComPatch: Grey's + Victorian Century

<!-- meta
пара: Grey's × VC
статус: done
версии: Game 1.13 (exe 1.13.11) — Victorian Century (версии нет в metadata), Grey's: USU / soft_pop / soft_econ / food / ranch (версий нет в metadata)
позиция: грузится после Victorian Century и после всей пачки Grey's
файлов: 7 (шесть плюс `.off`-двойник у zz_gvc_companies.txt, добавлен 27.08.2026 -- GR.16)
генератор: tools/regen_greys_vc.py
зависит от: Grey's (обязателен), Victorian Century (обязателен для пяти файлов из шести; zz_gvc_companies.txt теперь нужен и без VC, если используется аддон-LLWA -- см. решение №9 и раздел GR.16 ниже)
-->

## Для мастерской

[h1]ComPatch: Grey's + Victorian Century[/h1]
[b]Game 1.13 (exe 1.13.11).[/b]

Victorian Century and the Grey's family of mods rewrite the same records — both with full bodies. Grey's loads later, so the last body wins and VC's version of those records is simply gone. Nothing appears in the error log; the traits, companies and methods are still there, they just say what Grey's says.

What stops working with both mods installed and no compatch:

[list]
[*][b]60 state traits[/b] — every river, bay and terrain trait both mods rewrite. VC's river defence bonuses, market-access impacts and construction-sector slots disappear.
[*][b]6 companies[/b] — Grey's USU moves Mantetsu, the Orient Express, the Prussian State Railways, the Great Indian Railway, Panama and Suez onto its own railway building, replacing the whole record. VC's prestige goods, prosperity modifiers and culture gates go with it.
[*][b]10 production methods[/b] — the four construction methods, the three subsistence defaults and the passenger-carriage methods. VC injects into them, USU re-issues them whole.
[*][b]2 buildings[/b] — VC's private-construction gate on the food industry and the livestock ranch.
[*][b]popneed_basic_food[/b] — VC's groceries weight, and with it the whole VC × TGR merge the VC addon already made for that record.
[*][b]VC's own 17 port traits[/b] — Grey's Soft Pop rewrites the cultural-community script and its harbour bonus still lists only the six vanilla harbours, so none of VC's ports count.
[/list]

This compatch puts VC's contribution back on top of Grey's bodies, field by field. The rule is the same everywhere: [b]Grey's wins wherever it made a real decision, VC's value survives where Grey's body only re-stated vanilla[/b]. Grey's redesigns (the river-port system, the pop-need rework, the demography defines) are left alone on purpose — they are the newer design and they are internally consistent.

[h2]Load order[/h2]
[list]
[*]Victorian Century
[*]… the whole Grey's pack (Soft Econ, Soft Pop, USU, Deeper Cinosphere, Food, Ranch, Diplo, Subject)
[*][b]this ComPatch[/b]
[/list]

Requires both. Every file is generated, and every merged record carries its own merge log in the comments above it.

---

## Что теряется без этого компача

`pair_matrix.py --pair "VC,Grey's"` — **129 общих ключей, 0 общих путей файлов**. Разобраны все 129; содержательных потерь шесть классов, остальное — не конфликт (см. ниже).

| категория | сколько | что происходит |
| --- | --- | --- |
| `common/state_traits` | 60 | VC `REPLACE_OR_CREATE:` полным телом, `grey_usu` `TRY_REPLACE:` полным телом. USU позже — ни один из 60 трейтов VC не работает |
| `common/company_types` | 6 | `grey_usu` `TRY_REPLACE:` полным телом ради переезда на `building_usu_railway_line`; вместе с этим уходят престижные товары VC, его модификаторы процветания, культурные гейты и ai-веса |
| `common/production_methods` | 10 | VC `INJECT:`, USU переиздаёт запись целиком (`REPLACE_OR_CREATE:` стройки и `TRY_REPLACE:` subsistence) |
| `common/buildings` | 2 | VC `TRY_INJECT: can_build_private` (его гейт автономных инвестиций), `grey_food` и `grey_food_2_ranch` переиздают здание целиком |
| `common/pop_needs` | 1 | `popneed_basic_food`: тело `grey_food_2_ranch` — **дословная ваниль**, и оно съедает не только VC-шный вес бакалеи 1.5, но и весь мердж VC × TGR, который аддон-VC для этой записи уже сделал (`max_supply_share` 0.3 / `min_supply_share` 0.2 от TGR на всех пяти строках) |
| `common/script_values` | 1 | `cultural_community_creation_weight`: `_grey_soft_pop` переписывает скрипт целиком, и его портовый бонус знает только шесть ванильных гаваней — 17 портовых трейтов VC не считаются нигде |

## Что внутри

| файл | записей | что делает |
| --- | --- | --- |
| `common/state_traits/zz_gvc_state_traits.txt` | 60 | тело USU + поля VC: 83 добавлено, 28 чисел VC возвращено там, где USU только переизложил ваниль; 11 полей VC не восстановлены — USU намеренно убрал их вместе с ванильными |
| `common/company_types/zz_gvc_companies.txt` | 6 | мердж по под-блокам, ваниль как общий предок |
| `common/production_methods/zz_gvc_methods.txt` | 10 | инжекты VC, переизданные дословно |
| `common/buildings/zz_gvc_buildings.txt` | 2 | то же для `can_build_private` |
| `common/pop_needs/zz_gvc_pop_needs.txt` | 1 | тело аддона-VC (VC + TGR) + два инжекта ranch, внесённые в тело |
| `common/script_values/zz_gvc_cultural_community_weight.txt` | 1 | тело soft_pop + 17 портовых трейтов VC в список гаваней |

Пять из шести файлов помечены баннером `=== VC-ONLY FILE ===`: с решения №11 (26.08.2026) VC опционален, и без него можно удалять всю папку компача целиком. **Исключение с 27.08.2026 (GR.16): `common/company_types/zz_gvc_companies.txt`.** Шесть компаний в нём -- это ровно те же шесть, что нужны аддону-LLWA (grey_usu полным телом молча сбрасывает и вклад VC, и вклад аддона-LLWA на одних и тех же записях). Поэтому у этого файла теперь два режима, тег `=== CARRIES A VC LAYER ===` вместо `VC-ONLY` (решение №9):

* играете с VC (и, может быть, с аддоном-LLWA) -- ничего делать не надо, `zz_gvc_companies.txt` активен по умолчанию;
* играете с аддоном-LLWA, но **без** VC -- переименуйте `zz_gvc_companies.txt.off` в `zz_gvc_companies.txt` (заменив активный файл): тот же ремонт для шести компаний, но без слоя VC;
* не используете ни VC, ни аддон-LLWA -- удаляйте всю папку компача целиком, как раньше, оба варианта файла не нужны.

Остальные пять файлов (`state_traits`, `production_methods`, `buildings`, `pop_needs`, `script_values`) остаются чисто VC-шными без исключений.

## Как сделан мердж

**Одно правило на весь компач: намерение — это отличие от ванили.**

Мод, который пишет полное тело, переизлагает *все* поля записи, в том числе те, которые ему безразличны. Поэтому «USU тоже называет это поле» ничего не доказывает. Доказывает только разница с ванилью:

* поле, которое **USU подвинул** относительно ванили → остаётся USU. Это его решение;
* поле, которое **USU переизложил ванильным же значением**, а VC изменил → берётся значение VC. USU тут ничего не выбирал;
* поле, которое **USU намеренно убрал** (в ванили было, в его теле нет) → не восстанавливается, даже если VC его настраивал;
* поле, которого **у USU нет, а у VC оно новое** → дописывается.

Тот же принцип на уровне под-блоков у компаний: список (`building_types`) объединяется по тем же правилам поэлементно, блок-«мешок модификаторов» — по полям, а под-блок, который **оба переписали** (`possible`, `potential`), достаётся USU целиком; под-блок, которого у USU нет, а у VC есть (`possible_prestige_goods` у Мантэцу), дописывается.

Почему база — тело Grey's, а не VC: у USU `state_building_river_port_max_level_add` и урезанная `state_infrastructure_add` — **одна система**. Река у него даёт не инфраструктуру напрямую, а уровень речного порта. Взять числа инфраструктуры от VC и уровни портов от USU — значит выдать реке и то и другое (решение от 27.08.2026).

Десять методов и два здания **не мерджатся вообще**: там переиздан дословный `INJECT:` самого VC, файлом, который грузится после Grey's. По правилу из `Правила работы с модами Victoria 3.md`, раздел «Переопределение», переиздание чужого `INJECT:` поверх более позднего тела — точное восстановление. Плюс это не зависит от того, чем разрешится открытый вопрос про семантику под-блоков у `REPLACE:`: что бы движок ни делал с инжектом VC поверх ванили, ровно то же он сделает с ним поверх тела USU.

## Что намеренно не тронуто

Разобрано и признано не конфликтом — файлов на это нет:

* **10 `combat_unit_types`** — оба мода `INJECT:` в один `upkeep_modifier`, но непересекающимися ключами (VC — стрелковка и боеприпасы, USU — `goods_input_usu_logistics_add`). Блоки модификаторов складываются, выживает и то и другое;
* **3 `mobilization_options`** — VC инжектит `upkeep_modifier`, USU `upkeep_modifier_unscaled`. Разные под-блоки;
* **27 из 33 общих компаний** — USU трогает их через `TRY_INJECT:`, а инжект в список добавляет, а не заменяет, и в блоке модификаторов складывается. Ничего не вытесняется;
* **`company_putilov_company`** — 34-я общая компания и седьмое полное тело, которого нет. USU пишет её как `TRY_INJECT::company_putilov_company` — **два двоеточия**. Битый префикс не грузится вообще (тот же класс, что `REPLACE:REPLACE:`), так что до записи USU не доходит и тело VC цело. Ещё две записи с той же опечаткой в том же файле — `company_john_holt`, `company_lanfang_kongsi`. Это поломка Grey's сама по себе, без всякого VC, и чинится отдельной внутриблочной задачей (GR.20), а не здесь;
* **5 из 6 `pop_needs`** — `popneed_heating` у VC дословно ванильный, терять нечего; `popneed_communication`, `popneed_free_movement`, `popneed_leisure`, `popneed_luxury_food` — осознанный редизайн Grey's (везде добавлены `services` и `min_supply_share`, шкала пересчитана), он выигрывает по существу;
* **3 `defines`** — `NAI` и `NEconomy` пересекаются только именем группы, общих листовых ключей нет вовсе. У `NPops` общих шесть, расходятся четыре (`CULTURAL_COMMUNITY_LINGER_TIME_WEEKS` 120/5, `CULTURAL_COMMUNITY_MAX_PER_MONTH_CHANCE` 0.1/1.0, `JOB_SATISFACTION_BASE` −180/−120, `WORKING_ADULT_RATIO_SKEW_MAXIMUM` 50/4.0) плюс `WORKING_ADULT_RATIO_BASE`, где soft_pop возвращает ванильные 0.25 поверх 0.30 VC. Решение 27.08.2026: **числа остаются за soft_pop** — его демография это цельная настройка, а числа VC под неё никто не считал;
* **`state_region_devastation`** — `_grey_soft_econ` переписывает статик-модификатор осознанно и с комментариями, и трогает ровно то единственное поле, которое меняет VC (`state_devastation_decay_mult` 3.0 против 2.5). По тому же правилу, что и трейты, поле остаётся за soft_econ. Второе изменение VC (`building_throughput_add` −0.5) soft_econ и так сделал сам, тем же числом.

## Открытые вопросы

* **`state_trait_columbia_river` — та же запись, что в HC.7 и GR.4d.** Здесь её тело построено на USU, вклада Hail, Columbia! в нём нет: в ветке VC блока HC вообще не существует, а в ветке «оба сразу» его тело и так съедено USU до нас. Когда GR.4d будет закрыта, её слой обязан лечь в эту же запись — по той же причине, что и слой GR.16 в компании;
* **`popneed_basic_food` закрывает и свой пункт из GR.18.** А вот остальные пункты GR.18 по pop_needs решение «редизайн Grey's выигрывает» не закрывает: оно принималось против чисел VC, а не против TGR-слоя аддона-VC, которого в тех записях, впрочем, и нет — проверено, аддон-VC пишет только `popneed_basic_food`;
* **Шесть компаний этого файла — те же, что в GR.16.** `company_great_indian_railway`, `company_mantetsu`, `company_orient_express`, `company_panama_company`, `company_prussian_state_railways`, `company_suez_company` теряют ещё и `LLWA_building_roadway` / `LLWA_building_waterway` от аддона-LLWA — по той же причине и в том же `TRY_REPLACE:` USU. Здесь этого слоя нет: пара другая. Когда GR.16 будет закрыта, её слой обязан лечь **в эти же записи**, а не в отдельный файл — иначе два `REPLACE_OR_CREATE:` на одну запись, и побеждает тот, чьё имя файла позже. Тогда же файл перестанет быть чисто VC-шным и получит тег `=== CARRIES A VC LAYER ===` с `.off`-двойником (решение №9);
* **`potential` и `possible` у Мантэцу достались USU целиком.** У VC там было шире: `country_has_primary_culture = cu:japanese` **или** `cu:russian`, `has_state_in_state_region` вместо `country_or_subject_owns_entire_state_region`, `count >= 1` вместо `2`. Оба мода переписали блок, правило отдаёт его USU. Если захочется вернуть — это ручной мердж триггера, а не поле;
* **`prestige_good_japanese_express`** приезжает вместе с записью Мантэцу. Против лимита «три престижных товара на базовый» набор считался в VC.7 — при добавлении компании лимит не меняется, но пересчитать после сборки аддона стоит.

* **`thumbnail.png` не сделан**, а `metadata.json` на него ссылается. Тот же статус, что у
  аддона-LLWA и HC.11: компач в мастерскую пока не выкладывается, id нет.

## Пересборка

```
python3 tools/regen_greys_vc.py           # переписать компач
python3 tools/regen_greys_vc.py --check   # только отчёт, код 1 если источники разъехались
```

Генератор печатает **каждое** принятое решение построчно (что добавлено, где число VC победило переизложенную ваниль, что не восстановлено) и падает с внятным сообщением, если чужой мод сменил префикс, перестал определять запись или если тело `grey_food_2_ranch` для `popneed_basic_food` перестало быть дословной ванилью — то есть если довод в пользу этого файла исчез.
