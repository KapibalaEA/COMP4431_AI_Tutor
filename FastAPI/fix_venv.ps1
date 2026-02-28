# Run from FastAPI folder. Fixes broken pydantic_core in venv.
# Usage: .\fix_venv.ps1

& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\python.exe -m pip uninstall -y pydantic pydantic-core 2>$null
& .\venv\Scripts\python.exe -m pip install "pydantic>=2.0,<3" "pydantic-core" --no-cache-dir --force-reinstall
Write-Host "Done. Try: .\venv\Scripts\activate; uvicorn app.main:app --reload"
