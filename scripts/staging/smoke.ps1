# PatchHive local staging smoke (Windows PowerShell)
# Brings up docker-compose.staging.yml, probes /health + /health/ready,
# verifies alembic head, and runs a pg_dump → restore-list backup drill.
#
# Usage (repo root):
#   pwsh scripts/staging/smoke.ps1
#   pwsh scripts/staging/smoke.ps1 -ApiPort 18000 -FePort 15173 -DbPort 5433
#   pwsh scripts/staging/smoke.ps1 -SkipBuild
#   pwsh scripts/staging/smoke.ps1 -DownOnly

param(
    [int]$ApiPort = 18000,
    [int]$FePort = 15173,
    [int]$DbPort = 5433,
    [switch]$SkipBuild,
    [switch]$DownOnly,
    [string]$ComposeFile = "docker-compose.staging.yml"
)

$ErrorActionPreference = "Continue"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

function Ensure-Docker {
    $v = cmd /c "docker version --format {{.Server.Version}} 2>nul"
    if ($LASTEXITCODE -eq 0 -and $v) { return }
    Write-Host "Starting Docker Desktop..."
    docker desktop start 2>$null | Out-Null
    for ($i = 0; $i -lt 40; $i++) {
        $v = cmd /c "docker version --format {{.Server.Version}} 2>nul"
        if ($LASTEXITCODE -eq 0 -and $v) {
            Write-Host "Docker engine ready: $v"
            return
        }
        Start-Sleep -Seconds 3
    }
    throw "Docker engine not available"
}

function Set-StagingEnv {
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
}

function Invoke-Compose {
    # Pass compose args as a single string array so PowerShell does not steal "-d".
    param([string[]]$ComposeArgs)
    Set-StagingEnv
    $argList = @("-f", $ComposeFile) + $ComposeArgs
    & docker compose @argList
    if ($LASTEXITCODE -ne 0) { throw "docker compose $($ComposeArgs -join ' ') failed ($LASTEXITCODE)" }
}

Ensure-Docker

if ($DownOnly) {
    Invoke-Compose -ComposeArgs @("down", "-v")
    Write-Host "Stack torn down."
    exit 0
}

Write-Host "=== Staging smoke (API :$ApiPort FE :$FePort DB :$DbPort) ==="
if ($SkipBuild) {
    Invoke-Compose -ComposeArgs @("up", "-d")
} else {
    Invoke-Compose -ComposeArgs @("up", "-d", "--build")
}

$readyUrl = "http://localhost:$ApiPort/health/ready"
$liveUrl = "http://localhost:$ApiPort/health"
$readyOk = $false
$readyBody = ""
for ($i = 0; $i -lt 45; $i++) {
    try {
        $r = Invoke-WebRequest -Uri $readyUrl -UseBasicParsing -TimeoutSec 4
        if ($r.StatusCode -eq 200) {
            $readyOk = $true
            $readyBody = $r.Content
            break
        }
    } catch {
        Write-Host "  wait ready $i..."
    }
    Start-Sleep -Seconds 2
}
if (-not $readyOk) { throw "GET $readyUrl never returned 200" }

$live = (Invoke-WebRequest -Uri $liveUrl -UseBasicParsing).Content
Write-Host "GET /health        -> $live"
Write-Host "GET /health/ready  -> $readyBody"

Set-StagingEnv
$current = (cmd /c "docker compose -f $ComposeFile exec -T backend python -m alembic current 2>&1" | Out-String)
Write-Host "alembic current:`n$current"
if ($current -notmatch "20260726_module_registry_slugs") {
    throw "Unexpected alembic current (expected 20260726_module_registry_slugs)"
}

