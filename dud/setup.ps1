# HaShamran publisher: one-time setup on dud. Run by double-clicking setup.cmd.
# Installs Python (if missing) and the publisher into %LOCALAPPDATA%\HaShamran, registers the
# "HaShamran Publisher" scheduled task (every 30 minutes, catches up after sleep), then opens the
# automation Chrome window once so you can sign in to Substack.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$data = Join-Path $env:LOCALAPPDATA "HaShamran"
$app = Join-Path $data "app"
New-Item -ItemType Directory -Force -Path $app | Out-Null

Write-Host "1/6 Checking Python..."
$py = (Get-Command py -ErrorAction SilentlyContinue)
if (-not $py) {
    Write-Host "    Installing Python 3.12 (winget)..."
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

Write-Host "2/6 Creating the publisher's own Python environment..."
$venv = Join-Path $data "venv"
if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) { py -3 -m venv $venv }
$python = Join-Path $venv "Scripts\python.exe"
$pythonw = Join-Path $venv "Scripts\pythonw.exe"
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet requests "python-substack==0.10.0" playwright tzdata

Write-Host "3/6 Copying the publisher..."
Copy-Item (Join-Path $here "publisher.py") $app -Force
Copy-Item (Join-Path $here "substack_doc.py") $app -Force

Write-Host "4/6 Registering the scheduled task 'HaShamran Publisher' (every 30 minutes)..."
$env:HASHAMRAN_STATUS_DIR = $here
[Environment]::SetEnvironmentVariable("HASHAMRAN_STATUS_DIR", $here, "User")
$action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$app\publisher.py`" run" -WorkingDirectory $app
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(5) -RepetitionInterval (New-TimeSpan -Minutes 30)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 20) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "HaShamran Publisher" -Action $action -Trigger $trigger -Settings $settings `
    -Description "Publishes translated HaShamran posts to Substack (web only). Source: github.com/HaShamran/hashamran-links" -Force | Out-Null

Write-Host "5/6 GitHub: lets dud tell the repo when a post is live (opens a browser to approve once)..."
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    winget install -e --id GitHub.cli --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
gh auth status 2>$null
if ($LASTEXITCODE -ne 0) { gh auth login --hostname github.com --web --git-protocol https }

Write-Host "6/6 Opening Chrome: sign in to Substack in that window, then close it."
& $python (Join-Path $app "publisher.py") login
Write-Host ""
Write-Host "Done. Status is written to $here\publisher-status.txt"
Read-Host "Press Enter to close"
