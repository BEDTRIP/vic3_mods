import re

p = "tools/regen_ef_currency_merge.py"
s = open(p, encoding="utf-8").read()

old = s[s.index("def gen_popneed("): s.index("def gen_modtypes(")]
new = '''def gen_popneed(src: str, removed: list[str], keep: str) -> str:
    """Drop the `entry = { goods = <removed> ... }` blocks.

    Brace-matched, not regex-matched: E&F closes the last entry as `}#end_tag_1`,
    a comment on the same line as the brace, and any pattern that looks for a
    lone closing brace on its own line runs straight past it into the closing
    brace of popneed_currency itself.
    """
    out = src
    rm = set(removed)
    while True:
        for m in re.finditer(r"[ \\t]*entry\\s*=\\s*\\{", out):
            end = block_span(out, m.end() - 1)
            body = out[m.start():end]
            g = re.search(r"\\bgoods\\s*=\\s*([a-z0-9_]+)", strip_comments(body))
            if g and g.group(1) in rm:
                nl = out.find("\\n", end)
                out = out[:m.start()] + out[(nl + 1 if nl != -1 else end):]
                break
        else:
            break
    head = (BANNER +
            f"### Source: the hotfix's own {POPNEED_FILE}.\\n"
            f"### popneed_currency keeps two entries: local_currency (weight 0.1, the\\n"
            f"### fallback for countries with no monetary system) and {keep} (0.25).\\n"
            "### The 56 dropped entries all carried the same weights, so a pop's currency\\n"
            "### need is satisfied exactly as before -- out of one good instead of 57.\\n\\n")
    return head + out


'''
s = s.replace(old, new)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
