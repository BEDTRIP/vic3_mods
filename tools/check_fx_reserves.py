"""R1б (8.10): foreign currency in a CB's reserves, straight from a text save -- what the model values it at.

    py tools/check_fx_reserves.py [save] TAG [TAG ...]

Per country: E&F's stocks of other currencies in its states (stockpiling_<cur>_state_1, the units the model counts in the
engine's money); per currency the global E&F value (money_value_<cur>_global_var, gold per national unit) and the
issuer's parity in gold the model keeps (zz_ef_fxpar_<cur>, R1б.1) -- the model's value of a unit is the first over the
second (zz_ef_fx_gold_<cur>), E&F's value as it is when the parity is not kept. Sums both ways.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from save_money_check import SAVES, VAR_RE, block, var_value  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')


def main():
    args = sys.argv[1:]
    path = os.path.join(SAVES, 'autosave.v3')
    if args and not re.fullmatch(r'[A-Z][A-Z0-9]{2}', args[0]):
        path = args.pop(0)
        if not os.path.isabs(path):
            path = os.path.join(SAVES, path)
    s = open(path, 'rb').read().decode('utf-8', 'replace')
    date = re.search(r'game_date=([\d.]+)', s).group(1)
    allv = {k: var_value(x) for k, x in VAR_RE.findall(s)}
    value = {k[len('money_value_'):-len('_global_var')]: v for k, v in allv.items()
             if k.startswith('money_value_') and k.endswith('_global_var')}
    par = {k[len('zz_ef_fxpar_'):]: v for k, v in allv.items() if k.startswith('zz_ef_fxpar_')}
    print(f'{os.path.basename(path)} {date}: E&F values {len(value)}, parities kept {len(par)}')
    seg, _ = block(s, 'country_manager')
    ids = {}
    for mm in re.finditer(r'\n(\d+)=\{\n(?:\t[^\n]*\n){0,3}?\tdefinition="(\w+)"', seg):
        ids[mm.group(2)] = mm.group(1)
    states_seg, _ = block(s, 'states')
    for tag in args:
        cid = ids.get(tag)
        tot_ef = tot_mod = 0.0
        rows = []
        for mm in re.finditer(r'\n(\d+)=\{\n', states_seg):
            end = states_seg.find('\n}\n', mm.start())
            rec = states_seg[mm.start():end]
            c = re.search(r'\n\tcountry=(\d+)', rec)
            if not c or c.group(1) != cid:
                continue
            for k, raw in VAR_RE.findall(rec):
                m = re.fullmatch(r'stockpiling_(\w+?)_state_1', k)
                if not m or m.group(1).endswith('reserve_currency'):
                    continue
                cur, units = m.group(1), var_value(raw)
                if not units:
                    continue
                ef = units * value.get(cur, 0)
                mod = ef / par[cur] if par.get(cur) else ef
                tot_ef += ef
                tot_mod += mod
                rows.append((mod, cur, units, value.get(cur, 0), par.get(cur, 0), ef))
        print(f'\n{tag}: by E&F value {tot_ef:,.0f}, by the model {tot_mod:,.0f}')
        for mod, cur, units, v, p, ef in sorted(rows, reverse=True)[:15]:
            print(f'  {cur:32} units {units:14,.0f}  value {v:9.4f}  parity {p:9.4f}  E&F {ef:14,.0f}  model {mod:14,.0f}')


if __name__ == '__main__':
    main()
