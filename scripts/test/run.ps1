# PatchHive unified test runner (Windows PowerShell)
#
# Usage (repo root):
#   powershell -File scripts/test/run.ps1 unit
#   powershell -File scripts/test/run.ps1 acceptance
#   powershell -File scripts/test/run.ps1 frontend
#   powershell -File scripts/test/run.ps1 e2e
#   powershell -File scripts/test/run.ps1 ci
#   powershell -File scripts/test/run.ps1 smoke
#   powershell -File scripts/test/run.ps1 design-engine
#   powershell -File scripts/test/run.ps1 staging
#   powershell -File scripts/test/run.ps1 all

param(
    [Parameter(Position = 0)]
    [ValidateSet(
        "unit", "acceptance", "frontend", "e2e", "ci",
        "smoke", "design-engine", "staging", "all", "help"
    )]
    [string]$Suite = "help"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

if ($Suite -eq "help") {
    Get-Content $PSCommandPath -TotalCount 16 | Select-Object -Skip 1 | ForEach-Object {
        if ($_ -match "^#") { $_.TrimStart("#").TrimStart() }
    }
    exit 0
}

$env:TEST_MODE = if ($env:TEST_MODE) { $env:TEST_MODE } else { "true" }
$env:STRIPE_TEST_MODE = if ($env:STRIPE_TEST_MODE) { $env:STRIPE_TEST_MODE } else { "true" }
$env:ALLOW_PRODUCTION_PAYMENTS = if ($env:ALLOW_PRODUCTION_PAYMENTS) { $env:ALLOW_PRODUCTION_PAYMENTS } else { "false" }

function Get-BackendPython {
    $venvPy = Join-Path $RepoRoot "backend\.venv\Scripts\python.exe"
    $acceptPy = Join-Path $RepoRoot "backend\.venv-acceptance\Scripts\python.exe"
    if (Test-Path $venvPy) { return $venvPy }
    if (Test-Path $acceptPy) { return $acceptPy }
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $cmd = Get-Command py -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    throw "No Python found"
}

function Ensure-BackendDev {
    $py = Get-BackendPython
    & $py -c "import pytest" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing backend[dev]..."
        $backend = Join-Path $RepoRoot "backend"
        & $py -m pip install -e "${backend}[dev]"
        if ($LASTEXITCODE -ne 0) { throw "pip install backend[dev] failed" }
    }
    return $py
}

function Invoke-Unit {
    Write-Host "=== suite: unit (backend, ignore acceptance) ==="
    $py = Ensure-BackendDev
    Push-Location (Join-Path $RepoRoot "backend")
    try {
        Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
        & $py -m pytest tests --ignore=tests/acceptance -q --tb=short
        if ($LASTEXITCODE -ne 0) { throw "unit tests failed ($LASTEXITCODE)" }
    } finally {
        Pop-Location
    }
}

function Invoke-Acceptance {
    Write-Host "=== suite: acceptance (backend) ==="
    $py = Ensure-BackendDev
    $exportDir = Join-Path $RepoRoot "tmp\acceptance-run\exports"
    $pytestTmp = Join-Path $RepoRoot "tmp\acceptance-run\pytest-tmp"
    New-Item -ItemType Directory -Path $exportDir -Force | Out-Null
    New-Item -ItemType Directory -Path $pytestTmp -Force | Out-Null
    $env:ACCEPTANCE_EXPORT_DIR = $exportDir
    $env:TEMP = $pytestTmp
    $env:TMP = $pytestTmp
    $env:TMPDIR = $pytestTmp
    $env:TEST_MODE = "true"
    $env:STRIPE_TEST_MODE = "true"
    $env:ALLOW_PRODUCTION_PAYMENTS = "false"
    Push-Location (Join-Path $RepoRoot "backend")
    try {
        Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
        & $py -m pytest tests/acceptance -q --tb=short
        if ($LASTEXITCODE -ne 0) { throw "acceptance tests failed ($LASTEXITCODE)" }
    } finally {
        Pop-Location
    }
}

function Invoke-Frontend {
    Write-Host "=== suite: frontend (vitest) ==="
    Push-Location (Join-Path $RepoRoot "frontend")
    try {
        if (-not (Test-Path "node_modules")) { npm ci }
        npm test -- --run
        if ($LASTEXITCODE -ne 0) { throw "frontend tests failed ($LASTEXITCODE)" }
    } finally {
        Pop-Location
    }
}

function Invoke-E2E {
    Write-Host "=== suite: e2e (playwright) ==="
    Push-Location (Join-Path $RepoRoot "frontend")
    try {
        if (-not (Test-Path "node_modules")) { npm ci }
        npx playwright install chromium
        npm run test:e2e
        if ($LASTEXITCODE -ne 0) { throw "e2e tests failed ($LASTEXITCODE)" }
    } finally {
        Pop-Location
    }
}

function Invoke-Smoke {
    Write-Host "=== suite: staging smoke ==="
    $args = @("-File", (Join-Path $RepoRoot "scripts\staging\smoke.ps1"))
    if ($env:SKIP_BUILD -eq "1") { $args += "-SkipBuild" }
    & powershell -NoProfile -ExecutionPolicy Bypass @args
    if ($LASTEXITCODE -ne 0) { throw "smoke failed ($LASTEXITCODE)" }
}

function Invoke-DesignEngine {
    Write-Host "=== suite: design-engine walkthrough ==="
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\staging\design-engine.ps1")
    if ($LASTEXITCODE -ne 0) { throw "design-engine failed ($LASTEXITCODE)" }
}

function Invoke-StagingAcceptance {
    Write-Host "=== suite: staging acceptance (compose Postgres) ==="
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\staging\acceptance.ps1")
    if ($LASTEXITCODE -ne 0) { throw "staging acceptance failed ($LASTEXITCODE)" }
}

switch ($Suite) {
    "unit" { Invoke-Unit }
    "acceptance" { Invoke-Acceptance }
    "frontend" { Invoke-Frontend }
    "e2e" { Invoke-E2E }
    "ci" {
        Invoke-Unit
        Invoke-Frontend
        Invoke-Acceptance
    }
    "smoke" { Invoke-Smoke }
    "design-engine" { Invoke-DesignEngine }
    "staging" {
        Invoke-Smoke
        Invoke-StagingAcceptance
        Invoke-DesignEngine
    }
    "all" {
        Invoke-Unit
        Invoke-Frontend
        Invoke-Acceptance
        Invoke-E2E
    }
}

Write-Host "TEST SUITE PASS: $Suite"
