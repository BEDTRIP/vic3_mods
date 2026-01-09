import re
from pathlib import Path


LAWGROUP_RE = re.compile(r"\blawgroup_[A-Za-z0-9_]+\b")


def extract_law_groups(common_dir: Path) -> set[str]:
    """
    Extract *used* law-groups from a mod by scanning all txt files under common/.

    This captures both:
    - `group = lawgroup_x` in common/laws/
    - `lawgroup_x = { ... }` stances in common/ideologies/
    - any other references across scripts
    """
    groups: set[str] = set()
    if not common_dir.exists():
        return groups
    for p in common_dir.rglob("*.txt"):
        txt = p.read_text(encoding="utf-8-sig", errors="ignore")
        groups.update(LAWGROUP_RE.findall(txt))
    return groups


def main() -> None:
    vc_common = Path(
        r"C:\Users\Andrey\Projects\vic3_mods_out\Victorian Century\common"
    )
    tgr_common = Path(
        r"C:\Users\Andrey\Projects\vic3_mods_out\TheGreatRevision\common"
    )

    vc = extract_law_groups(vc_common)
    tgr = extract_law_groups(tgr_common)

    vc_only = sorted(vc - tgr)
    tgr_only = sorted(tgr - vc)

    print(f"VC_COUNT {len(vc)}")
    print(f"TGR_COUNT {len(tgr)}")
    print("VC_ONLY")
    for g in vc_only:
        print(g)
    print("TGR_ONLY")
    for g in tgr_only:
        print(g)


if __name__ == "__main__":
    main()

