; CYVEX installer. Build: makensis installer\cyvex.nsi  (after build.py)
Unicode true
!define APP "CYVEX"
!define VER "1.0.2"
!define UNKEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\CYVEX"

Name "${APP}"
OutFile "..\dist\CYVEX-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\CYVEX"
RequestExecutionLevel user
SetCompressor /SOLID lzma
Icon "..\icon.ico"
UninstallIcon "..\icon.ico"
BrandingText "CYVEX ${VER}"

!include "MUI2.nsh"
!define MUI_ICON "..\icon.ico"
!define MUI_UNICON "..\icon.ico"
!define MUI_FINISHPAGE_RUN "$INSTDIR\CYVEX.exe"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  nsExec::Exec 'taskkill /F /IM CYVEX.exe'
  SetOutPath "$INSTDIR"
  File /r /x data "..\dist\CYVEX\*.*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\CYVEX.lnk" "$INSTDIR\CYVEX.exe" "" "$INSTDIR\CYVEX.exe" 0
  CreateShortcut "$SMPROGRAMS\CYVEX.lnk" "$INSTDIR\CYVEX.exe" "" "$INSTDIR\CYVEX.exe" 0
  WriteRegStr HKCU "${UNKEY}" "DisplayName" "${APP}"
  WriteRegStr HKCU "${UNKEY}" "DisplayVersion" "${VER}"
  WriteRegStr HKCU "${UNKEY}" "Publisher" "NOVU"
  WriteRegStr HKCU "${UNKEY}" "DisplayIcon" "$INSTDIR\CYVEX.exe"
  WriteRegStr HKCU "${UNKEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKCU "${UNKEY}" "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
SectionEnd

Section "Uninstall"
  nsExec::Exec 'taskkill /F /IM CYVEX.exe'
  Delete "$DESKTOP\CYVEX.lnk"
  Delete "$SMPROGRAMS\CYVEX.lnk"
  DeleteRegKey HKCU "${UNKEY}"
  RMDir /r "$INSTDIR"
SectionEnd
