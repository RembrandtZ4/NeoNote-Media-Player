🇬🇧 English · 🇩🇪 Deutsch unten

## Download

| System | File |
|---|---|
| **Windows 10/11** | `NeoNote-Setup-1.3.2.exe` – run it and click through the installer. NeoNote 1.1.8 and newer offer this update by itself. |
| **Linux (all distributions)** | `NeoNote-1.3.2-x86_64.flatpak` – open it with a double-click (Discover, GNOME Software) or run `flatpak install --user NeoNote-1.3.2-x86_64.flatpak`. |
| **Linux (Arch, CachyOS, Manjaro …)** | `neonote-1.3.2-linux-arch.zip` – unpack it and run `./install.sh` in the folder. From now on NeoNote updates the Arch package itself. |

> The Flatpak is attached a few minutes after the release is published (it is built automatically). On first launch Windows may show “Windows protected your PC” because the installer isn't signed. Click “More info ▸ Run anyway” to continue.

### ✨ New features
- **Updates and beta channel for the Arch package:** if NeoNote was installed from the Arch zip, the updater now downloads new versions itself and installs them in a terminal window (makepkg asks for your password there), then restarts NeoNote. Test versions (beta) are now also available as an Arch zip.
- **Safe mode and crash report:** if NeoNote closes unexpectedly shortly after starting, it starts once in safe mode next time (without hardware video decoding, background blur and media controls) and shows a report to copy – on Windows including the entry from the Windows Event Viewer. Safe mode can also be turned on permanently (Settings ▸ About).
- **Open music and videos with NeoNote** like VLC does: the installer option (and the button under Settings ▸ System) now makes NeoNote the default for every format that has no app chosen yet. Formats you or Windows already assigned stay protected by Windows – those you switch by hand. You can pick which formats: music and videos separately or one by one – in the installer and later under Settings ▸ System. Suggested by Holgi in the Deskmodder forum.
- **Animated dialogs:** settings and other dialogs fade in and glide up slightly when opening, and fade out when closing (Settings ▸ Appearance, can be turned off).
- **Update progress:** when NeoNote updates itself, a small window in the installer's look now shows the progress instead of nothing happening until NeoNote restarts.
- **Start in the background when signing in** (Settings ▸ System): NeoNote loads invisibly into the system tray when you sign in – clicking NeoNote then opens the window instantly. Closing only hides it; quit from the tray icon's menu.
- **What's new after an update:** after updating, NeoNote shows once what's new in this version (Settings ▸ About, can be turned off). “What's new?” in the update bar now starts right with the changes. Both are sorted into “New features”, “Improvements” and “Bug fixes”.
- **Uninstall:** like VLC, the uninstaller now offers to also delete your library, playlists, settings and cached covers (default: keep everything; music and video files are never touched). Suggested by Holgi in the Deskmodder forum.
- **Smoother window moving on older PCs (Windows):** Settings ▸ Appearance ▸ “Pause blur while moving the window” – the blur is switched off only while dragging or resizing.
- **Beta channel:** Settings ▸ System or ▸ About ▸ “Also offer test versions (beta)” – the updater then also offers test versions before they are officially released.

### ⚡ Improvements
- Tooltips look lighter: more translucent, finer border, properly rounded corners on Windows too (without the hard Windows shadow).
- Tooltips are now off by default (Settings ▸ Appearance ▸ “Show tooltips when hovering with the mouse”).
- Test versions show “Beta” next to the version number.
- **Faster start:** the finished library (albums, compilations, editions) is kept in a quick-start cache – with large libraries the library step takes only about a third of the time.
- **Instant start feedback (Windows):** a start screen appears right when you click NeoNote, before Python and Qt are loaded – previously nothing happened for about two seconds.
- **Reopening a running NeoNote is much faster (Windows):** it hands over to the running instance before loading Qt – especially noticeable with “Start in the background when signing in” and when opening files.

