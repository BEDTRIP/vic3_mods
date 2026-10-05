<#
Starts the PC bridge for a Claude Code cloud session (5.10.2026): the ngrok tunnel in its own
window and the MCP server (tools/pc_bridge/server.py) in this one. Ctrl+C here stops the server;
close the ngrok window to cut the tunnel.

Run from the user's desktop session (not a service, not over RDP): the game script needs the screen.
    powershell -ExecutionPolicy Bypass -File tools\pc_bridge\start.ps1
First time: creates the venv _bridge\venv (mcp<2, pillow, uvicorn) and the token _bridge\token.txt.
#>
param(
    [string]$Domain = "untimed-diploma-creation.ngrok-free.dev",
    [int]$Port = 8080
)
$ErrorActionPreference = "Stop"
$repo = Split-Path (Split-Path $PSScriptRoot)
$bridge = Join-Path (Split-Path $repo) "_bridge"
$py = Join-Path $bridge "venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    New-Item -ItemType Directory -Force $bridge | Out-Null
    python -m venv (Join-Path $bridge "venv")
    & $py -m pip install --quiet "mcp<2" pillow uvicorn
}
if (-not (Get-Process ngrok -ErrorAction SilentlyContinue)) {
    Start-Process ngrok -ArgumentList "http", "--url=$Domain", "$Port"
}
$env:PC_BRIDGE_PORT = "$Port"
Write-Host "bridge: https://$Domain/mcp -> 127.0.0.1:$Port; token in $bridge\token.txt"
foreach ($d in "vic3_mods_out", "_tmp_analysis") {
    $link = Join-Path $bridge $d; $target = Join-Path (Split-Path $repo) $d
    if ((Test-Path $target) -and -not (Test-Path $link)) { New-Item -ItemType Junction -Path $link -Target $target | Out-Null }
}
& $py (Join-Path $PSScriptRoot "server.py")
