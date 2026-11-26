Target amd64-unicode
; NeoNote-Setup: entpackt NeoNote in einen temporären Ordner und startet den Installer im NeoNote-Look
; (NeoNote.exe --setup). Danach schreibt es den Deinstaller in den gewählten Ordner.
!include "LogicLib.nsh"
!include "FileFunc.nsh"
!include "WinMessages.nsh"
!define APP "NeoNote"
!define TITLE "NeoNote Media Player"
!ifndef VERSION
  !define VERSION "1.3.1"
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
!ifndef VIVERSION
  !define VIVERSION "1.3.1.0"   ; Dateiversion braucht vier Stellen
!endif
VIProductVersion "${VIVERSION}"
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
  ; /UPDATE: still installiert, aber von NeoNote selbst gestartet – dann zeigen wir Fortschritt
  StrCpy $4 "0"
  ClearErrors
  ${GetOptions} $R0 "/UPDATE" $R1
  IfErrors +2
  StrCpy $4 "1"
  ; Startfenster im NeoNote-Look, solange entpackt wird (schließt sich, sobald das Setup- bzw. Update-Fenster erscheint)
  ${If} $9 != "1"
  ${OrIf} $4 == "1"
    InitPluginsDir
    File "/oname=$PLUGINSDIR\neonote-splash.exe" "splash\neonote-splash.exe"
    Exec '"$PLUGINSDIR\neonote-splash.exe"'
  ${EndIf}
  ; Läuft NeoNote noch? Ab 1.1.9 bitten wir es, sich selbst zu beenden (speichert Sitzung und Verlauf);
  ; ältere Versionen kennen --quit nicht. Was nach 6 Sekunden noch läuft, wird hart beendet.
  nsExec::Exec 'cmd /c tasklist /NH /FI "IMAGENAME eq NeoNote.exe" | find /I "NeoNote.exe"'
  Pop $0
  ${If} $0 == 0
    ReadRegStr $7 HKLM "Software\NeoNote" "InstallDir"
    StrCpy $6 "0"
    ${If} ${FileExists} "$7\NeoNote.exe"
      ClearErrors
      GetDLLVersion "$7\NeoNote.exe" $R2 $R3
      ${IfNot} ${Errors}
        ${If} $R2 > 65537
          StrCpy $6 "1"
        ${ElseIf} $R2 == 65537
        ${AndIf} $R3 >= 589824
          StrCpy $6 "1"
        ${EndIf}
      ${EndIf}
    ${EndIf}
    ${If} $6 == "1"
      System::Call 'kernel32::SetEnvironmentVariable(t "PYINSTALLER_SUPPRESS_SPLASH_SCREEN", t "1")'
  nsExec::Exec '"$7\NeoNote.exe" --quit'
      Pop $0
      StrCpy $5 0
      ${Do}
        Sleep 250
        nsExec::Exec 'cmd /c tasklist /NH /FI "IMAGENAME eq NeoNote.exe" | find /I "NeoNote.exe"'
        Pop $0
        ${If} $0 != 0
          ${ExitDo}
        ${EndIf}
        IntOp $5 $5 + 1
      ${LoopUntil} $5 >= 24
    ${EndIf}
  ${EndIf}
  nsExec::Exec 'taskkill /IM NeoNote.exe /F'
  Pop $0
  ; Entpacken in einen Ordner, den nur Administratoren ändern dürfen (nicht nach %TEMP%):
  ; sonst könnte ein anderes Programm dort DLLs austauschen, bevor das Setup mit Adminrechten startet
  StrCpy $8 "$PROGRAMFILES64\NeoNote-Setup.tmp"
  RMDir /r "$8"
  SetOutPath "$8"
  File /r "dist\NeoNote\*.*"
  StrCpy $1 ""
  StrCmp $9 "1" 0 +2
  StrCpy $1 "--silent"
  StrCmp $4 "1" 0 +2
  StrCpy $1 "--silent --update"
  ; Das Startbild des Programmstarters hier unterdrücken – das Installer-Startfenster ist ja schon da
  System::Call 'kernel32::SetEnvironmentVariable(t "PYINSTALLER_SUPPRESS_SPLASH_SCREEN", t "1")'
  ; Arbeitsordner NICHT im Entpack-Ordner: sonst „steht“ das Setup (und das danach gestartete NeoNote) darin,
  ; und Windows lässt den Ordner am Ende nicht löschen (übrig blieb „NeoNote-Setup.tmp“)
  SetOutPath "$TEMP"
  ExecWait '"$8\NeoNote.exe" --setup --version ${VERSION} $1' $0
  FindWindow $2 "NeoNoteSplash"
  ${If} $2 != 0
    SendMessage $2 ${WM_CLOSE} 0 0
  ${EndIf}
  ${If} $0 == 0
    ReadRegStr $INSTDIR HKLM "Software\NeoNote" "InstallDir"
    ${If} $INSTDIR != ""
      WriteUninstaller "$INSTDIR\Uninstall.exe"
    ${EndIf}
  ${EndIf}
  ; Entpack-Ordner entfernen – kurz warten, falls Windows (z. B. der Virenscanner) die Dateien noch festhält
  StrCpy $5 0
  ${Do}
    RMDir /r "$8"
    ${IfNot} ${FileExists} "$8\*.*"
      ${ExitDo}
    ${EndIf}
    Sleep 500
    IntOp $5 $5 + 1
  ${LoopUntil} $5 >= 10
  RMDir /r /REBOOTOK "$8"          ; notfalls beim nächsten Neustart
