$ErrorActionPreference = "Stop"

if ($PSVersionTable.PSVersion.Major -lt 5) {
  throw "PowerShell 5+ is required."
}

$nssmCmd = Get-Command nssm.exe -ErrorAction SilentlyContinue
if (-not $nssmCmd) {
  throw "nssm.exe was not found in PATH. Install NSSM first."
}

$serviceName = if ($env:NSSM_SERVICE_NAME) { $env:NSSM_SERVICE_NAME } else { "zdash-janie-server" }
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

if (-not $service) {
  Write-Host "Service '$serviceName' does not exist."
  exit 0
}

if ($service.Status -ne 'Stopped') {
  Write-Host "Stopping service '$serviceName'..."
  & nssm.exe stop $serviceName
}

Write-Host "Removing service '$serviceName'..."
& nssm.exe remove $serviceName confirm
Write-Host "Service '$serviceName' removed."
