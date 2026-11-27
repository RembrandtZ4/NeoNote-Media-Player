🧪 **Beta / test version** · 🇩🇪 Deutsch unten

This is a **test version** for everyone who wants to try new features early. It may still contain bugs. The regular version is still [1.3.2](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/latest).

**Download:**
- **Windows 10/11:** `NeoNote-Setup-1.3.2.90.exe` – install over your existing NeoNote, settings and library are kept.
- **Arch Linux / CachyOS:** `neonote-1.3.2.90-linux-arch.zip` – unpack and run `./install.sh`. With 1.3.2 or newer, NeoNote offers this update itself once test versions are enabled.
- **Flatpak:** test builds are available in the [test](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/tag/test) pre-release.

**Get test versions automatically:** Settings ▸ System (or ▸ About) ▸ “Also offer test versions (beta)”.

### ✨ New features
- **Casting – DLNA, Chromecast and AirPlay:** the new cast button next to the volume slider plays music and videos on devices in your home network – AV receivers (e.g. Yamaha MusicCast), smart TVs, Chromecast/Google TV, network speakers and AirPlay speakers. NeoNote finds them by itself and becomes the remote: play/pause, skip, seeking and volume control the device, the next track follows automatically, and title, artist and cover appear on the device. “Continue on this PC” switches back at the same position. AirPlay: music only, for devices that accept unencrypted streaming (devices that require pairing are shown as not supported). Firewall: on Windows the installer allows NeoNote for your home network automatically; on Linux NeoNote detects an active firewall (ufw, firewalld) and opens it with one click and your password – on first use it offers this by itself (also in Settings ▸ System). Suggested by Holgi in the Deskmodder forum.

### ⚡ Improvements
- “Always on top” now uses **Ctrl+Alt+T** (Ctrl+Shift+T is “reopen closed tab” in browsers and was easy to hit by accident), and a short hint shows when it is switched on or off.
- Tooltips can now be switched separately: on buttons and icons (on by default) and on tracks and albums in lists (off by default) – Settings ▸ Appearance.

### 🐞 Bug fixes
- “Always on top” is only restored a few seconds after startup, once NeoNote is running smoothly – if it froze at startup, a frozen window could otherwise cover everything. In safe mode it stays off. Also, with “always on top”, dialogs (settings, “What’s new?” …) opened behind the main window and blocked it – NeoNote looked frozen. Dialogs now open on top, and for the Windows settings NeoNote steps back until you return. Reported by Holgi in the Deskmodder forum.
- Windows: “Default apps ▸ NeoNote” no longer shows an empty page when file associations are switched off – leftovers of earlier installations are removed.

---

🧪 **Beta / Testversion**

Das ist eine **Testversion** für alle, die neue Funktionen früh ausprobieren möchten. Sie kann noch Fehler enthalten. Die reguläre Version ist weiterhin [1.3.2](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/latest).

**Download:**
- **Windows 10/11:** `NeoNote-Setup-1.3.2.90.exe` – einfach über das vorhandene NeoNote installieren, Einstellungen und Bibliothek bleiben erhalten.
- **Arch Linux / CachyOS:** `neonote-1.3.2.90-linux-arch.zip` – entpacken und `./install.sh` ausführen. Ab 1.3.2 bietet NeoNote dieses Update selbst an, wenn Testversionen eingeschaltet sind.
- **Flatpak:** Testpakete gibt es in der Vorabversion [test](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/tag/test).

**Testversionen automatisch bekommen:** Einstellungen ▸ System (oder ▸ Über) ▸ „Auch Testversionen (Beta) anbieten“.

### ✨ Neue Funktionen
- **Casting – DLNA, Chromecast und AirPlay:** Der neue Cast-Knopf neben der Lautstärke spielt Musik und Videos auf Geräten im Heimnetz ab – AV-Receiver (z. B. Yamaha MusicCast), Smart-TVs, Chromecast/Google TV, Netzwerk- und AirPlay-Lautsprecher. NeoNote findet sie selbst und wird zur Fernbedienung: Play/Pause, Weiter, Springen und Lautstärke steuern das Gerät, der nächste Titel folgt automatisch, Titel, Interpret und Cover erscheinen am Gerät. „Auf diesem PC weiterhören“ schaltet an derselben Stelle zurück. AirPlay: nur Musik, für Geräte, die unverschlüsselte Übertragung annehmen (Geräte mit Pflicht-Kopplung werden als nicht unterstützt angezeigt). Firewall: Unter Windows gibt der Installer NeoNote automatisch fürs Heimnetz frei; unter Linux erkennt NeoNote eine aktive Firewall (ufw, firewalld) und gibt sie mit einem Klick und deinem Passwort frei – beim ersten Mal bietet es das von selbst an (auch unter Einstellungen ▸ System). Ein Wunsch von Holgi aus dem Deskmodder-Forum.

### ⚡ Verbesserungen
- „Immer im Vordergrund“ hat jetzt das Kürzel **Strg+Alt+T** (Strg+Umschalt+T ist im Browser „geschlossenen Tab öffnen“ und wurde leicht versehentlich gedrückt), und ein kurzer Hinweis zeigt an, wenn es ein- oder ausgeschaltet wird.
- Kurzinfos lassen sich jetzt getrennt schalten: über Knöpfen und Symbolen (standardmäßig an) und über Titeln und Alben in Listen (standardmäßig aus) – Einstellungen ▸ Darstellung.

### 🐞 Behobene Fehler
- „Immer im Vordergrund“ wird beim Start erst nach ein paar Sekunden wiederhergestellt, wenn NeoNote flüssig läuft – fror es beim Start ein, lag sonst ein hängendes Fenster über allem. Im sicheren Modus bleibt es aus. Außerdem öffneten sich bei „Immer im Vordergrund“ Dialoge (Einstellungen, „Was ist neu?“ …) hinter dem Hauptfenster und sperrten es – NeoNote wirkte eingefroren. Dialoge erscheinen jetzt obenauf, und für die Windows-Einstellungen tritt NeoNote zurück, bis du wieder hineinklickst. Gemeldet von Holgi im Deskmodder-Forum.
- Windows: „Standard-Apps ▸ NeoNote“ zeigt keine leere Seite mehr, wenn die Verknüpfungen aus sind – Reste früherer Installationen werden entfernt.
