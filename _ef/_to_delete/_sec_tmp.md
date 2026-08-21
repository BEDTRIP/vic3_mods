## 9. Currencies merged into one good — and given back as prestige goods

This is the block that turned the hotfix from a patch into something bigger, and it
is the reason E&F can now share a build with Tech & Res at all.

### The arithmetic

Vanilla 53, PSC 4, E&F with this hotfix 65, Morgenröte 5, Tech & Res 35 — **162**
against a ceiling of 128. 57 of E&F's 65 goods are currencies, one per monetary
system law.

Collapsing 56 of them into `spe_uni_c` takes the pack to **106**, with 22 slots to
spare and Tech & Res whole — no cutting eras, data goods or androids.

Nothing about the monetary system is removed. All 95 currency laws stay, every
country keeps its own law and its own `pm_currency_*`, the bank still mints, the
buildings still pay for liquidity. Only the good on the belt is shared.

### Why it was safe to do

E&F's exchange rates, money supply, gold and silver standard, stockpiles, imports
and exports run on country and global **variables**, not on the market data of the
currency goods. Of the 36 script-value families E&F defines per currency, 14 are
referenced nowhere at all — including every one that reads
`market.mg:<X>_c.market_goods_*`.

The one live consumer of a currency good's market data was the money-issuance
controller:

```
target_demand_currency              = market.mg:<own currency>.market_goods_buy_orders
target_demand_currency_for_modifier = (target − current output) / current * 100
currency_demande on the bank        = goods_output_<cur>_mult 0.01 * that
```

The bank drives its output until it equals market demand for its currency. That was
self-limiting while every country had its own good — "demand for the pound" was,
near enough, Britain's demand. With one shared good it became the whole market's
demand and every bank chased all of it: six banks on the British market issued
~196K each against ~192K of buy orders, price −99%. Rewritten to split the market's
demand between its issuers by GDP — one field that tracks both halves of the demand,
pops through `popneed_currency` and buildings through `pmg_market_liquidity`.

### The currencies came back as prestige goods

Prestige goods do not count against the 128 — measured with a hundred dummies on one
base good, not assumed. So all 95 currencies return as prestige variants of the
shared good, with their own names, their own icons, a prestige bonus and the
engine's +20% throughput for buildings that consume them.

**The prestige good reuses the old good's key** (`pound_sterling_c`). It stopped
being a good when the merge commented it out, so the name was free — and every
piece of localisation E&F ships for it, in eleven languages, plus the separate
Russian translation mod, keeps working untouched. Zero translation work.

**Which one a company produces is decided by the currency law, not by the company.**
Company → country is not in the files: 6 of E&F's 103 companies name a tag, the rest
go by interest markers. So every bank company is offered all 95 and each prestige
good carries `possible = { has_law = law_type:law_<cur>_currency }`.

### The central bank is now a private business

A company can only produce a prestige good from a building it owns, so three things
had to change on `building_bank`, and each was found the hard way:

| what | why |
|---|---|
| `ownership_type = no_ownership` → `self` | no ownership shares meant nothing to hold. Not enough on its own |
| `bg_bank: is_government_funded = yes` → `no` | a government-funded building is state-run and has no owners at all. This is the one that mattered |
| `ai_nationalization_desire = 0` → `-5` | 0 is exactly the engine's privatise threshold; a company can only hold privatised levels |

**This is a design decision, not a fix.** A private central bank pays its dividends
to its owners instead of the treasury — about 6K a month on a 1836 British save —
and the treasury no longer pays for its gold and paper either. If that is not
wanted, run the generator without `--private-bank` and drop the prestige currencies;
the goods ceiling is closed either way.

### The company that owns it always exists

Every country with a central bank gets a bank company, keeps it, and does not pay a
company slot for it:

* **spawned** monthly and once at game start — a country that owns a central bank
  and holds no bank company is given `company_BasicBank`;
* **free** — a country modifier with `country_max_companies_add = 1` while the
  central bank stands. E&F's own +1 sat inside `prosperity_modifier`, so it only
  ever reached a prosperous generic company;
* **undeletable** — no such flag exists in the engine, so it is imitated: delete it
  and the monthly pass puts it back;
* **replaced by the flavoured one** where E&F has it. It cannot be picked for the
  country, so the generic one is granted and withdraws itself the moment any of
  E&F's 96 flavoured bank companies appears.

### A rule worth writing down

`REPLACE:key = { ... }` is a **complete definition of the entry. Everything not
listed disappears.** The difference from `INJECT:` is not "list versus block", it is
"replace everything versus append".

Proved twice, both times by breakage: `REPLACE:building_bank = { ownership_type =
self }` made the central bank vanish from the game, and 285 production methods
restated with only `building_modifiers` lost their `unlocking_laws` — the central
bank started offering all 95 currencies in a dropdown meant to show one.

So everything here that changes one field in an E&F entry restates the whole entry,
taken from E&F by the generator rather than copied by hand.

