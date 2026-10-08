"""Счёт смеллов кода форка «E&F: Ledgerdemain» (аудит до R8, 8.10.2026: `архив/2026-10-08 аудит смеллов кода.md`).

Разбирает весь скрипт форка (`common/`, `events/`, `.txt`) в дерево, строит граф вызовов по именам и считает «жару»
места — первую точку входа, из которой оно достижимо: неделя (`zz_ef_sched_step`), месяц, день планировщика,
полгода, год, пять лет, старт, история, окна (имена, которые читают `gui/` и английская локализация). Граф по именам —
жару чуть завышает (условный вызов считается безусловным).

    python tools/ld_smells.py [summary]                 # сводка — числа таблицы аудита
    python tools/ld_smells.py chains [--min 10]         # цепочки if / else_if, ряды if, switch, длинные OR
    python tools/ld_smells.py nest                      # перебор внутри перебора, мировые переборы в неделе / месяце
    python tools/ld_smells.py families                  # семейства имён «сущность × N», глобальные переменные
    python tools/ld_smells.py vars                      # переменные без читателя / читатели без писателя
    python tools/ld_smells.py dups [--min 20]           # одинаковые блоки (точно и с точностью до валюты / номера)
    python tools/ld_smells.py magic                     # числа в логике ld_* против именованных констант
    python tools/ld_smells.py headers                   # шапки «GENERATED» без живого генератора
    python tools/ld_smells.py occ '<regex>' [--files <regex>] [--defs] [--lines] [--top N]

Таблицы (`chains.tsv` и др.) — в `_tmp_analysis/ld_smells/`. Ничего в форке не меняет.
"""
import argparse
import collections
import hashlib
import os
import re
import sys

sys.setrecursionlimit(100000)
HERE = os.path.dirname(os.path.abspath(__file__))
FORK = os.path.normpath(os.path.join(HERE, "..", "..", "Economic-and-Financial-Ledgerdemain-Mod"))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "_tmp_analysis", "ld_smells"))
TOKEN = re.compile(r'#[^\n]*|"(?:[^"\\\n]|\\.)*"|[{}]|[<>!=?]=|[<>=]|[^\s{}<>!=?#"]+')
OPS = {"=", "?=", "<", ">", "<=", ">=", "!=", "=="}
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")
DEF_DIRS = {
    "common/scripted_effects": "effect", "common/scripted_triggers": "trigger", "common/script_values": "value",
    "common/on_actions": "on_action", "common/scripted_guis": "sgui", "common/scripted_buttons": "sbutton",
    "common/customizable_localization": "cloc",
}
HEAT_ROOTS = [
    ("week", ["zz_ef_sched_step"]),
    ("month", ["zz_ef_sched_monthly", "zz_ef_monthly_unscheduled", "on_monthly_pulse", "on_monthly_pulse_country",
               "ef_on_monthly_pulse_country", "zz_ef_roles_world_pass"]),
    ("day", ["zz_ef_sched_day", "zz_ef_sched_probe"]),
    ("halfyear", ["ef_on_half_yearly_pulse_country", "on_half_yearly_pulse_country"]),
    ("year", ["ef_on_yearly_pulse_country", "on_yearly_pulse_country", "central_bank_ef_on_yearly_pulse_country"]),
    ("5year", ["ef_on_five_year_pulse_country", "on_five_year_pulse_country", "ef_on_decade_pulse_country"]),
    ("start", ["on_game_started_after_lobby", "zz_ef_start_setup", "on_game_started"]),
]


# ---- разбор --------------------------------------------------------------------------------------------------

class Node:
    __slots__ = ("key", "op", "value", "kids", "line", "end_line")

    def __init__(self, key, op, value, line):
        self.key, self.op, self.value, self.line, self.end_line = key, op, value, line, line
        self.kids = None

    def walk(self, stack=()):
        yield self, stack
        if self.kids:
            st = stack + (self,)
            for k in self.kids:
                yield from k.walk(st)


