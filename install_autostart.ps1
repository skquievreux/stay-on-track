
$TargetFile = "$PSScriptRoot\venv\Scripts\pythonw.exe"
$Arguments = "$PSScriptRoot\src\main.py"
$ShortcutFile = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\StayOnTrack.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = $TargetFile
$Shortcut.Arguments = $Arguments
$Shortcut.WorkingDirectory = "$PSScriptRoot"
$Shortcut.Save()
Write-Host "Shortcut created at $ShortcutFile"
