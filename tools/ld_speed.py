"""Скорость прогона: секунды реального времени на игровой месяц (ФК2, оптимизация).

    python tools/ld_speed.py <прогон> [<прогон> ...] [--from 1836.3] [--out <файл>]

Точки — строки `debug*.log` (и `dbgparts/`) с реальным временем `[ЧЧ:ММ:СС]` и игровой датой «мая 5, 1837» в тексте:
ванильные строки `00_code_on_actions` (партии, выборы — есть и без мода) и строки логов мода `EF?|<дата>|…`. По
каждому прогону: точек, первая и последняя игровая дата, наклон (МНК) — секунд на 30 игровых дней, всего и по
кварталам (видно, дорожает ли игра со временем). `--from` отбрасывает начало (первые недели — загрузка, первые пульсы).
Ничего не меняет.
"""
import argparse
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ld_logcats import HEAD, files  # noqa: E402

MONTHS = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8,
          "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12,
          "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
          "September": 9, "October": 10, "November": 11, "December": 12}
DATE = re.compile(r"(?:^|[|:]\s?)(" + "|".join(MONTHS) + r") (\d{1,2}), (\d{4})")
TIME = re.compile(r"^\[(\d\d):(\d\d):(\d\d)\]")


def points(run):
    out, prev, day = [], None, 0
    for p in files(run, "debug"):
        with open(p, encoding="utf-8", errors="replace") as f:
            for line in f:
                t = TIME.match(line)
                if not t or not HEAD.match(line):
                    continue
                d = DATE.search(line)
                if not d:
                    continue
                sec = int(t[1]) * 3600 + int(t[2]) * 60 + int(t[3])
                if prev is not None and sec + day < prev - 3600:  # полночь
                    day += 86400
                sec += day
                prev = sec
                g = date(int(d[3]), MONTHS[d[1]], int(d[2])).toordinal()
                out.append((g, sec))
    return out


def slope(pts):
    n = len(pts)
    if n < 3:
        return None
    mx = sum(g for g, _ in pts) / n
    my = sum(s for _, s in pts) / n
    sxx = sum((g - mx) ** 2 for g, _ in pts)
    if sxx == 0:
        return None
    return sum((g - mx) * (s - my) for g, s in pts) / sxx * 30


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--from", dest="start", default="1836.2")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.out:
        sys.stdout = open(a.out, "w", encoding="utf-8")
    y, m = (int(x) for x in a.start.split(".")[:2])
    g0 = date(y, m, 1).toordinal()
    for run in a.runs:
        pts = sorted(p for p in points(run) if p[0] >= g0)
        name = os.path.basename(os.path.normpath(run))
        if len(pts) < 3:
            print(f"{name}: точек {len(pts)} — мало")
            continue
        s = slope(pts)
        d1, d2 = date.fromordinal(pts[0][0]), date.fromordinal(pts[-1][0])
        print(f"{name}: точек {len(pts)}, {d1} … {d2}; {s:.2f} с на игровой месяц")
        q0 = pts[0][0]
        while q0 < pts[-1][0]:
            q = [p for p in pts if q0 <= p[0] < q0 + 91]
            qs = slope(q)
            if qs is not None and len(q) >= 5:
                print(f"    {date.fromordinal(q0)}: {qs:.2f} с/мес ({len(q)} точек)")
            q0 += 91


if __name__ == "__main__":
    main()
