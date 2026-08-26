This is an [b]anti-mod[/b] for [b]The Great Revision (TGR)[/b] that disables selected TGR modules by overwriting their files with empty “disabled” stubs.

[h2]Load order[/h2]
[list]
[*]Community Mod Framework (CMF)
[*]The Great Revision (TGR)
[*][b]AntiTGR: no Better Politics and German Unification (this mod)[/b]
[/list]

[i]This mod must be loaded after TGR, otherwise it cannot disable TGR content.[/i]

[h2]What this mod does[/h2]
[list]
[*][b]Disables TGR Politics module[/b]
[list]
[*]Overrides TGR Politics files (laws/lawgroups/ideologies/parties/etc.) with empty stubs so they do not load in-game.
[*]Effectively removes the “TGR_POLITICS_*” content from your run while keeping the rest of TGR enabled.
[/list]

[*][b]Disables TGR German Unification module[/b]
[list]
[*]Overrides German Unification content (country formation, JEs, scripted buttons, on_actions, events, AI defines, truces) with empty stubs.
[*]Effectively removes the “TGR_GER_UNIFICATION_*” content from your run while keeping the rest of TGR enabled.
[/list]
[/list]

[h2]Notes / compatibility[/h2]
[list]
[*]This mod [b]adds nothing[/b] — it only disables parts of TGR by file overwrite.
[*]If you also run [b]Better Politics Mod (BPM)[/b] together with TGR, the intended full stack is usually:
[list]
[*]CMF
[*]TGR
[*][b]AntiTGR (this mod)[/b]
[*]BPM
[*]ComPatch BPM + TGR (separate mod from this pack)
[/list]
[*]If another mod re-enables/replaces the same TGR files, the last loaded mod wins.
[/list]
