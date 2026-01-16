# Self-Signed Code Signing Certificate Guide

## Übersicht

Dieses Dokument beschreibt, wie Sie ein Self-Signed Zertifikat für Stay-On-Track erstellen und verwenden.

## Warum Self-Signed?

**Vorteile:**
- ✅ Kostenlos
- ✅ Sofort verfügbar
- ✅ Gut für persönliche Nutzung und Tests

**Nachteile:**
- ⚠️ Windows SmartScreen warnt beim ersten Start
- ⚠️ Benutzer müssen Zertifikat manuell vertrauen

## Schritt 1: Zertifikat erstellen

### PowerShell (Als Administrator ausführen):

```powershell
# Zertifikat erstellen
$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=Quievreux, O=Quievreux, C=DE" `
    -KeyUsage DigitalSignature `
    -FriendlyName "StayOnTrack Code Signing" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3") `
    -NotAfter (Get-Date).AddYears(3)

# Zertifikat exportieren (mit Passwort)
$password = ConvertTo-SecureString -String "IhrPasswortHier" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "C:\CODE\GIT\Stay-On-Track\code-signing.pfx" -Password $password

# Zertifikat auch als .cer exportieren (für Vertrauensstellung)
Export-Certificate -Cert $cert -FilePath "C:\CODE\GIT\Stay-On-Track\code-signing.cer"
```

## Schritt 2: Executable signieren

### Manuell (lokal):

```powershell
# SignTool ist Teil des Windows SDK
# Download: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/

# Signieren
signtool sign /f "code-signing.pfx" /p "IhrPasswortHier" `
    /t http://timestamp.digicert.com `
    /fd SHA256 `
    "dist\StayOnTrack\StayOnTrack.exe"

# Verifizieren
signtool verify /pa "dist\StayOnTrack\StayOnTrack.exe"
```

## Schritt 3: CI/CD Integration

### GitHub Secrets einrichten:

1. Gehen Sie zu: https://github.com/skquievreux/stay-on-track/settings/secrets/actions
2. Klicken Sie auf "New repository secret"
3. Name: `CODE_SIGNING_PFX_BASE64`
4. Value: Base64-encoded .pfx Datei

**Base64 encodieren:**
```powershell
$bytes = [System.IO.File]::ReadAllBytes("code-signing.pfx")
$base64 = [System.Convert]::ToBase64String($bytes)
$base64 | Out-File "code-signing-base64.txt"
```

5. Zweites Secret: `CODE_SIGNING_PASSWORD`
   - Value: Ihr Passwort

### CI Workflow aktualisieren:

```yaml
# In .github/workflows/ci.yml nach PyInstaller Build:

- name: Decode certificate
  run: |
    $bytes = [System.Convert]::FromBase64String("${{ secrets.CODE_SIGNING_PFX_BASE64 }}")
    [System.IO.File]::WriteAllBytes("code-signing.pfx", $bytes)

- name: Sign executable
  run: |
    & "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign `
      /f code-signing.pfx `
      /p "${{ secrets.CODE_SIGNING_PASSWORD }}" `
      /t http://timestamp.digicert.com `
      /fd SHA256 `
      dist/StayOnTrack/StayOnTrack.exe

- name: Remove certificate file
  run: Remove-Item code-signing.pfx
```

## Schritt 4: Zertifikat vertrauen (für Benutzer)

### Option A: Automatisch beim Installer

**In `setup_script.iss` hinzufügen:**
```ini
[Files]
Source: "code-signing.cer"; DestDir: "{tmp}"; Flags: dontcopy

[Code]
procedure InstallCertificate();
var
  ResultCode: Integer;
begin
  ExtractTemporaryFile('code-signing.cer');
  Exec('certutil.exe', '-addstore TrustedPublisher "' + ExpandConstant('{tmp}\code-signing.cer') + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    InstallCertificate();
end;
```

### Option B: Manuell

1. Doppelklick auf `code-signing.cer`
2. "Zertifikat installieren"
3. "Lokaler Computer"
4. "Alle Zertifikate in folgendem Speicher" → "Vertrauenswürdige Herausgeber"

## Schritt 5: Testen

```powershell
# Nach dem Signieren:
signtool verify /pa dist\StayOnTrack\StayOnTrack.exe

# Sollte ausgeben:
# Successfully verified: dist\StayOnTrack\StayOnTrack.exe
```

## Wichtige Hinweise

⚠️ **NIEMALS** das .pfx File oder Passwort in Git committen!

**Zu .gitignore hinzufügen:**
```
*.pfx
*.cer
code-signing-base64.txt
```

## Upgrade zu kommerziellem Zertifikat

Wenn Sie später upgraden möchten:

1. Zertifikat kaufen (SSL.com, Sectigo, DigiCert)
2. GitHub Secrets aktualisieren
3. Fertig - CI verwendet automatisch neues Zertifikat

---

**Erstellt:** 2026-01-16  
**Für:** Stay-On-Track v1.0.0
