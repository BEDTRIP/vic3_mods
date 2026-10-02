# E&F Hotfix

<!-- meta
мод: свой хотфикс E&F 1.13
статус: done, переписан под E&F 02.09.2026 (EF.1-EF.8), торговля/формула/престиж
  возвращены на liquidity_currency (EF.9), local_currency и liquidity_currency
  объединены в один товар (EF.10) — тем же вечером, см. План проекта.md;
  09.09.2026 — меню компаний переделано (EF.11), см. «The companies panel»
версии: —
позиция: —
файлов: 290 (из них 132 локализации)
генератор: tools/regen_ef_psc_copies.py (стройка PSC, с 02.10.2026); regen_ef_* по разделам;
  валютный — списан 02.09.2026 (tools/_to_delete/regen_ef_currency_merge_retired_2026-09-02.py)
зависит от: E&F, PSC (3420714166) — с 02.10.2026
-->

## Обновление 02.10.2026 — компач E&F × PSC вошёл в хотфикс (СТР.6)

Решено пользователем 30.09: почти вся переделка E&F (стройка, ставка, деньги) опирается на PSC,
держать два мода смысла мало. Компач `ef+psc` (мод 3640702353) целиком переехал сюда; хотфикс
теперь **зависит от PSC**. Папка, id в Мастерской (3786286962) и порядок запуска прежние:
**PSC → E&F → хотфикс**. Будущее имя «E&F: Rebalance» и редизайн страницы — вместе с UI (блок З).

* Файлы компача лежат здесь под теми же именами (`zz_pb_ef_*`, `00_ef_companies.txt`,
  `zz_financial_scripted_effects.txt`, `zz_ef_buttons.txt`, локали в `replace/`). Что они делают
  и история — раздел «Стройка: PSC (бывший компач E&F × PSC)» ниже.
* `common/history/buildings/00_ef_building.txt` — одна версия: ручные правки хотфикса +
  замена `building_ef_private_construction` → `building_construction_sector`, которую
  `tools/regen_ef_psc_copies.py` делает **прямо в файле** (ручные правки не затираются).
  `00_ef_companies.txt`, `establish_bank_and_ef_compagnie` и строки журнала УФС генератор
  копирует из E&F в хотфикс.
* Журнал УФС (`financial_center_je_2`) переиздаёт один файл —
  `journal_entries/zz_pb_ef_financial_center_je.txt` (из компача); хотфиксовый
  `zz_ef_financial_center_je.txt` удалён — он и раньше проигрывал компачу по порядку.
* Поведение в игре не меняется: внутри хотфикса и в мегапаках побеждают те же тела, что и
  раньше (разбор порядка — `План проекта.md`, СТР.6). Мегапаки больше не несут файлов `ef+psc`,
  кроме слитой с T&R `script_values/zz_pb_ef_psc_scope_fix.txt` (`megapack`, `megapack no tgr`)
  и TGR-локали групп акций, которую несёт и `ef+tgr`.

## Обновление 02.09.2026 — E&F слил валюты сам

Автор E&F в этом обновлении сделал то же слияние 95 национальных валют, что
раньше делали мы: почти все главы ниже (генератор, `spe_uni_c` как общий
товар, реставрации `gui/*`, пересчёт `local_currency`) описывают механизм,
который **больше не существует в этом хотфиксе** — оставлено как история
решения, не как текущее устройство. Текущее устройство: хотфикс правит только
то, что автор не починил сам (EF.2 — старые баги; EF.4 — три престижные
валюты и центробанк в собственности компании, теперь на `liquidity_currency`;
кусок EF.5 — тайпо Вюртемберга и мёртвые валютные законы). Подробности,
решения и открытые вопросы (в т.ч. `law_spe_uni_currency`, не проверенные в
игре пункты) — раздел «Обновление модов-исходников 02.09.2026» в
`План проекта.md`.

**EF.9, тем же вечером:** запрошено вернуть у `liquidity_currency` то, что
было у `spe_uni_c` до слияния — торговлю (`tradeable = yes`) и формульную
выдачу `local_currency` минорным странам по населению/уровню жизни вместо
плоских 2500. Заодно нашлась и закрыта дыра — EF.1 вместе с 95 мёртвыми
валютами удалил и локализацию пяти живых объектов (три престижные валюты +
компания/модификатор центробанка), она восстановлена для всех 11 языков
хотфикса.

**EF.10, следом:** запрошено объединить `local_currency` и
`liquidity_currency` обратно в один товар — минорные страны теперь тоже
получают `liquidity_currency` (та же формула), а не отдельный товар,
центробанки по-прежнему чеканят его престижные варианты. Имя обычного
варианта — «Локальная валюта», иконка — старая монетка. Осознанный побочный
эффект: `liquidity_currency` торгуем (нужно для престижных валют), значит
рыночная утечка минорской валюты — тот самый баг из EF.5 — снова возможна
структурно, просто для другого товара; не подавлялась намеренно, не
измерялась. Попутно обнаружена и исправлена рассинхронизация репо/живой
копии отдельного мод-перевода `V4 RUS` (EF.7 применилась только к репо).
Подробности — разделы EF.9-EF.10 в `План проекта.md`.

**EF.11, 09.09.2026:** запрошено переделать меню компаний — с модами их
набирается 100+ на страну, они шли одним плоским списком без разделения по
доступности, и открытое меню заметно просаживало FPS. Список неоснованных
компаний разбит на три сворачиваемые секции по готовым спискам движка
(доступные / не хватает условий / привязаны к чужой области), карточка
заменена на компактную строку. Хотфикс снова содержит один файл `gui/` —
но не реставрацию ванили, а собственную правку. Глава «The companies panel».

## Для мастерской

Paste as is into the workshop page.

```
[h1]E&F Hotfix [1.13][/h1]
Fixes for [b]Economic and Financial[/b] (repo version 04.07.2026) on Victoria 3 [b]1.13[/b].
Load [b]after E&F[/b]. [b]Requires Private Sector Construction (PSC)[/b] since 02.10.2026: the former PSC + E&F ComPatch is now part of this mod.

[h2]Load order[/h2]
[list]
[*]Community Mod Framework (CMF)
[*]Expanded Topbar Framework (or Dense UI)
[*]Private Sector Construction (PSC)
[*]Economic and Financial (E&F)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3520140574]my E&F RU Localization (if u need)[/url]
[*][b]E&F Hotfix (this mod)[/b]
[/list]

[h2]E&F can finally share a build with other big mods[/h2]
Victoria 3 crashes on entering a game above [b]128[/b] goods, silently, with nothing in the log. Vanilla ships 53 and E&F adds 73 — [b]126[/b], two slots left. Any mod bringing three or more goods breaks the game, which is why E&F and Tech & Res could never run together.

57 of E&F's 73 goods are currencies, one per monetary system law. This mod merges them into one, taking E&F from 73 goods to [b]8[/b]:
[list]
[*]E&F alone: 126 → [b]61[/b]
[*]+ Morgenröte: crash → 66
[*]+ PSC: crash → 70
[*]+ Tech & Res: crash → [b]96[/b]
[/list]

[b]Nothing about the monetary system is removed.[/b] All 95 currency laws stay, every country keeps its own law, its own mint, its own exchange rate and money supply. Only the good on the belt is shared, and it is called Local Currency.

[h2]Your currency is a prestige good now[/h2]
A base good gets three prestige slots — measured, not guessed — so the currencies come back as three, one per monetary standard:
[list]
[*][b]Representative Currency[/b] — gold, silver, bimetallic standard
[*][b]Pegged Currency[/b] — gold exchange, external exchange standard
[*][b]Fiat Currency[/b] — fiat standard
[/list]
Each with its own name and icon, a prestige bonus, and the engine's +20% throughput for buildings that consume it. Change your monetary standard law and the central bank starts minting the matching one.

To produce a prestige good a company has to own the building, so [b]the central bank is now owned by a bank company[/b] — the country's own historical one where E&F ships it (Bank of England, Banque de France, the State Bank), a generated "Central Bank" company otherwise. It is granted free of a company slot, it cannot be deleted, and it holds the monopoly on banks so no rival buys it out.

The treasury still funds the central bank, so the company collects no dividends from it and the building panel still calls it a government building. That is deliberate: the company holds the bank to mint the currency, not to profit from it.

[h2]Construction runs on PSC[/h2]
E&F's own "private construction sector" sits in a building group that is not government funded, so nothing it consumes reaches your budget, yet it hands out construction points — at double the vanilla rate for a quarter of the goods. This mod hands construction over to PSC instead: sectors produce construction goods, a regulator turns them into points, and the treasury and the investment pool pay for every unit. E&F's money and finance layer is rewired onto PSC's sector:
[list]
[*]E&F's private construction building is disabled; its history, companies and bank-founding effect point at PSC's sector
[*]Sector limit = urban centres × (1 − 5 × central bank rate). Above it an excess-capacity penalty grows month by month and cuts sector throughput; the Financial Stability Office journal shows it in its own section
[*]Buttons to ban or allow private construction sectors; the AI uses them too
[*]The speculative bubble no longer slows construction
[*]PSC's per-state construction price lookup no longer reads a regulator that does not exist yet (startup error spam)
[/list]

[h2]What else it fixes[/h2]
[list]
[*][b]The crash when the world map appears[/b]
[list]
[*]Six vanilla GUI files E&F still ships in their 1.12 form are restored, keeping the [i]@money![/i] → currency symbol substitution
[*][i]map_markers.gui[/i] was missing [i]enemy_naval_mission_marker[/i] — the engine looks that widget up by name and crashes when it is gone
[/list]

[*][b]~70,000 script errors per session[/b]
[list]
[*]31 of 32 E&F alerts read variables that are never initialised — the national stockpile they belong to ships inside a .zip the game does not read
[*]Every alert now checks [i]has_variable[/i] first. Two bond alerts also ran in market scope while reading country variables, and markets have no variables in Vic3
[/list]

[*][b]History bugs[/b]
[list]
[*]Spain got no starting silver mine: E&F points at [i]STATE_ANDALUSIA[/i], which 1.13 split into Lower and Upper
[*]Greece got gold and silver mines in Saxony and Brandenburg — a copy-paste of the Prussian block, running in a NULL state
[*]Württemberg got no currency at all: its law is spelled [i]gulde[/i] without the n
[*]Thirteen countries held a named currency law whose good does not exist — worse than having no currency. Moved to [i]law_no_market_liquidity[/i]
[/list]

[*][b]Currency laws were unavailable to everyone[/b]
[list]
[*]All 95 required a technology named [i]currency_standars[/i] — the real one has a d. One letter, 95 times, and the whole law group could never be enacted by hand
[*]Fixed, with a restriction: a law is available only to the tags E&F itself assigns it to, and only once you actually have a central bank
[/list]

[*][b]Local currency flooding every market[/b]
[list]
[*]E&F handed countries without a monetary system a flat 2500 local currency [b]per state[/b], regardless of size. ~600 of 724 countries qualify, and their cheap currency crowded real national currencies out of [i]popneed_currency[/i]
[*]Now computed from population and standard of living, using E&F's own [i]buy_packages[/i] table as the curve — and local currency is part of the merge, so there is no cheaper currency to switch to any more
[/list]

[*][b]Three script guards[/b]
[list]
[*]E&F's stock and bond demand values divide by [i]building_financial_num[/i], zero for any country without a financial centre — the author's own comment on that line says "division par zero possible"
[*]The same division by zero in the currency, which he left unguarded, and which was Britain and China printing a million currency at random
[*][i]sell_currency_privat_bank[/i] dereferences a seller scope that may not exist
[/list]

[*][b]The company menu with 100+ companies[/b]
[list]
[*]Companies you have not founded yet are split into three collapsible sections — [i]Available[/i], [i]Attainable[/i], [i]Potential[/i] — instead of one flat list, with a count on each
[*]Each entry is a compact row now; the full card is in the tooltip. Collapsed sections build nothing, so the panel no longer costs frames while it is open
[*]Search, filters and sorting are untouched, in their own section at the bottom
[/list]

[*][b]E&F's dev panel showing up in the budget screen[/b] — the round [b]1[/b] button under the budget tabs. Tied to [i]-debug_mode[/i], so anyone playing with the console open sees it. Hidden
[/list]

[h2]Not fixed[/h2]
[list]
[*][i]budget_panel.gui[/i] and [i]construction_panel.gui[/i] are equally out of date but hold real E&F reworks — they need a manual merge, not a vanilla swap. Expect trouble at bankruptcy and in the ship construction queue
[/list]

[i]Overrides five E&F data files and seven .gui files, so it has to be rebuilt after every E&F update and every game patch.[/i]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]
```

---

Fixes for **Economic and Financial**, repository version **04.07.2026**, on Victoria 3 **1.13**.
Load it **after E&F**. It does not depend on any compatch and works without them.

The headline change is the **currency merge**: E&F's 57 currency goods become one, which is
what lets E&F share a build with Tech & Res, Morgenröte or PSC at all. Around it sits the
machinery that merge needed — three monetary standards as prestige goods, a central bank
owned by a company, a rewritten money-issuance controller — and then a list of independent
repairs: history, GUI, alerts, local currency, currency laws, script guards, dev panel.

