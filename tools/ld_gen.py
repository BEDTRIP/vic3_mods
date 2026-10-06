"""Общий вывод генераторов в форк «E&F: Ledgerdemain» (ФК5, Д.7).

Генератор строит текст файла, как раньше для хотфикса, и отдаёт его сюда — `emit(путь_хотфикса, текст)`. Путь
переводится в путь форка (`zz_ef_X` → `ld_X`, `zz_pb_ef_X` → `ld_pb_X`, папка `_ef/ef hotfix 1.13/` → корень форка), а
текст делится на записи и вписывается **по ключам** в существующий файл форка:

- запись есть в файле форка — заменяется на месте (в режиме `--check` только сравнивается, `ld_pdx.norm`);
- записи в файле форка нет — она влита в тело E&F руками (ФК1) или удалена; генератор её больше не ведёт:
  пропускается и попадает в отчёт `absent`;
- записи файла форка, которых генератор не выдал, не трогаются (рукописные);
- GUI-файл (`*.gui`) — целиком: файл генератора (`gui/ld_cb_rate_panel.gui`) рукописных записей не держит.

Локализация (`*.yml`) — так же по ключам строк `ключ:N "…"`; пишутся только английский и русский, девять остальных
языков — копия английского (`ld_loc_langs.py`, запускать после генераторов, которые меняют английский).

Итог генератора — `report()`: что совпало, что изменено, чего в форке нет. Код выхода `--check` — 1 при расхождениях.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_pdx  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FORK = os.path.normpath(os.path.join(HERE, "..", "..", "Economic-and-Financial-Ledgerdemain-Mod"))
HOTFIX_DIR = "ef hotfix 1.13"
LANGS_WRITTEN = ("english", "russian")
LOC_LINE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\d*\s*"', re.M)

CHECK = "--check" in sys.argv
_stats = {"same": [], "changed": [], "absent": [], "no_file": [], "skipped_lang": []}


def fork_rel(path):
    """Путь хотфикса (абсолютный или относительный) → относительный путь в форке."""
    p = path.replace("\\", "/")
    if HOTFIX_DIR in p:
        p = p.split(HOTFIX_DIR + "/", 1)[1]
    d, f = os.path.split(p)
    f = re.sub(r"^zz_pb_ef_", "ld_pb_", f)
    f = re.sub(r"^zz_ef_", "ld_", f)
    f = re.sub(r"^00_00_ef_", "ld_", f)
    return (d + "/" + f) if d else f


def _lang(rel):
    m = re.search(r"_l_([a-z_]+)\.yml$", rel)
    return m.group(1) if m else None


def _loc_entries(text):
    """{ключ: (start, end)} — строки локализации целиком (без перевода строки)."""
    out = {}
    for m in LOC_LINE.finditer(text):
        ls = text.rfind("\n", 0, m.start()) + 1
        le = text.find("\n", m.start())
        out[m.group(1)] = (ls, le if le >= 0 else len(text))
    return out


def _norm_loc(line):
    return line.strip()


def emit(path, text):
    """Вписать вывод генератора (текст файла хотфикса `path`) в файл форка по ключам записей."""
    rel = fork_rel(path)
    lang = _lang(rel)
    if lang and lang not in LANGS_WRITTEN:
        _stats["skipped_lang"].append(rel)
        return
    dst = os.path.join(FORK, rel)
    if not os.path.exists(dst):
        _stats["no_file"].append(rel)
        return
    src, bom, eol = ld_pdx.read(dst)
    gen = text.replace("\r\n", "\n").lstrip("﻿")
    if rel.endswith(".gui"):
        # GUI-файл генератора — целиком (`types X { … }` по записям не делится; ФК2, 7.10)
        k = "<файл>"
        if ld_pdx.norm(src) == ld_pdx.norm(gen):
            _stats["same"].append(f"{rel} | {k}")
        else:
            _stats["changed"].append(f"{rel} | {k}")
            if not CHECK:
                ld_pdx.write(dst, gen, bom=bom, eol=eol)
        return
    if lang:
        have, want = _loc_entries(src), _loc_entries(gen)
        pieces = {k: gen[s:e] for k, (s, e) in want.items()}
        cur = {k: src[s:e] for k, (s, e) in have.items()}
        same = lambda k: _norm_loc(cur[k]) == _norm_loc(pieces[k])  # noqa: E731
        spans = have
    else:
        hents, _ = ld_pdx.parse(src)
        gents, probs = ld_pdx.parse(gen)
        if probs:
            raise SystemExit(f"{rel}: вывод генератора не разбирается: {probs[:3]}")
        spans = {e.key: (e.start, e.end) for e in hents}
        cur = {e.key: e.text(src) for e in hents}
        pieces = {e.key: e.text(gen) for e in gents}
        same = lambda k: ld_pdx.norm(cur[k]) == ld_pdx.norm(pieces[k])  # noqa: E731
    repl = []
    for k, piece in pieces.items():
        if k not in spans:
            _stats["absent"].append(f"{rel} | {k}")
        elif same(k):
            _stats["same"].append(f"{rel} | {k}")
        else:
            _stats["changed"].append(f"{rel} | {k}")
            repl.append((spans[k], piece))
    if repl and not CHECK:
        for (s, e), piece in sorted(repl, reverse=True):
            src = src[:s] + piece + src[e:]
        ld_pdx.write(dst, src, bom=bom, eol=eol)


def report(name=""):
    s = _stats
    print(f"{name}: совпало {len(s['same'])}, {'расходится' if CHECK else 'изменено'} {len(s['changed'])}, "
          f"нет в форке {len(s['absent'])}, нет файла {len(s['no_file'])}, языки по копии {len(s['skipped_lang'])}")
    for k in ("changed", "absent", "no_file"):
        for x in s[k][:40]:
            print(f"  {k}: {x}")
        if len(s[k]) > 40:
            print(f"  {k}: … ещё {len(s[k]) - 40}")
    if CHECK and (s["changed"] or s["no_file"]):
        sys.exit(1)
