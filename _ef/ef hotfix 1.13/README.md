# E&F Hotfix

<!-- meta
мод: свой хотфикс E&F 1.13
статус: done, переписан под E&F 02.09.2026 (EF.1-EF.8), торговля/формула/престиж
  возвращены на liquidity_currency (EF.9), local_currency и liquidity_currency
  объединены в один товар (EF.10) — тем же вечером, см. План проекта.md
версии: —
позиция: —
файлов: 39
генератор: — (списан 02.09.2026, tools/_to_delete/regen_ef_currency_merge_retired_2026-09-02.py)
зависит от: —
-->

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

## Для мастерской

Paste as is into the workshop page.

```
[h1]E&F Hotfix [1.13][/h1]
Fixes for [b]Economic and Financial[/b] (repo version 04.07.2026) on Victoria 3 [b]1.13[/b].
Load [b]after E&F[/b]. Works with or without any of the compatches.

[h2]Load order[/h2]
[list]
[*]Community Mod Framework (CMF)
[*]Expanded Topbar Framework (or Dense UI)
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

### `common/scripted_effects/zz_ef_currency_scope_guard_fix.txt` — dereferencing a scope that may not exist

`sell_currency_privat_bank` builds a seller/buyer pair out of an ordered list and then does, unconditionally:

```
scope:seller.owner = { save_scope_as = seller_country }
```

If the list came back empty there is no `scope:seller`. The same holds for `scope:central_bank_site` in the two metal-transfer branches further down. The fix aborts cleanly on a missing seller and adds `exists = scope:central_bank_site` to those two limits. The arithmetic is untouched.

Verified still unguarded in E&F 04.07.2026 on 2026-08-19.

### `common/history/global/zz_ef_init_stockpiling_state_vars.txt` — ⚠ probably redundant, verify and delete

Additive `GLOBAL` block that fills in seven state variables (`stockpiling_{bond,manufacture_stock,agricultural_stock,mining_stock,railroad_stock}_var_state_1`, `financial_center_site_var`, `looted_state`) if they are missing. It was written against E&F v4.1.1 to stop startup spam of `Failed to fetch variable ... due to not being set` and `Invalid left side during comparison 'var'`.

Re-checked against E&F 04.07.2026 and it now looks unnecessary: `common/history/global/01_ef_state_global_variable.txt:1362-1389` already sets all seven inside `GLOBAL = { every_state = { ... } }`, which covers unowned states too, and a sweep of `common/` found no `stockpiling_*` variable that is read via `var:` but never set (552 read, 2303 set, 0 orphans).

It is kept for now only because the original log that showed the spam could not be re-read during this pass. **Start a game with this file disabled, grep `error.log` for those two lines, and if it is clean, delete the file.** Every write is guarded by `NOT = { has_variable = ... }`, so leaving it in cannot do harm in the meantime — it just runs a loop over every state at game start for nothing.

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

## Left undone

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
`00_ef_alert_types.txt`, `01_ef_currency_type.txt`, `00_ef_pop_needs.txt`, seven `.gui` files)
and E&F **keys** by prefix (everything `zz_ef_cm_`). Which means:

- **after every E&F update** the generator has to be re-run, otherwise the hotfix rolls his
  changes back;
- **after every game patch** the six restored vanilla `.gui` files have to be re-copied from
  the new vanilla.

```
python3 tools/regen_ef_currency_merge.py --check    # has anything drifted
python3 tools/regen_ef_currency_merge.py            # rebuild
python3 tools/regen_ef_currency_merge.py --private-bank   # ...with a privately funded bank
```

Hand-written originals of the two path-overridden data files live in `_gen_source/` — the game
does not read that folder, and those are the ones to edit. `common/goods/ef_00_goods.txt` and
`common/pop_needs/00_ef_pop_needs.txt` in the mod are generator output and get overwritten.

Every run prints what it changed and self-checks the result: top-level key names, duplicate
keys, brace balance with comments stripped, and that what was read is what was written. Two
bugs that each killed the game before the main menu are caught by that check.

Things worth re-checking against a new E&F by hand:

```bash
cd vic3_mods_out

# is the div/0 still there? (the author's own comment marks it)
grep -n -A3 'target_demand_bond_ajusted' "E&F/common/script_values/00_financial_scripted_value.txt"

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
