# Windows-Installer bauen (unter Linux mit Wine)

Notizen für den Bau von `NeoNote-Setup-<Version>.exe` ohne Windows-Rechner.

## Umgebung

- Wine 9 (`apt install wine64`), Präfix `/opt/wineprefix`
- Windows-Python 3.12 (64 Bit) von conda-forge, entpackt nach `/opt/winpy`
- darin per pip: `pyside6-essentials pyside6-addons mutagen python-mpv pyinstaller py7zr`
  sowie `winrt-runtime winrt-Windows.Foundation winrt-Windows.Foundation.Collections winrt-Windows.Media
  winrt-Windows.Media.Playback winrt-Windows.Storage winrt-Windows.Storage.Streams`
- NSIS (`apt install nsis`, Linux-`makensis`)

## Stolperfallen

- Wine immer mit minimaler Umgebung starten, sonst Absturz („free(): invalid pointer“):
  `env -i HOME=/root PATH=/usr/bin:/bin WINEPREFIX=/opt/wineprefix WINEDEBUG=-all wine …`
- PyInstaller braucht `WINEPATH='Z:\opt\winpy\Library\bin;Z:\opt\winpy'`, sonst fehlt `ffi-8.dll` (`_ctypes`).
- Ausgabe von Wine-Python per Pipe weiterleiten (`| cat`), nicht in eine Datei umleiten.
- Für Fenstertests unter xvfb fehlt Wine `WcsCreateIccProfile`: Stub-`mscms.dll` mit
  `WINEDLLOVERRIDES="mscms=n"`. Vor dem Bau wieder aus `/opt/winpy` entfernen.

## libmpv (seit 1.1.8 im Installer)

Neueste `mpv-dev-x86_64-<datum>-git-<hash>.7z` von
https://github.com/shinchiro/mpv-winbuild-cmake/releases laden, `libmpv-2.dll` entpacken und neben
`neonote.spec` legen. Die spec nimmt sie automatisch auf, wenn sie vorhanden ist.

## Bauen

```
python make_version.py ../neonote.py        # version_info.txt
python make_icons.py icons
python -m PyInstaller --noconfirm --clean neonote.spec
makensis -DVERSION=<Version> neonote.nsi
```

## Veröffentlichen

Releases entstehen über den Workflow im verwaisten Zweig `release`: `version.txt`, `commit.txt`
(Commit auf main), `notes.md` (oben Englisch, `---`, dann Deutsch) und `files/*` (Installer,
`neonote-<Version>-linux-arch.zip` aus `git archive` ohne docs/.github/aur) dorthin pushen.
