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
    -Commands     extra console commands after loading, ';'-separated (e.g. "dump_data_types"); their
                  output files in logs/ are copied with the other logs
    -AiTag        console "enable_ai <tag>" after loading, so the AI plays the player's country
                  too (default "all"; "" to skip)
    -StartSave    start from this save instead of the last one: a file name in "save games" (e.g.
                  sandbox_1836.v3). It is copied to sandbox_start.v3 and continue_game.json is pointed at
                  the copy, so the original is never written to; later runs without -StartSave go on
                  from the run's own autosaves.
    -NewGame      start a new game from 1836 instead of a save (start conditions, history files):
                  main menu -> New game -> Sandbox -> Random country -> Start, then the console
                  "tag <Tag>". Clicks are at fractions of the window, measured on 2560x1440 (16:9).
    -Tag          the country to play in a new game (default GBR)
    -NoDumps      kept for old command lines; does nothing (1.10 night: debugcountrybudgets and
                  debugmarkets are strings in victoria3.exe, but the release console answers
                  "Unknown command" -- developer-build commands)
    -OutDir       where to put logs and screenshots (default: %TEMP%\vic3_sandbox\<timestamp>)
#>
param(
    [int]$RunMinutes = 5,
    [int]$LoadWaitSec = 400,
    [int]$Autosaves = 0,
    [string]$AiTag = "all",
    [string]$Commands = "",
    [string]$StartSave = "",
    [switch]$NewGame,
    [string]$Tag = "BUG",
    [switch]$NoDumps,
    [string]$OutDir = ""
)

$ErrorActionPreference = "Stop"
$Exe = "C:\games\steam\steamapps\common\Victoria 3\binaries\victoria3.exe"
$Docs = Join-Path $env:USERPROFILE "Documents\Paradox Interactive\Victoria 3"
$Logs = Join-Path $Docs "logs"
if (-not $OutDir) { $OutDir = Join-Path $env:TEMP ("vic3_sandbox\" + (Get-Date -Format "yyyyMMdd_HHmmss")) }
New-Item -ItemType Directory -Force $OutDir | Out-Null

Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class W {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [StructLayout(LayoutKind.Sequential)] public struct KEYBDINPUT { public ushort wVk, wScan; public uint dwFlags, time; public IntPtr extra; }
    [StructLayout(LayoutKind.Explicit, Size = 40)] public struct INPUT { [FieldOffset(0)] public uint type; [FieldOffset(8)] public KEYBDINPUT ki; }
    [DllImport("user32.dll")] public static extern uint SendInput(uint n, INPUT[] inputs, int size);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, UIntPtr e);
    // Types text as Unicode characters (WM_CHAR), whatever the keyboard layout.
    public static void TypeText(string s) {
        foreach (char c in s) {
            INPUT[] a = new INPUT[2];
            a[0].type = 1; a[0].ki.wScan = c; a[0].ki.dwFlags = 4;
            a[1].type = 1; a[1].ki.wScan = c; a[1].ki.dwFlags = 4 | 2;
            SendInput(2, a, Marshal.SizeOf(typeof(INPUT)));
            System.Threading.Thread.Sleep(15);
        }
    }
}
"@

function Log($m) { $l = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m; Write-Host $l; Add-Content (Join-Path $OutDir "run.log") $l }

# The engine keeps only debug.1..5.log (~2.5 MB, about 2 game years of the
# weekly lines): a run of 33 min lost 1836-1837 (run 10, 1.10). A rotated part
# keeps its write time when renamed, so it is saved once under that time.
function Save-DebugParts {
    $dir = Join-Path $OutDir "dbgparts"
    New-Item -ItemType Directory -Force $dir | Out-Null
    Get-ChildItem $Logs -Filter "debug.*.log" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $t0 } | ForEach-Object {
        $dst = Join-Path $dir ("{0}.log" -f $_.LastWriteTime.Ticks)
        if (-not (Test-Path $dst)) { Copy-Item $_.FullName $dst -ErrorAction SilentlyContinue }
    }
}

function Get-Game { Get-Process -Name "victoria3" -ErrorAction SilentlyContinue | Select-Object -First 1 }

# Keys and clicks go to whatever window has the focus. Windows may refuse to
# bring the game forward (the user is working in another window): then every
# key would land in the user's window (1.10 morning: "enable_ai all" was typed
# into the user's chat). So nothing is sent unless the game is in front; if
# it cannot be brought forward the run stops.
function Focus-Game($p) {
    [W]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
    [W]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
    Start-Sleep -Milliseconds 400
    if ([W]::GetForegroundWindow() -ne $p.MainWindowHandle) {
        # the ALT trick: a key event lets this process take the foreground
        [W]::keybd_event(0x12, 0x38, 0, [UIntPtr]::Zero); [W]::keybd_event(0x12, 0x38, 2, [UIntPtr]::Zero)
        [W]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
        Start-Sleep -Milliseconds 400
    }
    if ([W]::GetForegroundWindow() -ne $p.MainWindowHandle) {
        Log "the game is not in front (another window has the focus) - stopping, nothing sent"
        throw "game window not in front"
    }
}

