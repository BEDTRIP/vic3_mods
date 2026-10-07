<#
Sandbox run of Victoria 3 for the agent (EF.48, 2026-10-01).

Launches the game with the last save (-continuelastsave -debug_mode), waits for
it to load, sets speed 5 and unpauses, lets it run, pauses, takes a screenshot
of the game window, closes the game and collects the logs. The weekly money
model writes one line a week per big economy into debug.log (EFW = the step,
EFR = the GUI bridge's receiver, scripted_effects/zz_ef_money_model.txt;
EFX = every currency once a month, EFC = a currency-crisis redemption);
they are extracted into <OutDir>/eflog.txt.

Progress is checked by the date on screen (debug.log is buffered until the
game closes, autosaves may be half-yearly): the window must stay visible and
the date at its top right uncovered; a standing date is unpaused.

The save must be played as a country: in observer mode the game does not run
GUI commands, so the bridge (and the savings) stay empty.

While it runs the game takes the keyboard focus: do not type or click.

Usage (PowerShell):
    powershell -ExecutionPolicy Bypass -File tools\run_vic3_sandbox.ps1 -RunMinutes 5
Parameters:
    -RunMinutes   real minutes to let the game run at speed 5 (default 5)
    -LoadWaitSec  at most this many seconds for the save to load (default 400); the script goes on as
                  soon as the game's screen is up (Wait-Screen, by the colour of the left icon column)
    -Autosaves    stop as soon as this many new autosaves are written (0 = run -RunMinutes);
                  -RunMinutes stays the limit. Autosaves are half-yearly in this setup, so
                  the state to read from the save needs the run to pass 1 Jan / 1 Jul.
    -NoModLogs    do not send "event zz_ef_logs.1" (the fork's EF* debug logs stay off, as in a normal game);
                  through the bridge: the word "nomodlogs" in -Commands
    -Minimized    run with the game window minimized (R1а, Р8 7.10: does the GUI bridge live without drawing?);
                  the date is not checked while minimized, the window comes back before the pause;
                  through the bridge: the word "minimized" in -Commands
    -Commands     extra console commands after loading, ';'-separated (e.g. "dump_data_types"); their
                  output files in logs/ are copied with the other logs. "end:<cmd>" -- entered at the end of
                  the run, after the pause; "end:ui:<step>" -- a vic3_ui.ps1 step there (script profiler:
                  "Script.Profiling.Start;end:Script.Profiling.Stop;end:Script.Profiling.Gui;end:ui:wait 3;
                  end:ui:shot prof_1"; ScriptProfiling.Dump crashes 1.13.11, vanilla too -- 7.10)
    -AiTag        console "enable_ai <tag>" after loading, so the AI plays the player's country
                  too (default "all"; "" to skip)
    -StartSave    start from this save instead of the last one: a file name in "save games" (e.g.
                  sandbox_1836.v3). It is copied to sandbox_start.v3 and continue_game.json is pointed at
                  the copy, so the original is never written to; later runs without -StartSave go on
                  from the run's own autosaves -- if it made none, "continue" is put back to the previous save.
                  A manual save may open in the lobby (no country chosen): a random country, then "tag <Tag>".
    -NewGame      start a new game from 1836 instead of a save (start conditions, history files):
                  main menu -> New game -> Sandbox -> Random country -> Start, then the console
                  "tag <Tag>". Clicks are at fractions of the window, measured on 2560x1440 (16:9).
    -Playset      run on this launcher playset's mods instead of the last ones the launcher started (the game
                  reads content_load.json, not the active playset -- 6.10): the file is written from
                  launcher-v2.sqlite (tools/playset_content_load.py) and put back after the run, failures too
    -Tag          the country to play in a new game (default GBR)
    -NoDumps      kept for old command lines; does nothing (1.10 night: debugcountrybudgets and
                  debugmarkets are strings in victoria3.exe, but the release console answers
                  "Unknown command" -- developer-build commands)
    -KeepOpen     leave the game paused at the end instead of closing it (tooltips and other countries
                  with tools/vic3_ui.ps1, which closes it and gathers the logs: -Do close)
    -Shots        at the end (paused) take the money screens of the played country: the currency tooltip,
                  its account cards, every budget tab page by page (tools/vic3_ui.ps1, macros in
                  vic3_ui_points.ps1); <Tag>_*.png
    -Countries    then sit down as these countries in turn ("GBR,USA,RUS"; console "tag") and take the
                  same screens of each; nothing is played as them, the game stays paused
    -OutDir       where to put logs and screenshots (default: %TEMP%\vic3_sandbox\<timestamp>)
#>
param(
    [int]$RunMinutes = 5,
    [int]$LoadWaitSec = 400,
    [int]$Autosaves = 0,
    [string]$AiTag = "all",
    [string]$Commands = "",
    [switch]$NoModLogs,
    [switch]$Minimized,
    [string]$StartSave = "",
    [switch]$NewGame,
    [string]$Tag = "BUG",
    [string]$Playset = "",
    [switch]$NoDumps,
    [switch]$KeepOpen,
    [switch]$Shots,
    [string]$Countries = "",
    [string]$OutDir = ""
)

$ErrorActionPreference = "Stop"
$Exe = "C:\games\steam\steamapps\common\Victoria 3\binaries\victoria3.exe"
$Docs = Join-Path $env:USERPROFILE "Documents\Paradox Interactive\Victoria 3"
$Logs = Join-Path $Docs "logs"
if (-not $OutDir) { $OutDir = Join-Path $env:TEMP ("vic3_sandbox\" + (Get-Date -Format "yyyyMMdd_HHmmss")) }
New-Item -ItemType Directory -Force $OutDir | Out-Null

. (Join-Path $PSScriptRoot "vic3_ui_lib.ps1")

if (Get-Game) { throw "Victoria 3 is already running - close it first." }

# -continuelastsave loads the save named by "title" in continue_game.json.
if ($StartSave) {
    $Saves = Join-Path $Docs "save games"
    $src = Join-Path $Saves $StartSave
    if (-not (Test-Path $src)) { throw "no save $src" }
    Copy-Item $src (Join-Path $Saves "sandbox_start.v3") -Force
    $cg = Join-Path $Docs "continue_game.json"
    $j = Get-Content $cg -Raw -Encoding UTF8 | ConvertFrom-Json
    $prevTitle = $j.title
    $j.title = "sandbox_start"
    [IO.File]::WriteAllText($cg, ($j | ConvertTo-Json), (New-Object Text.UTF8Encoding $false))
    Log "start save: $StartSave (copied to sandbox_start.v3)"
}

# -Playset: the game's mod list for this run; the previous one comes back at the end (and on a failure, by the trap)
$ContentLoad = Join-Path $Docs "content_load.json"
$ContentBackup = Join-Path $OutDir "content_load.before.json"
if ($Playset) {
    Copy-Item $ContentLoad $ContentBackup -Force
    & python (Join-Path $PSScriptRoot "playset_content_load.py") --playset $Playset --out $ContentLoad | ForEach-Object { Log "playset $_" }
    if ($LASTEXITCODE -ne 0) { Copy-Item $ContentBackup $ContentLoad -Force; throw "no playset '$Playset'" }
    trap { if (Test-Path $ContentBackup) { Copy-Item $ContentBackup $ContentLoad -Force; Log "content_load.json restored (failure)" }; break }
}

if ($NewGame) {
    Log "launching $Exe -debug_mode (new game)"
    Start-Process -FilePath $Exe -ArgumentList "-debug_mode" -WorkingDirectory (Split-Path $Exe)
} else {
    Log "launching $Exe -continuelastsave -debug_mode"
    Start-Process -FilePath $Exe -ArgumentList "-continuelastsave", "-debug_mode" -WorkingDirectory (Split-Path $Exe)
}

$t0 = Get-Date
$p = $null
while (((Get-Date) - $t0).TotalSeconds -lt 240) {
    $p = Get-Game
    if ($p -and $p.MainWindowHandle -ne 0) { break }
    Start-Sleep 3
}
if (-not $p -or $p.MainWindowHandle -eq 0) { throw "no game window after 4 minutes" }
if ($NewGame) {
    # The main menu, the goals screen, the lobby (map), the game (2026-10-01, 1.13.11 with this playset).
    Wait-Screen "menu" 300 3 | Out-Null
    $p = Get-Game
    Shot $p "00a_menu.png"
    Click-Window $p 0.2086 0.394                                               # New game
    Wait-Screen "goals" 90 4 | Out-Null; Shot $p "00b_goals.png"
    Click-Window $p 0.8665 0.625                                               # Sandbox: start the game
    Wait-Screen "lobby" 180 3 | Out-Null; Shot $p "00c_lobby.png"
    Click-Window $p 0.25 0.981; Start-Sleep 2                                  # Random country
    Click-Window $p 0.9215 0.975; Log "new game: starting"                     # Start
    Wait-Screen "game" 300 8 | Out-Null
    $p = Get-Game
    Console-Cmd $p "tag $Tag"
    Start-Sleep 5
} else {
    Log "window up, waiting for the save to load (at most $LoadWaitSec s)"
    # a save may open in the lobby (r1005_103836, -StartSave of a manual save: the country picker, no country
    # chosen -- "Начать" does nothing until one is, r1005_104216 waited 5 min): as for a new game -- "Случайное
    # государство", "Начать", then "tag" to -Tag (without -Tag the run plays the random country -- logged)
    if ((Wait-Screen @("game", "lobby") $LoadWaitSec 8) -eq "lobby") {
        $p = Get-Game; Shot $p "00c_lobby.png"
        Click-Window $p 0.25 0.981; Start-Sleep 2
        Click-Window $p 0.9215 0.975; Log "the save opened in the lobby: a random country, starting"
        Wait-Screen "game" 300 8 | Out-Null
        if ($PSBoundParameters.ContainsKey("Tag")) { Console-Cmd (Get-Game) "tag $Tag"; Start-Sleep 5 }
        else { Log "no -Tag: playing the random country of the lobby" }
    }
}
$p = Get-Game
Shot $p "01_loaded.png"
if ($AiTag) { Console-Cmd $p "enable_ai $AiTag"; Shot $p "01b_ai.png" }
# Ledgerdemain's EF* debug logs are off by default (game rule, R0.2 7.10): switch them on for the run (in a game
# without the fork the event is unknown -- a harmless console error)
# the bridge passes only -Commands: the word "nomodlogs" there does the same as -NoModLogs
if ($Commands -match '(^|;)\s*nomodlogs\s*(;|$)') { $NoModLogs = $true; $Commands = ($Commands -replace '(^|;)\s*nomodlogs\s*(?=;|$)', '') }
if (-not $NoModLogs) { Console-Cmd $p "event zz_ef_logs.1"; Start-Sleep 2 }
if ($Commands -match '(^|;)\s*minimized\s*(;|$)') { $Minimized = $true; $Commands = ($Commands -replace '(^|;)\s*minimized\s*(?=;|$)', '') }
# a command "ui:<step>" is a step of tools/vic3_ui.ps1 (key, click, hover, shot, wait ...), the rest -- console commands
# a command "end:<cmd>" is entered at the end of the run, after the pause (e.g. "end:Script.Profiling.Stop", 7.10)
$EndCommands = @()
foreach ($c in ($Commands -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ })) {
    if ($c.StartsWith("end:")) { $EndCommands += $c.Substring(4); continue }
    if ($c.StartsWith("ui:")) { & (Join-Path $PSScriptRoot "vic3_ui.ps1") -OutDir $OutDir -Do $c.Substring(3) }
    else { Console-Cmd $p $c; Start-Sleep 5; Log "console: $c" }
}

# speed 5, unpause; verify by the date on screen, toggle pause once more if it stands
Focus-Game $p
Send-Key 0x35 0x06
Send-Key 0x20 0x39
$ok = Is-Advancing $p 24
if (-not $ok) { Send-Key 0x20 0x39; $ok = Is-Advancing $p 24 }
Log ("advancing: " + $ok)
if (-not $ok) { Shot $p "02_not_running.png"; Log "the game does not advance - stopping"; }
else {
    Log "running for $RunMinutes min (autosaves wanted: $Autosaves)"
    # SW_MINIMIZE; Is-Advancing raises the window, so the date is not checked until the end
    if ($Minimized) { [W]::ShowWindow($p.MainWindowHandle, 6) | Out-Null; Log "the game window is minimized" }
    $since = Get-Date
    $autoSeen = New-Object 'System.Collections.Generic.HashSet[long]'
    $end = (Get-Date).AddMinutes($RunMinutes)
    while ((Get-Date) -lt $end) {
        # every 15 s: in run 12 several parts rotated within one minute and a
        # game year was lost
        for ($k = 0; $k -lt 4; $k++) { Start-Sleep 15; Save-DebugParts }
        if ($Autosaves -gt 0) {
            # Count distinct write times, not files: the game keeps five rotating
            # autosave files, so a file count never got past 5 (3.10, night G).
            Get-ChildItem (Join-Path $Docs "save games") -Filter "autosave*.v3" | Where-Object { $_.LastWriteTime -gt $since -and $_.Name -ne "autosave_exit.v3" } | ForEach-Object { [void]$autoSeen.Add($_.LastWriteTime.Ticks) }
            $n = $autoSeen.Count
            Log "new autosaves: $n"
            if ($n -ge $Autosaves) { Start-Sleep 20; break }
        }
        if (-not (Get-Game)) { Log "the game exited"; break }
        $p = Get-Game
        if ($Minimized) { Log "minimized"; continue }
        if (-not (Is-Advancing $p 16)) {
            Log "date stands - unpausing"
            Shot $p ("stall_" + (Get-Date -Format "HHmmss") + ".png")
            if (Is-Screen $p "console") { Log "the console is open"; Close-Console $p | Out-Null }
            Send-Key 0x20 0x39
            if (-not (Is-Advancing $p 16)) { Send-Key 0x20 0x39; Log "still standing after a toggle" }
        } else { Log "advancing" }
    }
    $p = Get-Game
    if ($p -and $Minimized) { [W]::ShowWindow($p.MainWindowHandle, 9) | Out-Null; Start-Sleep 3; Raise-Game $p | Out-Null; Log "the game window is restored" }
    if ($p) {
        # pause at once, even if the user is at the PC (the user, 5.10); the screens after it wait for the user
        Pause-Now $p; $script:WantPaused = $true; Start-Sleep 3; Shot $p "03_end.png"
        foreach ($c in $EndCommands) {
            if ($c.StartsWith("ui:")) { & (Join-Path $PSScriptRoot "vic3_ui.ps1") -OutDir $OutDir -Do $c.Substring(3) }
            else { Console-Cmd $p $c; Start-Sleep 10; Log "console (end): $c" }
        }
    }
}

if (($Shots -or $Countries) -and (Get-Game)) {
    # the night of 4.10 (D.3): tooltips and budget tabs of the played country and of big ones
    Set-Content (Join-Path $OutDir "t0.txt") $t0.ToString("o")
    # events and panels the AI or the console click left open covered the shots (r1005_102757, r1005_104528: an
    # event window over the cards) -- closed first, as after the user (Escape until the game menu, once more)
    Reset-UI (Get-Game); Shot (Get-Game) "03b_clean.png"
    $steps = @()
    if ($Shots) { $own = if ($NewGame) { $Tag } else { "own" }; $steps += "macro currency $own; macro cards $own; macro budget $own" }
    foreach ($c in ($Countries -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })) { $steps += "country $c" }
    Log "money screens: $($steps -join '; ')"
    try { & (Join-Path $PSScriptRoot "vic3_ui.ps1") -OutDir $OutDir -Do ($steps -join '; ') }
    catch { Log "money screens failed: $_" }
}
if ($KeepOpen -and (Get-Game)) {
    # the game stays paused for tools/vic3_ui.ps1 (tooltips, other countries); logs are
    # gathered when that script closes it ("close")
    Set-Content (Join-Path $OutDir "t0.txt") $t0.ToString("o")
    Log "kept open (paused)"
} else {
    Close-And-Collect
}
# -StartSave pointed "continue" at the copy; if the run made no autosave (a short run -- the game moves the pointer
# itself on an autosave) the pointer still names the copy and the user's "Continue" (and the next run without
# -StartSave) would open it: r1005_105248 continued the copy into the lobby. Put the previous save back.
if ($StartSave -and -not $KeepOpen) {
    $j = Get-Content $cg -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($j.title -eq "sandbox_start") {
        $j.title = $prevTitle
        [IO.File]::WriteAllText($cg, ($j | ConvertTo-Json), (New-Object Text.UTF8Encoding $false))
        Log "continue_game.json: back to '$prevTitle' (the run made no autosave)"
    }
}
if ($Playset -and (Test-Path $ContentBackup)) {
    Copy-Item $ContentBackup $ContentLoad -Force
    Log "content_load.json: back to the launcher's mods"
}
Log "done: $OutDir"
