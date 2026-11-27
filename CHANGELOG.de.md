# Änderungen

🇬🇧 [English](CHANGELOG.md) | 🇩🇪 **Deutsch**

## Nächste Version (in Arbeit)

### ✨ Neue Funktionen
- **Casting – DLNA, Chromecast und AirPlay:** Der neue Cast-Knopf neben der Lautstärke spielt Musik und Videos auf Geräten im Heimnetz ab – AV-Receiver (z. B. Yamaha MusicCast), Smart-TVs, Chromecast/Google TV, Netzwerk- und AirPlay-Lautsprecher. NeoNote findet sie selbst und wird zur Fernbedienung: Play/Pause, Weiter, Springen und Lautstärke steuern das Gerät, der nächste Titel folgt automatisch, Titel, Interpret und Cover erscheinen am Gerät. „Auf diesem PC weiterhören“ schaltet an derselben Stelle zurück. AirPlay: nur Musik, für Geräte, die unverschlüsselte Übertragung annehmen (Geräte mit Pflicht-Kopplung werden als nicht unterstützt angezeigt). Firewall: Unter Windows gibt der Installer NeoNote automatisch fürs Heimnetz frei; unter Linux erkennt NeoNote eine aktive Firewall (ufw, firewalld) und gibt sie mit einem Klick und deinem Passwort frei – beim ersten Mal bietet es das von selbst an (auch unter Einstellungen ▸ System). Ein Wunsch von Holgi aus dem Deskmodder-Forum.

### ⚡ Verbesserungen
- Kurzinfos lassen sich jetzt getrennt schalten: über Knöpfen und Symbolen (standardmäßig an) und über Titeln und Alben in Listen (standardmäßig aus) – Einstellungen ▸ Darstellung.

### 🐞 Behobene Fehler
- „Immer im Vordergrund“ wird beim Start erst nach ein paar Sekunden wiederhergestellt, wenn NeoNote flüssig läuft – fror es beim Start ein, lag sonst ein hängendes Fenster über allem. Im sicheren Modus bleibt es aus. Außerdem öffneten sich bei „Immer im Vordergrund“ Dialoge (Einstellungen, „Was ist neu?“ …) hinter dem Hauptfenster und sperrten es – NeoNote wirkte eingefroren. Dialoge erscheinen jetzt obenauf, und für die Windows-Einstellungen tritt NeoNote zurück, bis du wieder hineinklickst. Gemeldet von Holgi im Deskmodder-Forum.
- Windows: „Standard-Apps ▸ NeoNote“ zeigt keine leere Seite mehr, wenn die Verknüpfungen aus sind – Reste früherer Installationen werden entfernt.

## 1.3.2 – 26.11.2026

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

## 1.3.1 – 24.11.2026

### ⚡ Verbesserungen
- **Immer im Vordergrund:** Stecknadel-Knopf neben „Minimieren“ (und im ☰-Menü, Strg+Umschalt+T). Ein Wunsch von Holgi aus dem Deskmodder-Forum.
- Kurzinfos (Tooltips) und Rechtsklick-Menüs passen jetzt zum Fenster: durchscheinend, mit runden Ecken und Weichzeichner. Abschaltbar unter Einstellungen ▸ Darstellung.

### 🐞 Behobene Fehler
- Update-Prüfung: Ist die GitHub-API nicht erreichbar (z. B. Abfragelimit), nutzt NeoNote die Release-Seite; die Meldung nennt jetzt den Grund.
- Update-Prüfung und alle Online-Funktionen scheiterten auf frischen Windows-Installationen (z. B. Windows-Sandbox) mit „Keine Verbindung zu GitHub“: Windows lädt fehlende Stammzertifikate erst nach, wenn ein Browser sie braucht. NeoNote bringt jetzt eine eigene Zertifikatsliste als Rückfall mit.
- Windows: „Immer im Vordergrund“ hielt das Fenster nicht oben – noch am Veröffentlichungstag im Download von 1.3.1 behoben.
- Einstellungen: Das Fenster ist hoch genug für den größten Reiter (vorher wurden Zeilen zusammengequetscht).

