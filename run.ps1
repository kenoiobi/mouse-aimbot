# kill-mouse — normal run (snap only, no debug overlay)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
. "$PSScriptRoot\_uv.ps1"

Write-Host "Starting kill-mouse (no overlay). Force quit: Ctrl+Alt+Q"
& $uv run python -m kill_mouse --no-overlay @args
