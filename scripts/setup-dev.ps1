$ErrorActionPreference = "Stop"

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .\backend

Write-Host "Development environment ready."
Write-Host "Activate with: .\\.venv\\Scripts\\Activate.ps1"
