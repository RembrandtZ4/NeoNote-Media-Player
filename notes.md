🧪 **Beta / test version** · 🇩🇪 Deutsch unten

This is a **test version** for everyone who wants to try new features early. It may still contain bugs. The regular version is still [1.3.3](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/latest).

**Download:**
- **Windows 10/11:** `NeoNote-Setup-1.3.3.91.exe` – install over your existing NeoNote, settings and library are kept.
- **Arch Linux / CachyOS:** `neonote-1.3.3.91-linux-arch.zip` – unpack and run `./install.sh`. With 1.3.2 or newer, NeoNote offers this update itself once test versions are enabled.
- **Flatpak:** test builds are available in the [test](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/tag/test) pre-release.

**Get test versions automatically:** Settings ▸ System (or ▸ About) ▸ “Also offer test versions (beta)”.

### ⚡ Improvements
- **Log viewer** (Organize ▸ Show log…): shows live what NeoNote records during playback and casting – with “Copy all” for bug reports. No terminal needed anymore.
- **Better search:** searching in the Artist, Album, Genre and Folder views now finds songs too (before, only artist and album names). Several words can be combined across fields (“queen bohemian”), accents and punctuation no longer matter (“beyonce” finds Beyoncé, “acdc” finds AC/DC, “sweet child o mine” finds “Sweet Child o' Mine”), and “No results” is shown instead of an empty view.
- **Picture quality** (Settings ▸ Video): “High” uses sharper scaling filters, smooths banding in color gradients and converts HDR more accurately – for videos played with mpv, takes effect immediately. Default stays “Default”, as it needs a stronger graphics card.

### 🐞 Bug fixes
- **Windows: DLNA devices were not found** (e.g. a Yamaha receiver showed up only via AirPlay): NeoNote now sends the search on every network adapter explicitly. The search result is noted in the log.
- **Casting: jumping within some M4A files restarted the track** (e.g. long mixes whose index sits at the end of the file): NeoNote now delivers such files to the device with the index in front. The file on your disk stays unchanged.
- **Waveform and visualization now also work while casting** (DLNA, AirPlay, Chromecast). Before, they stayed empty because the device plays the sound.
- **Casting stopped after a few minutes** (DLNA and AirPlay, e.g. with Yamaha receivers): over AirPlay, NeoNote now reports the track progress every few seconds like iTunes does – without it, the Yamaha hung up after about 7 minutes. If a device still hangs up, NeoNote reconnects within seconds and continues at the same spot. Over DLNA, NeoNote asks the device for its status half as often, and if it stops mid-track after playing for a while, NeoNote restarts it at the same spot. Streaming problems are now also noted in the log.
- Tooltips with longer text (e.g. on the info and casting buttons) were cut off at the right edge. Fixed.

---

🧪 **Beta / Testversion**

Das ist eine **Testversion** für alle, die neue Funktionen früh ausprobieren möchten. Sie kann noch Fehler enthalten. Die reguläre Version ist weiterhin [1.3.3](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/latest).

**Download:**
- **Windows 10/11:** `NeoNote-Setup-1.3.3.91.exe` – einfach über das vorhandene NeoNote installieren, Einstellungen und Bibliothek bleiben erhalten.
- **Arch Linux / CachyOS:** `neonote-1.3.3.91-linux-arch.zip` – entpacken und `./install.sh` ausführen. Ab 1.3.2 bietet NeoNote dieses Update selbst an, sobald Testversionen eingeschaltet sind.
- **Flatpak:** Testversionen gibt es in der Vorabversion [test](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases/tag/test).

**Testversionen automatisch erhalten:** Einstellungen ▸ System (oder ▸ Über) ▸ „Auch Testversionen (Beta) anbieten“.

### ⚡ Verbesserungen
- **Protokoll anzeigen** (Organisieren ▸ Protokoll anzeigen…): zeigt live, was NeoNote beim Abspielen und Streamen mitschreibt – mit „Alles kopieren“ für Fehlerberichte. Kein Terminal mehr nötig.
- **Bessere Suche:** In den Ansichten Interpret, Album, Genre und Ordner findet die Suche jetzt auch Songs (vorher nur Namen von Interpreten und Alben). Mehrere Wörter lassen sich über Felder hinweg kombinieren („queen bohemian“), Akzente und Satzzeichen spielen keine Rolle mehr („beyonce“ findet Beyoncé, „acdc“ findet AC/DC, „sweet child o mine“ findet „Sweet Child o' Mine“), und statt einer leeren Ansicht erscheint „Keine Treffer“.
- **Bildqualität** (Einstellungen ▸ Video): „Hoch“ nutzt schärfere Skalierfilter, glättet Streifen in Farbverläufen und rechnet HDR genauer um – für Videos über mpv, wirkt sofort. Voreingestellt bleibt „Standard“, weil „Hoch“ eine stärkere Grafikkarte braucht.

### 🐞 Behobene Fehler
- **Windows: DLNA-Geräte wurden nicht gefunden** (z. B. erschien ein Yamaha-Receiver nur über AirPlay): NeoNote schickt die Suche jetzt ausdrücklich über jeden Netzwerkadapter. Das Ergebnis der Suche steht im Protokoll.
- **Streamen: Springen in manchen M4A-Dateien startete den Titel von vorn** (z. B. lange Mixe, deren Inhaltsverzeichnis am Dateiende steht): NeoNote liefert solche Dateien dem Gerät jetzt mit dem Inhaltsverzeichnis vorne aus. Die Datei auf der Festplatte bleibt unverändert.
- **Waveform und Visualisierung funktionieren jetzt auch beim Streamen** (DLNA, AirPlay, Chromecast). Vorher blieben sie leer, weil das Gerät den Ton abspielt.
- **Streamen brach nach ein paar Minuten ab** (DLNA und AirPlay, z. B. bei Yamaha-Receivern): Über AirPlay meldet NeoNote dem Gerät jetzt alle paar Sekunden den Fortschritt des Titels, so wie iTunes – ohne das hat der Yamaha nach etwa 7 Minuten aufgelegt. Legt ein Gerät trotzdem auf, verbindet NeoNote sich innerhalb weniger Sekunden neu und spielt an derselben Stelle weiter. Über DLNA fragt NeoNote den Status nur noch halb so oft ab, und hört das Gerät nach einer Weile mitten im Titel auf, startet NeoNote an derselben Stelle neu. Probleme beim Streamen stehen jetzt auch im Protokoll.
- Kurzinfos mit längerem Text (z. B. an den Knöpfen für Infos und Streamen) wurden am rechten Rand abgeschnitten. Behoben.