## 1.3 – 23.11.2026

### ✨ Neue Funktionen
- **Überblenden** zwischen Titeln (Einstellungen ▸ System ▸ Übergänge, 1–12 Sekunden): Der nächste Titel wird eingeblendet, während der laufende ausklingt. Innerhalb eines Albums bleibt es auf Wunsch lückenlos – Live- und Konzeptalben werden nicht zerhackt.
- **Wiedergabegeschwindigkeit** 0,5× bis 2× mit Tonhöhenkorrektur (☰-Menü) – praktisch für Hörbücher und Podcasts; eine Anzeige in der Steuerleiste zeigt, wenn es nicht 1× ist.
- **Ausgabegerät wählen und bitgenaue Wiedergabe** für externe DACs (Einstellungen ▸ System ▸ Audioausgabe): exklusiver Zugriff (unter Windows WASAPI exklusiv), die Musik geht unverändert in Abtastrate und Bittiefe der Datei ans Gerät – ohne Lautstärke, Equalizer, ReplayGain oder Umrechnung. Wer trotzdem lieber mit dem Regler in NeoNote arbeitet, kann das zuschalten (exklusiv, aber nicht mehr streng bitgenau).
- **Ordneransicht:** durch die Musikordner stöbern wie im Dateimanager – Ordner als Kacheln mit Coverstapeln, die Titel eines Ordners als Liste (neuer Eintrag „Ordner“ in der Navigation).
- **Dateien umbenennen und einsortieren** nach Muster, z. B. `{albumartist}/{album}/{track} {title}` – mit Vorschau, bevor etwas verschoben wird. `.lrc`-Dateien wandern mit, Sterne, Wiedergabezähler und Wiedergabelisten werden nachgezogen, leere Ordner entfernt. Organisieren ▸ „Letztes Einsortieren rückgängig machen“ holt alles zurück.
- **Scrobbeln** zu ListenBrainz (Benutzer-Token) und Last.fm (eigener, kostenloser API-Schlüssel, das Passwort wird nicht gespeichert): Ein Titel zählt, wenn er wirklich zur Hälfte (oder 4 Minuten) gehört wurde; ohne Verbindung wird nachgereicht.
- **Infos zum Interpreten** in „Wird gespielt“ und rechts in der Bibliothek (Knopf neben dem Songtext, `Strg+I`): Biografie aus der Wikipedia, Lebensdaten, Herkunft und Genres von MusicBrainz, ähnliche Interpreten von ListenBrainz – die aus deiner Sammlung sind anklickbar.
- **Visualisierung** in „Wird gespielt“ (Rechtsklick ▸ Visualisierung, `Strg+Umschalt+V`): Spektrum-Balken mit fallenden Spitzen oder fließende Wellen in der Akzentfarbe – aus echten Frequenzbändern der Musik.
- **Auto-DJ:** Rechtsklick auf einen Titel ▸ „Auto-DJ ab diesem Titel“ oder ☰ ▸ Auto-DJ – passende Musik ohne Ende aus der eigenen Sammlung (gleiches Genre, ähnliche Interpreten, ähnliche Zeit, deine Bewertungen), nie zweimal derselbe Interpret hintereinander.
- **Sternbewertungen stehen jetzt in den Musikdateien**, so wie es Windows Media Player macht: bei MP3 und WMA im Format von WMP (WMP12 zeigt sie also auch an), bei FLAC, Ogg und Opus als `FMPS_RATING` (lesen Strawberry, Clementine, Amarok). Damit überstehen die Sterne Abstürze, Neuinstallationen und den Wechsel zwischen Windows und Linux. Schon vergebene Sterne trägt NeoNote einmalig nach. Das Änderungsdatum der Datei bleibt gleich, Sicherungs- und Sync-Programme halten die Dateien also nicht für neu. Der gerade laufende Titel wird erst nach dem Ende beschrieben. Abschaltbar unter Einstellungen ▸ Online-Informationen.

