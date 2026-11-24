#!/bin/sh
# Baut NeoNote-Setup-<Version>.exe. Unter Windows in Git-Bash/MSYS ausführen (oder unter Linux mit Wine):
#   Voraussetzungen: Python 3.12 (64 Bit), NSIS 3 (makensis im PATH)
#   pip install pyside6-essentials pyside6-addons mutagen python-mpv pyinstaller py7zr certifi \
#       winrt-runtime winrt-Windows.Foundation winrt-Windows.Foundation.Collections winrt-Windows.Media \
#       winrt-Windows.Media.Playback winrt-Windows.Storage winrt-Windows.Storage.Streams
# Die Versionsnummer kommt aus APP_VERSION in neonote.py.
set -e
cd "$(dirname "$0")"
VERSION=$(sed -n 's/^APP_VERSION = "\(.*\)"/\1/p' ../neonote.py)
python make_version.py ../neonote.py
python make_icons.py icons
python -m PyInstaller --noconfirm --clean neonote.spec
makensis -DVERSION="$VERSION" neonote.nsi
echo "Fertig: windows/NeoNote-Setup-$VERSION.exe"
