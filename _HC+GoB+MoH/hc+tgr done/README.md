This is part of [url=]Addon 1 for the MegaComPatch[/url]
[h1]Hail, Columbia! + Gates of the Bosphorus + Mandate of Heaven  +  The Great Revision ComPatch[/h1]

Compatibility patch for using the [b]Hail, Columbia! / Gates of the Bosphorus / Mandate of Heaven[/b] block together with [b]The Great Revision[/b].

Built 24.08.2026, against [b]TGR 2.0 (1.13.10)[/b], [b]Hail, Columbia! 8.6-Roosevelt[/b], [b]Gates of the Bosphorus 4.0.8[/b] and [b]Mandate of Heaven 1.4.6.1[/b]. Briefly carried a Victorian Century layer on top of four of its files (added and split back out again, same day, 26.08.2026) once VC plus this whole block together turned out too heavy to run at once on ordinary hardware -- see "Victorian Century" below for where that content lives now.

[h2]Load order[/h2]
[list]
[*]Community Mod Framework
[*]The Great Revision
[*]Hail, Columbia!
[*]Gates of the Bosphorus
[*]Mandate of Heaven
[*][b]this patch[/b]
[/list]

[h2]What this patch does[/h2]
[list]
[*][b]Gives TGR its two interest groups back[/b]
[list]
[*]TGR reworks [i]ig_landowners[/i] and [i]ig_rural_folk[/i] with [i]REPLACE_OR_CREATE:[/i] from its own files. Hail, Columbia! ships [i]common/interest_groups/00_landowners.txt[/i] and [i]00_rural_folk.txt[/i] - the vanilla paths, bare bodies - and loads last, so TGR's version of both is gone entirely.
[*]What TGR actually changes is four numbers: the leader-popularity multiplier in both groups (0.0025 to 0.030), and the rural-folk weights for farmers (200 to 250) and peasants (200 to 150). The patch merges those into HC's bodies three-way against vanilla, so a future edit by either author conflicts loudly instead of being dropped.
[*]TGR's [i]scope:interest_group ?= {[/i] -> [i]= {[/i] downgrade in the leader-popularity block is not carried -- vanilla and HC both use the safe form, and the strict one is the one that can go wrong in a scope that might not resolve. Restored throughout.
[/list]

[*][b]Cleans up Mandate of Heaven's copy of ig_rural_folk on the way past[/b]
[list]
[*]MoH [i]INJECT:[/i]s 316 lines into this interest group. Two of its fifteen sub-blocks are its own - the KMT leader ideology and the [i]Nongmin[/i] rename for Chinese cultures. The other thirteen are a copy of a pre-1.13 vanilla body: [i]has_law[/i] where 1.13 has [i]has_law_or_variant[/i], strict scopes where 1.13 has safe ones, an empty [i]on_character_ig_membership[/i] where vanilla has the Zanzibar religion rule, a [i]priority_cultures[/i] missing vanilla's Zanzibar rule, and [i]commander_leader_chance[/i], which 1.13 renamed to [i]commander_leader_weight[/i].
[*]The merged body carries MoH's two real additions and current vanilla everywhere else.
[/list]

[*][b]Jacksonian Democrats get their law stances back[/b]
[list]
[*]TGR injects [i]lawgroup_election_system[/i] and [i]lawgroup_legislative_process[/i] into [i]ideology_jacksonian_democrat[/i]; HC then rewrites the whole ideology and names neither, so a Jacksonian leader ends up with no opinion at all on either law group. The patch appends TGR's two stance blocks to HC's body.
[/list]

[*][b]Two starting companies[/b]
[list]
[*][i]common/history/countries/chi - china.txt[/i]: TGR and Mandate of Heaven ship the same path, MoH wins the file, and TGR's Ong Lung Sheng Tea Company never gets founded.
[*][i]common/history/countries/tur - ottoman empire.txt[/i]: same shape, Gates of the Bosphorus wins, and TGR's Imperial Arsenal goes with it.
[*]The patch ships each winner's file with TGR's [i]add_company[/i] block appended.
[/list]
[/list]

[h2]Victorian Century[/h2]
Four of the files above -- [i]zz_hct_ig_landowners.txt[/i], [i]zz_hct_ig_rural_folk.txt[/i], [i]zz_hct_jacksonian_democrat.txt[/i] and [i]tur - ottoman empire.txt[/i] -- are REPLACEd a second time by the standalone [i]ComPatch HC + GoB + MoH + The Great Revision + Victorian Century[/i] (folder [i]_HC+GoB+MoH/hc+vc done[/i]), which layers Victorian Century's own rework on top of the exact base built here. It imports the base-building functions straight from this pair's own generator ([i]tools/regen_addon1.py[/i]) rather than recomputing them, so the two can never quietly drift apart. [i]chi - china.txt[/i] was checked against VC too and needs no change either way. Get that compatch, and Victorian Century, if you want VC -- see its own README for the full write-up, including [i]usa - usa.txt[/i], which lives there now since TGR never touched that file to begin with.

[h2]Checked and deliberately left alone[/h2]
[list]
[*][b]manifest_destiny.[/b] Hail, Columbia! ships [i]common/decisions/manifest_destiny.txt[/i] with the whole decision commented out - it deliberately removes the vanilla decision and replaces it with a 1100-line journal-entry chain. TGR's rework of that same decision goes with the file, and its [i]great_revision_events.5[/i] and [i]great_revision_usa_manifest_destiny[/i] become unreachable. That is HC's design working as intended; putting TGR's decision back would give the player two Manifest Destinies.
[*][b]je_oregon / je_conquer_oregon.[/b] HC rewrites both from [i]common/journal_entries/00_oregon.txt[/i] and wins the path. The only thing of TGR's that is lost is a group reassignment ([i]je_group_usa_manifest_destiny[/i] to [i]je_group_historical_content[/i]) - and HC owns that journal entry group. TGR's file is also a stale copy of an older vanilla: pre-[i]sr:[/i] region syntax, strict scopes, a missing British Columbia homeland block and [i]months = normal_modifier_time[/i], which is 152 years.
[*][b]ig_armed_forces, ig_intelligentsia, ig_petty_bourgeoisie, ideology_communist.[/b] TGR rewrites, MoH injects, different sub-blocks. Additive.
[*][b]law_ethnostate, law_freedom_of_conscience, law_protectionism, law_canton_system, law_theocracy.[/b] In every case the last mod to touch the law injects, and into a sub-block nobody else names.
[*][b]NAI.[/b] Defines merge per key. HC sets [i]NUM_GROWING_COLONIES_MAX[/i]; TGR and Kuromi's AI set neither that nor anything overlapping it.
[/list]
