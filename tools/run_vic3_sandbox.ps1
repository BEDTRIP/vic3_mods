<#
Sandbox run of Victoria 3 for the agent (EF.48, 2026-10-01).

Launches the game with the last save (-continuelastsave -debug_mode), waits for
it to load, sets speed 5 and unpauses, lets it run, pauses, takes a screenshot
of the game window, closes the game and collects the logs. The weekly money
model writes one line a week per big economy into debug.log (EFW = the step,
EFR = the GUI bridge's receiver, scripted_effects/zz_ef_money_model.txt);
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
    -LoadWaitSec  seconds to wait after the window appears, for the save to load (default 150)
    -Autosaves    stop as soon as this many new autosaves are written (0 = run -RunMinutes);
                  -RunMinutes stays the limit. Autosaves are half-yearly in this setup, so
                  the state to read from the save needs the run to pass 1 Jan / 1 Jul.
    -OutDir       where to put logs and screenshots (default: %TEMP%\vic3_sandbox\<timestamp>)
#>
param(
    [int]$RunMinutes = 5,
    [int]$LoadWaitSec = 150,
    [int]$Autosaves = 0,
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
}
"@

function Log($m) { $l = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m; Write-Host $l; Add-Content (Join-Path $OutDir "run.log") $l }

function Get-Game { Get-Process -Name "victoria3" -ErrorAction SilentlyContinue | Select-Object -First 1 }

function Focus-Game($p) {
    [W]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
    [W]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
    Start-Sleep -Milliseconds 400
}

# vk + scan code (DirectInput reads scan codes): Space 0x20/0x39, '5' 0x35/0x06
function Send-Key([byte]$vk, [byte]$scan) {
    [W]::keybd_event($vk, $scan, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [W]::keybd_event($vk, $scan, 2, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 200
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

Log "launching $Exe -continuelastsave -debug_mode"
Start-Process -FilePath $Exe -ArgumentList "-continuelastsave", "-debug_mode" -WorkingDirectory (Split-Path $Exe)

$t0 = Get-Date
$p = $null
while (((Get-Date) - $t0).TotalSeconds -lt 240) {
    $p = Get-Game
    if ($p -and $p.MainWindowHandle -ne 0) { break }
    Start-Sleep 3
}
if (-not $p -or $p.MainWindowHandle -eq 0) { throw "no game window after 4 minutes" }
Log "window up, waiting $LoadWaitSec s for the save to load"
Start-Sleep $LoadWaitSec
$p = Get-Game
Shot $p "01_loaded.png"

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
    $end = (Get-Date).AddMinutes($RunMinutes)
    while ((Get-Date) -lt $end) {
        Start-Sleep 60
        if ($Autosaves -gt 0) {
            $n = @(Get-ChildItem (Join-Path $Docs "save games") -Filter "autosave*.v3" | Where-Object { $_.LastWriteTime -gt $since }).Count
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
    if ($p) { Focus-Game $p; Send-Key 0x20 0x39; Start-Sleep 3; Shot $p "03_end.png" }
}

$p = Get-Game
if ($p) {
    Log "closing the game"
    $p.CloseMainWindow() | Out-Null
    if (-not $p.WaitForExit(30000)) { Log "force stop"; Stop-Process -Id $p.Id -Force }
}
Start-Sleep 2
foreach ($f in "debug.log", "error.log", "game.log") {
    $src = Join-Path $Logs $f
    if (Test-Path $src) { Copy-Item $src (Join-Path $OutDir $f) }
}
$d = Join-Path $OutDir "debug.log"
if (Test-Path $d) {
    Select-String -Path $d -Pattern "EFW|", "EFR|" -SimpleMatch | ForEach-Object { $_.Line -replace "^.*?(EF[WR]\|)", '$1' } |
        Set-Content -Encoding utf8 (Join-Path $OutDir "eflog.txt")
}
Log "done: $OutDir"
