; Stay On Track Professional Installer
; Auto-generated version from semantic-release

#ifndef MyAppVersion
  #define MyAppVersion ReadIni(SourcePath + "\version.txt", "Version", "Number", "1.0.0")
#endif

#define MyAppName "Stay On Track"
#define MyAppPublisher "Quievreux Consulting"
#define MyAppURL "https://github.com/skquievreux/stay-on-track"
#define MyAppExeName "StayOnTrack.exe"
#define MyAppContact "https://quievreux.com"
#define MyAppId "{{A3D8F2A1-8E4B-4E3F-9C1D-7B5A6F2C1D0E}"

[Setup]
; Unique GUID - DO NOT CHANGE (ensures proper upgrades)
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppContact}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2026 {#MyAppPublisher}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Productivity Tracker with 15-Minute Reminders
VersionInfoTextVersion={#MyAppVersion}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
OutputBaseFilename=StayOnTrack_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Automatically uninstall previous version
Uninstallable=yes
CreateUninstallRegKey=yes
; Prevent multiple instances during install
AppMutex=Global\StayOnTrackAppMutex

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Automatically start Stay On Track when Windows starts"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\StayOnTrack\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\StayOnTrack\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: startup; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
// Helper to get registry key for uninstall
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstPathKey: String;
begin
  sUnInstPath := '';
  // The key is usually AppId + '_is1'
  sUnInstPathKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1';
  
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
