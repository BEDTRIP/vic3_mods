[h1]E&F Currency Merge [1.13][/h1]
Economic and Financial ships one market good per currency — 57 of them live, 95 declared. Victoria 3 1.13 cannot hold more than 128 goods in total, and it does not say so: above the ceiling the game crashes on entering a campaign with nothing in error.log. Those 57 are what stops E&F from sharing a build with any other large mod.

This mod collapses them into a single good. [b]Nothing about the monetary system is removed.[/b] All 95 currency laws stay, every country keeps its own law and its own mint, exchange rates, gold and silver standards, money supply, stockpiles, debt and the crisis chain all keep working exactly as before. Only the thing that travels on the market is shared.

[h2]Load order[/h2]
[list]
[*]Economic and Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3786286962]E&F Hotfix[/url] — [b]required[/b], this mod is built on top of its goods list
[*][b]This mod[/b]
[*]anything else
[/list]

[h2]What it buys you[/h2]
[table]
[tr][td][/td][td]goods[/td][/tr]
[tr][td]vanilla 1.13.10[/td][td]53[/td][/tr]
[tr][td]+ Private Sector Construction[/td][td]57[/td][/tr]
[tr][td]+ E&F with the Hotfix[/td][td]122[/td][/tr]
[tr][td]+ Morgenröte[/td][td]127[/td][/tr]
[tr][td]+ Tech & Res[/td][td][b]162 — crash[/b][/td][/tr]
[tr][td]the same pack with this mod[/td][td][b]106[/b][/td][/tr]
[/table]

22 slots to spare, and Tech & Res stays whole — no cutting eras, data goods or androids.

[h2]Why this is safe[/h2]
E&F's currency machinery does not run on the goods. It runs on country and global variables: [i]money_value_*[/i], [i]money_value_in_gold_*[/i], [i]stockpiling_*[/i], [i]export_to_*[/i], [i]import_from_*[/i], [i]var:money_value_target_1[/i] — all of them variables set by E&F's own monthly and yearly effects, none of them reading a market price.

Of the 36 script-value families E&F defines per currency, [b]14 are referenced nowhere at all[/b] — including every single one that reads [i]market.mg:<currency>.market_goods_*[/i]. The only live consumer of a currency good's market data is the overlord-buys-subject-currency path, and E&F's own author disabled its production method group on the central bank years ago with the comment "caché suppretion suite à trop de bug".

So the merge touches goods, production methods, pop needs, and the bookkeeping that names goods. Nothing else.

[h2]What actually changes in play[/h2]
[list]
[*][b]Within one market, currencies stop having separate prices.[/b] Today the British market carries the pound, the rupee, the Canadian and Australian dollars as four goods with four prices; now it carries one. Between markets nothing changes — France has its own market and its own price for the same good, so an exchange rate is still the ratio of two prices.
[*][b]Inflation stops being national inside a shared market.[/b] If India over-issues today, the rupee cheapens and the pound does not. Afterwards, over-issue by anyone in the market cheapens the currency for everyone in it. For a colonial empire that is arguably the point — the cost of the empire's money is the empire's problem.
[*][b]Pops barely notice.[/b] They already pooled currencies: [i]popneed_currency[/i] weighs every currency on the same market by its share of sell orders, so a London pop was already covering part of its need with rupees.
[*][b]local_currency is untouched[/b] — countries with no monetary system still issue it, at the Hotfix's computed rate, at weight 0.1 against 0.25.
[/list]

[h2]Bonus: 38 dead references fixed[/h2]
E&F declares 95 currency laws and 95 × 3 production methods against 57 live goods. 38 of those production methods, and their pop-need entries, modifier types, static-modifier lines and script values, already pointed at goods its own author had commented out. All 95 are retargeted here, so those go away too.

[h2]Known[/h2]
[list]
[*][b]Load-time log lines.[/b] E&F's original definitions are still parsed before this mod's replacements win, so the currencies whose goods are gone may each cost a line in error.log at load. That is the same class of noise E&F already ships with its own 38 dead currencies — nothing points at a missing good at runtime. If the log turns out to be unbearable, the generator has a switch to emit whole-file overrides instead; see below.
[*][b]The currency panel still lists every currency.[/b] E&F's GUI draws one entry per currency law, and the laws are all still there. Entries for currencies nobody issues will read zero — same as today.
[/list]

[h2]Валюты вернулись — престижными товарами[/h2]

Престижные товары не занимают слот в базе из 128 — это измерено, а не предположено:
сотня пустышек на одном базовом товаре грузится нормально. Поэтому все 95 валют
возвращаются как престижные варианты общего товара: со своими названиями, своими
иконками, престижем за место в лидерборде и движковым +20% к пропускной способности
зданиям, которые их потребляют.

