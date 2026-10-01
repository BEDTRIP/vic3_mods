"""EF.48, block В night 2 (2.10.2026): the morning report page.

Usage: py tools/ef48_report/build_night2_report.py <run.json> <out.html> [label]
<run.json> comes from tools/parse_eflog.py. The texts (what was done, decisions) are in
night2_meta.json next to this script. Charts per country: money M0-M3 to GDP, inflation from prices,
metal cover and the currency's value against its parity, the key and the government's rate,
the trade balance in money.
"""
import json, os, sys

SCR = os.path.dirname(os.path.abspath(__file__))
COUNTRIES = ["Великобритания", "Франция", "Россия", "Северо-Американские Соединённые Штаты", "Австрия", "Пруссия"]
SHORT = {"Северо-Американские Соединённые Штаты": "США"}


def series(run):
    out = {}
    for c in COUNTRIES:
        d = run.get(c)
        if not d:
            continue
        w = d.get("EFW", [])
        r = {x["date"]: x for x in d.get("EFR", [])}
        rows = []
        for i, x in enumerate(w):
            if i % 4:  # every 4th week
                continue
            gdp = x.get("gdp") or 0
            if gdp <= 0:
                continue
            rr = r.get(x["date"], {})
            rows.append({
                "d": x["date"],
                "m0": x.get("m0", 0) / gdp, "m1": x.get("m1", 0) / gdp,
                "m2": x.get("m2", 0) / gdp, "m3": x.get("m3", 0) / gdp,
                "tr": (x.get("trea") or 0) / gdp,
                "infl": x.get("infl"),
                "cover": x.get("cover"),
                "val": (x.get("mv0") or 0) / (x.get("target1") or 1) if x.get("target1") else None,
                "rate": x.get("rate"),
                "grt": rr.get("grt"),
                "trade": (rr.get("trade") or 0) * 52 / gdp if "trade" in rr else None,
                "gdp": gdp / 1e6,
            })
        out[SHORT.get(c, c)] = rows
    return out


def main():
    run = json.load(open(sys.argv[1], encoding="utf-8"))
    label = sys.argv[3] if len(sys.argv) > 3 else ""
    meta = json.load(open(os.path.join(SCR, "night2_meta.json"), encoding="utf-8"))
    meta["run"] = label
    tpl = open(os.path.join(SCR, "night2_template.html"), encoding="utf-8").read()
    html = (tpl.replace("/*__DATA__*/null", json.dumps(series(run), ensure_ascii=False))
               .replace("/*__META__*/null", json.dumps(meta, ensure_ascii=False)))
    open(sys.argv[2], "w", encoding="utf-8").write(html)
    print("ok", len(html))


if __name__ == "__main__":
    main()
