<#
Shared helpers of the Victoria 3 sandbox scripts (run_vic3_sandbox.ps1, vic3_ui.ps1):
window focus, keys, clicks and hovers at window fractions, console commands, screenshots,
screen recognition by colour. Dot-source it; the caller sets $OutDir (and $Logs, $t0 for
Save-DebugParts).
#>
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
    # error.log rotates too (~0.5 MB a part): in a 3-minute run (4.10) the load errors were gone
    # before the game ran -- its parts go to errparts the same way
    foreach ($kind in @("debug", "error")) {
        $dir = Join-Path $OutDir ($(if ($kind -eq "debug") { "dbgparts" } else { "errparts" }))
        New-Item -ItemType Directory -Force $dir | Out-Null
        Get-ChildItem $Logs -Filter "$kind.*.log" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $t0 } | ForEach-Object {
            $dst = Join-Path $dir ("{0}.log" -f $_.LastWriteTime.Ticks)
            if (-not (Test-Path $dst)) { Copy-Item $_.FullName $dst -ErrorAction SilentlyContinue }
        }
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
# console key close it (run 2: a stray character; run 3, 1.10: the console stayed
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
    # the column's skin depends on the country's interface style: (76, 68, 68) for most, (92, 84, 65) for
    # Croatia -- Austria's style (4.10, the user; a new game waited the full 400 s) -- tolerance 25
    game  = @{ box = @(5, 210, 45, 980); rgb = @(76, 68, 68); tol = 25 }
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
        if ($t0) { Save-DebugParts }
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

