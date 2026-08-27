# ComPatch Grey's + KAI

<!-- meta
пара: Grey's × Kuromi's AI (KAI)
статус: done
версии: Game 1.13 (exe 1.13.11) — Kuromi's AI 7.5, Grey's pack (версии моды не объявляют)
позиция: после KAI, после grey_usu и grey_diplo
файлов: 2
генератор: tools/regen_greys_kai_fix.py
зависит от: —
-->

## Для мастерской

[h1]ComPatch: Grey's + KAI[/h1]
[b]Game 1.13 (exe 1.13.11) — Kuromi's AI, Grey's pack.[/b]

Два фикса. Первый: grey_usu переиздаёт здание `building_government_administration` целиком и молча теряет AI-приоритет KAI на достройку при нехватке бюрократии. Второй: собственный переспор grey_diplo блока `ai` записи `foreign_investment_rights` заодно откатывает не переспоренный, а просто пропущенный багфикс KAI в `wargoal_score_multiplier` — эта часть возвращена, остальной переспор grey_diplo не тронут.

[h2]Load order[/h2]
[list]
[*]Kuromi's AI
[*]Grey's pack (soft_econ, soft_pop, USU, food, ranch, diplo, subject, …)
[*][b]this ComPatch[/b]
[/list]

---

## Подробности

**Game 1.13 (exe 1.13.11). Kuromi's AI 7.5; Grey's pack (declares no versions).**

Пара GR.8, пришла на замену старой паре с T&R+KAI на 128 ключей после решения от 25.08.2026 (T&R убран, осталась только часть с KAI). Порядок: KAI грузится рано (сразу после PSC), Grey's поздно — Grey's выигрывает любую общую запись.

## Пять ключей пары, что где закрыто

* **`building_construction_sector` [KAI vs grey_usu] — уже закрыт в `_greys/greys+psc done` (GR.2).** Тело оттуда несёт железную ветку KAI (`ai_value`, приоритет по железной руде) целиком. Свой файл на эту запись не пишем.
* **`NAI` [KAI vs `_grey_soft_econ`, grey_usu] — не потеря, `defines` сливаются по полю.** Тот же класс, что развилка №3 (GR.17, `NEconomy`/`PRICE_RANGE`) — категория `defines` не переопределяется целиком, каждое имя поля само по себе. Проверено: поля KAI (`REFORM_GOVERNMENT_*`, `SUPPLY_SHIP_*`, `MONEY_SPENDING_*`, `PRODUCTION_*`, `GOVERNMENT_BUILDING_*`, `CONSUMPTION_TAX_INCOME_VALUE`) не пересекаются по имени ни с полями `_grey_soft_econ` (`TRADE_CENTER_MINIMUM_GDP_*`), ни с полями grey_usu (`SUBSIDIZE_SHARE_OF_INFRA_FACTOR`, `OWNER_BUILDING_LOCATION_*`) — все три мода просто добавляют разные настройки в один общий блок. Файла не требует.
* **`ai_strategy_territorial_expansion` [KAI vs grey_subject] — уже смержено автором.** Тело grey_subject (`REPLACE_OR_CREATE:`, `MoG_diplomatic_strategies_SIS.txt`) несёт комментарий «Cannot INJECT weights in the correct sequence» — автор явно не смог применить `INJECT:` KAI по порядку и вместо этого переписал вручную то же самое: `undesirable_infamy_level = 50` и `unacceptable_infamy_level = 100` — побайтово те же числа, что несёт `INJECT:` KAI. Файла не требует.
* **`building_government_administration` [KAI vs grey_usu] — закрыт.** См. ниже.
* **`foreign_investment_rights` [KAI vs grey_diplo] — закрыт 27.08.2026, решением М.** См. ниже.

## Что теряется на `building_government_administration`

`INJECT:` KAI (`kai_buildings.txt`) добавляет `ai_value` — приоритет постройки для ИИ, который выше там, где не хватает налоговой ёмкости (`tax_capacity_usage` превышает `tax_capacity`). Тело grey_usu (`REPLACE_OR_CREATE:`, `yMoG_USU_government.txt`) такого поля не несёт вовсе — не переспор чисел, поле просто отсутствует. Отдельно от этого на той же записи уже потеряна и восстановлена группа Morgenröte `pmg_panum_hospital` (`_greys/greys+morg done`, GR.6) — оба фикса аддитивны друг к другу, не пересекаются.

`common/buildings/zz_greys_kai_fix_gov_admin.txt` — `TRY_INJECT:` блока `ai_value`, читается живьём из файла KAI.

## Что чинится на `foreign_investment_rights`

Тело grey_diplo (`TRY_REPLACE:`) — развёрнутый, откомментированный переспор блока `ai` KAI: та же структура `accept_score`, несколько чисел сознательно изменены с объяснением (штраф `law_isolationism` −300 → −100, одна добавка KAI явно отвергнута комментарием «wtf is this»). Этот переспор — дизайн автора grey_diplo, не тронут.

Но один под-блок выпал без единого комментария рядом, в отличие от всех остальных правок в том же файле: `wargoal_score_multiplier` у KAI несёт собственный багфикс с пояснением — «Replaced target_country, which is actually the attacker, with source_country… Added a check against subjects, since the treaty will be broken immediately if a country does not have diplomatic autonomy» (в ванили здесь проверялась не та страна, и договор о правах инвестиций рвался сразу же, если его требовали у вассала). Тело grey_diplo молча откатывает оба — обратно на `scope:target_country` и без исключения для вассалов.

Решение М от 27.08.2026: смержить — оставить переспор grey_diplo everywhere else, вернуть только этот под-блок из KAI. `common/treaty_articles/zz_greys_kai_fix_foreign_investment_rights.txt` — `TRY_REPLACE:` всей записи телом grey_diplo, с `ai.wargoal_score_multiplier` заменённым на тело KAI (оба читаются живьём). Полный `TRY_REPLACE:`, а не точечный `TRY_INJECT:`, потому что обе стороны объявляют `wargoal_score_multiplier` с одинаковыми именами полей и разной логикой — инжект не разрешит, чьё тело побеждает внутри под-блока, только полная замена записи однозначна.

## Пересборка

`tools/regen_greys_kai_fix.py`; `--check` печатает `SAME`/`DRIFT` и ничего не пишет.
* `ai_value`: падает с сообщением, если тело grey_usu вдруг обзаведётся собственным `ai_value`.
* `wargoal_score_multiplier`: падает, если тело KAI перестанет нести пометку `source_country`/`is_subject = yes`, или если тело grey_diplo перестанет быть откаченной версией (`target_country`, без `is_subject = yes`) — оба случая значат, что кто-то из авторов поменял эту часть, сверять заново.
