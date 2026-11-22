$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\Yoga gen 3\.gemini\antigravity\scratch\daily-market-ta"
$PythonExe = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$MainPy = Join-Path $ProjectDir "main.py"
$LogDir = Join-Path $ProjectDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir ("run_" + (Get-Date -Format "yyyy-MM-dd") + ".log")

Set-Location $ProjectDir
"=== Start $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -FilePath $LogFile -Append -Encoding utf8

# Wait up to 60s for network when waking up from sleep/boot
for ($i = 0; $i -lt 12; $i++) {
    try {
        $ok = Test-NetConnection -ComputerName "smtp.gmail.com" -Port 465 -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($ok) { break }
    } catch {}
    Start-Sleep -Seconds 5
}

# Run with up to 2 attempts for resilience against transient network/API glitches
for ($attempt = 1; $attempt -le 2; $attempt++) {
    "--- Attempt $attempt ---" | Out-File -FilePath $LogFile -Append -Encoding utf8
    & $PythonExe -u $MainPy *>> $LogFile
    if ($LASTEXITCODE -eq 0) {
        "=== Completed OK at $(Get-Date -Format 'HH:mm:ss') ===" | Out-File -FilePath $LogFile -Append -Encoding utf8
        exit 0
    }
    Start-Sleep -Seconds 15
}

"=== Failed after retries at $(Get-Date -Format 'HH:mm:ss') ===" | Out-File -FilePath $LogFile -Append -Encoding utf8
exit 1