# Moves the mouse to a point of the window (fraction of its size) without clicking: tooltips.
function Hover-Window($p, $fx, $fy) {
    $r = New-Object W+RECT
    [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    Assert-Front $p
    [W]::SetCursorPos([int]($r.L + ($r.R - $r.L) * $fx), [int]($r.T + ($r.B - $r.T) * $fy)) | Out-Null
}

# Closes the game and gathers the logs written since $t0 into $OutDir: every log file, the
# rotated debug parts, and the money model's lines (EFW|, EFR| ...) into eflog.txt.
function Close-And-Collect {
    $p = Get-Game
    if ($p) {
        Log "closing the game"
        $p.CloseMainWindow() | Out-Null
        if (-not $p.WaitForExit(30000)) { Log "force stop"; Stop-Process -Id $p.Id -Force }
    }
    Start-Sleep 2
    Get-ChildItem $Logs -File | Where-Object { $_.LastWriteTime -gt $t0 } | ForEach-Object { Copy-Item $_.FullName (Join-Path $OutDir $_.Name) }
    # debug.log rotates at ~512 KB and keeps only debug.1..5.log: the parts saved
    # during the run (dbgparts) + the last ones, oldest first, each line once.
    Save-DebugParts
    $parts = @(Get-ChildItem (Join-Path $OutDir "dbgparts") -Filter "*.log" -ErrorAction SilentlyContinue | Sort-Object Name) +
        @(Get-ChildItem $OutDir -Filter "debug.log")
    if ($parts) {
        $seen = New-Object 'System.Collections.Generic.HashSet[string]'
        Select-String -Path ($parts | ForEach-Object FullName) -Pattern "EFW|", "EFR|", "EFX|", "EFC|", "EFM|", "EFJ|", "EFO|", "EFF|", "EFD|" -SimpleMatch |
            ForEach-Object { $_.Line -replace "^.*?(EF[WRXCMJOFD]\|)", '$1' } |
            Where-Object { $seen.Add($_) } |
            Set-Content -Encoding utf8 (Join-Path $OutDir "eflog.txt")
    }
}

# Mouse wheel at a point of the window: $notches > 0 up, < 0 down (120 per notch).
function Scroll-Window($p, $fx, $fy, $notches) {
    Hover-Window $p $fx $fy
    Start-Sleep -Milliseconds 150
    $n = [Math]::Abs([int]$notches); $d = if ($notches -lt 0) { -120 } else { 120 }
    for ($i = 0; $i -lt $n; $i++) { [W]::mouse_event(0x0800, 0, 0, [BitConverter]::ToUInt32([BitConverter]::GetBytes([int32]$d), 0), [UIntPtr]::Zero); Start-Sleep -Milliseconds 80 }
    Start-Sleep -Milliseconds 400
}

# П.15 (4.10, the user: "the script must be able to see everything"): the collapsed section headers of a
# panel ("› Показать список", "› Займы"): a gold chevron at the panel's left edge. Collapsed "›" is taller than
# wide, expanded "⌄" wider than tall. Returns the window-fraction y of each collapsed chevron, top down.
# $x0..$x1, $y0..$y1 -- pixels of a 2560x1440 window (scaled to the real size).
function Find-Collapsed($p, $x0, $x1, $y0, $y1) {
    $r = New-Object W+RECT
    [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    $kx = ($r.R - $r.L) / 2560.0; $ky = ($r.B - $r.T) / 1440.0
    $w = [int](($x1 - $x0) * $kx); $h = [int](($y1 - $y0) * $ky)
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.L + [int]($x0 * $kx), $r.T + [int]($y0 * $ky), 0, 0, $bmp.Size)
    $rows = @{}
    for ($y = 0; $y -lt $h; $y++) {
        for ($x = 0; $x -lt $w; $x++) {
            $c = $bmp.GetPixel($x, $y)
            if ($c.R -gt 150 -and $c.G -gt 100 -and ($c.R - $c.B) -gt 70) {
                if (-not $rows.ContainsKey($y)) { $rows[$y] = @($x, $x, 1) }
                else { $rows[$y] = @([Math]::Min($rows[$y][0], $x), [Math]::Max($rows[$y][1], $x), ($rows[$y][2] + 1)) }
            }
        }
    }
    $g.Dispose(); $bmp.Dispose()
    # clusters of consecutive rows
    $out = @(); $ys = $rows.Keys | Sort-Object
    # "›" (4.10, Britain's budget): 18 px tall, 11 wide, a thin stroke (~1/3 of its box); "⌄" 17 wide, 12 tall;
    # a flag in a table is a filled block
    $start = $null; $prev = $null; $minx = 9999; $maxx = -1; $cnt = 0
    foreach ($y in ($ys + @(99999))) {
        if ($null -ne $prev -and $y -gt $prev + 2) {
            $hh = ($prev - $start + 1) / $ky; $ww = ($maxx - $minx + 1) / $kx; $fill = $cnt / [double](($prev - $start + 1) * ($maxx - $minx + 1))
            # the shape of ">": the middle rows reach further right than the top and the bottom ones (the orange
            # first letters of table cells -- "С", "М", "Д" -- passed the size test, 4.10)
            $n3 = [Math]::Max(1, [int](($prev - $start + 1) / 4))
            $cx = { param($a, $b) $v = @(); for ($q = $a; $q -le $b; $q++) { if ($rows.ContainsKey($q)) { $v += ($rows[$q][0] + $rows[$q][1]) / 2.0 } }; if ($v.Count) { ($v | Measure-Object -Average).Average } else { 0 } }
            $ct = & $cx $start ($start + $n3 - 1); $cb = & $cx ($prev - $n3 + 1) $prev
            $mid = [int](($start + $prev) / 2); $cm = & $cx ($mid - 1) ($mid + 1)
            $arrow = ($cm -gt $ct + 2 * $kx) -and ($cm -gt $cb + 2 * $kx)
            if ($arrow -and $hh -ge 12 -and $hh -le 28 -and $ww -ge 5 -and $ww -le 18 -and $hh -gt 1.3 * $ww -and $fill -lt 0.55) {
                $out += (($y0 + ($start + $prev) / 2.0 / $ky) / 1440.0)
            }
            $start = $null; $minx = 9999; $maxx = -1; $cnt = 0
        }
        if ($y -eq 99999) { break }
        if ($null -eq $start) { $start = $y }
        $minx = [Math]::Min($minx, $rows[$y][0]); $maxx = [Math]::Max($maxx, $rows[$y][1]); $cnt += $rows[$y][2]; $prev = $y
    }
    return $out
}

# П.15: a cheap signature of a screen region (the panel), to tell when scrolling stopped moving it.
function Region-Sig($p, $x0, $x1, $y0, $y1) {
    $r = New-Object W+RECT
    [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    $kx = ($r.R - $r.L) / 2560.0; $ky = ($r.B - $r.T) / 1440.0
    $w = [int](($x1 - $x0) * $kx); $h = [int](($y1 - $y0) * $ky)
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.L + [int]($x0 * $kx), $r.T + [int]($y0 * $ky), 0, 0, $bmp.Size)
    $sb = New-Object System.Text.StringBuilder
    for ($y = 0; $y -lt $h; $y += 23) { for ($x = 0; $x -lt $w; $x += 29) { $c = $bmp.GetPixel($x, $y); [void]$sb.Append([int](($c.R + $c.G + $c.B) / 24)) } }
    $g.Dispose(); $bmp.Dispose()
    return $sb.ToString()
}

# П.15: the panel's scrollbar thumb (teal, x ~608 px of 2560 for the left panels). Returns @(top, bottom) in
# window fractions, or $null.
function Find-Thumb($p, $xpx, $y0, $y1) {
    $r = New-Object W+RECT
    [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    $kx = ($r.R - $r.L) / 2560.0; $ky = ($r.B - $r.T) / 1440.0
    $h = [int](($y1 - $y0) * $ky)
    $bmp = New-Object System.Drawing.Bitmap 5, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.L + [int](($xpx - 2) * $kx), $r.T + [int]($y0 * $ky), 0, 0, $bmp.Size)
    $top = -1; $bot = -1
    for ($y = 0; $y -lt $h; $y++) {
        $c = $bmp.GetPixel(2, $y)
        if ($c.G -gt $c.R + 15 -and $c.B -gt $c.R + 10 -and $c.G -gt 70) { if ($top -lt 0) { $top = $y }; $bot = $y }
    }
    $g.Dispose(); $bmp.Dispose()
    if ($top -lt 0) { return $null }
    return @((($y0 + $top / $ky) / 1440.0), (($y0 + $bot / $ky) / 1440.0))
}
# Drag with the left button from one point to another (window fractions), in small steps.
function Drag-Window($p, $fx, $fy, $tx, $ty) {
    $r = New-Object W+RECT
    [W]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
    Assert-Front $p
    $W = $r.R - $r.L; $H = $r.B - $r.T
    [W]::SetCursorPos([int]($r.L + $W * $fx), [int]($r.T + $H * $fy)) | Out-Null; Start-Sleep -Milliseconds 150
    [W]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 100
    for ($i = 1; $i -le 10; $i++) {
        $x = $fx + ($tx - $fx) * $i / 10; $y = $fy + ($ty - $fy) * $i / 10
        [W]::SetCursorPos([int]($r.L + $W * $x), [int]($r.T + $H * $y)) | Out-Null; Start-Sleep -Milliseconds 30
    }
    Start-Sleep -Milliseconds 100
    [W]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 300
}
