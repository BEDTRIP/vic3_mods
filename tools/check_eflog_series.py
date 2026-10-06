"""A few keys of the money model's log as monthly series (stage 2, night 6.10): eflog.txt -> a small table.

Usage:  py tools/check_eflog_series.py <run>/eflog.txt <LINE> <country|*> key [key ...] [--every N] [--sum]
  LINE     EFW, EFR, EFT, EFV, EFM ...;  country: the name as in the log (Великобритания), '*' = all of them
           (one row per country, the last month only)
  --every  print every N-th line instead of the last line of each month (N weeks)
  --sum    sum the keys over the month instead of the last value (flows)
Through the PC bridge: py_tool("check_eflog_series", ["runs/<id>/eflog.txt", "EFW", "Великобритания", "cover", "m2"]).
"""
import re
import sys
from collections import OrderedDict

sys.stdout.reconfigure(encoding="utf-8")
MON = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8,
       "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12}


def ymd(s):
    m = re.match(r"(\w+) (\d+), (\d+)", s.strip())
    return f"{int(m.group(3)):04d}-{MON.get(m.group(1), 0):02d}-{int(m.group(2)):02d}" if m else s


def num(v):
    try:
        return float(v.replace(",", "").replace(" ", ""))
    except ValueError:
        return None


def main():
    a = sys.argv[1:]
    every, summ = None, False
    if "--every" in a:
        i = a.index("--every"); every = int(a[i + 1]); del a[i:i + 2]
    if "--sum" in a:
        a.remove("--sum"); summ = True
    path, line_tag, country, keys = a[0], a[1], a[2], a[3:]
    rows = []
    for line in open(path, encoding="utf-8-sig", errors="replace"):
        p = line.strip().split("|")
        if len(p) < 4 or p[0] != line_tag or (country != "*" and p[2] != country):
            continue
        rec = {}
        for x in p[3:]:
            if " " in x:
                k, v = x.split(" ", 1)
                rec[k] = num(v)
            else:
                rec["_"] = x
        rows.append((ymd(p[1]), p[2], rec))
    if country == "*":
        last = OrderedDict()
        for d, c, r in rows:
            last[c] = (d, r)
        print(f"{'country':28} {'date':10} " + " ".join(f"{k:>14}" for k in keys))
        for c, (d, r) in last.items():
            print(f"{c[:28]:28} {d:10} " + " ".join(f"{fmt(r.get(k)):>14}" for k in keys))
        return
    out = OrderedDict()
    for i, (d, c, r) in enumerate(rows):
        key = d if every else d[:7]
        if every and i % every:
            continue
        if summ and key in out:
            for k in keys:
                if r.get(k) is not None:
                    out[key][k] = (out[key].get(k) or 0) + r[k]
        else:
            out[key] = dict(r) if not summ else {k: r.get(k) for k in keys}
    print(f"{'date':10} " + " ".join(f"{k:>14}" for k in keys))
    for d, r in out.items():
        print(f"{d:10} " + " ".join(f"{fmt(r.get(k)):>14}" for k in keys))


def fmt(v):
    if v is None:
        return "-"
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:.4g}"


if __name__ == "__main__":
    main()
