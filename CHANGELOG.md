# Änderungen

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