Most of the mod is **generated** from E&F's own files by `tools/regen_ef_currency_merge.py`.
Anything with a `zz_ef_cm_` prefix is its output and must not be edited by hand; see
[Maintenance](#maintenance).

---

## The currency merge — 57 goods into one

### The arithmetic

Victoria 3 1.13 cannot digest more than **128** goods. Established empirically with dummy
filler goods: 128 loads, 130 and 131 crash on entering the game, without a single script
error in the log.

E&F brings 73 goods of its own on top of vanilla's 53 — **126**, two slots left. Any mod
adding three or more breaks the game, and it breaks silently.

57 of those 73 are currencies, one per monetary system law. Merging them into a single good
takes E&F down to **8**:

| build | before | after |
|---|---:|---:|
| vanilla | 53 | 53 |
| + E&F | 126 | **61** |
| + Morgenröte (+5) | 131 — crash | 66 |
| + PSC (+4) | 135 — crash | 70 |
| + Tech & Res (+35) | 161 — crash | **96** |

Tech & Res is the point of the exercise: it and E&F simply could not coexist, and now they
do, with neither side cut.

### What is not lost

All 95 currency laws stay. Every country keeps its own law, its own `pm_currency_*`, its own
exchange rate and money supply. The bank still mints, buildings still pay for liquidity.
Only the good on the belt is shared.

`local_currency` is merged in too, and that is a fix in its own right rather than a side
effect: it was a separate, cheaper good that also satisfied `popneed_currency`, so pops in
real nations covered their currency need with somebody else's local money instead of their
own. The hotfix used to fight that by recomputing how much of it gets issued (see the
`local_currency` section); merging removes the cause instead of the symptom, because there is
no longer a cheaper currency to switch to. It is the same good at the same price.

It also frees a name and an icon. The surviving good is called **Local Currency** and wears
`local_currency`'s icon, because that is what it is: the plain money every country makes.

### Why it was safe to do

E&F's exchange rates, money supply, gold and silver standard, stockpiles, imports and
exports run on country and global **variables**, not on the market data of the currency
goods. Of the 36 script-value families E&F defines per currency, 14 are referenced nowhere
at all — including every one that reads `market.mg:<X>_c.market_goods_*`.

The one live consumer of a currency good's market data was the money-issuance controller,
which needed rewriting; that has a section of its own below.

### What the generator rewrites

Not just the goods file. Every reference to a dead currency has to be retargeted, and the
two shapes have to be handled separately — a bare key (`mg:pound_sterling_c`) and a key
baked into a modifier name (`goods_input_pound_sterling_c_add`), where a `\b`-anchored
pattern silently misses.

| | count |
|---|---:|
| currency laws / production methods left intact | 95 |
| production methods retargeted | 285 |
| script values retargeted | 475 |
| orphaned modifier types dropped | 378 |
| pop-need entries dropped | 95 |
| goods colours dropped | 94 |
| languages localised | 11 |

---

## The three monetary standards

The currencies come back — not as 95 separate prestige goods, which was the first attempt,
but as **three**, one per monetary standard.

### Three is the ceiling, and it is measured

A base good gets **three prestige slots**. Only the first three declarations become real
slots; everything past them silently falls back into the third. There is no define for it —
the number is in the executable. The symptom was the entire world minting the Iraqi dinar.

### The three

| prestige good | monetary standard laws |
|---|---|
| **Representative Currency** | gold standard, silver standard, bimetallism |
| **Pegged Currency** | gold exchange standard, external exchange standard |
| **Fiat Currency** | fiat standard |

Each carries `possible = { has_law = law_type:law_<standard> }`, which **is** evaluated in
country scope — confirmed in game at three goods, after it had been dismissed as unreliable
at ninety-five. So the central bank of a country on the gold standard mints Representative
Currency, and the same bank mints Fiat Currency after the law changes. The prestige bonus
and the engine's +20% throughput for buildings consuming it come along for free.

Prestige goods do not count against the 128 — measured with a hundred dummies on one base
good, not assumed.

Fiat reuses E&F's `spe_uni` icon; the other two are new icons drawn in E&F's style, 350×350
uncompressed DDS in `gfx/interface/icons/goods_icons/currencies/`.

**The "Currency Issued" row is back in the bank panel.** E&F hides that production method
group — and eleven others — by name in `building_details_panel.gui`, so the bank showed two
rows and not three. `pmg_currency_type` is taken off that list; the other eleven stay hidden,
they are E&F's internal plumbing. It does nothing mechanically and never did; it says which
currency this bank issues.

---

## The central bank and the company that owns it

A company can only produce a prestige good from a building it **owns**, so the central bank
had to become ownable. That turned out to be the largest single block in the mod.

### Ownership can only happen at creation

There is no effect in the game that gives an existing building to a company. `add_ownership`
is a field of `create_building` and nothing else — all ~1900 uses in vanilla are inside one,
and no ownership effect appears in `effects_l_english.yml` or `common/effect_localization/`.
The only other route into company hands is privatisation, which is the AI's decision on its
own schedule.

So the bank has to be **born owned**. All 1,004 of E&F's `create_building` calls for the
central bank are rewritten to go through `zz_ef_cm_create_owned_bank`, which picks the owner
and creates the building already in its hands.

Two engine rules learned the hard way here:

* **`level` cannot stand next to `add_ownership`** in one `create_building`. The level is the
  sum of the ownership levels; writing both makes the engine throw the whole block away at
  load (`PostValidate of effect 'create_building' returned false`). Vanilla says the same by
  example: 3128 blocks with `add_ownership`, not one with `level`.
* **`$CB_SIZE$` has to be a literal.** It is a macro argument, pasted in as text, and it lands
  inside `add_ownership = { company = { levels = $CB_SIZE$ } }` where a `var:` read does not
  resolve. Passing one there cost four countries their central bank outright: the building was
  removed and recreated with zero levels, with nothing in any log.

### Which company

Whatever bank company the country already holds. E&F ships 98 of them and lists them itself,
in the `private_bank_type` block of its customizable localisation — that list is the source
of truth. A hand-written table of tag → company was tried first and kept losing the race
against E&F's roster: it named the Da-Qing Bank for China, which is founded in 1905, while
the bank China actually holds in 1836 is the Imperial Bank of China. Mexico, Belgium,
Portugal and Turkey were the same shape of miss.

The curated table survives, but it only decides **order** — Britain holds six banks and the
Bank of England should win.

Countries with no bank of their own get one generated company, `zz_ef_cm_central_bank`,
named "Central Bank" with the central bank icon. There used to be ninety-five of these, one
per currency law and identical but for the key; since the prestige good is chosen by the
monetary standard law rather than by the currency, the currency had nothing left to select.

All 98 get `building_bank` on their `building_types` and the three regime currencies on
their `possible_prestige_goods`, by `INJECT:` — nothing is taken away, so nothing needs
restating, and they keep the railways and trade centres E&F gave them.

**`building_types` is the only real lock on who may own a building.** A monopoly is a price
and construction rule, not a lock: in the Papal States, Banca d'Italia privatised four levels
of the central bank out from under the company that held the monopoly.

### Growing versus changing hands

The bank is **torn down only to change hands** — when the country's own historical bank turns
up years after a stand-in took the central bank. Ownership cannot be moved, so the only way
to hand it over is to build it again, and the upkeep pass calls that rebuild itself rather
than waiting for E&F, whose spawners fire on gdp_view thresholds and may never come for a
country that is not growing.

Ordinary growth is an ordinary `create_building` on top of what is there. It used to be a
tear-down as well, and that had a price worth writing down: E&F calls its spawners from
`ef_on_yearly_pulse_country` with a size that grows with `gdp_view`, so a growing country
crosses a threshold about once a year. Each rebuild dropped that country's entire issuance
for a month while the new building staffed up, and the currency price fell to 0.01 and came
back — which is why the countries that grow fastest spiked and Austria did not.

A rebuilt bank also comes back bare, so both of E&F's setup effects have to run:
`central_bank_production_methods` picks the methods and `central_bank_modifier` re-applies
`currency_demande`, the mult that turns the production method's ~27 units into Britain's
100K. That modifier lives on the building, so tearing the building down takes it with it.

### Owned, but still government funded

| what | why |
|---|---|
| `ownership_type = no_ownership` → `self` | no ownership shares meant nothing to hold |
| `ai_nationalization_desire = 0` → `-5` | 0 is exactly the engine's privatise threshold; a company can only hold privatised levels |

**`bg_bank: is_government_funded` is deliberately left at `yes`.** Ownership shares and
government funding are separate switches, and only the first one is thrown here. The treasury
goes on paying the central bank's inputs and wages and taking its output, so the company that
owns the bank collects no dividends from it.

The visible consequence is that the building panel calls the central bank a government
building even though a company is named on its ownership tab. That reads like a bug and is
not one — the money really does move the government way, and the panel is telling the truth.
The company holds the bank so it can mint the country's prestige currency and so no rival can
buy the bank out from under it, not so it can collect the bank's profits.

`--private-bank` emits the `bg_bank` override and hands those profits to the owner — about 6K
a month on a 1836 British save — which is a different mod.

### The company always exists, and costs nothing

* **granted** at game start and monthly — a country that owns a central bank and holds no bank
  company is given one;
* **free** — a country modifier with `country_max_companies_add = 1` while the central bank
  stands. E&F's own +1 sits inside `prosperity_modifier`, so it only ever reached a prosperous
  company;
* **undeletable** — no such flag exists in the engine, so it is imitated: delete it and the
  monthly pass puts it back;
* **holds the monopoly** on `building_bank`, with a free charter so the patent does not cost
  one of the country's four.

---

## Money issuance — the one thing the merge broke

E&F's bank drives its output until it equals market demand for its currency:

```
target_demand_currency              = market.mg:<own currency>.market_goods_buy_orders
target_demand_currency_for_modifier = (target − current output) / current × 100
currency_demande on the bank        = goods_output_<cur>_mult 0.01 × that
```

That was self-limiting while every country had its own good — "demand for the pound" was,
near enough, Britain's demand. With one shared good it became the whole market's demand and
every bank chased all of it: six banks on the British market issued ~196K each against ~192K
of buy orders, price −99%.

### Splitting the demand

Each issuer takes the share of its market's currency demand that its **GDP** is of the summed
GDP of that market's central banks. GDP is one field, always available, and it tracks both
halves of currency demand at once — pops through `popneed_currency`, roughly half the buy
orders, and buildings through `pmg_market_liquidity` at 98 per workforce unit, the other half.

Two things about that sum are not obvious, and both cost a test round:

* **It is computed in an effect, not in the script value.** Global list iterators do not run
  inside script values. `every_scope_state` does, which is what made `every_country` look
  plausible — so the sum silently stayed 0, `min = 1` turned it into 1, and every share came
  out as `gdp / 1` clamped to the maximum of 1. Every bank on a market then chased the entire
  market's demand: 1.22M of currency against 214K of buy orders on the British market, price
  −98%, West Bengal alone printing 1.08M. Nothing in any log says so — a script value that
  quietly evaluates to zero is indistinguishable from one that legitimately is zero.
* **There is one copy per market, kept on the market's owner.** Every country computes the
  same sum, but each on its own day — the monthly pulse is spread across the days of the month
  — so several issuers on one market held several slightly different ideas of one number and
  their shares did not add to one.

Membership in the sum is "does a central bank stand in this country", not
`has_modifier = has_central_bank`. That modifier is E&F's bookkeeping, applied and removed on
its own pulses, and a country between pulses would drop out of the denominator for a month
while everyone else overprinted to cover the gap.

Countries on `law_no_market_liquidity` issue nothing and take no share, but their pops and
buildings still buy — so their demand is covered by the market's issuers pro rata, which is
what one expects of a colonial market.

### The divisor, and two wrong fixes

`base_demande_currency_fix` is the bank's flat output —
`scope:central_bank_scope.modifier:goods_output_spe_uni_c_add`, the production method's
workforce-scaled `= 1`, about 27 on a level 20 bank. The percentage computed from it feeds a
**mult**, so taking a bank from 27 units to Britain's 100K needs roughly 370,000. Hundreds of
thousands is the working range, not an overflow.

Which is why there is no cap. Capping it at the author's commented-out 25000 cut Britain to a
fifteenth of what it should print; 100000 cut it to a quarter. Nor the `if fix > 0` guard the
five other financial goods use — their divisor is a financial-centre count that grows on its
own, this one is what the bank is already issuing, and skipping at zero locks the bank at bare
production method output forever (Britain went from 100K to 6.77).

The only thing actually wrong is the divide by zero, on the tick after a bank is rebuilt
before its production methods are back. The divisor is clamped at 1, the way E&F clamps
`building_financial_num` elsewhere; with a healthy divisor the arithmetic is bit-identical to
E&F's.

---

## The market panel

E&F gives currencies their own tab, "Currency in Circulation", built from a hard-coded list of
all 95. With one currency the tab is a list of one, and it had a bug of its own: it always
showed the **player's own market**, whichever market panel you opened it from. It was fed by
`GetGlobalList('gui_market_currency_list')` — a global variable list rebuilt for whichever
market the panel last cached, so there was nothing to repair inside it.

The tab is removed, along with the two list-builders that fed it, and the currency now appears
in the ordinary goods grid. That took a second change: `goods_entry_button` hides goods by name
through a `visible` built from 105 `EqualTo_string` terms, and `spe_uni_c` was one of them. 94
of those goods no longer exist, so the filter is rebuilt from the eight financial products that
do.

---

## History

### `common/history/global/zz_ef_currency_fix.txt` (new, additive)

`GLOBAL` blocks stack, and `zz_` is processed after `99_ef_history_global_variable.txt`, so this file overrides nothing — it simply appends its `activate_law` calls last.

**Württemberg.** E&F gives it `law_gulden_south_german_gulde_currency` — no trailing `n`. No such law exists, `activate_law` silently does nothing, and WUR ends up with no currency at all even though the good `gulden_south_german_gulden_c` is alive. We hand it the correct law.

**Thirteen countries → `law_no_market_liquidity`.** Eleven of them hold currencies the author cut while forgetting to remove the `activate_law`: Liberia, Costa Rica, Ecuador, El Salvador, Guatemala, Honduras, Nicaragua, Paraguay, Uruguay, Venezuela, Dai Viet. Plus Haiti and New Zealand, whose currencies an earlier build of this hotfix cut to stay under the goods ceiling — the merge made that unnecessary, but both laws are still duplicates of currencies their neighbours already carry, so they stay where they were put.

Why this matters. A named currency law with no good behind it is a worse state than having no currency: the stock `pm_no_currency_type` and `pm_no_market_liquidity` never switch on (`law_no_market_liquidity` is what unlocks them), and the named production methods that run instead point at nothing. The bank mints nothing, buildings pay nothing for liquidity. `law_no_market_liquidity` is the first law in `lawgroup_currency_type`, with no requirements and no effects — most of the world already lives on it.

### `common/history/buildings/00_ef_building.txt` (overrides the E&F file)

Two edits, everything else copied byte for byte.

**`s:STATE_ANDALUSIA` → `s:STATE_LOWER_ANDALUSIA`.** No such state exists in 1.13; Andalusia is split into Lower and Upper. Because of it Spain never got its starting silver mine.

The target state was picked from the deposit, not from history: Spain's `silver_mine_max_level` modifier is granted to `STATE_LOWER_ANDALUSIA` in `common/history/states/01_ef_states.txt:67`. Without it `building_silver_mine` fails its `possible`/`potential` and never appears. The first version of this hotfix used Upper — an in-game check showed an empty Upper Andalusia and a 0/10 deposit in Lower.

**The `#GRE` block is commented out.** It is a character-for-character copy of the `#PRU` block with the tag swapped, `company_PreussischeSeehandlung` included: Greece was handed gold and silver mines in Saxony and Brandenburg. Greece owns neither state, so `region_state:GRE` returns an invalid object and five `create_building` calls run in a NULL state.

---

## GUI

E&F overrides **32** vanilla `.gui` files. Some are genuine reworks for the financial system, but six had fallen hundreds of lines behind 1.13. That is more dangerous than it sounds: the engine looks some widgets up **by name**, and when the name is missing from the overriding file the game does not complain quietly — it crashes.

That is exactly what the crash on opening the world map looked like:

```
[pdx_gui.h:91]: Could not find widget 'enemy_naval_mission_marker'
                in file 'gui/map_markers.gui'
```

Vanilla has that widget (`map_markers.gui:3995`); the E&F copy does not.

### Restored (vanilla 1.13.10 + the `@money!` → currency symbol substitution)

| file | behind by | what was lost |
|---|---|---|
| `map_markers.gui` | −420 lines | `name=`: `enemy_naval_mission_marker`, `coastal_building_marker`, `enemy_frame`; `type=`: `naval_mission_marker_dot` — **crash on map load** |
| `custom_tooltip.gui` | −336 | `type=`: `naval_mission_marker_tooltip_fleet`, `coastal_building_marker_tooltip_row`, `treaty_tooltip_article_entry` — tooltips for those same naval markers |
| `military_formation_panel.gui` | −387 | `type=`: `military_formation_cancel_invasion_button` — a candidate for the crash on opening the military tab |
| `frontend/shared/lists.gui` | −121 | `type=`: `dropdown_menu_round`, pre-1.13 dropdown structure |
| `popups.gui` | −135 | `name=`: `amount_input`, `decommission_supply_ships_window` |
| `right_click_menu.gui` | −71 | `name=`: `enemy_fleets_on_mission_in_sea_region` |

Verified: across all six restored files not a single `name=` and not a single `type=` is missing relative to vanilla 1.13.10.

What is lost from the E&F side is minimal and cosmetic: six `using = tooltip_above` in the markers, one `tooltip = "TOOLTIP_STATE_DEVASTATION"`, one `text = "[MilitaryFormation.GetNameNoIcon]"`, and the `treaty_tooltip_article` variants under `acquire_monopoly_for_company`. Every money string is reproduced automatically by the `@money!` substitution.

### ⚠ Two more files with the same illness — left alone

| file | missing `name=` | when it blows up |
|---|---|---|
| `budget_panel.gui` | `declare_bankruptcy_button`, `bankruptcy_progress_bar`, `bankruptcy_progressbar` | when the bankruptcy interface is shown |
| `construction_panel.gui` | `ship_construction_queue_pages` | when the ship construction queue is opened |

These cannot be swapped for vanilla: they are real E&F reworks (−145/+218 and −113/+105) and hold his entire budget mechanic. They need a manual merge — take vanilla 1.13 and port the E&F changes onto it. A separate job.

---

## The companies panel

`gui/companies_panel.gui` — the only `.gui` file the hotfix ships now, and unlike the six
restorations described above it is a change, not a copy of vanilla.

### What was wrong

Vanilla puts every company type the country has not established yet into one flat list of
`potential_company_item` cards. A card is not cheap: two backgrounds, two data models of
building icons, a prestige-goods data model, and five text boxes whose localisation calls
`CompanyType.GetProductivity`, `GetProsperityModifier` and `GetNumBuildingLevels` on every
update. That is fine for the ~40 types vanilla ships. With E&F and the content mods on top the
count passes **100**, the panel builds several thousand live widgets, and the frame rate drops
for as long as it stays open.

The second problem is that the flat list says nothing about whether a company can actually be
founded. The vanilla visibility filter has three settings — Available / Attainable / Potential —
but they are a radio button over one list, not a grouping, so the answer is one click away per
category and never visible at once.

### What it does now

The engine already classifies company types per country and exposes the result as three data
models, which is what the vanilla filter counter is built from:

| data model | meaning |
|---|---|
| `Country.GetAvailableCompanies` | every requirement met — can be established now |
| `Country.GetAttainableCompanies` | requirements are reachable: buildings, technology, a free slot |
| `Country.GetPotentialCompanies` | needs a state the country does not hold |

Each gets its own `section_header_button` with a live count and a collapse arrow. **Available**
is expanded by default, the other two are collapsed, and a collapsed section builds no items at
all — that is where most of the frame time comes back. The collapse state lives in
`GetVariableSystem` under `ef_companies_available` / `_attainable` / `_potential`, so it holds
for the session and resets on load, exactly like vanilla's own `established_companies` toggle.

Rows are the new `ef_company_type_row`: icon, name, one subtitle line, the prestige goods the
type can mint, and the Establish button. Everything else the card used to show is still
there in `FancyTooltip_CompanyType`, which vanilla already wrote and which is only built for the
row under the cursor. The subtitle is the company category, except in the Potential section,
where it is `COMPANY_TYPE_HEADQUARTER_STATE` — the state you would have to take.

The prestige goods sit in an `overlappingitembox` holding vanilla's own
`company_type_prestige_good_item`, so each icon keeps `FancyTooltip_Goods` and a company with
three of them stacks the icons rather than running into the button.

The row is a plain `widget` with everything placed by hand, not a `flowcontainer`. In a flow the
prestige holder collapses to nothing on a company that has no prestige goods and drags the
Establish button left with it, so the buttons stop lining up down the list — visible immediately
once the panel had real data in it. Anchoring the button to the row's right edge fixes the
column for good, whatever sits to its left.

### The established companies

The section above the split is vanilla's, with one addition: a small round button on the right,
over the list, that swaps the big `company_item` cards for `ef_established_company_row` — one
row per company, same right-anchored layout as the rows below it, carrying the name, prosperity,
the prestige goods it mints (faded while it is not actually producing them), profit, and the
go-to / pin / disband buttons. `FancyTooltip_Company` covers the rest, as before.

The state is `ef_companies_compact` in `GetVariableSystem`; the cards are still the default, so
nothing changes for anyone who does not press the button. It earns its place late, when a
country runs its full complement of companies and the section alone fills the panel before the
not-yet-established list even starts.

### Search, filters and sorting

These are the one thing that cannot follow the split. The search bar, the filter block and the
four sort buttons all act on `CompaniesPanel.GetFilteredCompanyTypes`, the panel's own list, and
there is no way to ask the engine which category a single `CompanyType` belongs to — only for
the three lists as a whole. So they keep the vanilla flat list, moved under a fourth collapsed
section, `EF_COMPANIES_SECTION_SEARCH`. Nothing from vanilla is removed; the flat list is simply
no longer what greets you.

### Localisation

Three of the four section titles reuse vanilla keys — `COMPANY_AVAILABLE_FILTER_TITLE`,
`COMPANY_ATTAINABLE_FILTER_TITLE`, `COMPANY_POTENTIAL_FILTER_TITLE` — with
`COMPANY_*_FILTER_NAME` as their tooltips, so the wording matches the filter buttons that are
still in the panel and no new translation was needed. Only the fourth title is new:
`EF_COMPANIES_SECTION_SEARCH`, plus `EF_COMPANIES_VIEW_COMPACT` / `EF_COMPANIES_VIEW_CARDS` for
the view toggle — `localization/*/zz_ef_companies_panel_l_*.yml`, all eleven languages.

### Caveats

- **The free company slot.** The split is the engine's, and by the wording of
  `COMPANY_ATTAINABLE_FILTER_NAME` ("...or gaining a free company slot") a type with every
  other requirement met may sit under **Attainable** rather than **Available** when no slot is
  free. Not verified in game. If it turns out that way, Available emptying out mid-game is the
  engine's classification, not the panel's.
- **Load order.** The file overrides vanilla by path, so any mod loading after the hotfix that
  ships its own `gui/companies_panel.gui` replaces it wholesale. Checked against the current
  playset — nothing does. E&F's own stray copy under
  `gui/ef_dev_and_custom_windows/maj/NonEssential/` is a different path, loses the type
  registration race to `gui/companies_panel.gui`, and is already ignored (it is what the
  "already registered at 'gui/companies_panel.gui'" lines in `gui.log` are).
- **After every game patch** this file has to be rebuilt from the new vanilla, same as the
  restorations were: it is a vanilla file with one block replaced.

---

## Alerts — 70,000 errors per session

`common/alert_types/00_ef_alert_types.txt` holds 32 alerts, 31 of which read variables that are uninitialised in most games:

- **29 `store_release_*`** (ammunition, grain, coal, oil…) read `<good>_store_month_fixe`, `store_<good>_time` and friends. These are national stockpile variables, and the stockpile's production methods and PM groups live in `17_ef_national_stockpile.zip` — the game does not read archives, and no building with the `bg_national_stockpile` group exists in the mod. No data, no variables.
- **2 `selle_bond_maturity_yers_time_*_Y`** read `selle_bond_maturity_yers_time_1..10` in market scope.

The alerts are declared with `script_context = player_country` and `player_market`, meaning they are re-evaluated on every change of played country. Hence the outcome: in a test game those two families produced **on the order of 70,000** entries like

```
Value of wrong type in 'common/alert_types/00_ef_alert_types.txt:1017'. Got value of type 'none'
Failed to fetch variable for 'selle_bond_maturity_yers_time_6' due to no variables in scope
```

and that was the **only** source of errors in the log, discounting noise from the base game.

**What was done.** Every `valid` block got `has_variable` guards for each variable that alert reads — directly and through the `*_time_rest` script values in `00_economic_scripted_value.txt`. No data, no evaluation, no noise. With data present it behaves exactly as before.

31 of 32 alerts are patched. `fso_alert` is untouched: it reads no variables.

**A second fix in the same file.** Two alerts, `selle_bond_maturity_yers_time_5_Y` and `_10_Y`, are declared `script_context = player_market` but read `var:selle_bond_maturity_yers_time_1..10`. Markets in Victoria 3 do not support variables at all — the engine answers `This scope doesn't support variables. Scope: Market ...`. Those two alerts could never have worked.

The variables themselves are set in `common/history/global/00_ef_financial_global_variable.txt` inside `GLOBAL = { every_country = { ... } }`, i.e. they are **country-scoped**. So `script_context` is changed to `player_country` — the error goes away and the alert finally starts doing what it was meant to.

Only live lines are patched: the file also holds 28 commented-out `buy_sell_*_order` drafts with the same `player_market`, and the patch leaves them alone.

One caveat: where an alert reads five variables through an `or`, all five are now required. Previously, with partially populated data, one branch evaluated while the rest threw errors — so the result was undefined either way.

---

## `local_currency` issuance — computed, not handed out flat

**What it was.** E&F puts the `no_money_production` modifier on every country without a monetary system:

```
no_money_production = {
	state_sell_orders_local_currency_add = 2500
}
```

It is a country modifier, so 2500 units landed in **every state** the country owns, with no regard for population, wealth or anything else. About 600 of the game's 724 countries have no monetary system, and their cheap local currency flooded the shared markets: any currency satisfies the currency need, local currency is cheaper, so pops of proper nations covered `popneed_currency` with it instead of their own national money.

**What it is now.** The flat issuance is disabled at the source:

```
REPLACE:no_money_production = {
	icon = gfx/interface/icons/timed_modifier_icons/no_money_production.dds
}
```

The entry stays alive, so every `has_modifier = no_money_production` check in E&F keeps working — it simply cannot print money anymore. In its place the country gets what the formula computes:

```
country demand = population/1000 × f(average standard of living) × 0.0132
per state      = demand / number of states, at least 25
```

> ⚠ **Formula validation mode is currently ON: the calculation applies to ALL countries without a monetary system.** Normal behaviour — throttling only those sitting in someone else's market with a real currency — is restored by uncommenting the `market` block in `common/scripted_triggers/zz_ef_local_currency_triggers.txt`.

### Why at the source rather than by subtracting it back

That is how it worked before — a modifier with a base of `-1` subtracting the excess from E&F's 2500. Dropped for two reasons, both of which showed up in game:

1. **A month of lag.** E&F applies `no_money_production` from the `law_no_monetary_system` effect on its own pulse, while the game spreads `on_monthly_pulse_country` across the days of the month. The state printed the full 2500 in between — which is what "2.5k keeps popping up on random vassals" was. Countries born mid-game (revolts, releases, unifications) started life with the full amount.
2. **A ceiling.** If the computed demand exceeded 2500 per state there was nothing left to subtract and the country kept E&F's number. The grant has no upper bound now beyond a `max = 25000` sanity cap.

### Why not from actual consumption

Tried and abandoned; the knowledge was expensive, so it is written down. Reading `state_goods_consumption` for `local_currency` works technically: the per-state sum accumulates inside a country-scoped script value and stays a country-scoped number, exactly like vanilla's `country_total_urbanization`. It fails on meaning.

**In a flooded market, consumption measures availability, not need.** Currency is plentiful and cheap → pops happily cover `popneed_currency` with it → consumption is high → we allow printing more → there is even more of it. The Ionian Islands on the British market (188k people, ~113 units by the formula) printed the full 2500 that way.

Capping the measurement at 2× the formula killed the runaway but produced the same thing in a milder form: everybody pinned themselves to the cap and steadily ran at twice the computed value.

"They genuinely need this much" cannot be told apart from "they are simply getting it cheap" through consumption. Real demand (`buy_orders`) is only computed by the game at market level, where it is shared across every participant and useless for sizing one small country:

| scope | available |
|---|---|
| market | `market_goods_buy_orders`, `market_goods_consumption`, `market_goods_delta`, production, imports, exports |
| state | `state_goods_consumption`, `state_goods_production`, `state_goods_delta` |
| country | nothing — only a manual sum over states |

Hence a clean formula with no feedback from the market.

### About the flicker in the first month

`on_monthly_pulse_country` is not "once a month for everybody at once": the game spreads it across the days, recomputing roughly a thirtieth of all countries each day. On top of that E&F applies `no_money_production` from its own pulse. Values will jump around the vassals for the first month — that is normal, and the only cure is dropping modifiers in favour of buildings.

### Where the curve f comes from

The need is defined in `common/buy_packages/00_ef_buy_packages.txt` — E&F injects `popneed_currency` into all 99 wealth levels:

| wealth | 1 | 5 | 10 | 15 | 20 | 25 | 30 | 40 | 99 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| £ | 21 | 28 | 37 | 41 | 40 | 46 | 62 | 96 | 6177 |

The shape is lopsided: it climbs briskly up to level 10, sits on a shelf from 10 to 20, accelerates past 20 and goes exponential past 40. In `zz_ef_local_currency_values.txt` it is broken into segments (`zz_ef_lc_curve_a` … `_e`), each clamped to its own bounds and multiplied by its own slope. Agreement with the table: SoL 6.1 → 30.8 (table says 31), 11 → 37.3 (38), 30 → 62.0 (62), 40 → 96.0 (96).

### Calibration

In-game measurements, whole-country consumption:

| country | population | SoL | measured | formula | |
|---|---:|---:|---:|---:|---:|
| New Granada | 1.47M | 7.3 | 1640 | 634 | 39% |
| Circassia | 664k | ~11 | 372 | 327 | 88% |
| Bukhara | 1.47M | 6.1 | 380 | 597 | 157% |

Per capita they differ by a factor of four, and **neither population nor wealth explains it** — by the curve all three should consume almost the same. Something else does the work: pop composition, the price of the good at the moment of measurement, the dependant ratio. So `rate` is the geometric mean of the three fits — a compromise, not a fit to one country.

One knob, and it is linear: `zz_ef_local_currency_rate`, currently `0.0132`. It started at `0.013` plus 25% headroom (`0.01625` in total); after a test run the headroom was folded into the knob and the overall level cut by 19%. Turn it the same way from here: `0.0132` → `0.0099` is another quarter off everyone at once.

### Why the modifier is country-scoped

Applying it per state was tried and does not work, and this is worth remembering. **The `multiplier` in `add_modifier` is not evaluated in the scope the effect sits in.** Inside `every_scope_state` the triggers see the state fine, but the multiplier one line below does not:

```
Value of wrong type in 'zz_ef_local_currency_on_actions.txt:39'. Got value of type 'none'
```

`state_population` and `sg:local_currency` came back as zero, everything bottomed out on the lower bound, and states issued 10 units instead of thousands.

Note this is a limitation **on the modifier, not on reading data**: the per-state sum can be accumulated inside a country-scoped script value (see `country_total_urbanization` above) — it was dropped on meaning, not on technique.

Side effect of a country-scoped modifier: states of one country get equal shares, even though Circassia's two hold 590k and 74k people. The only cure is dropping modifiers in favour of buildings, which is what the local banks mod does.

### Mechanics

| file | what |
|---|---|
| `common/static_modifiers/zz_ef_no_money_production.txt` | `REPLACE:` — kills E&F's flat 2500 at the source |
| `common/static_modifiers/zz_ef_local_currency_fix.txt` | our grant modifier, base `+1` |
| `common/scripted_triggers/zz_ef_local_currency_triggers.txt` | who it applies to. **Currently everyone with `no_money_production`**; the market condition is commented out |
| `common/script_values/zz_ef_local_currency_values.txt` | the curve and the calculation. One knob — `rate` |
| `common/on_actions/zz_ef_local_currency_on_actions.txt` | monthly recalculation |
| the last block in `zz_ef_currency_fix.txt` | the initial grant, so the first month is not spent without currency |

Also in `common/pop_needs/00_ef_pop_needs.txt` the weight of `local_currency` inside `popneed_currency` is lowered from `0.25` to `0.1`: a real currency should be more attractive than a generic local one. All 65 real currencies keep `0.25`.

**With the _ZZ EF Local Banks mod installed** it neuters our grant too (`TRY_REPLACE:zz_ef_local_currency_fix`) and prints currency from buildings instead. The hotfix does not depend on it and works fully without it.

---

## Currency laws — a typo removed

All 95 laws in `common/laws/01_ef_currency_type.txt` required:

```
unlocking_technologies = {
    currency_standars
}
```

No technology by that name exists — the real one is `currency_standards`, with a `d`. One letter, 95 times, and the whole `lawgroup_currency_type` was unavailable to anyone, ever.

**It did not affect the intended path**: `introduction_of_<currency>` calls `activate_law` directly, which bypasses requirements. The typo only closed off manual selection by the player.

**It is worth fixing for one case** — a country formed mid-game. Germany inherits Prussia's central bank, Prussia researched `central_banking` long ago, so `on_researched` will never fire again, and GER could never get the mark: not by history (it has none), not by automation (already spent), not by law (the typo). An open law group is the only way out.

Since the laws can now be enacted by hand, a `possible` block was added. It is built from E&F's own data rather than invented:

| | count | rule |
|---|---:|---|
| law bound to tags | 53 | available to whoever E&F itself hands that currency to in history — including the HMM branch, so formable countries are covered |
| ownerless currency | 3 | available to everyone — Tunisian and Yugoslav dinar, South German gulden |
| good commented out | 39 | `always = no` — holding a law with no good is worse than having no currency: the bank mints nothing, the production methods point at nothing |

On top of that **every available law requires `has_modifier = has_central_bank`**. This is the important part: you cannot pick a currency before you have a central bank. Otherwise a Japan player would take the yen in 1836 and walk straight past the Meiji chain that gates it (see below).

The author never intended "one currency per country": there was no `possible` on any of the 95 laws, and he deliberately hands one currency to several tags (Canadian dollar — CAN, ONT, QUE; Prussian thaler — PRU and NGF; Bolivian peso — BOL and PBC).

### How the central bank is actually granted — and why we stay out of it

Worked out while debugging Japan; written down so nobody steps on it again.

The path to a central bank is not a journal entry but `on_researched` on the technologies:

```
banking            → add_technology_researched = currency_standards
currency_standards → activate_law = law_type:law_fiat_standard
central_banking    → currency_standards + metalique_standard
                   → introduction_new_currency = yes
```

`introduction_new_currency` (`09_introduction_building_lvl.txt:38456`) places a level 5 `building_bank` in the capital, applies `central_bank_modifier` and `central_bank_production_methods`, then calls 90+ `introduction_of_<currency>` effects, each handing its law to the right tag.

It is called under this condition:

```
or = {
	is_valid_country = yes
	AND = { var:gdp_view >= 1   NOT = { c:JAP ?= this } }
	AND = { is_player = yes     NOT = { c:JAP ?= this } }
}
```

So **any played country gets a central bank as soon as it researches `central_banking`** — except Japan, explicitly excluded from both open branches. Japan can only come in through `is_valid_country`, and there:

```
is_valid_country_JAP = {
	c:JAP ?= this
	or = {
		has_journal_entry = je_meiji_economy
		has_variable = japan_emperor_restored
		has_variable = japan_restoration_complete
	}
}
```

All three flags are alive in vanilla 1.13 (`00_meiji_restoration.txt:744`, plus the variable is used in achievements, `ai_strategies` and companies). **Japan is not broken — it is gated behind the Meiji Restoration, and that is intentional.**

The other countries "missing" from the main history list are gated the same way, to the historical dates their currencies were introduced — PHI 1851, CUB and CLM 1857, SAF 1860, ARG 1867, CHL 1881, SER 1884, EGY 1898, MOR 1906, KOR 1911.

What follows for the hotfix: **handing these countries banks and currencies at game start is not allowed** — that demolishes the design rather than fixing a bug. It was tried and reverted. `bank_je_central_1` is left alone too: it genuinely cannot complete (it requires an already standing bank while `on_complete` leads to the commented-out `bank_je_central_2`), but it is not the main path, and "fixing" it would open a way around Meiji.

---

## Two script guards, moved here from the PSC compatch

These fix E&F on its own and have nothing to do with PSC, so they were moved out of the E&F + PSC compatch and into this mod. Both are key-level `REPLACE_OR_CREATE:` overrides — no E&F file is overwritten, so they cost nothing on the next E&F update beyond a re-check.

### `common/script_values/zz_ef_div0_fix.txt` — division by zero

E&F's five stock/bond demand values divide twice by numbers that are legitimately zero:

```
target_demand_<good>_ajusted = {
    value    = target_demand_<good>
    subtract = market.mg:<good>.market_goods_exports
    divide   = building_financial_num   # <-- 0 for anyone without a financial centre
    ...
}
target_demand_<good>_for_modifier = {
    value    = target_demand_<good>_ajusted
    subtract = base_demande_<good>_fix
    divide   = base_demande_<good>_fix  # <-- 0 until the first centre exists
    multiply = 100
}
```

The author knows about the first one — the comment on that very line in `00_financial_scripted_value.txt` reads `---------------> division par zero possible`. `building_financial_num` is a sum of ~90 `has_building_financial_centre_<tag>` flags, so it is 0 for most of the world in 1836. `base_demande_<good>_fix` just reads `var:base_demande_<good>_fix`, which is 0 until a centre is built.

The fix clamps the first divisor with `divide = { value = building_financial_num min = 1 }` and wraps the second in a `> 0` check so the block is skipped rather than divided. Note `min` on a `divide = { }` block clamps the **divisor**, not the result — with one or more centres the arithmetic is bit-identical to E&F's. Ten values patched: bond, manufacture, agricultural, mining and railroad stock, `_ajusted` and `_for_modifier` each.

#### The sixth `_for_modifier` — the exchange bubble

The financial-centre block computes six `_for_modifier` values. Five of them are demand, and each ends with the author's own `max = 25000`. The sixth has neither that ceiling nor a zero guard — and it is the one that drives **output**:

| line | value | divisor | `max` |
|---|---|---|---|
| 3688 | `target_demand_bond_for_modifier` | `base_demande_bond_fix` | 25000 |
| 3739 | `target_demand_manufacture_stock_for_modifier` | `base_demande_manufacture_stock_fix` | 25000 |
| 3788 | `target_demand_agricultural_stock_for_modifier` | `base_demande_agricultural_stock_fix` | 25000 |
| 3837 | `target_demand_mining_stock_for_modifier` | `base_demande_mining_stock_fix` | 25000 |
| 3886 | `target_demand_railroad_stock_for_modifier` | `base_demande_railroad_stock_fix` | 25000 |
| **3611** | **`target_supply_mutual_fund_for_modifier`** | **`base_supply_mutual_fund_fix`** | **—** |

The five feed `goods_input_<good>_mult` on the exchange. The sixth feeds `mutual_fund_supply`, which is `goods_output_mutual_funds_mult = 0.01` (`00_ef_dynamic_modifier_building.txt:233`), applied at `09_introduction_building_lvl.txt:22459`. A building's output value *is* its GDP contribution, so this number lands in the state's GDP with nothing in between.

Its divisor is `var:base_demande_bond_fix`, written by `financial_center_modifier_fixed_var` from `scope:financial_center_scope.modifier:goods_input_bond_add` — the workforce-scaled bond intake of `pm_bond_exchange`. Zero on any tick with no workforce to scale: **the tick after the exchange changes hands**, the same window as the central bank in [The divisor, and two wrong fixes](#the-divisor-and-two-wrong-fixes).

Observed in a 1858 campaign: Britain took Egypt's capital state and with it a third exchange (`building_financial_centre_egy`, alongside `_gbr` and `_gbr_2`). That state's GDP then ran past 60 billion — an order of magnitude above the whole world's. Division by zero here is the only path in this subsystem that multiplies an exchange's output without bound.

Patched to the same shape as its five siblings: skip the block instead of dividing at zero, then the author's own 25000. **On the ceiling** — 25000 means `goods_output_mutual_funds_mult = +250`, output ×251, the same headroom he allows on the five inputs. This is not the currency case where a cap strangled the mechanic: there the number *is* the mechanic, here it is a percentage deviation from the exchange's own bond intake. Still, if exchanges visibly shrink after this, delete the `max` line and keep the guard — the guard alone is what stops the blow-up.

Twelve values patched in total, and one more for insurance: `max_building_financial_center_by_number_in_market` (line 203) divides `var:gdp_view_fc` by `building_financial_num` unguarded. It is the multiplier of `financial_center_place_spe`, i.e. `state_building_financial_centre_<tag>_max_level_add` — how tall the exchange in that state may be built. In ordinary play the divisor cannot be 0 where it is read, since the branch only runs in states that hold such a building; the windows where it might are the same ones above. `min = 1` costs nothing and closes them.

Noted, not fixed: `gdp_view_fc` is a country variable and `building_financial_num` counts via `any_scope_state`, yet both are read from inside `every_scope_state`. If the engine evaluated `add_modifier` multipliers in state scope, that would be an unset variable and a wrong-scope trigger every month per centre. Neither error appears in `error.log`, so the multiplier resolves against the country. Worth re-checking if that ever changes.

### `common/scripted_effects/zz_ef_currency_scope_guard_fix.txt` — dereferencing a scope that may not exist

`sell_currency_privat_bank` builds a seller/buyer pair out of an ordered list and then does, unconditionally:

```
scope:seller.owner = { save_scope_as = seller_country }
```

If the list came back empty there is no `scope:seller`. The same holds for `scope:central_bank_site` in the two metal-transfer branches further down. The fix aborts cleanly on a missing seller and adds `exists = scope:central_bank_site` to those two limits. The arithmetic is untouched.

Verified still unguarded in E&F 04.07.2026 on 2026-08-19.

### The seven state variables — history was never enough

Two files, and the second is the one that actually works.

`common/history/global/zz_ef_init_stockpiling_state_vars.txt` is an additive `GLOBAL` block that fills in seven state variables (`stockpiling_{bond,manufacture_stock,agricultural_stock,mining_stock,railroad_stock}_var_state_1`, `financial_center_site_var`, `looted_state`) if they are missing. Written against E&F v4.1.1 to stop startup spam of `Failed to fetch variable ... due to not being set` and `Invalid left side during comparison 'var'`.

It was once marked ⚠ *probably redundant*, on the grounds that `01_ef_state_global_variable.txt:1362-1389` now sets all seven itself. **That was the wrong worry.** Both inits live in `common/history/`, which runs when a *campaign starts* and never again. A save begun before either init existed carries states that have never had the variables, and no history block can reach them.

Measured in a 1858 save on 2026-09-12 — 68 seconds of runtime at speed 4, `1858.1.1 → 1858.1.6`:

| count | error |
|---|---|
| 300 | `Failed to fetch variable for 'stockpiling_*_var_state_1' due to not being set` |
| 303 | `Event target link 'var' returned an unset scope` |
| 303 | `Invalid left side during comparison 'var'` |

906 of the ~1000 script errors that session threw while actually running, from one gate — `01_economic_scripted_effects.txt` (~133298 in the 4.1.7 numbering), inside `stockpiling_capital_state_transfert`:

```
if = {
    limit = {
        any_scope_state = {
            var:financial_center_site_var = 0
            or = {
                var:stockpiling_bond_var_state_1 > 0
                ... four more ...
            }
        }
    }
    stockpiling_capital_state_transfert_financial_center_place = yes
}
```

`any_scope_state` walks every state the country owns, so a country with a bank pays three errors per missing variable per state — and `update_modifiers_bc_fc_ns` calls that effect three times a month (see [Performance](#performance)).

`common/on_actions/zz_ef_stockpile_state_var_init.txt` (new) hangs the same seven writes off `on_game_started_after_lobby`, which fires on every session, loaded saves included — E&F hangs `com_topbar_setup_ef` off it for exactly that reason. One guarded pass over `every_state` at load and the gate has real zeroes to read. Scope note: that on_action has none, so it is `every_state` (the top-level global list, same as E&F's top-level `every_country` at `00_ef_on_action.txt:349`) and **not** `every_scope_state`, which needs a country or region and would silently do nothing.

The history file stays. It is guarded the same way, so on a new campaign it runs first and the on_action finds nothing to do.

**Follow-up, 20:03 run — it did not clear them.** The reads fell from ~151 error blocks per in-game day to ~24, but most of that drop is [7g](#update_modifiers_bc_fc_ns-does-the-same-heavy-work-three-times-a-month) collapsing three transfert calls into one. Something about the seed is not reaching the states the gate walks. Two candidates, and `common/scripted_effects/zz_ef_stockpile_state_var_seed.txt` covers both rather than guessing between them:

1. `on_game_started_after_lobby` may not fire on a *loaded* save the way it does on a new campaign. A second hook on `on_monthly_pulse_country`, gated on a global variable, runs the seed once ever — one pass on the first country pulse after install, then never again. States neither appear nor vanish in Vic3, so once the variables exist they stay in the save.
2. `every_state` may not reach every state the gate walks. The gate is `any_scope_state` on a **country**, so the set that matters is exactly "states someone owns" — the seed now makes a second pass as `every_country` → `every_scope_state`, guarded the same way, writing nothing when the first pass was enough.

If the next run is clean, both are cheap enough to leave in. If it is not, the seed is not the problem and those reads are coming from somewhere other than the states a country owns.

### `common/history/buildings/00_a_ef_history_var_init.txt` — the `country_already_financial_center` spam

```
Failed to fetch variable for 'country_already_financial_center' due to not being set
Invalid left side during comparison 'var'
  common/scripted_effects/09_introduction_building_lvl.txt:22681
  common/history/buildings/00_ef_building.txt:2999
```

`00_ef_building.txt:2999` calls `financial_center_modifier = yes` for the historic financial-centre countries. That effect reads exactly two variables — nothing else:

| where | read |
|---|---|
| `financial_center_modifier` line 43 | `add_modifier = { name = financial_center_place  multiplier = var:gdp_view_fc }` |
| `financial_center_modifier` line 22725 | `not = { var:country_already_financial_center = 1 }` |

Both are initialised in exactly one place at campaign start — `common/history/global/00_ef_economic_global_variable.txt`, line 628 (`= 0`) and line 784 (`= 5`), both under `GLOBAL -> every_country`. And `common/history/buildings/` is processed **before** `common/history/global/`, so when the effect runs neither variable exists.

Checked the rest of what `00_ef_building.txt` calls, and this is the only one affected: `establish_bank_and_ef_compagnie` (9658 lines), `initialize_historic_macro_facilities_bc`, `initialize_historic_macro_facilities_fc` and `is_valid_country_hmm` read no variables at all.

**This one is not just log noise.** The failing read on line 43 is a modifier multiplier — when it comes back `none` the `financial_center_place` modifier is applied with a broken scale, so the historic financial centres start the game mis-sized. The comparison at 22725 failing really is cosmetic: history/global resets that flag to 0 immediately afterwards regardless.

The fix is a separate additive `BUILDINGS` block. Files in the folder are processed in name order and `BUILDINGS` blocks stack, so `00_a_` lands ahead of `00_ef_building.txt` without overriding it. Both writes are guarded by `has_variable`, so if the author ever moves his init earlier this file quietly becomes a no-op. The values are his: 0 and 5.

Found while digging, **not fixed**: `00_ef_building.txt:117` calls `initialize_historic_macro_facilities_ns = { ... }`, whose only definition is commented out at `09_introduction_building_lvl.txt:23546` — the call resolves to nothing. Removing it would change what the campaign starts with, which is the author's call, not a hotfix's.

---

## The leftover dev panel in the Economy tab

`common/scripted_guis/zz_ef_hide_debug_panel.txt` (new)

E&F ships its own debug UI: a small round **1** button under the budget tabs — widget
`Panel_1` in `gui/00_ef_deported_gui_1.gui`, sitting inside
`type budget_panel_economy_panel_content` — which opens
`gui/ef_dev_and_custom_windows/ef_custom_windows.gui`, a grid of unlabeled test buttons
(`PA PL L E I1 T 14 … 320`).

It is gated on the global variable `EF_debug_mode`, and `gui/01_ef_debug_widget.gui`
(registered through `gui/scripted_widgets/EF_scripted_widgets.txt`) does nothing but
mirror `[InDebugMode]` into that variable. So anyone launching with `-debug_mode` —
which is most people who want the console — gets a dev panel in the middle of the
budget screen.

It stayed invisible for a long time by accident: with E&F + TGR the Economy tab content
was never built at all, because the ComPatch's `budget_panel.gui` was a 1.12-era merge.
Once that was rebuilt on 21.08.2026 the tab started rendering — and brought the dev
panel with it.

```
REPLACE_OR_CREATE:EF_debug_mode_visibility = {
	is_shown = {
		always = no
	}
}
```

The button is hidden rather than the variable cleared: `EF_debug_mode` also gates E&F's
own debug decisions (`Open_Test_Decision` / `Close_Test_Decison` in
`common/decisions/00_ef_debug_decisions.txt`), which read it directly and are harmless
where they are. Removing the variable would be a wider change than this needs.

Comment the block out if you want the dev panel back.

---

---

## Performance

Same 1858 save, 2026-09-12. Three things account for most of it, in order of how cheap they are to act on.

**Measure unpaused seconds, not wall clock.** The first figure taken here — "five in-game days in 68 seconds" — was wrong: 59 of those 68 seconds were a pause. Summing only the unpause→pause intervals in `dedicated_server.log` against the `Processing Tick` dates is the honest number, and it moves the baseline by an order of magnitude.

| run | dates | in-game days | unpaused | s/day | to title | to idler |
|---|---|---|---|---|---|---|
| 19:43, before 7e–7g | `1858.1.1 → 1858.1.6` | 6 | 9 s | **1.50** | 105 s | 137 s |
| 20:03, after 7e–7g | `1858.1.1 → 1858.2.1` | 32 | 44 s | **1.38** | 40 s | 66 s |

So the monthly-pulse work is *not* what the tick time is made of — 7g cut the transfert from three calls to one (visible in `error.log`: three call sites at 300 error blocks each became one at 750) and the clock barely moved. The load times halving is almost certainly OS file cache on a second launch twenty minutes later, not anything in this mod. Both runs had `--debugmode` on.

### `--debugmode` is on, and it is the expensive one

`LaunchArguments` in the crash meta reads `--debugmode --gdprcompliant ...`, and the current session confirms it: `debug.log` carries `PostValidate of effect '...' returned false` and `Variable '...' is set but is never used`, neither of which is written outside debug mode.

Debug mode runs a validation sweep over every scripted effect at load. That sweep is what produced **7338 errors in the single second 19:42:59** and 2821 more at 19:42:40 — roughly 3 MB of `error.log` before the campaign even started, out of ~4120 error blocks for the whole session:

| count | error | what it means |
|---|---|---|
| 275 | `create_building [ Invalid production method: pm_unrefrigerated ]` | vanilla/TGR history builds with a PM that Grey's Food Industries Rework removed |
| 197 | `trigger_event [ Event not found! EventID: 00_ef_economic_event.N ]` | E&F calls its own events that do not exist (matching `.dds` icons missing too) |
| 166 | `create_building [ company: Not found in database class CCompanyTypeDatabase ]` | E&F's `establish_bank_and_ef_compagnie` naming companies that are not in the database |
| 95 | `activate_production_method [ Invalid production method 'pm_no_gold_consuption' ]` | referenced by `01_economic_scripted_effects.txt:139022+`, defined nowhere in E&F's `production_methods/` |
| 32 | `create_building [ Invalid production method: pm_manual_dough_processing ]` | same class as `pm_unrefrigerated` |

These are real incompatibilities and worth fixing on their own, but none of them is *caused* by debug mode — debug mode is what makes the game stop and write a callstack for each one. **This is now the only untried lever: run one session without `--debugmode` and compare s/day against the table above.** Keep it for hotfix work, drop it for play.

### `update_modifiers_bc_fc_ns` does the same heavy work three times a month

`00_on_action_main.txt:18423` runs on every country's monthly pulse and calls `stockpiling_capital_state_transfert` three times — once per branch:

| line | gate | calls |
|---|---|---|
| 18431 | owns `building_bank` | `central_bank_modifier`, then the transfert |
| 18483 | owns any of the ~40 financial centres | `financial_center_modifier`, then the transfert |
| 18493 | `national_stockpile` researched **and** owns a bank | `national_stockpile_modifier`, then the transfert |

`stockpiling_capital_state_transfert` takes no arguments and its first line (`01_economic_scripted_effects.txt:130847`) is `financial_center_modifier = yes`. So a country with a bank, a centre and the tech runs the transfert three times and `financial_center_modifier` **four** times a month — and `financial_center_modifier` is itself five `every_scope_state` passes with a 40-way `has_building` OR in each, plus `financial_center_production_methods`. For Britain that is on the order of 10⁵ building checks per month for one effect, repeated across every bank-owning country.

Nothing between the three calls changes what the transfert reads except the three `*_modifier` effects that precede them, and the transfert handles the central-bank and financial-centre cases in one body.

Patched in `common/scripted_effects/zz_ef_monthly_pulse_dedup.txt`: the three branches keep their own gates and their own modifier effects, each sets a flag instead of calling the transfert, and the transfert is called **once** after all three. **Transfert 3 → 1, `financial_center_modifier` 4 → 2.**

Why that is the same thing: the transfert takes no arguments, so three calls differ only in what the preceding modifier effects left behind, and it keys off `central_bank_historic_place` (written by `central_bank_modifier`) and `financial_center_site_var` (written by `financial_center_modifier`) itself. Calling it once at the end means both halves see all three modifier effects applied rather than one or two — in E&F the first call reads *last month's* `financial_center_site_var`, because this month's is not written until branch two. Later is fresher, not different.

Why a flag and not a re-check of the gates: `bank OR any-centre` would cover all three (the third gate is a subset of the first), but it means a second copy of the 40-name building list in the file and a silent hole the day E&F adds a forty-first centre. The flag follows whether a branch actually ran, so it cannot drift. One integer per country, rewritten to 0 at the top of every pulse.

⚠ **This is a key-level `REPLACE_OR_CREATE:` that carries a full copy of a 91-line E&F effect** (`00_on_action_main.txt:18423-18513` in 4.1.7). No E&F file is overwritten, but it has to be re-diffed after every E&F update — the four edited lines are marked `###` in the file, everything else is his, comments and all.

**7i, 2026-09-23 — two more edits to the same copy:**

- The redundant `financial_center_modifier = yes` in the second branch is gone: **`financial_center_modifier` 2 → 1 a month.** It is the expensive one of the three, since it strips and re-adds `financial_center_place` / `_spe` / `_historic_place` on every state of the country. The only effect is order (it now runs after `national_stockpile_modifier`), and the bodies were checked: `national_stockpile_modifier` (`09_introduction_building_lvl.txt:22735`) touches only `national_stockpile_*` modifiers and `country_already_national_stockpile`; `financial_center_modifier` (`:22136`) and `financial_center_production_methods` (`01_financial_scripted_effects.txt:25228`) read none of those, and the reverse holds too. Not measured in play yet.
- Before the one transfert call, the guarded per-state seed (`zz_ef_seed_stockpile_vars_on_state`, 7h) now runs over the country's own states. The one-shot seed missed states created after it ran (a state region split by conquest or cession gets a new state object), and the 23.09 run (1867 save) still logged ten blocks of `stockpiling_*_var_state_1 ... not being set` from the transfert's closing gate (`01_economic_scripted_effects.txt:133303`).

Measured on the 23.09 run, 1867 save, **still with `-debug_mode`** (Steam launch options): about 1–1.5 s per in-game day at speed 4, with occasional 6-second quarter-day ticks.

### The save is 460 MB

Vanilla saves at this date are tens of megabytes. E&F's per-state and per-country variable sets are what the rest is, and every one of them is walked on the pulses above. Not fixable from a hotfix — noted so it is not mistaken for something that is.

## Iron and lead mines carry the stock group twice (EF.12, 2026-09-23)

E&F's own `common/buildings/ef_03_mines.txt` lists `pmg_private_ownership_mining_stock` **twice** in its `INJECT:` on `building_iron_mine` and on `building_lead_mine` (lines 15/17 and 24/26 of the 92-line file; coal, sulfur and the two gold buildings list it once). An `INJECT:` appends list items, so every iron and lead mine in the world ends up with the group twice. Found by resolving the final building bodies over the whole playset, not seen in a log — nothing about it is ever logged. What a doubled group does in play was seen on 2026-08-28 on other buildings: double upkeep and double stock output (see `tools/regen_addon_greys.py`).

Fixed by overriding the file by **path**: `common/buildings/ef_03_mines.txt` here is E&F's file byte for byte (BOM and CRLF kept, no header of ours) minus those two lines, so after an E&F update the check is one diff:

```bash
diff <(tr -d '\r' < "E&F/common/buildings/ef_03_mines.txt") \
     <(tr -d '\r' < "E&F Hotfix/common/buildings/ef_03_mines.txt")
# expected: exactly the two `pmg_private_ownership_mining_stock` deletions
```

If E&F fixes it himself, delete the copy. If he adds anything else to that file, re-copy and delete the two lines again — the override hides whatever he adds.

## Bond buyer lists compared a number with a country (EF.13, 2026-09-24)

`common/scripted_effects/zz_ef_bond_buyer_list_type_fix.txt` re-issues E&F's ten `central_bank_debt_buyer_list_N_clear` (`08_list_effect.txt:1558-1737`). Each walked `every_country` testing `var:ai_seller_country_general_N = root`, but that variable is the number 0 on every country without a live AI bond, so each call wrote ~180 `Left side and right side during comparison were of different types (left was 'value', right was 'country')` errors with call stacks to both `game.log` and `error.log` — 4838 in twelve minutes on the 1867 save. The test is now `is_target_in_variable_list` on the same-named list that E&F writes and clears together with the variable; the reasoning that the two are equivalent for all ten slots is in the file header. The player half (`var:seller_country_general_N = root`) is dropped: E&F never sets that variable to a country, so the test was never true and only ever errored. Whether the author meant the player branch to run is an open question, not something to switch on silently.

## Balance pass, 2026-09-24 (EF.14–EF.17, EF.23) — not yet tested in game

Each file carries the full reasoning in its header; this is the map.

| Task | File | What |
|---|---|---|
| EF.14 | `common/production_methods/zz_ef_currency_liquidity_pm.txt` + `pm_currency_liquidity_currency` in the 9 non-English, non-Russian `zz_ef_cm_goods_l_*.yml` | The currency method gets the local-currency coin instead of the generic "currency type" picture; E&F ships its name in English only. The Russian name is in the V4 RUS translation (repo and local copy); the workshop copy of V4 RUS predates it and needs a re-upload. |
| EF.15 | `common/script_values/zz_ef_cb_bond_issuance_values.txt`, `common/static_modifiers/zz_ef_cb_bond_issuance.txt`, `common/scripted_effects/zz_ef_cb_bond_issuance.txt`, one call in 7g | Central bank bond output × (debt % of GDP / 50), clamped 0…3×, via `goods_output_bond_mult` on the bank building. The six minting methods are not touched. Knob: `zz_ef_cb_bond_reference_debt_pct`. |
| EF.16 | — | **Reverted the same day.** A company name has no COUNTRY context: `debug.log` "Data error in loc string 'zz_ef_cm_central_bank'". Back to the plain "Central Bank". |
| EF.17 (1) | `common/building_groups/zz_ef_financial_centre_group.txt` | `bg_financial_centre` urbanization 5 → 0. |
| EF.17 (2) | `common/static_modifiers/zz_ef_financial_centre_cap.txt` | Exchange ceiling: `_max_level_add` 1 → 0.1 in `financial_center_place` and `_spe`, i.e. one level per 10M of GDP instead of 1M. Covers the generic and all 41 national exchanges with one number. |
| EF.17 (4) | 7e in `zz_ef_div0_fix.txt` | **Reverted the same day.** Capping the output multiplier (25000 → 500) while the five input multipliers kept their own ceilings bankrupted every exchange — London in 1840 bought 269K a week of stock and sold 19K of funds. |
| EF.17 (4b) | `common/script_values/zz_ef_exchange_margin.txt` | Instead: the exchange's margin. E&F sizes output to 1.5 × the cost of the inputs; now 1.25. Output and cost move together, value added per worker roughly halves. |
| EF.23 | ~~`common/scripted_effects/zz_ef_capitalization_decay.txt`~~ | Capitalization counters decay 2 % a month. **Superseded 2026-09-24 by EF.24** (the file is now `zz_ef_capitalization_accumulation_off.txt`). |

Measure on a save after these (GDP, exchange levels and productivity, capital urbanization) before EF.17 (3, 5) and before EF.18 in the megapack is judged.

## Balance pass 2, 2026-09-24 (EF.22, EF.24, EF.25) — not yet tested in game

| Task | File | What |
|---|---|---|
| EF.24 | `common/script_values/zz_ef_capitalization_snapshot.txt` | Capitalization from this week's issuance, averaged: each stock's snapshot = the country's own weekly output × `zz_ef_cap_weeks` (520, a price/earnings multiple, not a time window) × E&F's price; shown capitalization = a moving average of monthly snapshots with weight 1/12 ("about the last year"). E&F's quantity values are re-issued as average / current price, so every quantity × price formula (menu, gold conversion, ranking) gives the average. Bonds = the real national debt (`country_credit` + `var:credit_at_central_bank`) / bond price: the bond line is E&F's register of debt on sale (`total_debt` → `remaining_debt`, what foreign central banks and private banks buy). |
| EF.24 | `common/scripted_effects/zz_ef_capitalization_average.txt` | Monthly per country: the four averages (1/12), a half-year average of the total (1/6), and E&F's stock market index as a level index (value when the country first had stocks × equity now / equity then). 5 averages + 2 for the index. |
| EF.24 | `common/scripted_effects/zz_ef_capitalization_accumulation_off.txt` | `stockpile_finacial_product` is empty: nothing reads the monthly counters any more. Replaces EF.23. |
| EF.24 | `common/scripted_effects/zz_ef_capitalization_crash.txt` | Every month (countries with a stock exchange): the half-year average now against the same average exactly 12 months ago, kept in 12 monthly marks `zz_ef_cap_m1..m12` (E&F compared two snapshots 6 months apart, once a year, with a gap). E&F's half-yearly effect is re-issued without its snapshot pair. Change → E&F's `country_indice_value_dif_01` (menu, country list, size of the crash consequences); below −50 % with equity above `zz_ef_crash_floor` (5M) and no crash in the last 15 months → `financial_crash`. The cooldown keeps one fall from being seen by two checks — the second call is what brings E&F's full consequences (exchanges demolished, −100 % throughput on private industry for 23 months). |
| EF.25 | `common/script_values/zz_ef_mass_shareholding_values.txt`, `common/static_modifiers/zz_ef_mass_shareholding.txt`, `common/on_actions/zz_ef_capitalization_on_actions.txt` | Mass shareholding: country modifier `building_company_worker_dividends_add` = 0.25 × min(1, equity capitalization / GDP), monthly, right after the averages (one on_action). Knob `zz_ef_mass_shareholding_max`. |
| EF.22 | `common/production_methods/zz_ef_company_hq_publicly_traded.txt`, `common/production_method_groups/zz_ef_company_hq_publicly_traded.txt` | "Publicly Traded" ownership for company HQs: capitalist-owned companies, `joint_stock_companies`, owners' shares to shopkeepers and clerks, 15 % of company dividends to workers, E&F's ~10 employment per level. TGR's trade layer for it is in the megapack (`_ef/ef+tgr done`). |

Names in all 11 `zz_ef_cm_goods_l_*.yml`.

| EF.24 (index) | `common/scripted_effects/zz_ef_capitalization_average.txt` | 2026-09-25: E&F's stock market index (points) = equity capitalization / GDP × 1000, monthly; points a year = the index minus its value at the last yearly mark. The 24.09 level index (10 × equity / equity in the first month) showed growth multiples of up to 12000 from a tiny first month. |
| EF.25 (literacy) | `common/script_values/zz_ef_mass_shareholding_values.txt` | 2026-09-25: the share × literacy. In the 1847 save capitalization / GDP was 0.6–2.1 everywhere, so nearly every country had the full 25 %. |
| EF.29 | `common/on_actions/zz_ef_bubble_on_actions.txt`, `common/journal_entries/zz_ef_financial_center_je.txt`, `common/script_values/zz_ef_bubble_values.txt`, `common/messages/zz_ef_bubble_messages.txt`, `common/static_modifiers/zz_ef_bubble_no_construction.txt` | 2026-09-25: the speculative bubble moved here from the E&F x PSC compatch — it follows the stock market, which is the hotfix's (EF.24, EF.28). E&F's monthly bubble code runs in our own on_action (with the `character_role_executive` fix and a feed notification); E&F's journal is re-issued without it; the bubble modifier has no construction malus. Behaviour unchanged. The compatch's journal section reads `zz_ef_bubble_step_eff`, so the compatch now depends on the hotfix. |
| EF.28 | `common/scripted_effects/zz_ef_stock_issue_literacy.txt`, `common/script_values/zz_ef_stock_issue_literacy_values.txt`, `common/static_modifiers/zz_ef_stock_issue_literacy.txt` | 2026-09-25: stock issuance × min(1, share of literate pops with wealth ≥ 15 in the whole population / 12 %). Monthly walk over the country's pops; country modifier `goods_output_<type>_stock_mult` on all four stocks. 1847 save: Britain 12 % (full issue), Russia 1 % (~8 %), Japan 0.7 %, China 0.5 %; Belgium 30 %, Netherlands 18 %. |
| EF.27 | `common/building_groups/zz_ef_central_bank_group.txt` | `bg_bank` (the central bank) urbanization 20 → 0 per level. 1847 observer run: Britain's central bank had 250 levels in the Home Counties — 5000 urbanization from one government building of 250 employees. Same reasoning as EF.17 (1) for the exchanges. |
| — | `common/scripted_effects/zz_ef_capitalization_crash.txt` | `debug_log` + `debug_log_scopes` before `financial_crash`: the 1847 run crashed some country once and `error.log` could not say which. Look for `ZZEF crash` in `debug.log` (not `game.log`). |
| — | `common/scripted_effects/zz_ef_capitalization_crash.txt` | 2026-09-25, 1850 run: no crash before 1838 — five countries "crashed" in 1836-37 because the year-ago marks start at the first month, before EF.28 cuts the issuance of low-literacy countries. The yearly change is now kept for every country (the E&F list showed 0.00% for countries without an exchange or under the 5M floor); the crash itself still needs an exchange and the floor. |
| EF.26 | — (file removed 2026-09-30, replaced by EF.30) | E&F's AI rate controller `base_rate_change` gated its "raise the rate" branch on `var:base_rate_percentage > 0.7` (a fraction, so 70%, never true). The `0.07` fix opened the branch, but the yearly pool credit is itself a function of the rate, so outside 6-7% the rate confirmed its own trigger and crawled to 11.1% (9 of 45 big countries at the ceiling in 1850) or to 2%. |
| EF.30 | `common/scripted_effects/zz_ef_central_bank_rate.txt`, `script_values/zz_ef_cb_rate_values.txt`, `on_actions/zz_ef_cb_rate_on_actions.txt`, `scripted_guis/zz_ef_cb_rate_buttons.txt`, `gui/00_00_ef_cb_rate_panel.gui` (generated, `tools/regen_ef_cb_rate_gui.py`), `localization/*/zz_ef_cb_rate_panel_l_*.yml`, `game_concepts/zz_ef_cb_rate_concepts.txt` | The central bank sets the rate, one rule for AI and player (v2, 2026-09-30). `base_rate_change` is emptied; every 3 months (monthly counter) the rate moves towards `zz_ef_cb_rate_target` by ≤ 0.5 pp (≤ 1 pp when the gap is over 5 pp). Target: the credit note 0..12.5 (10 from the score, +0.5 per central bank institution level) 0..10 mapped linearly onto 12%..2% (1 pp per point, above 10 stays at 2%), clamped 2-12%, plus the player's policy (±2 pp), never below 0.5%; no central bank → 6.5% (E&F's neutral, zero pool credit). `rise/down_base_rate` are set on each step (E&F reads them for currency arbitrage and inflation policy). The ±0.5 pp buttons (same names) move the rate and the target (policy ≤ ±2 pp), free, no cooldown (2026-09-30; v2 had 1% of GDP and 3 months — a standing penalty for deviating from the bank's target comes later, EF.31); every condition is a `custom_tooltip`. The E&F panel type `budget_panel_financial_panel_content` is re-issued with button tooltips (description, cost, conditions via `BuildTooltip`) and a row of boxes: rating, bank target, next step, government policy. v2 run to 1845 (2026-09-30): rates converge on the target quarterly, GBR 2%, USA 2.4%, FRA 4.6%, RUS 4.8%, no errors. The panel file must sort before E&F's `00_ef_deported_gui_1.gui`: the FIRST file to register a GUI type wins (`logs/gui.log`: "Type … already registered at …"); as `zz_ef_cb_rate_panel.gui` it was ignored (Prussia run to 1847). 2026-09-30 (Prussia/Tuscany run to 1847.9, works): the box row shows the **policy rule rate** (the bank's own rate from the rating, without the government's adjustment; red above the actual rate, green below) and the **discretionary adjustment**, both game concepts linked to E&F's; the rate still steers to rule + adjustment, penalties on the gap come later (EF.31). Button tooltips: `BuildTooltip` only (a separate `ExecuteTooltip` doubled the effect line). The copy is cleaned of E&F's own engine-rejected properties (`nobaseline` in `parentanchor`, `align` on icons, `ignoreinvisible`/`elide`/`default_format` where not taken, duplicated properties): 802 lines, matched line by line against the 1848 run's logs; nothing visible changes. Also (run 2026-09-30, 1848): E&F's 20 live debt buyer / seller lists were gated on `ai_quantity_purchasing_N_visibility` with `Country.MakeScope` at list level (no Country in context; E&F defines only `_1` of 19) — failed every frame, filled all six error.log rotations in a minute and kept the lists hidden; now `visible = no` (same look, no spam; showing them is EF.13 / UI). |
| EF.46 | `common/script_values/zz_ef_credit_rating_rank_fix.txt` | E&F's `country_credit_pondered_mean` scored only ranks 2-49 (and the player); the rank bonus 1..4 went only to countries without a central bank. A central bank country at rank 50+ got note 0 → credit rating D, which carries `market_disallow_trade_routes_bool` (all trade routes lost), and with EF.30 a 12% rate. 1845 run: FIN, TUS, PER, QUE, ONT, NPU. Key-level `REPLACE_OR_CREATE`: the score branch runs for every central bank country below rank 1; the rest is E&F 4.1.7 as is. Yearly, cheap. |
| EF.39 + EF.44 + EF.31 | `common/script_values/zz_ef_money_model_values.txt`, `scripted_effects/zz_ef_money_model.txt`, `on_actions/zz_ef_money_model_on_actions.txt`, `static_modifiers/zz_ef_rate_private_construction.txt` | Money model (decided 2026-09-30). E&F's "pop savings" only grew (France 1848: 1960M at GDP 85M) and inflated the money supply; the yearly `investement_pool_borrowing` added up to 10% of it to the pool: France 561M in the pool = 31 years of private construction, Belgium/Spain/Sweden ~0, and the rate no longer mattered for building. Now, monthly, every country: savings keep E&F's inflow and lose pops' outlays on goods and taxes (GDP/12 − pool contributions; saturating `outlays × S/(S+K)`, K = 24 months of outlays), through `pop_capital_loss_fix`; deposits `var:zz_ef_deposits` move towards a target share (literacy, central bank, rate, crisis); the pool is steered to deposits × credit multiplier (3 at 2%, 1.2 at 12%; up 5%, down 2% of the gap a month). `investement_pool_borrowing` replaced (REPLACE_OR_CREATE), only the private banks' bond interest kept. One-off seed: savings = 0.5 × GDP. Run 1836-1840: E&F's inflow is the whole market's currency demand written to the market owner only (Britain +2.13M/month, British India, Ontario, Bavaria 0) — split monthly by GDP share (`market.gdp`); savings over 2 × GDP are cut (currency law changes carry old counters over: Norway 9.3 × GDP). Composition (2026-09-30, after the 1848 run): `money_circulating` replaced (REPLACE_OR_CREATE) — E&F's `government_loan` counter out (cumulative minting, already paid into the treasury, + loans from the CB, which are debt: `var:credit_at_central_bank`), treasury (`gold_reserves` > 0) in, building cash = vanilla `credit` − `define:NEconomy|COUNTRY_MIN_CREDIT_BASE` − `..._SCALED` × GDP. M0 = CB reserves + treasury + savings, M1 = + business cash, M2 = + pool. Deposits now move into the pool (were only a claim). Monthly ledger per account (`var:zz_ef_f_*` flows, `var:zz_ef_d_*` changes, `zz_ef_other_*` residual). Gold parity re-anchored once to the current value (money supply dropped to M2: Britain 15.3 vs parity 7.32, cover 209%). Tooltip: `tools/regen_ef_money_supply_loc.py` → `localization/*/replace/zz_ef_money_supply_replace_l_*.yml` (E&F's 12 `MONEY_SUPPLY_DESC_*` keys, each account a nested tooltip with its card: the month's change, rows 1-4 = the other accounts, row 5 = outside (new money, vanilla, other), each `-> : +in` / `<- : -out`; cells then in a generated `zz_ef_money_ledger_values.txt`, removed the same day). EF.48 (2026-09-30): six accounts (savings, treasury, businesses, banks, CB, abroad) + outside; each transfer one entry in `tools/regen_ef_money_supply_loc.py` (FLOWS: from, to, label, value), shown in both cards with opposite signs; the treasury lists every budget line exactly through GUI data functions (`GetTrendValue(Country.Get…Trend)` × 4.333, labels are vanilla budget concepts); a card's other = change − listed, computed in the GUI (treasury: `zz_ef_other_treasury_budget` = change − (total income − total expenses) × 4.333); trade balance from E&F's `trade_balance_in_gold_delta` / `money_value_in_gold`. EF.48 steps 2-3 (2026-09-30, evening): `zz_ef_money_model_values.txt` rewritten by account; monthly step: pops' savings from flows (S moves 5%/month towards 4 months of income ≈ GDP/12; E&F's currency-good inflow taken back out; purchases are the card's closing line), deposits move into the pool, interest on deposits (key − 1.5 pp, ≥ 0.5%) pool → savings, bank credit borrowed from the CB (`var:zz_ef_bank_cb_debt`: borrow 5% of the gap below deposits × multiplier, repay 5% above, at most the debt; interest at the key rate pool → CB → treasury via `add_treasury`); no more credit from nowhere or contraction into nothing. Savings card: taxes and state pay exact, wages and dividends = GDP/12 − state pay, purchases = rest. **Revised the same evening (new game to 1838, user's decision): everything in the engine's money.** E&F's CB reserves and currency-good flows are counts of the liquidity_currency good, not money; pops hold no money in the engine (income → taxes, purchases, the rest becomes wealth), so the savings model, deposits and deposit interest are removed. `money_supply` (REPLACE_OR_CREATE) = `money_circulating` = treasury + business cash + pool (M0/M1/M2); the gold parity is re-anchored once more (`var:zz_ef_parity_version` = 2). Kept: bank credit borrowed from the CB — pool steered to a month's contributions × 12 months at 2% … 3 at 12%, borrow/repay 5% of the gap, interest pool → CB → treasury. Cards: treasury, business cash, banks (+ E&F private banks' foreign bonds from the change of Σ `ai_privat_bank_bond_value_1..25`), pops (transit, closed by purchases and wealth growth), CB (money transit), abroad, and E&F's currency-good stock (counts). **Weekly (2026-09-30, the user: the pool's card did not match the pool tooltip — a monthly step against weekly budget lines).** The engine has no weekly country pulse (script_docs `on_actions.log`), so the step is a chain: `zz_ef_money_model_weekly` re-triggers itself with `days = 7`; the monthly on_action (re)starts it via a daily probe (≤ 8 days) that waits for the budget tick (`gold_reserves − principal` changes), so each 7-day window holds one tick. Cards are per week, with no × 4.333; the pool's transfer to the treasury = `investment_pool_gross_income − investment_pool_net_income` at the step (the budget's `GetInvestmentIncomeTrend` is a smoothed trend); the treasury's other uses the budget stored at the step (`var:zz_ef_f_budget`). Borrow/repay 1.15% of the gap a week, CB interest rate / 52. M0/M1/M2: the week's change and % over a month (4 weeks), a year (49–52 weeks) and 5 years (248–260 weeks) from history rings (`zz_ef_<m>_w1..4`, `_q1..13`, `_r1..20`). E&F's currency good and EF.31's modifier stay monthly. **GUI bridge (2026-09-30, prototype):** script sees only budget totals, the lines outside the accounts (minting, additional income/expenses, diplomacy, treaties, power bloc, supply-network fees, tolls, piracy) are GUI-only. BPM's pattern: the weekly step queues the country in global list `zz_ef_hook_countries` (+ `var:zz_ef_hook_pending`, 6 days); `gui/zz_ef_money_hook.gui` (scripted widget, invisible, host only in MP) has a datamodel over that list and, on each item's creation, executes `scripted_guis/zz_ef_money_hook.txt` with `MakeScopeValue(sum of those lines)`; the receiver (idempotent — on_start may fire twice) stores `var:zz_ef_f_ext` and the week's M2 leak `var:zz_ef_f_leak` = ΔM2 − outside lines − CB net credit + foreign bonds bought. Reconciliation block: recorded vs live outside lines, the leak, and a settled/forecast check line (Trend vs budget-panel values). Debt interest moved from «outside» to treasury → pops (vanilla pays it to the owners of the buildings' reserves that back the loans). Bridge fix (2026-10-01): CMF's pattern (`_cmf/gui/com_hidden_trigger.gui`) — item state `trigger_when = [Scope.IsSet]` + `on_finish`, root widget 500×500; works when playing a country, **not in observer mode** (GUI commands are not executed). **Pops' savings and deposits (2026-10-01):** the receiver adds −leak to `var:zz_ef_pop_savings` (the money that dropped out of the engine's money: pops' income left over, which vanilla turns into wealth, merged with payments abroad inside the market); `var:zz_ef_pop_deposits` moves 2% of the gap a week to savings × deposit share (30% at a 4% key rate, +5 pp per pp, 10–70%) via `add_investment_pool` (withdrawals capped by the pool), interest at key − 1.5 pp (≥ 0.5%) pool → deposits. The operations fall into the next week's window (`var:zz_ef_w_dep_*`) and are taken out of that week's leak. Tooltip: savings line under M2, pops' card with a savings block and «into savings» line, banks' card with deposits, withdrawals and interest. Savings outflow computed ratio-first: S × outlays overflowed the engine's fixed point (~9.2e13; Britain 60M × 6.6M), giving 150K for 1.8M. EF.31: the rate moves the private share of construction points (+0.225 at 2%, 0 at 6.5%, −0.275 at 12%, ±0.3). The money supply E&F sums is now M2; exchange rates move — recalibrate after a run. |
| EF.48 night 1.10 (items 1-14) | `script_values/zz_ef_money_model_values.txt`, `scripted_effects/zz_ef_money_model.txt`, `scripted_effects/zz_ef_rate_policy.txt`, `static_modifiers/zz_ef_consumer_credit.txt`, `zz_ef_rate_policy.txt`, `zz_ef_treasury_out_of_circulation.txt`, `zz_ef_financial_centre_cap.txt`, `gui/00_00_ef_currency_symbol_fix.gui`, `script_values/zz_ef_cb_rate_values.txt` | The user's decisions of 1.10 (План проекта.md, «Решения 1.10»): trade centres' cash and the pool's unexplained change are flows abroad, not pops' savings; deposits 5%/week; the CB and abroad are one account — the net flow abroad moves the CB's metal (Hume), E&F's trade balance left `national_capacity`; top sums in gold; consumer credit through a uniform dependents' surcharge (limit 4 months of income, key + 3 pp, a year); business credit as accounting; the treasury out of circulation (E&F's `money_supply` = business cash + pool, CB treasury cap ×4 → ×2); `inflation_value` = M3 growth − GDP growth a year; the rate policy costs −100 authority and up to −5 approval of hard/soft money groups per 0.5 pp; bubble signs shown; risk premium + default, radicals, legitimacy, war, literacy; one currency-symbol textbox instead of ~220; the exchange's GDP-scaled market-access price impact removed. |
| EF.48 В2.1 (2.10) | `scripted_effects/zz_ef_reserve_trade.txt`, `script_values/zz_ef_reserve_trade_values.txt` (generated: `tools/regen_ef_reserve_trade.py`), `scripted_effects/zz_ef_money_model.txt` (monthly step) | Trade reserve currency as a flow. E&F's `trade_balance` (REPLACE_OR_CREATE) counted units exported to every foreign currency's market with a `while` stepping by 1 (up to 5000 a currency) and `stockpiling_currency_type_1` added the value to the exporter's reserve forever, the importer losing nothing, on top of the metal our Hume step already moves (run 20: 10–65 million a state). Now its counters are zeroed once (the old reserve stays in old saves) and `trade_balance_in_gold_fixe` goes. Monthly `zz_ef_rc_step`: for each pair of market owners with a CB, the week's exports both ways (`market_exports`, binary search, 19 checks) × each market's average export price; the importer pays `zz_ef_rc_share` (25%) of the net in currency instead of metal — first it hands back the exporter's currency it holds, the rest the exporter's CB takes in the importer's currency (`stockpiling_<cur>_state_1`, at the importer's parity); the exporter's CB gives up that much metal, the importer's gets it (metal standards). `zz_ef_fx_liab` = the currency held by other CBs. AI CBs on the forex monthly was tried and taken back (run 24: E&F's purchases at parity twelve times a year blew the reserves up). Run 23: the importer also got the metal back, and the exporter's metal was valued at today's value — reserves out of nothing (Prussia 24 → 1401); fixed: no metal to the importer, valued at parity. Log EFX: `rcin`, `rcback`, `rcmetal`, `liab`. |
| EF.48 В2.3 (2.10) | `production_methods/zz_ef_gold_mine_minting_off.txt`, `scripted_effects/zz_ef_money_model.txt` (`zz_ef_mint_step`), `script_values/zz_ef_money_model_values.txt` | Gold mined was counted three times: vanilla's `country_minting_add` of every gold method into the treasury (picks 250 … diesel 1000, nitroglycerin 125, dynamite 250, the gold field 500), our CB coining half of it, and the gold sold on the market. Vanilla's minting is cancelled by counterweight INJECTs (−N; repeated keys in a modifier block add up). The CB's coined money is split by `zz_ef_mint_treasury_share` (0.01 = 1% brassage to the treasury, the rest to the owners — pops' savings; 1 = all to the treasury) — a parameter until a run shows the sums (EFR `mint`, `mint_tr`); tooltip flows «чеканка ЦБ — владельцам» and «брассаж в казну». |
| EF.48 В4.1 (2.10) | generated by `tools/regen_ef_monetary_policy.py`: `scripted_effects/zz_ef_monetary_policy.txt`, `script_values/zz_ef_monetary_policy_values.txt`, `scripted_triggers/zz_ef_monetary_policy_triggers.txt`, `scripted_guis/zz_ef_monetary_policy_buttons.txt`, `laws/zz_ef_monetary_policy_laws.txt`, `localization/*/zz_ef_monetary_policy_l_*.yml`; panel row — `tools/regen_ef_cb_rate_gui.py` (`mp_row`) | Devaluation / revaluation as a CB tool. E&F's laws only hung a modifier (currency-good demand ×1.25…1.75, its own inflation counter) — nothing in our money; the AI devalued on a petition `money_supply_state_ratio < 0.1`. Now the measure is the metal cover: the law remembers it (start = target), the player moves the target (−5 −1 +1 +5 pp) and the pace (1–5 pp a month) in the CB panel; devaluation prints `M2 × pace / cover` a month into the treasury (minus what the treasury has not spent yet), revaluation takes `M2 × pace / (cover + pace)` out of it (at most the treasury and what is needed). Target reached → parity = today's value (`money_value_target_1 = money_value_0`), law back to none, E&F's modifiers removed, 2-year AI cooldown. AI: devaluation at cover < 30% and value ≤ 75% of parity, revaluation at cover > 60% and value ≥ 125%, target 40% (`activate_law`; laws re-issued with `ai_will_do = no`). E&F's 25/50/75% buttons hidden. Log `EFM` (step / done). |
| EF.48 В5.1 (2.10) | `scripted_guis/zz_ef_cb_loan.txt`, `script_values/zz_ef_cb_loan_values.txt`, `localization/*/replace/zz_ef_cb_loan_replace_l_*.yml` (generated: `tools/regen_ef_cb_loan.py`) | The government's loan from the CB: E&F moved the share by 5% of GDP with no cap and «take» could be pressed any number of times. Now step 0.5%, share 0.5–50%, «take» only while the debt to the CB after it stays within 50% of GDP (`zz_ef_cb_loan_after_to_gdp`; checked in the effect too — E&F's button has no `enabled` binding). E&F's `debt_issued_relative_GDP_2` re-issued with `|%1`. Bond slots (5 / 10) unchanged. |
| EF.48 В3.3 (2.10) | `script_values/zz_ef_customs_union_values.txt`, `scripted_triggers/zz_ef_customs_union_triggers.txt` (generated: `tools/regen_ef_customs_union.py`), `zz_ef_trade_net_week` (money model values), the receiver | A customs union member keeps its own currency. E&F's `money_value` gave every country outside its own market the owner's value (and `money_value_in_gold` the owner's standard) — a Zollverein state with its own CB and metal had no currency of its own; the engine counts no exports inside a market, so Hume saw nothing of its trade. Now `zz_ef_currency_own` (owner, or a member with a CB that is not a subject) replaces `market_owner_is_root_4` in both (REPLACE_OR_CREATE); the member's trade account = Σ over the 53 vanilla goods of its states' production − consumption × the market price (goods of other mods left out: `sg:` takes fixed keys); the owner's trade = the market's exports − imports − the members' accounts. Members are in the EFR log. |
| EF.45 + EF.43 | `common/script_values/zz_ef_cb_rate_values.txt`, `scripted_guis/zz_ef_cb_rate_buttons.txt`, `tools/regen_ef_cb_rate_loc.py` | The policy rule rate was 12% − 1 pp × credit note. Now a Fisher-style rule: 2.5% neutral real + consumer goods inflation (6-month rolling × 2; other E&F goods groups too noisy) + risk premium 0.6 pp per note point below 10 (0-6 pp) + metal cover (<75% +1, <50% +2, >125% −0.5). Corridor by standard: metal 2-12%, fiat / no system 0.5-25%; the buttons' ceiling follows it. Rule box tooltip lists the four parts. Localization generator moved from scratch into `tools/regen_ef_cb_rate_loc.py`. |
| loc | `localization/*/replace/zz_ef_cm_goods_replace_l_*.yml` | `liquidity_currency` ("Local Currency") moved to `replace/`: E&F and V4 RUS define the key first and localization is first-come, so the name never showed. |

### Found by the 1836–1840 observer run with the local hotfix (2026-09-24)

- **Minor-country currency printed nothing since EF.10.** `zz_ef_local_currency_fix` gives `state_sell_orders_liquidity_currency_add`, a modifier type nobody declared (vanilla declares these per good, E&F only the `local_currency` one). Declared in `common/modifier_type_definitions/zz_ef_liquidity_currency_sell_orders.txt`, name in all 11 languages.
- **Dead market-weight loop removed** from `zz_ef_cm_bank_company_upkeep`. It summed `zz_ef_cm_issuer_weight`, which was deleted on 02.09.2026 together with everything that read the sum; the add failed at load ("Badly read script value"), and the loop walked `every_country` for every country every month (138 invalid-market errors).
- `log =` → `debug_log =` in the same file (`Unknown effect log`).
- **`zz_ef_new_country_immediate_init.txt` is additive now.** It put `effect = { }` straight into six vanilla on_actions; an on_action holds one effect and ours, loading last, replaced vanilla's, Morgenröte's, Grey's and ETF's. Each vanilla on_action now only lists our own on_action. BOM added to it and to its events file.
- 7a–7e: `has_variable` before the `base_*_fix > 0` checks (a country E&F never initialized logged `none`, 19 × 6).

## Стройка: PSC (бывший компач E&F × PSC)

С 02.10.2026 здесь (СТР.6). E&F держит отдельное здание частной стройки
`building_ef_private_construction` в группе без госфинансирования: его потребление не попадает
в бюджет, а очки стройки оно даёт — вдвое больше ванильного сектора за четверть товаров. Хотфикс
отключает его и переводит E&F на сектор PSC `building_construction_sector`.

| файл | что делает |
| --- | --- |
| `buildings/zz_pb_ef_disable_ef_private_construction.txt` | здание E&F не строится |
| `buildings/zz_pb_ef_construction_sector.txt` | сектор PSC: `pmg_market_liquidity` E&F, флаг запрета в `can_build_private`, `ai_value` сверх лимита ÷ 2 |
| `buildings/zz_pb_ef_investment_score_patch.txt` | цель финансового квартала для `bg_construction` |
| `company_types/00_ef_companies.txt`, `scripted_effects/zz_financial_scripted_effects.txt`, `history/buildings/00_ef_building.txt`, `localization/*/replace/zz_pb_ef_psc_je_l_*` | замена здания E&F на сектор PSC — `tools/regen_ef_psc_copies.py` |
| `script_values/zz_pb_ef_overbuild_values.txt`, `on_actions/zz_pb_ef_overbuild_counter.txt`, `static_modifiers/zz_pb_ef_overbuild_modifiers.txt`, `messages/zz_pb_ef_overbuild_messages.txt` | EF.18 v2: лимит секторов = городские центры × (1 − 5 × ставка), индекс избыточных мощностей идёт к цели `100 × (1 − лимит / секторы)`, штраф −1% выработки секторов за пункт, уведомления |
| `script_values/zz_pb_ef_remap_pcs_values.txt` | `building_ef_private_construction_lvl` E&F считает секторы PSC |
| `script_values/zz_pb_ef_ai_construction_values.txt` | подталкивание ИИ строить секторы при дорогих стройматериалах |
| `script_values/zz_pb_ef_psc_scope_fix.txt` | ошибка PSC: цена стройки в области читала регулятор, которого там нет (в мегапаках с T&R — слитая версия с бетоном) |
| `production_methods/zz_pb_ef_construction_pm.txt`, `zz_pb_ef_point_conversion_ui.txt` | методы стройки PSC без акций E&F; подписи пересчёта очков |
| `journal_entries/zz_pb_ef_financial_center_je.txt`, `gui/scripted_widgets/zz_pb_ef_fso_widgets.gui`, `scripted_guis/zz_pb_ef_fso_sguis.txt` | журнал УФС: секции пузыря и избыточных мощностей, без кнопки 13 |
| `scripted_buttons/zz_pb_ef_css_private_ban_buttons.txt`, `scripted_buttons/zz_ef_buttons.txt`, `scripted_guis/zz_pb_ef_speculative_pcs_sguis.txt` | запрет/разрешение частных секторов; кнопки стимула 9-12 (выключены 30.09, СТР.4) |
| `localization/*/replace/zz_pb_ef_psc_l_*`, `zz_ef_psc_modifiers_l_*`, `zz_ef_tgr_private_ownership_stock_l_*`, `localization/*/zz_pb_ef_overbuild_l_*` | тексты (en + ru, прочие — английский) |

Открытые задачи по стройке — `План проекта.md`, блок Г.

### История (из README компача)

> **25.09.2026, поздняя ночь — кнопки стимула 9-12 (по прогону 1850, решение пользователя).**
> Кнопки больше не строят секторы (частная очередь их не брала) и не требуют нулевого штрафа:
> снижение ставки на 1-4% с ценой +10 пунктов штрафа мощностей за 1%, доступно при штрафе
> < 90 / 80 / 70 / 60, откат 12 месяцев. ИИ-ветка (`zz_ef_buttons.txt`) выключена. ИИ снимает
> запрет частных секторов при штрафе < 10 (было «= 0», запрет залипал). 30.09 кнопки выключены (СТР.4).

> **25.09.2026, ночь — шкалы в панели через CMF.** Убрана копия `gui/journal_entry.gui`; запись
> журнала кладёт пустой виджет `zz_pb_ef_fso_hide_bars_widget` в
> `com_custom_widget_container_scripted_progress_bars` — CMF не рисует стандартные шкалы этой
> записи. Без CMF шкалы в панели задвоятся, и только.

> **25.09.2026, поздний вечер — пузырь ушёл в хотфикс (EF.29).** Месячный пересчёт пузыря,
> уведомление, значения шага и модификатор без штрафа стройки — в хотфиксе; у стройки остался вид
> секции в журнале.

> **25.09.2026 — избыточные мощности v3–v5** (по прогону 1837: при −85% эффективности стройки
> Британия нарастила стройку 400 → 750). Штраф — на выработку секторов
> (`building_construction_sector_throughput_add` −1% за пункт). Индекс идёт к цели по 2 в месяц
> при разрыве > 10, иначе по 1. Секция стройки — таблица 2 × 4 в стиле бюджета E&F (секторы,
> городские центры, ставка, лимит / соотношение, цель, динамика, текущий штраф), кнопка запрета.

> **24.09.2026 — EF.18 v2, журнал УФС, локализация в `replace/`.** Лимит секторов от городских
> центров и ставки (`building_urban_center_lvl_by_base_rate`, ручка `zz_pb_ef_css_rate_mult`);
> счётчик `speculative_share_2` ведёт наш on_action; журнал `financial_center_je_2` переиздан без
> кнопки 13 (она сносила `building_ef_private_construction`, которого под PSC нет); все
> перекрытия чужих строк — в `localization/<язык>/replace/` (локализация — «кто первый»).

---

## Left undone

- `pm_fiat_standard_bank_money_currency` (E&F, `15_ef_bank.txt`) has its `country_modifiers`
  nested inside `building_modifiers`, so fiat standard mints nothing (`country_minting_add = 250`
  never applies). Silent — nothing in error.log. Not fixed: it changes balance, and it is the
  author's to decide.
- The Tunisian and Yugoslav dinars are left in: tags `c:TUN` and `c:YUG` stand behind them.
- `bank_je_central_1` cannot complete (see the currency laws section). A bug report for the
  E&F author, not something to patch here.
- 39 of the 95 currency laws still carry `possible = { always = no }`, from the days when
  their goods were commented out by E&F's own author. Their production methods are retargeted
  now like every other, so the block may well be obsolete — worth a look before the next
  release.
- `budget_panel.gui` and `construction_panel.gui` are as far behind vanilla as the six files
  that were restored, but they hold real E&F reworks and need a manual merge rather than a
  vanilla swap.

All of this is worth sending to the E&F author — it is far cheaper to fix on his side.

---

## Maintenance

The mod overrides E&F files by **path** (`ef_00_goods.txt`, `00_ef_building.txt`,
`00_ef_alert_types.txt`, `01_ef_currency_type.txt`, `00_ef_pop_needs.txt`, `ef_03_mines.txt`,
seven `.gui` files)
and E&F **keys** by prefix (everything `zz_ef_cm_`). Which means:

- **after every E&F update** the generator has to be re-run, otherwise the hotfix rolls his
  changes back;
- **after every game patch** the six restored vanilla `.gui` files have to be re-copied from
  the new vanilla — and `gui/companies_panel.gui` rebuilt from it, since it is the new
  vanilla file with the not-yet-established block replaced (see
  [The companies panel](#the-companies-panel)).

```
python3 tools/regen_ef_currency_merge.py --check    # has anything drifted
python3 tools/regen_ef_currency_merge.py            # rebuild
python3 tools/regen_ef_currency_merge.py --private-bank   # ...with a privately funded bank
```

Hand-written originals of the two path-overridden data files live in `_gen_source/` — the game
does not read that folder, and those are the ones to edit. `common/goods/ef_00_goods.txt` and
`common/pop_needs/00_ef_pop_needs.txt` in the mod are generator output and get overwritten.

**Construction (PSC part).** After every E&F update: re-merge E&F's
`common/history/buildings/00_ef_building.txt` into the hotfix's copy by hand (it carries the
hotfix's own edits), then

```
python3 tools/regen_ef_psc_copies.py --check    # drift (exit 1 if anything would change)
python3 tools/regen_ef_psc_copies.py            # rebuild the copies, rename in place
```

It copies `00_ef_companies.txt`, `establish_bank_and_ef_compagnie` and the journal strings from
E&F with the building renamed, renames inside `00_ef_building.txt`, and fails if another hotfix
file touches a generated key from the wrong side of it in filename order.

Every run prints what it changed and self-checks the result: top-level key names, duplicate
keys, brace balance with comments stripped, and that what was read is what was written. Two
bugs that each killed the game before the main menu are caught by that check.

Things worth re-checking against a new E&F by hand:

```bash
cd vic3_mods_out

# is the div/0 still there? (the author's own comment marks it)
grep -n -A3 'target_demand_bond_ajusted' "E&F/common/script_values/00_financial_scripted_value.txt"

# is the supply twin still the only _for_modifier without a max?
grep -n -A8 'target_supply_mutual_fund_for_modifier' "E&F/common/script_values/00_financial_scripted_value.txt"

# re-diff the copied effect -- 7g carries a full copy of this one
sed -n '/^update_modifiers_bc_fc_ns = {/,/^}/p' "E&F/common/scripted_effects/00_on_action_main.txt" \
  | diff - <(sed -n '/^REPLACE_OR_CREATE:update_modifiers_bc_fc_ns/,/^}/p' \
      "E&F Hotfix/common/scripted_effects/zz_ef_monthly_pulse_dedup.txt" | sed 's/^REPLACE_OR_CREATE://')

# is the seller scope still dereferenced unguarded?
grep -n -A2 'scope:seller.owner' "E&F/common/scripted_effects/01_economic_scripted_effects.txt"

# are both history bugs still alive?
grep -n 'STATE_ANDALUSIA' "E&F/common/history/buildings/00_ef_building.txt"
grep -n -A3 '#GRE'        "E&F/common/history/buildings/00_ef_building.txt"

# is the typo still there? (if not, the laws override can be dropped)
grep -c 'currency_standars' "E&F/common/laws/01_ef_currency_type.txt"

# is the dev panel still gated on EF_debug_mode?
```

---
