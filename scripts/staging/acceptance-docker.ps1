# Run backend acceptance suite entirely inside Docker (compose network).
# No host Python venv required.
#
# Prerequisites: Docker Desktop; staging compose file present.
#
# Usage (repo root):
#   powershell -File scripts/staging/acceptance-docker.ps1
#   powershell -File scripts/staging/acceptance-docker.ps1 -DbPassword '...'

param(
    [string]$DbPassword = "",
    [string]$ComposeFile = "docker-compose.staging.yml",
    [string]$AcceptanceCompose = "docker-compose.staging.acceptance.yml"
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
    for ($i = 0; $i -lt 40; $i++) {
        $v = cmd /c "docker version --format {{.Server.Version}} 2>nul"
        if ($LASTEXITCODE -eq 0 -and $v) { return }
        Start-Sleep -Seconds 3
    }
    throw "Docker engine not available"
}

Ensure-Docker
$env:STAGING_DB_PASSWORD = $DbPassword
# Keep remapped ports consistent with smoke when already set
if (-not $env:STAGING_DB_PORT) { $env:STAGING_DB_PORT = "5433" }
if (-not $env:STAGING_API_PORT) { $env:STAGING_API_PORT = "18000" }
if (-not $env:STAGING_FE_PORT) { $env:STAGING_FE_PORT = "15173" }
if (-not $env:STAGING_SECRET_KEY) {
    $env:STAGING_SECRET_KEY = "staging-smoke-secret-key-min-32-chars-xx"
}
if (-not $env:STAGING_PUBLIC_API_URL) {
    $env:STAGING_PUBLIC_API_URL = "http://localhost:$($env:STAGING_API_PORT)"
}

$exportHost = Join-Path $RepoRoot "tmp\acceptance-docker"
New-Item -ItemType Directory -Path $exportHost -Force | Out-Null

Write-Host "=== Ensure staging db is up ==="
& docker compose -f $ComposeFile up -d db
if ($LASTEXITCODE -ne 0) { throw "compose up db failed" }

Write-Host "=== Docker acceptance (in-network pytest) ==="
& docker compose -f $ComposeFile -f $AcceptanceCompose run --rm --no-deps acceptance
if ($LASTEXITCODE -ne 0) { throw "docker acceptance failed ($LASTEXITCODE)" }

Write-Host "DOCKER ACCEPTANCE PASS"
