🇬🇧 English · 🇩🇪 Deutsch unten

## Download

| System | File |
|---|---|
| **Windows 10/11** | `NeoNote-Setup-1.2.exe` – run it and click through the installer. NeoNote 1.1.8 and newer offer this update by itself. |
| **Linux (all distributions)** | `NeoNote-1.2-x86_64.flatpak` – open it with a double-click (Discover, GNOME Software) or run `flatpak install --user NeoNote-1.2-x86_64.flatpak`. |
| **Linux (Arch, CachyOS, Manjaro …)** | `neonote-1.2-linux-arch.zip` – unpack it and run `./install.sh` in the folder. |

> The Flatpak is attached a few minutes after the release is published (it is built automatically). On first launch Windows may show “Windows protected your PC” because the installer isn't signed. Click “More info ▸ Run anyway” to continue.

**New**
- **Videos via mpv:** videos now play through mpv, which renders directly on the graphics card – smooth 4K, HDR videos with correct colors on regular screens, hardware decoding via D3D11VA, VA-API or NVDEC. Image subtitles from Blu-rays and DVDs (PGS, VobSub) now work, as do .ass and .vtt subtitles. Subtitles move up while the control bar is visible. Can be turned off under Settings ▸ Video; without mpv, videos play through Qt Multimedia as before.
- **Lyrics** in “Now playing”: the cover moves to the left, the lyrics appear on the right. Synced lyrics scroll along with the current line highlighted; click a line to jump there, scroll with the mouse wheel. Sources in this order: a `.lrc` file with the same name next to the track, lyrics stored in the file (MP3, FLAC, OGG, M4A, WMA …), otherwise online from **LRCLIB** (can be turned off under Settings ▸ Online information). Toggle with the new button in the control bar or `Ctrl+T`. In the library the lyrics appear on the right below the playlist (height adjustable with the splitter). Right-click to save lyrics found online as a `.lrc` file next to the track.
- **Smart playlists** like in WMP12: rules for artist, album artist, album, title, genre, year, rating, play count, last played, date added, length, file type and folder – e.g. “genre contains rock” and “year between 1980 and 1989”, or “never played”. Match all or any rule, limit to a number of tracks or minutes, sort as you like (including random, reshuffled daily). The editor shows right away how many tracks match. The lists update themselves and appear with a lightning icon under Playlists (Organize ▸ “New smart playlist…” or right-click “Playlists”).
- **Sleep timer** (☰ menu and system tray): after 15, 30, 45, 60, 90 minutes or a custom time, after this track or after this album. At the end the volume fades out over 10 seconds and playback pauses – “Play” later continues at the same spot. While it runs, a moon in the control bar shows the remaining time; click it to change or stop the timer.
- **Dialogs in the window's look:** with the custom title bar, Settings, Equalizer, album info, confirmations and all other dialogs now have no system frame either, but their own title bar, rounded corners and the same translucent, blurred background as the main window (slightly more opaque so text stays readable). Move them by the title bar, resize at the edges. Can be turned off under Settings ▸ Appearance.
- **Resume:** long videos and audiobooks (20 minutes or more) remember where you stopped and continue there next time. If you watched almost to the end, it starts from the beginning. Can be turned off under Settings ▸ Video.
- **Chapters:** movies with chapters show a chapter list in the tracks menu; `Ctrl+PgDown` / `Ctrl+PgUp` jumps to the next or previous chapter.
- **Crash protection for videos:** if NeoNote crashes while starting a video, it decodes without hardware acceleration next time; if it crashes again, videos play through Qt Multimedia. A notice says what was changed. On Windows, mpv uses the stable copy modes (e.g. `d3d11va-copy`) – decoding still happens on the graphics card.
- If a video was open last, NeoNote no longer shows its still frame at startup; the video just sits in the queue and continues where you left off when played. To get the still frame back: Settings ▸ Video.
- **Flatpak** for all Linux systems (Fedora, Ubuntu, Mint, openSUSE, Steam Deck …): `NeoNote-1.2-x86_64.flatpak` is attached to the release; install with a double-click in Discover/GNOME Software or with `flatpak install`. Includes libmpv and everything else needed; NeoNote shows updates, which you install via Discover or `flatpak update`.

