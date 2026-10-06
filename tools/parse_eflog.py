"""EF.48 sandbox runs: eflog.txt (EFW/EFR lines of the weekly money model) -> JSON.

Usage: py tools/parse_eflog.py <run>/eflog.txt [more eflog.txt ...] <out.json>
Output: {country: {"EFW": [{"date": "1837-01-05", key: value, ...}], "EFR": [...], "EFX": [...], "EFC": [...]}}
(EFX: the monthly currency line of every country; EFC: a currency-crisis redemption, night 2;
EFS: consols, Д2.7б -- debt, sale, interest, buy-back; EFL: listed companies and capitalization, Д2.10-Д2.11, monthly;
EFT: the metal accounts of a country, weekly; EFV: the world line of metal (WORLD), weekly -- stage 2, night 6.10).
Dates are written by the game in Russian month names (the user's language).
"""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
MON = {"января":1,"февраля":2,"марта":3,"апреля":4,"мая":5,"июня":6,"июля":7,"августа":8,"сентября":9,"октября":10,"ноября":11,"декабря":12,
       "January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
def date(s):
    m = re.match(r"(\w+) (\d+), (\d+)", s.strip())
    if not m: return s
    return f"{int(m.group(3)):04d}-{MON.get(m.group(1),0):02d}-{int(m.group(2)):02d}"
def num(v):
    v = v.replace(",", "").replace(" ", "")
    try: return float(v)
    except: return None
out = {}
for path in sys.argv[1:-1]:
    for line in open(path, encoding="utf-8-sig", errors="replace"):
        parts = line.strip().split("|")
        if len(parts) < 4 or parts[0] not in ("EFW", "EFR", "EFX", "EFC", "EFM", "EFJ", "EFO", "EFF", "EFD", "EFS", "EFK", "EFA", "EFP", "EFG", "EFB", "EFL", "EFT", "EFV"): continue
        rec = {"date": date(parts[1])}
        for p in parts[3:]:
            if " " in p:
                k, v = p.split(" ", 1); rec[k] = num(v)
            else:
                rec["tag"] = p
        out.setdefault(parts[2], {}).setdefault(parts[0], []).append(rec)
json.dump(out, open(sys.argv[-1], "w", encoding="utf-8"), ensure_ascii=False)
for c, d in out.items():
    print(c, {k: len(v) for k, v in d.items()})
