; Inno Setup Script for FUS Testpad (Release)
; 
; IMPORTANT: Version is automatically set from testpad/VERSION file during CI/CD builds.
; The hardcoded MyAppVersion below is only a fallback for manual local builds.
; 
; Manual build: ISCC build_config\testpad-release.iss
; Override version: ISCC /DMyAppVersion=1.2.3 build_config\testpad-release.iss

#ifndef MyAppVersion
  ; Fallback version for manual builds (overridden in CI/CD from VERSION file)
  #define MyAppVersion "1.11.0"
#endif

#define MyCompany       "FUS Instruments"
#define MyCompanyURL    "https://fusinstruments.com"
#define MyAppName       "FUS Testpad"
#define MyAppShort      "Testpad"
#define RepoRoot        AddBackslash(SourcePath) + ".."
#define DistDir         AddBackslash(SourcePath) + "..\\dist"
#define BuildFolder     "testpad_main"
#define MyAppExeName    "testpad_main.exe"

[Setup]
AppId={{6a3fbb27-776f-491b-8b0f-cea3c10fc0a7}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyCompany}
AppPublisherURL={#MyCompanyURL}
AppSupportURL={#MyCompanyURL}
DefaultDirName={autopf}\{#MyCompany}\{#MyAppShort}
DefaultGroupName={#MyCompany}\{#MyAppShort}
OutputDir={#SourcePath}..\installers
OutputBaseFilename=testpad-setup-v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
PrivilegesRequired=admin
SetupIconFile={#RepoRoot}\src\testpad\resources\fus_icon_transparent.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardStyle=modern
UsePreviousAppDir=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[InstallDelete]
; Clean up old files before installing (runs during upgrades)
Type: filesandordirs; Name: "{app}\*"

[Files]
Source: "{#DistDir}\{#BuildFolder}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[UninstallDelete]
; Remove everything during uninstall (including user-generated files)
Type: filesandordirs; Name: "{app}"

[Icons]
Name: "{group}\{#MyAppShort}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppShort}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppShort}"; Flags: nowait postinstall skipifsilent