### ⚡ Verbesserungen
- Installer: Statt des grauen Kastens „Setup wird vorbereitet …“ erscheint beim Entpacken ein Startfenster im NeoNote-Look – mit Neon-Note, Version und laufendem Fortschrittsbalken; es blendet sich aus, sobald das Setup-Fenster da ist.
- Die Einstellungen haben jetzt **OK**, **Übernehmen** und **Abbrechen**: „Übernehmen“ speichert, ohne das Fenster zu schließen. Das Fenster ist breit genug für alle Reiter.
- Dialoge haben genau dieselbe Deckkraft wie das Hauptfenster, und der Deckkraft-Regler reagiert sofort (nur neu zeichnen statt die ganze Darstellung neu aufzubauen).

### 🐞 Behobene Fehler
- Filme mit 5.1/7.1-Ton (z. B. DTS) hatten an Stereo-Lautsprechern und Kopfhörern keine Stimmen, weil der Mittenkanal verloren ging. NeoNote mischt Filmton jetzt selbst auf Stereo; mit Surround-Anlage lässt sich unveränderte Mehrkanal-Ausgabe einschalten (Einstellungen ▸ Video).
- Flatpak: mpv startete nicht (fehlende Lua-Optionen), dadurch lief alles über den schwächeren Ersatzweg Qt Multimedia – keine Bild-Untertitel, kein DTS-Ton, Hänger. Behoben; der Ersatzweg stürzt unter Linux außerdem nicht mehr ab.
- Songtexte: Steht in der Datei nur ein einfacher Text ohne Zeitstempel (häufig bei gerippten MP3s), sucht NeoNote jetzt zusätzlich bei LRCLIB nach einem zeitgesteuerten Text und nimmt diesen – so läuft der Text mit. Einfache Texte wandern außerdem langsam mit dem Lied mit.
- Bei ausgeblendeter Wiedergabeliste springt der Songtext-Knopf nicht mehr nach „Wird gespielt“, sondern blendet die Wiedergabeliste mit dem Songtext darunter ein.
- In NeoNote gelöschte Sterne bleiben gelöscht – „Komplett neu einlesen“ holt keine alte Bewertung aus der Datei mehr zurück.
- Linux: Dialoge waren deckend mit schwarzen Ecken statt durchscheinend mit runden Ecken. Behoben.
- Linux/KDE: Das NeoNote-Fenster fehlte in der Fensterleiste (angeheftete Starter wurden nicht als geöffnet markiert); das App-Symbol hat jetzt einen Rand, damit der Strich für „geöffnet“ darunter sichtbar ist.
- Flatpak: Musikordner auf anderen Laufwerken (z. B. `/media/…` oder interne NTFS-Platten) lassen sich jetzt hinzufügen; ist ein Ordner nicht lesbar, sagt NeoNote das verständlich. Dialogknöpfe zeigen keine KDE-Symbole mehr.

## 1.2 – 20.11.2026

### ✨ Neue Funktionen
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

### 🐞 Behobene Fehler
- Beim Bearbeiten direkt in der Titelliste (F2) war der markierte Text weiß auf hellem Grund und kaum lesbar; außerdem schnitt das Eingabefeld die Schrift oben und unten ab.
- Nach einem Film blieb beim Hören von Musik der Knopf „Spuren“ stehen.
- Bibliothek, Statistik (Bewertungen, Wiedergabezähler, „Zuletzt gespielt“), Bearbeitungen und Wiedergabelisten werden jetzt sicher gespeichert: erst in eine Hilfsdatei, dann getauscht, die vorige Fassung bleibt als `.bak`. Stürzt NeoNote mitten im Speichern ab, geht nichts mehr verloren – beim nächsten Start wird die Sicherung gelesen.

## 1.1.9 – 20.11.2026

### ✨ Neue Funktionen
- **Interpreten zusammenführen** wie im WMP12: In der Interpretenansicht eine Kachel (oder mehrere markierte) auf einen anderen Interpreten ziehen. Nach einer Rückfrage wandern alle Titel dorthin – Interpret bzw. Albuminterpret wird auf den Zielnamen gesetzt (in die Dateien geschrieben oder nur in der Bibliothek, je nach Einstellung).
- **Angaben neben dem Cover anklickbar:** In der Titelliste öffnet ein Klick auf Albumtitel, Interpret, Genre oder Jahr die passende Ansicht. Neu ist dabei die Jahresansicht mit allen Alben aus diesem Jahr, wie im WMP12.

