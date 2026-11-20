🇬🇧 English · 🇩🇪 Deutsch unten

## Download

| System | File |
|---|---|
| **Windows 10/11** | `NeoNote-Setup-1.1.9.exe` – run it and click through the installer. NeoNote 1.1.8 offers this update by itself. |
| **Linux (Arch, CachyOS, Manjaro …)** | `neonote-1.1.9-linux-arch.zip` – unpack it and run `./install.sh` in the folder. |

Other Linux distributions: see the [README](https://github.com/RembrandtZ4/NeoNote-Media-Player/blob/main/README.en.md).

> On first launch Windows may show “Windows protected your PC” because the installer isn't signed. Click “More info ▸ Run anyway” to continue.

**New**
- **Merge artists** like in WMP12: in the artist view, drag a tile (or several selected ones) onto another artist. After a confirmation, all tracks move there – their artist or album artist is set to the target name (written into the files or only saved in the library, depending on your settings).
- **Clickable details next to the cover:** in the track list, clicking the album title, artist, genre or year opens the matching view. This includes a new year view with all albums from that year, like in WMP12.

**Improved**
- Like in WMP12, the window can now also be moved by the control bar at the bottom – on any empty spot and over title and artist. Double-clicking there maximizes, just like at the top.
- Back and forward now remember their history across restarts (the last 50 views, including scroll position).
- Installer: if NeoNote is still running, the installer now asks it to quit by itself, so the playback position and history are still saved. Only if that hasn't worked after a few seconds is it closed forcibly as before. (Takes effect when updating from 1.1.9 to later versions.)
- Crash log: if NeoNote crashes, `crash.log` in the data folder shows where it happened and which video or track was open last.
- On startup NeoNote writes how long each startup step took to `startup.log` in the data folder – helps to track down slow starts.
- In the ☰ menu, “Show command bar” now sits next to “Appearance…” instead of at the very bottom.
- Windows 11: the title bars of dialogs (settings, equalizer, album info …) now have the same color as the window – one continuous surface instead of a separate bar. This also applies to the main window with the system frame and follows color changes instantly.

**Bug fixes**
- Crash when turning on image subtitles (PGS from Blu-rays, VobSub from DVDs, DVB) in MKV videos: Qt Multimedia can't handle them. NeoNote now detects these tracks itself and shows them grayed out in the menu (“not supported yet”); text subtitles work as usual.
- Large videos (4K, HDR) no longer pile up frames: if they arrive faster than NeoNote can draw them, intermediate frames are skipped. 4K HDR will only be fully smooth with playback via mpv (planned for 1.2).

---

## Download

| System | Datei |
|---|---|
| **Windows 10/11** | `NeoNote-Setup-1.1.9.exe` – starten und den Installer durchklicken. NeoNote 1.1.8 bietet dieses Update von selbst an. |
| **Linux (Arch, CachyOS, Manjaro …)** | `neonote-1.1.9-linux-arch.zip` – entpacken, im Ordner `./install.sh` ausführen. |

Andere Linux-Systeme: siehe [README](https://github.com/RembrandtZ4/NeoNote-Media-Player#readme).

> Windows zeigt beim ersten Start eventuell „Der Computer wurde durch Windows geschützt“, weil der Installer nicht signiert ist. Über „Weitere Informationen ▸ Trotzdem ausführen“ geht es weiter.

**Neu**
- **Interpreten zusammenführen** wie im WMP12: In der Interpretenansicht eine Kachel (oder mehrere markierte) auf einen anderen Interpreten ziehen. Nach einer Rückfrage wandern alle Titel dorthin – Interpret bzw. Albuminterpret wird auf den Zielnamen gesetzt (in die Dateien geschrieben oder nur in der Bibliothek, je nach Einstellung).
- **Angaben neben dem Cover anklickbar:** In der Titelliste öffnet ein Klick auf Albumtitel, Interpret, Genre oder Jahr die passende Ansicht. Neu ist dabei die Jahresansicht mit allen Alben aus diesem Jahr, wie im WMP12.

**Verbessert**
- Wie im WMP12 lässt sich das Fenster jetzt auch an der Steuerleiste unten verschieben – an allen freien Stellen und über Titel und Interpret. Doppelklick dort maximiert, wie oben.
- Zurück und Vor merken sich ihren Verlauf jetzt auch über einen Neustart hinweg (die letzten 50 Ansichten, mit Scrollposition).
- Installer: Läuft NeoNote noch, bittet der Installer es jetzt, sich selbst zu beenden – so werden Wiedergabeposition und Verlauf noch gespeichert. Erst wenn das nach ein paar Sekunden nicht geklappt hat, wird es wie bisher hart beendet. (Wirkt ab dem Update von 1.1.9 auf spätere Versionen.)
- Absturzprotokoll: Stürzt NeoNote ab, steht in `crash.log` im Datenordner, wo es passiert ist und welches Video bzw. welche Spur zuletzt geöffnet war.
- Beim Start schreibt NeoNote die Dauer jedes Startschritts in `startup.log` im Datenordner – hilft, langsame Starts aufzuspüren.
- Im Menü ☰ steht „Befehlsleiste anzeigen“ jetzt bei „Darstellung…“ statt ganz unten.
- Windows 11: Die Titelleisten der Dialoge (Einstellungen, Equalizer, Albuminfos …) haben jetzt dieselbe Farbe wie das Fenster – eine durchgehende Fläche statt eines abgesetzten Balkens. Gilt auch fürs Hauptfenster mit Systemrahmen und passt sich beim Farbwechsel sofort an.

**Fehlerbehebungen**
- Absturz beim Einschalten von Bild-Untertiteln (PGS von Blu-rays, VobSub von DVDs, DVB) in MKV-Videos: Qt Multimedia kommt damit nicht zurecht. NeoNote erkennt diese Spuren jetzt selbst und zeigt sie im Menü ausgegraut („noch nicht unterstützt“); Text-Untertitel funktionieren wie gewohnt.
- Große Videos (4K, HDR) stauen keine Bilder mehr auf: Kommen sie schneller, als NeoNote sie zeichnen kann, werden Zwischenbilder ausgelassen. Ganz flüssig wird 4K-HDR erst mit der Wiedergabe über mpv (geplant für 1.2).
