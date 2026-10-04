<#
Drives a Victoria 3 window left open by run_vic3_sandbox.ps1 -KeepOpen (4.10, night of stages 0-4):
screenshots of tooltips and panels, other countries, then closing the game with the logs gathered.

Usage (PowerShell):
    powershell -ExecutionPolicy Bypass -File tools\vic3_ui.ps1 -OutDir <run dir> -Do "<step>;<step>;..."
Steps (';'-separated, run in order):
    shot <name>             screenshot of the window into <OutDir>\<name>.png
    click <fx> <fy>         left click at a fraction of the window (2560x1440 measured)
    hover <fx> <fy>         move the mouse there (a tooltip opens after ~1 s)
    scroll <fx> <fy> <n>    mouse wheel there, n notches (negative = down)
    wait <sec>              sleep
    key <name>              esc | space | enter | f1..f9 (scan codes for DirectInput)
    console <command>       a console command (debug_mode), e.g. "console tag GBR"
    macro <name> <prefix>   a named step sequence from vic3_ui_points.ps1 ({P} = prefix)
    tips <set> <prefix>     every hover of the named set below, one screenshot each (<prefix>_<n>.png)
    country <TAG>           "tag <TAG>", then the currency tooltip, its account cards and the budget tabs (macros
                            currency, cards, budget)
    close                   close the game and gather the logs into <OutDir> (eflog.txt as after a run)
#>
param(
    [Parameter(Mandatory = $true)][string]$OutDir,
    [Parameter(Mandatory = $true)][string]$Do
)

$ErrorActionPreference = "Stop"
$Docs = Join-Path $env:USERPROFILE "Documents\Paradox Interactive\Victoria 3"
$Logs = Join-Path $Docs "logs"
New-Item -ItemType Directory -Force $OutDir | Out-Null
$t0f = Join-Path $OutDir "t0.txt"
$t0 = if (Test-Path $t0f) { [datetime]::Parse((Get-Content $t0f -Raw).Trim(), $null, [Globalization.DateTimeStyles]::RoundtripKind) } else { (Get-Date).AddHours(-3) }

. (Join-Path $PSScriptRoot "vic3_ui_lib.ps1")

$Keys = @{ esc = @(0x1B, 0x01); space = @(0x20, 0x39); enter = @(0x0D, 0x1C)
    f1 = @(0x70, 0x3B); f2 = @(0x71, 0x3C); f3 = @(0x72, 0x3D); f4 = @(0x73, 0x3E); f5 = @(0x74, 0x3F)
    f6 = @(0x75, 0x40); f7 = @(0x76, 0x41); f8 = @(0x77, 0x42); f9 = @(0x78, 0x43) }

# Named hover sets: the points measured on the screenshots of the night of 4.10 (fractions of a
# 2560x1440 window). Filled in as they are found.
$TipSets = @{}
$Macros = @{}
$setsFile = Join-Path $PSScriptRoot "vic3_ui_points.ps1"
if (Test-Path $setsFile) { . $setsFile }