### ⚡ Verbesserungen
- Wie im WMP12 lässt sich das Fenster jetzt auch an der Steuerleiste unten verschieben – an allen freien Stellen und über Titel und Interpret. Doppelklick dort maximiert, wie oben.
- Zurück und Vor merken sich ihren Verlauf jetzt auch über einen Neustart hinweg (die letzten 50 Ansichten, mit Scrollposition).
- Installer: Läuft NeoNote noch, bittet der Installer es jetzt, sich selbst zu beenden – so werden Wiedergabeposition und Verlauf noch gespeichert. Erst wenn das nach ein paar Sekunden nicht geklappt hat, wird es wie bisher hart beendet. (Wirkt ab dem Update von 1.1.9 auf spätere Versionen.)
- Absturzprotokoll: Stürzt NeoNote ab, steht in `crash.log` im Datenordner, wo es passiert ist und welches Video bzw. welche Spur zuletzt geöffnet war.
- Beim Start schreibt NeoNote die Dauer jedes Startschritts in `startup.log` im Datenordner – hilft, langsame Starts aufzuspüren.
- Im Menü ☰ steht „Befehlsleiste anzeigen“ jetzt bei „Darstellung…“ statt ganz unten.
- Windows 11: Die Titelleisten der Dialoge (Einstellungen, Equalizer, Albuminfos …) haben jetzt dieselbe Farbe wie das Fenster – eine durchgehende Fläche statt eines abgesetzten Balkens. Gilt auch fürs Hauptfenster mit Systemrahmen und passt sich beim Farbwechsel sofort an.

### 🐞 Behobene Fehler
- Absturz beim Einschalten von Bild-Untertiteln (PGS von Blu-rays, VobSub von DVDs, DVB) in MKV-Videos: Qt Multimedia kommt damit nicht zurecht. NeoNote erkennt diese Spuren jetzt selbst und zeigt sie im Menü ausgegraut („noch nicht unterstützt“); Text-Untertitel funktionieren wie gewohnt.
- Große Videos (4K, HDR) stauen keine Bilder mehr auf: Kommen sie schneller, als NeoNote sie zeichnen kann, werden Zwischenbilder ausgelassen. Ganz flüssig wird 4K-HDR erst mit der Wiedergabe über mpv (geplant für 1.2).

## 1.1.8 – 19.11.2026

### ✨ Neue Funktionen
- **Updates:** NeoNote sucht auf Wunsch nach neuen Versionen – bei jedem Start, einmal am Tag (Standard), einmal pro Woche oder nie (Einstellungen ▸ System ▸ Updates, außerdem „Nach Updates suchen“ unter Über NeoNote). Es wird nur die Release-Seite auf GitHub gelesen.
  - Windows: „Jetzt aktualisieren“ lädt den Installer (Prüfsumme wird kontrolliert), installiert ihn still und startet NeoNote neu. Alternativ: automatisch herunterladen und beim Beenden installieren.
  - Linux: Hinweis mit „Was ist neu?“; aktualisiert wird über die Paketverwaltung.
