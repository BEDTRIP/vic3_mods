This is part of [url=]Addon 1 for the MegaComPatch[/url]
[h1]Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven  +  The Great Revision ComPatch[/h1]

Compatibility patch for using the [b]Hail, Columbia! / Gates of the Bosphorus / Mandate of Heaven[/b] block together with [b]The Great Revision[/b]. [b]Victorian Century[/b] is a dependency too -- see below.

Built 24.08.2026, extended 26.08.2026 with Victorian Century's law stances, its rework of both interest groups, and its additions to all three history files below, against [b]TGR 2.0 (1.13.10)[/b], [b]Hail, Columbia! 8.6-Roosevelt[/b], [b]Gates of the Bosphorus 4.0.8[/b], [b]Mandate of Heaven 1.4.6.1[/b] and [b]Victorian Century[/b] (unpacked 2026-08-25, the mod declares no version).

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]The Great Revision
[*]Victorian Century
[*]ComPatch: The Great Revision + Victorian Century
[*]Hail, Columbia!
[*]Gates of the Bosphorus
[*]Mandate of Heaven
[*][b]this patch[/b]
[/list]

[h2]What this patch does[/h2]
[list]
[*][b]Gives TGR its two interest groups back -- and now Victorian Century's rework of them too[/b]
[list]
[*]TGR reworks [i]ig_landowners[/i] and [i]ig_rural_folk[/i] with [i]REPLACE_OR_CREATE:[/i] from its own files, and Victorian Century reworks both of them again, wholesale, the same way. Hail, Columbia! ships [i]common/interest_groups/00_landowners.txt[/i] and [i]00_rural_folk.txt[/i] - the vanilla paths, bare bodies - and loads last of the three, so TGR's and VC's versions are both gone entirely.
[*]What TGR actually changes is four numbers: the leader-popularity multiplier in both groups (0.0025 to 0.030), and the rural-folk weights for farmers (200 to 250) and peasants (200 to 150). The patch merges those into HC's bodies three-way against vanilla, so a future edit by either author conflicts loudly instead of being dropped.
[*]What Victorian Century changes is much bigger: nation-specific noble trait sets in [i]ig_landowners[/i] (Russia, Japan, Prussia, Austria, China, Turkey, Spain, plus a German-nobles ideology switch), three new pop types eligible for [i]ig_landowners[/i] membership (capitalists, bureaucrats, peasants) with matching pop_weight bonuses for Prussia and for non-French European freemen, three ideology-switch blocks in [i]ig_rural_folk[/i] on_enable (Russia, Britain, the British East India Company), a China officers/soldiers clause in [i]ig_rural_folk[/i]'s pop_potential, and two Chinese-officer pop_weight bonuses there. All of it is folded in on top of the TGR+HC(+MoH) body, three-way against vanilla per sub-block, so it survives alongside every number and rule already merged in.
[*]Neither TGR's nor VC's identical [i]scope:interest_group ?= {[/i] -> [i]= {[/i] downgrade in the leader-popularity block is carried -- vanilla and HC both use the safe form, and the strict one is the one that can go wrong in a scope that might not resolve. Restored throughout, which also fixed one occurrence TGR's own merge had already let through silently before Victorian Century was added to this build.
[/list]

[*][b]Cleans up Mandate of Heaven's copy of ig_rural_folk on the way past[/b]
[list]
[*]MoH [i]INJECT:[/i]s 316 lines into this interest group. Two of its fifteen sub-blocks are its own - the KMT leader ideology and the [i]Nongmin[/i] rename for Chinese cultures. The other thirteen are a copy of a pre-1.13 vanilla body: [i]has_law[/i] where 1.13 has [i]has_law_or_variant[/i], strict scopes where 1.13 has safe ones, an empty [i]on_character_ig_membership[/i] where vanilla has the Zanzibar religion rule, a [i]priority_cultures[/i] missing vanilla's Zanzibar rule, and [i]commander_leader_chance[/i], which 1.13 renamed to [i]commander_leader_weight[/i].
[*]The merged body carries MoH's two real additions and current vanilla everywhere else.
[/list]

[*][b]Jacksonian Democrats get their law stances back -- from TGR and now from Victorian Century too[/b]
[list]
[*]TGR injects [i]lawgroup_election_system[/i] and [i]lawgroup_legislative_process[/i] into [i]ideology_jacksonian_democrat[/i]; HC then rewrites the whole ideology and names neither, so a Jacksonian leader ends up with no opinion at all on either law group. The patch appends TGR's two stance blocks to HC's body.
[*]Victorian Century adds 10 new laws to vanilla law groups and, via the [i]ComPatch: The Great Revision + Victorian Century[/i] compatch, injects a stance on each of them into every vanilla-side ideology including this one -- eight law groups in all, one new law apiece in [i]lawgroup_bureaucracy[/i] and [i]lawgroup_distribution_of_power[/i] (both of which HC already has an opinion on) and six whole new groups ([i]taxation, education_system, economic_system, trade_policy, citizenship, policing[/i]). HC's rewrite drops all eight the same way it drops TGR's two. The patch folds VC's two single-law additions into HC's existing bureaucracy/distribution_of_power blocks and appends the six new groups whole.
[*]Source for VC's stances: the [i]tgr+vc[/i] compatch's own generated file, itself built from a hand-filled spreadsheet (see that compatch's README) -- this patch reads that compatch's output, not Victorian Century directly, so build order is compatch-1 (TGR + VC) before compatch-2 (this one).
[/list]

[*][b]Two starting companies[/b]
[list]
[*][i]common/history/countries/chi - china.txt[/i]: TGR and Mandate of Heaven ship the same path, MoH wins the file, and TGR's Ong Lung Sheng Tea Company never gets founded.
[*][i]common/history/countries/tur - ottoman empire.txt[/i]: same shape, Gates of the Bosphorus wins, and TGR's Imperial Arsenal goes with it.
[*]The patch ships each winner's file with TGR's [i]add_company[/i] block appended.
[/list]
[*][b]Victorian Century's laws checked against all three history files -- China gets nothing new, the Ottomans and the USA do[/b]
[list]
[*][i]chi - china.txt[/i]: VC's [i]activate_law[/i] list looks different from MoH's at first glance, but the difference is structural, not a missed update -- MoH swaps [i]law_serfdom[/i] for [i]law_tenant_farmers[/i] and hangs its own [i]amendment_chinese_traditional_land_system[/i] on that exact law; MoH and VC pick different, similarly-named bureaucracy laws for entirely different reasons ([i]law_imperial_examinations[/i] for MoH's own [i]je_keju[/i] chain vs. VC's [i]law_imperial_examination[/i]); and VC's one new law, [i]law_classical_learning[/i], needs serfdom or its own imperial-examination law active to enact -- neither holds once MoH's picks win, so adding it would ship a law with an unmet prerequisite. Nothing else in VC's file is portable: the rest is VC's own parallel China journal/political chain, same call already made for [i]CHI_minguo[/i]/[i]CHI_republic[/i] in [i]hc+vc done[/i]. MoH's file ships unchanged; three [i]need()[/i] checks in [i]regen_addon1.py[/i] ([i]_check_china_activate_law_vs_vc[/i]) catch drift in either mod's law list or the unmet prerequisite.
[*][i]tur - ottoman empire.txt[/i]: VC is much closer to vanilla here than to GoB (keeps [i]law_autocracy[/i]/[i]law_slave_trade[/i], leaves migration controls alone), so three things carry cleanly on top of GoB's file: [i]law_madrasa[/i] (VC's one new law, [i]lawgroup_education_system[/i]; its prerequisite [i]law_millet_system[/i] is already active in every version of the file, and GoB's own [i]amendment_gbbf_elifba[/i] had no law to attach a new active pick to until now) plus VC's two lawgroup amendments ([i]amendment_salt_monopoly[/i] on taxation, [i]amendment_kanunname_law[/i] on governance principles -- both groups GoB never touches, both target laws already active regardless of which version of the file is winning). Left out: VC's three extra starting techs and its own Ottoman journal chain (Peter the Great of Turkey, Sublime Porte and five more entries) -- the same parallel-political-system call as China's, just with a different outcome.
[*][i]usa - usa.txt[/i]: HC and VC pick laws in 15 groups; 10 agree outright and 5 compete (VC would put the USA on different governance, distribution-of-power, taxation, trade-policy and citizenship laws) -- HC's own picks win all five, same reasoning as China and the Ottomans. What still carries is VC's law-group [i]amendment[/i] chain: an amendment attaches to whichever law is active in its group, not to one specific law, so 12 of VC's 14 amendments (2 were already byte-identical to ones HC ships itself) are safe regardless of which of the five competing law picks wins. Not carried: VC's own tariff setting and its entire parallel American journal/variable/modifier chain -- the same [i]manifest_destiny.txt[/i]-precedent call as above, just for the USA instead of Oregon.
[*]All three checks are programmatic (exact [i]activate_law[/i] list comparisons, exact amendment-count and prerequisite assertions in [i]regen_addon1.py[/i]) so a future update to any of the four mods fails loudly here instead of silently going stale.
[/list]
[/list]

[h2]Checked and deliberately left alone[/h2]
[list]
[*][b]manifest_destiny.[/b] Hail, Columbia! ships [i]common/decisions/manifest_destiny.txt[/i] with the whole decision commented out - it deliberately removes the vanilla decision and replaces it with a 1100-line journal-entry chain. TGR's rework of that same decision goes with the file, and its [i]great_revision_events.5[/i] and [i]great_revision_usa_manifest_destiny[/i] become unreachable. That is HC's design working as intended; putting TGR's decision back would give the player two Manifest Destinies.
[*][b]je_oregon / je_conquer_oregon.[/b] HC rewrites both from [i]common/journal_entries/00_oregon.txt[/i] and wins the path. The only thing of TGR's that is lost is a group reassignment ([i]je_group_usa_manifest_destiny[/i] to [i]je_group_historical_content[/i]) - and HC owns that journal entry group. TGR's file is also a stale copy of an older vanilla: pre-[i]sr:[/i] region syntax, strict scopes, a missing British Columbia homeland block and [i]months = normal_modifier_time[/i], which is 152 years.
[*][b]ig_armed_forces, ig_intelligentsia, ig_petty_bourgeoisie, ideology_communist.[/b] TGR rewrites, MoH injects, different sub-blocks. Additive.
[*][b]law_ethnostate, law_freedom_of_conscience, law_protectionism, law_canton_system, law_theocracy.[/b] In every case the last mod to touch the law injects, and into a sub-block nobody else names.
[*][b]NAI.[/b] Defines merge per key. HC sets [i]NUM_GROWING_COLONIES_MAX[/i]; TGR and Kuromi's AI set neither that nor anything overlapping it.
[/list]