### 🐞 Bug fixes
- Arch zip: `./install.sh` stopped with “en.json was not found” (1.3.1). Fixed.
- Windows: after installing or updating, an empty folder “NeoNote-Setup.tmp” could be left behind in “Program Files”. The installer now removes it reliably; the uninstaller also cleans up leftovers from older versions. Reported by Holgi in the Deskmodder forum.
- Appearance: changing colors or the blur reacted slowly. The blur now switches instantly, and color changes no longer reload every cover from disk.
- Settings open faster: the audio device list and file associations load right after the window appears.
- Settings: the window opens at its usual size again and can be made smaller; long tabs scroll instead of being squeezed.
- **Frozen NeoNote in the background (Windows):** if a running (e.g. preloaded) NeoNote no longer responds, clicking NeoNote used to do nothing at all. NeoNote now notices this after a few seconds and offers to end the frozen instance and start fresh.
- The start screen shown on click is now closed again as a safety measure if it stays up for some reason; dialogs always close even if their fade-out animation gets stuck.

---

## Download

| System | Datei |
|---|---|
| **Windows 10/11** | `NeoNote-Setup-1.3.2.exe` – starten und den Installer durchklicken. NeoNote ab 1.1.8 bietet dieses Update von selbst an. |
| **Linux (alle Distributionen)** | `NeoNote-1.3.2-x86_64.flatpak` – per Doppelklick öffnen (Discover, GNOME Software) oder `flatpak install --user NeoNote-1.3.2-x86_64.flatpak` ausführen. |
| **Linux (Arch, CachyOS, Manjaro …)** | `neonote-1.3.2-linux-arch.zip` – entpacken und im Ordner `./install.sh` ausführen. Ab jetzt aktualisiert NeoNote das Arch-Paket selbst. |

> Das Flatpak wird ein paar Minuten nach der Veröffentlichung angehängt (es wird automatisch gebaut). Beim ersten Start zeigt Windows eventuell „Der Computer wurde durch Windows geschützt“, weil der Installer nicht signiert ist. Mit „Weitere Informationen ▸ Trotzdem ausführen“ geht es weiter.

### ✨ Neue Funktionen
- **Updates und Beta-Kanal für das Arch-Paket:** Wurde NeoNote über die Arch-Zip installiert, lädt der Updater neue Versionen jetzt selbst und installiert sie in einem Terminalfenster (makepkg fragt dort nach dem Passwort), danach startet NeoNote neu. Testversionen (Beta) gibt es jetzt auch als Arch-Zip.
- **Sicherer Modus und Absturzbericht:** Endet NeoNote kurz nach dem Start unerwartet, startet es beim nächsten Mal einmal im sicheren Modus (ohne Hardware-Videodecodierung, Weichzeichner und Mediensteuerung) und zeigt einen Bericht zum Kopieren – unter Windows samt Eintrag aus der Ereignisanzeige. Der sichere Modus lässt sich auch dauerhaft einschalten (Einstellungen ▸ Über).
- **Musik und Videos mit NeoNote öffnen** wie bei VLC: Die Option im Installer (und der Knopf unter Einstellungen ▸ System) macht NeoNote jetzt zum Standard für alle Formate, für die noch kein Programm gewählt ist. Formate, die du oder Windows schon zugeordnet habt, schützt Windows – die stellst du von Hand um. Welche Formate, lässt sich auswählen: Musik und Videos getrennt oder einzeln – im Installer und später unter Einstellungen ▸ System. Ein Hinweis von Holgi aus dem Deskmodder-Forum.
- **Animierte Dialoge:** Einstellungen und andere Dialoge blenden sich beim Öffnen weich ein und gleiten leicht nach oben, beim Schließen blenden sie aus (Einstellungen ▸ Darstellung, abschaltbar).
- **Update-Fortschritt:** Aktualisiert sich NeoNote selbst, zeigt jetzt ein kleines Fenster im Look des Installers den Fortschritt – vorher passierte bis zum Neustart sichtbar nichts.
- **Beim Anmelden im Hintergrund starten** (Einstellungen ▸ System): NeoNote lädt beim Anmelden unsichtbar in die Systemleiste – ein Klick auf NeoNote öffnet das Fenster dann sofort. Schließen versteckt es nur, beendet wird über das Menü des Symbols.
- **Neuerungen nach einem Update:** Nach dem Aktualisieren zeigt NeoNote einmal, was in dieser Version neu ist (Einstellungen ▸ Über, abschaltbar). „Was ist neu?“ in der Update-Leiste beginnt jetzt direkt mit den Neuerungen. Beides ist in „Neue Funktionen“, „Verbesserungen“ und „Behobene Fehler“ gegliedert.
- **Deinstallation:** Wie bei VLC bietet der Deinstaller jetzt an, auch Bibliothek, Wiedergabelisten, Einstellungen und zwischengespeicherte Cover zu löschen (Standard: alles behalten; Musik- und Videodateien werden nie angefasst). Ein Hinweis von Holgi aus dem Deskmodder-Forum.
- **Flüssigeres Verschieben auf älteren Rechnern (Windows):** Einstellungen ▸ Darstellung ▸ „Weichzeichner beim Verschieben pausieren“ – der Weichzeichner ist nur während des Ziehens oder Größenänderns aus.
- **Beta-Kanal:** Einstellungen ▸ System oder ▸ Über ▸ „Auch Testversionen (Beta) anbieten“ – der Updater bietet dann auch Testversionen an, bevor sie offiziell erscheinen.

