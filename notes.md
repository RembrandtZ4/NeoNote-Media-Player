🧪 **Beta / test version** · 🇩🇪 Deutsch unten

This is a **test version** for everyone who wants to try new features early. It may still contain bugs. The regular version is still [1.3.1](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/latest).

**Download:**
- **Windows 10/11:** `NeoNote-Setup-1.3.1.98.exe` – install over your existing NeoNote, settings and library are kept.
- **Arch Linux / CachyOS:** `neonote-1.3.1.98-linux-arch.zip` – unpack and run `./install.sh`. From this version on, NeoNote updates the Arch package itself.
- **Flatpak:** test builds are available in the [test](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/tag/test) pre-release.

**Get test versions automatically:** Settings ▸ System (or ▸ About) ▸ “Also offer test versions (beta)”.

### ✨ New features
- **Updates and beta channel for the Arch package:** if NeoNote was installed from the Arch zip, the updater now downloads new versions itself and installs them in a terminal window (makepkg asks for your password there), then restarts NeoNote.
- **Safe mode and crash report:** if NeoNote closes unexpectedly shortly after starting, it starts once in safe mode next time (without hardware video decoding, background blur and media controls) and shows a report to copy – on Windows including the entry from the Windows Event Viewer. Just click “Copy report” and paste it on GitHub or in the forum. Safe mode can also be turned on permanently (Settings ▸ About).
- **What's new after an update:** after updating, NeoNote shows once what's new in this version – sorted into “New features”, “Improvements” and “Bug fixes” (Settings ▸ About, can be turned off).
- **Uninstall:** like VLC, the uninstaller now offers to also delete your library, playlists, settings and cached covers (default: keep everything; music and video files are never touched). Suggested by Holgi in the Deskmodder forum.
- **Smoother window moving on older PCs:** Settings ▸ Appearance ▸ “Pause blur while moving the window” – the blur is switched off only while dragging or resizing.
- **Frozen NeoNote in the background:** if a running (e.g. preloaded) NeoNote no longer responds, clicking NeoNote used to do nothing at all. NeoNote now notices this after a few seconds and offers to end the frozen instance and start fresh.

### ⚡ Improvements
- “What's new?” in the update bar now starts right with the changes and uses the same sections.

### 🐞 Bug fixes
- The start screen shown on click is closed again as a safety measure if it stays up for some reason.
- Dialogs always close, even if their fade-out animation gets stuck (e.g. in virtual machines).

---

🧪 **Beta / Testversion**

Das ist eine **Testversion** für alle, die neue Funktionen früh ausprobieren möchten. Sie kann noch Fehler enthalten. Die reguläre Version ist weiterhin [1.3.1](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/latest).

**Download:**
- **Windows 10/11:** `NeoNote-Setup-1.3.1.98.exe` – einfach über das vorhandene NeoNote installieren, Einstellungen und Bibliothek bleiben erhalten.
- **Arch Linux / CachyOS:** `neonote-1.3.1.98-linux-arch.zip` – entpacken und `./install.sh` ausführen. Ab dieser Version aktualisiert NeoNote das Arch-Paket selbst.
- **Flatpak:** Testpakete gibt es in der Vorabversion [test](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/tag/test).

**Testversionen automatisch bekommen:** Einstellungen ▸ System (oder ▸ Über) ▸ „Auch Testversionen (Beta) anbieten“.

### ✨ Neue Funktionen
- **Updates und Beta-Kanal für das Arch-Paket:** Wurde NeoNote über die Arch-Zip installiert, lädt der Updater neue Versionen jetzt selbst und installiert sie in einem Terminalfenster (makepkg fragt dort nach dem Passwort), danach startet NeoNote neu.
- **Sicherer Modus und Absturzbericht:** Endet NeoNote kurz nach dem Start unerwartet, startet es beim nächsten Mal einmal im sicheren Modus (ohne Hardware-Videodecodierung, Weichzeichner und Mediensteuerung) und zeigt einen Bericht zum Kopieren – unter Windows samt Eintrag aus der Ereignisanzeige. Einfach „Bericht kopieren“ klicken und auf GitHub oder im Forum einfügen. Der sichere Modus lässt sich auch dauerhaft einschalten (Einstellungen ▸ Über).
- **Neuerungen nach einem Update:** Nach dem Aktualisieren zeigt NeoNote einmal, was in dieser Version neu ist – gegliedert in „Neue Funktionen“, „Verbesserungen“ und „Behobene Fehler“ (Einstellungen ▸ Über, abschaltbar).
- **Deinstallation:** Wie bei VLC bietet der Deinstaller jetzt an, auch Bibliothek, Wiedergabelisten, Einstellungen und zwischengespeicherte Cover zu löschen (Standard: alles behalten; Musik- und Videodateien werden nie angefasst). Ein Hinweis von Holgi aus dem Deskmodder-Forum.
- **Flüssigeres Verschieben auf älteren Rechnern:** Einstellungen ▸ Darstellung ▸ „Weichzeichner beim Verschieben pausieren“ – der Weichzeichner ist nur während des Ziehens oder Größenänderns aus.
- **Hängendes NeoNote im Hintergrund:** Reagierte ein laufendes (z. B. vorgeladenes) NeoNote nicht mehr, passierte beim Klick auf NeoNote einfach gar nichts. Jetzt merkt NeoNote das nach ein paar Sekunden und bietet an, die hängende Instanz zu beenden und neu zu starten.

### ⚡ Verbesserungen
- „Was ist neu?“ in der Update-Leiste beginnt jetzt direkt mit den Neuerungen und nutzt dieselben Abschnitte.

### 🐞 Behobene Fehler
- Das Startbild beim Klick wird zur Sicherheit noch einmal geschlossen, falls es aus irgendeinem Grund stehen bleibt.
- Dialoge schließen sich immer, auch wenn ihre Ausblend-Animation hängt (z. B. in virtuellen Maschinen).


