🇬🇧 English · 🇩🇪 Deutsch unten

## Download

| System | File |
|---|---|
| **Windows 10/11** | `NeoNote-Setup-1.3.3.exe` – run it and click through the installer. NeoNote 1.1.8 and newer offer this update by itself. |
| **Linux (all distributions)** | `NeoNote-1.3.3-x86_64.flatpak` – open it with a double-click (Discover, GNOME Software) or run `flatpak install --user NeoNote-1.3.3-x86_64.flatpak`. |
| **Linux (Arch, CachyOS, Manjaro …)** | `neonote-1.3.3-linux-arch.zip` – unpack it and run `./install.sh` in the folder. NeoNote 1.3.2 and newer installed from the Arch zip offer this update by itself. |

> The Flatpak is attached a few minutes after the release is published (it is built automatically). On first launch Windows may show “Windows protected your PC” because the installer isn't signed. Click “More info ▸ Run anyway” to continue.

### ✨ New features
- **8 new languages:** French, Spanish, Italian, Dutch, Polish, Portuguese (Brazil), Russian and Turkish. With “Automatic (system language)”, NeoNote picks your system language by itself; you can also choose it under Settings ▸ Appearance ▸ Language. The translations were made with AI – if you are a native speaker and spot something odd, corrections are very welcome (GitHub issue or pull request on `i18n/<language>.json`).
- **Casting – DLNA, Chromecast and AirPlay:** the new cast button next to the volume slider plays music and videos on devices in your home network – AV receivers (e.g. Yamaha MusicCast), smart TVs, Chromecast/Google TV, network speakers and AirPlay speakers. NeoNote finds them by itself and becomes the remote: play/pause, skip, seeking and volume control the device, the next track follows automatically, and title, artist and cover appear on the device. “Continue on this PC” switches back at the same position. AirPlay: music only, for devices that accept unencrypted streaming (devices that require pairing are shown as not supported). Firewall: on Windows the installer allows NeoNote for your home network automatically; on Linux NeoNote detects an active firewall (ufw, firewalld) and opens it with one click and your password – on first use it offers this by itself (also in Settings ▸ System). Tested with a Yamaha MusicCast receiver via DLNA and AirPlay; Chromecast has not yet been tested on a real device – feedback welcome. Suggested by Holgi in the Deskmodder forum.

### ⚡ Improvements
- “Always on top” now uses **Ctrl+Alt+T** (Ctrl+Shift+T is “reopen closed tab” in browsers and was easy to hit by accident), and a short hint shows when it is switched on or off. Thanks to Holgi from the Deskmodder forum, whose reports led to this.
- Tooltips can now be switched separately: on buttons and icons (on by default) and on tracks and albums in lists (off by default) – Settings ▸ Appearance.

### 🐞 Bug fixes
- “Always on top” is only restored a few seconds after startup, once NeoNote is running smoothly – if it froze at startup, a frozen window could otherwise cover everything. In safe mode it stays off. Also, with “always on top”, dialogs (settings, “What’s new?” …) opened behind the main window and blocked it – NeoNote looked frozen. Dialogs now open on top, and for the Windows settings NeoNote steps back until you return. Reported by Holgi in the Deskmodder forum.
- Windows: “Default apps ▸ NeoNote” no longer shows an empty page when file associations are switched off – leftovers of earlier installations are removed.

---

## Download

| System | Datei |
|---|---|
| **Windows 10/11** | `NeoNote-Setup-1.3.3.exe` – starten und den Installer durchklicken. NeoNote ab 1.1.8 bietet dieses Update von selbst an. |
| **Linux (alle Distributionen)** | `NeoNote-1.3.3-x86_64.flatpak` – per Doppelklick öffnen (Discover, GNOME Software) oder `flatpak install --user NeoNote-1.3.3-x86_64.flatpak` ausführen. |
| **Linux (Arch, CachyOS, Manjaro …)** | `neonote-1.3.3-linux-arch.zip` – entpacken und im Ordner `./install.sh` ausführen. Über die Arch-Zip installiertes NeoNote ab 1.3.2 bietet dieses Update von selbst an. |