**Ключ престижного товара — тот же, что был у товара-валюты** (`pound_sterling_c`).
Как товар он закомментирован слиянием, имя освободилось, и вся локализация E&F в
одиннадцати языках плюс отдельный русский мод продолжают работать без единой правки.
Иконки тоже.

**Кто какую валюту выпускает, решает не компания, а закон.** Связь компания → страна
из файлов не выводится: тег назван у 6 компаний из 103, остальные опознаются по
интерес-маркерам и регионам. Поэтому все 97 банковских компаний E&F получают все 95
престижных валют, а у каждой престижной валюты стоит

```
possible = { has_law = law_type:law_<валюта>_currency }
```

Страна с законом фунта может совпасть ровно с одной.

**Центробанк стал владеемым.** Компания производит престижный товар только из
здания, которым владеет, а `ownership_type = no_ownership` означает, что долей
владения у здания нет вовсе. `common/buildings/zz_ef_cm_bank.txt` выдаёт определение
`building_bank` из E&F целиком, с единственной заменой на `ownership_type = self`, и
`building_bank` дописывается в `building_types` всех банковских компаний — E&F держит
там `#building_bank` закомментированным, потому что раньше это и не могло работать.

Определение выдаётся целиком не для красоты: **`REPLACE:` заменяет запись полностью,
а не перечисленные поля.** Отправленный однажды `REPLACE:building_bank = {
ownership_type = self }` убрал центробанк из игры вовсе.

[h2]Если владение не заработает без второго шага[/h2]

Казённым здание делают две независимые вещи, и E&F выставил обе:

| где | что |
|---|---|
| `building_bank` | `ownership_type = no_ownership` — снято |
| `bg_bank` | `is_government_funded = yes` — НЕ снято |

Второе по умолчанию не трогается, потому что это не переключатель, а
перебалансировка. `is_government_funded` означает, что казна платит за входы и
зарплаты банка и забирает выпуск. Выключаем — центробанк становится частным
бизнесом, и по британскому сейву 1836 года его 200 облигаций плюс валюта против
~2.5K расходов превращаются из статьи бюджета в прибыль, дивиденды и приток в
инвестиционный пул, каждый месяц, у владельца центробанка.

Если окажется, что без этого компания банк не берёт:

```
python3 tools/regen_ef_currency_merge.py --private-bank
```

и смотреть не на вкладку владения, а на инвестиционный пул через десяток лет.

[h2]Что проверить[/h2]

[list]
[*]Британия → панель компаний → Банк Англии → вкладка [b]Активы[/b]. Центральный банк там? Это главное.
[*]Дожать компанию до «процветающей» — престижная доля должна появиться у товара «Валюта» в панели рынка, с названием «Фунт стерлингов» и своей иконкой.
[*]В самом банке выпадающий список выпускаемой валюты должен показывать [b]одну[/b] строку, а не 95: замок — это `unlocking_laws`, который вернулся вместе с полными определениями PM.
[*]`error.log` — искать `building_bank`, `prestige`, `possible`.
[/list]

[i]Мод[/i] `bank ownership test` [i]при этом надо выключить — он делает то же самое и будет конфликтовать.[/i]

---

## Сопровождение

Весь мод генерируется, руками не правится:

```
python3 tools/regen_ef_currency_merge.py --check   # разъехалось ли
python3 tools/regen_ef_currency_merge.py          # пересобрать
python3 tools/regen_ef_currency_merge.py --keep spe_uni_c
```

Гонять после каждого обновления E&F и после каждого изменения хотфикса — хотфикс
здесь источник истины для `common/goods/ef_00_goods.txt` и `common/pop_needs/`,
E&F для всего остального.

| файл | что делает |
|---|---|
| `common/goods/ef_00_goods.txt` | 56 валют закомментированы |
| `common/pop_needs/00_ef_pop_needs.txt` | 94 записи `popneed_currency` убраны, осталось две |
| `common/modifier_type_definitions/00_ef_building_modifier_types.txt` | 376 осиротевших типов модификаторов убраны |
| `common/static_modifiers/00_ef_dynamic_modifier_{building,country,state}.txt` | список из 95 одинаковых строк схлопнут в одну |
| `common/named_colors/00_ef_goods_colors.txt` | 94 цвета мёртвых товаров убраны |
| `common/production_methods/zz_ef_cm_production_methods.txt` | 285 `REPLACE:` — только `building_modifiers` |
| `common/script_values/zz_ef_cm_script_values.txt` | 1130 значений, читавших товар |
| `common/scripted_triggers/zz_ef_cm_scripted_triggers.txt` | `market_goods_is_currency` |

Почему `REPLACE:` только на `building_modifiers`, а не на PM целиком: `REPLACE:`
меняет только те под-блоки, которые перечислены, поэтому `texture`,
`unlocking_laws` и `is_hidden_when_unavailable` продолжают приходить из E&F —
переименование закона там не требует правки здесь.
