$ErrorActionPreference = "Stop"

if ($PSVersionTable.PSVersion.Major -lt 5) {
  throw "PowerShell 5+ is required."
}

$nssmCmd = Get-Command nssm.exe -ErrorAction SilentlyContinue
if (-not $nssmCmd) {
  throw "nssm.exe was not found in PATH. Install NSSM first."
}

$serviceName = if ($env:NSSM_SERVICE_NAME) { $env:NSSM_SERVICE_NAME } else { "zdash-janie-server" }
$displayName = if ($env:NSSM_DISPLAY_NAME) { $env:NSSM_DISPLAY_NAME } else { "zDash Janie Server" }
$description = if ($env:NSSM_DESCRIPTION) { $env:NSSM_DESCRIPTION } else { "zDash Janie Server and Agent Runtime" }
$backendHost = if ($env:NSSM_BACKEND_HOST) { $env:NSSM_BACKEND_HOST } else { "127.0.0.1" }
$backendPort = if ($env:NSSM_BACKEND_PORT) { $env:NSSM_BACKEND_PORT } else { "8005" }

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendPath = Join-Path $repoRoot "backend"
if (-not (Test-Path $backendPath)) {
  throw "Backend directory not found at: $backendPath"
}

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  throw "Python executable not found in PATH."
}
$pythonExe = $pythonCmd.Source

$logsDir = Join-Path $repoRoot "logs"
if (-not (Test-Path $logsDir)) {
  New-Item -ItemType Directory -Path $logsDir | Out-Null
}
$stdoutLog = Join-Path $logsDir "${serviceName}.stdout.log"
$stderrLog = Join-Path $logsDir "${serviceName}.stderr.log"

$appArgs = "-m uvicorn app.main:app --host $backendHost --port $backendPort"

Write-Host "Installing NSSM service '$serviceName'..."
& nssm.exe install $serviceName $pythonExe $appArgs
& nssm.exe set $serviceName AppDirectory $backendPath
& nssm.exe set $serviceName DisplayName $displayName
& nssm.exe set $serviceName Description $description
& nssm.exe set $serviceName AppStdout $stdoutLog
& nssm.exe set $serviceName AppStderr $stderrLog
& nssm.exe set $serviceName AppRotateFiles 1
& nssm.exe set $serviceName AppRotateOnline 1
& nssm.exe set $serviceName AppRotateBytes 10485760
& nssm.exe set $serviceName Start SERVICE_AUTO_START
& nssm.exe set $serviceName AppExit Default Restart

Write-Host "Service installed successfully."
Write-Host "Start service:   nssm start $serviceName"
Write-Host "Stop service:    nssm stop $serviceName"
Write-Host "Service status:  nssm status $serviceName"