> Das Flatpak wird ein paar Minuten nach der Veröffentlichung angehängt (es wird automatisch gebaut). Beim ersten Start zeigt Windows eventuell „Der Computer wurde durch Windows geschützt“, weil der Installer nicht signiert ist. Mit „Weitere Informationen ▸ Trotzdem ausführen“ geht es weiter.

### ✨ Neue Funktionen
- **8 neue Sprachen:** Französisch, Spanisch, Italienisch, Niederländisch, Polnisch, Portugiesisch (Brasilien), Russisch und Türkisch. Mit „Automatisch (Systemsprache)“ wählt NeoNote die Sprache des Systems selbst; einstellen lässt sie sich auch unter Einstellungen ▸ Darstellung ▸ Sprache. Die Übersetzungen wurden mit KI erstellt – wer die Sprache als Muttersprache spricht und etwas Holpriges findet: Korrekturen sind sehr willkommen (GitHub-Issue oder Pull-Request auf `i18n/<sprache>.json`).
- **Streamen – DLNA, Chromecast und AirPlay:** Der neue Streamen-Knopf neben der Lautstärke spielt Musik und Videos auf Geräten im Heimnetz ab – AV-Receiver (z. B. Yamaha MusicCast), Smart-TVs, Chromecast/Google TV, Netzwerk- und AirPlay-Lautsprecher. NeoNote findet sie selbst und wird zur Fernbedienung: Play/Pause, Weiter, Springen und Lautstärke steuern das Gerät, der nächste Titel folgt automatisch, Titel, Interpret und Cover erscheinen am Gerät. „Auf diesem PC weiterhören“ schaltet an derselben Stelle zurück. AirPlay: nur Musik, für Geräte, die unverschlüsselte Übertragung annehmen (Geräte mit Pflicht-Kopplung werden als nicht unterstützt angezeigt). Firewall: Unter Windows gibt der Installer NeoNote automatisch fürs Heimnetz frei; unter Linux erkennt NeoNote eine aktive Firewall (ufw, firewalld) und gibt sie mit einem Klick und deinem Passwort frei – beim ersten Mal bietet es das von selbst an (auch unter Einstellungen ▸ System). Getestet mit einem Yamaha-MusicCast-Receiver über DLNA und AirPlay; Chromecast ist noch nicht an einem echten Gerät getestet – Rückmeldungen willkommen. Ein Wunsch von Holgi aus dem Deskmodder-Forum.

### ⚡ Verbesserungen
- „Immer im Vordergrund“ hat jetzt das Kürzel **Strg+Alt+T** (Strg+Umschalt+T ist im Browser „geschlossenen Tab öffnen“ und wurde leicht versehentlich gedrückt), und ein kurzer Hinweis zeigt an, wenn es ein- oder ausgeschaltet wird. Danke an Holgi aus dem Deskmodder-Forum, dessen Meldungen dazu geführt haben.
- Kurzinfos lassen sich jetzt getrennt schalten: über Knöpfen und Symbolen (standardmäßig an) und über Titeln und Alben in Listen (standardmäßig aus) – Einstellungen ▸ Darstellung.

### 🐞 Behobene Fehler
- „Immer im Vordergrund“ wird beim Start erst nach ein paar Sekunden wiederhergestellt, wenn NeoNote flüssig läuft – fror es beim Start ein, lag sonst ein hängendes Fenster über allem. Im sicheren Modus bleibt es aus. Außerdem öffneten sich bei „Immer im Vordergrund“ Dialoge (Einstellungen, „Was ist neu?“ …) hinter dem Hauptfenster und sperrten es – NeoNote wirkte eingefroren. Dialoge erscheinen jetzt obenauf, und für die Windows-Einstellungen tritt NeoNote zurück, bis du wieder hineinklickst. Gemeldet von Holgi im Deskmodder-Forum.
- Windows: „Standard-Apps ▸ NeoNote“ zeigt keine leere Seite mehr, wenn die Verknüpfungen aus sind – Reste früherer Installationen werden entfernt.
