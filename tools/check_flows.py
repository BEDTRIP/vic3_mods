"""Stage 1 (5.10, В1.6): do the money model's flows with the world add up?  eflog.txt of a run -> a monthly table.

The user's goal for stage 1: every operation converges -- between the accounts and between the countries; money and
metal neither appear nor vanish. This reads the money model's log lines (tools/run_vic3_sandbox.ps1 -> eflog.txt):

  EFR (weekly; 5.10 -- only the ~9 countries the model logs, not the whole world: the sums below are theirs, a
      world check needs a world line from the model -- stage 1, В1.6): ext_net -- the week's net flow with the rest of the world, hume -- metal through the
      clearing (money at parity), trade -- the market's trade balance, div -- dividends from abroad, gmined -- metal
      mined; summed per calendar month and country;
  EFG (В1.6, 5.10; weekly, the WHOLE world, in gold): in / out -- the net inflows / outflows with abroad of all
      countries; nocl -- |flow| of the countries outside the clearing (no CB); subj_in / subj_out -- the subjects' part;
      hume / hume_abs -- the CBs' metal moved by the clearing, signed sum and |sum|; n / n0 -- countries / with no value;
      clr_in / clr_out / clr_pot -- the clearing's last window;
  EFX (monthly, every country): gold / silver -- the central bank's metal (E&F's own scale), fxm -- foreign currency
      in the reserves (in metal), liab -- our currency held abroad; clr_in / clr_out / clr_pay / clr_pot -- the world
      clearing of the last window (the same numbers in every country's line).

Printed per month:
  world   sum(ext_net) / sum|ext_net| -- the share of the flows with no counterpart (0 = every payment has a payer);
          sum(hume) -- metal sent minus metal received through the clearing (0 = metal conserved), sum(trade);
  metal   world gold, silver (in gold), fx reserves; the change against last month and against mining; when it jumps
          without mining, the countries that made the jump (В2.4: E&F's "metal from nowhere");
  clear   the clearing window: inflows, outflows, the share paid, what lies in the pot.
Flags (>> at the line's start) when the share without a counterpart is over --tol (default 0.05) or the world metal moves
by more than --metal-tol (default 0.01) of itself beyond the month's mining.

Usage:  py tools/check_flows.py <run>/eflog.txt [more eflog.txt ...] [--tol 0.05] [--metal-tol 0.01] [--json out.json]
        (through the PC bridge: py_tool("check_flows", ["runs/<id>/eflog.txt"]))
"""
import json, re, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
MON = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8,
       "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12,
       "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
       "September": 9, "October": 10, "November": 11, "December": 12}


def month_of(s):
    m = re.match(r"(\w+) (\d+), (\d+)", s.strip())
    return f"{int(m.group(3)):04d}-{MON.get(m.group(1), 0):02d}" if m else None


def num(v):
    try:
        return float(v.replace(",", "").replace(" ", ""))
    except ValueError:
        return None


def read(paths):
    efr = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))   # month -> country -> key -> sum
    efx = defaultdict(dict)                                              # month -> country -> last EFX record
    efg = defaultdict(lambda: defaultdict(float))                        # month -> key -> sum of the weeks
    seen = set()
    for path in paths:
        for line in open(path, encoding="utf-8-sig", errors="replace"):
            parts = line.strip().split("|")
            if len(parts) < 4 or parts[0] not in ("EFR", "EFX", "EFG"):
                continue
            key = (parts[0], parts[1], parts[2])          # a line repeated in two eflogs (or parts) counts once
            if key in seen:
                continue
            seen.add(key)
            mon = month_of(parts[1])
            if not mon:
                continue
            rec = {}
            for p in parts[3:]:
                if " " in p:
                    k, v = p.split(" ", 1)
                    rec[k] = num(v)
            if parts[0] == "EFG":
                g = efg[mon]
                for k, v in rec.items():
                    if v is not None and k not in ("clr_pot", "n", "n0"):
                        g[k] += v
                for k in ("clr_pot", "n", "n0"):
                    if rec.get(k) is not None:
                        g[k] = rec[k]
                g["weeks"] += 1
            elif parts[0] == "EFR":
                acc = efr[mon][parts[2]]
                for k in ("ext_net", "hume", "trade", "div", "gmined", "ext"):
                    if rec.get(k) is not None:
                        acc[k] += rec[k]
                acc["weeks"] += 1
            else:
                efx[mon][parts[2]] = rec
    return efr, efx, efg


def world_table(efg, tol):
    """В1.6: the EFG lines -- the whole world's flows with abroad, in gold, summed by month."""
    if not efg:
        print("\nno EFG lines (the world line, В1.6) -- a run before 5.10")
        return [], 0
    print(f"\nWORLD (EFG, gold): {'month':8} {'wk':>3} {'in':>12} {'out':>12} {'in-out':>12} {'share':>7} {'nocl':>11} "
          f"{'subj in':>11} {'subj out':>11} {'hume':>10} {'|hume|':>10} {'n':>4} {'n0':>4}")
    out, flags = [], 0
    for mon in sorted(efg):
        g = efg[mon]
        gin, gout = g.get("in", 0.0), g.get("out", 0.0)
        share = (gin - gout) / (gin + gout) if gin + gout else 0.0
        flag = abs(share) > tol
        flags += flag
        print(f"{'>>' if flag else '  '}                 {mon:8} {g['weeks']:>3.0f} {gin:>12,.0f} {gout:>12,.0f} "
              f"{gin - gout:>12,.0f} {share:>7.3f} {g.get('nocl', 0):>11,.0f} {g.get('subj_in', 0):>11,.0f} "
              f"{g.get('subj_out', 0):>11,.0f} {g.get('hume', 0):>10,.0f} {g.get('hume_abs', 0):>10,.0f} "
              f"{g.get('n', 0):>4.0f} {g.get('n0', 0):>4.0f}")
        out.append({"month": mon, **g, "share": share, "flag": flag})
    return out, flags


