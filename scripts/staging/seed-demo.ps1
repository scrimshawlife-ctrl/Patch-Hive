# Seed golden demo users + rig into local staging Compose Postgres.
# Restores known demo passwords (re-seed safe).
#
# Accounts:
#   golden_demo / demo-pass  (User)
#   admin / admin-pass       (Admin)
#   admin_demo / admin-pass  (Admin, alias)
#
# Usage (repo root):
#   powershell -File scripts/staging/seed-demo.ps1
#   powershell -File scripts/staging/seed-demo.ps1 -DbPort 5433

param(
    [int]$DbPort = 5433,
    [string]$DbPassword = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

if (-not $DbPassword) {
    if ($env:STAGING_DB_PASSWORD) { $DbPassword = $env:STAGING_DB_PASSWORD }
    else { $DbPassword = "staging-smoke-db-pass-xx" }
}

$py = Join-Path $RepoRoot "backend\.venv-acceptance\Scripts\python.exe"
if (-not (Test-Path $py)) {
    $py = Join-Path $RepoRoot "backend\.venv\Scripts\python.exe"
}
if (-not (Test-Path $py)) {
    Write-Host "Creating backend\.venv-acceptance..."
    py -m venv (Join-Path $RepoRoot "backend\.venv-acceptance")
    $py = Join-Path $RepoRoot "backend\.venv-acceptance\Scripts\python.exe"
    & $py -m pip install -U pip
    & $py -m pip install -e "$(Join-Path $RepoRoot 'backend')[dev]"
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
}

$env:DATABASE_URL = "postgresql://patchhive:${DbPassword}@localhost:${DbPort}/patchhive"
$env:PYTHONPATH = (Join-Path $RepoRoot "backend")
$env:TEST_MODE = "true"
$env:STRIPE_TEST_MODE = "true"
$env:ALLOW_PRODUCTION_PAYMENTS = "false"

Write-Host "=== Seed golden demo (DATABASE_URL host localhost:$DbPort) ==="
& $py (Join-Path $RepoRoot "scripts\seed_golden_demo.py")
if ($LASTEXITCODE -ne 0) { throw "seed_golden_demo failed ($LASTEXITCODE)" }

Write-Host "DEMO SEED PASS"
Write-Host "  User:  golden_demo / demo-pass"
Write-Host "  Admin: admin / admin-pass"
