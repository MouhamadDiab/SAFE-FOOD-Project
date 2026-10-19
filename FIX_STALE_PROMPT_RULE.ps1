$ErrorActionPreference = 'Stop'
$path = Join-Path (Get-Location) 'access-layer\prompt_rules.txt'
if (!(Test-Path $path)) { throw "Missing $path. Run this from project root." }
$old = 'the current real sample has ZERO USDA records, so link count should be zero'
$new = 'Option A has 2,925 synthetic OFF-shaped and 797 synthetic USDA-shaped product nodes; 146 exact-barcode candidate OFF-to-USDA pairs are linked'
$content = [System.IO.File]::ReadAllText($path)
if ($content.Contains($old)) {
    Copy-Item $path ($path + '.bak') -Force
    $updated = $content.Replace($old, $new)
    [System.IO.File]::WriteAllText($path, $updated, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host 'Updated obsolete USDA prompt text. Backup: prompt_rules.txt.bak'
} elseif ($content.Contains($new)) {
    Write-Host 'Prompt already updated. No changes made.'
} else {
    Write-Host 'Old text not present; review access-layer/prompt_rules.txt manually.'
}
