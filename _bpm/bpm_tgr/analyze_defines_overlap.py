from __future__ import annotations

import re
from pathlib import Path


def parse_defines(mod_root: Path) -> dict[str, dict[str, dict[str, str]]]:
    """
    Heuristic parser for Vic3 defines:
    - namespace at depth 0: NAI = {
    - key at depth 1: SOME_KEY = value

    Returns: namespace -> key -> { filename -> value }
    """
    out: dict[str, dict[str, dict[str, str]]] = {}
    defines_dir = mod_root / "common" / "defines"
    if not defines_dir.exists():
        return out

    for p in sorted(defines_dir.glob("*.txt")):
        try:
            lines = p.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
        except Exception:
            lines = p.read_text(errors="ignore").splitlines()

        depth = 0
        ns: str | None = None

        for raw in lines:
            # keep raw for brace accounting; strip comments for parsing
            line = raw.split("#", 1)[0].strip()

            if depth == 0:
                m_ns = re.match(r"^([A-Za-z0-9_]+)\s*=\s*\{", line)
                if m_ns:
                    ns = m_ns.group(1)
                    out.setdefault(ns, {})

            elif depth == 1 and ns:
                m_kv = re.match(r"^([A-Za-z0-9_]+)\s*=\s*(.+)$", line)
                if m_kv:
                    key = m_kv.group(1)
                    val = m_kv.group(2).strip()
                    out[ns].setdefault(key, {})[p.name] = val

            depth += raw.count("{")
            depth -= raw.count("}")
            if depth <= 0:
                depth = 0
                ns = None

    return out


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    tgr_root = repo / ".TheGreatRevision"
    bpm_root = repo / ".BPM"

    tgr = parse_defines(tgr_root)
    bpm = parse_defines(bpm_root)

    for ns in sorted(set(tgr) & set(bpm)):
        inter = sorted(set(tgr[ns]) & set(bpm[ns]))
        print(f"== {ns} == overlap keys: {len(inter)}")
        for k in inter:
            tvals = tgr[ns][k]
            bvals = bpm[ns][k]
            t_example = next(iter(tvals.values()))
            b_example = next(iter(bvals.values()))

            differs = (t_example != b_example) or (len(tvals) > 1) or (len(bvals) > 1)
            print(f"- {k}: TGR({len(tvals)} files) vs BPM({len(bvals)} files)" + (" DIFF" if differs else ""))
            if differs:
                for fn, val in sorted(tvals.items()):
                    print(f"  TGR {fn}: {val}")
                for fn, val in sorted(bvals.items()):
                    print(f"  BPM {fn}: {val}")
        print()


if __name__ == "__main__":
    main()

