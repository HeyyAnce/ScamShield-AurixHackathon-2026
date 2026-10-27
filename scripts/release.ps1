param([string]$Message = 'Fix configuration, AI fallback and embedded feedback usability')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $projectRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $python)) { throw 'Create .venv and install requirements-dev.txt first.' }
function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Executable failed with exit code $LASTEXITCODE" }
}
if ((git branch --show-current) -ne 'main') { throw 'Run releases from main.' }
$remote = git remote get-url origin
if ($remote -ne 'https://github.com/HeyyAnce/ScamShield-AurixHackathon-2026.git') { throw 'Unexpected origin; refusing to publish.' }
Invoke-Checked $python @('-m', 'pytest', 'tests', '-q')
Invoke-Checked 'git' @('diff', '--check')
Invoke-Checked 'git' @('fetch', 'origin')
Invoke-Checked 'git' @('merge-base', '--is-ancestor', 'origin/main', 'HEAD')
# Explicit project paths only; never stage .env, environments or audit output.
$paths = @('.env.example', '.gitignore', '.streamlit', 'README.md', 'app.py', 'cloud_ui.py', 'web_server.py', 'requirements.txt', 'web_requirements.txt', 'requirements-dev.txt', 'frontend', 'src', 'data', 'tests', 'scripts', 'CHANGELOG.md')
Invoke-Checked 'git' (@('add', '--') + $paths)
$staged = git diff --cached --name-only
if ($staged -match '(^|/)(\.env|secrets\.toml)$') { throw 'Private configuration staged; refusing to publish.' }
if ($staged) { Invoke-Checked 'git' @('commit', '-m', $Message) }
Invoke-Checked 'git' @('push', 'origin', 'main')
Write-Host 'Pushed to the branch connected to Streamlit Community Cloud.'
Write-Host 'Deployment is not confirmed until the live browser loads release 20261027-cleanup1 and a check succeeds.'
Write-Host 'https://scamshield-aurixhackathon-2026.streamlit.app/'
