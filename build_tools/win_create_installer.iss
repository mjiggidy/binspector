[Setup]
PrivilegesRequired=lowest
AppName=Binspector!
AppVersion=1.0
DefaultDirName={autoappdata}\Binspector
OutputDir=..\dist
OutputBaseFilename=binspector_win
Compression=lzma
SolidCompression=yes
SourceDir=..\build
;LicenseFile=..\EULA

[Files]
Source: "binspector.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Binspector"; Filename: "{app}\binspector.exe"