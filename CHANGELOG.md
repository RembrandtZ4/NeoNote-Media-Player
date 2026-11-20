# Änderungen

## Nächste Version (in Arbeit)

**Neu**
- **Videos über mpv:** Videos laufen jetzt über mpv, das direkt auf der Grafikkarte zeichnet – flüssiges 4K, HDR-Videos mit richtigen Farben auf normalen Bildschirmen, Hardware-Decodierung über D3D11VA, VA-API oder NVDEC. Bild-Untertitel von Blu-rays und DVDs (PGS, VobSub) funktionieren jetzt, ebenso .ass- und .vtt-Untertitel. Untertitel weichen nach oben aus, solange die Steuerleiste eingeblendet ist. Abschaltbar unter Einstellungen ▸ Video; ohne mpv laufen Videos wie bisher über Qt Multimedia.
- War zuletzt ein Video geöffnet, zeigt NeoNote beim Start nicht mehr dessen Standbild; das Video steht nur in der Warteschlange und setzt beim Abspielen an der letzten Stelle fort. Wer das Standbild wieder möchte: Einstellungen ▸ Video.
- **Absturzschutz für Videos:** Stürzt NeoNote beim Start eines Videos ab, decodiert es beim nächsten Mal ohne Hardwarebeschleunigung; passiert es dann wieder, laufen Videos über Qt Multimedia. Ein Hinweis sagt, was umgestellt wurde. Unter Windows nutzt mpv die stabilen Kopier-Modi (z. B. `d3d11va-copy`) – decodiert wird weiter auf der Grafikkarte.
- **Intelligente Wiedergabelisten** wie im WMP12: Regeln für Interpret, Albuminterpret, Album, Titel, Genre, Jahr, Bewertung, Wiedergaben, zuletzt gespielt, hinzugefügt, Länge, Dateityp und Ordner – z. B. „Genre enthält Rock“ und „Jahr zwischen 1980 und 1989“ oder „noch nie gespielt“. Alle oder mindestens eine Regel, begrenzbar auf eine Anzahl Titel oder Minuten, sortiert nach Wunsch (auch zufällig, täglich neu gemischt). Der Editor zeigt sofort, wie viele Titel passen. Die Listen aktualisieren sich von selbst und stehen mit Blitz-Symbol bei den Wiedergabelisten (Organisieren ▸ „Neue intelligente Wiedergabeliste…“ oder Rechtsklick auf „Wiedergabelisten“).
- **Einschlaf-Timer** (☰-Menü und Systemleiste): nach 15, 30, 45, 60, 90 Minuten oder einer eigenen Zeit, nach diesem Titel oder nach diesem Album. Am Ende wird die Lautstärke in 10 Sekunden ausgeblendet und die Wiedergabe angehalten – „Abspielen“ macht später an derselben Stelle weiter. Solange er läuft, zeigt ein Mond in der Steuerleiste die Restzeit; ein Klick darauf ändert oder beendet ihn.
- **Kapitel:** Filme mit Kapiteln zeigen im Spuren-Menü eine Kapitelliste; `Strg+Bild↓` / `Strg+Bild↑` springt zum nächsten bzw. vorherigen Kapitel.
- **Songtexte** in „Wird gespielt“: Das Cover rückt nach links, rechts steht der Text. Zeitgesteuerte Texte laufen mit, die aktuelle Zeile ist hervorgehoben; ein Klick auf eine Zeile springt dorthin, mit dem Mausrad lässt sich vor- und zurückblättern. Quellen in dieser Reihenfolge: eine `.lrc`-Datei mit gleichem Namen neben dem Titel, ein in der Datei gespeicherter Text (MP3, FLAC, OGG, M4A, WMA …), sonst online von **LRCLIB** (abschaltbar unter Einstellungen ▸ Online-Informationen). Ein- und ausblenden über den neuen Knopf in der Steuerleiste oder `Strg+T`. Per Rechtsklick lässt sich ein gefundener Online-Text als `.lrc` neben dem Titel speichern.
- **Weiterschauen:** Lange Videos und Hörbücher (ab 20 Minuten) merken sich, wo du aufgehört hast, und setzen beim nächsten Mal dort fort. Wer bis kurz vor Schluss geschaut hat, beginnt wieder von vorn. Abschaltbar unter Einstellungen ▸ Video.

**Fehlerbehebungen**
- Beim Bearbeiten direkt in der Titelliste (F2) war der markierte Text weiß auf hellem Grund und kaum lesbar; außerdem schnitt das Eingabefeld die Schrift oben und unten ab.
- Nach einem Film blieb beim Hören von Musik der Knopf „Spuren“ stehen.
- Bibliothek, Statistik (Bewertungen, Wiedergabezähler, „Zuletzt gespielt“), Bearbeitungen und Wiedergabelisten werden jetzt sicher gespeichert: erst in eine Hilfsdatei, dann getauscht, die vorige Fassung bleibt als `.bak`. Stürzt NeoNote mitten im Speichern ab, geht nichts mehr verloren – beim nächsten Start wird die Sicherung gelesen.

## 1.1.9 – 20.11.2026

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

## 1.1.8 – 19.11.2026

**Neu**
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