# Backup drill: dump + verify restore listing
$dumpDir = Join-Path $RepoRoot "tmp\staging-smoke"
New-Item -ItemType Directory -Path $dumpDir -Force | Out-Null
$dumpFile = Join-Path $dumpDir "patchhive-staging.dump"
Write-Host "=== Backup drill (pg_dump custom format) ==="
cmd /c "docker compose -f $ComposeFile exec -T db pg_dump -U patchhive -d patchhive -Fc -f /tmp/patchhive.dump"
if ($LASTEXITCODE -ne 0) { throw "pg_dump failed" }
cmd /c "docker compose -f $ComposeFile cp db:/tmp/patchhive.dump `"$dumpFile`""
if (-not (Test-Path $dumpFile)) { throw "dump file missing: $dumpFile" }
$size = (Get-Item $dumpFile).Length
Write-Host "dump bytes: $size"

Write-Host "=== Restore verify (create DB + pg_restore --list) ==="
$list = (cmd /c "docker compose -f $ComposeFile exec -T db pg_restore -l /tmp/patchhive.dump 2>&1" | Out-String)
if ($LASTEXITCODE -ne 0) { throw "pg_restore -l failed" }
if ($list -notmatch "TABLE DATA| TABLE ") {
    Write-Host $list.Substring(0, [Math]::Min(500, $list.Length))
    throw "pg_restore list did not include TABLE entries"
}
# Full restore into a side database (does not replace live staging DB)
cmd /c "docker compose -f $ComposeFile exec -T db psql -U patchhive -d postgres -v ON_ERROR_STOP=1 -c `"DROP DATABASE IF EXISTS patchhive_restore_smoke;`""
cmd /c "docker compose -f $ComposeFile exec -T db psql -U patchhive -d postgres -v ON_ERROR_STOP=1 -c `"CREATE DATABASE patchhive_restore_smoke;`""
cmd /c "docker compose -f $ComposeFile exec -T db pg_restore -U patchhive -d patchhive_restore_smoke --no-owner --no-acl /tmp/patchhive.dump"
if ($LASTEXITCODE -ne 0) { throw "pg_restore into patchhive_restore_smoke failed" }
$ver = cmd /c "docker compose -f $ComposeFile exec -T db psql -U patchhive -d patchhive_restore_smoke -t -A -c `"SELECT version_num FROM alembic_version;`" 2>&1"
$ver = ($ver | Out-String).Trim()
Write-Host "restored alembic_version: $ver"
if ($ver -notmatch "20260726_module_registry_slugs") {
    throw "restored DB alembic_version mismatch: $ver"
}
cmd /c "docker compose -f $ComposeFile exec -T db psql -U patchhive -d postgres -c `"DROP DATABASE IF EXISTS patchhive_restore_smoke;`""

# F2 dual-path: canon rigs list must be mounted on the running image
Write-Host "=== F2 probe GET /api/canon/rigs ==="
$rigsUrl = "http://localhost:$ApiPort/api/canon/rigs"
try {
    $rigs = Invoke-WebRequest -Uri $rigsUrl -UseBasicParsing -TimeoutSec 10
    if ($rigs.StatusCode -ne 200) { throw "status $($rigs.StatusCode)" }
    $rigsBody = $rigs.Content
    if ($rigsBody -notmatch '"total"') { throw "response missing total: $rigsBody" }
    Write-Host "GET /api/canon/rigs -> $rigsBody"
} catch {
    throw "F2 probe failed at $rigsUrl : $_"
}

# Restore known login accounts (Login page must match these).
Write-Host "=== Seed demo credentials ==="
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\staging\seed-demo.ps1") -DbPort $DbPort
if ($LASTEXITCODE -ne 0) { throw "seed-demo failed ($LASTEXITCODE)" }

Write-Host "=== Login probe golden_demo / demo-pass ==="
$loginBody = '{"username":"golden_demo","password":"demo-pass"}'
try {
    $login = Invoke-WebRequest -Uri "http://localhost:$ApiPort/api/community/auth/login" `
        -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
    if ($login.StatusCode -ne 200) { throw "status $($login.StatusCode)" }
    if ($login.Content -notmatch "access_token") { throw "no access_token" }
    Write-Host "Login demo user OK"
} catch {
    throw "Demo login probe failed: $_"
}

Write-Host ""
Write-Host "SMOKE PASS"
Write-Host "  API:  $liveUrl"
Write-Host "  Ready: $readyUrl"
Write-Host "  FE:   http://localhost:$FePort"
Write-Host "  Dump: $dumpFile"
Write-Host "  Head: 20260726_module_registry_slugs"
Write-Host "  F2:   GET /api/canon/rigs OK"
Write-Host "  Auth: golden_demo/demo-pass · admin_demo/admin-pass"
Write-Host "Payments remain fail-closed (ALLOW_PRODUCTION_PAYMENTS=false)."
