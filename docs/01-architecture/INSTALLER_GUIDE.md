# Complete Guide: Python Desktop App mit Installer & CI/CD

## Übersicht

Diese Anleitung zeigt Schritt-für-Schritt, wie Sie eine Python Desktop-Anwendung mit professionellem Installer und automatischer CI/CD-Pipeline erstellen.

**Basierend auf:** Stay-On-Track Projekt (2026-01-16)

---

## Phase 1: Projekt-Setup

### 1.1 Repository erstellen

```bash
git init my-python-app
cd my-python-app
```

### 1.2 Grundstruktur

```
my-python-app/
├── src/
│   ├── main.py          # Entry Point
│   ├── config.py        # Konfiguration
│   └── ...
├── version.py           # Versionsverwaltung
├── requirements.txt     # Dependencies
├── build.spec          # PyInstaller Config
├── setup_script.iss    # Inno Setup Config
├── .gitignore
└── README.md
```

### 1.3 Wichtige .gitignore Einträge

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/

# PyInstaller
build/
dist/
*.spec

# Inno Setup
Output/
*.exe

# Secrets
*.pfx
*.cer
code-signing-base64.txt
```

---

## Phase 2: PyInstaller Setup

### 2.1 Build Spec erstellen

**WICHTIG:** Alle lokalen Module müssen in `hiddenimports` aufgelistet werden!

```python
# build.spec
block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # KRITISCH: Alle lokalen Module hier auflisten!
        'config',
        'storage',
        'ui',
        'scheduler',
        # Externe Dependencies
        'PIL',
        'pystray',
        'customtkinter',
        'babel.numbers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Für GUI-Apps
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',  # Optional
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyApp',
)
```

### 2.2 Lokal testen

```bash
pip install pyinstaller
pyinstaller build.spec --clean
```

**Testen:** `dist/MyApp/MyApp.exe` ausführen

---

## Phase 3: Inno Setup Installer

### 3.1 Setup Script erstellen

```ini
; setup_script.iss
[Setup]
AppName=My Application
AppVersion=1.0.0
AppId={{YOUR-GUID-HERE}}
AppPublisher=Your Name
AppPublisherURL=https://github.com/yourname/myapp
DefaultDirName={autopf}\MyApp
DefaultGroupName=My Application
OutputDir=Output
OutputBaseFilename=MyApp_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
; Prevent multiple instances
AppMutex=Global\MyAppMutex
; Ensure uninstall key is created
CreateUninstallRegKey=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "Start with Windows"; GroupDescription: "Startup:"

[Files]
Source: "dist\MyApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\My Application"; Filename: "{app}\MyApp.exe"
Name: "{autodesktop}\My Application"; Filename: "{app}\MyApp.exe"; Tasks: desktopicon
Name: "{userstartup}\My Application"; Filename: "{app}\MyApp.exe"; Tasks: startup

[Run]
Filename: "{app}\MyApp.exe"; Description: "{cm:LaunchProgram,My Application}"; Flags: nowait postinstall skipifsilent

[Code]
// Helper to get registry key for uninstall
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstPathKey: String;
begin
  sUnInstPath := '';
  sUnInstPathKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppStateId}_is1';
  // Note: Ensure AppStateId or AppId is used correctly here.
  
  if RegQueryStringValue(HKLM, sUnInstPathKey, 'UninstallString', sUnInstPath) then
    Result := sUnInstPath
  else if RegQueryStringValue(HKCU, sUnInstPathKey, 'UninstallString', sUnInstPath) then
    Result := sUnInstPath;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
  UninstallString: String;
