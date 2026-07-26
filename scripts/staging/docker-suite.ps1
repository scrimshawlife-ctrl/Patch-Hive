# Full local Docker staging suite:
#   1) smoke (up/rebuild, /health/ready, alembic head, backup/restore, F2 probe)
#   2) acceptance entirely in Docker network
#   3) Design Engine walkthrough (overlay flags + export)
#
# Usage (repo root):
#   powershell -File scripts/staging/docker-suite.ps1
#   powershell -File scripts/staging/docker-suite.ps1 -SkipBuild
#   powershell -File scripts/staging/docker-suite.ps1 -SkipDesignEngine

param(
    [int]$ApiPort = 18000,
    [int]$FePort = 15173,
    [int]$DbPort = 5433,
    [switch]$SkipBuild,
    [switch]$SkipDesignEngine,
    [switch]$SkipAcceptance
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$env:STAGING_API_PORT = "$ApiPort"
$env:STAGING_FE_PORT = "$FePort"
$env:STAGING_DB_PORT = "$DbPort"
$env:STAGING_PUBLIC_API_URL = "http://localhost:$ApiPort"
$env:STAGING_CORS_ORIGINS = "http://localhost:$FePort,http://localhost:5173,http://localhost:3000"
if (-not $env:STAGING_SECRET_KEY) {
    $env:STAGING_SECRET_KEY = "staging-smoke-secret-key-min-32-chars-xx"
}
if (-not $env:STAGING_DB_PASSWORD) {
    $env:STAGING_DB_PASSWORD = "staging-smoke-db-pass-xx"
}

Write-Host "========================================"
Write-Host " Docker staging suite"
Write-Host " API :$ApiPort  FE :$FePort  DB :$DbPort"
Write-Host "========================================"

$smokeArgs = @(
    "-NoProfile", "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $RepoRoot "scripts\staging\smoke.ps1"),
    "-ApiPort", "$ApiPort",
    "-FePort", "$FePort",
    "-DbPort", "$DbPort"
)
if ($SkipBuild) { $smokeArgs += "-SkipBuild" }

Write-Host "`n--- [1/3] smoke ---"
& powershell @smokeArgs
if ($LASTEXITCODE -ne 0) { throw "smoke failed ($LASTEXITCODE)" }

if (-not $SkipAcceptance) {
    Write-Host "`n--- [2/3] acceptance (docker network) ---"
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\staging\acceptance-docker.ps1")
    if ($LASTEXITCODE -ne 0) { throw "acceptance-docker failed ($LASTEXITCODE)" }
} else {
    Write-Host "`n--- [2/3] acceptance SKIPPED ---"
}

if (-not $SkipDesignEngine) {
    Write-Host "`n--- [3/3] design-engine ---"
    $deArgs = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", (Join-Path $RepoRoot "scripts\staging\design-engine.ps1"),
        "-ApiPort", "$ApiPort",
        "-FePort", "$FePort",
        "-DbPort", "$DbPort"
    )
    if ($SkipBuild) { $deArgs += "-SkipRebuild" }
    & powershell @deArgs
    if ($LASTEXITCODE -ne 0) { throw "design-engine failed ($LASTEXITCODE)" }
} else {
    Write-Host "`n--- [3/3] design-engine SKIPPED ---"
}

Write-Host ""
Write-Host "DOCKER STAGING SUITE PASS"
Write-Host "  API:  http://localhost:$ApiPort/health/ready"
Write-Host "  FE:   http://localhost:$FePort"
Write-Host "  Payments fail-closed."
