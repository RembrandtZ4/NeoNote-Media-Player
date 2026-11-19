# Änderungen

## Nächste Version (in Arbeit)

**Neu**
- **Updates:** NeoNote sucht auf Wunsch nach neuen Versionen – bei jedem Start, einmal am Tag (Standard), einmal pro Woche oder nie (Einstellungen ▸ System ▸ Updates, außerdem „Nach Updates suchen“ unter Über NeoNote). Es wird nur die Release-Seite auf GitHub gelesen.
  - Windows: „Jetzt aktualisieren“ lädt den Installer (Prüfsumme wird kontrolliert), installiert ihn still und startet NeoNote neu. Alternativ: automatisch herunterladen und beim Beenden installieren.
  - Linux: Hinweis mit „Was ist neu?“; aktualisiert wird über die Paketverwaltung.
- **Installer:** Desktop-Verknüpfung, „Öffnen mit“ und Standardplayer sind bei der Installation nicht mehr vorausgewählt – du entscheidest selbst. Updates aus NeoNote heraus übernehmen die bisherige Einrichtung.
- **Sampler:** Alben mit vielen verschiedenen Interpreten erscheinen als ein Album unter „Verschiedene Interpreten“ statt verstreut bei jedem einzelnen Interpreten. Erkannt am Sampler-Kennzeichen in den Tags oder daran, dass im selben Ordner mindestens drei Interpreten dasselbe Album ohne Albuminterpreten haben. An den Dateien ändert sich nichts; ein selbst gesetzter Albuminterpret hat immer Vorrang.

**Fehlerbehebungen**
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
