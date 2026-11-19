Target amd64-unicode
; NeoNote-Setup: entpackt NeoNote in einen temporären Ordner und startet den Installer im NeoNote-Look
; (NeoNote.exe --setup). Danach schreibt es den Deinstaller in den gewählten Ordner.
!include "LogicLib.nsh"
!include "FileFunc.nsh"
!define APP "NeoNote"
!define TITLE "NeoNote Media Player"
!ifndef VERSION
  !define VERSION "1.1.7"
!endif
Name "${TITLE}"
Caption "${TITLE} ${VERSION} – Setup"
OutFile "NeoNote-Setup-${VERSION}.exe"
Icon "neonote.ico"
UninstallIcon "neonote.ico"
RequestExecutionLevel admin
SilentInstall silent
SetCompressor /SOLID lzma
InstallDir "$PROGRAMFILES64\NeoNote"
BrandingText "${TITLE} ${VERSION}"
VIProductVersion "${VERSION}.0"
VIAddVersionKey "ProductName" "${TITLE}"
VIAddVersionKey "ProductVersion" "${VERSION}"
VIAddVersionKey "FileVersion" "${VERSION}"
VIAddVersionKey "FileDescription" "${TITLE} Setup"
VIAddVersionKey "LegalCopyright" ""

Section
  SetRegView 64
  ; /S auf der Kommandozeile? (IfSilent ist hier immer wahr, weil das Setup selbst unsichtbar läuft)
  StrCpy $9 "0"
  ${GetParameters} $R0
  ClearErrors
  ${GetOptions} $R0 "/S" $R1
  IfErrors +2
  StrCpy $9 "1"
  StrCmp $9 "1" +2
  Banner::show /set 76 "${TITLE} ${VERSION}" "Setup wird vorbereitet …"
  nsExec::Exec 'taskkill /IM NeoNote.exe /F'
  Pop $0
  ; Entpacken in einen Ordner, den nur Administratoren ändern dürfen (nicht nach %TEMP%):
  ; sonst könnte ein anderes Programm dort DLLs austauschen, bevor das Setup mit Adminrechten startet
  StrCpy $8 "$PROGRAMFILES64\NeoNote-Setup.tmp"
  RMDir /r "$8"
  SetOutPath "$8"
  File /r "dist\NeoNote\*.*"
  StrCmp $9 "1" +2
  Banner::destroy
  StrCpy $1 ""
  StrCmp $9 "1" 0 +2
  StrCpy $1 "--silent"
  ExecWait '"$8\NeoNote.exe" --setup --version ${VERSION} $1' $0
  ${If} $0 == 0
    ReadRegStr $INSTDIR HKLM "Software\NeoNote" "InstallDir"
    ${If} $INSTDIR != ""
      WriteUninstaller "$INSTDIR\Uninstall.exe"
    ${EndIf}
  ${EndIf}
  SetOutPath "$TEMP"
  RMDir /r "$8"
SectionEnd

Function un.onInit
  MessageBox MB_YESNO|MB_ICONQUESTION "${TITLE} wirklich entfernen?$\n$\nDeine Bibliothek, Wiedergabelisten und Einstellungen bleiben erhalten." /SD IDYES IDYES +2
  Abort
FunctionEnd

