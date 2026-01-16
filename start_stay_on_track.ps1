$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot

if (Test-Path "$ScriptRoot\venv\Scripts\pythonw.exe") {
    Start-Process -FilePath "$ScriptRoot\venv\Scripts\pythonw.exe" -ArgumentList "src\main.py" -WorkingDirectory "$ScriptRoot"
}
else {
    Write-Warning "Virtual environment not found. Attempting to use system Python..."
    Start-Process -FilePath "pythonw.exe" -ArgumentList "src\main.py" -WorkingDirectory "$ScriptRoot"
}
