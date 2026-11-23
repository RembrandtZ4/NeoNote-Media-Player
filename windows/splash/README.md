# Startfenster des Installers

`neonote-splash.exe` zeigt beim Entpacken ein Fenster im NeoNote-Look (statt des grauen NSIS-Banners) und schließt sich,
sobald das Setup-Fenster von NeoNote erscheint.

```bash
cd windows/splash
cp ../neonote.ico .
python3 make_splash.py <version> logo.png      # Bilder (de/en, 100–200 %) + splash.rc
x86_64-w64-mingw32-windres splash.rc -O coff -o splash_res.o
x86_64-w64-mingw32-gcc -O2 -municode -mwindows -o neonote-splash.exe splash.c splash_res.o -lm -s
```

`neonote.nsi` erwartet die fertige Datei unter `splash\neonote-splash.exe` neben dem Skript.
