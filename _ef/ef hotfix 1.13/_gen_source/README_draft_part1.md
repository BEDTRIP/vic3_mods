# E&F Hotfix

Fixes for **Economic and Financial**, repository version **04.07.2026**, on Victoria 3 **1.13**.
Load it **after E&F**. It does not depend on any compatch and works without them.

The headline change is the **currency merge**: E&F's 57 currency goods become one, which is
what lets E&F share a build with Tech & Res, Morgenröte or PSC at all. The rest is a list of
independent repairs — history, GUI, alerts, local currency issuance, currency laws, script
guards, dev panel.

Most of the mod is **generated** from E&F's own files by `tools/regen_ef_currency_merge.py`.
Files with a `zz_ef_cm_` prefix are its output and must not be edited by hand; see
[Maintenance](#maintenance).

---

## 1. The currency merge — 57 goods into one

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
own. The hotfix used to fight that by recomputing how much of it gets issued (see block 8);
merging removes the cause instead of the symptom, because there is no longer a cheaper
currency to switch to. It is the same good at the same price.

It also frees a name and an icon. The surviving good is called **Local Currency** and wears
`local_currency`'s icon, because that is what it is: the plain money every country makes.

### Why it was safe to do

E&F's exchange rates, money supply, gold and silver standard, stockpiles, imports and
exports run on country and global **variables**, not on the market data of the currency
goods. Of the 36 script-value families E&F defines per currency, 14 are referenced nowhere
at all — including every one that reads `market.mg:<X>_c.market_goods_*`.

The one live consumer of a currency good's market data was the money-issuance controller:

```
target_demand_currency              = market.mg:<own currency>.market_goods_buy_orders
target_demand_currency_for_modifier = (target − current output) / current * 100
currency_demande on the bank        = goods_output_<cur>_mult 0.01 * that
```

The bank drives its output until it equals market demand for its currency. That was
self-limiting while every country had its own good — "demand for the pound" was, near
enough, Britain's demand. With one shared good it became the whole market's demand and every
bank chased all of it: six banks on the British market issued ~196K each against ~192K of
buy orders, price −99%. Rewritten to split the market's demand between its issuers by GDP —
one field that tracks both halves of the demand, pops through `popneed_currency` and
buildings through `pmg_market_liquidity`.

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

## 2. The three monetary standards

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

---

## 3. The central bank and the company that owns it

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
* **Growing an existing building hands the new levels to the state.** `add_ownership` only
  covers levels created together with the building, and E&F grows the central bank by calling
  `create_building` again with a bigger level. Finland came out 5 levels company-owned and 5
  state-owned. So the bank is **rebuilt**, not expanded.

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
monetary standard law rather than by the currency, the currency had nothing left to select
and the ninety-five bought nothing.

All 98 get `building_bank` on their `building_types` and the three regime currencies on
their `possible_prestige_goods`, by `INJECT:` — nothing is taken away, so nothing needs
restating.

**`building_types` is the only real lock on who may own a building.** A monopoly is a price
and construction rule, not a lock: in the Papal States, Banca d'Italia privatised four levels
of the central bank out from under the company that held the monopoly.

### When the historical bank turns up later

A country can hold a stand-in company for years and then be handed its own historical bank.
Ownership cannot be moved, so the bank is torn down and built again under the new owner. The
upkeep pass calls that rebuild **itself** rather than waiting for E&F: E&F calls its spawners
when `gdp_view` crosses a threshold, not on a schedule, so for a country whose economy is not
growing the call never comes.

The size is passed as a literal, one branch per level. `$CB_SIZE$` is a macro argument —
pasted in as text — and it lands inside `add_ownership = { company = { levels = $CB_SIZE$ } }`
where a `var:` read does not resolve. Passing one there cost four countries their central bank
outright: the building was removed and recreated with zero levels, with nothing in any log.

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

## 4. The market panel

E&F gives currencies their own tab in the market panel, "Currency in Circulation", built from
a hard-coded list of all 95. With one currency the tab is a list of one, and it had a bug of
its own: it always showed the **player's own market**, whichever market panel you opened it
from.

The tab is removed, along with the two list-builders that fed it, and the currency good now
appears in the ordinary goods grid like everything else. That last part needed one more edit:
E&F hides financial products from the grid by name, through a `visible` expression on
`goods_entry_button` built from 105 `EqualTo_string(Goods.GetKey, ...)` terms. 94 of those
goods no longer exist, so the whole expression is rebuilt from the eight that do.
