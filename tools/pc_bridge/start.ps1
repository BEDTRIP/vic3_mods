<#
The PC bridge vic3-pc of this project: vic3_tools/bridge/pc/start.ps1 with bridge.toml of this repo.
    powershell -ExecutionPolicy Bypass -File tools\pc_bridge\start.ps1        (runs on this screen)
    powershell -ExecutionPolicy Bypass -File tools\pc_bridge\start.ps1 -Vm    (runs in the sandbox VM)
#>
param([switch]$Vm)
$repo = Split-Path (Split-Path $PSScriptRoot)
& (Join-Path (Split-Path $repo) "vic3_tools\bridge\pc\start.ps1") -Config (Join-Path $repo "bridge.toml") -Vm:$Vm
