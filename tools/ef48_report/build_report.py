"""EF.48 run report page (1.10.2026): report_template.html + run JSONs + report_meta.json -> report/block_v_report.html.

Usage: py tools/ef48_report/build_report.py "прогон 7=<path>/run7.json" ["прогон 6=..." ...]
Run JSONs come from tools/parse_eflog.py; texts (done, decisions, open questions) are in report_meta.json.
Published as an artifact: https://claude.ai/artifact/5NxWf7z2CFJAEbQhuVuxBB (republish with url=).
"""
import json, os, sys
SCR = os.path.dirname(os.path.abspath(__file__))
data = {}
for r in sys.argv[1:]:
    name, path = r.split("=", 1)
    data[name] = json.load(open(path if os.path.isabs(path) else os.path.join(os.getcwd(), path), encoding="utf-8"))
meta = open(os.path.join(SCR, "report_meta.json"), encoding="utf-8").read()
json.loads(meta)
tpl = open(os.path.join(SCR, "report_template.html"), encoding="utf-8").read()
out = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False)).replace("/*__META__*/null", meta)
os.makedirs(os.path.join(SCR, "report"), exist_ok=True)
open(os.path.join(SCR, "report", "block_v_report.html"), "w", encoding="utf-8").write(out)
print("ok", len(out))
