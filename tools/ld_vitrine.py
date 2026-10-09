"""R1а.9 (схема 3.1, 3.12): the vitrine -- the model values the windows of the fork read.

Usage:  python tools/ld_vitrine.py [--write] [--check]

Scans the fork's gui/**/*.gui and localization/english/**/*.yml (the other languages are copies) for the model's
names read through the GUI's data functions: ScriptValue('zz_ef_*'), Var('zz_ef_*') / GetVariable('zz_ef_*').
Each name is classed by what the window pays for it:
  var   -- a country variable read directly;
  vit   -- a script value that only reads a variable (`zz_ef_v_*` and the like: value = 0 / if has_variable ->
           value = var:...), cheap;
  calc  -- any other script value: computed at every redraw of the window (loops over buildings, states, goods ...)
           -- to be moved behind a variable set at the step (R10, each stage keeps the vitrine alive).
--write puts the counts and the list into docs/vitrine.md between the markers <!-- vitrine --> / <!-- /vitrine -->;
--check exits 1 if the doc's block differs from what the scan gives.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ld_gen  # noqa: E402

FORK = ld_gen.FORK
REF = re.compile(r"(ScriptValue|Var|GetVariable)\('(zz_ef_[A-Za-z0-9_]+)'\)")
DEF = re.compile(r"^(zz_ef_[A-Za-z0-9_]+)\s*=\s*\{", re.M)
DOC = os.path.join(FORK, "docs", "vitrine.md")
B, E = "<!-- vitrine -->", "<!-- /vitrine -->"


def bodies():
    out = {}
    root = os.path.join(FORK, "common", "script_values")
    for fn in sorted(os.listdir(root)):
        s = open(os.path.join(root, fn), encoding="utf-8-sig", errors="replace").read()
        for m in DEF.finditer(s):
            d, i = 0, s.index("{", m.start())
            for j in range(i, len(s)):
                if s[j] == "{":
                    d += 1
                elif s[j] == "}":
                    d -= 1
                    if d == 0:
                        break
            out[m.group(1)] = (fn, s[i + 1:j])
    return out


def is_vit(body):
    b = re.sub(r"#[^\n]*", "", body)
    toks = re.sub(r"\s+", " ", b).strip()
    return bool(re.fullmatch(r"(value = 0 )?(if = \{ limit = \{ has_variable = \w+ \} value = var:\w+ \} ?)+|value = var:\w+", toks))


def scan():
    refs = {}
    for top in ("gui", os.path.join("localization", "english")):
        for dp, _, fs in os.walk(os.path.join(FORK, top)):
            for fn in fs:
                if not fn.endswith((".gui", ".yml")):
                    continue
                rel = os.path.relpath(os.path.join(dp, fn), FORK).replace("\\", "/")
                s = open(os.path.join(dp, fn), encoding="utf-8-sig", errors="replace").read()
                for kind, name in REF.findall(s):
                    refs.setdefault(name, [set(), set()])
                    refs[name][0].add("var" if kind != "ScriptValue" else "sv")
                    refs[name][1].add(rel)
    defs = bodies()
    rows = []
    for name in sorted(refs):
        kinds, files = refs[name]
        if "sv" not in kinds:
            cls = "var"
        elif name in defs and is_vit(defs[name][1]):
            cls = "vit"
        else:
            cls = "calc"
        rows.append((name, cls, sorted(files)))
    return rows


def block(rows):
    n = {c: sum(1 for r in rows if r[1] == c) for c in ("var", "vit", "calc")}
    files = sorted({f for r in rows for f in r[2]})
    out = [B, f"Сгенерировано `../vic3_mods/tools/ld_vitrine.py --write`. Имён {len(rows)}: переменных {n['var']}, "
              f"значений-витрины {n['vit']}, вычисляемых при перерисовке {n['calc']}; файлов {len(files)}.", "",
           "| имя | класс | где читается |", "| --- | --- | --- |"]
    for name, cls, fs in rows:
        where = ", ".join(f"`{f}`" for f in fs[:3]) + (f" и ещё {len(fs) - 3}" if len(fs) > 3 else "")
        out.append(f"| `{name}` | {cls} | {where} |")
    out.append(E)
    return "\n".join(out)


def main():
    rows = scan()
    blk = block(rows)
    doc = open(DOC, encoding="utf-8").read()
    if B in doc:
        cur = doc[doc.index(B):doc.index(E) + len(E)]
    else:
        cur = None
    if "--check" in sys.argv:
        print("vitrine: " + ("same" if cur == blk else "differs"))
        sys.exit(0 if cur == blk else 1)
    n = {c: sum(1 for r in rows if r[1] == c) for c in ("var", "vit", "calc")}
    print(f"names {len(rows)}: var {n['var']}, vit {n['vit']}, calc {n['calc']}")
    if "--write" in sys.argv:
        if cur is None:
            doc = doc.rstrip("\n") + "\n\n" + blk + "\n"
        else:
            doc = doc.replace(cur, blk)
        open(DOC, "w", encoding="utf-8").write(doc)


if __name__ == "__main__":
    main()
