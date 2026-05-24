param(
  [string]$ServiceName = 'zDashJanieServer',
  [string]$PythonPath = 'C:\Python311\python.exe',
  [string]$ProjectDir = 'C:\zdash\backend',
  [string]$LogDir = 'C:\zdash\logs'
)

$ErrorActionPreference = 'Stop'
$nssm = 'nssm'
$uvicornCmd = '-m uvicorn app.main:app --host 0.0.0.0 --port 8000'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

& $nssm install $ServiceName $PythonPath $uvicornCmd
& $nssm set $ServiceName AppDirectory $ProjectDir
& $nssm set $ServiceName AppStdout "$LogDir\\backend-out.log"
& $nssm set $ServiceName AppStderr "$LogDir\\backend-err.log"
& $nssm set $ServiceName Start SERVICE_AUTO_START
& $nssm set $ServiceName AppRestartDelay 5000

Write-Host "Service installed: $ServiceName"
