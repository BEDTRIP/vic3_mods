# Power Blocs Expanded (PBE) + The Great Revision (TGR) ComPatch

<!-- meta
пара: PBE × TGR
статус: done
версии: Updated for 1.13.10
позиция: —
файлов: 3
генератор: —
зависит от: —
-->

## Для мастерской

This is part of [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3638078714]this MegaComPatch[/url]
[h1]Power Blocs Expanded (PBE) + The Great Revision (TGR) ComPatch[/h1]
[h2]Load order[/h2]
[list]
[*]The Great Revision (TGR)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3637467628]my TGR RU Localization (if u need)[/url]
[*]Power Blocs Expanded (PBE)
[*][url=https://steamcommunity.com/sharedfiles/filedetails/?id=3490395930]PBE RU Localization (if u need)[/url]
[*][b]PBE + TGR ComPatch (this mod)[/b]
[/list]

[i]This patch should be loaded after both mods. Place other mods after it only if they do not overwrite the same content (especially [b]common/diplomatic_actions[/b]).[/i]

[h2]What this patch does[/h2]
[list]
[*][b]Merges the Power Bloc "Force Regime Change" diplomatic action[/b]
[list]
[*]Both mods redefine the same diplomatic action ID [i]force_regime_change[/i]. PBE loads last, so without a patch every TGR change to it is lost silently.
[*]The merged action keeps PBE's structure and TGR's tuning:
[list]
[*]PBE: the cohesion/tenure requirement is lifted while PBE's [i]diplomatic action changes[/i] game rule is on, and the action instead costs infamy scaled to the target's population.
[*]TGR: cohesion floor 25%, tenure requirement of 1 year instead of vanilla's 5, and the [i]Installed Regime[/i] modifier lasts 24 months.
[*]Vanilla + TGR: the cohesion cost on accept is restored (PBE drops it, so with its rule off the action was free).
[/list]
[/list]
[/list]

[h2]Notes[/h2]
[list]
[*]This patch is intentionally minimal: [b]one[/b] database entry, [i]common/diplomatic_actions/force_regime_change[/i]. Nothing else in the two mods collides in a way that needs merging.
[*]The two mods also define the same modifier types ([i]country_influence_add[/i], [i]state_bureaucrats_investment_pool_contribution_add[/i]), but they differ only in tooltip colour and decimal places, so no patch is shipped for them.
[*]If you run other mods that change Power Bloc diplomatic actions, you may need an additional merge patch.
[/list]
[b]Updated for 1.13.10[/b] - PBE renamed its internal prefix, which broke the previous version of this patch: its infamy branch referenced identifiers that no longer exist.
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]

---

## Подробности

_Пока только описание для мастерской: подробного разбора для этого компача не писали._