- **Installer:** Desktop-Verknüpfung, „Öffnen mit“ und Standardplayer sind bei der Installation nicht mehr vorausgewählt – du entscheidest selbst. Updates aus NeoNote heraus übernehmen die bisherige Einrichtung.
- **Sampler:** Alben mit vielen verschiedenen Interpreten erscheinen als ein Album unter „Verschiedene Interpreten“ statt verstreut bei jedem einzelnen Interpreten. Erkannt am Sampler-Kennzeichen in den Tags oder daran, dass im selben Ordner mindestens drei Interpreten dasselbe Album ohne Albuminterpreten haben. An den Dateien ändert sich nichts; ein selbst gesetzter Albuminterpret hat immer Vorrang.
- **Menü ☰ neben dem Zahnrad:** Alles aus „Organisieren“ gibt es jetzt auch als Menü rechts neben dem Zahnrad. Ist die Befehlsleiste ausgeblendet, erscheinen Zahnrad und Menü oben in der Titelleiste, und über das Menü lässt sich die Befehlsleiste wieder einblenden.
- **Einstellungen ▸ Über:** „Über NeoNote“ ist jetzt ein eigener Reiter in den Einstellungen – mit Datum der Version, Credits, den genauen Versionen von FFmpeg (für Videos und für Musik in mpv), Qt und mpv sowie „Versionen kopieren“ für Fehlermeldungen.
- **Einstellungen ▸ Video:** Hardwarebeschleunigung wählbar (Automatisch, nur Prozessor oder ein bestimmtes Verfahren wie D3D11VA, VA-API oder CUDA) und GPU-Umwandlung abschaltbar – hilfreich, wenn ein Video ruckelt oder schwarz bleibt. Außerdem: bevorzugte Tonspur, Untertitel automatisch einschalten (nie, bei fremdsprachigem Ton oder immer) mit Wunschsprache, und ob eine gleichnamige .srt-Datei automatisch geladen wird.
- **Zeitanzeige:** Ein Klick wechselt jetzt zwischen drei Anzeigen: verstrichene Zeit / Länge, Restzeit / Länge und nur die Restzeit.
- **Windows: mpv ist dabei.** `libmpv-2.dll` liegt dem Installer bei – Equalizer und lückenlose Wiedergabe laufen sofort, ohne Download. Mit jedem Update kommt auch eine aktuelle libmpv (mit eigenem FFmpeg). Eine früher heruntergeladene Kopie wird entfernt.

### 🔄 Geändert
- „Wird gespielt“ bei Musik wieder wie in 1.1.5: normale Titelleiste oben mit Zurück/Vor und den Fensterknöpfen (ohne Suche und Überschrift), Steuerleiste unten. Der doppelte Bibliotheks-Knopf oben rechts im Bild entfällt – er sitzt unten rechts in der Steuerleiste. Die über dem Bild schwebenden, ausblendenden Leisten gibt es weiterhin bei Videos.

### 🐞 Behobene Fehler
- Das Einstellungsfenster schloss sich mit ✕ oder „Abbrechen“ spürbar verzögert, weil die ganze Darstellung neu aufgebaut wurde – auch ohne Änderungen. Jetzt wird nur zurückgenommen, was du wirklich geändert hast. Ebenso beim Ein- und Ausblenden der Befehlsleiste: Das geht jetzt sofort.
- Bei Titeln über einer Stunde wurde die Zeitanzeige abgeschnitten („12:01 …:03:11“). Das Feld passt sich jetzt an.
- „Zurück“ aus einem Interpreten oder Album führte in der Interpreten- und Albenansicht wieder ganz nach oben. Jetzt landest du an derselben Stelle wie vorher, und der eben geöffnete Eintrag ist markiert (auch mit „Vor“).
- Musikordner mit Ordner-Verknüpfungen (Symlinks), die auf einen übergeordneten Ordner zeigen, wurden mehrfach eingelesen – Titel erschienen doppelt. Jeder Ordner wird jetzt nur einmal gelesen.

## 1.1.7 – 19.11.2026

### 🐞 Behobene Fehler
- Liegt ein Album doppelt vor (z. B. einmal als FLAC, einmal als MP3 in eigenen Ordnern), wurden beide Fassungen zu einem Album zusammengeworfen. Jetzt erscheinen sie wie im WMP12 als getrennte Alben, mit dem Format neben dem Jahr („2000 · FLAC“). Alben, die nur auf mehrere Ordner verteilt sind (CD1/CD2), bleiben zusammen.
- Springen per Buchstabe in der Interpreten- und Albenansicht: Der Abschnitt erscheint jetzt oben statt am unteren Rand.
- Fortschrittsbalken und Lautstärkeregler zeigen beim Darüberfahren eine Hand als Mauszeiger.
- Die Hover- und Auswahlfläche in der Titelliste reichte über den Albumcover-Block hinaus. Sie bleibt jetzt bei den Titelspalten.

