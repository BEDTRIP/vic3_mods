"""E&F finance snapshot from a text save (not ironman): one row per country, by GDP.

Usage:  py tools/save_measure_ef.py [save]   (name in "save games" or a full path; default autosave.v3)

Columns: gdp, treasury (budget money), credit (credit limit), principal (debt), cap = sum of the four
stock averages zz_ef_cap_avg_* (hotfix EF.24), cap/gdp, index base_index_value, dif = yearly change
country_indice_value_dif_01, litR = zz_ef_literate_rich_share (EF.28), rate, ob = overcapacity penalty
speculative_share_2, msh = mass shareholding points, infamy, ban = private sectors banned (hotfix, ex ef+psc).
Values in currency of the country, M. Negative variables are stored as unsigned 64-bit in the save
and print as ~1.8e14: read them as (value - 184467440737095.5).
Written for the 1850 run (2026-09-25), see the research archive, "Прогон 1850".
"""
import os, re, sys, collections
p = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(r'~\Documents\Paradox Interactive\Victoria 3\save gamesutosave.v3')
if not os.path.isabs(p):
    p = os.path.join(os.path.expanduser(r'~\Documents\Paradox Interactive\Victoria 3\save games'), p)
s = open(p, 'rb').read().decode('utf-8', 'replace')
cm = s.find('\ncountry_manager={'); cm_end = s.find('\nstates={')
seg = s[cm:cm_end]
VR = re.compile(r'flag=(\w+)\n(?:\t+tick=\d+\n)?\t+data=\{\n\t+type=(\w+)\n(?:\t+identity=(-?\d+))?')
rows = []
tag_of = {}
for m in re.finditer(r'\n(\d+)=\{\n(?:\t[^\n]*\n){0,3}?\tdefinition="(\w+)"', seg):
    cid, tag = m.group(1), m.group(2); tag_of[cid] = tag
    rec = seg[m.start():seg.find('\n}\n', m.start())]
    v = {a: (int(c) / 100000 if c else 0) for a, t, c in VR.findall(rec)}
    g = re.search(r'\tgdp=\{.*?values=\{ ([^}]*)\}', rec, re.S)
    gdp = float(g.group(1).split()[-1]) if g else 0
    mo = re.search(r'\n\t\tmoney=(-?[\d.]+)', rec); cr = re.search(r'\n\t\tcredit=(-?[\d.]+)', rec)
    pr = re.search(r'\n\t\tprincipal=(-?[\d.]+)', rec)
    inf = re.search(r'\n\tinfamy=([\d.]+)', rec)
    alive = '\n\tstates={' in rec
    cap = sum(v.get(k, 0) for k in ('zz_ef_cap_avg_ms', 'zz_ef_cap_avg_as', 'zz_ef_cap_avg_mn', 'zz_ef_cap_avg_rr'))
    rows.append(dict(tag=tag, id=cid, gdp=gdp, money=float(mo.group(1)) if mo else 0, credit=float(cr.group(1)) if cr else 0,
        principal=float(pr.group(1)) if pr else None, infamy=float(inf.group(1)) if inf else 0, alive=alive, cap=cap,
        idx=v.get('base_index_value'), dif=v.get('country_indice_value_dif_01'), lit=v.get('zz_ef_literate_rich_share'),
        rate=v.get('base_rate_percentage'), ob=v.get('speculative_share_2'), bub=v.get('speculative_share_1'),
        msh=v.get('zz_ef_msh_points'), gl=v.get('government_loan'), ccb=v.get('credit_at_central_bank'), ban=('zz_pb_ef_css_private_ban' in v)))
rows.sort(key=lambda r: -r['gdp'])
def f(x, d=1):
    return '-' if x is None else (f'{x/1e6:.{d}f}' if abs(x) >= 1e5 else f'{x:.3g}')
print('tag   alive gdpM   money  credit  princ  capM  cap/gdp idx   dif    litR  rate   ob  msh  infamy ban')
for r in rows[:45]:
    print(f"{r['tag']:5} {int(r['alive'])} {f(r['gdp']):>6} {f(r['money']):>7} {f(r['credit']):>7} {f(r['principal']):>6} {f(r['cap']):>6} {r['cap']/r['gdp'] if r['gdp'] else 0:6.2f} {r['idx'] or 0:6.0f} {r['dif'] or 0:6.2f} {r['lit'] or 0:5.3f} {r['rate'] or 0:6.4f} {r['ob'] or 0:4.0f} {r['msh'] or 0:4.1f} {r['infamy']:5.1f} {int(r['ban'])}")
dead_idx = [r for r in rows if not r['alive'] and r['idx']]
print('dead with index:', [(r['tag'], r['idx']) for r in dead_idx][:20])