Section "Uninstall"
  SetRegView 64
  SetShellVarContext all
  nsExec::Exec 'taskkill /IM NeoNote.exe /F'
  Pop $0
  Sleep 400
  Delete "$SMPROGRAMS\NeoNote Media Player.lnk"
  Delete "$DESKTOP\NeoNote Media Player.lnk"
  RMDir /r "$INSTDIR\_internal"
  Delete "$INSTDIR\NeoNote.exe"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  DeleteRegValue HKLM "Software\Classes\.3gp\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.aac\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.ac3\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.aif\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.aiff\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.amr\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.ape\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.asf\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.au\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.avi\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.dff\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.divx\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.dsf\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.dts\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.flac\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.flv\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.m2ts\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.m4a\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.m4b\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.m4v\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mka\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mkv\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mov\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mp2\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mp3\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mp4\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mpc\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mpeg\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mpg\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.mts\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.oga\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.ogg\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.ogv\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.opus\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.spx\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.ts\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.tta\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.vob\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.wav\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.webm\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.wma\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.wmv\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.wv\OpenWithProgids" "NeoNote.Media"
  DeleteRegValue HKLM "Software\Classes\.3gp\OpenWithProgids" "NeoNote.3gp"
  DeleteRegKey HKLM "Software\Classes\NeoNote.3gp"
  DeleteRegValue HKLM "Software\Classes\.aac\OpenWithProgids" "NeoNote.aac"
  DeleteRegKey HKLM "Software\Classes\NeoNote.aac"
  DeleteRegValue HKLM "Software\Classes\.ac3\OpenWithProgids" "NeoNote.ac3"
  DeleteRegKey HKLM "Software\Classes\NeoNote.ac3"
  DeleteRegValue HKLM "Software\Classes\.aif\OpenWithProgids" "NeoNote.aif"
  DeleteRegKey HKLM "Software\Classes\NeoNote.aif"
  DeleteRegValue HKLM "Software\Classes\.aiff\OpenWithProgids" "NeoNote.aiff"
  DeleteRegKey HKLM "Software\Classes\NeoNote.aiff"
  DeleteRegValue HKLM "Software\Classes\.amr\OpenWithProgids" "NeoNote.amr"
  DeleteRegKey HKLM "Software\Classes\NeoNote.amr"
  DeleteRegValue HKLM "Software\Classes\.ape\OpenWithProgids" "NeoNote.ape"
  DeleteRegKey HKLM "Software\Classes\NeoNote.ape"
  DeleteRegValue HKLM "Software\Classes\.asf\OpenWithProgids" "NeoNote.asf"
  DeleteRegKey HKLM "Software\Classes\NeoNote.asf"
  DeleteRegValue HKLM "Software\Classes\.au\OpenWithProgids" "NeoNote.au"
  DeleteRegKey HKLM "Software\Classes\NeoNote.au"
  DeleteRegValue HKLM "Software\Classes\.avi\OpenWithProgids" "NeoNote.avi"
  DeleteRegKey HKLM "Software\Classes\NeoNote.avi"
  DeleteRegValue HKLM "Software\Classes\.dff\OpenWithProgids" "NeoNote.dff"
  DeleteRegKey HKLM "Software\Classes\NeoNote.dff"
  DeleteRegValue HKLM "Software\Classes\.divx\OpenWithProgids" "NeoNote.divx"
  DeleteRegKey HKLM "Software\Classes\NeoNote.divx"
  DeleteRegValue HKLM "Software\Classes\.dsf\OpenWithProgids" "NeoNote.dsf"
  DeleteRegKey HKLM "Software\Classes\NeoNote.dsf"
  DeleteRegValue HKLM "Software\Classes\.dts\OpenWithProgids" "NeoNote.dts"
  DeleteRegKey HKLM "Software\Classes\NeoNote.dts"
  DeleteRegValue HKLM "Software\Classes\.flac\OpenWithProgids" "NeoNote.flac"
  DeleteRegKey HKLM "Software\Classes\NeoNote.flac"
  DeleteRegValue HKLM "Software\Classes\.flv\OpenWithProgids" "NeoNote.flv"
  DeleteRegKey HKLM "Software\Classes\NeoNote.flv"
  DeleteRegValue HKLM "Software\Classes\.m2ts\OpenWithProgids" "NeoNote.m2ts"
  DeleteRegKey HKLM "Software\Classes\NeoNote.m2ts"
  DeleteRegValue HKLM "Software\Classes\.m4a\OpenWithProgids" "NeoNote.m4a"
  DeleteRegKey HKLM "Software\Classes\NeoNote.m4a"
  DeleteRegValue HKLM "Software\Classes\.m4b\OpenWithProgids" "NeoNote.m4b"
  DeleteRegKey HKLM "Software\Classes\NeoNote.m4b"
  DeleteRegValue HKLM "Software\Classes\.m4v\OpenWithProgids" "NeoNote.m4v"
  DeleteRegKey HKLM "Software\Classes\NeoNote.m4v"
  DeleteRegValue HKLM "Software\Classes\.mka\OpenWithProgids" "NeoNote.mka"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mka"
  DeleteRegValue HKLM "Software\Classes\.mkv\OpenWithProgids" "NeoNote.mkv"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mkv"
  DeleteRegValue HKLM "Software\Classes\.mov\OpenWithProgids" "NeoNote.mov"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mov"
  DeleteRegValue HKLM "Software\Classes\.mp2\OpenWithProgids" "NeoNote.mp2"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mp2"
  DeleteRegValue HKLM "Software\Classes\.mp3\OpenWithProgids" "NeoNote.mp3"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mp3"
  DeleteRegValue HKLM "Software\Classes\.mp4\OpenWithProgids" "NeoNote.mp4"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mp4"
  DeleteRegValue HKLM "Software\Classes\.mpc\OpenWithProgids" "NeoNote.mpc"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mpc"
  DeleteRegValue HKLM "Software\Classes\.mpeg\OpenWithProgids" "NeoNote.mpeg"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mpeg"
  DeleteRegValue HKLM "Software\Classes\.mpg\OpenWithProgids" "NeoNote.mpg"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mpg"
  DeleteRegValue HKLM "Software\Classes\.mts\OpenWithProgids" "NeoNote.mts"
  DeleteRegKey HKLM "Software\Classes\NeoNote.mts"
  DeleteRegValue HKLM "Software\Classes\.oga\OpenWithProgids" "NeoNote.oga"
  DeleteRegKey HKLM "Software\Classes\NeoNote.oga"
  DeleteRegValue HKLM "Software\Classes\.ogg\OpenWithProgids" "NeoNote.ogg"
  DeleteRegKey HKLM "Software\Classes\NeoNote.ogg"
  DeleteRegValue HKLM "Software\Classes\.ogv\OpenWithProgids" "NeoNote.ogv"
  DeleteRegKey HKLM "Software\Classes\NeoNote.ogv"
  DeleteRegValue HKLM "Software\Classes\.opus\OpenWithProgids" "NeoNote.opus"
  DeleteRegKey HKLM "Software\Classes\NeoNote.opus"
  DeleteRegValue HKLM "Software\Classes\.spx\OpenWithProgids" "NeoNote.spx"
  DeleteRegKey HKLM "Software\Classes\NeoNote.spx"
  DeleteRegValue HKLM "Software\Classes\.ts\OpenWithProgids" "NeoNote.ts"
  DeleteRegKey HKLM "Software\Classes\NeoNote.ts"
  DeleteRegValue HKLM "Software\Classes\.tta\OpenWithProgids" "NeoNote.tta"
  DeleteRegKey HKLM "Software\Classes\NeoNote.tta"
  DeleteRegValue HKLM "Software\Classes\.vob\OpenWithProgids" "NeoNote.vob"
  DeleteRegKey HKLM "Software\Classes\NeoNote.vob"
  DeleteRegValue HKLM "Software\Classes\.wav\OpenWithProgids" "NeoNote.wav"
  DeleteRegKey HKLM "Software\Classes\NeoNote.wav"
  DeleteRegValue HKLM "Software\Classes\.webm\OpenWithProgids" "NeoNote.webm"
  DeleteRegKey HKLM "Software\Classes\NeoNote.webm"
  DeleteRegValue HKLM "Software\Classes\.wma\OpenWithProgids" "NeoNote.wma"
  DeleteRegKey HKLM "Software\Classes\NeoNote.wma"
  DeleteRegValue HKLM "Software\Classes\.wmv\OpenWithProgids" "NeoNote.wmv"
  DeleteRegKey HKLM "Software\Classes\NeoNote.wmv"
  DeleteRegValue HKLM "Software\Classes\.wv\OpenWithProgids" "NeoNote.wv"
  DeleteRegKey HKLM "Software\Classes\NeoNote.wv"
  DeleteRegKey HKLM "Software\Classes\NeoNote.Media"
  DeleteRegKey HKLM "Software\Classes\Applications\NeoNote.exe"
  DeleteRegValue HKLM "Software\RegisteredApplications" "NeoNote"
  DeleteRegKey HKLM "Software\NeoNote"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NeoNote"
  System::Call 'shell32::SHChangeNotify(i 0x08000000, i 0, p 0, p 0)'
  IfSilent +2
  MessageBox MB_OK|MB_ICONINFORMATION "${TITLE} wurde entfernt."
SectionEnd
