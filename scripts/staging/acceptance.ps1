# Run backend acceptance suite against local staging Compose Postgres.
# Uses a dedicated database (patchhive_acceptance) so the live staging API DB is not truncated.
#
# Prerequisites: Docker staging stack up (scripts/staging/smoke.ps1 or compose up).
#
# Usage (repo root):
#   powershell -File scripts/staging/acceptance.ps1
#   powershell -File scripts/staging/acceptance.ps1 -DbPort 5433

param(
    [int]$DbPort = 5433,
    [string]$DbPassword = "",
    [string]$ComposeFile = "docker-compose.staging.yml",
    [string]$AcceptanceDb = "patchhive_acceptance"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

if (-not $DbPassword) {
    if ($env:STAGING_DB_PASSWORD) { $DbPassword = $env:STAGING_DB_PASSWORD }
    else { $DbPassword = "staging-smoke-db-pass-xx" }
}

function Ensure-Docker {
    $v = cmd /c "docker version --format {{.Server.Version}} 2>nul"
    if ($LASTEXITCODE -eq 0 -and $v) { return }
    docker desktop start 2>$null | Out-Null
    for ($i = 0; $i -lt 30; $i++) {
        $v = cmd /c "docker version --format {{.Server.Version}} 2>nul"
        if ($LASTEXITCODE -eq 0 -and $v) { return }
        Start-Sleep -Seconds 3
    }
    throw "Docker engine not available"
}

Ensure-Docker
$env:STAGING_DB_PORT = "$DbPort"
$env:STAGING_DB_PASSWORD = $DbPassword

# Ensure db is up
$ps = cmd /c "docker compose -f $ComposeFile ps --status running --services 2>nul"
if ($ps -notmatch "db") {
    Write-Host "Starting staging db..."
    cmd /c "docker compose -f $ComposeFile up -d db"
    Start-Sleep -Seconds 5
}

Write-Host "=== Ensure acceptance database '$AcceptanceDb' ==="
cmd /c "docker compose -f $ComposeFile exec -T db psql -U patchhive -d postgres -v ON_ERROR_STOP=1 -c `"SELECT 1 FROM pg_database WHERE datname='$AcceptanceDb'`"" | Out-Null
$exists = cmd /c "docker compose -f $ComposeFile exec -T db psql -U patchhive -d postgres -t -A -c `"SELECT 1 FROM pg_database WHERE datname='$AcceptanceDb';`""
if (($exists | Out-String).Trim() -ne "1") {
    cmd /c "docker compose -f $ComposeFile exec -T db psql -U patchhive -d postgres -v ON_ERROR_STOP=1 -c `"CREATE DATABASE $AcceptanceDb;`""
    if ($LASTEXITCODE -ne 0) { throw "CREATE DATABASE failed" }
    Write-Host "Created $AcceptanceDb"
} else {
    Write-Host "Database $AcceptanceDb already exists"
}

$acceptUrl = "postgresql://patchhive:${DbPassword}@localhost:${DbPort}/${AcceptanceDb}"
Write-Host "ACCEPTANCE_DATABASE_URL=$acceptUrl"

# Host-side venv for pytest (backend image has no dev deps)
$venv = Join-Path $RepoRoot "backend\.venv-acceptance"
$py = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Creating venv + installing backend[dev]..."
    py -m venv $venv
    & $py -m pip install -U pip
    & $py -m pip install -e "$(Join-Path $RepoRoot 'backend')[dev]"
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
}

$env:ACCEPTANCE_DATABASE_URL = $acceptUrl
$env:TEST_MODE = "true"
$env:STRIPE_TEST_MODE = "true"
$env:ALLOW_PRODUCTION_PAYMENTS = "false"
$env:PYTHONPATH = (Join-Path $RepoRoot "backend")
$tmpRoot = Join-Path $RepoRoot "tmp\acceptance-run"
$exportDir = Join-Path $tmpRoot "exports"
$pytestTmp = Join-Path $tmpRoot "pytest-tmp"
New-Item -ItemType Directory -Path $exportDir -Force | Out-Null
New-Item -ItemType Directory -Path $pytestTmp -Force | Out-Null
$env:ACCEPTANCE_EXPORT_DIR = $exportDir
$env:TEMP = $pytestTmp
$env:TMP = $pytestTmp
$env:TMPDIR = $pytestTmp

Write-Host "=== pytest tests/acceptance ==="
Set-Location (Join-Path $RepoRoot "backend")
& $py -m pytest tests/acceptance -q --tb=short
$code = $LASTEXITCODE
Write-Host "pytest exit $code"
exit $code
