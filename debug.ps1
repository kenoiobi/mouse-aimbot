# kill-mouse — debug run (snap + on-screen detection overlays)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. "$PSScriptRoot\_uv.ps1"

Write-Host "Starting kill-mouse (debug overlay). Force quit: Ctrl+Alt+Q"
& $uv run python -m kill_mouse @args