**Bug fixes**
- When editing directly in the track list (F2), the selected text was white on a light background and hard to read; the input field also cut off the text at the top and bottom.
- After a movie, the “Tracks” button stayed visible while listening to music.
- Library, statistics (ratings, play counts, “Recently played”), edits and playlists are now saved safely: first to a temporary file, then swapped, with the previous version kept as `.bak`. If NeoNote crashes while saving, nothing is lost – the backup is read at the next start.

---

## Download

| System | Datei |
|---|---|
| **Windows 10/11** | `NeoNote-Setup-1.2.exe` – starten und den Installer durchklicken. NeoNote ab 1.1.8 bietet dieses Update von selbst an. |
| **Linux (alle Distributionen)** | `NeoNote-1.2-x86_64.flatpak` – per Doppelklick öffnen (Discover, GNOME Software) oder `flatpak install --user NeoNote-1.2-x86_64.flatpak` ausführen. |
| **Linux (Arch, CachyOS, Manjaro …)** | `neonote-1.2-linux-arch.zip` – entpacken, im Ordner `./install.sh` ausführen. |

> Das Flatpak erscheint ein paar Minuten nach der Veröffentlichung (es wird automatisch gebaut). Beim ersten Start zeigt Windows eventuell „Der Computer wurde durch Windows geschützt“, weil der Installer nicht signiert ist. Mit „Weitere Informationen ▸ Trotzdem ausführen“ geht es weiter.

