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
    # 4.10 (П.15, the user): straight onto "£ = 7.31" -- no stops on the diplomacy (0.15 0.012) and innovation
    # (0.1 0.06) icons of the top bar; 3 s for the tooltip to pin; one hover a card (the second height, +0.0125 for
    # E&F's wrapped silver line, missed every card with the new tooltip -- the user saw a row-by-row walk).
    # the first tooltip of a macro did not show (the cash card missed twice) -- a warm-up hover first
    $s = @("hover 0.6 0.97; wait 0.5; hover 0.0975 0.0916; wait 1; hover 0.6 0.97; wait 1")
    foreach ($k in $Cards.Keys) {
        $s += "hover 0.0975 0.0916; wait 3; hover 0.0975 0.125; wait 0.3; hover 0.03 $($Cards[$k]); wait 2; shot {P}_card_$k; hover 0.6 0.97; wait 1"
    }
    return ($s -join "; ")
}

# П.15 (4.10, the user): the budget tooltip ("£ +125K", top bar) pins itself; each of its lines' number has a
# tooltip of its own (the breakdown). Lines as in Britain's of 1836: 18 px a line from 0.176 to 0.636 (1440p);
# a stop on a heading or a gap just shoots the bare tooltip.
function BudgetTipShots {
    $s = @("hover 0.6 0.97; wait 1; hover 0.24 0.012; wait 3; shot {P}_budgettip")
    $i = 0
    for ($y = 0.176; $y -le 0.636; $y += 0.016) {
        $i++
        $s += "hover 0.6 0.97; wait 0.5; hover 0.24 0.012; wait 3; hover 0.2 0.05; wait 0.3; hover 0.17 $([Math]::Round($y, 4)); wait 1.5; shot {P}_budgettip_$('{0:D2}' -f $i)"
    }
    $s += "hover 0.6 0.97; wait 1"
    return ($s -join "; ")
}

# П.15 (4.10, the user: population, incomes, needs, the census): the population panel (the left column's
# icon at 0.461), the classes' income / taxes / needs tooltips (columns 0.06 / 0.13 / 0.2), then the census
# (the panel's bottom button) -- the table paged by the wheel over it.
function PopShots {
    # the panel remembers its tab (it opened on "Diagrams", 4.10) -- "Overview" clicked first; the census is the
    # "census" step (sort / row), not pages (the user: "no 500 screenshots of the census")
    $s = @("hover 0.75 0.55; wait 0.5; click 0.0085 0.461; wait 2; click 0.05 0.145; wait 1; hover 0.75 0.55; wait 1; crop {P}_pop 0 0 640 1440")
    foreach ($c in @(@("low", 0.06), @("mid", 0.13), @("high", 0.2))) {
        foreach ($r in @(@("income", 0.529), @("taxes", 0.559), @("needs", 0.587))) {
            $s += "hover $($c[1]) $($r[1]); wait 1.5; crop {P}_pop_$($c[0])_$($r[0]) 0 0 1400 1440; hover 0.75 0.55; wait 0.5"
        }
    }
    return ($s -join "; ")
}

$Macros = @{
    pop      = PopShots
    # П.15: the inflation tooltip (the top bar's second row, "-8.03%")
    infl     = "hover 0.6 0.97; wait 1; hover 0.0575 0.0907; wait 2.5; shot {P}_inflation; hover 0.6 0.97; wait 1"
    budgettip = BudgetTipShots
    # П.15: the budget's Economy, Finance and Stocks tabs whole -- every collapsed section expanded, page by page
    # (the "browse" step: the scrollbar's thumb, stops at the end or when the panel changes)
    budgetall = "hover 0.6 0.97; key f2; wait 2; hover 0.13 0.09; wait 0.8; click 0.13 0.214; wait 1.5; browse {P}_eco; hover 0.13 0.09; wait 0.8; click 0.1725 0.214; wait 1.5; browse {P}_fin; hover 0.13 0.09; wait 0.8; click 0.215 0.214; wait 1.5; browse {P}_stocks; click 0.2265 0.095; wait 1"
    # the currency tooltip ("Денежная масса" and the money's value, all accounts in one): the top bar
    # expands on hover, the second row holds "CHF = 19.2" (the currency's value); its tooltip lists
    # M0..M3 and the accounts. F2 + the panel's X first: F2 opens the budget over any panel ("tag"
    # leaves a state panel open, its title tooltip took the hover), the X closes it.
    currency = "key f2; wait 1; click 0.2265 0.095; wait 1; hover 0.0975 0.0916; wait 3; shot {P}_currency; hover 0.6 0.97; wait 1"
    cards    = CardShots
    # the budget panel (F2, the left column's second icon) and its five tabs page by page. F2 opens it over
    # any other panel and does not toggle; the panel's X (0.2265 0.095) closes it at the end
    budget   = "key f2; wait 2; " + (Pages 0.045 5 "t1_overview") + "; " + (Pages 0.0875 3 "t2_states") + "; " + (Pages 0.13 7 "t3_economy") + "; " + (Pages 0.1725 8 "t4_finance") + "; " + (Pages 0.215 3 "t5_stocks") + "; click 0.2265 0.095; wait 1"
}