begin
  if (CurStep = ssInstall) then
  begin
    UninstallString := GetUninstallString();
    if (UninstallString <> '') then
    begin
      UninstallString := RemoveQuotes(UninstallString);
      Exec(UninstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
```

### 3.2 Lokal kompilieren

```powershell
# Inno Setup installieren
choco install innosetup -y

# Kompilieren
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_script.iss
```

**Output:** `Output/MyApp_Setup.exe`

---

## Phase 4: Versionsverwaltung

### 4.1 Version-Datei

```python
# version.py
__version__ = "1.0.0"
__build_date__ = "2026-01-16"
__app_name__ = "My Application"
```

### 4.2 Import in main.py

```python
# Am Anfang von main.py
try:
    from version import __version__
except ImportError:
    __version__ = "1.0.0"

# Später im Code verwenden
print(f"Version: {__version__}")
```

---

## Phase 5: Code-Qualität (Pylint)

### 5.1 Häufige Probleme vermeiden

**Problem 1: Trailing Whitespace**
```python
# ❌ FALSCH
def foo():
    return True    # <- Leerzeichen am Ende

# ✅ RICHTIG
def foo():
    return True
```

**Problem 2: Import outside toplevel**
```python
# ❌ FALSCH
def foo():
    from version import __version__  # Import in Funktion

# ✅ RICHTIG
from version import __version__  # Import am Anfang

def foo():
    return __version__
```

**Problem 3: Encoding nicht angegeben**
```python
# ❌ FALSCH
with open(file, "r") as f:
    data = f.read()

# ✅ RICHTIG
with open(file, "r", encoding="utf-8") as f:
    data = f.read()
```

### 5.2 Lokaler Test-Script

```batch
REM test-local.bat
@echo off
echo Running Pylint...
pylint src --disable=C0114,C0115,C0116,R0903,W0702,E0401
if %ERRORLEVEL% NEQ 0 exit /b 1

echo Building with PyInstaller...
pyinstaller build.spec --clean
if %ERRORLEVEL% NEQ 0 exit /b 1

echo All checks passed!
```

**IMMER vor jedem Commit ausführen!**

---

## Phase 6: GitHub Actions CI/CD

### 6.1 CI Workflow (.github/workflows/ci.yml)

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller pylint

      - name: Analysing the code with pylint
        run: |
          pylint src --disable=C0114,C0115,C0116,R0903,W0702,E0401

      - name: Build with PyInstaller
        run: |
          pyinstaller build.spec

      - name: Install Inno Setup
        run: |
          choco install innosetup -y

      - name: Compile Installer
        run: |
          & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_script.iss

      - name: Upload Installer Artifact
        uses: actions/upload-artifact@v4
        with:
          name: MyApp-Installer
          path: Output/MyApp_Setup.exe
```

### 6.2 Release Workflow (.github/workflows/release.yml)

**KRITISCH:** `permissions: contents: write` nicht vergessen!

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write  # WICHTIG für Release-Erstellung!

jobs:
  build-and-release:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller pylint

      - name: Analysing the code with pylint
        run: |
          pylint src --disable=C0114,C0115,C0116,R0903,W0702,E0401

      - name: Build with PyInstaller
        run: |
          pyinstaller build.spec

      - name: Install Inno Setup
        run: |
          choco install innosetup -y

      - name: Compile Installer
        run: |
          & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_script.iss

      - name: Calculate SHA256
        id: sha256
        run: |
          $hash = (Get-FileHash -Path "Output\MyApp_Setup.exe" -Algorithm SHA256).Hash
          echo "INSTALLER_SHA256=$hash" >> $env:GITHUB_OUTPUT

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: Output/MyApp_Setup.exe
          generate_release_notes: true
          body: |
            ## Installation
            Download `MyApp_Setup.exe` and run it.
            
            ### SHA256 Checksum
            ```
            ${{ steps.sha256.outputs.INSTALLER_SHA256 }}
            ```
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Phase 7: Release erstellen

### 7.1 Version aktualisieren

```python
# version.py
__version__ = "1.0.1"  # Neue Version
```

### 7.2 Git Tag erstellen

```bash
git add version.py
git commit -m "chore: bump version to 1.0.1"
git push origin main

# Tag erstellen und pushen
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

### 7.3 Automatischer Release

Der Release-Workflow wird automatisch ausgelöst und erstellt:
- ✅ GitHub Release
- ✅ Installer als Download
- ✅ SHA256 Hash
- ✅ Release Notes

---

## Phase 8: Distribution (Optional)

### 8.1 Winget Package

1. Fork: https://github.com/microsoft/winget-pkgs
2. Manifests erstellen (siehe DISTRIBUTION.md)
3. Pull Request erstellen
4. Nach Merge: `winget install YourPublisher.YourApp`

### 8.2 Chocolatey Package

1. Account: https://community.chocolatey.org/
2. Nuspec erstellen (siehe DISTRIBUTION.md)
3. Package hochladen
4. Nach Approval: `choco install yourapp`

---

## Häufige Probleme & Lösungen

### Problem 1: ModuleNotFoundError beim Ausführen der EXE

**Ursache:** Lokale Module nicht in `hiddenimports`

**Lösung:**
```python
# In build.spec
hiddenimports=[
    'config',      # Alle lokalen Module
    'storage',     # explizit auflisten!
    'ui',
    # ...
]
```

### Problem 2: GitHub Release schlägt mit 403 fehl

**Ursache:** Fehlende Berechtigungen

**Lösung:**
```yaml
# In .github/workflows/release.yml
permissions:
  contents: write  # Diese Zeile hinzufügen!
```

### Problem 3: Pylint schlägt in CI fehl

**Ursache:** Trailing whitespace, fehlende encoding, etc.

**Lösung:**
1. `test-local.bat` VOR jedem Commit ausführen
2. VS Code Setting: `"files.trimTrailingWhitespace": true`
3. Alle `open()` Aufrufe mit `encoding="utf-8"`

### Problem 4: Import-Fehler (E0401) in CI

**Ursache:** Pylint findet Module nicht

**Lösung:**
```yaml
# In CI Workflow
pylint src --disable=C0114,C0115,C0116,R0903,W0702,E0401
#                                                    ^^^^^ E0401 deaktivieren
```

### Problem 5: Installer zeigt SmartScreen-Warnung

**Ursache:** Nicht signierte Software

**Lösungen:**
1. **Kurzfristig:** Self-Signed Zertifikat (siehe CODE_SIGNING.md)
2. **Mittelfristig:** Winget/Chocolatey Package
3. **Langfristig:** Kommerzielles Code-Signing Zertifikat (€100-300/Jahr)

---

## Checkliste für neues Projekt

```markdown
### Setup
- [ ] Repository erstellen
- [ ] Projektstruktur anlegen
- [ ] .gitignore konfigurieren
- [ ] requirements.txt erstellen

### PyInstaller
- [ ] build.spec erstellen
- [ ] ALLE lokalen Module in hiddenimports
- [ ] Lokal testen: `pyinstaller build.spec --clean`

### Inno Setup
- [ ] setup_script.iss erstellen
- [ ] Lokal testen: Installer kompilieren

### Versionsverwaltung
- [ ] version.py erstellen
- [ ] Import in main.py

### Code-Qualität
- [ ] test-local.bat erstellen
- [ ] Pylint-Konfiguration
- [ ] VS Code: trimTrailingWhitespace aktivieren

### CI/CD
- [ ] .github/workflows/ci.yml erstellen
- [ ] .github/workflows/release.yml erstellen
- [ ] permissions: contents: write setzen!
- [ ] Ersten Tag pushen: git push origin v1.0.0

### Distribution (Optional)
- [ ] Winget Manifest erstellen
- [ ] Chocolatey Package erstellen
- [ ] Code-Signing Setup (optional)
```

---

## Zeitaufwand (Schätzung)

| Phase           | Erstmaliges Setup | Zukünftige Projekte |
| --------------- | ----------------- | ------------------- |
| Projekt-Setup   | 30 Min            | 10 Min              |
| PyInstaller     | 2 Std             | 30 Min              |
| Inno Setup      | 1 Std             | 20 Min              |
| CI/CD           | 2 Std             | 30 Min              |
| Testing & Fixes | 3 Std             | 1 Std               |
| **GESAMT**      | **~8 Std**        | **~2 Std**          |

---

## Weiterführende Ressourcen

- **PyInstaller:** https://pyinstaller.org/
- **Inno Setup:** https://jrsoftware.org/isinfo.php
- **GitHub Actions:** https://docs.github.com/en/actions
- **Winget:** https://github.com/microsoft/winget-pkgs
- **Chocolatey:** https://community.chocolatey.org/

---

**Erstellt:** 2026-01-16  
**Basierend auf:** Stay-On-Track Projekt  
**Version:** 1.0
