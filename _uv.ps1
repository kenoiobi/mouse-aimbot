# Shared uv bootstrap — dot-source from run.ps1 / debug.ps1
# Sets $uv in the caller's scope.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Find-Uv {
    $cmd = Get-Command uv -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $candidates = @(
        "$env:USERPROFILE\.local\bin\uv.exe",
        "$env:USERPROFILE\.cargo\bin\uv.exe",
        "$env:LOCALAPPDATA\Programs\uv\uv.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

$uv = Find-Uv
if (-not $uv) {
    Write-Host "uv not found. Installing..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:USERPROFILE\.cargo\bin;$env:Path"
    $uv = Find-Uv
    if (-not $uv) {
        Write-Error "uv install failed. Install from https://docs.astral.sh/uv/ and retry."
    }
}

Write-Host "Syncing environment with uv..."
& $uv sync | Out-Host
if ($LASTEXITCODE -ne 0) { throw "uv sync failed ($LASTEXITCODE)" }
