# SAFE-FOOD final verification: read-only to project code and persistent source files.
# It reads the running Docker stack, tests its endpoints, and runs a Morph-KGC
# comparison in a disposable Docker container. No Google key is printed.
# Usage: powershell -ExecutionPolicy Bypass -File .\FINAL_CHECK.ps1
# Optional, after setting live key locally in .env: ... .\FINAL_CHECK.ps1 -Live
param([switch]$Live, [switch]$SkipR2RML)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path '.\docker-compose.yml') -or !(Test-Path '.\mapping\mapping.ttl')) {
    throw 'Put FINAL_CHECK.ps1 in the root of SAFE-FOOD-REVIEWED, not in Downloads.'
}
New-Item -ItemType Directory -Force -Path '.\build' | Out-Null
Write-Host 'SAFE-FOOD: last-mile verification' -ForegroundColor Cyan
Write-Host 'Checking Docker services...'
& docker compose ps
if ($LASTEXITCODE -ne 0) { throw 'docker compose ps failed. Start Docker Desktop.' }

Write-Host '1/3: Checking actual Fuseki SPARQL results...'
$q = 'PREFIX fs: <https://ul.edu.lb/kr/foodsafe#> SELECT (COUNT(?p) AS ?total) WHERE { ?p a fs:PackagedProduct . }'
$fuseki = Invoke-RestMethod -Uri 'http://127.0.0.1:3030/kr/sparql' -Method Post -Body @{query=$q} -Headers @{Accept='application/sparql-results+json'} -TimeoutSec 40
$count = [int]$fuseki.results.bindings[0].total.value
Write-Host "Products from Fuseki: $count"
if ($count -ne 50) { throw "Expected 50 products; got $count" }

Write-Host '2/3: Checking TEXT2SPARQL HTTP contract...'
$dataset = 'https://ul.edu.lb/kr/foodsafe/'
$checks = @(
    @{Q='How many packaged products declare the gluten allergen?'; Refuse=$false},
    @{Q='What is the safe medical dose of aspartame for a child eating this yogurt?'; Refuse=$true}
)
foreach ($entry in $checks) {
    $uri = 'http://127.0.0.1:8000/?question=' + [uri]::EscapeDataString($entry.Q) + '&dataset=' + [uri]::EscapeDataString($dataset)
    $res = Invoke-RestMethod -Uri $uri -Method Get -TimeoutSec 150
    $returned = [string]$res.query
    if ($entry.Refuse) {
        if ($returned -notmatch 'REFUSE') { throw "Refusal was not returned for: $($entry.Q)" }
        Write-Host 'Refusal check: PASS'
    } else {
        if ($returned -notmatch '(?i)SELECT|ASK') { throw "No SPARQL SELECT/ASK query returned: $returned" }
        Write-Host 'English-to-SPARQL contract: PASS'
    }
}

if (!$SkipR2RML) {
    Write-Host '3/3: Checking declarative R2RML with isolated Morph-KGC...'
    Write-Host 'This may take a few minutes on first run (Docker downloads dependencies).'
    # The disposable container installs Morph-KGC; it does NOT modify your
    # Python course environment, the running Fuseki data, or GitHub.
    $previousEAP = $ErrorActionPreference
    $ErrorActionPreference = 'Continue' # native Docker/pip can emit harmless warnings on stderr
    & docker compose run --rm --no-deps pipeline sh -c 'pip install --no-cache-dir -q morph-kgc==2.10.0 && python mapping/verify_r2rml.py' 2>&1 | Tee-Object -FilePath '.\build\r2rml-verification.log'
    $status = $LASTEXITCODE
    $ErrorActionPreference = $previousEAP
    if ($status -ne 0) {
        Write-Warning "Independent R2RML verification needs review (exit $status). See build/r2rml-verification.log."
        Write-Host 'Do NOT describe R2RML parity as verified yet.' -ForegroundColor Yellow
    } else {
        Write-Host 'R2RML engine: PASS' -ForegroundColor Green
    }
} else {
    Write-Host '3/3: R2RML check skipped by request.' -ForegroundColor Yellow
}

if ($Live) {
    Write-Host 'Optional: evaluating with the real Gemini API (may use API quota)...'
    $envLines = Get-Content '.\.env' -ErrorAction Stop
    $modeLine = @($envLines | Where-Object { $_ -match '^\s*LLM_MODE\s*=' }) | Select-Object -Last 1
    $keyLine = @($envLines | Where-Object { $_ -match '^\s*GOOGLE_API_KEY\s*=' }) | Select-Object -Last 1
    if ($modeLine -notmatch '^\s*LLM_MODE\s*=\s*live\s*$' -or !$keyLine -or $keyLine -match '^\s*GOOGLE_API_KEY\s*=\s*$') {
        throw 'For -Live, set LLM_MODE=live and GOOGLE_API_KEY=... in your LOCAL .env only; never share the key.'
    }
    & docker compose up -d --force-recreate access-layer
    if ($LASTEXITCODE -ne 0) { throw 'Could not restart access-layer for live mode.' }
    & docker compose exec -T access-layer python evaluate.py --setting repair --quiet 2>&1 | Tee-Object -FilePath '.\build\gemini-live-evaluation.log'
    if ($LASTEXITCODE -ne 0) { Write-Warning 'Live evaluation failed; inspect build/gemini-live-evaluation.log.' }
}

Write-Host 'Verification complete. Save the results and update report before pushing.' -ForegroundColor Cyan
