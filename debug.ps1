# mouse-aimbot — debug run (snap + on-screen detection overlays)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. "$PSScriptRoot\_uv.ps1"

Write-Host "Starting mouse-aimbot (debug overlay). Force quit: Ctrl+Alt+Q"
& $uv run python -m mouse_aimbot @args