def read(path):
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n")


def parse(text):
    """Дерево блока: корень — Node(None) с kids; голое слово в списке — Node(слово, None, None)."""
    toks, ln, last = [], 1, 0
    for m in TOKEN.finditer(text):
        s = m.group(0)
        if s.startswith("#"):
            continue
        ln += text.count("\n", last, m.start())
        last = m.start()
        toks.append((s, ln))
    root = Node(None, None, None, 0)
    root.kids = []
    stack = [root]
    i, n = 0, len(toks)
    while i < n:
        s, l = toks[i]
        cur = stack[-1]
        if s == "}":
            if len(stack) > 1:
                stack[-1].end_line = l
                stack.pop()
            i += 1
            continue
        if s == "{":
            nd = Node(None, None, None, l)
            nd.kids = []
            cur.kids.append(nd)
            stack.append(nd)
            i += 1
            continue
        if i + 2 < n and toks[i + 1][0] in OPS:
            op, v = toks[i + 1][0], toks[i + 2][0]
            if v == "{" or (i + 3 < n and toks[i + 3][0] == "{" and v in ("hsv", "rgb", "hsv360")):
                nd = Node(s, op, None if v == "{" else v, l)
                nd.kids = []
                cur.kids.append(nd)
                stack.append(nd)
                i += 3 if v == "{" else 4
                continue
            cur.kids.append(Node(s, op, v, l))
            i += 3
            continue
        cur.kids.append(Node(s, None, None, l))
        i += 1
    return root


def script_files(dirs=("common", "events"), exts=(".txt",)):
    for d in dirs:
        for dp, dn, fn in os.walk(os.path.join(FORK, d)):
            for f in sorted(fn):
                if f.endswith(exts):
                    yield os.path.relpath(os.path.join(dp, f), FORK).replace("\\", "/")


_TREES = None


def trees():
    global _TREES
    if _TREES is None:
        _TREES = {rel: parse(read(os.path.join(FORK, rel))) for rel in script_files()}
    return _TREES


# ---- граф вызовов и жара -----------------------------------------------------------------------------------

def words_of(node):
    out = set()
    for nd, _ in node.walk():
        for s in (nd.key, nd.value):
            if not s:
                continue
            for w in WORD.findall(s):
                out.add(w)
                if "." in w:
                    out.update(w.split("."))
            if ":" in s:
                out.update(s.split(":"))
    return out


_G = None


def graph():
    """{'defs': имя -> [(вид, файл, строка, конец)], 'edges': имя -> {имена}}."""
    global _G
    if _G is not None:
        return _G
    defs = collections.defaultdict(list)
    nodes = []
    for rel, root in trees().items():
        if rel.startswith("events/"):
            for nd in root.kids:
                if nd.key and nd.kids is not None and re.match(r"^\w+\.\d+$", nd.key):
                    defs[nd.key].append(("event", rel, nd.line, nd.end_line))
                    nodes.append((nd.key, nd))
            continue
        kind = next((k for d, k in DEF_DIRS.items() if rel.startswith(d)), None)
        if not kind:
            continue
        for nd in root.kids:
            if nd.key and nd.op:
                name = nd.key.split(":")[-1]
                defs[name].append((kind, rel, nd.line, nd.end_line))
                nodes.append((name, nd))
    names = set(defs)
    edges = collections.defaultdict(set)
    for name, nd in nodes:
        ws = words_of(nd) if nd.kids else set(WORD.findall(nd.value or ""))
        edges[name].update(w for w in ws if w in names and w != name)
    _G = {"defs": dict(defs), "edges": dict(edges)}
    return _G


def reach(roots):
    g, seen, st = graph(), set(), list(roots)
    while st:
        x = st.pop()
        if x in seen:
            continue
        seen.add(x)
        st.extend(g["edges"].get(x, ()))
    return seen


