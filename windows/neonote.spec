# -*- mode: python -*-
block_cipher = None
import os
_bins = [('vulkan-1.dll', '.')] + ([('libmpv-2.dll', '.')] if os.path.exists('libmpv-2.dll') else [])
a = Analysis(['../neonote.py'], pathex=[], binaries=_bins, datas=[('neonote.ico', '.'), ('icons', 'icons'), ('../i18n', 'i18n'), ('../LICENSE', '.'), ('../THIRD_PARTY_NOTICES.md', '.')],
    hiddenimports=['mpv', 'py7zr', 'winrt.windows.media', 'winrt.windows.media.playback', 'winrt.windows.foundation',
                   'winrt.windows.foundation.collections', 'winrt.windows.storage', 'winrt.windows.storage.streams',
                   'mutagen.id3', 'mutagen.asf', 'mutagen.mp4', 'mutagen.flac', 'mutagen.oggvorbis'],
    excludes=['jeepney', 'tkinter', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtQuick3D',
              'PySide6.Qt3DCore', 'PySide6.Qt3DRender', 'PySide6.QtCharts', 'PySide6.QtDataVisualization',
              'PySide6.QtGraphs', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets', 'PySide6.QtDesigner', 'PySide6.QtBluetooth',
              'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtLocation', 'PySide6.QtPositioning', 'PySide6.QtSensors',
              'PySide6.QtSerialPort', 'PySide6.QtHelp', 'PySide6.QtQuick', 'PySide6.QtQml', 'PySide6.QtQuickWidgets',
              'PySide6.QtRemoteObjects', 'PySide6.QtScxml', 'PySide6.QtTextToSpeech', 'PySide6.QtWebSockets',
              'PySide6.QtNfc', 'PySide6.QtSpatialAudio', 'PySide6.QtHttpServer', 'PySide6.QtCanvasPainter'],
    noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='NeoNote', debug=False, strip=False, upx=False,
          console=False, icon='neonote.ico', version='version_info.txt')
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='NeoNote')