**Geändert**
- „Wird gespielt“ bei Musik wieder wie in 1.1.5: normale Titelleiste oben mit Zurück/Vor und den Fensterknöpfen (ohne Suche und Überschrift), Steuerleiste unten. Der doppelte Bibliotheks-Knopf oben rechts im Bild entfällt – er sitzt unten rechts in der Steuerleiste. Die über dem Bild schwebenden, ausblendenden Leisten gibt es weiterhin bei Videos.

**Fehlerbehebungen**
- Das Einstellungsfenster schloss sich mit ✕ oder „Abbrechen“ spürbar verzögert, weil die ganze Darstellung neu aufgebaut wurde – auch ohne Änderungen. Jetzt wird nur zurückgenommen, was du wirklich geändert hast. Ebenso beim Ein- und Ausblenden der Befehlsleiste: Das geht jetzt sofort.
- Bei Titeln über einer Stunde wurde die Zeitanzeige abgeschnitten („12:01 …:03:11“). Das Feld passt sich jetzt an.
- „Zurück“ aus einem Interpreten oder Album führte in der Interpreten- und Albenansicht wieder ganz nach oben. Jetzt landest du an derselben Stelle wie vorher, und der eben geöffnete Eintrag ist markiert (auch mit „Vor“).
- Musikordner mit Ordner-Verknüpfungen (Symlinks), die auf einen übergeordneten Ordner zeigen, wurden mehrfach eingelesen – Titel erschienen doppelt. Jeder Ordner wird jetzt nur einmal gelesen.

## 1.1.7 – 19.11.2026

**Fehlerbehebungen**
- Liegt ein Album doppelt vor (z. B. einmal als FLAC, einmal als MP3 in eigenen Ordnern), wurden beide Fassungen zu einem Album zusammengeworfen. Jetzt erscheinen sie wie im WMP12 als getrennte Alben, mit dem Format neben dem Jahr („2000 · FLAC“). Alben, die nur auf mehrere Ordner verteilt sind (CD1/CD2), bleiben zusammen.
- Springen per Buchstabe in der Interpreten- und Albenansicht: Der Abschnitt erscheint jetzt oben statt am unteren Rand.
- Fortschrittsbalken und Lautstärkeregler zeigen beim Darüberfahren eine Hand als Mauszeiger.
- Die Hover- und Auswahlfläche in der Titelliste reichte über den Albumcover-Block hinaus. Sie bleibt jetzt bei den Titelspalten.

## 1.1.6 – 18.11.2026

**Verbessert**
- „Wird gespielt“ bei Musik wie bei Videos: Statt der Titelleiste mit Suche gibt es nur noch eine schmale Leiste mit Titel, Minimieren, Maximieren und Schließen. Oben und unten laufen die Leisten jetzt durchgehend transparent ins Bild aus – ohne Kanten und Trennlinien.
- Ziehen der Fenstergröße deutlich flüssiger: Kacheln werden als fertige Bilder gezeichnet, ihre Größe liest Qt direkt aus dem Modell, der Fensterhintergrund wird schneller gefüllt (bei 800 Interpreten etwa doppelt so schnell).

**Fehlerbehebungen**
- Windows: Der Weichzeichner wird beim Ziehen der Fenstergröße nicht mehr bei jeder kurzen Pause neu gesetzt (das ganze Fenster wurde dabei neu gezeichnet).
- Der Größenpfeil vom Fensterrand blieb stehen, wenn man die Maus ohne Klick zurück ins Fenster bewegte.

## 1.1.5 – 17.11.2026

**Neu seit 1.1.0**
- **Jellyfin-Anbindung:** Musik vom eigenen Jellyfin-Server mit denselben Ansichten wie die eigene Bibliothek. Wählbare Streaming-Qualität (Original bis 128 kbit/s), Titel und Alben offline speichern, Favoriten und gespielte Titel werden mit dem Server abgeglichen.
- **Bibliothek prüfen:** findet doppelte Titel (beste Fassung vorausgewählt), Alben ohne Cover, lückenhafte Tags und fehlende Dateien; verschobene Dateien werden wiedergefunden.
- **Englische Oberfläche:** Sprache unter Einstellungen ▸ Darstellung, automatisch nach Systemsprache.
- **„Über NeoNote“** mit Version, verwendeten Bausteinen und Datenordnern.
- **Kein Standby während der Wiedergabe** (wie im WMP): Bei Musik bleibt der Rechner wach, bei Videos zusätzlich der Bildschirm. Abschaltbar unter Einstellungen ▸ System.

**Schneller**
- Flüssiges Scrollen auch bei sehr großen Bibliotheken: Cover laden im Hintergrund und werden beim Entpacken gleich verkleinert, Cover-Stapel und Album-Blöcke werden nur einmal gezeichnet. Bei 800 Interpreten etwa 4–8 ms statt 17–80 ms pro Bild.
- Schnellerer Start: die Titelliste wird nur noch einmal statt dreimal aufgebaut, die zuletzt geöffnete Ansicht erscheint direkt, die Suche nach geänderten Dateien beginnt erst, wenn das Fenster steht.
- Unter Windows deutlich schnelleres Prüfen der Musikordner auf Änderungen.

**Fehlerbehebungen**
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
