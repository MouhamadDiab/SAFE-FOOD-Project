# Run from the reviewed project's root on Windows PowerShell.
# Uses the already-installed Knowledge Representation course Python environment.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = "..\course_knowledge_representation\demos\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Missing course Python environment: $python" }
$commands = @(
    @('data/build_example_sql.py'),
    @('pipeline/run.py', '--no-load'),
    @('profiling/profiling.py'),
    @('rules/rule_checks.py'),
    @('model/build_graph.py'),
    @('model/baseline.py'),
    @('model/gnn.py'),
    @('model/link_prediction.py')
)
foreach ($cmd in $commands) {
    Write-Host "Running $($cmd -join ' ')"
    & $python @cmd
    if ($LASTEXITCODE -ne 0) { throw "Failed: $($cmd -join ' ')" }
}
$env:LLM_MODE = 'offline'
& $python 'access-layer/ask.py' 'How many packaged products declare the gluten allergen?'
if ($LASTEXITCODE -ne 0) { throw "Access query failed" }
& $python 'access-layer/ask.py' 'What is the safe medical dose of aspartame for a child eating this yogurt?'
if ($LASTEXITCODE -ne 0) { throw "Refusal demo failed" }
Write-Host 'LOCAL DEMO COMPLETE (offline mode only; Docker/Gemini still unverified).' -ForegroundColor Green
