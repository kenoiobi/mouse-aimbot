# mouse-aimbot — normal run (snap only, no debug overlay)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. "$PSScriptRoot\_uv.ps1"

Write-Host "Starting mouse-aimbot (no overlay). Force quit: Ctrl+Alt+Q"
& $uv run python -m mouse_aimbot --no-overlay @args
