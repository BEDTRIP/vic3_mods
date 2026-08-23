def bank_companies(ef: Path) -> list[str]:
    """Every company E&F itself calls a bank, straight out of E&F.

    Source: the `private_bank_type` block in
    common/customizable_localization/00_ef_localization_ custom.txt -- 99 entries,
    one `is_company_type = company_type:X` per bank, which is E&F's own answer to
    "is this company a bank" and the only list of them it keeps.

    This replaces a hand-written table, and the table is why the Imperial Bank of
    China never became China's central bank: CENTRAL_BANK_COMPANY named the
    Da-Qing Bank for CHI, the Da-Qing Bank is founded in 1905, and the bank China
    actually holds in 1836 is company_BankIBC -- which was on no list of ours at
    all. Mexico, Persia, Turkey and Sicily were the same shape of miss. Any table
    written here is a race against E&F's roster that it eventually loses.

    company_BasicBank is dropped: it is E&F's generic bank, offered to every
    country, and letting it stand for "this country has its own historical bank"
    would mean nobody ever gets the generated one.
    """
    src = read(ef / "common/customizable_localization/00_ef_localization_ custom.txt")
    m = re.search(r"^private_bank_type\s*=\s*\{", src, re.M)
    if not m:
        return []
    blk = src[m.start():block_span(src, m.end() - 1)]
    out, seen = [], set()
    for name in re.findall(r"is_company_type\s*=\s*company_type:(\w+)", blk):
        if name != "company_BasicBank" and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def historical_central_banks(ef: Path) -> tuple[list[str], list[str]]:
    """Every bank company E&F ships, best candidate for the central bank first.

    ORDER, NOT MEMBERSHIP, is what CENTRAL_BANK_COMPANY decides now. It used to
    decide both, and that is why four countries kept a stand-in they should have
    handed over: the table named one bank per tag, and the bank the country
    actually held was a different one. China holds the Imperial Bank of China in
    1836, not the Da-Qing Bank of 1905. The rule that survives contact is the
    loose one -- whatever bank this country holds is its central bank -- with the
    curated table breaking ties, because Britain holds six and the Bank of England
    should win.

    E&F's grants are still checked against the table, so a rename is reported
    rather than quietly producing a branch that can never fire.
    """
    notes: list[str] = []
    every = bank_companies(ef)
    if not every:
        notes.append("WARNING private_bank_type: no bank list found in E&F, "
                     "falling back to the curated table alone")
    known = set(every)
    granted = establish_mapping(ef, known)
    table = {t: ([c] if isinstance(c, str) else list(c))
             for t, c in CENTRAL_BANK_COMPANY.items()}
    out: list[str] = []
    for tag in sorted(table):
        for comp in table[tag]:
            if comp not in known:
                notes.append(f"WARNING {comp}: E&F does not call it a bank any more")
                continue
            if comp not in granted:
                notes.append(f"WARNING {comp}: E&F grants it to nobody")
            elif tag not in granted[comp]:
                notes.append(f"WARNING {comp}: E&F grants it to {granted[comp]}, not {tag}")
            if comp not in out:
                out.append(comp)
    curated = len(out)
    for comp in every:
        if comp not in out:
            out.append(comp)
    notes.append(f"bank companies: {len(out)} ({curated} curated first, "
                 f"{len(out) - curated} from E&F's own list)")
    return out, notes
