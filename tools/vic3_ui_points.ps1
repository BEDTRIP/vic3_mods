<#
Points and step sequences of tools/vic3_ui.ps1, measured on the screenshots of the night of 4.10.2026
(Victoria 3 1.13.11, this playset, 2560x1440 window, Russian UI). Fractions of the window.
Macros: "macro <name> <prefix>" runs the sequence; {P} in it becomes the prefix of the shots.
#>

# a neutral spot for the mouse (the budget panel's title): no map tooltip over the shot
$Neutral = "0.13 0.09"

function Pages($tabX, $n, $tag) {
    # a budget tab: click it (the mouse leaves the left icon column first: hovered, it unfolds its
    # labels over the panel's tabs and the click opened the buildings panel, 4.10), back to the top, then a shot per page (9 wheel notches ~ 420 px)
    $s = "hover $Neutral; wait 0.8; click $tabX 0.214; scroll 0.12 0.6 40; hover $Neutral; wait 1.2; shot {P}_${tag}_1"
    for ($i = 2; $i -le $n; $i++) { $s += "; scroll 0.12 0.6 -9; hover $Neutral; wait 1; shot {P}_${tag}_$i" }
    return $s
}

# The account cards: links inside the currency tooltip (it pins itself after ~2 s, then the mouse
# may enter it). Rows as in Britain's tooltip of 1836 (gold standard); under silver (Russia,
# Switzerland) E&F's line "share of silver reserves ... (140.11%)" wraps and every row is one line
# (~0.0125) lower -- the night of 4.10 got only the treasury card for Russia. So each card is taken
# at both heights (<card>_a, <card>_b); the one that missed shows the bare currency tooltip.
# 4.10 (П.1/П.7): the tooltip opens with the four-line rate block; abroad moved under "outside the money".
# Rows as in Britain's tooltip of 1838 (gold standard).
$Cards = [ordered]@{ cash = 0.2613; business = 0.3307; deposits = 0.3724; treasury = 0.4418; pool = 0.456; abroad = 0.4978; cb = 0.5387 }
function CardShots {
    $s = @()
    foreach ($k in $Cards.Keys) {
        foreach ($v in @(@("a", 0.0), @("b", 0.0125))) {
            $y = [Math]::Round($Cards[$k] + $v[1], 4)
            $s += "hover 0.15 0.012; wait 1; hover 0.1 0.06; wait 0.5; hover 0.0975 0.0916; wait 3; hover 0.06 0.1; wait 0.3; hover 0.03 $y; wait 2.5; shot {P}_card_${k}_$($v[0]); hover 0.6 0.97; wait 2"
        }
    }
    return ($s -join "; ")
}

$Macros = @{
    # the currency tooltip ("Денежная масса" and the money's value, all accounts in one): the top bar
    # expands on hover, the second row holds "CHF = 19.2" (the currency's value); its tooltip lists
    # M0..M3 and the accounts. F2 + the panel's X first: F2 opens the budget over any panel ("tag"
    # leaves a state panel open, its title tooltip took the hover), the X closes it.
    currency = "key f2; wait 1; click 0.2265 0.095; wait 1; hover 0.15 0.012; wait 1; hover 0.1 0.06; wait 0.5; hover 0.0975 0.0916; wait 3; shot {P}_currency; hover 0.6 0.97; wait 2"
    cards    = CardShots
    # the budget panel (F2, the left column's second icon) and its five tabs page by page. F2 opens it over
    # any other panel and does not toggle; the panel's X (0.2265 0.095) closes it at the end
    budget   = "key f2; wait 2; " + (Pages 0.045 5 "t1_overview") + "; " + (Pages 0.0875 3 "t2_states") + "; " + (Pages 0.13 7 "t3_economy") + "; " + (Pages 0.1725 8 "t4_finance") + "; " + (Pages 0.215 3 "t5_stocks") + "; click 0.2265 0.095; wait 1"
}