SectionEnd

Function un.onInit
  MessageBox MB_YESNO|MB_ICONQUESTION "${TITLE} wirklich entfernen?" /SD IDYES IDYES +2
  Abort
  ; Wie bei VLC: auf Wunsch auch die persönlichen Daten entfernen (Standard: behalten). Musikdateien bleiben immer.
  StrCpy $R9 "0"
  MessageBox MB_YESNO|MB_ICONQUESTION|MB_DEFBUTTON2 "Auch deine Bibliothek, Wiedergabelisten, Einstellungen und zwischengespeicherten Cover löschen?$\n$\nDeine Musik- und Videodateien bleiben in jedem Fall erhalten.$\n$\nNein = alles behalten, z. B. für eine spätere Neuinstallation." /SD IDNO IDNO +2
  StrCpy $R9 "1"
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
  RMDir /r "$PROGRAMFILES64\NeoNote-Setup.tmp"   ; Rest älterer Installer (bis 1.3.1.98)
  ; Vorladen beim Anmelden entfernen
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "NeoNote"
  ; NeoNote als Standard für Formate ohne Nutzerauswahl (HKCU) wieder austragen
  ReadRegStr $0 HKCU "Software\Classes\.3gp" ""
  StrCmp $0 "NeoNote.3gp" 0 +2
  DeleteRegValue HKCU "Software\Classes\.3gp" ""
  ReadRegStr $0 HKCU "Software\Classes\.aac" ""
  StrCmp $0 "NeoNote.aac" 0 +2
  DeleteRegValue HKCU "Software\Classes\.aac" ""
  ReadRegStr $0 HKCU "Software\Classes\.ac3" ""
  StrCmp $0 "NeoNote.ac3" 0 +2
  DeleteRegValue HKCU "Software\Classes\.ac3" ""
  ReadRegStr $0 HKCU "Software\Classes\.aif" ""
  StrCmp $0 "NeoNote.aif" 0 +2
  DeleteRegValue HKCU "Software\Classes\.aif" ""
  ReadRegStr $0 HKCU "Software\Classes\.aiff" ""
  StrCmp $0 "NeoNote.aiff" 0 +2
  DeleteRegValue HKCU "Software\Classes\.aiff" ""
  ReadRegStr $0 HKCU "Software\Classes\.amr" ""
  StrCmp $0 "NeoNote.amr" 0 +2
  DeleteRegValue HKCU "Software\Classes\.amr" ""
  ReadRegStr $0 HKCU "Software\Classes\.ape" ""
  StrCmp $0 "NeoNote.ape" 0 +2
  DeleteRegValue HKCU "Software\Classes\.ape" ""
  ReadRegStr $0 HKCU "Software\Classes\.asf" ""
  StrCmp $0 "NeoNote.asf" 0 +2
  DeleteRegValue HKCU "Software\Classes\.asf" ""
  ReadRegStr $0 HKCU "Software\Classes\.au" ""
  StrCmp $0 "NeoNote.au" 0 +2
  DeleteRegValue HKCU "Software\Classes\.au" ""
  ReadRegStr $0 HKCU "Software\Classes\.avi" ""
  StrCmp $0 "NeoNote.avi" 0 +2
  DeleteRegValue HKCU "Software\Classes\.avi" ""
  ReadRegStr $0 HKCU "Software\Classes\.dff" ""
  StrCmp $0 "NeoNote.dff" 0 +2
  DeleteRegValue HKCU "Software\Classes\.dff" ""
  ReadRegStr $0 HKCU "Software\Classes\.divx" ""
  StrCmp $0 "NeoNote.divx" 0 +2
  DeleteRegValue HKCU "Software\Classes\.divx" ""
  ReadRegStr $0 HKCU "Software\Classes\.dsf" ""
  StrCmp $0 "NeoNote.dsf" 0 +2
  DeleteRegValue HKCU "Software\Classes\.dsf" ""
  ReadRegStr $0 HKCU "Software\Classes\.dts" ""
  StrCmp $0 "NeoNote.dts" 0 +2
  DeleteRegValue HKCU "Software\Classes\.dts" ""
  ReadRegStr $0 HKCU "Software\Classes\.flac" ""
  StrCmp $0 "NeoNote.flac" 0 +2
  DeleteRegValue HKCU "Software\Classes\.flac" ""
  ReadRegStr $0 HKCU "Software\Classes\.flv" ""
  StrCmp $0 "NeoNote.flv" 0 +2
  DeleteRegValue HKCU "Software\Classes\.flv" ""
  ReadRegStr $0 HKCU "Software\Classes\.m2ts" ""
  StrCmp $0 "NeoNote.m2ts" 0 +2
  DeleteRegValue HKCU "Software\Classes\.m2ts" ""
  ReadRegStr $0 HKCU "Software\Classes\.m4a" ""
  StrCmp $0 "NeoNote.m4a" 0 +2
  DeleteRegValue HKCU "Software\Classes\.m4a" ""
  ReadRegStr $0 HKCU "Software\Classes\.m4b" ""
  StrCmp $0 "NeoNote.m4b" 0 +2
  DeleteRegValue HKCU "Software\Classes\.m4b" ""
  ReadRegStr $0 HKCU "Software\Classes\.m4v" ""
  StrCmp $0 "NeoNote.m4v" 0 +2
  DeleteRegValue HKCU "Software\Classes\.m4v" ""
  ReadRegStr $0 HKCU "Software\Classes\.mka" ""
  StrCmp $0 "NeoNote.mka" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mka" ""
  ReadRegStr $0 HKCU "Software\Classes\.mkv" ""
  StrCmp $0 "NeoNote.mkv" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mkv" ""
  ReadRegStr $0 HKCU "Software\Classes\.mov" ""
  StrCmp $0 "NeoNote.mov" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mov" ""
  ReadRegStr $0 HKCU "Software\Classes\.mp2" ""
  StrCmp $0 "NeoNote.mp2" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mp2" ""
  ReadRegStr $0 HKCU "Software\Classes\.mp3" ""
  StrCmp $0 "NeoNote.mp3" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mp3" ""
  ReadRegStr $0 HKCU "Software\Classes\.mp4" ""
  StrCmp $0 "NeoNote.mp4" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mp4" ""
  ReadRegStr $0 HKCU "Software\Classes\.mpc" ""
  StrCmp $0 "NeoNote.mpc" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mpc" ""
  ReadRegStr $0 HKCU "Software\Classes\.mpeg" ""
  StrCmp $0 "NeoNote.mpeg" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mpeg" ""
  ReadRegStr $0 HKCU "Software\Classes\.mpg" ""
  StrCmp $0 "NeoNote.mpg" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mpg" ""
  ReadRegStr $0 HKCU "Software\Classes\.mts" ""
  StrCmp $0 "NeoNote.mts" 0 +2
  DeleteRegValue HKCU "Software\Classes\.mts" ""
  ReadRegStr $0 HKCU "Software\Classes\.oga" ""
  StrCmp $0 "NeoNote.oga" 0 +2
  DeleteRegValue HKCU "Software\Classes\.oga" ""
  ReadRegStr $0 HKCU "Software\Classes\.ogg" ""
  StrCmp $0 "NeoNote.ogg" 0 +2
  DeleteRegValue HKCU "Software\Classes\.ogg" ""
  ReadRegStr $0 HKCU "Software\Classes\.ogv" ""
  StrCmp $0 "NeoNote.ogv" 0 +2
  DeleteRegValue HKCU "Software\Classes\.ogv" ""
  ReadRegStr $0 HKCU "Software\Classes\.opus" ""
  StrCmp $0 "NeoNote.opus" 0 +2
  DeleteRegValue HKCU "Software\Classes\.opus" ""
  ReadRegStr $0 HKCU "Software\Classes\.spx" ""
  StrCmp $0 "NeoNote.spx" 0 +2
  DeleteRegValue HKCU "Software\Classes\.spx" ""
  ReadRegStr $0 HKCU "Software\Classes\.ts" ""
  StrCmp $0 "NeoNote.ts" 0 +2
  DeleteRegValue HKCU "Software\Classes\.ts" ""
  ReadRegStr $0 HKCU "Software\Classes\.tta" ""
  StrCmp $0 "NeoNote.tta" 0 +2
  DeleteRegValue HKCU "Software\Classes\.tta" ""
  ReadRegStr $0 HKCU "Software\Classes\.vob" ""
  StrCmp $0 "NeoNote.vob" 0 +2
  DeleteRegValue HKCU "Software\Classes\.vob" ""
  ReadRegStr $0 HKCU "Software\Classes\.wav" ""
  StrCmp $0 "NeoNote.wav" 0 +2
  DeleteRegValue HKCU "Software\Classes\.wav" ""
  ReadRegStr $0 HKCU "Software\Classes\.webm" ""
  StrCmp $0 "NeoNote.webm" 0 +2
  DeleteRegValue HKCU "Software\Classes\.webm" ""
  ReadRegStr $0 HKCU "Software\Classes\.wma" ""
  StrCmp $0 "NeoNote.wma" 0 +2
  DeleteRegValue HKCU "Software\Classes\.wma" ""
  ReadRegStr $0 HKCU "Software\Classes\.wmv" ""
  StrCmp $0 "NeoNote.wmv" 0 +2
  DeleteRegValue HKCU "Software\Classes\.wmv" ""
  ReadRegStr $0 HKCU "Software\Classes\.wv" ""
  StrCmp $0 "NeoNote.wv" 0 +2
  DeleteRegValue HKCU "Software\Classes\.wv" ""
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
  ${If} $R9 == "1"
    SetShellVarContext current
    RMDir /r "$APPDATA\NeoNote"
    RMDir /r "$LOCALAPPDATA\NeoNote"
    DeleteRegKey HKCU "Software\NeoNote"
    SetShellVarContext all
  ${EndIf}
  System::Call 'shell32::SHChangeNotify(i 0x08000000, i 0, p 0, p 0)'
  IfSilent +2
  MessageBox MB_OK|MB_ICONINFORMATION "${TITLE} wurde entfernt."
SectionEnd
