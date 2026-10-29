# One-line installer for the HaShamran publisher on dud. Paste into PowerShell:
#   irm https://raw.githubusercontent.com/HaShamran/hashamran-links/main/dud/install.ps1 | iex
$ErrorActionPreference = "Stop"
$docs = Join-Path $env:USERPROFILE "OneDrive\Documents\HaShamran"
if (-not (Test-Path $docs)) { $docs = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "HaShamran" }
$dest = Join-Path $docs "v2"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
$raw = "https://raw.githubusercontent.com/HaShamran/hashamran-links/main"
foreach ($f in @("dud/setup.ps1", "dud/setup.cmd", "dud/login.cmd", "dud/publish-now.cmd", "dud/publisher.py", "pipeline/substack_doc.py")) {
    Invoke-WebRequest -UseBasicParsing "$raw/$f" -OutFile (Join-Path $dest (Split-Path $f -Leaf))
}
Write-Host "Downloaded the publisher to $dest"
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $dest "setup.ps1")
