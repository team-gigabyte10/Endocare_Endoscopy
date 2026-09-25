; =====================================================================
; Endocare Endoscopy Management System
; Inno Setup 6 Script for Professional Windows Installer Distribution
; =====================================================================

#define MyAppName "Endocare"
#define MyAppVersion "2.42"
#define MyAppPublisher "Endocare Medical Systems"
#define MyAppURL "https://endocare-medical.com"
#define MyAppExeName "Endocare.exe"

[Setup]
; App Identity
AppId={{D37E6B20-891A-4C2E-B715-4D12FE56A01F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Destination Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Packaging & Output
OutputDir=..\installer_output
OutputBaseFilename=Endocare_Setup_v2.42
SetupIconFile=..\assets\logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; Permissions & System Integration
PrivilegesRequiredOverridesAllowed=dialog
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Dist folder contents produced by PyInstaller
Source: "..\dist\Endocare\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu and Desktop Shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Option to launch the application immediately after setup finishes
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
