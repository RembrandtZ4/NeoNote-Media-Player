# Roadmap

🇬🇧 English | 🇩🇪 Deutsch weiter unten

Planned ideas for upcoming versions. The focus is on **Linux** (KDE Plasma). The order is rough, not binding. More ideas are welcome as an [issue](https://github.com/RembrandtZ4/NeoNote-Media-Player/issues/new/choose).

## Version 1.2 – released 2026-11-20
- [x] **Videos via mpv** – rendering on the GPU: smooth 4K, HDR on regular screens, image subtitles (PGS/VobSub) from Blu-rays and DVDs
- [x] **Resume where you left off** for audiobooks, podcasts and long videos, chapter navigation
- [x] **Sleep timer** (“after 30 minutes”, “after this album”)
- [x] **Smart playlists** with custom rules (e.g. “80s rock, at least 4 stars, not played for 3 months”) – like in Windows Media Player 12
- [x] **Lyrics**, synced in “Now playing” mode (e.g. via LRCLIB) and from the files themselves
- [x] **Transparent dialogs** (settings, equalizer …) with their own title bar and the same blur as the main window – one continuous surface on Windows and KDE
- [x] **Flatpak** – for Ubuntu, Fedora, Mint and other distributions (Flathub listing to follow)

## Version 1.3 – released 2026-11-23
- [x] **Crossfade** between tracks
- [x] **Playback speed** for audiobooks and videos
- [x] **Audio output selection** and bit-perfect playback (e.g. for external DACs)
- [x] **Folder view** – browse your music folders
- [x] **Rename and organize files** using patterns like “Artist/Album/No. Title”
- [x] **Scrobbling** to Last.fm and ListenBrainz
- [x] **Artist info** in “Now playing” – biography and similar artists
- [x] **Visualization** like in Windows Media Player
- [x] **Auto DJ** – endless matching music from your own collection
- [x] **Star ratings in the music files** (WMP-compatible)

## Version 1.3.2 – released 2026-11-26
- [x] **Faster start** – quick-start cache for the library, instant start screen and optional preloading at login (starts hidden in the tray, the window then appears instantly)
- [x] **Open music and videos with NeoNote** like VLC – pick the formats in the installer and in the settings
- [x] **Beta channel** – try test versions early, on Windows and as an Arch zip
- [x] **Safe mode and crash report** – if something goes wrong at start, NeoNote helps itself and shows a report to copy
- [x] **What's new after an update**, animated dialogs, and the uninstaller can remove personal data on request

## Next
- [ ] **Jellyfin security:** store the access token in the system's password store (Windows Credential Manager, KWallet) and warn before signing in over unencrypted `http://` outside the home network
- [ ] **AUR package** – install with `yay -S neonote` (ready; waiting for AUR registration to reopen)
- [ ] **Native Wayland** with KDE's own blur (sharper with fractional scaling)
- [ ] **Flathub** listing

## Later
- [ ] **Casting** to Chromecast, AirPlay and DLNA/UPnP devices (TVs, speakers, AV receivers)
- [ ] **Remote control** – control NeoNote on the PC from your phone via a simple web page on the home network (no app needed)

## Earlier
- [x] **Updater for Windows** – install new versions right from NeoNote *(since 1.1.8)*

---

# Roadmap (Deutsch)

Geplante Ideen für kommende Versionen. Der Schwerpunkt liegt auf **Linux** (KDE Plasma). Die Reihenfolge ist grob, nicht verbindlich. Weitere Wünsche gern als [Issue](https://github.com/RembrandtZ4/NeoNote-Media-Player/issues/new/choose).

## Version 1.2 – erschienen am 20.11.2026
- [x] **Videos über mpv** – Darstellung auf der Grafikkarte: flüssiges 4K, HDR auf normalen Bildschirmen, Bild-Untertitel (PGS/VobSub) von Blu-rays und DVDs
- [x] **Weiterhören an der letzten Stelle** bei Hörbüchern, Podcasts und langen Videos, Kapitelsprünge
- [x] **Einschlaf-Timer** („nach 30 Minuten“, „nach diesem Album“)
- [x] **Intelligente Wiedergabelisten** mit eigenen Regeln (z. B. „Rock aus den 80ern, mindestens 4 Sterne, seit 3 Monaten nicht gespielt“) – wie in Windows Media Player 12
- [x] **Songtexte**, zeitgesteuert im „Wird gespielt“-Modus (z. B. über LRCLIB) und aus den Dateien selbst
- [x] **Transparente Dialoge** (Einstellungen, Equalizer …) mit eigener Titelleiste und demselben Weichzeichner wie das Hauptfenster – eine durchgehende Fläche unter Windows und KDE
- [x] **Flatpak** – für Ubuntu, Fedora, Mint und andere Distributionen (Aufnahme in Flathub folgt später)

## Version 1.3 – erschienen am 23.11.2026
- [x] **Überblenden** zwischen Titeln
- [x] **Wiedergabegeschwindigkeit** für Hörbücher und Videos
- [x] **Eigene Audioausgabe** und bitgenaue Wiedergabe (z. B. für externe DACs)
- [x] **Ordneransicht** – durch die Musikordner stöbern
- [x] **Dateien umbenennen und einsortieren** nach Mustern wie „Interpret/Album/Nr. Titel“
- [x] **Scrobbeln** zu Last.fm und ListenBrainz
- [x] **Infos zum Interpreten** in „Wird gespielt“ – Biografie und ähnliche Künstler
- [x] **Visualisierung** wie im Windows Media Player
- [x] **Auto-DJ** – endlos passende Musik aus der eigenen Sammlung
- [x] **Sternbewertungen in den Musikdateien** (kompatibel mit WMP)

## Version 1.3.2 – erschienen am 26.11.2026
- [x] **Schnellerer Start** – Schnellstart-Speicher für die Bibliothek, sofortiges Startbild und auf Wunsch Vorladen beim Anmelden (startet unsichtbar im Infobereich, das Fenster erscheint dann sofort)
- [x] **Musik und Videos mit NeoNote öffnen** wie bei VLC – Formate im Installer und in den Einstellungen wählbar
- [x] **Beta-Kanal** – Testversionen früh ausprobieren, unter Windows und als Arch-Zip
- [x] **Sicherer Modus und Absturzbericht** – geht beim Start etwas schief, hilft sich NeoNote selbst und zeigt einen Bericht zum Kopieren
- [x] **Neuerungen nach einem Update**, animierte Dialoge, und der Deinstaller entfernt auf Wunsch die persönlichen Daten

## Als Nächstes
- [ ] **Jellyfin-Sicherheit:** den Zugangsschlüssel im Passwortspeicher des Systems ablegen (Windows-Anmeldeinformationsverwaltung, KWallet) und vor einer Anmeldung über unverschlüsseltes `http://` außerhalb des Heimnetzes warnen
- [ ] **AUR-Paket** – Installation mit `yay -S neonote` (fertig vorbereitet; wartet darauf, dass das AUR die Registrierung wieder öffnet)
- [ ] **Natives Wayland** mit dem Weichzeichner von KDE (schärfer bei krummer Skalierung)
- [ ] **Aufnahme in Flathub**

## Später
- [ ] **Streamen (Cast)** zu Chromecast, AirPlay und DLNA/UPnP-Geräten (Fernseher, Lautsprecher, AV-Receiver)
- [ ] **Fernbedienung** – NeoNote am PC vom Handy aus steuern, über eine einfache Webseite im Heimnetz (ohne App)

## Früher
- [x] **Updater für Windows** – neue Versionen direkt aus NeoNote installieren *(seit 1.1.8)*