_HEATS = None
_GUIW = None
_OWN = None


def heats():
    global _HEATS
    if _HEATS is None:
        _HEATS = [(k, reach(r)) for k, r in HEAT_ROOTS]
    return _HEATS


def gui_reach():
    global _GUIW
    if _GUIW is None:
        w = set()
        for d in ("gui", "localization/english"):
            for dp, dn, fn in os.walk(os.path.join(FORK, d)):
                for f in fn:
                    if f.endswith((".gui", ".yml")):
                        w.update(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", read(os.path.join(dp, f))))
        _GUIW = reach([x for x in w if x in graph()["defs"]])
    return _GUIW


def heat(name, rel=""):
    if rel.startswith("common/history"):
        return "history"
    if name is None:
        return "-"
    for k, s in heats():
        if name in s:
            return k
    if rel.startswith(("common/scripted_guis", "common/scripted_buttons")) or name in gui_reach():
        return "gui"
    return "-"


def owner(rel, line):
    global _OWN
    if _OWN is None:
        _OWN = collections.defaultdict(list)
        for name, lst in graph()["defs"].items():
            for kind, r, l, e in lst:
                _OWN[r].append((l, e, name))
        for v in _OWN.values():
            v.sort()
    best = None
    for l, e, name in _OWN.get(rel, ()):
        if l > line:
            break
        if l <= line <= e:
            best = name
    return best


# ---- сущности: валюты, банки E&F, теги, номера --------------------------------------------------------------

def currencies():
    s = read(os.path.join(FORK, "common/laws/01_ef_currency_type.txt"))
    return sorted(set(re.findall(r"^law_(\w+?)_currency = \{", s, re.M)), key=len, reverse=True)


CURS = currencies()
CUR_RE = re.compile(r"(?<![a-z])(" + "|".join(CURS) + r")(?![a-z])")
BANKS = sorted(set(re.findall(r"stockpiling_\w+?_company_(\w+?)_fixe",
                              read(os.path.join(FORK, "common/history/global/00_ef_economic_global_variable.txt")))),
               key=len, reverse=True)
BANK_RE = re.compile(r"(?<![A-Za-z])(" + "|".join(map(re.escape, BANKS)) + r")(?![A-Za-z])") if BANKS else None


def template(w):
    t = CUR_RE.sub("<cur>", w)
    if BANK_RE:
        t = BANK_RE.sub("<bank>", t)
    t = re.sub(r"(?<=_)\d+(?=_|$)", "N", t)
    return re.sub(r"(?<=_)([A-Z]{3})(?=_|$)", "<TAG>", t)


def family_kind(t):
    return "<cur>" if "<cur>" in t else "<bank>" if "<bank>" in t else "<TAG>" if "<TAG>" in t else "N"


# ---- сканеры -------------------------------------------------------------------------------------------------

def disc(node):
    """Что проверяет ветка (по её limit / trigger)."""
    lim = next((k for k in node.kids or () if k.key in ("limit", "trigger")), None)
    if lim is None:
        return "?"
    s = " ".join(f"{n.key}{n.op or ''}{n.value or ''}" for n, _ in lim.walk() if n is not lim)
    if re.search(r"law_type:law_\w+_currency|has_law\s*=\s*law_\w+_currency", s):
        return "закон <cur>"
    if "flag:" in s:
        return "флаг <cur>" if CUR_RE.search(s) else "флаг"
    if re.search(r"c:[A-Z][A-Z0-9]{2}\b", s):
        return "тег"
    if "is_company_type" in s or "company_type:" in s:
        return "тип компании"
    if CUR_RE.search(s):
        return "имя с <cur>"
    if re.search(r"_\d+\b", s):
        return "номер _N"
    if "is_building_type" in s or "has_building" in s:
        return "здание"
    if "culture" in s or "heritage" in s:
        return "культура"
    return "прочее"


def scan_chains(minb=5):
    out = []
    for rel, root in trees().items():
        for nd, _ in root.walk():
            if not nd.kids or nd is root:
                continue
            kids, i = nd.kids, 0
            while i < len(kids):
                if kids[i].key in ("if", "trigger_if"):
                    j = i + 1
                    while j < len(kids) and kids[j].key in ("else_if", "trigger_else_if"):
                        j += 1
                    if j - i >= minb:
                        d = collections.Counter(disc(x) for x in kids[i:j]).most_common(1)[0][0]
                        out.append((rel, kids[i].line, j - i, "if/else_if", d))
                    i = j
                else:
                    i += 1
            run = []
            for k in kids + [None]:
                if k is not None and k.key == "if":
                    run.append(k)
                    continue
                if len(run) >= max(8, minb):
                    d, c = collections.Counter(disc(x) for x in run).most_common(1)[0]
                    if c >= len(run) * 0.8 and d not in ("?", "прочее"):
                        out.append((rel, run[0].line, len(run), "ряд if", d))
                run = []
            if nd.key == "switch":
                out.append((rel, nd.line, len(kids) - 1, "switch", "switch"))
            if nd.key in ("OR", "NOR", "AND", "NOT", "or") and len(kids) >= 10:
                key, c = collections.Counter(k.key for k in kids).most_common(1)[0]
                if c >= 10:
                    v = next(k for k in kids if k.key == key).value or ""
                    out.append((rel, nd.line, c, nd.key + "-список", f"{key}{' <cur>' if CUR_RE.search(v) else ''}"))
    return [(r, l, n, k, d, owner(r, l), heat(owner(r, l), r)) for r, l, n, k, d in out]


IT = re.compile(r"^(every|any|ordered|random)_(\w+)$")
WORLD_IT = {"country", "state", "market", "company", "character", "interest_group", "power_bloc", "province",
            "strategic_region", "state_region", "diplomatic_play", "war", "political_movement"}


def scan_nest():
    nested, hot = collections.Counter(), collections.Counter()
    for rel, root in trees().items():
        for nd, stack in root.walk():
            m = IT.match(nd.key or "")
            if not m:
                continue
            chain = [IT.match(s.key).group(2) for s in stack if IT.match(s.key or "")] + [m.group(2)]
            world = [c for c in chain if c in WORLD_IT]
            o = owner(rel, nd.line)
            h = heat(o, rel)
            if len(world) >= 2:
                nested[(" > ".join(world), rel, o, h)] += 1
            if m.group(2) in ("country", "state", "market", "company") and h in ("week", "month", "day"):
                hot[(h, nd.key, o, rel)] += 1
    return nested, hot


def scan_vars():
    w_set = re.compile(r"(?:set|change|clamp|round)_(?:global_|local_)?variable\s*=\s*\{[^{}]*?name\s*=\s*([A-Za-z_$][\w$]*)")
    w_short = re.compile(r"set_(?:global_|local_)?variable\s*=\s*([A-Za-z_$][\w$]*)")
    w_list = re.compile(r"add_to_(?:global_|local_)?variable_list\s*=\s*\{[^{}]*?name\s*=\s*([A-Za-z_$][\w$]*)")
    rd = [re.compile(p) for p in (
        r"(?:global_var|var|local_var):([A-Za-z_$][\w$]*)",
        r"has_(?:global_|local_)?variable(?:_list)?\s*=\s*([A-Za-z_$][\w$]*)",
        r"(?:every|any|random|ordered)_in_(?:global_|local_)?list\s*=\s*\{[^{}]*?variable\s*=\s*([A-Za-z_$][\w$]*)",
        r"is_target_in_(?:global_|local_)?variable_list\s*=\s*\{[^{}]*?name\s*=\s*([A-Za-z_$][\w$]*)",
        r"(?:variable_list_size|global_variable_list_size)\s*=\s*\{[^{}]*?name\s*=\s*([A-Za-z_$][\w$]*)",
        r"(?:Var|GlobalVariable|GetVariable|GetGlobalVariable|GetVariableList|GetGlobalList|GetList|HasVariable|"
        r"HasGlobalVariable|GetGlobalVariableList)\s*\(\s*'([A-Za-z_$][\w$]*)'")]
    writers, readers = collections.defaultdict(set), collections.defaultdict(set)
    for d, exts in (("common", (".txt",)), ("events", (".txt",)), ("gui", (".gui", ".txt")), ("localization/english", (".yml",))):
        for rel in script_files((d,), exts):
            t = read(os.path.join(FORK, rel))
            if rel.endswith(".txt"):
                t = re.sub(r"#[^\n]*", "", t)
            for rx in (w_set, w_short, w_list):
                for m in rx.finditer(t):
                    writers[m.group(1)].add(rel)
            for rx in rd:
                for m in rx.finditer(t):
                    readers[m.group(1)].add(rel)

    def expand(names):
        plain = {n for n in names if "$" not in n}
        pats = [re.compile("^" + re.sub(r"\\\$\w+\\\$", r"\\w+", re.escape(n)) + "$")
                for n in names if "$" in n and len(re.sub(r"\$\w+\$", "", n)) >= 5]
        return plain, pats

    wp, wpat = expand(writers)
    rp, rpat = expand(readers)
    has = lambda n, plain, pats: n in plain or any(p.match(n) for p in pats)  # noqa: E731
    no_reader = sorted(n for n in wp if not has(n, rp, rpat))
    no_writer = sorted(n for n in rp if not has(n, wp, wpat))
    return no_reader, no_writer, writers, readers


def scan_dups(minl=20, tmpl=False):
    def norm(nd):
        out = []
        for sub, _ in nd.walk():
            k, v = sub.key or "{", sub.value or ""
            if tmpl:
                k, v = template(k), template(v)
            out.append(f"{k}{sub.op or ''}{v}{'{' if sub.kids is not None else ''}")
        return "|".join(out)

    groups = collections.defaultdict(list)
    for rel, root in trees().items():
        for nd, _ in root.walk():
            if nd.kids is None or nd is root or nd.end_line - nd.line + 1 < minl:
                continue
            groups[hashlib.md5(norm(nd).encode()).hexdigest()].append((rel, nd.line, nd.end_line - nd.line + 1, nd.key))
    res = []
    for lst in groups.values():
        if len({(r, owner(r, l)) for r, l, s, k in lst}) >= 2:
            res.append((lst[0][2] * (len(lst) - 1), lst))
    res.sort(key=lambda x: -x[0])
    covered, kept = set(), []
    for waste, lst in res:
        if all(any(r == cr and cl <= l <= ce for cr, cl, ce in covered) for r, l, s, k in lst):
            continue
        for r, l, s, k in lst:
            covered.add((r, l, l + s - 1))
        kept.append((waste, lst))
    return kept


SKIP_NUM_KEYS = {"days", "months", "years", "weeks", "duration", "id", "level", "index", "priority", "position", "size"}
COMMON_NUMS = {"0", "1", "-1", "0.0", "1.0", "2", "100", "-100", "52", "7", "4", "12", "13", "20", "0.5", "10"}


def scan_magic():
    named, lit, ex = 0, collections.Counter(), collections.defaultdict(collections.Counter)
    skip = ("history", "/laws/", "static_modifiers", "production_methods", "buildings", "pop_needs", "game_rules",
            "modifier_type")
    for rel, root in trees().items():
        b = os.path.basename(rel)
        if not b.startswith(("ld_", "zz_")) or any(s in rel for s in skip):
            continue
        for top in root.kids:
            if top.kids is None and top.value and re.match(r"^-?\d+(\.\d+)?$", top.value):
                named += 1
                continue
            for nd, _ in top.walk():
                v = nd.value
                if v and re.match(r"^-?\d+(\.\d+)?$", v) and nd.key not in SKIP_NUM_KEYS and v not in COMMON_NUMS:
                    lit[rel] += 1
                    ex[rel][f"{nd.key}={v}"] += 1
    return named, lit, ex


def scan_headers():
    live = set(f[:-3] for f in os.listdir(HERE) if f.endswith(".py"))
    out = []
    for d, exts in (("common", (".txt",)), ("events", (".txt",)), ("gui", (".gui", ".txt")), ("localization/english", (".yml",))):
        for rel in script_files((d,), exts):
            head = read(os.path.join(FORK, rel))[:600]
            m = re.search(r"GENERATED by (?:tools/)?(\w+)\.py", head)
            if m and m.group(1) not in live:
                out.append((rel, m.group(1)))
    return out


def occ(rx, fpat=None, comments=False):
    r = re.compile(rx)
    hits = []
    for rel in script_files():
        if fpat and not re.search(fpat, rel):
            continue
        for i, line in enumerate(read(os.path.join(FORK, rel)).split("\n"), 1):
            for m in r.finditer(line if comments else line.split("#")[0]):
                hits.append((rel, i, m.group(0), line))
    return hits


# ---- вывод ---------------------------------------------------------------------------------------------------

def write_tsv(name, rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    return os.path.join(OUT, name)


def cmd_summary(a):
    tr = trees()
    total = sum(read(os.path.join(FORK, r)).count("\n") + 1 for r in tr)
    ours = sum(read(os.path.join(FORK, r)).count("\n") + 1 for r in tr if os.path.basename(r).startswith("ld_"))
    g = graph()
    fam = collections.defaultdict(int)
    for name, lst in g["defs"].items():
        t = template(name)
        if t != name:
            fam[t] += sum(e - l + 1 for k, r, l, e in lst)
    fams = collections.defaultdict(lambda: [0, 0])
    members = collections.Counter(template(n) for n in g["defs"] if template(n) != n)
    for t, lines in fam.items():
        if members[t] >= 5:
            fams[family_kind(t)][0] += lines
    print(f"скрипт: {total} строк ({len(tr)} файлов), ld_*: {ours}; определений {len(g['defs'])}")
    copies = sum(v[0] for v in fams.values())
    print(f"копии «сущность × N» (семейства ≥ 5): {copies} строк ({round(copies * 100 / max(total, 1))} %): "
          + ", ".join(f"{k} {v[0]}" for k, v in sorted(fams.items(), key=lambda x: -x[1][0])))
    hl = occ(r"has_law\s*=\s*law_type:law_\w+_currency")
    by = collections.Counter(heat(owner(r, l), r) for r, l, m, s in hl)
    print(f"has_law <cur>: {len(hl)} — " + ", ".join(f"{k} {v}" for k, v in by.most_common())
          + f"; в ld_*: {sum(1 for r, l, m, s in hl if os.path.basename(r).startswith('ld_'))}")
    print(f"var:zz_ef_cur: {len(occ(r'var:zz_ef_cur(?![a-z_])'))} чтений")
    gv = set(m.group(1) for r, l, m0, s in occ(r"(?:set|change)_global_variable\s*=\s*\{\s*name\s*=\s*\w+")
             for m in [re.search(r"name\s*=\s*(\w+)", m0)])
    gv |= set(re.findall(r"global_var:(\w+)", " ".join(s for r, l, m, s in occ(r"global_var:\w+"))))
    gv |= set(re.findall(r"has_global_variable\s*=\s*(\w+)", " ".join(s for r, l, m, s in occ(r"has_global_variable"))))
    gf = collections.Counter(template(n) for n in gv)
    print(f"глобальных переменных: {len(gv)}; в семействах ≥ 5: {sum(c for t, c in gf.items() if c >= 5)}; "
          f"наших zz_: {sum(1 for n in gv if n.startswith('zz_'))}")
    ch = scan_chains(10)
    write_tsv("chains.tsv", ch)
    cd = collections.Counter()
    for r, l, n, k, d, o, h in ch:
        cd[(h, d)] += n
    print(f"цепочки ≥ 10 веток: {len(ch)}, веток {sum(x[2] for x in ch)}; в неделе: "
          + ", ".join(f"{d} {n}" for (h, d), n in cd.most_common() if h == "week"))
    nested, hot = scan_nest()
    wk = sorted({(o, r) for (h, k, o, r) in hot if h == "week" and k == "every_country"})
    ours = [o for o, r in wk if os.path.basename(r).startswith("ld_")]
    print(f"мировой перебор стран в недельном пути: ld_* — {', '.join(ours)}; E&F — {len(wk) - len(ours)} "
          f"определений (граф завышает: проверять вызов)")
    sv = []
    for rel in script_files(("gui", "localization/english"), (".gui", ".yml")):
        sv += re.findall(r"ScriptValue\('([A-Za-z0-9_]+)'\)", read(os.path.join(FORK, rel)))
    print(f"окна: ScriptValue {len(sv)} вызовов, {len(set(sv))} разных")
    dl = occ(r"\bdebug_log\s*=")
    ungated = 0
    for r, l, m, s in dl:
        lines = read(os.path.join(FORK, r)).split("\n")
        if "zz_ef_logs_on" not in "\n".join(lines[max(0, l - 7):l]) and "ld_money_log_rest" not in r:
            ungated += 1
    print(f"debug_log: {len(dl)}, без zz_ef_logs_on рядом: {ungated}")
    nr, nw, _, _ = scan_vars()
    print(f"переменных без читателя: {len(nr)} (наших {sum(1 for n in nr if n.startswith('zz_'))}), "
          f"читателей без писателя: {len(nw)} (наших {sum(1 for n in nw if n.startswith('zz_'))})")
    print(f"точные дубли ≥ 20 строк: лишних {sum(w for w, l in scan_dups(20))} строк")
    named, lit, _ = scan_magic()
    print(f"числа в логике ld_*: {sum(lit.values())} литералов, {named} именованных констант")
    hd = scan_headers()
    print(f"«GENERATED» без живого генератора: {len(hd)} — " + ", ".join(f"{r} ({gname})" for r, gname in hd))
    cm = occ(r"zz_ef_[a-z_]+\.txt", comments=True)
    have = set(os.path.basename(r) for r in script_files())
    gone = [m for r, l, m, s in cm if m not in have]
    print(f"ссылок на имена файлов zz_ef_*.txt, которых в форке нет: {len(gone)} ({len(set(gone))} имён)")
    cl = [s for r, l, m, s in occ(r"^\s*#", comments=True) if os.path.basename(r).startswith("ld_")]
    hist = [s for s in cl if re.search(r"\br10[0-9]{2}_[0-9]{6}|run [a-z0-9_]+|\([0-9]{1,2}\.10|\bwas\b|Was:|night", s)]
    print(f"комментариев в ld_*: {len(cl)}, с прогоном / датой / «was»: {len(hist)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", nargs="?", default="summary",
                    choices=["summary", "chains", "nest", "families", "vars", "dups", "magic", "headers", "occ"])
    ap.add_argument("rx", nargs="?")
    ap.add_argument("--min", type=int)
    ap.add_argument("--files")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--defs", action="store_true")
    ap.add_argument("--lines", action="store_true")
    a = ap.parse_args()
    if a.cmd == "summary":
        cmd_summary(a)
    elif a.cmd == "chains":
        ch = scan_chains(a.min or 10)
        p = write_tsv("chains.tsv", sorted(ch, key=lambda c: -c[2]))
        s = collections.Counter()
        for r, l, n, k, d, o, h in ch:
            s[(h, k, d)] += n
        for (h, k, d), n in s.most_common(a.top):
            print(f"{h:8} {k:12} {d:16} веток {n}")
        print("->", p)
    elif a.cmd == "nest":
        nested, hot = scan_nest()
        print("== вложенные мировые переборы")
        for (ch, rel, o, h), c in sorted(nested.items(), key=lambda x: (x[0][3] != "week", x[0][3] != "month", -x[1]))[:a.top]:
            print(f"{h:8} {ch:24} {o}  {rel}  x{c}")
        print("== мировые переборы в неделе / месяце")
        for (h, k, o, rel), c in sorted(hot.items(), key=lambda x: (x[0][0], -x[1]))[:a.top * 3]:
            print(f"{h:6} {k:16} {o}  ({rel}) x{c}")
    elif a.cmd == "families":
        g = graph()
        fam = collections.defaultdict(lambda: [0, set(), collections.Counter()])
        for name, lst in g["defs"].items():
            t = template(name)
            if t != name:
                fam[t][1].add(name)
                for k, r, l, e in lst:
                    fam[t][0] += e - l + 1
                    fam[t][2][os.path.basename(r)] += 1
        rows = sorted(((v[0], len(v[1]), t, ", ".join(f for f, _ in v[2].most_common(2))) for t, v in fam.items()
                       if len(v[1]) >= 5), reverse=True)
        write_tsv("families.tsv", rows)
        for lines, n, t, ff in rows[:a.top]:
            print(f"{lines:7} {n:5}  {t}   {ff}")
    elif a.cmd == "vars":
        nr, nw, wr, rd = scan_vars()
        for title, lst, src in (("без читателя", nr, wr), ("без писателя", nw, rd)):
            fam = collections.Counter(template(n) for n in lst)
            print(f"== {title}: {len(lst)}; семейства: " + ", ".join(f"{k} {v}" for k, v in fam.most_common(10)))
            for n in lst:
                if n.startswith("zz_") or a.lines:
                    print(f"   {n}: {', '.join(sorted(src[n]))}")
    elif a.cmd == "dups":
        for tmpl in (False, True):
            kept = scan_dups(a.min or 20, tmpl)
            print(f"== {'с точностью до <cur> / N / <bank>' if tmpl else 'точные'}: лишних {sum(w for w, l in kept)} строк")
            for waste, lst in kept[:a.top]:
                ex = "; ".join(f"{os.path.basename(r)}:{l} {owner(r, l)}" for r, l, s, k in lst[:3])
                print(f"{waste:7} = {lst[0][2]} × {len(lst)}  [{lst[0][3]}]  {ex}")
    elif a.cmd == "magic":
        named, lit, ex = scan_magic()
        print(f"именованных констант: {named}; литералов: {sum(lit.values())}")
        for f, c in lit.most_common(a.top):
            print(f"{c:5} {f}   {', '.join(k for k, _ in ex[f].most_common(6))}")
    elif a.cmd == "headers":
        for rel, gname in scan_headers():
            print(f"{rel}: {gname}.py — нет в tools/")
    elif a.cmd == "occ":
        if not a.rx:
            ap.error("occ: нужен шаблон")
        hits = occ(a.rx, a.files)
        by = collections.Counter(heat(owner(r, l), r) for r, l, m, s in hits)
        print(f"всего {len(hits)}; по жаре: {dict(by.most_common())}")
        for f, c in collections.Counter(h[0] for h in hits).most_common(a.top):
            print(f"{c:7}  {f}")
        if a.defs:
            d = collections.Counter((r, owner(r, l)) for r, l, m, s in hits)
            for (r, o), c in d.most_common(a.top):
                print(f"{c:7}  {heat(o, r):8} {o}  ({r})")
        if a.lines:
            for r, l, m, s in hits[:a.top]:
                print(f"{r}:{l}: {s.strip()[:200]}")


if __name__ == "__main__":
    main()
