# Design Engine staging enablement walkthrough (local compose).
# Turns on design flags via compose overlay, seeds golden demo, runs API preview+export.
#
# Usage (repo root):
#   powershell -File scripts/staging/design-engine.ps1
#   powershell -File scripts/staging/design-engine.ps1 -ApiPort 18000 -DbPort 5433

param(
    [int]$ApiPort = 18000,
    [int]$FePort = 15173,
    [int]$DbPort = 5433,
    [string]$DbPassword = "",
    [switch]$SkipRebuild
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

if (-not $DbPassword) {
    if ($env:STAGING_DB_PASSWORD) { $DbPassword = $env:STAGING_DB_PASSWORD }
    else { $DbPassword = "staging-smoke-db-pass-xx" }
}

$env:STAGING_API_PORT = "$ApiPort"
$env:STAGING_FE_PORT = "$FePort"
$env:STAGING_DB_PORT = "$DbPort"
$env:STAGING_DB_PASSWORD = $DbPassword
$env:STAGING_PUBLIC_API_URL = "http://localhost:$ApiPort"
$env:STAGING_CORS_ORIGINS = "http://localhost:$FePort,http://localhost:5173"
if (-not $env:STAGING_SECRET_KEY) {
    $env:STAGING_SECRET_KEY = "staging-smoke-secret-key-min-32-chars-xx"
}

$ComposeBase = "docker-compose.staging.yml"
$ComposeDesign = "docker-compose.staging.design-engine.yml"

function Ensure-Docker {
    $v = cmd /c "docker version --format {{.Server.Version}} 2>nul"
    if ($LASTEXITCODE -eq 0 -and $v) { return }
    docker desktop start 2>$null | Out-Null
    for ($i = 0; $i -lt 40; $i++) {
        $v = cmd /c "docker version --format {{.Server.Version}} 2>nul"
        if ($LASTEXITCODE -eq 0 -and $v) { return }
        Start-Sleep -Seconds 3
    }
    throw "Docker engine not available"
}

Ensure-Docker

Write-Host "=== Design Engine staging (API :$ApiPort) ==="
$upArgs = @("-f", $ComposeBase, "-f", $ComposeDesign, "up", "-d")
if (-not $SkipRebuild) { $upArgs += "--build" }
$upArgs += "backend"
& docker compose @upArgs
if ($LASTEXITCODE -ne 0) {
    # Ensure db too
    & docker compose -f $ComposeBase -f $ComposeDesign up -d db
    & docker compose @upArgs
    if ($LASTEXITCODE -ne 0) { throw "compose up failed" }
}

# Wait ready
$readyUrl = "http://localhost:$ApiPort/health/ready"
$ok = $false
for ($i = 0; $i -lt 45; $i++) {
    try {
        $r = Invoke-WebRequest -Uri $readyUrl -UseBasicParsing -TimeoutSec 4
        if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch { Write-Host "  wait ready $i..." }
    Start-Sleep -Seconds 2
}
if (-not $ok) { throw "backend not ready at $readyUrl" }
Write-Host "GET /health/ready -> $((Invoke-WebRequest -Uri $readyUrl -UseBasicParsing).Content)"

# Confirm flags via a lightweight probe: preview without auth should 401; with wrong flags export stays queued
# Use acceptance venv
$py = Join-Path $RepoRoot "backend\.venv-acceptance\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Creating acceptance venv..."
    py -m venv (Join-Path $RepoRoot "backend\.venv-acceptance")
    & $py -m pip install -U pip
    & $py -m pip install -e "$(Join-Path $RepoRoot 'backend')[dev]"
}

$env:DATABASE_URL = "postgresql://patchhive:${DbPassword}@localhost:${DbPort}/patchhive"
$env:STAGING_API_URL = "http://localhost:$ApiPort"
$env:PYTHONPATH = (Join-Path $RepoRoot "backend")

Write-Host "=== Walkthrough script ==="
& $py (Join-Path $RepoRoot "scripts\staging\design_engine_walkthrough.py")
if ($LASTEXITCODE -ne 0) { throw "walkthrough failed ($LASTEXITCODE)" }

# Pack files inside container
Write-Host "=== List design_packs in container ==="
cmd /c "docker compose -f $ComposeBase -f $ComposeDesign exec -T backend sh -c `"ls -la /app/exports/design_packs 2>/dev/null | head -20`""

Write-Host ""
Write-Host "DESIGN ENGINE STAGING WALKTHROUGH PASS"
Write-Host "  UI: Style Studio on http://localhost:$FePort (flags on backend)"
Write-Host "  Payments remain fail-closed."
