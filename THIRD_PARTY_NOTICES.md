# Verwendete Software und Lizenzen

NeoNote Media Player selbst steht unter der **GNU General Public License v3.0** (siehe `LICENSE`).

NeoNote nutzt die folgenden Bibliotheken und Dienste. Unter Linux kommen sie aus der Paketverwaltung des Systems. Der Windows-Installer enthält die mit ✱ markierten Bausteine unverändert. Ihren Quelltext und die vollständigen Lizenztexte findest du unter den angegebenen Adressen.

| Baustein | Zweck | Lizenz | Projekt |
|---|---|---|---|
| Python ✱ | Laufzeitumgebung | PSF License | https://www.python.org |
| Qt 6 / PySide6 ✱ | Oberfläche, Video | LGPL-3.0 | https://www.qt.io, https://wiki.qt.io/Qt_for_Python |
| FFmpeg ✱ (in Qt Multimedia) | Video- und Audiodekodierung | LGPL-2.1-or-later | https://ffmpeg.org |
| mutagen ✱ | Tags lesen und schreiben | GPL-2.0-or-later | https://github.com/quodlibet/mutagen |
| python-mpv ✱ | Anbindung an mpv | GPL-2.0-or-later oder LGPL-2.1-or-later | https://github.com/jaseg/python-mpv |
| mpv / libmpv ✱ (`libmpv-2.dll`, mit eigenem FFmpeg) | Wiedergabe, Equalizer, lückenlose Wiedergabe | GPL-3.0-or-later (Windows-Build) / unter Linux je nach Paket | https://mpv.io, https://github.com/shinchiro/mpv-winbuild-cmake |
| Vulkan Loader ✱ (`vulkan-1.dll`) | Grafik für mpv unter Windows | Apache-2.0 | https://github.com/KhronosGroup/Vulkan-Loader |
| PyWinRT ✱ | Windows-Mediensteuerung | MIT | https://github.com/pywinrt/pywinrt |
| jeepney | KDE-/Linux-Mediensteuerung (D-Bus) | MIT | https://gitlab.com/takluyver/jeepney |
| PyInstaller ✱ (Startprogramm) | Windows-Paket | GPL-2.0 mit Ausnahme für Bootloader | https://pyinstaller.org |
| NSIS ✱ (Deinstallation) | Windows-Installer | zlib/libpng | https://nsis.sourceforge.io |

**mpv unter Windows:** Seit Version 1.1.8 liegt `libmpv-2.dll` dem Installer bei, unverändert aus den Builds von https://github.com/shinchiro/mpv-winbuild-cmake (dort auch Quelltext und Bauanleitung). Dieser Build enthält ein eigenes, fest eingebautes FFmpeg und weitere Bibliotheken unter GPL-kompatiblen Lizenzen. Mit jeder neuen NeoNote-Version kommt auch eine aktuelle libmpv mit.

**Online-Dienste:** Albuminformationen kommen von [MusicBrainz](https://musicbrainz.org) (Daten unter CC0), Cover vom [Cover Art Archive](https://coverartarchive.org). Die Rechte an den Coverbildern liegen bei den jeweiligen Rechteinhabern.

„Windows Media Player“ ist eine Marke von Microsoft. NeoNote ist ein unabhängiges Projekt und steht in keiner Verbindung zu Microsoft.
