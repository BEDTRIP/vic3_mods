"""R2 и R3, закрытие (8.10.2026): проверки прогона по логам.

    py tools/ld_r23_checks.py <прогон> [--countries Великобритания,США,...]

- капитал банков на первом шаге страны (`EFJ`, первая строка страны): сколько стран с capital < 0 и какие;
- металл на старте (`EFM|…|metal_start`): строки стран из списка В4 (Ганновер, Финляндия, обе Канады, Саксония);
- выкуп уровней движком (`EFJ` lvl_pool / lvl_tr) и «прочее» (other, other_pool, other_tr) — первая и последняя
  строка по странам из --countries;
- мир (`EFJ|…|WORLD`): медиана и первая неделя изменения «прочего»;
- R3.6 — ошибки `money_value_target_pre_set` («Value of wrong type», строки 01_economic_scripted_effects.txt:112xx);
- R3.5 — «not permitted to retain law»: число, по законам, примеры;
- R3.7 — `EFM|…|cur_reform`, события `ld_currency_formed`;
- ошибки с местом в файлах `ld_*` (error.log).
Ничего не меняет.
"""
import argparse
import os
import re
import sys
from collections import Counter, defaultdict
from statistics import median

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ld_logcats import files  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
V4 = ("Ганновер", "Финляндия", "Нижняя Канада", "Верхняя Канада", "Саксония")


def kv(parts):
    out = {}
    for p in parts:
        if " " in p:
            k, v = p.split(" ", 1)
            try:
                out[k] = float(v.replace(",", ""))
            except ValueError:
                out[k] = v
    return out


def lines(run, kind):
    for p in files(run, kind):
        with open(p, encoding="utf-8", errors="replace") as f:
            yield from f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--countries", default="Великобритания,США,Россия,Франция,Швейцария")
    a = ap.parse_args()
    watch = a.countries.split(",")

    efj, world, ms, reform, efv = defaultdict(list), [], [], [], []
    for line in lines(a.run, "debug"):
        i = line.find("EF")
        if i < 0 or line[i + 3:i + 4] != "|":
            continue
        parts = line[i:].rstrip("\n").split("|")
        tag = parts[0]
        if tag == "EFJ" and len(parts) > 3:
            if parts[2] == "WORLD":
                world.append((parts[1], kv(parts[3:])))
            else:
                efj[parts[2]].append((parts[1], kv(parts[3:])))
        elif tag == "EFM" and len(parts) > 3 and parts[3] == "metal_start":
            ms.append(line[i:].strip())
        elif tag == "EFM" and len(parts) > 3 and parts[3] == "cur_reform":
            reform.append(line[i:].strip())
        elif tag == "EFV":
            efv.append(line[i:].strip())

    print(f"== EFJ: стран {len(efj)}")
    neg = [(c, r[0][1].get("capital")) for c, r in efj.items()
           if isinstance(r[0][1].get("capital"), float) and r[0][1]["capital"] < 0]
    print(f"капитал < 0 на первом шаге: {len(neg)}", neg[:20])
    for c in watch:
        r = efj.get(c)
        if not r:
            print(f"{c}: нет строк")
            continue
        f, l = r[0], r[-1]
        keys = ("other", "other_pool", "other_tr", "lvl_pool", "lvl_tr", "capital", "pool")
        print(f"{c}: {f[0]} → {l[0]} | " + " | ".join(f"{k} {l[1].get(k)}" for k in keys))
    lvl = sorted(((c, r[-1][1].get("lvl_pool") or 0, r[-1][1].get("lvl_tr") or 0) for c, r in efj.items()),
                 key=lambda x: x[1])
    print("выкуп уровней, пул (накопл.) — топ-8:", [(c, round(p), round(t)) for c, p, t in lvl[:8]])
    print("            по миру: пул", round(sum(x[1] for x in lvl)), "казна", round(sum(x[2] for x in lvl)))
    oth = sorted(((c, r[-1][1].get("other") or 0) for c, r in efj.items()), key=lambda x: x[1])
    print("«прочее» (накопл.) — худшие 8:", [(c, round(v)) for c, v in oth[:8]])

    if world:
        w = [x[1].get("other") or 0 for x in world]
        print(f"== WORLD: недель {len(w)}, первая {w[0]:.0f}, медиана {median(w):.0f}, медиана без первой "
              f"{median(w[1:]) if len(w) > 1 else 0:.0f}")

    print(f"== metal_start: строк {len(ms)}")
    for s in ms:
        if any(c in s for c in V4):
            print("  ", s[:400])

    print(f"== R3.7 cur_reform: {len(reform)}")
    for s in reform[:10]:
        print("  ", s[:300])
    print(f"== EFV: {len(efv)}")
    for s in efv[:12]:
        print("  ", s[:260])

    err = Counter()
    r36, perm, permlaw, ld = 0, 0, Counter(), Counter()
    for kind in ("error", "debug", "game"):
        for line in lines(a.run, kind):
            if "not permitted to retain law" in line or "not permitted" in line and "law" in line:
                perm += 1
                m = re.search(r"law_\w+", line)
                permlaw[m.group(0) if m else line[30:120]] += 1
            if kind != "error":
                continue
            if "01_economic_scripted_effects.txt:112" in line and "wrong type" in line:
                r36 += 1
            m = re.search(r"(common|events|gui)/[^\s:]*/?ld_[\w.]+:\d+", line)
            if m:
                ld[m.group(0)] += 1
    print(f"== R3.6 (wrong type в money_value_target_pre_set): {r36}")
    print(f"== R3.5 not permitted: {perm}; по законам:", permlaw.most_common(15))
    print(f"== ошибки с местом в ld_*: {sum(ld.values())}", ld.most_common(15))


if __name__ == "__main__":
    main()
