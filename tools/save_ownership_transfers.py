"""Levels that changed owner without the building changing size: who sells to whom between saves (В1.2, 3.10).

Usage:  py tools/save_ownership_transfers.py [--price N] [--buyer TAG] <save1> <save2> [...]   (oldest first; names inside 'save games' are fine)

The engine's company privatization: companies (and foreign owners) buy levels from manors, financial districts,
the state at the privatization price -- PRIVATIZATION_PER_LEVEL_COST x the level's construction points (at least
MIN_FAKE_CONSTRUCTION_COST 100), paid from the buyer's investment pool: 15 000 a level with VC (150 x 100); vanilla 250
-- 25 000 and more, 50 000 for a 200-point building (8.10: the Ledgerdemain playset has no VC). --price N (default 15000)
is only the estimate's price per level. Per pair of saves: levels lost and gained
by owner class (classes as in save_ownership.py), world and the top countries by levels sold. --buyer TAG adds every
sale whose buyer (owner building: company HQ / regional office / manor / financial district) sits in TAG -- the pool
that paid: building, its country, type, levels, seller class.
"""
import sys, collections
import save_ownership as so


def per_building(d, banks):
    r = collections.defaultdict(collections.Counter)
    for (k, o, bid), lv in d['own'].items():
        c, cl = so.classify(d, k, o, bid, banks)
        if c:
            r[bid][cl] += lv
    return r


def buyer_rows(a, b, tag, banks):
    # per building: owners that gained levels while the building kept its size, the buyer's country = its owner building's
    rows = []
    sa, sb = collections.Counter(), collections.Counter()
    for (k, o, bid), lv in a['own'].items(): sa[bid] += lv
    for (k, o, bid), lv in b['own'].items(): sb[bid] += lv
    for (k, o, bid), lv in b['own'].items():
        if k != 'building' or sa.get(bid) != sb.get(bid):
            continue
        dl = lv - a['own'].get((k, o, bid), 0)
        ob = b['bld'].get(o)
        if dl <= 0 or not ob or b['tag'].get(ob[1], ob[1]) != tag:
            continue
        bd = b['bld'].get(bid)
        if not bd:
            continue
        sold = collections.Counter()
        for (k2, o2, b2), lv2 in a['own'].items():
            if b2 == bid:
                d2 = b['own'].get((k2, o2, b2), 0) - lv2
                if d2 < 0:
                    sold[so.classify(a, k2, o2, b2, banks)[1]] -= d2
        rows.append((b['tag'].get(bd[1], bd[1]), bd[0], dl, ob[0], dict(sold)))
    return rows


def main():
    args = sys.argv[1:]
    price = 15000
    buyer = None
    if args and args[0] == "--price":
        price = int(args[1]); args = args[2:]
    if args and args[0] == "--buyer":
        buyer = args[1]; args = args[2:]
    banks = so.bank_companies()
    saves = [so.parse(p) for p in args]
    for a, b in zip(saves, saves[1:]):
        A, B = per_building(a, banks), per_building(b, banks)
        lose, gain = collections.Counter(), collections.Counter()
        by = collections.defaultdict(collections.Counter)
        for bid in set(A) & set(B):
            if sum(A[bid].values()) != sum(B[bid].values()):
                continue  # built or demolished: not a sale
            for cl in set(A[bid]) | set(B[bid]):
                dl = B[bid][cl] - A[bid][cl]
                if dl < 0:
                    lose[cl] -= dl
                    by[b['tag'].get(b['bld'][bid][1], b['bld'][bid][1])][cl] -= dl
                elif dl > 0:
                    gain[cl] += dl
        print(f"{a['date']} -> {b['date']}: sold {sum(lose.values())} levels "
              f"(~{sum(lose.values()) * price / 1e6:.1f}M at {price})")
        print('  sold by  ', dict(lose.most_common()))
        print('  bought by', dict(gain.most_common()))
        for c, v in sorted(by.items(), key=lambda x: -sum(x[1].values()))[:10]:
            print(f'    {c:5} {dict(v.most_common())}')
        if buyer:
            for r in buyer_rows(a, b, buyer, banks):
                print(f'  {buyer} bought: {r[0]:5} {r[1]} +{r[2]} by {r[3]} from {r[4]}')


if __name__ == '__main__':
    main()