**Neu**
- **Videos über mpv:** Videos laufen jetzt über mpv, das direkt auf der Grafikkarte zeichnet – flüssiges 4K, HDR-Videos mit richtigen Farben auf normalen Bildschirmen, Hardware-Decodierung über D3D11VA, VA-API oder NVDEC. Bild-Untertitel von Blu-rays und DVDs (PGS, VobSub) funktionieren jetzt, ebenso .ass- und .vtt-Untertitel. Untertitel weichen nach oben aus, solange die Steuerleiste eingeblendet ist. Abschaltbar unter Einstellungen ▸ Video; ohne mpv laufen Videos wie bisher über Qt Multimedia.
- War zuletzt ein Video geöffnet, zeigt NeoNote beim Start nicht mehr dessen Standbild; das Video steht nur in der Warteschlange und setzt beim Abspielen an der letzten Stelle fort. Wer das Standbild wieder möchte: Einstellungen ▸ Video.
- **Absturzschutz für Videos:** Stürzt NeoNote beim Start eines Videos ab, decodiert es beim nächsten Mal ohne Hardwarebeschleunigung; passiert es dann wieder, laufen Videos über Qt Multimedia. Ein Hinweis sagt, was umgestellt wurde. Unter Windows nutzt mpv die stabilen Kopier-Modi (z. B. `d3d11va-copy`) – decodiert wird weiter auf der Grafikkarte.
- **Intelligente Wiedergabelisten** wie im WMP12: Regeln für Interpret, Albuminterpret, Album, Titel, Genre, Jahr, Bewertung, Wiedergaben, zuletzt gespielt, hinzugefügt, Länge, Dateityp und Ordner – z. B. „Genre enthält Rock“ und „Jahr zwischen 1980 und 1989“ oder „noch nie gespielt“. Alle oder mindestens eine Regel, begrenzbar auf eine Anzahl Titel oder Minuten, sortiert nach Wunsch (auch zufällig, täglich neu gemischt). Der Editor zeigt sofort, wie viele Titel passen. Die Listen aktualisieren sich von selbst und stehen mit Blitz-Symbol bei den Wiedergabelisten (Organisieren ▸ „Neue intelligente Wiedergabeliste…“ oder Rechtsklick auf „Wiedergabelisten“).
- **Einschlaf-Timer** (☰-Menü und Systemleiste): nach 15, 30, 45, 60, 90 Minuten oder einer eigenen Zeit, nach diesem Titel oder nach diesem Album. Am Ende wird die Lautstärke in 10 Sekunden ausgeblendet und die Wiedergabe angehalten – „Abspielen“ macht später an derselben Stelle weiter. Solange er läuft, zeigt ein Mond in der Steuerleiste die Restzeit; ein Klick darauf ändert oder beendet ihn.
- **Kapitel:** Filme mit Kapiteln zeigen im Spuren-Menü eine Kapitelliste; `Strg+Bild↓` / `Strg+Bild↑` springt zum nächsten bzw. vorherigen Kapitel.
- **Songtexte** in „Wird gespielt“: Das Cover rückt nach links, rechts steht der Text. Zeitgesteuerte Texte laufen mit, die aktuelle Zeile ist hervorgehoben; ein Klick auf eine Zeile springt dorthin, mit dem Mausrad lässt sich vor- und zurückblättern. Quellen in dieser Reihenfolge: eine `.lrc`-Datei mit gleichem Namen neben dem Titel, ein in der Datei gespeicherter Text (MP3, FLAC, OGG, M4A, WMA …), sonst online von **LRCLIB** (abschaltbar unter Einstellungen ▸ Online-Informationen). Ein- und ausblenden über den neuen Knopf in der Steuerleiste oder `Strg+T`. In der Bibliothek erscheint der Text rechts unter der Wiedergabeliste (Höhe per Teiler einstellbar), in „Wird gespielt“ groß neben dem Cover. Per Rechtsklick lässt sich ein gefundener Online-Text als `.lrc` neben dem Titel speichern.
- **Dialoge im Look des Fensters:** Bei eigener Fensterleiste haben jetzt auch Einstellungen, Equalizer, Albuminfos, Rückfragen und alle anderen Dialoge keinen Systemrahmen mehr, sondern eine eigene Titelleiste, runde Ecken und denselben durchscheinenden, weichgezeichneten Hintergrund wie das Hauptfenster (etwas deckender, damit Text gut lesbar bleibt). Verschieben an der Titelleiste, Größe ändern an den Rändern. Abschaltbar unter Einstellungen ▸ Darstellung.
- **Weiterschauen:** Lange Videos und Hörbücher (ab 20 Minuten) merken sich, wo du aufgehört hast, und setzen beim nächsten Mal dort fort. Wer bis kurz vor Schluss geschaut hat, beginnt wieder von vorn. Abschaltbar unter Einstellungen ▸ Video.
- **Flatpak** für alle Linux-Systeme (Fedora, Ubuntu, Mint, openSUSE, Steam Deck …): `NeoNote-1.2-x86_64.flatpak` hängt an der Release, Installation per Doppelklick in Discover/GNOME Software oder mit `flatpak install`. Bringt libmpv und alles Nötige mit; Updates zeigt NeoNote an, installiert werden sie über Discover bzw. `flatpak update`.

**Fehlerbehebungen**
- Beim Bearbeiten direkt in der Titelliste (F2) war der markierte Text weiß auf hellem Grund und kaum lesbar; außerdem schnitt das Eingabefeld die Schrift oben und unten ab.
- Nach einem Film blieb beim Hören von Musik der Knopf „Spuren“ stehen.
- Bibliothek, Statistik (Bewertungen, Wiedergabezähler, „Zuletzt gespielt“), Bearbeitungen und Wiedergabelisten werden jetzt sicher gespeichert: erst in eine Hilfsdatei, dann getauscht, die vorige Fassung bleibt als `.bak`. Stürzt NeoNote mitten im Speichern ab, geht nichts mehr verloren – beim nächsten Start wird die Sicherung gelesen.
