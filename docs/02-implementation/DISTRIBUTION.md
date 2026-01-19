# Distribution Guide: Winget & Chocolatey

## Übersicht

Dieses Dokument beschreibt, wie Stay-On-Track über Winget und Chocolatey verteilt wird.

---

## 1. GitHub Releases (Basis)

### Automatisches Release erstellen

**Datei:** `.github/workflows/release.yml`

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build with PyInstaller
        run: pyinstaller build.spec

      - name: Install Inno Setup
        run: choco install innosetup -y

      - name: Compile Installer
        run: |
          & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_script.iss

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: Output/StayOnTrack_Setup.exe
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Release erstellen:

```bash
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

---

## 2. Winget (Windows Package Manager)

### Warum Winget?
- ✅ Offiziell von Microsoft
- ✅ Kostenlos
- ✅ Automatische Updates
- ✅ Reduziert Trust-Probleme

### Schritt 1: Manifest erstellen

**Datei:** `winget/Quievreux.StayOnTrack.yaml`

```yaml
# Created using wingetcreate 1.6.1.0
# yaml-language-server: $schema=https://aka.ms/winget-manifest.version.1.6.0.schema.json

PackageIdentifier: Quievreux.StayOnTrack
PackageVersion: 1.0.0
DefaultLocale: en-US
ManifestType: version
ManifestVersion: 1.6.0
```

**Datei:** `winget/Quievreux.StayOnTrack.locale.en-US.yaml`

```yaml
# Created using wingetcreate 1.6.1.0
# yaml-language-server: $schema=https://aka.ms/winget-manifest.defaultLocale.1.6.0.schema.json

PackageIdentifier: Quievreux.StayOnTrack
PackageVersion: 1.0.0
PackageLocale: en-US
Publisher: Quievreux
PublisherUrl: https://github.com/skquievreux
PublisherSupportUrl: https://github.com/skquievreux/stay-on-track/issues
Author: Quievreux
PackageName: Stay On Track
PackageUrl: https://github.com/skquievreux/stay-on-track
License: MIT
LicenseUrl: https://github.com/skquievreux/stay-on-track/blob/main/LICENSE
ShortDescription: Productivity tracker with 15-minute interval logging
Description: Stay On Track helps you maintain productivity by prompting you every 15 minutes to log what you're working on. All data is stored locally in CSV format.
Moniker: stayontrack
Tags:
- productivity
- time-tracking
- logging
- windows
ManifestType: defaultLocale
ManifestVersion: 1.6.0
```

**Datei:** `winget/Quievreux.StayOnTrack.installer.yaml`

```yaml
# Created using wingetcreate 1.6.1.0
# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.1.6.0.schema.json

PackageIdentifier: Quievreux.StayOnTrack
PackageVersion: 1.0.0
InstallerType: inno
Scope: user
InstallModes:
- interactive
- silent
- silentWithProgress
UpgradeBehavior: install
Installers:
- Architecture: x64
  InstallerUrl: https://github.com/skquievreux/stay-on-track/releases/download/v1.0.0/StayOnTrack_Setup.exe
  InstallerSha256: HASH_HIER_EINFUEGEN
ManifestType: installer
ManifestVersion: 1.6.0
```

### Schritt 2: SHA256 Hash berechnen

```powershell
Get-FileHash -Path "Output\StayOnTrack_Setup.exe" -Algorithm SHA256
```

### Schritt 3: Pull Request erstellen

1. Fork: https://github.com/microsoft/winget-pkgs
2. Erstelle Ordner: `manifests/q/Quievreux/StayOnTrack/1.0.0/`
3. Kopiere die 3 YAML-Dateien hinein
4. Commit & Push
5. Erstelle Pull Request

**Titel:** `New package: Quievreux.StayOnTrack version 1.0.0`

### Schritt 4: Nach Merge

Benutzer können installieren mit:
```powershell
winget install Quievreux.StayOnTrack
```

---

## 3. Chocolatey

### Warum Chocolatey?
- ✅ Beliebt bei Entwicklern
- ✅ Automatische Updates
- ✅ Kostenlos für Open Source

### Schritt 1: Account erstellen

https://community.chocolatey.org/account/register

### Schritt 2: Nuspec erstellen

**Datei:** `chocolatey/stayontrack.nuspec`

```xml
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
  <metadata>
    <id>stayontrack</id>
    <version>1.0.0</version>
    <packageSourceUrl>https://github.com/skquievreux/stay-on-track</packageSourceUrl>
    <owners>Quievreux</owners>
    <title>Stay On Track</title>
    <authors>Quievreux</authors>
    <projectUrl>https://github.com/skquievreux/stay-on-track</projectUrl>
    <iconUrl>https://raw.githubusercontent.com/skquievreux/stay-on-track/main/assets/icon.png</iconUrl>
    <licenseUrl>https://github.com/skquievreux/stay-on-track/blob/main/LICENSE</licenseUrl>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <projectSourceUrl>https://github.com/skquievreux/stay-on-track</projectSourceUrl>
    <docsUrl>https://github.com/skquievreux/stay-on-track/blob/main/README.md</docsUrl>
    <bugTrackerUrl>https://github.com/skquievreux/stay-on-track/issues</bugTrackerUrl>
    <tags>productivity time-tracking logging windows</tags>
    <summary>Productivity tracker with 15-minute interval logging</summary>
    <description>