function Assert-Front($p) {
    if ([W]::GetForegroundWindow() -ne $p.MainWindowHandle) { Focus-Game $p }
}

# vk + scan code (DirectInput reads scan codes): Space 0x20/0x39, '5' 0x35/0x06
function Send-Key([byte]$vk, [byte]$scan) {
    Assert-Front (Get-Game)
    [W]::keybd_event($vk, $scan, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [W]::keybd_event($vk, $scan, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 200
}

# Left click at a point of the window (fraction of its size).
function Click-Window($p, $fx, $fy) {
    $r = New-Object W+RECT
    [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    Assert-Front $p
    [W]::SetCursorPos([int]($r.L + ($r.R - $r.L) * $fx), [int]($r.T + ($r.B - $r.T) * $fy)) | Out-Null
    Start-Sleep -Milliseconds 150
    [W]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 60
    [W]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 300
}

# Console (debug_mode): the key left of 1 (VK_OEM_3, scan 0x29), clear the line
# (if the console was still open the key typed a character into it), type,
# Enter. Closing: while the input line has the focus neither Escape nor the
# console key close it (run 2: a stray "ё"; run 3, 1.10: the console stayed
# open and the speed key "5" went into it, the game never ran). So a click on
# the map takes the focus off the line, then the console key closes it.
function Console-Cmd($p, $cmd) {
    Focus-Game $p
    Send-Key 0xC0 0x29
    Start-Sleep -Milliseconds 500
    for ($i = 0; $i -lt 3; $i++) { Send-Key 0x08 0x0E }
    Assert-Front $p
    [W]::TypeText($cmd)
    Start-Sleep -Milliseconds 200
    Send-Key 0x0D 0x1C
    Start-Sleep -Milliseconds 800
    Click-Window $p 0.62 0.45
    Send-Key 0xC0 0x29
    Start-Sleep -Milliseconds 400
    Log "console: $cmd"
}

function Shot($p, $name) {
    $r = New-Object W+RECT
    [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    $w = $r.R - $r.L; $h = $r.B - $r.T
    if ($w -le 0 -or $h -le 0) { return }
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size)
    $f = Join-Path $OutDir $name
    $bmp.Save($f); $g.Dispose(); $bmp.Dispose()
    Log "screenshot $f"
}

# Which screen is up, from the mean colour of a box (2560x1440 coordinates, scaled to the
# window). Measured 2026-10-01 on the screenshots of runs 14-15: the main menu's "New game"
# button is dark green, the goals screen's top-left corner near black, the lobby's ocean light,
# and in a loaded game the left column of icons is (76,68,68) for every country (the top-left
# corner is the flag, different per country).
$Screens = @{
    menu  = @{ box = @(340, 545, 730, 590); rgb = @(33, 46, 42); tol = 15 }
    goals = @{ box = @(5, 5, 130, 90); rgb = @(33, 31, 32); tol = 15 }
    # the lobby: the dark right panel AND the grey "Start" button -- run 17 (1.10 night) took a
    # loading screen's light stadium for the lobby's sea and clicked into the void
    lobby = @{ box = @(2200, 300, 2540, 900); rgb = @(47, 52, 49); tol = 15; box2 = @(2180, 1395, 2540, 1430); rgb2 = @(53, 53, 53); tol2 = 15 }
    game  = @{ box = @(5, 210, 45, 980); rgb = @(76, 68, 68); tol = 15 }
}
function Is-Screen($p, $name) {
    $sc = $Screens[$name]
    if (-not (Is-Box $p $sc.box $sc.rgb $sc.tol)) { return $false }
    if ($sc.box2) { return (Is-Box $p $sc.box2 $sc.rgb2 $sc.tol2) }
    return $true
}
function Is-Box($p, $box, $rgb, $tol) {
    $sc = @{ box = $box; rgb = $rgb; tol = $tol }
    $r = New-Object W+RECT
    [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    $kx = ($r.R - $r.L) / 2560.0; $ky = ($r.B - $r.T) / 1440.0
    $x0 = [int]($sc.box[0] * $kx); $y0 = [int]($sc.box[1] * $ky)
    $w = [Math]::Max(1, [int](($sc.box[2] - $sc.box[0]) * $kx)); $h = [Math]::Max(1, [int](($sc.box[3] - $sc.box[1]) * $ky))
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.L + $x0, $r.T + $y0, 0, 0, $bmp.Size)
    $sum = @(0, 0, 0); $n = 0
    for ($x = 0; $x -lt $w; $x += 3) { for ($y = 0; $y -lt $h; $y += 3) { $c = $bmp.GetPixel($x, $y); $sum[0] += $c.R; $sum[1] += $c.G; $sum[2] += $c.B; $n++ } }
    $g.Dispose(); $bmp.Dispose()
    for ($i = 0; $i -lt 3; $i++) { if ([Math]::Abs($sum[$i] / $n - $sc.rgb[$i]) -gt $sc.tol) { return $false } }
    return $true
}
# Waits until the screen is up (polled every 3 s), at most $max seconds; then $settle seconds.
function Wait-Screen($name, $max, $settle) {
    $t = Get-Date
    while (((Get-Date) - $t).TotalSeconds -lt $max) {
        $p = Get-Game
        if ($p -and $p.MainWindowHandle -ne 0 -and (Is-Screen $p $name)) {
            Log ("screen '$name' after {0:N0} s" -f ((Get-Date) - $t).TotalSeconds); Start-Sleep $settle; return $true
        }
        Start-Sleep 3
    }
    Log "screen '$name' not seen in $max s - going on"
    return $false
}

# debug.log is buffered while the game runs and autosaves may be half-yearly,
# so progress is read from the screen: the date text at the top right of the
# window (2560x1440: about 330..190 px from the right edge, 2..34 px down).
function Date-Crop($p) {
    $r = New-Object W+RECT
    [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    $bmp = New-Object System.Drawing.Bitmap 160, 32
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.R - 340, $r.T + 2, 0, 0, $bmp.Size)
    $ms = New-Object System.IO.MemoryStream
    $bmp.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
    [Convert]::ToBase64String($ms.ToArray())
}

# True if the date on screen changes within $sec seconds.
function Is-Advancing($p, $sec) {
    Focus-Game $p
    $a = Date-Crop $p
    for ($i = 0; $i -lt $sec; $i += 4) { Start-Sleep 4; if ((Date-Crop $p) -ne $a) { return $true } }
    return $false
}

if (Get-Game) { throw "Victoria 3 is already running - close it first." }

# -continuelastsave loads the save named by "title" in continue_game.json.
if ($StartSave) {
    $Saves = Join-Path $Docs "save games"
    $src = Join-Path $Saves $StartSave
    if (-not (Test-Path $src)) { throw "no save $src" }
    Copy-Item $src (Join-Path $Saves "sandbox_start.v3") -Force
    $cg = Join-Path $Docs "continue_game.json"
    $j = Get-Content $cg -Raw -Encoding UTF8 | ConvertFrom-Json
    $j.title = "sandbox_start"
    [IO.File]::WriteAllText($cg, ($j | ConvertTo-Json), (New-Object Text.UTF8Encoding $false))
    Log "start save: $StartSave (copied to sandbox_start.v3)"
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
    Wait-Screen "game" $LoadWaitSec 8 | Out-Null
}
$p = Get-Game
Shot $p "01_loaded.png"
if ($AiTag) { Console-Cmd $p "enable_ai $AiTag"; Shot $p "01b_ai.png" }
foreach ($c in ($Commands -split ';' | Where-Object { $_.Trim() })) { Console-Cmd $p $c.Trim(); Start-Sleep 5; Log "console: $($c.Trim())" }

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
        if (-not (Is-Advancing $p 16)) {
            Log "date stands - unpausing"
            Shot $p ("stall_" + (Get-Date -Format "HHmmss") + ".png")
            Send-Key 0x20 0x39
            if (-not (Is-Advancing $p 16)) { Send-Key 0x20 0x39; Log "still standing after a toggle" }
        } else { Log "advancing" }
    }
    $p = Get-Game
    if ($p) {
        Focus-Game $p; Send-Key 0x20 0x39; Start-Sleep 3; Shot $p "03_end.png"
    }
}

$p = Get-Game
if ($p) {
    Log "closing the game"
    $p.CloseMainWindow() | Out-Null
    if (-not $p.WaitForExit(30000)) { Log "force stop"; Stop-Process -Id $p.Id -Force }
}
Start-Sleep 2
# every log written during the run (debug/error/game.log, the console dumps)
Get-ChildItem $Logs -File | Where-Object { $_.LastWriteTime -gt $t0 } | ForEach-Object { Copy-Item $_.FullName (Join-Path $OutDir $_.Name) }
# debug.log rotates at ~512 KB and keeps only debug.1..5.log: the parts saved
# during the run (dbgparts) + the last ones, oldest first, each line once.
Save-DebugParts
$parts = @(Get-ChildItem (Join-Path $OutDir "dbgparts") -Filter "*.log" -ErrorAction SilentlyContinue | Sort-Object Name) +
    @(Get-ChildItem $OutDir -Filter "debug.log")
if ($parts) {
    $seen = New-Object 'System.Collections.Generic.HashSet[string]'
    Select-String -Path ($parts | ForEach-Object FullName) -Pattern "EFW|", "EFR|", "EFX|", "EFC|", "EFM|", "EFJ|", "EFO|" -SimpleMatch |
        ForEach-Object { $_.Line -replace "^.*?(EF[WRXCMJO]\|)", '$1' } |
        Where-Object { $seen.Add($_) } |
        Set-Content -Encoding utf8 (Join-Path $OutDir "eflog.txt")
}
Log "done: $OutDir"
