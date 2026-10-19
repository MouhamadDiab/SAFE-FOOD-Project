# SAFE-FOOD: Create a CLEAN, separate Git checkout from your GitHub repository
# and stage the reviewed source without copying .env, build outputs, secrets,
# local Python environments or generated model tensor snapshots.
# This script does NOT commit or push anything.
$ErrorActionPreference = 'Stop'
$source = $PSScriptRoot
$parent = Split-Path -Parent $source
$destination = Join-Path $parent 'SAFE-FOOD-SUBMISSION'
$repoUrl = 'https://github.com/MohammadMantach/Knowledge-Representation-Project.git'
$branch = 'safefood-reviewed-submission'

if (!(Test-Path (Join-Path $source 'docker-compose.yml'))) {
    throw 'Run this script inside the SAFE-FOOD-REVIEWED folder.'
}
if (Test-Path $destination) {
    throw "Destination already exists: $destination. Nothing was changed. Please inspect before trying again."
}

Write-Host 'Cloning the GitHub project into a SEPARATE folder...' -ForegroundColor Cyan
& git clone $repoUrl $destination
if ($LASTEXITCODE -ne 0) { throw 'Git clone failed. Check connection / repository access.' }

Push-Location $destination
try {
    & git switch -c $branch
    if ($LASTEXITCODE -ne 0) { throw 'Could not create a submission branch.' }

    # Replace only project source subfolders within this newly cloned copy.
    $directories = @('.github','access-layer','data','er','fuseki','mapping','model','ontology','pipeline','profiling','report','rules','shapes','tests')
    foreach ($dir in $directories) {
        $from = Join-Path $source $dir
        $to = Join-Path $destination $dir
        if (!(Test-Path $from)) { throw "Missing reviewed source folder: $from" }
        if (Test-Path $to) { Remove-Item -LiteralPath $to -Force -Recurse }
        New-Item -ItemType Directory -Path $to -Force | Out-Null
        Get-ChildItem -LiteralPath $from -Recurse -File -Force | ForEach-Object {
            $relative = $_.FullName.Substring($from.Length).TrimStart([char]'\',[char]'/')
            $parts = $relative -split '[\\/]'
            if ($parts -contains '__pycache__' -or $parts -contains '.pytest_cache' -or $parts -contains 'build' -or $parts -contains '.venv') { return }
            if ($_.Name -match '\.(pyc|sqlite|db|pt|log|pem|p12|key)$' -or $_.Name -eq '.env') { return }
            $targetFile = Join-Path $to $relative
            New-Item -ItemType Directory -Path (Split-Path -Parent $targetFile) -Force | Out-Null
            Copy-Item -LiteralPath $_.FullName -Destination $targetFile -Force
        }
    }

    # Explicit allowlist: copy public root-level project files, never .env.
    $rootFiles = @('.gitignore','.dockerignore','.env.example','README.md','docker-compose.yml',
        'CHANGELOG_REVIEW.md','DEFENSE_GUIDE.md','PACKAGE_CONTENTS.md','START_HERE.md',
        'TEST_STATUS.md','WINDOWS_VERIFIED_RESULTS.md','run_local_demo.ps1','FINAL_CHECK.ps1',
        'PREPARE_GITHUB.ps1')
    foreach ($file in $rootFiles) {
        $from = Join-Path $source $file
        if (Test-Path $from) { Copy-Item -LiteralPath $from -Destination (Join-Path $destination $file) -Force }
    }

    if (Test-Path '.\.env') { throw 'Unsafe: .env is unexpectedly present in submission clone.' }
    & git add -A
    if ($LASTEXITCODE -ne 0) { throw 'git add failed.' }
    $staged = @(& git diff --cached --name-only)
    $unsafe = @($staged | Where-Object { $_ -match '(^|/)(\.env|[^/]+\.(pem|p12|key|sqlite|db|pt)|__pycache__)(/|$)' })
    if ($unsafe.Count -gt 0) {
        & git reset --quiet
        throw ('Unsafe staged files detected; staging undone: ' + ($unsafe -join ', '))
    }
    $stagedText = (& git diff --cached --unified=0 | Out-String)
    if ($stagedText -match 'AIza[0-9A-Za-z_-]{25,}') {
        & git reset --quiet
        throw 'A possible Google API key was found in the staged diff; staging was undone.'
    }
    Write-Host ''
    Write-Host 'READY: Reviewed files are staged on a new local branch.' -ForegroundColor Green
    Write-Host "Branch: $branch"
    Write-Host "Folder: $destination"
    Write-Host 'No files were pushed to GitHub.'
    Write-Host 'Review the changes below, and fill in team member names before committing:'
    & git diff --cached --stat
    Write-Host ''
    Write-Host 'After review, manually run:' -ForegroundColor Yellow
    Write-Host "cd `"$destination`""
    Write-Host 'git commit -m "Prepare reviewed SAFE-FOOD Session 8 submission"'
    Write-Host "git push -u origin $branch"
    Write-Host 'Then open the Pull Request in GitHub to merge only after checking the diff.'
}
finally { Pop-Location }