Stay On Track helps you maintain productivity by prompting you every 15 minutes to log what you're working on. 

Features:
- 15-minute interval reminders
- System tray integration
- Local CSV storage
- Activity history viewer
- Configurable work hours
    </description>
    <releaseNotes>https://github.com/skquievreux/stay-on-track/releases/tag/v1.0.0</releaseNotes>
  </metadata>
  <files>
    <file src="tools\**" target="tools" />
  </files>
</package>
```

**Datei:** `chocolatey/tools/chocolateyinstall.ps1`

```powershell
$ErrorActionPreference = 'Stop'
$toolsDir   = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url64      = 'https://github.com/skquievreux/stay-on-track/releases/download/v1.0.0/StayOnTrack_Setup.exe'

$packageArgs = @{
  packageName   = $env:ChocolateyPackageName
  unzipLocation = $toolsDir
  fileType      = 'exe'
  url64bit      = $url64

  softwareName  = 'Stay On Track*'

  checksum64    = 'HASH_HIER_EINFUEGEN'
  checksumType64= 'sha256'

  silentArgs    = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  validExitCodes= @(0)
}

Install-ChocolateyPackage @packageArgs
```

**Datei:** `chocolatey/tools/chocolateyuninstall.ps1`

```powershell
$ErrorActionPreference = 'Stop'
$packageArgs = @{
  packageName   = $env:ChocolateyPackageName
  softwareName  = 'Stay On Track*'
  fileType      = 'exe'
  silentArgs    = '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-'
  validExitCodes= @(0)
}

$uninstalled = $false
[array]$key = Get-UninstallRegistryKey -SoftwareName $packageArgs['softwareName']

if ($key.Count -eq 1) {
  $key | % { 
    $packageArgs['file'] = "$($_.UninstallString)"
    Uninstall-ChocolateyPackage @packageArgs
  }
} elseif ($key.Count -eq 0) {
  Write-Warning "$packageName has already been uninstalled by other means."
} elseif ($key.Count -gt 1) {
  Write-Warning "$($key.Count) matches found!"
  Write-Warning "To prevent accidental data loss, no programs will be uninstalled."
}
```

### Schritt 3: Package erstellen

```powershell
# Chocolatey installieren (falls nicht vorhanden)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Package erstellen
cd chocolatey
choco pack

# Lokal testen
choco install stayontrack -s . -y

# Hochladen
choco push stayontrack.1.0.0.nupkg --source https://push.chocolatey.org/ --api-key YOUR_API_KEY
```

### Schritt 4: Nach Veröffentlichung

Benutzer können installieren mit:
```powershell
choco install stayontrack
```

---

## 4. Automatisierung

### GitHub Action für automatisches Publishing

**Datei:** `.github/workflows/publish-packages.yml`

```yaml
name: Publish Packages

on:
  release:
    types: [published]

jobs:
  update-winget:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Get version
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT
      
      - name: Update Winget manifests
        run: |
          # SHA256 berechnen
          $hash = (Get-FileHash -Path "Output/StayOnTrack_Setup.exe" -Algorithm SHA256).Hash
          
          # Manifests aktualisieren
          # ... (automatisch mit wingetcreate)
      
      - name: Create Winget PR
        # Automatisch PR zu microsoft/winget-pkgs erstellen

  publish-chocolatey:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Chocolatey package
        run: |
          cd chocolatey
          choco pack
      
      - name: Push to Chocolatey
        run: |
          choco push chocolatey/*.nupkg --source https://push.chocolatey.org/ --api-key ${{ secrets.CHOCOLATEY_API_KEY }}
```

---

## 5. Checkliste für neues Release

```markdown
- [ ] Version in version.py aktualisieren
- [ ] Git Tag erstellen: `git tag -a v1.0.1 -m "Release v1.0.1"`
- [ ] Tag pushen: `git push origin v1.0.1`
- [ ] GitHub Release wird automatisch erstellt
- [ ] SHA256 Hash von StayOnTrack_Setup.exe kopieren
- [ ] Winget Manifest aktualisieren und PR erstellen
- [ ] Chocolatey Package aktualisieren und pushen
- [ ] Release Notes in GitHub ergänzen
```

---

**Erstellt:** 2026-01-16  
**Version:** 1.0.0