foreach ($step in ($Do -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ })) {
    $a = $step -split '\s+', 2
    $cmd = $a[0]; $rest = if ($a.Count -gt 1) { $a[1] } else { "" }
    $p = Get-Game
    if (-not $p -and $cmd -ne "close") { Log "no game running - '$step' skipped"; break }
    switch ($cmd) {
        "shot"    { Focus-Game $p; Start-Sleep -Milliseconds 300; Shot $p ($rest + ".png") }
        "click"   { $xy = $rest -split '\s+'; Click-Window $p ([double]$xy[0]) ([double]$xy[1]) }
        "hover"   { $xy = $rest -split '\s+'; Hover-Window $p ([double]$xy[0]) ([double]$xy[1]) }
        "scroll"  { $xy = $rest -split '\s+'; Scroll-Window $p ([double]$xy[0]) ([double]$xy[1]) ([int]$xy[2]) }
        "wait"    { Start-Sleep -Milliseconds ([int]([double]$rest * 1000)) }
        "key"     { $k = $Keys[$rest]; Send-Key ([byte]$k[0]) ([byte]$k[1]) }
        "console" { Console-Cmd $p $rest }
        "tips"    {
            $xy = $rest -split '\s+'; $set = $TipSets[$xy[0]]; $pre = $xy[1]
            if (-not $set) { Log "no tip set '$($xy[0])'"; break }
            $i = 0
            foreach ($pt in $set) {
                $i++
                if ($pt.click) { Click-Window $p $pt.click[0] $pt.click[1]; Start-Sleep -Milliseconds 1200 }
                if ($pt.hover) { Hover-Window $p $pt.hover[0] $pt.hover[1]; Start-Sleep -Milliseconds 1800 }
                Shot $p ("{0}_{1:D2}_{2}.png" -f $pre, $i, $pt.name)
            }
        }
        "macro"   {
            $xy = $rest -split '\s+'; $m = $Macros[$xy[0]]
            if (-not $m) { Log "no macro '$($xy[0])'"; break }
            & $PSCommandPath -OutDir $OutDir -Do ($m -replace '\{P\}', $xy[1])
        }
        "country" {
            # sit down as another country (paused, nothing played) and take its money screens
            & $PSCommandPath -OutDir $OutDir -Do "console tag $rest; wait 3; hover 0.6 0.97; wait 1; macro currency $rest; macro cards $rest; macro budget $rest"
        }
        "browse"  {
            # П.15 (4.10): the open panel's tab top to bottom -- every collapsed section expanded (only "›",
            # what is open stays open), a shot a page, until the page stops moving. "browse <name> [pages]".
            # Paged by dragging the scrollbar's thumb (x 0.2375): the wheel over the content scrolled the nested
            # tables (currencies, countries) instead of the panel, over the scrollbar it did nothing. A "›" that stays after its click (a button,
            # not a section) is not clicked again.
            $xy = $rest -split '\s+'; $name = $xy[0]; $max = if ($xy.Count -gt 1) { [int]$xy[1] } else { 150 }
            # the panel's title bar is remembered; before every click and drag it must be the same -- the user
            # closed the panel once and the drags went on over the map (4.10)
            Hover-Window $p 0.13 0.09; Start-Sleep -Milliseconds 700
            $title = Region-Sig $p 130 540 95 175
            $same = { (Region-Sig $p 130 540 95 175) -eq $title }
            # to the top: the thumb dragged above the track
            $th = Find-Thumb $p 608 280 1435
            if ($th) { Drag-Window $p 0.2375 (($th[0] + $th[1]) / 2) 0.2375 0.15 }
            Hover-Window $p 0.13 0.09; Start-Sleep -Milliseconds 700
            $last = ""
            for ($pg = 1; $pg -le $max; $pg++) {
                $skip = @()
                for ($k = 0; $k -lt 10; $k++) {
                    $f = @(Find-Collapsed $p 50 92 300 1430 | Where-Object { $y = $_; -not ($skip | Where-Object { [Math]::Abs($_ - $y) -lt 0.004 }) })
                    if ($f.Count -eq 0) { break }
                    if (-not (& $same)) { Log "browse: the panel changed - stopping"; $pg = $max + 1; break }
                    Log ("browse: expanding the section at y {0:N4}" -f $f[0])
                    Click-Window $p 0.06 $f[0]; Start-Sleep -Milliseconds 900; Hover-Window $p 0.13 0.09; Start-Sleep -Milliseconds 500
                    $after = @(Find-Collapsed $p 50 92 300 1430)
                    if ($after | Where-Object { [Math]::Abs($_ - $f[0]) -lt 0.004 }) { $skip += $f[0]; Log "browse: it stays collapsed - skipped" }
                }
                if ($pg -gt $max) { break }
                if (-not (& $same)) { Log "browse: the panel changed - stopping"; break }
                $sig = Region-Sig $p 60 600 300 1430
                if ($sig -eq $last) { Log "browse: the end at page $pg"; break }
                $last = $sig
                Shot $p ("{0}_{1:D2}.png" -f $name, $pg)
                # a page down: the thumb dragged by 85% of its height (its height is the visible share)
                $th = Find-Thumb $p 608 280 1435
                if (-not $th) { Log "browse: no scrollbar - one page"; break }
                $mid = ($th[0] + $th[1]) / 2; Drag-Window $p 0.2375 $mid 0.2375 ($mid + 0.85 * ($th[1] - $th[0]))
                Hover-Window $p 0.13 0.09; Start-Sleep -Milliseconds 700
            }
        }
        "close"   { Close-And-Collect }
        default   { Log "unknown step '$step'" }
    }
}
Log "vic3_ui done: $Do"
