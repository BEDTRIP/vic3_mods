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
[*][b]Fixes the Power Bloc “Force Regime Change” diplomatic action conflict[/b]
[list]
[*]Both mods define/overwrite the same diplomatic action ID: [i]force_regime_change[/i]. Without a merge, whichever mod loads last wins and the other logic is lost.
[*]This patch ships a merged [i]force_regime_change[/i] so you keep the intended behavior from both sides:
[list]
[*]Keeps TGR requirements/effects (baseline cohesion + short tenure, installed regime modifier duration, cohesion cost).
[*]Keeps PBE requirements/effects (progressiveness-distance requirement and optional infamy incident when PBE diplo-action rules are enabled).
[/list]
[/list]
[/list]

[h2]Notes[/h2]
[list]
[*]This patch is intentionally minimal and only touches [i]common/diplomatic_actions/force_regime_change[/i]. If you have other mods that also change Power Bloc diplomatic actions, you may need an additional merge patch.
[/list]
[url=https://github.com/BEDTRIP/vic3_mods]my github[/url]