## 1.1.6 – 18.11.2026

### ⚡ Verbesserungen
- „Wird gespielt“ bei Musik wie bei Videos: Statt der Titelleiste mit Suche gibt es nur noch eine schmale Leiste mit Titel, Minimieren, Maximieren und Schließen. Oben und unten laufen die Leisten jetzt durchgehend transparent ins Bild aus – ohne Kanten und Trennlinien.
- Ziehen der Fenstergröße deutlich flüssiger: Kacheln werden als fertige Bilder gezeichnet, ihre Größe liest Qt direkt aus dem Modell, der Fensterhintergrund wird schneller gefüllt (bei 800 Interpreten etwa doppelt so schnell).

### 🐞 Behobene Fehler
- Windows: Der Weichzeichner wird beim Ziehen der Fenstergröße nicht mehr bei jeder kurzen Pause neu gesetzt (das ganze Fenster wurde dabei neu gezeichnet).
- Der Größenpfeil vom Fensterrand blieb stehen, wenn man die Maus ohne Klick zurück ins Fenster bewegte.

## 1.1.5 – 17.11.2026

### Neu seit 1.1.0
- **Jellyfin-Anbindung:** Musik vom eigenen Jellyfin-Server mit denselben Ansichten wie die eigene Bibliothek. Wählbare Streaming-Qualität (Original bis 128 kbit/s), Titel und Alben offline speichern, Favoriten und gespielte Titel werden mit dem Server abgeglichen.
- **Bibliothek prüfen:** findet doppelte Titel (beste Fassung vorausgewählt), Alben ohne Cover, lückenhafte Tags und fehlende Dateien; verschobene Dateien werden wiedergefunden.
- **Englische Oberfläche:** Sprache unter Einstellungen ▸ Darstellung, automatisch nach Systemsprache.
- **„Über NeoNote“** mit Version, verwendeten Bausteinen und Datenordnern.
- **Kein Standby während der Wiedergabe** (wie im WMP): Bei Musik bleibt der Rechner wach, bei Videos zusätzlich der Bildschirm. Abschaltbar unter Einstellungen ▸ System.

### ⚡ Verbesserungen
- Flüssiges Scrollen auch bei sehr großen Bibliotheken: Cover laden im Hintergrund und werden beim Entpacken gleich verkleinert, Cover-Stapel und Album-Blöcke werden nur einmal gezeichnet. Bei 800 Interpreten etwa 4–8 ms statt 17–80 ms pro Bild.
- Schnellerer Start: die Titelliste wird nur noch einmal statt dreimal aufgebaut, die zuletzt geöffnete Ansicht erscheint direkt, die Suche nach geänderten Dateien beginnt erst, wenn das Fenster steht.
- Unter Windows deutlich schnelleres Prüfen der Musikordner auf Änderungen.

### 🐞 Behobene Fehler
- Windows: Minimieren und Wiederherstellen werden jetzt wie bei anderen Programmen animiert (vorher verschwand das Fenster einfach).
- Windows: Ein an die Taskleiste angeheftetes NeoNote (auch mit eigenem Symbol) erzeugte beim Start einen zweiten Taskleisten-Knopf. Fenster und angeheftetes Symbol gehören jetzt zusammen.
- Windows: „Als Standardplayer festlegen“ öffnete den Explorer statt der Windows-Einstellungen.
- Ein erneuter Start von NeoNote holt das laufende Fenster jetzt auch aus der Systemleiste oder dem Mini-Player zurück.
- Windows: `NeoNote.exe` trägt jetzt Programmname und Version (Task-Manager, Mediensteuerung, Dateieigenschaften).
- Gespeicherte Platzhalter wie „Unbekannter Interpret“ oder „Internetradio“ erscheinen in der gewählten Sprache.

## 1.0.8
- Sicherheit: Der Installer entpackt nicht mehr in den Temp-Ordner, die Verbindung zwischen zwei NeoNote-Fenstern nimmt nur Anfragen des eigenen Benutzers an, Titel aus Dateien werden nur als reiner Text angezeigt.

## 1.0
- Erste vollständige Version für Linux und Windows.
