# SAFE-FOOD Option A. Safe local no-Docker run using an existing Python environment.
# Read RUN_GUIDE_AR.md first; this does NOT contact GitHub or publish files.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = if (Test-Path '.venv\Scripts\python.exe') { '.\.venv\Scripts\python.exe' } else { 'python' }
$steps = @(
  @('data/prepare_option_a.py'),
  @('data/build_example_sql.py'),
  @('pipeline/run.py','--no-load'),
  @('profiling/profiling.py'),
  @('rules/rule_checks.py'),
  @('er/match_products.py'),
  @('model/build_graph.py'),
  @('model/baseline.py'),
  @('model/gnn.py'),
  @('model/link_prediction.py')
)
foreach ($argsForStep in $steps) {
    Write-Host "`n>>> python $($argsForStep -join ' ')" -ForegroundColor Cyan
    & $python @argsForStep
    if ($LASTEXITCODE -ne 0) { throw "Option A failed: $($argsForStep -join ' ')" }
}
Write-Host "DONE: read build/shacl-report.txt; model/outputs/*.csv; data/quality/summary.json" -ForegroundColor Green