### ⚡ Verbesserungen
- Kurzinfos wirken zarter: durchscheinender, feinerer Rand, auch unter Windows sauber runde Ecken (ohne den harten Windows-Schatten).
- Kurzinfos sind jetzt standardmäßig aus (Einstellungen ▸ Darstellung ▸ „Kurzinfos beim Darüberfahren mit der Maus anzeigen“).
- Testversionen zeigen „Beta“ hinter der Versionsnummer.
- **Schnellerer Start:** Die fertig sortierte Bibliothek (Alben, Sampler, Editionen) liegt in einem Schnellstart-Zwischenspeicher – bei großen Bibliotheken dauert dieser Schritt nur noch etwa ein Drittel.
- **Sofortige Rückmeldung beim Start (Windows):** Ein Startbild erscheint direkt beim Klick auf NeoNote, noch bevor Python und Qt geladen sind – vorher passierte rund zwei Sekunden lang nichts.
- **Ein laufendes NeoNote öffnet sich viel schneller (Windows):** Es übergibt an die laufende Instanz, bevor Qt geladen wird – spürbar vor allem mit „Beim Anmelden im Hintergrund starten“ und beim Öffnen von Dateien.

### 🐞 Behobene Fehler
- Arch-Zip: `./install.sh` brach mit „en.json wurde nicht gefunden“ ab (1.3.1). Behoben.
- Windows: Nach dem Installieren oder Aktualisieren konnte ein leerer Ordner „NeoNote-Setup.tmp“ in „Programme“ zurückbleiben. Der Installer entfernt ihn jetzt zuverlässig, der Deinstaller räumt auch Reste älterer Versionen weg. Gemeldet von Holgi im Deskmodder-Forum.
- Darstellung: Farbwechsel und Weichzeichner reagierten träge. Der Weichzeichner schaltet jetzt sofort um, und bei Farbwechseln liest NeoNote nicht mehr alle Cover neu von der Platte.
- Einstellungen öffnen schneller: Geräteliste und Dateizuordnung laden erst direkt nach dem Öffnen.
- Einstellungen: Das Fenster öffnet wieder in der gewohnten Größe und lässt sich kleiner ziehen; lange Reiter scrollen, statt gequetscht zu werden.
- **Hängendes NeoNote im Hintergrund (Windows):** Reagierte ein laufendes (z. B. vorgeladenes) NeoNote nicht mehr, passierte beim Klick auf NeoNote einfach gar nichts. Jetzt merkt NeoNote das nach ein paar Sekunden und bietet an, die hängende Instanz zu beenden und neu zu starten.
- Das Startbild beim Klick wird zur Sicherheit noch einmal geschlossen, falls es aus irgendeinem Grund stehen bleibt; Dialoge schließen sich auch dann, wenn ihre Ausblend-Animation hängt.