def main():
    args = sys.argv[1:]
    tol, mtol, jout = 0.05, 0.01, None
    paths = []
    i = 0
    while i < len(args):
        if args[i] == "--tol":
            tol = float(args[i + 1]); i += 2
        elif args[i] == "--metal-tol":
            mtol = float(args[i + 1]); i += 2
        elif args[i] == "--json":
            jout = args[i + 1]; i += 2
        else:
            paths.append(args[i]); i += 1
    if not paths:
        print(__doc__)
        sys.exit(1)
    efr, efx, efg = read(paths)
    months = sorted(set(efr) | set(efx))
    out = []
    prev = None
    flags = 0
    print(f"{'month':8} {'n':>4} {'sum ext_net':>13} {'gross':>13} {'share':>7} {'sum hume':>12} {'sum trade':>13} | "
          f"{'world gold':>14} {'d gold':>12} {'silver(g)':>14} {'d silver':>12} {'fx':>12} | clearing in / out / paid / pot")
    for mon in months:
        rows = efr.get(mon, {})
        s_ext = sum(r["ext_net"] for r in rows.values())
        gross = sum(abs(r["ext_net"]) for r in rows.values())
        s_hume = sum(r["hume"] for r in rows.values())
        s_trade = sum(r["trade"] for r in rows.values())
        mined = sum(r["gmined"] for r in rows.values())
        share = s_ext / gross if gross else 0.0
        xs = efx.get(mon, {})
        gold = sum((x.get("gold") or 0) for x in xs.values())
        silv = sum((x.get("silver") or 0) * (x.get("s2g") or 0) for x in xs.values())
        fx = sum((x.get("fxm") or 0) for x in xs.values())
        any_x = next(iter(xs.values()), {})
        clr = (any_x.get("clr_in"), any_x.get("clr_out"), any_x.get("clr_pay"), any_x.get("clr_pot"))
        d_gold = d_silv = None
        movers = []
        flag = abs(share) > tol
        if not xs:
            gold = silv = fx = None                     # no monthly line (the run's last, cut month): not compared
        if prev and xs:
            d_gold = gold - prev["gold"]
            d_silv = silv - prev["silver"]
            base = max(prev["gold"] + prev["silver"], 1.0)
            # world metal should move only by mining (and the countries that appear or vanish); the first month after
            # the start holds the one-time rescale of the metal to 40% cover (M.1) -- not flagged
            if abs(d_gold + d_silv - mined) > mtol * base and prev.get("n", 0) > 0 and not prev.get("first"):
                flag = True
                for c, x in xs.items():
                    px = prev["by"].get(c)
                    if px is None:
                        continue
                    d = ((x.get("gold") or 0) - px[0]) + ((x.get("silver") or 0) * (x.get("s2g") or 0) - px[1])
                    movers.append((abs(d), c, d))
                movers = [(c, round(d)) for _, c, d in sorted(movers, reverse=True)[:5]]
        flags += flag
        fmt = lambda v: "" if v is None else f"{v:,.0f}"
        print(f"{'>>' if flag else '  '}{mon:6} {len(rows):>4} {s_ext:>13,.0f} {gross:>13,.0f} {share:>7.3f} {s_hume:>12,.0f} "
              f"{s_trade:>13,.0f} | {fmt(gold):>14} {fmt(d_gold):>12} {fmt(silv):>14} {fmt(d_silv):>12} {fmt(fx):>12} | "
              + " / ".join(fmt(v) if k != 2 else ("" if v is None else f"{v:.3f}") for k, v in enumerate(clr)))
        if movers:
            print("          metal moved by: " + ", ".join(f"{c} {d:+,}" for c, d in movers))
        out.append({"month": mon, "countries": len(rows), "sum_ext_net": s_ext, "gross": gross, "share": share,
                    "sum_hume": s_hume, "sum_trade": s_trade, "mined": mined, "gold": gold, "silver_gold": silv,
                    "d_gold": d_gold, "d_silver": d_silv, "fx": fx, "clearing": clr, "flag": flag, "movers": movers})
        if xs:
            prev = {"gold": gold, "silver": silv, "n": len(xs), "first": prev is None,
                    "by": {c: ((x.get("gold") or 0), (x.get("silver") or 0) * (x.get("s2g") or 0)) for c, x in xs.items()}}
    world, wflags = world_table(efg, tol)
    print(f"\n{len(months)} months, {flags} flagged, {wflags} world months flagged (share without a counterpart > {tol}, or world metal off mining by > {mtol})")
    if jout:
        json.dump({"countries": out, "world": world}, open(jout, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
