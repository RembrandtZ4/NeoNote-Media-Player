#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-only
# NeoNote Media Player – Copyright (C) 2026 RembrandtZ4
"""
NeoNote Media Player – Musik- und Videoplayer für Linux, angelehnt an Windows Media Player 12.
Flaches Design mit Transparenz, anpassbaren Farben und WMP12-Titelliste mit Albumcovern.

Abhängigkeiten:  PySide6, mutagen
Start:           python3 neonote.py
"""
import base64
import bisect
import glob as globmod
import re
import ctypes
import ctypes.util
import hashlib
import html
import json
import math
import os
import random
import subprocess
import sys
import queue
from datetime import timedelta
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from collections import OrderedDict, defaultdict, deque
from pathlib import Path

import mutagen
from PySide6.QtCore import (QPropertyAnimation, QEasingCurve, QProcess, QAbstractItemModel, QBuffer, QEvent, QFileSystemWatcher, QLocale, QObject, QItemSelection,
                            QItemSelectionModel, QModelIndex, QPoint, QPointF, QRect,
                            QRectF, QSettings, QSize, Qt, QThread, QTimer,
                            QUrl, Signal, qVersion)
from PySide6.QtGui import (QRegion, QActionGroup, QColor, QFont, QFontMetrics, QGuiApplication, QLinearGradient, QRadialGradient, QTransform,
                           QIcon, QImage, QImageReader, QKeySequence, QPainter,
                           QPainterPath, QPalette, QPen, QPixmap, QPolygonF,
                           QShortcut, QStandardItem, QStandardItemModel, QDesktopServices)
from PySide6.QtMultimedia import QAudioOutput, QMediaMetaData, QMediaPlayer, QVideoSink
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (QScrollArea, QTextBrowser, QAbstractButton, QAbstractItemView, QGraphicsOpacityEffect,
                               QApplication, QButtonGroup, QCheckBox,
                               QColorDialog, QComboBox, QDialog,
                               QDialogButtonBox, QFileDialog, QFormLayout,
                               QFrame, QGridLayout, QHBoxLayout, QHeaderView, QInputDialog, QLabel,
                               QLineEdit, QListView, QListWidget,
                               QListWidgetItem, QMainWindow, QMenu,
                               QMessageBox, QProgressBar, QPushButton,
                               QSlider, QSplitter, QSplitterHandle, QStackedWidget, QStyle, QSystemTrayIcon,
                               QStyledItemDelegate, QStyleOptionSlider,
                               QStyleOptionViewItem, QTabWidget, QToolButton,
                               QTreeView, QRadioButton,
                               QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                               QWidget)

IS_WIN = sys.platform == "win32"
APP_NAME = "NeoNote"
APP_TITLE = "NeoNote Media Player"
OLD_NAME = "DarkPlayer"
if IS_WIN:
    DATA_DIR = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming")) / APP_NAME
    COVER_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / APP_NAME / "covers"
    MPV_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / APP_NAME / "mpv"
else:
    DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "neonote"
    COVER_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "neonote" / "covers"
    MPV_DIR = None
LIB_FILE = DATA_DIR / "library.json"
STATS_FILE = DATA_DIR / "stats.json"
OVERRIDES_FILE = DATA_DIR / "overrides.json"
HIDDEN_FILE = DATA_DIR / "hidden.json"
JF_CACHE_FILE = DATA_DIR / "jellyfin.json"
JF_OFFLINE_DIR = DATA_DIR / "jellyfin-offline"
PLAYLIST_DIR = DATA_DIR / "playlists"
APP_VERSION = "1.1.7"

# ── Sprache ───────────────────────────────────────────────────────────────
LANGUAGES = [("auto", "Automatisch (Systemsprache)"), ("de", "Deutsch"), ("en", "English")]


def _lang_dirs():
    here = Path(__file__).resolve().parent
    return [Path(getattr(sys, "_MEIPASS", here)) / "i18n", here / "i18n", Path("/usr/share/neonote/i18n")]


def _tr_init():
    """Sprache beim Start festlegen (Wechsel wirkt nach einem Neustart)."""
    try:
        choice = QSettings("NeoNote", "NeoNote").value("ui/lang", "auto") or "auto"
    except Exception:
        choice = "auto"
    if choice == "auto":
        from PySide6.QtCore import QLocale
        choice = "de" if QLocale.system().name().lower().startswith("de") else "en"
    table = {}
    if choice != "de":
        for d in _lang_dirs():
            f = d / f"{choice}.json"
            if f.exists():
                try:
                    table = json.loads(f.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    table = {}
                break
    return choice, table


LANG, _TR = _tr_init()


def tr_(text):
    """Übersetzt einen Oberflächentext (Schlüssel ist der deutsche Text)."""
    t = _TR.get(text)
    if t:
        return t
    return text.split("@", 1)[0] if "@" in text else text    # „Titel@nav“: Kontext nur für die Übersetzung


_PLACEHOLDERS = {"Unbekannter Interpret", "Unbekanntes Album", "Unbekanntes Genre", "Unbekannter Titel", "Videos",
                 "Datei fehlt", "Internetradio"}


def disp(text):
    """Platzhalter aus der Bibliothek („Unbekanntes Album“ …) in der eingestellten Sprache anzeigen."""
    return tr_(text) if text in _PLACEHOLDERS else text


def fmt_int(n):
    """Zahl mit Tausendertrennzeichen in der Schreibweise der Sprache (1.234 bzw. 1,234)."""
    s = f"{int(n):,}"
    return s.replace(",", ".") if LANG == "de" else s

LIB_VERSION = 3
AUDIO_EXT = {".mp3", ".flac", ".ogg", ".oga", ".opus", ".m4a", ".m4b", ".mp4", ".aac", ".wav", ".wma",
             ".ape", ".wv", ".aiff", ".aif", ".dsf", ".dff", ".mpc", ".tta", ".mka", ".ac3", ".dts", ".spx",
             ".mp2", ".amr", ".au"}
VIDEO_EXT = {".mkv", ".mp4", ".m4v", ".avi", ".webm", ".mov", ".wmv", ".flv", ".mpg", ".mpeg", ".ts",
             ".m2ts", ".mts", ".3gp", ".ogv", ".vob", ".divx", ".asf"}
MEDIA_EXT = AUDIO_EXT | VIDEO_EXT
if IS_WIN:
    import getpass
    SERVER_NAME = "neonote-" + re.sub(r"[^A-Za-z0-9_.-]", "_", getpass.getuser() or "user")
    # Keine Windows-Fehlerfenster, wenn eine DLL nicht passt (z. B. veralteter Vulkan-Treiber) –
    # NeoNote fällt dann still auf Qt Multimedia zurück
    try:
        ctypes.windll.kernel32.SetErrorMode(0x0001 | 0x8000)   # SEM_FAILCRITICALERRORS | SEM_NOOPENFILEERRORBOX
    except Exception:
        pass
    # libmpv-2.dll: im Programmordner oder von NeoNote heruntergeladen.
    # Sie braucht vulkan-1.dll; NeoNote bringt einen aktuellen Vulkan-Loader mit, der vor System32 gefunden wird.
    _dll_dirs = [MPV_DIR, Path(getattr(sys, "_MEIPASS", Path(sys.argv[0]).resolve().parent)),
                 Path(sys.executable).resolve().parent]
    os.environ["PATH"] = os.pathsep.join(str(d) for d in _dll_dirs) + os.pathsep + os.environ.get("PATH", "")
    for _d in _dll_dirs:
        try:
            if Path(_d).is_dir():
                os.add_dll_directory(str(_d))
        except (OSError, AttributeError):
            pass
else:
    SERVER_NAME = f"neonote-{os.getuid()}"
FOLDER_COVER_NAMES = ("cover", "folder", "front", "album", "albumart", "albumartsmall")
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

ROLE_KIND = Qt.UserRole + 1
ROLE_COVERS = Qt.UserRole + 2
ROLE_SUB = Qt.UserRole + 3
ROLE_KEY = Qt.UserRole + 4

TILE_W, TILE_H, ART = 262, 128, 92
ROLE_RATING = Qt.UserRole + 5
ROWH = 24


# ════════════════════════════════════════════════════════════════════════════
#  Farbschema
# ════════════════════════════════════════════════════════════════════════════
DEFAULT_THEME = {"accent": "#3d8fe0", "bg": "#14171c", "opacity": 80, "blur": True, "cover": 1, "navsel": 0,
                 "seamless": True, "cmdbar": True}
ACCENTS = [(tr_("Blau"), "#3d8fe0"), (tr_("Türkis"), "#1fb5ad"), (tr_("Grün"), "#43b05c"), (tr_("Gold"), "#d4a72c"),
           (tr_("Orange"), "#f08a24"), (tr_("Rot"), "#e5484d"), (tr_("Pink"), "#e84393"), (tr_("Violett"), "#8e6cf0"),
           (tr_("Silber"), "#b8bec7"), (tr_("Weiß"), "#eef0f3")]
BACKGROUNDS = [(tr_("Graphit"), "#14171c"), (tr_("Anthrazit"), "#1f2023"), (tr_("Mitternacht"), "#0e1322"), (tr_("Schiefer"), "#252a33"),
               (tr_("Schwarz"), "#030303"), (tr_("Aubergine"), "#1d1520"), (tr_("Wald"), "#0f1a15"),
               (tr_("Hell"), "#eef0f3")]
COVER_SIZES = [(tr_("Klein"), 96), (tr_("Mittel"), 140), (tr_("Groß"), 200)]


def mix(a, b, t):
    a, b = QColor(a), QColor(b)
    return QColor(round(a.red() + (b.red() - a.red()) * t), round(a.green() + (b.green() - a.green()) * t),
                  round(a.blue() + (b.blue() - a.blue()) * t))


class Theme:
    def __init__(self, d):
        self.update(d)

    def update(self, d):
        self.d = dict(d)
        self.accent = QColor(d["accent"])
        self.bg = QColor(d["bg"])
        self.alpha = max(0.2, min(1.0, d["opacity"] / 100.0))
        self.dark = self.bg.lightnessF() < 0.5
        self.fg = QColor("#e9ecf1") if self.dark else QColor("#1b1e24")
        self.dim = QColor("#97a0ae") if self.dark else QColor("#5d6471")
        self.ovc = QColor(255, 255, 255) if self.dark else QColor(0, 0, 0)
        self.solid = mix(self.bg, self.ovc, 0.06)          # für Menüs / Dialoge (deckend)
        self.cover = COVER_SIZES[max(0, min(2, int(d["cover"])))][1]
        self.navsel = int(d.get("navsel", 0))
        self.seamless = bool(d.get("seamless", True))      # eine durchgehende Fläche ohne Trennlinien
        # Schrift auf Akzentflächen: dunkel bei hellen Akzentfarben (z. B. Silber, Gold)
        self.on_acc = QColor("#15171a") if self.accent.lightnessF() > 0.66 else QColor("white")

    def ov(self, a):
        c = QColor(self.ovc); c.setAlphaF(a); return c

    def acc(self, a):
        c = QColor(self.accent); c.setAlphaF(a); return c

    def bga(self):
        c = QColor(self.bg); c.setAlphaF(self.alpha); return c


T = Theme(DEFAULT_THEME)


def css(c):
    c = QColor(c)
    return f"rgba({c.red()},{c.green()},{c.blue()},{c.alphaF():.3f})"


# ════════════════════════════════════════════════════════════════════════════
#  Hilfsfunktionen
# ════════════════════════════════════════════════════════════════════════════
def fmt_time(sec):
    sec = int(sec or 0)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_size(b):
    if not b:
        return ""
    return (f"{b / 1048576:.1f} MB" if b < 1024 ** 3 else f"{b / 1024 ** 3:.2f} GB").replace(".", ",")


def to_num(v):
    try:
        return int(str(v).split("/")[0].strip())
    except (ValueError, TypeError):
        return 0


def first_tag(tags, *keys):
    if not tags:
        return ""
    for k in keys:
        try:
            v = tags.get(k)
        except Exception:
            v = None
        if v:
            if isinstance(v, (list, tuple)):
                v = v[0] if v else ""
            v = str(v).strip()
            if v:
                return v
    return ""


def sort_name(name):
    """Sortiername wie in WMP12: führendes „The“ wird ignoriert."""
    s = (name or "").strip()
    if s.lower().startswith("the ") and len(s) > 4:
        s = s[4:]
    return s.lower()


def index_letter(name):
    s = sort_name(name)
    c = unicodedata.normalize("NFKD", s[:1]).encode("ascii", "ignore").decode().upper() if s else ""
    return c if c.isalpha() else "#"


def show_in_file_manager(path):
    """Öffnet den Dateimanager (Dolphin bzw. Explorer) und markiert die Datei."""
    if IS_WIN:
        subprocess.Popen(f'explorer /select,"{os.path.normpath(path)}"')
        return
    try:
        from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage
        iface = QDBusInterface("org.freedesktop.FileManager1", "/org/freedesktop/FileManager1",
                               "org.freedesktop.FileManager1", QDBusConnection.sessionBus())
        if iface.isValid():
            r = iface.call("ShowItems", [QUrl.fromLocalFile(path).toString()], "")
            if r.type() != QDBusMessage.ErrorMessage:
                return
    except Exception:
        pass
    subprocess.Popen(["xdg-open", os.path.dirname(path)])


def album_key(artist, album):
    return hashlib.md5(f"{artist.lower()}|{album.lower()}".encode()).hexdigest()


def cover_path(key):
    """Cover-Datei zu einem Album-Schlüssel. Getrennte Ausgaben desselben Albums (z. B. FLAC und MP3 in eigenen
    Ordnern) heißen „<schlüssel>~2“ usw. und teilen sich das Cover."""
    return COVER_DIR / f"{str(key).split('~', 1)[0]}.jpg"


def read_track(path):
    try:
        f = mutagen.File(path, easy=True)
    except Exception:
        f = None
    if f is None:
        return basic_track(path)
    tags = f.tags or {}
    title = first_tag(tags, "title", "Title") or Path(path).stem
    artist = first_tag(tags, "artist", "Author") or "Unbekannter Interpret"
    albumartist = first_tag(tags, "albumartist", "album artist", "WM/AlbumArtist") or artist
    album = first_tag(tags, "album", "WM/AlbumTitle") or "Unbekanntes Album"
    info = getattr(f, "info", None)
    try:
        size = os.path.getsize(path)
    except OSError:
        size = 0
    return {
        "path": path, "title": title, "artist": artist, "albumartist": albumartist, "album": album,
        "year": first_tag(tags, "date", "year", "WM/Year")[:4],
        "genre": first_tag(tags, "genre", "WM/Genre") or "Unbekanntes Genre",
        "composer": first_tag(tags, "composer", "WM/Composer"),
        "track": to_num(first_tag(tags, "tracknumber", "WM/TrackNumber")),
        "disc": to_num(first_tag(tags, "discnumber")) or 1,
        "length": float(getattr(info, "length", 0) or 0),
        "bitrate": int((getattr(info, "bitrate", 0) or 0) // 1000),
        "size": size, "type": Path(path).suffix.lower().lstrip("."),
        "cover": album_key(albumartist, album),
        **({"wr": wr} if (wr := read_rating(path)) else {}),
    }


def read_rating(path):
    """Sternbewertung (1–5) aus den Tags, wie sie Windows Media Player schreibt – sonst 0."""
    ext = Path(path).suffix.lower()
    try:
        if ext in (".mp3", ".mp2", ".aiff", ".aif", ".wav"):
            from mutagen.id3 import ID3
            frames = ID3(path).getall("POPM")
            if not frames:
                return 0
            frames.sort(key=lambda fr: "windows media player" not in (fr.email or "").lower())
            r = frames[0].rating
            return 0 if r <= 0 else 1 if r < 32 else 2 if r < 96 else 3 if r < 160 else 4 if r < 224 else 5
        if ext in (".wma", ".asf", ".wmv"):
            from mutagen.asf import ASF
            v = ASF(path).tags.get("WM/SharedUserRating")
            if not v:
                return 0
            r = int(str(v[0]))
            return 0 if r <= 0 else 1 if r < 25 else 2 if r < 50 else 3 if r < 75 else 4 if r < 99 else 5
    except Exception:
        return 0
    return 0


def basic_track(path):
    """Eintrag nur aus dem Dateinamen – für Formate ohne lesbare Tags (z. B. Videos)."""
    ext = Path(path).suffix.lower()
    if ext not in MEDIA_EXT:
        return None
    video = ext in VIDEO_EXT and ext != ".mp4"
    artist = "Unbekannter Interpret"
    album = "Videos" if video else "Unbekanntes Album"
    try:
        size = os.path.getsize(path)
    except OSError:
        size = 0
    return {"path": path, "title": Path(path).stem, "artist": artist, "albumartist": artist, "album": album,
            "year": "", "genre": "Unbekanntes Genre", "composer": "", "track": 0, "disc": 1, "length": 0.0,
            "bitrate": 0, "size": size, "type": ext.lstrip("."), "cover": album_key(artist, album)}


def arg_to_path(a):
    return QUrl(a).toLocalFile() if a.startswith("file:") else os.path.abspath(a)


def write_m3u(path, tracks):
    lines = ["#EXTM3U"]
    for t in tracks:
        lines.append(f"#EXTINF:{int(t.get('length') or -1)},{t.get('artist', '')} - {t.get('title', '')}")
        lines.append(t["path"])
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_playlist_file(path):
    """Liest M3U/M3U8/PLS/WPL. Gibt Liste von (Pfad oder URL, Titel) zurück."""
    base = Path(path).parent
    raw = Path(path).read_bytes()
    if Path(path).suffix.lower() in (".wpl", ".zpl"):
        # Windows-Media-Player-Wiedergabeliste (SMIL-XML): <media src="..."/>
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            return []
        res = []
        for el in root.iter():
            if el.tag.split("}")[-1].lower() == "media" and el.get("src"):
                src = el.get("src")
                if src.startswith(("http://", "https://")):
                    res.append((src, ""))
                    continue
                src = src.replace("\\", "/")
                pth = Path(src) if (Path(src).is_absolute() or re.match(r"^[A-Za-z]:/", src)) else base / src
                res.append((os.path.normpath(str(pth)), ""))
        return res
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    out, title = [], ""
    if Path(path).suffix.lower() == ".pls":
        titles = {}
        for line in text.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip().lower()
                if k.startswith("file"):
                    out.append([v.strip(), k[4:]])
                elif k.startswith("title"):
                    titles[k[5:]] = v.strip()
        return [(u, titles.get(n, "")) for u, n in out]
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF"):
            title = line.split(",", 1)[1].strip() if "," in line else ""
            continue
        if line.startswith("#"):
            continue
        if line.startswith(("http://", "https://")):
            out.append((line, title))
        else:
            if line.startswith("file:"):
                line = QUrl(line).toLocalFile()
            line = line.replace("\\", "/")
            pth = Path(line) if Path(line).is_absolute() else (base / line)
            out.append((os.path.normpath(str(pth)), title))
        title = ""
    return out


def stream_track(url, name=""):
    name = name or url
    return {"path": url, "title": name, "artist": "Internetradio", "albumartist": "Internetradio",
            "album": "Internetradio", "year": "", "genre": "Radio", "composer": "", "track": 0, "disc": 1,
            "length": 0.0, "bitrate": 0, "size": 0, "type": "stream", "stream": True,
            "cover": album_key("Internetradio", name)}


def parse_srt(path):
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252", errors="replace")
    cues = []
    tm = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")
    for block in re.split(r"\n\s*\n", text.replace("\r", "")):
        lines = block.strip().split("\n")
        for i, line in enumerate(lines):
            mm = tm.search(line)
            if mm:
                g = [int(x) for x in mm.groups()]
                start = ((g[0] * 60 + g[1]) * 60 + g[2]) * 1000 + g[3]
                end = ((g[4] * 60 + g[5]) * 60 + g[6]) * 1000 + g[7]
                body = re.sub(r"<[^>]+>|\{[^}]+\}", "", "\n".join(lines[i + 1:])).strip()
                if body:
                    cues.append((start, end, body))
                break
    cues.sort()
    return cues


def app_icon():
    icon = QIcon()
    for size in (16, 22, 24, 32, 48, 64, 128, 256):
        src = CoverCache.placeholder(size)
        pm = QPixmap(size, size); pm.fill(Qt.transparent)
        p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(QRectF(0, 0, size, size), size * 0.2, size * 0.2)
        p.setClipPath(path); p.drawPixmap(0, 0, src); p.end()
        icon.addPixmap(pm)
    return icon


def embedded_cover(path):
    try:
        f = mutagen.File(path)
    except Exception:
        return None
    if f is None:
        return None
    try:
        if getattr(f, "pictures", None):
            return sorted(f.pictures, key=lambda p: p.type != 3)[0].data
        tags = f.tags
        if not tags:
            return None
        for k in list(tags.keys()):
            if str(k).startswith("APIC"):
                return tags[k].data
        if "covr" in tags:
            return bytes(tags["covr"][0])
        if "metadata_block_picture" in tags:
            from mutagen.flac import Picture
            return Picture(base64.b64decode(tags["metadata_block_picture"][0])).data
    except Exception:
        return None
    return None


def folder_cover(path):
    try:
        imgs = [p for p in Path(path).parent.iterdir() if p.suffix.lower() in IMG_EXT]
    except OSError:
        return None
    for name in FOLDER_COVER_NAMES:
        for p in imgs:
            if p.stem.lower() == name or p.stem.lower().startswith(name + "_"):
                return p.read_bytes()
    return imgs[0].read_bytes() if imgs else None


def save_cover(path, key):
    data = embedded_cover(path) or folder_cover(path)
    if not data:
        return False
    img = QImage()
    if not img.loadFromData(data):
        return False
    img = img.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    return img.save(str(cover_path(key)), "JPG", 90)


def rounded_region(w, h, r):
    """Annäherung eines abgerundeten Rechtecks durch Rechtecke (x, y, b, h) – für die KWin-Blur-Region."""
    if r <= 0:
        return []
    rects = []
    for y in range(r):
        dy = r - y - 0.5
        inset = int(math.ceil(r - math.sqrt(max(0.0, r * r - dy * dy))))
        rects.append((inset, y, w - 2 * inset, 1))
        rects.append((inset, h - 1 - y, w - 2 * inset, 1))
    rects.append((0, r, w, h - 2 * r))
    return rects


def set_window_blur(widget, on, radius=0):
    """Weichzeichner hinter dem Fenster: KWin unter Linux, DWM unter Windows 10/11."""
    if IS_WIN:
        return set_win_blur(widget, on, radius)
    return set_kde_blur(widget, on, radius)


def set_win_blur(widget, on, radius=0):
    try:
        from ctypes import wintypes
        hwnd = wintypes.HWND(int(widget.winId()))
        user32 = ctypes.windll.user32

        class ACCENT(ctypes.Structure):
            _fields_ = [("AccentState", ctypes.c_int), ("AccentFlags", ctypes.c_int),
                        ("GradientColor", ctypes.c_uint), ("AnimationId", ctypes.c_int)]

        class WCAD(ctypes.Structure):
            _fields_ = [("Attribute", ctypes.c_int), ("Data", ctypes.c_void_p), ("SizeOfData", ctypes.c_size_t)]

        # Windows 11: runde Ecken vom System (DWMWA_WINDOW_CORNER_PREFERENCE = 33, DWMWCP_ROUND = 2)
        try:
            win = widget.window()
            rounded = not (win.isMaximized() or win.isFullScreen() or getattr(win, "_fs", False))
            want = (int(widget.winId()), 2 if rounded else 1)
            if getattr(widget, "_nn_corner", None) != want:
                pref = ctypes.c_int(want[1])
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(pref), ctypes.sizeof(pref))
                widget._nn_corner = want
        except Exception:
            pass
        # Nur ändern, was sich wirklich geändert hat: jedes erneute Setzen (vor allem SetWindowRgn)
        # zeichnet das ganze Fenster neu – beim Ziehen der Fenstergröße sah man das als Flackern.
        dpr = widget.devicePixelRatioF()
        w, h = int(widget.width() * dpr), int(widget.height() * dpr)
        r = int(round(radius * dpr))
        rgn_key = (w, h, r) if (on and r > 0) else None
        last = getattr(widget, "_nn_win_blur", None)
        key = (int(widget.winId()), bool(on), rgn_key)
        if last == key:
            return True
        if last is None or last[0] != key[0] or last[1] != key[1]:
            accent = ACCENT(3 if on else 0, 0, 0, 0)            # 3 = ACCENT_ENABLE_BLURBEHIND
            data = WCAD(19, ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p), ctypes.sizeof(accent))
            user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
        # Weichzeichner nur innerhalb der runden Ecken: Fensterbereich abrunden
        if rgn_key is not None:
            rgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, w + 1, h + 1, 2 * r, 2 * r)
            user32.SetWindowRgn(hwnd, rgn, True)
        elif last is None or last[0] != key[0] or last[2] is not None:
            user32.SetWindowRgn(hwnd, None, True)
        widget._nn_win_blur = key
        return True
    except Exception:
        return False


def set_kde_blur(widget, on, radius=0):
    """Weichzeichner hinter dem Fenster (KWin). Funktioniert für X11/XWayland-Fenster."""
    if QGuiApplication.platformName() != "xcb":
        return False
    try:
        lib = ctypes.util.find_library("X11")
        if not lib:
            return False
        x = ctypes.cdll.LoadLibrary(lib)
        x.XOpenDisplay.restype = ctypes.c_void_p
        x.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x.XInternAtom.restype = ctypes.c_ulong
        x.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
        x.XChangeProperty.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
        x.XDeleteProperty.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong]
        x.XFlush.argtypes = [ctypes.c_void_p]
        x.XCloseDisplay.argtypes = [ctypes.c_void_p]
        dpy = x.XOpenDisplay(None)
        if not dpy:
            return False
        atom = x.XInternAtom(dpy, b"_KDE_NET_WM_BLUR_BEHIND_REGION", 0)
        wid = int(widget.winId())
        if on:
            dpr = widget.devicePixelRatioF()
            rects = rounded_region(int(widget.width() * dpr), int(widget.height() * dpr), int(round(radius * dpr)))
            if rects:
                flat = [int(v) for rc in rects for v in rc]
                data = (ctypes.c_long * len(flat))(*flat)
                x.XChangeProperty(dpy, wid, atom, 6, 32, 0, data, len(flat))
            else:
                data = (ctypes.c_long * 1)(0)
                x.XChangeProperty(dpy, wid, atom, 6, 32, 0, data, 0)   # leere Region = ganzes Fenster
        else:
            x.XDeleteProperty(dpy, wid, atom)
        x.XFlush(dpy)
        x.XCloseDisplay(dpy)
        return True
    except Exception:
        return False


# ════════════════════════════════════════════════════════════════════════════
#  Online-Informationen: MusicBrainz + Cover Art Archive
# ════════════════════════════════════════════════════════════════════════════
MB_URL = "https://musicbrainz.org/ws/2/"
CAA_URL = "https://coverartarchive.org/"
USER_AGENT = f"NeoNote/{APP_VERSION} ( Linux-Musikplayer )"
_mb_lock = threading.Lock()
_mb_last = [0.0]
UNKNOWN = ("", "Unbekanntes Genre", "Unbekanntes Album", "Unbekannter Interpret")


class OnlineError(Exception):
    pass


def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def mb_get(path, **params):
    """Anfrage an MusicBrainz – höchstens eine pro Sekunde, wie von MusicBrainz verlangt."""
    params["fmt"] = "json"
    url = MB_URL + path + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        with _mb_lock:
            wait = 1.1 - (time.monotonic() - _mb_last[0])
            if wait > 0:
                time.sleep(wait)
            _mb_last[0] = time.monotonic()
        try:
            return json.loads(http_get(url))
        except urllib.error.HTTPError as e:
            if e.code in (503, 429) and attempt < 3:
                time.sleep(2 + attempt * 2)
                continue
            if e.code == 404:
                return None
            raise OnlineError(tr_("MusicBrainz antwortet mit Fehler {0}.").format(e.code))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise OnlineError(tr_("Keine Verbindung zu MusicBrainz ({0}).").format(getattr(e, 'reason', e)))
    raise OnlineError(tr_("MusicBrainz ist gerade ausgelastet. Bitte später noch einmal versuchen."))


def _phrase(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _words(s):
    special = set('+-&|!(){}[]^"~*?:\\/')
    return "".join("\\" + c if c in special else c for c in s).strip()


def _credit(ac):
    return "".join(c.get("name", "") + c.get("joinphrase", "") for c in (ac or [])) or ""


def _summary(r):
    media = r.get("media") or []
    fmts = []
    for m in media:
        f = m.get("format") or "?"
        if f not in fmts:
            fmts.append(f)
    labels = [li.get("label", {}).get("name", "") for li in (r.get("label-info") or []) if li.get("label")]
    return {
        "id": r["id"], "title": r.get("title", ""), "artist": _credit(r.get("artist-credit")),
        "year": (r.get("date") or "")[:4], "country": r.get("country") or "",
        "tracks": r.get("track-count") or sum(m.get("track-count", 0) for m in media),
        "format": (f"{len(media)}× " if len(media) > 1 else "") + ", ".join(fmts),
        "label": labels[0] if labels else "", "score": int(r.get("score", 0) or 0),
        "rgid": (r.get("release-group") or {}).get("id", ""),
        "type": (r.get("release-group") or {}).get("primary-type") or "",
    }


def mb_search(album, artist, fuzzy=False):
    a = _words(album) if fuzzy else _phrase(album)
    q = f"release:({a})" if fuzzy else f"release:{a}"
    if artist and artist not in UNKNOWN:
        q += f" AND artist:{_phrase(artist)}"
    data = mb_get("release/", query=q, limit=25) or {}
    res = [_summary(r) for r in data.get("releases", [])]
    res.sort(key=lambda r: -r["score"])
    return res


def _genre_name(g):
    return " ".join("-".join(p[:1].upper() + p[1:] for p in w.split("-")) for w in g.split())


def mb_release(mbid):
    r = mb_get(f"release/{mbid}", inc="recordings+release-groups+labels+artist-credits+genres")
    if not r:
        raise OnlineError(tr_("Album bei MusicBrainz nicht gefunden."))
    rg = r.get("release-group") or {}
    genres = sorted(r.get("genres") or [], key=lambda g: -g.get("count", 0))
    if not genres and rg.get("id"):
        g2 = mb_get(f"release-group/{rg['id']}", inc="genres") or {}
        genres = sorted(g2.get("genres") or [], key=lambda g: -g.get("count", 0))
    tracks = []
    for m in r.get("media") or []:
        for t in m.get("tracks") or []:
            try:
                pos = int(t.get("number") or t.get("position") or 0)
            except ValueError:
                pos = int(t.get("position") or 0)
            tracks.append({"disc": int(m.get("position") or 1), "pos": pos,
                           "title": t.get("title") or (t.get("recording") or {}).get("title", ""),
                           "length": (t.get("length") or 0) / 1000.0})
    labels = [li.get("label", {}).get("name", "") for li in (r.get("label-info") or []) if li.get("label")]
    return {
        "id": r["id"], "rgid": rg.get("id", ""), "title": r.get("title", ""),
        "artist": _credit(r.get("artist-credit")),
        "year": (r.get("date") or rg.get("first-release-date") or "")[:4],
        "genre": _genre_name(genres[0]["name"]) if genres else "",
        "label": labels[0] if labels else "", "tracks": tracks,
    }


def caa_cover(mbid, rgid="", size=500):
    """Lädt das Frontcover aus dem Cover Art Archive (erst Release, dann Release-Gruppe)."""
    urls = [f"{CAA_URL}release/{mbid}/front-{size}"]
    if rgid:
        urls.append(f"{CAA_URL}release-group/{rgid}/front-{size}")
    for url in urls:
        try:
            return http_get(url, timeout=30)
        except urllib.error.HTTPError as e:
            if e.code in (404, 400):
                continue
            raise OnlineError(tr_("Cover Art Archive antwortet mit Fehler {0}.").format(e.code))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise OnlineError(tr_("Keine Verbindung zum Cover Art Archive ({0}).").format(getattr(e, 'reason', e)))
    return None


def pick_match(results, n_tracks):
    """Automatische Auswahl: guter Treffer mit gleicher Titelanzahl, sonst nur sehr sichere Treffer."""
    for r in results:
        if r["score"] >= 85 and r["tracks"] == n_tracks:
            return r
    for r in results:
        if r["score"] >= 95 and abs(r["tracks"] - n_tracks) <= 2:
            return r
    return None


def plan_changes(album, rel, overwrite=False):
    """Vergleicht die lokalen Titel mit dem MusicBrainz-Album. Ergebnis: {pfad: {feld: wert}}."""
    flat = rel["tracks"]
    local = album["tracks"]
    multi = len({r["disc"] for r in flat}) > 1
    changes = {}
    for i, t in enumerate(local):
        r = None
        if t.get("track"):
            r = next((x for x in flat if x["pos"] == t["track"] and (x["disc"] == t.get("disc", 1) or not multi)), None)
            if r and not overwrite and SequenceMatcher(None, r["title"].lower(), t["title"].lower()).ratio() < 0.35 \
                    and t["title"] != Path(t["path"]).stem:
                r = None   # Nummer passt, Titel aber gar nicht – lieber über den Namen suchen
        if r is None and len(flat) == len(local) and not any(x.get("track") for x in local):
            r = flat[i]
        if r is None:
            best = max(flat, key=lambda x: SequenceMatcher(None, x["title"].lower(), t["title"].lower()).ratio(),
                       default=None)
            if best and SequenceMatcher(None, best["title"].lower(), t["title"].lower()).ratio() >= 0.6:
                r = best
        ch = {}

        def want(field, new, missing):
            if new and (overwrite or missing) and str(t.get(field, "")) != str(new):
                ch[field] = new

        want("year", rel["year"], not t.get("year"))
        want("genre", rel["genre"], t.get("genre") in UNKNOWN)
        if r:
            want("track", r["pos"], not t.get("track"))
            if multi:
                want("disc", r["disc"], t.get("disc", 1) == 1 and r["disc"] != 1)
            want("title", r["title"], t["title"] == Path(t["path"]).stem)
        if ch:
            changes[t["path"]] = ch
    return changes


def image_from_mime(md):
    """Bilddaten aus Drag & Drop oder Zwischenablage: Bilddatei, Bild aus dem Browser oder Bild-URL."""
    if md is None:
        return None
    if md.hasUrls():
        for u in md.urls():
            if u.isLocalFile() and Path(u.toLocalFile()).suffix.lower() in IMG_EXT:
                try:
                    return Path(u.toLocalFile()).read_bytes()
                except OSError:
                    continue
    if md.hasImage():
        img = QImage(md.imageData())
        if not img.isNull():
            buf = QBuffer(); buf.open(QBuffer.WriteOnly); img.save(buf, "PNG")
            return bytes(buf.data())
    if md.hasUrls():
        for u in md.urls():
            if u.scheme() in ("http", "https"):
                try:
                    import urllib.request
                    req = urllib.request.Request(u.toString(), headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"})
                    with urllib.request.urlopen(req, timeout=10) as r:
                        data = r.read(15 * 1024 * 1024)
                    if QImage.fromData(data).isNull():
                        continue
                    return data
                except Exception:
                    continue
    return None


def mime_has_image(md):
    if md is None:
        return False
    if md.hasImage():
        return True
    for u in md.urls() if md.hasUrls() else []:
        if u.isLocalFile() and Path(u.toLocalFile()).suffix.lower() in IMG_EXT:
            return True
        if u.scheme() in ("http", "https") and re.search(r"\.(jpe?g|png|webp|bmp)(\?|$)", u.path() + "?", re.I):
            return True
    return False


def normalize_jpeg(data, max_size=1200):
    img = QImage()
    if not data or not img.loadFromData(data):
        return None
    if max(img.width(), img.height()) > max_size:
        img = img.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    buf = QBuffer()
    buf.open(QBuffer.WriteOnly)
    img.convertToFormat(QImage.Format_RGB32).save(buf, "JPG", 92)
    return bytes(buf.data())


def write_tags(path, ch):
    from mutagen.asf import ASF
    from mutagen.id3 import ID3, TALB, TCOM, TCON, TDRC, TIT2, TPE1, TPE2, TPOS, TRCK
    f = mutagen.File(path)
    if f is None:
        raise ValueError(tr_("Unbekanntes Dateiformat"))
    if isinstance(f, ASF):
        m = {"year": "WM/Year", "genre": "WM/Genre", "track": "WM/TrackNumber", "disc": "WM/PartOfSet", "title": "Title",
             "artist": "Author", "albumartist": "WM/AlbumArtist", "album": "WM/AlbumTitle", "composer": "WM/Composer"}
        for k, v in ch.items():
            f.tags[m[k]] = [str(v)]
        f.save()
        return
    if f.tags is None:
        f.add_tags()
    if isinstance(f.tags, ID3):                                       # MP3, WAV, AIFF
        frames = {"year": TDRC, "genre": TCON, "track": TRCK, "disc": TPOS, "title": TIT2,
                  "artist": TPE1, "albumartist": TPE2, "album": TALB, "composer": TCOM}
        for k, v in ch.items():
            cls = frames[k]
            f.tags.setall(cls.__name__, [cls(encoding=3, text=[str(v)])])
        f.save()
        return
    e = mutagen.File(path, easy=True)                                 # FLAC, Ogg, Opus, M4A …
    if e.tags is None:
        e.add_tags()
    m = {"year": "date", "genre": "genre", "track": "tracknumber", "disc": "discnumber", "title": "title",
         "artist": "artist", "albumartist": "albumartist", "album": "album", "composer": "composer"}
    for k, v in ch.items():
        if v in ("", 0) and k in ("year", "track", "disc", "composer", "genre"):
            try:
                del e[m[k]]
            except KeyError:
                pass
        else:
            e[m[k]] = [str(v)]
    e.save()


def embed_cover(path, jpg):
    from mutagen.flac import FLAC, Picture
    from mutagen.id3 import APIC, ID3
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.oggopus import OggOpus
    from mutagen.oggvorbis import OggVorbis
    f = mutagen.File(path)
    if f is None:
        raise ValueError(tr_("Unbekanntes Dateiformat"))

    def picture():
        pic = Picture()
        pic.type, pic.mime, pic.desc, pic.data = 3, "image/jpeg", tr_("Cover"), jpg
        return pic

    if isinstance(f, FLAC):
        f.clear_pictures(); f.add_picture(picture())
    elif isinstance(f, MP4):
        if f.tags is None:
            f.add_tags()
        f.tags["covr"] = [MP4Cover(jpg, imageformat=MP4Cover.FORMAT_JPEG)]
    elif isinstance(f, (OggVorbis, OggOpus)):
        f["metadata_block_picture"] = [base64.b64encode(picture().write()).decode("ascii")]
    else:
        if f.tags is None:
            f.add_tags()
        if not isinstance(f.tags, ID3):
            raise ValueError(tr_("Dieses Format unterstützt keine eingebetteten Cover"))
        f.tags.delall("APIC")
        f.tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc=tr_("Cover"), data=jpg))
    f.save()


def with_pending(album, changes, pending):
    """Ergänzt die Änderungen um Angaben, die bisher nur in der Bibliothek gespeichert waren."""
    out = {p: dict(c) for p, c in changes.items()}
    for t in album["tracks"]:
        pend = pending.get(t["path"])
        if pend:
            out[t["path"]] = {**pend, **out.get(t["path"], {})}
    return out


def write_album(album, changes, cover_bytes, opts, replace_cover):
    """Schreibt Änderungen (läuft im Hintergrund-Thread). Gibt Pfade zurück, deren Tags nicht geschrieben werden konnten."""
    failed = []
    if opts.get("write_tags"):
        for path, ch in changes.items():
            try:
                write_tags(path, ch)
            except Exception:
                failed.append(path)
    if cover_bytes:
        jpg = normalize_jpeg(cover_bytes)
        if jpg:
            img = QImage(); img.loadFromData(jpg)
            COVER_DIR.mkdir(parents=True, exist_ok=True)
            img.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation).save(
                str(cover_path(album['key'])), "JPG", 90)
            if opts.get("embed_cover"):
                for t in album["tracks"]:
                    try:
                        embed_cover(t["path"], jpg)
                    except Exception:
                        pass
            if opts.get("folder_cover") and album["tracks"]:
                target = Path(album["tracks"][0]["path"]).parent / "cover.jpg"
                if replace_cover or not target.exists():
                    try:
                        target.write_bytes(jpg)
                    except OSError:
                        pass
    return failed


class Job(QThread):
    """Führt eine Funktion im Hintergrund aus."""
    done = Signal(object)
    failed = Signal(str)

    def __init__(self, fn, parent):
        super().__init__(parent)
        self.fn = fn

    def run(self):
        try:
            self.done.emit(self.fn())
        except OnlineError as e:
            self.failed.emit(str(e))
        except Exception as e:
            self.failed.emit(tr_("Fehler: {0}").format(e))


class BatchLookup(QThread):
    """Sucht für viele Alben automatisch fehlende Infos und Cover."""
    progress = Signal(int, int, str)
    album_done = Signal(str, object, bool, object)
    finished_batch = Signal(int, int, int, str)

    def __init__(self, albums, opts, parent, pending=None):
        super().__init__(parent)
        self.albums, self.opts = albums, opts
        self.pending = pending or {}

    def run(self):
        ok = missing = errors = 0
        conn_errors = 0
        msg, last_err = "", ""
        for i, a in enumerate(self.albums):
            if self.isInterruptionRequested():
                msg = "abgebrochen"
                break
            self.progress.emit(i, len(self.albums), a["title"])
            try:
                n = len(a["tracks"])
                hit = pick_match(mb_search(a["title"], a["artist"]), n)
                if hit is None:
                    hit = pick_match(mb_search(a["title"], a["artist"], fuzzy=True), n)
                if hit is None:
                    missing += 1
                    continue
                rel = mb_release(hit["id"])
                cover = None
                if not (cover_path(a['key'])).exists():
                    cover = caa_cover(rel["id"], rel["rgid"])
                changes = plan_changes(a, rel)
                if self.opts.get("write_tags"):
                    changes = with_pending(a, changes, self.pending)
                if changes or cover:
                    failed = write_album(a, changes, cover, self.opts, replace_cover=False)
                    self.album_done.emit(a["key"], changes, cover is not None, failed)
                    ok += 1
                conn_errors = 0
            except OnlineError as e:
                errors += 1; conn_errors += 1; last_err = str(e)
                if conn_errors >= 3:
                    msg = "stop"
                    break
            except Exception as e:
                errors += 1; last_err = tr_("Fehler: {0}").format(e)
        self.progress.emit(len(self.albums), len(self.albums), "")
        self.finished_batch.emit(ok, missing, errors, msg or last_err)


# ════════════════════════════════════════════════════════════════════════════
#  MPRIS – Anbindung an KDE (Medien-Widget, Sperrbildschirm, globale Medientasten)
# ════════════════════════════════════════════════════════════════════════════
MPRIS_NAME = "org.mpris.MediaPlayer2.neonote"
MPRIS_PATH = "/org/mpris/MediaPlayer2"
MPRIS_ROOT = "org.mpris.MediaPlayer2"
MPRIS_PLAYER = "org.mpris.MediaPlayer2.Player"
DBUS_PROPS = "org.freedesktop.DBus.Properties"
MPRIS_XML = """<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node>
 <interface name="org.freedesktop.DBus.Introspectable"><method name="Introspect"><arg direction="out" type="s"/></method></interface>
 <interface name="org.freedesktop.DBus.Peer"><method name="Ping"/></interface>
 <interface name="org.freedesktop.DBus.Properties">
  <method name="Get"><arg direction="in" type="s"/><arg direction="in" type="s"/><arg direction="out" type="v"/></method>
  <method name="GetAll"><arg direction="in" type="s"/><arg direction="out" type="a{sv}"/></method>
  <method name="Set"><arg direction="in" type="s"/><arg direction="in" type="s"/><arg direction="in" type="v"/></method>
  <signal name="PropertiesChanged"><arg type="s"/><arg type="a{sv}"/><arg type="as"/></signal>
 </interface>
 <interface name="org.mpris.MediaPlayer2">
  <method name="Raise"/><method name="Quit"/>
  <property name="CanQuit" type="b" access="read"/><property name="CanRaise" type="b" access="read"/>
  <property name="Fullscreen" type="b" access="readwrite"/><property name="CanSetFullscreen" type="b" access="read"/>
  <property name="HasTrackList" type="b" access="read"/><property name="Identity" type="s" access="read"/>
  <property name="DesktopEntry" type="s" access="read"/>
  <property name="SupportedUriSchemes" type="as" access="read"/><property name="SupportedMimeTypes" type="as" access="read"/>
 </interface>
 <interface name="org.mpris.MediaPlayer2.Player">
  <method name="Next"/><method name="Previous"/><method name="Pause"/><method name="PlayPause"/>
  <method name="Stop"/><method name="Play"/>
  <method name="Seek"><arg direction="in" type="x"/></method>
  <method name="SetPosition"><arg direction="in" type="o"/><arg direction="in" type="x"/></method>
  <method name="OpenUri"><arg direction="in" type="s"/></method>
  <signal name="Seeked"><arg type="x"/></signal>
  <property name="PlaybackStatus" type="s" access="read"/><property name="LoopStatus" type="s" access="readwrite"/>
  <property name="Rate" type="d" access="readwrite"/><property name="Shuffle" type="b" access="readwrite"/>
  <property name="Metadata" type="a{sv}" access="read"/><property name="Volume" type="d" access="readwrite"/>
  <property name="Position" type="x" access="read"/><property name="MinimumRate" type="d" access="read"/>
  <property name="MaximumRate" type="d" access="read"/><property name="CanGoNext" type="b" access="read"/>
  <property name="CanGoPrevious" type="b" access="read"/><property name="CanPlay" type="b" access="read"/>
  <property name="CanPause" type="b" access="read"/><property name="CanSeek" type="b" access="read"/>
  <property name="CanControl" type="b" access="read"/>
 </interface>
</node>"""
MPRIS_MIMES = ["audio/mpeg", "audio/flac", "audio/ogg", "audio/opus", "audio/mp4", "audio/x-m4a", "audio/aac",
               "audio/x-wav", "audio/x-ms-wma", "audio/x-ape", "audio/x-wavpack", "audio/x-aiff", "video/mp4",
               "video/x-matroska", "video/webm", "video/x-msvideo", "video/quicktime", "video/x-ms-wmv"]


def smtc_available():
    if not IS_WIN:
        return False
    try:
        import winrt.windows.media.playback  # noqa: F401
        import winrt.windows.media  # noqa: F401
        return True
    except Exception:
        return False


class SleepGuard:
    """Hält den Rechner wach, solange etwas läuft – wie im Windows Media Player.
    Musik: kein Standby (Bildschirm darf aus). Video: zusätzlich bleibt der Bildschirm an.
    Windows: SetThreadExecutionState. Linux: D-Bus-Sperre bei KDE (PowerManagement) bzw. GNOME (SessionManager)."""

    REASON = "Wiedergabe läuft"

    def __init__(self):
        self.mode = None
        self._conn = None
        self._pm = None          # (Art, Cookie) der Standby-Sperre
        self._ss = None          # Cookie der Bildschirmschoner-Sperre

    def set(self, mode):
        if mode == self.mode:
            return
        self.mode = mode
        try:
            if IS_WIN:
                ES_CONTINUOUS, ES_SYSTEM, ES_DISPLAY = 0x80000000, 0x00000001, 0x00000002
                flags = ES_CONTINUOUS
                if mode:
                    flags |= ES_SYSTEM
                if mode == "video":
                    flags |= ES_DISPLAY
                ctypes.windll.kernel32.SetThreadExecutionState(ctypes.c_uint(flags))
            else:
                self._linux(mode)
        except Exception:
            pass

    def _call(self, path, bus, iface, method, sig, args):
        from jeepney import DBusAddress, MessageType, new_method_call
        if self._conn is None:
            from jeepney.io.blocking import open_dbus_connection
            self._conn = open_dbus_connection(bus="SESSION")
        addr = DBusAddress(path, bus_name=bus, interface=iface)
        reply = self._conn.send_and_get_reply(new_method_call(addr, method, sig, args), timeout=2)
        if reply.header.message_type != MessageType.method_return:
            raise RuntimeError(reply.body)
        return reply.body

    def _linux(self, mode):
        if mode and self._pm is None:
            try:
                ck = self._call("/org/freedesktop/PowerManagement/Inhibit", "org.freedesktop.PowerManagement",
                                "org.freedesktop.PowerManagement.Inhibit", "Inhibit", "ss", (APP_NAME, self.REASON))[0]
                self._pm = ("kde", ck)
            except Exception:
                try:     # GNOME u. a.: 4 = Standby verhindern
                    ck = self._call("/org/gnome/SessionManager", "org.gnome.SessionManager",
                                    "org.gnome.SessionManager", "Inhibit", "susu", ("neonote", 0, self.REASON, 4))[0]
                    self._pm = ("gnome", ck)
                except Exception:
                    self._pm = None
        elif not mode and self._pm is not None:
            kind, ck = self._pm
            self._pm = None
            if kind == "kde":
                self._call("/org/freedesktop/PowerManagement/Inhibit", "org.freedesktop.PowerManagement",
                           "org.freedesktop.PowerManagement.Inhibit", "UnInhibit", "u", (ck,))
            else:
                self._call("/org/gnome/SessionManager", "org.gnome.SessionManager",
                           "org.gnome.SessionManager", "Uninhibit", "u", (ck,))
        if mode == "video" and self._ss is None:
            try:
                self._ss = self._call("/org/freedesktop/ScreenSaver", "org.freedesktop.ScreenSaver",
                                      "org.freedesktop.ScreenSaver", "Inhibit", "ss", (APP_NAME, self.REASON))[0]
            except Exception:
                self._ss = None
        elif mode != "video" and self._ss is not None:
            ck, self._ss = self._ss, None
            self._call("/org/freedesktop/ScreenSaver", "org.freedesktop.ScreenSaver",
                       "org.freedesktop.ScreenSaver", "UnInhibit", "u", (ck,))


def media_control_available():
    return smtc_available() if IS_WIN else jeepney_available()


def jeepney_available():
    try:
        import jeepney  # noqa: F401
        return True
    except ImportError:
        return False


def _media_command(self, cmd, arg):
    """Befehle von MPRIS/SMTC (Hauptthread)."""
    if True:
        w = self.win
        st = w.player.playbackState()
        if cmd == "PlayPause":
            w.toggle_play()
        elif cmd == "Play":
            if st != QMediaPlayer.PlayingState:
                w.toggle_play()
        elif cmd == "Pause":
            if st == QMediaPlayer.PlayingState:
                w.player.pause()
        elif cmd == "Stop":
            w.stop()
        elif cmd == "Next":
            w.next_track()
        elif cmd == "Previous":
            w.prev_track()
        elif cmd == "Seek":
            target = w.player.position() + int(arg) // 1000
            if target >= w.player.duration() > 0:
                w.next_track()
            else:
                w.player.setPosition(max(0, target)); self.set_position(max(0, target), seeked=True)
        elif cmd == "SetPosition":
            track_id, pos = arg
            if w.cur and track_id == f"/org/neonote/track/{w.cur['id']}" and 0 <= pos // 1000 <= w.player.duration():
                w.player.setPosition(pos // 1000); self.set_position(pos // 1000, seeked=True)
        elif cmd == "Raise":
            w.show_window()
        elif cmd == "Quit":
            w.quit_app()
        elif cmd == "OpenUri":
            w.open_files([arg_to_path(arg)] if not arg.startswith("http") else [])
            if arg.startswith("http"):
                w.play_tracks([stream_track(arg)], 0)
        elif cmd == "set:Volume":
            w.vol.setValue(int(round(max(0.0, min(1.0, float(arg))) * 100)))
        elif cmd == "set:Shuffle":
            w.btn_shuffle.setChecked(bool(arg)); w.toggle_shuffle()
        elif cmd == "set:LoopStatus":
            w.repeat = {"None": 0, "Playlist": 1, "Track": 2}.get(arg, 0)
            w.settings.setValue("repeat", w.repeat); w._update_repeat_btn()
        elif cmd == "set:Fullscreen":
            if bool(arg) != w._fs:
                w.toggle_fullscreen()
        self.update_all()


class Smtc(QObject):
    """Windows-Mediensteuerung (Lautstärke-Overlay, Sperrbildschirm, Medientasten) über WinRT.
    Bietet dieselbe Schnittstelle wie Mpris."""
    command = Signal(str, object)

    def __init__(self, win):
        super().__init__(win)
        from winrt.windows.media.playback import MediaPlayer
        import winrt.windows.media as wm
        self.win, self.wm = win, wm
        self.pos_us, self.pos_time, self.playing = 0, time.monotonic(), False
        self._mp = MediaPlayer()
        self._mp.command_manager.is_enabled = False         # eigene Wiedergabe, nur die Steuerung nutzen
        self.smtc = self._mp.system_media_transport_controls
        for k in ("is_play_enabled", "is_pause_enabled", "is_next_enabled", "is_previous_enabled", "is_stop_enabled"):
            setattr(self.smtc, k, True)
        self.smtc.is_enabled = True
        B = wm.SystemMediaTransportControlsButton
        self._map = {B.PLAY: "Play", B.PAUSE: "Pause", B.STOP: "Stop", B.NEXT: "Next", B.PREVIOUS: "Previous"}
        self.command.connect(self._on_command)
        self._token = self.smtc.add_button_pressed(self._pressed)
        self._last_meta = None
        self.update_all()

    def _pressed(self, _sender, args):                      # läuft in einem WinRT-Thread
        cmd = self._map.get(args.button)
        if cmd:
            self.command.emit(cmd, None)

    def _on_command(self, cmd, arg):
        _media_command(self, cmd, arg)

    def update_all(self, emit=True):
        w, wm = self.win, self.wm
        try:
            st = w.player.playbackState()
            self.playing = st == QMediaPlayer.PlayingState
            self.smtc.playback_status = (wm.MediaPlaybackStatus.PLAYING if self.playing else
                                         wm.MediaPlaybackStatus.PAUSED if st == QMediaPlayer.PausedState
                                         else wm.MediaPlaybackStatus.STOPPED)
            t = w.cur["t"] if w.cur else None
            meta = None if not t else (w.stream_title or t["title"] if t.get("stream") else t["title"],
                                       t["title"] if t.get("stream") else t["artist"], t.get("album", ""),
                                       t.get("cover"), w.cur["id"])
            if meta != self._last_meta:
                self._last_meta = meta
                du = self.smtc.display_updater
                if not meta:
                    du.clear_all(); du.update()
                else:
                    du.type = wm.MediaPlaybackType.MUSIC
                    mp = du.music_properties
                    mp.title, mp.artist, mp.album_title = meta[0], meta[1], meta[2] or ""
                    du.update()
                    self._set_thumb(t)
            d = w.player.duration()
            if d > 0:
                tp = wm.SystemMediaTransportControlsTimelineProperties()
                tp.start_time = timedelta(0); tp.min_seek_time = timedelta(0)
                tp.end_time = tp.max_seek_time = timedelta(milliseconds=d)
                tp.position = timedelta(milliseconds=max(0, w.player.position()))
                self.smtc.update_timeline_properties(tp)
        except Exception:
            pass

    def _set_thumb(self, t):
        f = cover_path(t['cover'])
        if not f.exists():
            f = COVER_DIR / f"platzhalter-{T.accent.name().lstrip('#')}.png"
            if not f.exists():
                COVER_DIR.mkdir(parents=True, exist_ok=True)
                CoverCache.placeholder(300).save(str(f), "PNG")
        path, du = str(f), self.smtc.display_updater

        def work():
            try:
                import asyncio
                from winrt.windows.storage import StorageFile
                from winrt.windows.storage.streams import RandomAccessStreamReference
                sf = asyncio.run(StorageFile.get_file_from_path_async(path))
                du.thumbnail = RandomAccessStreamReference.create_from_file(sf)
                du.update()
            except Exception:
                pass
        threading.Thread(target=work, daemon=True).start()

    def set_position(self, ms, seeked=False):
        self.pos_us, self.pos_time = int(ms) * 1000, time.monotonic()
        if seeked:
            self.update_all()

    def update_track(self):
        self.update_all()

    def stop(self):
        try:
            self.smtc.remove_button_pressed(self._token)
            self.smtc.is_enabled = False
        except Exception:
            pass


class Mpris(QObject):
    """Stellt NeoNote über D-Bus als MPRIS-Player bereit (benötigt python-jeepney)."""
    command = Signal(str, object)

    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.lock = threading.Lock()
        self.outq = queue.Queue()
        self.stop_ev = threading.Event()
        self.root_props, self.player_props = {}, {}
        self.pos_us, self.pos_time, self.playing = 0, time.monotonic(), False
        self.command.connect(self._on_command)
        self.update_all(emit=False)
        self.thread = threading.Thread(target=self._run, name="mpris", daemon=True)
        self.thread.start()

    # ── Zustand (Hauptthread) ─────────────────────────────────────────────
    def _art_url(self, t):
        f = cover_path(t['cover'])
        if not f.exists():
            f = COVER_DIR / f"platzhalter-{T.accent.name().lstrip('#')}.png"
            if not f.exists():
                COVER_DIR.mkdir(parents=True, exist_ok=True)
                CoverCache.placeholder(300).save(str(f), "PNG")
        return QUrl.fromLocalFile(str(f)).toString()

    def _metadata(self):
        w = self.win
        if not w.cur:
            return {"mpris:trackid": ("o", "/org/mpris/MediaPlayer2/TrackList/NoTrack")}
        t = w.cur["t"]
        dur_ms = w.player.duration() or int((t.get("length") or 0) * 1000)
        md = {"mpris:trackid": ("o", f"/org/neonote/track/{w.cur['id']}"),
              "mpris:length": ("x", int(dur_ms) * 1000),
              "mpris:artUrl": ("s", self._art_url(t))}
        if t.get("stream"):
            md["xesam:title"] = ("s", w.stream_title or t["title"])
            md["xesam:artist"] = ("as", [t["title"]])
            md["xesam:url"] = ("s", t["path"])
        else:
            md["xesam:title"] = ("s", t["title"])
            md["xesam:artist"] = ("as", [t["artist"]])
            md["xesam:album"] = ("s", t["album"])
            md["xesam:albumArtist"] = ("as", [t.get("albumartist") or t["artist"]])
            md["xesam:url"] = ("s", QUrl.fromLocalFile(t["path"]).toString())
            if t.get("track"):
                md["xesam:trackNumber"] = ("i", int(t["track"]))
            if t.get("genre") and t["genre"] not in UNKNOWN:
                md["xesam:genre"] = ("as", [t["genre"]])
            r = w.stats.rating(t["path"])
            if r:
                md["xesam:userRating"] = ("d", r / 5.0)
        return md

    def update_all(self, emit=True):
        w = self.win
        st = w.player.playbackState()
        status = {QMediaPlayer.PlayingState: "Playing", QMediaPlayer.PausedState: "Paused"}.get(st, "Stopped")
        has = w.cur is not None
        player = {
            "PlaybackStatus": ("s", status),
            "LoopStatus": ("s", ["None", "Playlist", "Track"][w.repeat]),
            "Rate": ("d", 1.0), "MinimumRate": ("d", 1.0), "MaximumRate": ("d", 1.0),
            "Shuffle": ("b", bool(w.shuffle)),
            "Metadata": ("a{sv}", self._metadata()),
            "Volume": ("d", w.vol.value() / 100.0),
            "CanGoNext": ("b", len(w.queue) > 1 or w.repeat > 0),
            "CanGoPrevious": ("b", has),
            "CanPlay": ("b", has or bool(w.queue)),
            "CanPause": ("b", has),
            "CanSeek": ("b", has and w.player.duration() > 0),
            "CanControl": ("b", True),
        }
        root = {
            "CanQuit": ("b", True), "CanRaise": ("b", True), "HasTrackList": ("b", False),
            "Fullscreen": ("b", bool(w._fs)), "CanSetFullscreen": ("b", True),
            "Identity": ("s", APP_TITLE), "DesktopEntry": ("s", "neonote"),
            "SupportedUriSchemes": ("as", ["file", "http", "https"]),
            "SupportedMimeTypes": ("as", MPRIS_MIMES),
        }
        with self.lock:
            changed_p = {k: v for k, v in player.items() if self.player_props.get(k) != v}
            changed_r = {k: v for k, v in root.items() if self.root_props.get(k) != v}
            self.player_props, self.root_props = player, root
            self.playing = status == "Playing"
        if emit:
            from jeepney import DBusAddress, new_signal
            addr = DBusAddress(MPRIS_PATH, interface=DBUS_PROPS)
            if changed_p:
                self.outq.put(new_signal(addr, "PropertiesChanged", "sa{sv}as", (MPRIS_PLAYER, changed_p, [])))
            if changed_r:
                self.outq.put(new_signal(addr, "PropertiesChanged", "sa{sv}as", (MPRIS_ROOT, changed_r, [])))

    def set_position(self, ms, seeked=False):
        with self.lock:
            self.pos_us, self.pos_time = int(ms) * 1000, time.monotonic()
        if seeked:
            from jeepney import DBusAddress, new_signal
            self.outq.put(new_signal(DBusAddress(MPRIS_PATH, interface=MPRIS_PLAYER), "Seeked", "x",
                                     (int(ms) * 1000,)))

    def update_track(self):
        self.update_all()

    def stop(self):
        self.stop_ev.set()
        self.thread.join(1.5)

    # ── Befehle (Hauptthread) ─────────────────────────────────────────────
    def _on_command(self, cmd, arg):
        _media_command(self, cmd, arg)



    # ── D-Bus-Thread ──────────────────────────────────────────────────────
    def _props(self, iface):
        with self.lock:
            if iface == MPRIS_ROOT:
                return dict(self.root_props)
            if iface == MPRIS_PLAYER:
                props = dict(self.player_props)
                pos = self.pos_us + (int((time.monotonic() - self.pos_time) * 1e6) if self.playing else 0)
                props["Position"] = ("x", int(pos))
                return props
        return None

    def _handle(self, msg):
        from jeepney import HeaderFields, new_error, new_method_return
        h = msg.header.fields
        path = h.get(HeaderFields.path, "")
        iface = h.get(HeaderFields.interface, "")
        member = h.get(HeaderFields.member, "")
        if iface == "org.freedesktop.DBus.Introspectable" or member == "Introspect" and not iface:
            nodes = {"/": "org", "/org": "mpris", "/org/mpris": "MediaPlayer2"}
            if path in nodes:
                return new_method_return(msg, "s", (f'<node><node name="{nodes[path]}"/></node>',))
            return new_method_return(msg, "s", (MPRIS_XML,))
        if iface == "org.freedesktop.DBus.Peer":
            return new_method_return(msg)
        if path != MPRIS_PATH:
            return new_error(msg, "org.freedesktop.DBus.Error.UnknownObject", "s", (f"Kein Objekt {path}",))
        if iface == DBUS_PROPS:
            if member == "Get":
                i, name = msg.body
                props = self._props(i)
                if props is None or name not in props:
                    return new_error(msg, "org.freedesktop.DBus.Error.InvalidArgs", "s", (f"Unbekannt: {name}",))
                return new_method_return(msg, "v", (props[name],))
            if member == "GetAll":
                props = self._props(msg.body[0])
                return new_method_return(msg, "a{sv}", (props or {},))
            if member == "Set":
                _i, name, (_sig, val) = msg.body
                if name in ("Volume", "Shuffle", "LoopStatus", "Fullscreen"):
                    self.command.emit("set:" + name, val)
                    return new_method_return(msg)
                return new_error(msg, "org.freedesktop.DBus.Error.PropertyReadOnly", "s", (name,))
        if member in ("Raise", "Quit", "Next", "Previous", "Pause", "PlayPause", "Stop", "Play"):
            self.command.emit(member, None)
            return new_method_return(msg)
        if member == "Seek":
            self.command.emit("Seek", int(msg.body[0]))
            return new_method_return(msg)
        if member == "SetPosition":
            self.command.emit("SetPosition", (str(msg.body[0]), int(msg.body[1])))
            return new_method_return(msg)
        if member == "OpenUri":
            self.command.emit("OpenUri", str(msg.body[0]))
            return new_method_return(msg)
        return new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod", "s", (f"Unbekannte Methode {member}",))

    def _run(self):
        try:
            from jeepney import MessageType, new_error
            from jeepney.bus_messages import message_bus
            from jeepney.io.blocking import open_dbus_connection
            conn = open_dbus_connection(bus="SESSION")
            conn.send_and_get_reply(message_bus.RequestName(MPRIS_NAME), timeout=3)
        except Exception:
            return
        while not self.stop_ev.is_set():
            try:
                while True:
                    conn.send(self.outq.get_nowait())
            except queue.Empty:
                pass
            except Exception:
                break
            try:
                msg = conn.receive(timeout=0.1)
            except TimeoutError:
                continue
            except Exception:
                break
            if msg.header.message_type != MessageType.method_call:
                continue
            try:
                reply = self._handle(msg)
            except Exception as e:
                reply = new_error(msg, "org.freedesktop.DBus.Error.Failed", "s", (str(e),))
            if reply is not None:
                try:
                    conn.send(reply)
                except Exception:
                    break
        try:
            conn.close()
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════════════════
#  Wiedergabe: mpv für Musik/Radio (Gapless, Equalizer), Qt Multimedia für Videos
# ════════════════════════════════════════════════════════════════════════════
EQ_BANDS = [31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
EQ_PRESETS = OrderedDict([
    ("Neutral", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("Rock", [5, 4, 3, 1, -1, -1, 1, 3, 4, 5]),
    ("Pop", [-1, 1, 3, 4, 3, 0, -1, -1, 1, 2]),
    ("Dance", [6, 5, 2, 0, 0, -2, -2, 0, 4, 5]),
    ("Techno", [5, 4, 1, -1, -2, 0, 2, 4, 4, 5]),
    ("Jazz", [3, 2, 1, 2, -1, -1, 0, 1, 2, 3]),
    ("Klassik", [4, 3, 2, 1, -1, -1, 0, 2, 3, 4]),
    ("Bassverstärkung", [7, 6, 5, 3, 1, 0, 0, 0, 0, 0]),
    ("Höhenverstärkung", [0, 0, 0, 0, 0, 1, 3, 5, 6, 7]),
    ("Sprache", [-3, -2, -1, 1, 4, 4, 3, 1, 0, -2]),
    ("Loudness (leise hören)", [5, 4, 1, 0, -1, 0, 0, 1, 4, 5]),
])


def mpv_available():
    try:
        import mpv  # noqa: F401  (lädt libmpv)
        return True
    except Exception:
        return False


def eq_filter(enabled, gains, preamp, limiter_level=True):
    if not enabled:
        return ""
    parts = []
    if preamp:
        parts.append(f"volume=volume={preamp}dB")
    parts += [f"equalizer=f={f}:t=o:w=1:g={g}" for f, g in zip(EQ_BANDS, gains) if g]
    if parts and (preamp > 0 or any(g > 0 for g in gains)):
        parts.append("alimiter=limit=0.95" + (":level=false" if limiter_level else ""))
    return f"lavfi=[{','.join(parts)}]" if parts else ""


class _MpvMeta:
    """Ahmt QMediaMetaData.stringValue() für mpv-Metadaten nach (z. B. Streamtitel)."""

    def __init__(self, d):
        self.d = {str(k).lower(): v for k, v in (d or {}).items()}

    def stringValue(self, key):
        if key == QMediaMetaData.Key.Title:
            return str(self.d.get("icy-title") or self.d.get("title") or "")
        if key == QMediaMetaData.Key.Description:
            return str(self.d.get("icy-description") or "")
        return ""

    def value(self, key):
        return self.stringValue(key) or None


class MpvBackend(QObject):
    """mpv (libmpv) mit derselben Schnittstelle wie QMediaPlayer, soweit NeoNote sie nutzt."""
    positionChanged = Signal(int)
    durationChanged = Signal(int)
    playbackStateChanged = Signal(object)
    mediaStatusChanged = Signal(object)
    errorOccurred = Signal(object, str)
    hasVideoChanged = Signal(bool)
    metaDataChanged = Signal()
    tracksChanged = Signal()
    advanced = Signal()
    _ev = Signal(str, object)

    def __init__(self, parent):
        super().__init__(parent)
        import mpv
        self._mpv = mpv
        opts = dict(vid="no", idle="yes", load_scripts="no", ytdl="no", gapless_audio="yes",
                    prefetch_playlist="yes", audio_client_name=APP_NAME, input_default_bindings=False,
                    input_vo_keyboard=False, osc=False, replaygain="no", volume=100)
        if os.environ.get("NEONOTE_AO"):
            opts["ao"] = os.environ["NEONOTE_AO"]
            if os.environ.get("NEONOTE_PCM"):
                opts["ao_pcm_file"] = os.environ["NEONOTE_PCM"]
                opts["audio_format"] = "s16"
        self.m = mpv.MPV(**opts)
        self._state = QMediaPlayer.StoppedState
        self._status = QMediaPlayer.NoMedia
        self._pos = self._dur = 0
        self._last_pos_emit = -10000
        self._meta = {}
        self._src = ""
        self._started = False
        self._explicit = False
        self._next = None
        self._paused = True
        self._idle = True
        self._limiter_level = True
        self._vis_ok = True
        self._ev.connect(self._on_ev)
        for prop, tag in (("time-pos", "pos"), ("duration", "dur"), ("pause", "pause"),
                          ("idle-active", "idle"), ("metadata", "meta")):
            self.m.observe_property(prop, lambda _n, v, tag=tag: self._ev.emit(tag, v))
        self.m.register_event_callback(self._mpv_event)

    # ── mpv-Thread → Hauptthread ──────────────────────────────────────────
    def _mpv_event(self, e):
        eid = e.event_id.value
        E = self._mpv.MpvEventID
        if eid == E.FILE_LOADED:
            self._ev.emit("loaded", None)
        elif eid == E.END_FILE:
            d = getattr(e, "data", None)
            self._ev.emit("end", (getattr(d, "reason", -1), getattr(d, "error", 0)))

    def _on_ev(self, tag, v):
        if tag == "pos":
            if v is None:
                return
            ms = int(v * 1000)
            self._pos = ms
            if abs(ms - self._last_pos_emit) >= 100 or ms < self._last_pos_emit:
                self._last_pos_emit = ms
                self.positionChanged.emit(ms)
        elif tag == "dur":
            self._dur = int((v or 0) * 1000)
            self.durationChanged.emit(self._dur)
        elif tag == "pause":
            self._paused = bool(v); self._update_state()
        elif tag == "idle":
            self._idle = bool(v); self._update_state()
        elif tag == "meta":
            self._meta = v or {}
            self.metaDataChanged.emit()
        elif tag == "loaded":
            if self._explicit:
                self._explicit = False
            else:                                   # lückenloser Übergang zum vorgeladenen Titel
                self._next = None
                try:
                    self.m.command("playlist-remove", 0)
                except Exception:
                    pass
                self.advanced.emit()
            self._set_status(QMediaPlayer.LoadedMedia)
        elif tag == "end":
            reason, err = v
            EF = self._mpv.MpvEventEndFile
            if reason == EF.ERROR:
                self.errorOccurred.emit(None, tr_("Datei konnte nicht abgespielt werden"))
                if not self._next:
                    self._set_status(QMediaPlayer.EndOfMedia)
            elif reason == EF.EOF and not self._next:
                self._set_status(QMediaPlayer.EndOfMedia)

    def _set_status(self, st):
        self._status = st
        self.mediaStatusChanged.emit(st)

    def _update_state(self):
        if self._idle or not self._started:
            st = QMediaPlayer.StoppedState
        elif self._paused:
            st = QMediaPlayer.PausedState
        else:
            st = QMediaPlayer.PlayingState
        if st != self._state:
            self._state = st
            self.playbackStateChanged.emit(st)

    # ── QMediaPlayer-Schnittstelle ────────────────────────────────────────
    def setSource(self, url):
        src = url.toLocalFile() if url.isLocalFile() else url.toString()
        self._next = None
        self._started = False
        self._pos = 0; self._dur = 0; self._meta = {}
        if not src:
            self.stop(); return
        self._src = src
        self._explicit = True
        self.m.pause = True
        try:
            self.m.command("playlist-clear")
        except Exception:
            pass
        self.m.loadfile(src, "replace")
        self._set_status(QMediaPlayer.LoadingMedia)
        self._update_state()
        self.positionChanged.emit(0)

    def play(self):
        if self._idle and self._src:
            self._explicit = True
            self.m.loadfile(self._src, "replace")
        self._started = True
        self.m.pause = False
        self._paused = False
        self._update_state()

    def pause(self):
        self.m.pause = True

    def stop(self):
        self._started = False
        self._next = None
        try:
            self.m.command("stop")
        except Exception:
            pass
        self._pos = 0
        self._update_state()
        self.positionChanged.emit(0)

    def setPosition(self, ms):
        try:
            self.m.command("seek", max(0, ms) / 1000.0, "absolute+exact")
        except Exception:
            return
        self._pos = int(ms)
        self.positionChanged.emit(int(ms))

    def position(self):
        return self._pos

    def duration(self):
        return self._dur

    def playbackState(self):
        return self._state

    def mediaStatus(self):
        return self._status

    def metaData(self):
        return _MpvMeta(self._meta)

    def hasVideo(self):
        return False

    def audioTracks(self):
        return []

    def subtitleTracks(self):
        return []

    def activeAudioTrack(self):
        return 0

    def activeSubtitleTrack(self):
        return -1

    def setActiveAudioTrack(self, _i):
        pass

    def setActiveSubtitleTrack(self, _i):
        pass

    # ── mpv-spezifisch ────────────────────────────────────────────────────
    def set_next(self, src):
        """Nächsten Titel vorladen (lückenlose Wiedergabe)."""
        if (src or None) == self._next:
            return
        try:
            self.m.command("playlist-clear")
            if src:
                self.m.loadfile(src, "append")
        except Exception:
            src = None
        self._next = src or None

    def set_volume(self, gain, muted):
        self.m.volume = 100.0 * max(0.0, gain) ** (1 / 3)
        self.m.mute = bool(muted)

    VIS_AF = "@nnvis:lavfi=[astats=metadata=1:reset=1:measure_perchannel=none:measure_overall=RMS_level+Peak_level]"

    def level(self):
        """Aktueller Pegel 0…1 (für die Waveform unten links) oder None."""
        if not self._vis_ok:
            return None
        try:
            md = self.m._get_property("af-metadata/nnvis") or {}
            db = float(md.get("lavfi.astats.Overall.RMS_level", "-inf"))
            pk = float(md.get("lavfi.astats.Overall.Peak_level", "-inf"))
        except Exception:
            return None
        db = max(db, pk - 6)
        return 0.0 if db != db or db < -60 else max(0.0, min(1.0, (db + 48) / 44))

    def set_filter(self, enabled, gains, preamp):
        self._filter_args = (enabled, gains, preamp)
        af = eq_filter(enabled, gains, preamp, self._limiter_level)
        if self._vis_ok:
            af = f"{af},{self.VIS_AF}" if af else self.VIS_AF
        try:
            self.m.command("af", "set", af) if af else self.m.command("af", "clr", "")
        except Exception:
            if self._limiter_level:                # ältere FFmpeg-Versionen kennen „level“ nicht
                self._limiter_level = False
                self.set_filter(enabled, gains, preamp)
            elif self._vis_ok:                     # astats nicht verfügbar → ohne Waveform weiter
                self._vis_ok = False
                self.set_filter(enabled, gains, preamp)

    def set_replaygain(self, mode):
        try:
            self.m.replaygain = mode if mode in ("track", "album") else "no"
        except Exception:
            pass

    def shutdown(self):
        try:
            self.m.terminate()
        except Exception:
            pass


class EngineAudio:
    """Lautstärke für beide Wiedergabewege."""

    def __init__(self, engine):
        self.e, self.gain, self.muted = engine, 1.0, False

    def setVolume(self, g):
        self.gain = g
        self.e.qt_audio.setVolume(g)
        if self.e.mp:
            self.e.mp.set_volume(g, self.muted)

    def setMuted(self, m):
        self.muted = m
        self.e.qt_audio.setMuted(m)
        if self.e.mp:
            self.e.mp.set_volume(self.gain, m)

    def isMuted(self):
        return self.muted


class Engine(QObject):
    """Weiche: Musik und Radio über mpv (falls vorhanden), Videos über Qt Multimedia."""
    positionChanged = Signal(int)
    durationChanged = Signal(int)
    playbackStateChanged = Signal(object)
    mediaStatusChanged = Signal(object)
    errorOccurred = Signal(object, str)
    hasVideoChanged = Signal(bool)
    metaDataChanged = Signal()
    tracksChanged = Signal()
    advanced = Signal()
    SIGNALS = ("positionChanged", "durationChanged", "playbackStateChanged", "mediaStatusChanged",
               "errorOccurred", "hasVideoChanged", "metaDataChanged", "tracksChanged")

    def __init__(self, parent, use_mpv=True):
        super().__init__(parent)
        self.qt = QMediaPlayer(self)
        self.qt_audio = QAudioOutput(self)
        self.qt.setAudioOutput(self.qt_audio)
        self.mp, self.mpv_error = None, ""
        if use_mpv:
            try:
                self.mp = MpvBackend(self)
            except Exception as e:
                self.mp, self.mpv_error = None, str(e)
        self.b = self.qt
        for be in (self.qt, self.mp):
            if be is None:
                continue
            for name in self.SIGNALS:
                getattr(be, name).connect(lambda *a, be=be, name=name: be is self.b and getattr(self, name).emit(*a))
        if self.mp:
            self.mp.advanced.connect(self.advanced)
        self.audio = EngineAudio(self)

    def uses_mpv_for(self, src):
        if not self.mp:
            return False
        if src.startswith(("http://", "https://")):
            return True
        return Path(src).suffix.lower() not in VIDEO_EXT

    def on_mpv(self):
        return self.mp is not None and self.b is self.mp

    def setSource(self, url):
        src = url.toLocalFile() if url.isLocalFile() else url.toString()
        target = self.mp if self.uses_mpv_for(src) else self.qt
        if target is not self.b:
            self.b.stop()
            if self.b is self.qt:
                self.qt.setSource(QUrl())
                self.hasVideoChanged.emit(False)
            elif self.mp:
                self.mp.set_next(None)
            self.b = target
        target.setSource(url)

    def set_next(self, src):
        if self.on_mpv():
            self.mp.set_next(src)

    def level(self):
        """Pegel für die Waveform – nur über mpv messbar, sonst None."""
        return self.mp.level() if self.on_mpv() else None

    def setVideoSink(self, sink):
        self.qt.setVideoSink(sink)

    def setAudioOutput(self, _a):
        pass

    def __getattr__(self, name):
        # play, pause, stop, position, duration, setPosition, playbackState, mediaStatus, metaData,
        # audioTracks, subtitleTracks, activeAudioTrack, setActiveAudioTrack, … → aktiver Wiedergabeweg
        if name in ("qt", "mp", "b"):
            raise AttributeError(name)
        return getattr(self.b, name)

    def shutdown(self):
        if self.mp:
            self.mp.shutdown()


# ════════════════════════════════════════════════════════════════════════════
#  Windows: libmpv einmalig herunterladen (für Gapless und Equalizer)
# ════════════════════════════════════════════════════════════════════════════
MPV_REPO_API = "https://api.github.com/repos/shinchiro/mpv-winbuild-cmake/releases/latest"


class MpvDownloader(QThread):
    progress = Signal(int, int)          # empfangen, gesamt
    status = Signal(str)
    done = Signal(bool, str)

    def run(self):
        import urllib.request
        try:
            self.status.emit(tr_("Suche die aktuelle mpv-Version …"))
            req = urllib.request.Request(MPV_REPO_API, headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}",
                                                                "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                rel = json.loads(r.read().decode("utf-8"))
            assets = [a for a in rel.get("assets", [])
                      if re.match(r"^mpv-dev-x86_64-(?:gcc-|clang-)?\d{8}-git-[0-9a-f]+\.7z$", a.get("name", ""))]
            if not assets:
                raise RuntimeError(tr_("In der aktuellen mpv-Version wurde keine passende Datei gefunden."))
            a = assets[0]
            self.status.emit(tr_("Lade {0} …").format(a['name']))
            MPV_DIR.mkdir(parents=True, exist_ok=True)
            tmp = MPV_DIR / "download.7z"
            req = urllib.request.Request(a["browser_download_url"], headers={"User-Agent": APP_NAME})
            with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as out:
                total = int(r.headers.get("Content-Length") or a.get("size") or 0)
                got = 0
                while True:
                    if self.isInterruptionRequested():
                        raise RuntimeError(tr_("Abgebrochen."))
                    chunk = r.read(256 * 1024)
                    if not chunk:
                        break
                    out.write(chunk); got += len(chunk)
                    self.progress.emit(got, total)
            self.status.emit(tr_("Entpacke …"))
            import shutil
            import tempfile
            work = Path(tempfile.mkdtemp(prefix="neonote-mpv-"))
            try:
                # Die Archive nutzen den BCJ2-Filter – den kann das in Windows eingebaute tar (libarchive)
                tar = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "tar.exe"
                ok = False
                if tar.exists():
                    r = subprocess.run([str(tar), "-xf", str(tmp), "-C", str(work)], capture_output=True,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                    ok = r.returncode == 0
                if not ok:
                    import py7zr
                    with py7zr.SevenZipFile(tmp, "r") as z:
                        z.extractall(path=work)
                found = [p for p in work.rglob("*.dll") if p.name.lower() in ("libmpv-2.dll", "mpv-2.dll")]
                if not found:
                    raise RuntimeError(tr_("Im Archiv fehlt libmpv-2.dll."))
                shutil.copy2(found[0], MPV_DIR / found[0].name)
            finally:
                shutil.rmtree(work, ignore_errors=True)
            tmp.unlink(missing_ok=True)
            self.done.emit(True, "")
        except Exception as e:
            self.done.emit(False, str(e))


class MpvDownloadDialog(QDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle(tr_("mpv herunterladen"))
        self.setMinimumWidth(460)
        lay = QVBoxLayout(self); lay.setContentsMargins(18, 16, 18, 14); lay.setSpacing(10)
        info = QLabel(tr_("Für lückenlose Wiedergabe (Gapless), den Equalizer und die Waveform nutzt NeoNote "
                      "<b>mpv</b>. NeoNote lädt die Bibliothek <code>libmpv-2.dll</code> (ca. 30 MB) einmalig "
                      "von GitHub (Projekt shinchiro/mpv-winbuild-cmake) herunter und legt sie in deinem "
                      "Benutzerordner ab. Danach startet der Player neu."))
        info.setWordWrap(True); info.setTextFormat(Qt.RichText)
        lay.addWidget(info)
        self.lbl = QLabel(""); self.lbl.setObjectName("hint")
        self.bar = QProgressBar(); self.bar.setRange(0, 100); self.bar.setValue(0); self.bar.hide()
        lay.addWidget(self.lbl); lay.addWidget(self.bar)
        self.bb = QDialogButtonBox()
        self.go = self.bb.addButton("Herunterladen", QDialogButtonBox.AcceptRole)
        self.cancel = self.bb.addButton(tr_("Abbrechen"), QDialogButtonBox.RejectRole)
        self.go.clicked.connect(self.start); self.cancel.clicked.connect(self.reject)
        lay.addWidget(self.bb)
        self.th = None

    def start(self):
        self.go.setEnabled(False); self.bar.show(); self.bar.setRange(0, 0)
        self.th = MpvDownloader(self)
        self.th.status.connect(self.lbl.setText)
        self.th.progress.connect(self._prog)
        self.th.done.connect(self._done)
        self.th.start()

    def _prog(self, got, total):
        if total:
            self.bar.setRange(0, 100); self.bar.setValue(int(got * 100 / total))
        self.lbl.setText(tr_("Lade … {0:.1f} MB").format(got / 1048576) + (tr_(" von {0:.1f} MB").format(total / 1048576) if total else ""))

    def _done(self, ok, err):
        self.th.wait(); self.th = None
        if not ok:
            self.bar.hide(); self.go.setEnabled(True); self.go.setText(tr_("Erneut versuchen"))
            self.lbl.setText(tr_("Das hat nicht geklappt: {0}").format(err))
            return
        self.bar.setRange(0, 100); self.bar.setValue(100)
        self.lbl.setText(tr_("Fertig. NeoNote startet jetzt neu."))
        self.win.settings.setValue("audio/mpv", True)
        QTimer.singleShot(700, self.win.restart_app)
        self.accept()

    def reject(self):
        if self.th:
            self.th.requestInterruption(); self.th.wait(3000)
        super().reject()





# ════════════════════════════════════════════════════════════════════════════
#  Jellyfin: eigener Musikserver (z. B. auf dem Raspberry Pi) als zweite Bibliothek
# ════════════════════════════════════════════════════════════════════════════
class JellyfinError(OnlineError):
    pass


class Jellyfin:
    """Schlanker Jellyfin-Client (nur das, was NeoNote braucht). Läuft in Hintergrund-Threads."""
    QUALITIES = [("orig", tr_("Original (verlustfrei, für zu Hause)")), ("320", tr_("320 kbit/s")),
                 ("192", tr_("192 kbit/s (unterwegs)")), ("128", tr_("128 kbit/s (sparsam)"))]

    def __init__(self, url="", token="", user_id="", device_id="", quality="orig"):
        self.url = (url or "").rstrip("/")
        self.token, self.user_id, self.device_id, self.quality = token, user_id, device_id, quality

    # ── HTTP ──
    def _auth_header(self):
        import platform
        dev = re.sub(r'[^A-Za-z0-9 ._-]', "", platform.node() or "PC")[:40] or "PC"
        h = (f'MediaBrowser Client="{APP_NAME}", Device="{dev}", DeviceId="{self.device_id}", '
             f'Version="{APP_VERSION}"')
        if self.token:
            h += f', Token="{self.token}"'
        return h

    def _req(self, method, path, body=None, params=None, timeout=30, raw=False):
        import urllib.error
        import urllib.parse
        import urllib.request
        if not self.url.startswith(("http://", "https://")):
            raise JellyfinError(tr_("Die Adresse muss mit http:// oder https:// beginnen."))
        url = self.url + path
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", self._auth_header())
        req.add_header("X-Emby-Authorization", self._auth_header())
        if self.token:
            req.add_header("X-Emby-Token", self.token)
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                payload = r.read()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise JellyfinError(tr_("Anmeldung abgelehnt – Benutzer oder Passwort stimmen nicht.")) from None
            raise JellyfinError(tr_("Der Server meldet Fehler {0}.").format(e.code)) from None
        except urllib.error.URLError as e:
            raise JellyfinError(tr_("Server nicht erreichbar ({0}).").format(getattr(e, 'reason', e))) from None
        except OSError as e:
            raise JellyfinError(tr_("Server nicht erreichbar ({0}).").format(e)) from None
        if raw:
            return payload
        try:
            return json.loads(payload.decode("utf-8")) if payload else {}
        except ValueError:
            raise JellyfinError(tr_("Das ist kein Jellyfin-Server (unerwartete Antwort).")) from None

    def _try(self, *calls):
        """Erst den neuen Weg (Jellyfin 10.9+), sonst den älteren probieren."""
        err = None
        for method, path, params in calls:
            try:
                return self._req(method, path, params=params)
            except JellyfinError as e:
                err = e
        raise err

    # ── Anmeldung ──
    def login(self, user, password):
        info = self._req("GET", "/System/Info/Public", timeout=10)
        r = self._req("POST", "/Users/AuthenticateByName", body={"Username": user, "Pw": password})
        self.token = r.get("AccessToken", "")
        self.user_id = (r.get("User") or {}).get("Id", "")
        if not self.token or not self.user_id:
            raise JellyfinError(tr_("Anmeldung fehlgeschlagen."))
        return {"server": info.get("ServerName") or "Jellyfin", "version": info.get("Version", ""),
                "user": (r.get("User") or {}).get("Name", user)}

    def logout(self):
        try:
            self._req("POST", "/Sessions/Logout", timeout=5)
        except JellyfinError:
            pass

    # ── Bibliothek ──
    def _items(self, params):
        params = dict(params); params.setdefault("Recursive", "true")
        out, start = [], 0
        while True:
            p = dict(params, StartIndex=start, Limit=2000)
            try:
                r = self._req("GET", "/Items", params=dict(p, userId=self.user_id), timeout=60)
            except JellyfinError:
                r = self._req("GET", f"/Users/{self.user_id}/Items", params=p, timeout=60)
            items = r.get("Items", [])
            out += items
            start += len(items)
            if not items or start >= r.get("TotalRecordCount", start):
                break
        return out

    def fetch_tracks(self):
        items = self._items({"IncludeItemTypes": "Audio", "Fields": "Genres,DateCreated,MediaSources,ProductionYear,Path",
                             "EnableUserData": "true"})
        return [self.to_track(it) for it in items if it.get("Id")]

    def fetch_playlists(self):
        pls = []
        for p in self._items({"IncludeItemTypes": "Playlist"}):
            if (p.get("MediaType") or "Audio") not in ("Audio", "Unknown"):
                continue
            try:
                r = self._req("GET", f"/Playlists/{p['Id']}/Items", params={"userId": self.user_id, "Fields": "MediaSources"})
            except JellyfinError:
                continue
            ids = [it["Id"] for it in r.get("Items", []) if it.get("Type") == "Audio"]
            if ids:
                pls.append({"id": p["Id"], "name": p.get("Name", "Wiedergabeliste"), "items": ids})
        return pls

    def to_track(self, it):
        ms = (it.get("MediaSources") or [{}])[0]
        artists = it.get("Artists") or ([it["AlbumArtist"]] if it.get("AlbumArtist") else [])
        artist = ", ".join(artists) or "Unbekannter Interpret"
        aa = it.get("AlbumArtist") or artist
        album_id = it.get("AlbumId") or ""
        ud = it.get("UserData") or {}
        try:
            added = int(datetime_ts(it.get("DateCreated")))
        except Exception:
            added = 0
        return {
            "path": f"jf:{it['Id']}", "remote": True, "jf_id": it["Id"],
            "title": it.get("Name") or "Unbekannter Titel", "artist": artist, "albumartist": aa,
            "album": it.get("Album") or "Unbekanntes Album", "composer": "",
            "genre": (it.get("Genres") or [""])[0], "year": str(it.get("ProductionYear") or ""),
            "track": int(it.get("IndexNumber") or 0), "disc": int(it.get("ParentIndexNumber") or 1),
            "length": (it.get("RunTimeTicks") or 0) / 1e7,
            "bitrate": int((ms.get("Bitrate") or 0) / 1000), "size": int(ms.get("Size") or 0),
            "container": (ms.get("Container") or it.get("Container") or "").split(",")[0],
            "cover": f"jf-{album_id}" if album_id else f"jf-x-{album_key(aa, it.get('Album') or '')}",
            "jf_album": album_id, "jf_fav": bool(ud.get("IsFavorite")), "jf_plays": int(ud.get("PlayCount") or 0),
            "mtime": added,
        }

    # ── Wiedergabe ──
    def stream_url(self, item_id):
        import urllib.parse
        q = {"api_key": self.token, "DeviceId": self.device_id}
        if self.quality == "orig":
            q["static"] = "true"
            return f"{self.url}/Audio/{item_id}/stream?{urllib.parse.urlencode(q)}"
        q["audioBitRate"] = int(self.quality) * 1000
        q["audioCodec"] = "mp3"
        return f"{self.url}/Audio/{item_id}/stream.mp3?{urllib.parse.urlencode(q)}"

    def cover(self, album_id, size=600):
        return self._req("GET", f"/Items/{album_id}/Images/Primary", params={"maxHeight": size, "quality": 90},
                         raw=True, timeout=20)

    def download(self, item_id, dest, progress=None):
        import urllib.request
        url = f"{self.url}/Items/{item_id}/Download?api_key={self.token}"
        req = urllib.request.Request(url); req.add_header("Authorization", self._auth_header())
        try:
            r = urllib.request.urlopen(req, timeout=60)
        except Exception:
            req = urllib.request.Request(self.stream_url_orig(item_id)); r = urllib.request.urlopen(req, timeout=60)
        tmp = Path(str(dest) + ".part")
        with r, open(tmp, "wb") as f:
            while True:
                b = r.read(256 * 1024)
                if not b:
                    break
                f.write(b)
        tmp.replace(dest)

    def stream_url_orig(self, item_id):
        return f"{self.url}/Audio/{item_id}/stream?static=true&api_key={self.token}"

    def mark_played(self, item_id):
        self._try(("POST", f"/UserPlayedItems/{item_id}", {"userId": self.user_id}),
                  ("POST", f"/Users/{self.user_id}/PlayedItems/{item_id}", None))

    def set_favorite(self, item_id, on):
        m = "POST" if on else "DELETE"
        self._try((m, f"/UserFavoriteItems/{item_id}", {"userId": self.user_id}),
                  (m, f"/Users/{self.user_id}/FavoriteItems/{item_id}", None))


def datetime_ts(s):
    from datetime import datetime
    if not s:
        return 0
    s = s.rstrip("Z").split(".")[0]
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").timestamp()


class JfCoverFetcher(QThread):
    """Lädt Cover vom Jellyfin-Server nach, sobald eine Ansicht sie braucht."""
    loaded = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.client = None
        self.q = queue.Queue()
        self.asked = set()

    def want(self, key):
        if key in self.asked or not self.client or not key.startswith("jf-") or key.startswith("jf-x-"):
            return
        self.asked.add(key)
        self.q.put(key)
        if not self.isRunning():
            self.start()

    def run(self):
        while True:
            try:
                key = self.q.get(timeout=3)
            except queue.Empty:
                return
            try:
                data = self.client.cover(key[3:])
                img = QImage.fromData(data)
                if not img.isNull():
                    COVER_DIR.mkdir(parents=True, exist_ok=True)
                    img.save(str(cover_path(key)), "JPG", 90)
                    self.loaded.emit(key)
            except Exception:
                pass


JF_FETCHER = None     # wird vom Hauptfenster gesetzt; CoverCache fragt hier fehlende Jellyfin-Cover an

# ════════════════════════════════════════════════════════════════════════════
#  Bibliothek prüfen: doppelte Titel, fehlende Cover, lückenhafte Tags, fehlende Dateien
# ════════════════════════════════════════════════════════════════════════════
LOSSLESS = {".flac", ".wav", ".ape", ".wv", ".aiff", ".aif", ".dsf", ".dff", ".tta", ".alac"}


def _norm(txt):
    t = (txt or "").lower()
    t = re.sub(r"\s*[\(\[][^)\]]*(remaster|version|edit|mono|stereo|live)[^)\]]*[\)\]]", "", t)
    return re.sub(r"[^0-9a-zäöüß]+", "", t)


def quality_score(t, stats):
    ext = Path(t["path"]).suffix.lower()
    br = int(t.get("bitrate") or 0)
    return ((1 if ext in LOSSLESS else 0), br, stats.rating(t["path"]), stats.plays(t["path"]))


def quality_text(t):
    ext = Path(t["path"]).suffix.lower().lstrip(".").upper()
    br = t.get("bitrate")
    return f"{ext} · {br} kbit/s" if br else ext


class CheckWorker(QThread):
    done = Signal(object)

    def __init__(self, tracks, albums, stats, playlists):
        super().__init__()
        self.tracks, self.albums, self.stats, self.playlists = tracks, albums, stats, playlists

    def run(self):
        res = {"dups": [], "nocover": [], "tags": [], "missing": [], "count": len(self.tracks)}
        # doppelte Titel: gleicher Titel und Interpret (bereinigt), Länge ± 3 s
        groups = defaultdict(list)
        for t in self.tracks:
            if t.get("stream") or t.get("remote"):
                continue
            groups[(_norm(t["title"]), _norm(t["artist"]))].append(t)
        for (nt, _na), tl in groups.items():
            if len(tl) < 2 or not nt:
                continue
            tl = sorted(tl, key=lambda t: t.get("length") or 0)
            cluster = [tl[0]]
            for t in tl[1:]:
                if abs((t.get("length") or 0) - (cluster[-1].get("length") or 0)) <= 3:
                    cluster.append(t)
                else:
                    if len(cluster) > 1:
                        res["dups"].append(cluster)
                    cluster = [t]
            if len(cluster) > 1:
                res["dups"].append(cluster)
        for c in res["dups"]:
            c.sort(key=lambda t: quality_score(t, self.stats), reverse=True)
        res["dups"].sort(key=lambda c: (sort_name(c[0]["artist"]), c[0]["title"].lower()))
        # Alben ohne Cover
        for a in self.albums.values():
            if a["tracks"] and not a["tracks"][0].get("remote") and not (cover_path(a['key'])).exists():
                res["nocover"].append(a)
        # lückenhafte Tags
        for t in self.tracks:
            if t.get("stream") or t.get("remote"):
                continue
            miss = []
            if not t.get("artist") or t["artist"].startswith("Unbekannt"):
                miss.append(tr_("Interpret"))
            if not t.get("album") or t["album"].startswith("Unbekannt"):
                miss.append(tr_("Album"))
            if not t.get("year"):
                miss.append(tr_("Jahr"))
            if not t.get("track"):
                miss.append(tr_("Nr."))
            if not t.get("genre"):
                miss.append(tr_("Genre"))
            if miss:
                res["tags"].append((t, miss))
        # fehlende Dateien: Bewertungen/Zähler und Wiedergabelisten, deren Datei nicht mehr existiert
        known = {t["path"] for t in self.tracks}
        by_name = defaultdict(list)
        for t in self.tracks:
            by_name[Path(t["path"]).name.lower()].append(t["path"])
        refs = defaultdict(set)
        for pth in list(self.stats.data.keys()):
            refs[pth].add(tr_("Bewertung/Zähler"))
        for name, paths in self.playlists.items():
            for pth in paths:
                refs[pth].add(tr_("Liste „{0}“").format(name))
        for pth, where in refs.items():
            if pth in known or pth.startswith(("http://", "https://", "jf:")) or os.path.exists(pth):
                continue
            cands = [c for c in by_name.get(Path(pth).name.lower(), []) if c not in self.stats.data]
            res["missing"].append((pth, sorted(where), cands[0] if len(cands) == 1 else None))
        self.done.emit(res)


class CheckPage(QWidget):
    """Ansicht „Bibliothek prüfen“."""

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.res = None
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        from PySide6.QtWidgets import QScrollArea
        sa = QScrollArea(); sa.setWidgetResizable(True); sa.setFrameShape(QFrame.NoFrame)
        outer.addWidget(sa)
        body = QWidget(); sa.setWidget(body)
        self.sa = sa
        lay = QVBoxLayout(body); lay.setContentsMargins(22, 16, 22, 22); lay.setSpacing(10)
        head = QHBoxLayout()
        t = QLabel(tr_("Bibliothek prüfen")); t.setObjectName("checkTitle")
        self.sub = QLabel(""); self.sub.setObjectName("dim")
        self.btn_run = QPushButton(tr_("Neu prüfen")); self.btn_run.clicked.connect(self.run)
        head.addWidget(t); head.addSpacing(10); head.addWidget(self.sub); head.addStretch(); head.addWidget(self.btn_run)
        lay.addLayout(head)
        cards = QHBoxLayout(); cards.setSpacing(10)
        self.cards = {}
        for key, label in (("dups", tr_("Doppelte Titel")), ("nocover", tr_("Alben ohne Cover")),
                           ("tags", tr_("Lückenhafte Tags")), ("missing", tr_("Fehlende Dateien"))):
            b = QToolButton(); b.setObjectName("checkCard"); b.setToolButtonStyle(Qt.ToolButtonTextOnly)
            b.setSizePolicy(b.sizePolicy().horizontalPolicy().Expanding, b.sizePolicy().verticalPolicy())
            b.setText(f"{label}\n–"); b.setMinimumHeight(64)
            b.clicked.connect(lambda _=False, k=key: self._jump(k))
            self.cards[key] = (b, label)
            cards.addWidget(b, 1)
        lay.addLayout(cards)
        # doppelte Titel
        self.h_dups = self._section(lay, tr_("Doppelte Titel"),
                                    tr_("Die beste Fassung ist vorausgewählt (verlustfrei, höhere Bitrate, mehr Sterne, "
                                    "öfter gespielt). Häkchen bei allen, die du behalten willst."))
        self.dups = QTreeWidget(); self.dups.setColumnCount(4)
        self.dups.setHeaderLabels([tr_("Behalten"), tr_("Qualität"), tr_("Bewertung · gespielt"), tr_("Datei")])
        self.dups.setRootIsDecorated(False); self.dups.setUniformRowHeights(True)
        self.dups.setMinimumHeight(220)
        self.box_dups = self._box(lay, self.dups)
        row = QHBoxLayout()
        b1 = QPushButton(tr_("Nicht behaltene ausblenden")); b1.clicked.connect(lambda: self._dups_apply(False))
        b2 = QPushButton(tr_("Nicht behaltene in den Papierkorb")); b2.clicked.connect(lambda: self._dups_apply(True))
        row.addWidget(b1); row.addWidget(b2); row.addStretch(); self.box_dups.layout().addLayout(row)
        # Alben ohne Cover
        self.h_nocover = self._section(lay, tr_("Alben ohne Cover"),
                                       tr_("Doppelklick öffnet die Online-Suche für ein Album. Du kannst auch ein Bild "
                                       "auf das Album in der Bibliothek ziehen."))
        self.nocover = QListWidget(); self.nocover.setViewMode(QListView.IconMode)
        self.nocover.setIconSize(QSize(96, 96)); self.nocover.setGridSize(QSize(124, 136))
        self.nocover.setResizeMode(QListView.Adjust); self.nocover.setMovement(QListView.Static)
        self.nocover.setWordWrap(True); self.nocover.setMinimumHeight(160)
        self.nocover.itemDoubleClicked.connect(lambda it: self.win.lookup_album(it.data(Qt.UserRole)))
        self.box_nocover = self._box(lay, self.nocover)
        row = QHBoxLayout()
        b3 = QPushButton(tr_("Alle online suchen")); b3.clicked.connect(self._covers_online)
        row.addWidget(b3); row.addStretch(); self.box_nocover.layout().addLayout(row)
        # lückenhafte Tags
        self.h_tags = self._section(lay, tr_("Lückenhafte Tags"),
                                    tr_("Doppelklick zeigt den Titel in seinem Album – dort kannst du die Felder direkt "
                                    "bearbeiten (F2) oder per Rechtsklick online ergänzen."))
        self.tags = QTreeWidget(); self.tags.setColumnCount(4)
        self.tags.setHeaderLabels([tr_("Titel"), tr_("Interpret"), tr_("Es fehlt"), tr_("Datei")])
        self.tags.setRootIsDecorated(False); self.tags.setUniformRowHeights(True); self.tags.setMinimumHeight(200)
        self.tags.itemDoubleClicked.connect(self._tag_open)
        self.box_tags = self._box(lay, self.tags)
        row = QHBoxLayout()
        b4 = QPushButton(tr_("Fehlendes online ergänzen")); b4.clicked.connect(self._tags_online)
        row.addWidget(b4); row.addStretch(); self.box_tags.layout().addLayout(row)
        # fehlende Dateien
        self.h_missing = self._section(lay, tr_("Fehlende Dateien"),
                                       tr_("Dateien, auf die Bewertungen, Zähler oder Wiedergabelisten verweisen, die es aber "
                                       "nicht mehr gibt. Wurde eine verschoben, findet NeoNote sie oft wieder."))
        self.missing = QTreeWidget(); self.missing.setColumnCount(3)
        self.missing.setHeaderLabels([tr_("Datei"), tr_("Benutzt in"), tr_("Neu gefunden")])
        self.missing.setRootIsDecorated(False); self.missing.setUniformRowHeights(True)
        self.missing.setMinimumHeight(160)
        self.box_missing = self._box(lay, self.missing)
        row = QHBoxLayout()
        b5 = QPushButton(tr_("Gefundene neu zuordnen")); b5.clicked.connect(self._missing_relink)
        b6 = QPushButton(tr_("Nicht gefundene vergessen")); b6.clicked.connect(self._missing_forget)
        row.addWidget(b5); row.addWidget(b6); row.addStretch(); self.box_missing.layout().addLayout(row)
        lay.addStretch()
        for tv in (self.dups, self.tags, self.missing):
            tv.header().setStretchLastSection(True)
        self.th = None

    def _section(self, lay, title, hint):
        lay.addSpacing(10)
        h = QLabel(f"<b>{title}</b>"); lay.addWidget(h)
        d = QLabel(hint); d.setObjectName("hint"); d.setWordWrap(True); lay.addWidget(d)
        ok = QLabel(tr_("✓  Nichts gefunden – alles in Ordnung.")); ok.setObjectName("checkOk"); ok.hide(); lay.addWidget(ok)
        h._hint, h._ok = d, ok
        return h

    def _box(self, lay, widget):
        box = QWidget(); bl = QVBoxLayout(box); bl.setContentsMargins(0, 0, 0, 0); bl.setSpacing(8)
        bl.addWidget(widget); lay.addWidget(box)
        return box

    def _set_empty(self, head, box, empty):
        box.setVisible(not empty); head._hint.setVisible(not empty); head._ok.setVisible(empty)

    def _jump(self, key):
        w = {"dups": self.h_dups, "nocover": self.h_nocover, "tags": self.h_tags, "missing": self.h_missing}[key]
        self.sa.verticalScrollBar().setValue(max(0, w.y() - 10))

    def run(self):
        if self.th:
            return
        w = self.win
        pls = {}
        for name in w.playlist_names():
            try:
                pls[name] = [p for p, _t in read_playlist_file(w._pl_path(name))]
            except Exception:
                pass
        self.sub.setText(tr_("Prüfe …")); self.btn_run.setEnabled(False)
        self.th = CheckWorker(list(w.local_lib.tracks), w.local_lib.albums, w.stats, pls)
        self.th.done.connect(self._show)
        self.th.start()

    def _show(self, res):
        self.th.wait(); self.th = None
        self.btn_run.setEnabled(True)
        self.res = res
        self.sub.setText(tr_("· {0} Titel geprüft").format(fmt_int(res['count'])))
        counts = {"dups": sum(len(c) - 1 for c in res["dups"]), "nocover": len(res["nocover"]),
                  "tags": len(res["tags"]), "missing": len(res["missing"])}
        for k, (b, label) in self.cards.items():
            b.setText(f"{label}\n{counts[k]}")
        for k, head, box in (("dups", self.h_dups, self.box_dups), ("nocover", self.h_nocover, self.box_nocover),
                             ("tags", self.h_tags, self.box_tags), ("missing", self.h_missing, self.box_missing)):
            self._set_empty(head, box, counts[k] == 0)
        st = self.win.stats
        self.dups.clear()
        for cluster in res["dups"]:
            head = QTreeWidgetItem([f"{cluster[0]['title']}  ·  {cluster[0]['artist']}  ·  "
                                    f"{fmt_time(cluster[0].get('length'))}", "", "", ""])
            f = head.font(0); f.setBold(True); head.setFont(0, f)
            head.setFlags(Qt.ItemIsEnabled); head.setFirstColumnSpanned(True)
            self.dups.addTopLevelItem(head); head.setFirstColumnSpanned(True)
            for i, t in enumerate(cluster):
                r, n = st.rating(t["path"]), st.plays(t["path"])
                it = QTreeWidgetItem(["", quality_text(t), f"{'★' * r or '–'} · {n}×", t["path"]])
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
                it.setCheckState(0, Qt.Checked if i == 0 else Qt.Unchecked)
                it.setData(0, Qt.UserRole, t)
                it.setToolTip(3, t["path"])
                self.dups.addTopLevelItem(it)
        self.dups.resizeColumnToContents(0); self.dups.resizeColumnToContents(1); self.dups.resizeColumnToContents(2)
        self.nocover.clear()
        ph = QIcon(CoverCache.placeholder(96))
        for a in res["nocover"]:
            it = QListWidgetItem(ph, f"{disp(a['title'])}\n{disp(a['artist'])}"); it.setData(Qt.UserRole, a)
            self.nocover.addItem(it)
        self.tags.clear()
        for t, miss in res["tags"][:2000]:
            it = QTreeWidgetItem([t["title"], t["artist"], ", ".join(miss), t["path"]])
            it.setData(0, Qt.UserRole, t); self.tags.addTopLevelItem(it)
        self.tags.resizeColumnToContents(2)
        self.missing.clear()
        for pth, where, found in res["missing"]:
            it = QTreeWidgetItem([pth, ", ".join(where), found or tr_("– nicht gefunden –")])
            it.setData(0, Qt.UserRole, (pth, found)); self.missing.addTopLevelItem(it)
        self.missing.resizeColumnToContents(1)
        for tv in (self.dups, self.tags, self.missing):          # so hoch wie nötig, höchstens 360 px
            n = tv.topLevelItemCount()
            tv.setFixedHeight(min(360, tv.header().sizeHint().height() + 6 + n * max(20, tv.sizeHintForRow(0))))

    def _dups_apply(self, trash):
        drop = []
        for i in range(self.dups.topLevelItemCount()):
            it = self.dups.topLevelItem(i)
            t = it.data(0, Qt.UserRole)
            if t and it.checkState(0) == Qt.Unchecked:
                drop.append(t)
        if not drop:
            self.win.flash(tr_("Alles ist zum Behalten markiert."))
            return
        if trash:
            if QMessageBox.question(self, tr_("In den Papierkorb"),
                                    tr_("{0} Dateien in den Papierkorb verschieben?\n\nBewertungen und Zähler werden auf die behaltene Fassung übertragen.").format(len(drop))) \
                    != QMessageBox.Yes:
                return
        self._merge_stats(drop)
        failed = 0
        for t in drop:
            self.win.local_lib.hidden.add(t["path"])
            if trash:
                from PySide6.QtCore import QFile
                if not QFile.moveToTrash(t["path"]):
                    failed += 1
        self.win.local_lib.save_hidden()
        self.win.local_lib.set_tracks(list(self.win.local_lib.tracks)); self.win.local_lib.save()
        self.win.stats.save()
        self.win.flash(tr_("{0} Doppelte entfernt").format(len(drop) - failed) + (tr_(", {0} nicht möglich").format(failed) if failed else ""))
        self.run()

    def _merge_stats(self, drop):
        """Zähler der entfernten Fassung auf die behaltene übertragen, bessere Bewertung übernehmen."""
        st = self.win.stats
        for cluster in (self.res or {}).get("dups", []):
            kept = [t for t in cluster if t not in drop]
            if not kept:
                continue
            k = kept[0]["path"]
            for t in cluster:
                if t in drop:
                    d = st.data.get(t["path"], {})
                    e = st.data.setdefault(k, {})
                    e["p"] = e.get("p", 0) + d.get("p", 0)
                    e["r"] = max(e.get("r", 0), d.get("r", 0))
                    e["l"] = max(e.get("l", 0), d.get("l", 0))

    def _covers_online(self):
        albums = [self.nocover.item(i).data(Qt.UserRole) for i in range(self.nocover.count())]
        if albums:
            self.win.start_batch(albums)

    def _tags_online(self):
        keys, albums = set(), []
        for t, _m in (self.res or {}).get("tags", []):
            a = self.win.local_lib.albums.get(t.get("akey") or t.get("cover"))
            if a and a["key"] not in keys:
                keys.add(a["key"]); albums.append(a)
        if albums:
            self.win.start_batch(albums)

    def _tag_open(self, it, _c):
        t = it.data(0, Qt.UserRole)
        if t:
            self.win.navigate(f"album:{t['cover']}")
            self.win.reveal_track(t)

    def _missing_relink(self):
        w, n = self.win, 0
        mapping = {}
        for i in range(self.missing.topLevelItemCount()):
            old, new = self.missing.topLevelItem(i).data(0, Qt.UserRole)
            if new:
                mapping[old] = new
        for old, new in mapping.items():
            if old in w.stats.data and new not in w.stats.data:
                w.stats.data[new] = w.stats.data.pop(old)
            n += 1
        for name in w.playlist_names():
            tr = w.playlist_tracks(name)
            if any(t["path"] in mapping for t in tr):
                w.save_playlist(name, w.tracks_from_paths([(mapping.get(t["path"], t["path"]), t["title"]) for t in tr]))
        w.stats.save()
        w.flash(tr_("{0} Dateien neu zugeordnet").format(n))
        self.run()

    def _missing_forget(self):
        w, n = self.win, 0
        for i in range(self.missing.topLevelItemCount()):
            old, new = self.missing.topLevelItem(i).data(0, Qt.UserRole)
            if not new and old in w.stats.data:
                del w.stats.data[old]; n += 1
        w.stats.save()
        w.flash(tr_("{0} Einträge vergessen (Wiedergabelisten bleiben unverändert)").format(n))
        self.run()


# ════════════════════════════════════════════════════════════════════════════
#  Updates (Release-Seite auf GitHub)
# ════════════════════════════════════════════════════════════════════════════
GITHUB_REPO = "RembrandtZ4/NeoNote-Media-Player"
RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"
UPDATE_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v))[:4]) or (0,)


def is_newer(v):
    return version_tuple(v) > version_tuple(APP_VERSION)


def installed_by_package():
    """Linux: über pacman/AUR installiert (dann kümmert sich die Paketverwaltung um Updates)."""
    return not IS_WIN and str(Path(__file__).resolve()).startswith("/usr/")


def release_notes_for_lang(body):
    """Die Release-Texte sind zweisprachig (oben Englisch, nach „---“ Deutsch): passenden Teil wählen."""
    body = (body or "").replace("\r\n", "\n")
    parts = [x.strip() for x in re.split(r"\n-{3,}\n", body) if x.strip()]
    if len(parts) >= 2:
        txt = parts[1] if LANG == "de" else parts[0]
    else:
        txt = body.strip()
    lines = txt.splitlines()
    if lines and ("English" in lines[0] and "Deutsch" in lines[0]):
        lines = lines[1:]
    # Download-Tabelle weglassen – im Player interessiert nur, was neu ist
    first = next((i for i, l in enumerate(lines) if l.startswith("**")), None)
    if first is not None:
        lines = lines[first:]
    return "\n".join(lines).strip()


class UpdateCheck(QThread):
    """Fragt die neueste Release-Seite ab. Es werden keine Daten übertragen, nur diese eine Seite gelesen."""
    result = Signal(dict)
    failed = Signal(str)

    def run(self):
        try:
            req = urllib.request.Request(UPDATE_API, headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}",
                                                             "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read().decode("utf-8"))
            assets = {}
            for a in d.get("assets") or []:
                assets[a.get("name", "")] = {"url": a.get("browser_download_url", ""), "size": int(a.get("size") or 0),
                                             "digest": a.get("digest") or ""}
            ver = (d.get("tag_name") or "").lstrip("vV")
            if not ver:
                raise ValueError("no version")
            self.result.emit({"version": ver, "notes": d.get("body") or "", "url": d.get("html_url") or RELEASES_URL,
                              "assets": assets})
        except Exception as e:
            self.failed.emit(str(e))


class UpdateDownload(QThread):
    """Lädt den Windows-Installer herunter und prüft Größe und – falls GitHub sie liefert – die SHA-256-Prüfsumme."""
    progress = Signal(int, int)
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, url, name, size, digest):
        super().__init__()
        self.url, self.name, self.size, self.digest = url, name, size, digest

    def run(self):
        import tempfile
        try:
            if not self.url.startswith("https://github.com/") and not self.url.startswith("https://objects.githubusercontent.com/"):
                raise ValueError("unexpected download address")
            d = Path(tempfile.gettempdir()) / "NeoNote-Update"
            d.mkdir(parents=True, exist_ok=True)
            out = d / os.path.basename(self.name)
            part = out.with_suffix(out.suffix + ".part")
            h = hashlib.sha256()
            req = urllib.request.Request(self.url, headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"})
            got = 0
            with urllib.request.urlopen(req, timeout=30) as r, open(part, "wb") as f:
                total = int(r.headers.get("Content-Length") or self.size or 0)
                while True:
                    if self.isInterruptionRequested():
                        raise RuntimeError("cancelled")
                    chunk = r.read(256 * 1024)
                    if not chunk:
                        break
                    f.write(chunk); h.update(chunk); got += len(chunk)
                    self.progress.emit(got, total)
            if self.size and got != self.size:
                raise ValueError(tr_("Die Datei ist unvollständig."))
            if self.digest.startswith("sha256:") and h.hexdigest() != self.digest.split(":", 1)[1].lower():
                raise ValueError(tr_("Die Prüfsumme stimmt nicht."))
            part.replace(out)
            self.done.emit(str(out))
        except Exception as e:
            self.failed.emit(str(e))


def win_run_update(setup, restart):
    """Startet den Installer still mit Administratorrechten. Ein unsichtbarer, normaler PowerShell-Prozess
    wartet, bis er fertig ist, und startet NeoNote danach wieder – ohne Administratorrechte."""
    def q(x):
        return "'" + str(x).replace("'", "''") + "'"
    ps = f"try {{ Start-Process -FilePath {q(setup)} -ArgumentList '/S' -Verb RunAs -Wait }} catch {{ }}"
    if restart:
        ps += f"; Start-Sleep -Milliseconds 600; Start-Process -FilePath {q(sys.executable)}"
    subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


class WhatsNewDialog(QDialog):
    def __init__(self, parent, info):
        super().__init__(parent)
        self.setWindowTitle(tr_("Neu in NeoNote {0}").format(info["version"]))
        self.resize(620, 520)
        lay = QVBoxLayout(self); lay.setContentsMargins(18, 16, 18, 14)
        tb = QTextBrowser(); tb.setOpenExternalLinks(True)
        tb.setMarkdown(release_notes_for_lang(info.get("notes", "")))
        lay.addWidget(tb, 1)
        bb = QDialogButtonBox(QDialogButtonBox.Close); bb.rejected.connect(self.reject)
        bb.button(QDialogButtonBox.Close).setText(tr_("Schließen"))
        lay.addWidget(bb)


class AboutDialog(QDialog):
    """Über NeoNote: Version, verwendete Bausteine mit Lizenzen, Datenordner."""

    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle(tr_("Über {0}").format(APP_NAME))
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self); lay.setContentsMargins(26, 22, 26, 18); lay.setSpacing(10)
        head = QHBoxLayout(); head.setSpacing(16)
        ic = QLabel(); ic.setPixmap(app_icon().pixmap(72, 72)); head.addWidget(ic)
        tv = QVBoxLayout(); tv.setSpacing(2)
        t1 = QLabel(APP_TITLE); f = t1.font(); f.setPointSizeF(f.pointSizeF() + 6); f.setWeight(QFont.DemiBold); t1.setFont(f)
        t2 = QLabel(tr_("Version {0}").format(APP_VERSION)); t2.setObjectName("hint")
        t3 = QLabel(tr_("Musik und Videos im Stil des Windows Media Player 12 – für Linux und Windows."))
        t3.setWordWrap(True)
        tv.addWidget(t1); tv.addWidget(t2); tv.addSpacing(4); tv.addWidget(t3)
        head.addLayout(tv, 1); lay.addLayout(head)
        lay.addSpacing(6)
        lay.addWidget(QLabel(tr_("<b>Verwendete Bausteine</b>")))
        rows = [("Python", platform_version(), tr_("PSF-Lizenz")),
                ("Qt / PySide6", f"{qVersion()} / {_pyside_version()}", "LGPL-3.0"),
                ("FFmpeg", tr_("in Qt Multimedia"), "LGPL-2.1+"),
                ("mpv / libmpv", _mpv_version(), "LGPL-2.1+ / GPL-2.0+"),
                ("mutagen", _mod_version("mutagen", "version_string"), "GPL-2.0+"),
                ("python-mpv", "", "LGPL-2.1+ / GPL-2.0+")]
        rows.append(("WinRT-Anbindung (pywinrt)", "", "MIT") if IS_WIN else ("jeepney (D-Bus)", "", "MIT"))
        rows.append((tr_("Albumdaten"), "MusicBrainz", "CC0"))
        rows.append((tr_("Cover"), tr_("Cover Art Archive"), tr_("je nach Bild")))
        grid = QGridLayout(); grid.setHorizontalSpacing(18); grid.setVerticalSpacing(3)
        for i, (n, v, l) in enumerate(rows):
            a = QLabel(n); b = QLabel(v); c = QLabel(l)
            b.setObjectName("hint"); c.setObjectName("hint")
            for w in (a, b, c):
                w.setTextFormat(Qt.PlainText)
            grid.addWidget(a, i, 0); grid.addWidget(b, i, 1); grid.addWidget(c, i, 2)
        lay.addLayout(grid)
        lay.addSpacing(6)
        lay.addWidget(QLabel(tr_("<b>Deine Daten</b>")))
        brow = QHBoxLayout(); brow.setSpacing(8)
        for label, path in ((tr_("Bibliothek und Wiedergabelisten"), DATA_DIR), (tr_("Cover"), COVER_DIR.parent if IS_WIN else COVER_DIR)):
            b = QPushButton(label); b.setToolTip(str(path))
            b.clicked.connect(lambda _=False, p=path: (Path(p).mkdir(parents=True, exist_ok=True),
                                                         QDesktopServices.openUrl(QUrl.fromLocalFile(str(p)))))
            brow.addWidget(b)
        brow.addStretch(); lay.addLayout(brow)
        sp = QSettings(APP_NAME, APP_NAME).fileName()
        sl = QLabel(tr_("Einstellungen: {0}").format(sp)); sl.setObjectName("hint"); sl.setWordWrap(True)
        sl.setTextFormat(Qt.PlainText); sl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay.addWidget(sl)
        urow = QHBoxLayout(); urow.setSpacing(10)
        ub = QPushButton(tr_("Nach Updates suchen"))
        self.ulbl = QLabel(""); self.ulbl.setObjectName("hint"); self.ulbl.setWordWrap(True)
        ub.clicked.connect(lambda: win.check_updates(manual=True, report=self.ulbl.setText))
        urow.addWidget(ub); urow.addWidget(self.ulbl, 1); lay.addLayout(urow)
        bb = QDialogButtonBox(QDialogButtonBox.Close); bb.rejected.connect(self.reject); bb.accepted.connect(self.accept)
        bb.button(QDialogButtonBox.Close).setText(tr_("Schließen"))
        lay.addWidget(bb)


def platform_version():
    return ".".join(map(str, sys.version_info[:3]))


def _pyside_version():
    try:
        import PySide6
        return PySide6.__version__
    except Exception:
        return ""


def _mod_version(mod, attr):
    try:
        return str(getattr(__import__(mod), attr))
    except Exception:
        return ""


def _mpv_version():
    try:
        import mpv
        v = mpv._mpv_client_api_version()
        return f"API {v[0]}.{v[1]}"
    except Exception:
        return tr_("nicht installiert")


class EqualizerDialog(QDialog):
    """Grafischer Equalizer (10 Bänder) mit Presets, Vorverstärkung und Lautstärkeangleichung."""

    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle(tr_("Equalizer"))
        self.setMinimumWidth(620)
        st = win.settings
        self.enabled = st.value("eq/enabled", False, type=bool)
        try:
            self.gains = [int(x) for x in json.loads(st.value("eq/gains", "[]") or "[]")] or [0] * 10
        except ValueError:
            self.gains = [0] * 10
        self.preamp = st.value("eq/preamp", 0, type=int)
        lay = QVBoxLayout(self); lay.setContentsMargins(18, 16, 18, 14); lay.setSpacing(12)
        top = QHBoxLayout()
        self.c_on = QCheckBox(tr_("Equalizer aktiv")); self.c_on.setChecked(self.enabled)
        self.c_on.toggled.connect(self._changed)
        self.preset = QComboBox()
        for n in list(EQ_PRESETS) + ["Eigene Einstellung"]:
            self.preset.addItem(tr_(n + "@eq" if n == "Sprache" else n), n)
        self.preset.setCurrentIndex(max(0, self.preset.findData(st.value("eq/preset", "Neutral"))))
        self.preset.currentIndexChanged.connect(lambda _i: self._preset(self.preset.currentData()))
        top.addWidget(self.c_on); top.addStretch(); top.addWidget(QLabel(tr_("Voreinstellung"))); top.addWidget(self.preset)
        lay.addLayout(top)

        bands = QHBoxLayout(); bands.setSpacing(4)
        self.sliders, self.vals = [], []
        for i, f in enumerate(EQ_BANDS):
            col = QVBoxLayout(); col.setSpacing(4)
            val = QLabel(); val.setAlignment(Qt.AlignCenter); val.setObjectName("hint")
            sl = QSlider(Qt.Vertical); sl.setRange(-12, 12); sl.setValue(self.gains[i]); sl.setFixedHeight(170)
            sl.setTickPosition(QSlider.TicksBothSides); sl.setTickInterval(6); sl.setPageStep(3)
            sl.valueChanged.connect(self._slider)
            lab = QLabel(f"{f // 1000}k" if f >= 1000 else str(f)); lab.setAlignment(Qt.AlignCenter)
            col.addWidget(val); col.addWidget(sl, 0, Qt.AlignHCenter); col.addWidget(lab)
            bands.addLayout(col)
            self.sliders.append(sl); self.vals.append(val)
        lay.addLayout(bands)
        hz = QLabel(tr_("Hz")); hz.setObjectName("hint"); hz.setAlignment(Qt.AlignRight)
        lay.addWidget(hz)

        pre = QHBoxLayout()
        self.pre = QSlider(Qt.Horizontal); self.pre.setRange(-12, 12); self.pre.setValue(self.preamp)
        self.pre_lbl = QLabel(); self.pre_lbl.setFixedWidth(52)
        self.pre.valueChanged.connect(self._changed)
        pre.addWidget(QLabel(tr_("Vorverstärkung"))); pre.addWidget(self.pre, 1); pre.addWidget(self.pre_lbl)
        lay.addLayout(pre)
        rg = QHBoxLayout()
        self.rg = QComboBox(); self.rg.addItems([tr_("Aus"), tr_("Pro Titel"), tr_("Pro Album")])
        self.rg.setCurrentIndex(["no", "track", "album"].index(st.value("eq/replaygain", "no"))
                                if st.value("eq/replaygain", "no") in ("no", "track", "album") else 0)
        self.rg.currentIndexChanged.connect(self._changed)
        rg.addWidget(QLabel(tr_("Lautstärke angleichen (ReplayGain)"))); rg.addWidget(self.rg); rg.addStretch()
        reset = QPushButton(tr_("Zurücksetzen")); reset.setAutoDefault(False)
        reset.clicked.connect(lambda: self.preset.setCurrentIndex(self.preset.findData("Neutral")))
        rg.addWidget(reset)
        lay.addLayout(rg)
        self.info = QLabel(); self.info.setObjectName("hint"); self.info.setWordWrap(True); self.info.setTextFormat(Qt.RichText)
        lay.addWidget(self.info)
        bb = QDialogButtonBox(QDialogButtonBox.Close); bb.button(QDialogButtonBox.Close).setText(tr_("Schließen"))
        bb.rejected.connect(self.close)
        lay.addWidget(bb)
        if not win.player.mp:
            for w in (self.c_on, self.preset, self.pre, self.rg, reset, *self.sliders):
                w.setEnabled(False)
            self.info.setText(tr_("Der Equalizer braucht mpv. Unter Einstellungen → System kann NeoNote es herunterladen.")
                              if IS_WIN else
                              tr_("Der Equalizer braucht mpv. Installieren mit <code>sudo pacman -S mpv python-mpv</code> "
                              "und den Player neu starten."))
        else:
            self.info.setText(tr_("Gilt für Musik und Internetradio, nicht für Videos. ReplayGain wirkt nur bei Dateien, "
                              "die ReplayGain-Angaben enthalten (z. B. mit foobar2000, rsgain oder MusicBrainz Picard "
                              "erzeugt). Positive Werte werden automatisch vor Übersteuerung geschützt."))
        self._labels()

    def _labels(self):
        for sl, v in zip(self.sliders, self.vals):
            v.setText(f"{sl.value():+d}" if sl.value() else "0")
        self.pre_lbl.setText(tr_("{0:+d} dB").format(self.pre.value()) if self.pre.value() else tr_("0 dB"))

    def _preset(self, name):
        if name in EQ_PRESETS:
            for sl, g in zip(self.sliders, EQ_PRESETS[name]):
                sl.blockSignals(True); sl.setValue(g); sl.blockSignals(False)
            if name != "Neutral" and not self.c_on.isChecked():
                self.c_on.blockSignals(True); self.c_on.setChecked(True); self.c_on.blockSignals(False)
        self._changed()

    def _slider(self, _v):
        gains = [sl.value() for sl in self.sliders]
        match = next((n for n, g in EQ_PRESETS.items() if g == gains), "Eigene Einstellung")
        self.preset.blockSignals(True); self.preset.setCurrentIndex(self.preset.findData(match)); self.preset.blockSignals(False)
        if not self.c_on.isChecked():
            self.c_on.blockSignals(True); self.c_on.setChecked(True); self.c_on.blockSignals(False)
        self._changed()

    def _changed(self, *_):
        st = self.win.settings
        st.setValue("eq/enabled", self.c_on.isChecked())
        st.setValue("eq/gains", json.dumps([sl.value() for sl in self.sliders]))
        st.setValue("eq/preamp", self.pre.value())
        st.setValue("eq/preset", self.preset.currentData())
        st.setValue("eq/replaygain", ["no", "track", "album"][self.rg.currentIndex()])
        self._labels()
        self.win.apply_audio_settings()


# ════════════════════════════════════════════════════════════════════════════
#  Bibliothek & Statistik
# ════════════════════════════════════════════════════════════════════════════
class Scanner(QThread):
    progress = Signal(int, int)
    finished_scan = Signal(list)
    dirs_found = Signal(list)

    def __init__(self, folders, parent=None, extra=(), known=None):
        super().__init__(parent)
        self.folders = folders
        self.extra = list(extra)
        self.known = known or {}
        self.changed = 0

    def _walk(self, folder, files, dirs):
        """Ordner rekursiv durchgehen. os.scandir liefert unter Windows Größe und Änderungszeit gleich mit –
        bei tausenden Dateien spart das einen Großteil der Zeit beim Prüfen auf Änderungen."""
        stack = [folder]
        n = 0
        while stack:
            d = stack.pop()
            dirs.append(d)
            try:
                it = os.scandir(d)
            except OSError:
                continue
            with it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=True):
                            stack.append(e.path)
                        elif os.path.splitext(e.name)[1].lower() in AUDIO_EXT:
                            st = e.stat()
                            files[e.path] = (st.st_mtime, st.st_size)
                    except OSError:
                        continue
            n += 1
            if n % 50 == 0:
                time.sleep(0)                   # Oberfläche nicht ausbremsen

    def run(self):
        found, dirs = {}, []
        for folder in self.folders:
            self._walk(folder, found, dirs)
        self.dirs_found.emit(dirs)
        for f in self.extra:
            if f not in found:
                try:
                    st = os.stat(f)
                    found[f] = (st.st_mtime, st.st_size)
                except OSError:
                    pass
        files = sorted(found)
        tracks, attempts, have = [], defaultdict(int), set()
        for i, p in enumerate(files):
            if self.isInterruptionRequested():
                return
            mtime, size = found[p]
            old = self.known.get(p)
            if old and old.get("mtime") == mtime and old.get("size") == size:
                tracks.append(old)              # unverändert – Tags nicht neu lesen
                continue
            try:
                stt = os.stat(p)
            except OSError:
                continue
            self.changed += 1
            t = read_track(p)
            if t:
                t["mtime"] = stt.st_mtime
                k = t["cover"]
                if k not in have:
                    if (cover_path(k)).exists():
                        have.add(k)
                    elif attempts[k] < 3:
                        attempts[k] += 1
                        if save_cover(p, k):
                            have.add(k)
                tracks.append(t)
            if i % 20 == 0:
                self.progress.emit(i, len(files))
        self.changed += len(set(self.known) - set(files))
        self.progress.emit(len(files), len(files))
        self.finished_scan.emit(tracks)


class Library:
    def __init__(self):
        self.tracks, self.albums = [], OrderedDict()
        self.outdated = False
        try:
            self.overrides = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.overrides = {}
        try:
            self.hidden = set(json.loads(HIDDEN_FILE.read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError):
            self.hidden = set()

    def save_hidden(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        HIDDEN_FILE.write_text(json.dumps(sorted(self.hidden), ensure_ascii=False), encoding="utf-8")

    def save_overrides(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        OVERRIDES_FILE.write_text(json.dumps(self.overrides, ensure_ascii=False), encoding="utf-8")

    def load(self):
        try:
            data = json.loads(LIB_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {"version": LIB_VERSION, "tracks": []}
        if isinstance(data, list) or data.get("version") != LIB_VERSION:
            self.outdated = True
            data = {"tracks": data if isinstance(data, list) else data.get("tracks", [])}
        self.set_tracks(data["tracks"])

    def save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        LIB_FILE.write_text(json.dumps({"version": LIB_VERSION, "tracks": self.tracks}, ensure_ascii=False),
                            encoding="utf-8")

    def set_tracks(self, tracks):
        if self.hidden:                                  # in „Bibliothek prüfen“ ausgeblendete Doppelte
            tracks = [t for t in tracks if t["path"] not in self.hidden]
        self.tracks = tracks
        albums = {}
        for t in tracks:
            if t["path"] in self.overrides:
                t.update(self.overrides[t["path"]])
            if not t.get("stream") and not t.get("remote"):
                t["cover"] = album_key(t.get("albumartist") or t["artist"], t["album"])
            t["akey"] = t["cover"]
            a = albums.setdefault(t["cover"], {"key": t["cover"], "title": t["album"], "artist": t["albumartist"],
                                               "year": t.get("year", ""), "genre": t.get("genre", ""), "tracks": []})
            a["tracks"].append(t)
            if not a["year"] and t.get("year"):
                a["year"] = t["year"]
        albums = self._split_editions(albums)
        for a in albums.values():
            a["tracks"].sort(key=lambda t: (t.get("disc", 1), t.get("track", 0), t["title"].lower()))
        self.albums = OrderedDict(sorted(albums.items(), key=lambda kv: (
            sort_name(kv[1]["artist"]), kv[1]["year"] or "9999", kv[1]["title"].lower())))

    @staticmethod
    def _split_editions(albums):
        """Liegt dasselbe Album mehrfach vor (z. B. einmal als FLAC, einmal als MP3 in eigenen Ordnern), zeigt
        NeoNote es wie WMP12 als getrennte Alben. Ein Album, das nur auf mehrere Ordner verteilt ist (CD1/CD2),
        bleibt zusammen: getrennt wird nur, wenn derselbe Titel (CD, Nr., Name) doppelt vorkommt."""
        out = {}
        for key, a in albums.items():
            tracks = a["tracks"]
            if len(tracks) < 2 or tracks[0].get("remote") or tracks[0].get("stream"):
                out[key] = a
                continue
            seen, dup = set(), False
            for t in tracks:
                sig = (t.get("disc", 1), t.get("track", 0), t["title"].strip().lower())
                if sig in seen:
                    dup = True
                    break
                seen.add(sig)
            dirs = OrderedDict()
            for t in tracks:
                dirs.setdefault(os.path.dirname(t["path"]), []).append(t)
            if not dup or len(dirs) < 2:
                out[key] = a
                continue
            # Ordner mit gleichem Elternordner + „CD1“/„Disc 2“ … gehören zusammen; sonst je Ordner eine Ausgabe
            groups = OrderedDict()
            for d, ts in dirs.items():
                base = d
                if re.fullmatch(r"(?i)(cd|disc|disk)\s*\d+", os.path.basename(d) or ""):
                    base = os.path.dirname(d)
                groups.setdefault(base, []).extend(ts)
            if len(groups) < 2:
                out[key] = a
                continue
            # die Ausgabe mit der besten Qualität behält den ursprünglichen Schlüssel
            order = sorted(groups.values(), key=lambda ts: -sum((t.get("bitrate") or 0) for t in ts) / max(1, len(ts)))
            for i, ts in enumerate(order):
                k = key if i == 0 else f"{key}~{i + 1}"
                types = sorted({(t.get("type") or os.path.splitext(t["path"])[1][1:]).upper() for t in ts if t.get("type") or t["path"]})
                b = dict(a, key=k, tracks=ts, edition=" / ".join(x for x in types if x))
                for t in ts:
                    t["akey"] = k
                out[k] = b
        return out

    def group_albums(self, field):
        groups = defaultdict(list)
        for a in self.albums.values():
            groups[a[field]].append(a)
        return OrderedDict(sorted(groups.items(), key=lambda kv: sort_name(kv[0])))


class JellyfinLibrary(Library):
    """Die Jellyfin-Musik als zweite Bibliothek – zwischengespeichert, damit sie sofort (auch offline) da ist."""

    def __init__(self):
        self.tracks, self.albums = [], OrderedDict()
        self.outdated = False
        self.overrides, self.hidden = {}, set()
        self.playlists = []
        self.offline = {}

    def load(self):
        try:
            d = json.loads(JF_CACHE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            d = {}
        self.playlists = d.get("playlists", [])
        self.offline = d.get("offline", {})
        self.set_tracks(d.get("tracks", []))

    def save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        JF_CACHE_FILE.write_text(json.dumps({"tracks": self.tracks, "playlists": self.playlists,
                                             "offline": self.offline}, ensure_ascii=False), encoding="utf-8")

    def clear(self):
        self.set_tracks([]); self.playlists = []
        try:
            JF_CACHE_FILE.unlink()
        except OSError:
            pass

    def by_id(self):
        return {t["jf_id"]: t for t in self.tracks}

    def offline_path(self, t):
        p = self.offline.get(t.get("jf_id", ""))
        return p if p and os.path.exists(p) else None


class Stats:
    """Bewertungen und Wiedergabeanzahl, gespeichert pro Dateipfad."""

    def __init__(self):
        try:
            self.data = json.loads(STATS_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.data = {}
        self._timer = QTimer(singleShot=True, interval=1500)
        self._timer.timeout.connect(self.save)

    def rating(self, path):
        return self.data.get(path, {}).get("r", 0)

    def plays(self, path):
        return self.data.get(path, {}).get("p", 0)

    def set_rating(self, path, r):
        self.data.setdefault(path, {})["r"] = r
        self._timer.start()

    def add_play(self, path):
        d = self.data.setdefault(path, {})
        d["p"] = d.get("p", 0) + 1
        d["l"] = int(time.time())
        self._timer.start()

    def last(self, path):
        return self.data.get(path, {}).get("l", 0)

    def save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STATS_FILE.write_text(json.dumps(self.data), encoding="utf-8")


# ════════════════════════════════════════════════════════════════════════════
#  Cover-Cache
# ════════════════════════════════════════════════════════════════════════════
def load_cover_image(key, size):
    """Cover als quadratisches QImage in Zielgröße laden (thread-sicher).
    Der JPEG-Decoder verkleinert schon beim Entpacken – viel schneller als erst groß laden und dann skalieren."""
    path = cover_path(key)
    if not key or not path.exists():
        return None
    r = QImageReader(str(path))
    r.setAutoTransform(True)
    src = r.size()
    if src.isValid() and src.width() > 0 and src.height() > 0:
        k = size / min(src.width(), src.height())
        if k < 1:
            r.setScaledSize(QSize(max(size, round(src.width() * k)), max(size, round(src.height() * k))))
    img = r.read()
    if img.isNull():
        return None
    if img.width() != size or img.height() != size:
        img = img.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        if img.width() != size or img.height() != size:
            img = img.copy((img.width() - size) // 2, (img.height() - size) // 2, size, size)
    return img.convertToFormat(QImage.Format_ARGB32_Premultiplied)


class CoverLoader(QThread):
    """Lädt Cover im Hintergrund. Was gerade sichtbar ist, kommt zuerst dran."""
    loaded = Signal(str, int, QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._q, self._pending = deque(), set()
        self._cv = threading.Condition()
        self._stop = False

    def want(self, key, size, urgent=True):
        ck = (key, size)
        with self._cv:
            if ck in self._pending:
                if urgent and self._q and self._q[0] != ck:
                    try:
                        self._q.remove(ck)
                    except ValueError:
                        return
                    self._q.appendleft(ck)
                return
            self._pending.add(ck)
            (self._q.appendleft if urgent else self._q.append)(ck)
            self._cv.notify()
        if not self.isRunning():
            self.start(QThread.LowPriority)

    def drop_background(self):
        with self._cv:
            self._q.clear(); self._pending.clear()

    def stop(self):
        with self._cv:
            self._stop = True; self._cv.notify()
        self.wait(2000)

    def run(self):
        while True:
            with self._cv:
                while not self._q and not self._stop:
                    self._cv.wait()
                if self._stop:
                    return
                ck = self._q.popleft()
            try:
                img = load_cover_image(*ck)
            except Exception:
                img = None
            with self._cv:
                if ck not in self._pending:          # zwischendurch verworfen (Cache geleert)
                    continue
                self._pending.discard(ck)
            self.loaded.emit(ck[0], ck[1], img if img is not None else QImage())


class CoverCache:
    BUDGET = 192 * 1024 * 1024          # Bytes für fertig skalierte Cover

    def __init__(self, limit=None):
        self.cache = OrderedDict()
        self.bytes = 0
        self.gen = 0                    # steigt bei clear(); daran erkennen abgeleitete Caches veraltete Bilder
        self.loader = None
        self.on_loaded = []             # Rückrufe, wenn ein Cover im Hintergrund fertig wurde
        self._missing = set()
        self.sync_mode = False          # True: sofort laden (z. B. hinter dem Ladebildschirm)

    def _put(self, ck, pm):
        old = self.cache.pop(ck, None)
        if old is not None:
            self.bytes -= old.width() * old.height() * 4
        self.cache[ck] = pm
        self.bytes += pm.width() * pm.height() * 4
        while self.bytes > self.BUDGET and len(self.cache) > 1:
            _k, v = self.cache.popitem(last=False)
            self.bytes -= v.width() * v.height() * 4

    def get(self, key, size):
        ck = (key, size)
        if ck in self.cache:
            self.cache.move_to_end(ck)
            return self.cache[ck]
        img = load_cover_image(key, size) if key else None
        if img is None:
            if key and key.startswith("jf-") and JF_FETCHER is not None:
                JF_FETCHER.want(key)                      # wird nachgeladen; Platzhalter nicht merken
                return self.placeholder(size)
            pm = self.placeholder(size)
        else:
            pm = QPixmap.fromImage(img)
        self._put(ck, pm)
        return pm

    def peek(self, key, size, urgent=True):
        """Wie get(), lädt aber nicht im Vordergrund: None = wird gerade geladen."""
        ck = (key, size)
        if ck in self.cache:
            self.cache.move_to_end(ck)
            return self.cache[ck]
        if not key or key in self._missing or self.loader is None or self.sync_mode:
            return self.get(key, size)
        if key.startswith("jf-") and not (cover_path(key)).exists():
            return self.get(key, size)
        self.loader.want(key, size, urgent)
        return None

    def prefetch(self, keys, size):
        if self.loader is None:
            return
        for k in keys:
            if k and k not in self._missing and (k, size) not in self.cache:
                self.loader.want(k, size, urgent=False)

    def _loaded(self, key, size, img):
        if img.isNull():
            if key.startswith("jf-") and JF_FETCHER is not None:
                JF_FETCHER.want(key)
                return
            self._missing.add(key)
            pm = self.placeholder(size)
        else:
            pm = QPixmap.fromImage(img)
        self._put((key, size), pm)
        for cb in self.on_loaded:
            cb(key)

    def attach_loader(self, parent):
        self.loader = CoverLoader(parent)
        self.loader.loaded.connect(self._loaded)

    def forget(self, key):
        for ck in [k for k in self.cache if k[0] == key]:
            v = self.cache.pop(ck)
            self.bytes -= v.width() * v.height() * 4
        self._missing.discard(key)
        self.gen += 1

    def clear(self):
        self.cache.clear(); self.bytes = 0; self._missing.clear()
        self.gen += 1
        if self.loader is not None:
            self.loader.drop_background()

    _ph_cache = {}

    @staticmethod
    def _note_shape(s, ox=0.0, oy=0.0, k=1.0):
        """Umriss einer Doppelnote (♫) als eine zusammenhängende Fläche."""
        def P(x, y):
            return QPointF(ox + x * s * k, oy + y * s * k)
        shape = QPainterPath()
        for cx, cy in ((33, 74), (67, 66)):                      # Notenköpfe, leicht schräg
            e = QPainterPath()
            e.addEllipse(QPointF(0, 0), 13 * s * k, 9 * s * k)
            tf = QTransform().translate(P(cx, cy).x(), P(cx, cy).y()).rotate(-24)
            shape.addPath(tf.map(e))
        shape.addRect(QRectF(P(42.5, 30), P(47, 72)))          # Hälse
        shape.addRect(QRectF(P(76.5, 22), P(81, 64)))
        shape.addPolygon(QPolygonF([P(42.5, 29), P(81, 20), P(81, 31), P(42.5, 40)]))   # Balken
        shape.setFillRule(Qt.WindingFill)
        outline = shape.simplified()
        inner = QPainterPath(P(46, 34.5)); inner.lineTo(P(77.5, 27))                # zweiter Balken
        return outline, inner

    @staticmethod
    def _neon(p, paths, color, s, strength=1.0):
        """Zeichnet Pfade als leuchtende Neonröhre: weicher Schein, farbige Röhre, heller Kern."""
        for w, a in ((11.0, 0.05), (7.5, 0.09), (5.0, 0.15), (3.2, 0.26)):
            c = QColor(color); c.setAlphaF(a * strength)
            pen = QPen(c, max(1.0, w * s)); pen.setJoinStyle(Qt.RoundJoin); pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            for path in paths:
                p.drawPath(path)
        c = QColor(color); c.setAlphaF(min(1.0, 0.95 * strength))
        pen = QPen(c, max(0.8, 1.7 * s)); pen.setJoinStyle(Qt.RoundJoin); pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        for path in paths:
            p.drawPath(path)
        core = mix(color, QColor("white"), 0.65); core.setAlphaF(min(1.0, 0.9 * strength))
        pen = QPen(core, max(0.5, 0.6 * s)); pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        for path in paths:
            p.drawPath(path)

    @classmethod
    def placeholder(cls, size):
        """Platzhalter-Cover: Doppelnote als Neonröhre in der Akzentfarbe."""
        ck = (size, T.accent.name())
        if ck in cls._ph_cache:
            return cls._ph_cache[ck]
        acc = QColor(T.accent)
        pm = QPixmap(size, size)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        bg = QRadialGradient(QPointF(size * 0.45, size * 0.55), size * 0.85)
        bg.setColorAt(0, mix(QColor("#05070b"), acc, 0.16))
        bg.setColorAt(0.6, QColor("#06080c"))
        bg.setColorAt(1, QColor("#020304"))
        p.fillRect(0, 0, size, size, bg)
        s = size / 100.0
        # kleine, unscharfe Note oben rechts (Tiefe)
        o2, i2 = cls._note_shape(s, ox=69 * s, oy=-5 * s, k=0.34)
        cls._neon(p, [o2, i2], acc, s * 0.6, strength=0.45)
        # Hauptnote mit leichtem 3D-Versatz
        o, i = cls._note_shape(s, ox=-2 * s, oy=4 * s, k=0.98)
        depth = o.translated(2.6 * s, 2.0 * s)
        dc = QColor(acc); dc.setAlphaF(0.35)
        p.setPen(QPen(dc, max(0.8, 1.2 * s))); p.drawPath(depth)
        cls._neon(p, [o, i], acc, s)
        p.end()
        cls._ph_cache[ck] = pm
        if len(cls._ph_cache) > 40:
            cls._ph_cache.pop(next(iter(cls._ph_cache)))
        return pm


# ════════════════════════════════════════════════════════════════════════════
#  Icons
# ════════════════════════════════════════════════════════════════════════════
def make_icon(name, size=20, color=None):
    scale = 3
    pm = QPixmap(size * scale, size * scale)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(scale, scale)
    c = QColor(color) if color else QColor(T.fg)
    s = float(size)
    pen = QPen(c, 1.6); pen.setCapStyle(Qt.RoundCap); pen.setJoinStyle(Qt.RoundJoin)

    def P(x, y):
        return QPointF(x * s, y * s)

    def fill_poly(*pts):
        p.setPen(Qt.NoPen); p.setBrush(c)
        p.drawPolygon(QPolygonF([P(*pt) for pt in pts]))

    def head(tip, dx):
        fill_poly(tip, (tip[0] - dx, tip[1] - abs(dx) * .6), (tip[0] - dx, tip[1] + abs(dx) * .6))

    if name == "play":
        fill_poly((.32, .2), (.82, .5), (.32, .8))
    elif name == "pause":
        p.setPen(Qt.NoPen); p.setBrush(c)
        p.drawRect(QRectF(.27 * s, .22 * s, .15 * s, .56 * s)); p.drawRect(QRectF(.58 * s, .22 * s, .15 * s, .56 * s))
    elif name == "stop":
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawRect(QRectF(.29 * s, .29 * s, .42 * s, .42 * s))
    elif name == "prev":
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawRect(QRectF(.2 * s, .3 * s, .07 * s, .4 * s))
        fill_poly((.52, .3), (.29, .5), (.52, .7)); fill_poly((.78, .3), (.55, .5), (.78, .7))
    elif name == "next":
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawRect(QRectF(.73 * s, .3 * s, .07 * s, .4 * s))
        fill_poly((.48, .3), (.71, .5), (.48, .7)); fill_poly((.22, .3), (.45, .5), (.22, .7))
    elif name == "shuffle":
        p.setPen(pen); p.setBrush(Qt.NoBrush)
        a = QPainterPath(P(.12, .32)); a.cubicTo(P(.45, .32), P(.45, .68), P(.78, .68))
        b = QPainterPath(P(.12, .68)); b.cubicTo(P(.45, .68), P(.45, .32), P(.78, .32))
        p.drawPath(a); p.drawPath(b); head((.9, .32), .12); head((.9, .68), .12)
    elif name in ("repeat", "repeat1"):
        p.setPen(pen); p.setBrush(Qt.NoBrush)
        a = QPainterPath(P(.72, .3)); a.lineTo(P(.25, .3)); a.quadTo(P(.12, .3), P(.12, .45)); a.lineTo(P(.12, .52))
        b = QPainterPath(P(.28, .7)); b.lineTo(P(.75, .7)); b.quadTo(P(.88, .7), P(.88, .55)); b.lineTo(P(.88, .48))
        p.drawPath(a); p.drawPath(b); head((.82, .3), .11); head((.18, .7), -.11)
        if name == "repeat1":
            f = QFont(); f.setPixelSize(int(s * .34)); f.setBold(True)
            p.setFont(f); p.setPen(c); p.drawText(QRectF(0, .33 * s, s, .34 * s), Qt.AlignCenter, "1")
    elif name in ("volume", "mute"):
        fill_poly((.12, .38), (.28, .38), (.48, .2), (.48, .8), (.28, .62), (.12, .62))
        p.setPen(pen); p.setBrush(Qt.NoBrush)
        if name == "volume":
            p.drawArc(QRectF(.38 * s, .32 * s, .26 * s, .36 * s), -60 * 16, 120 * 16)
            p.drawArc(QRectF(.36 * s, .2 * s, .44 * s, .6 * s), -60 * 16, 120 * 16)
        else:
            p.drawLine(P(.6, .36), P(.86, .64)); p.drawLine(P(.86, .36), P(.6, .64))
    elif name == "back":
        p.setPen(pen); p.drawLine(P(.75, .5), P(.28, .5)); p.drawLine(P(.28, .5), P(.47, .31)); p.drawLine(P(.28, .5), P(.47, .69))
    elif name == "forward":
        p.setPen(pen); p.drawLine(P(.25, .5), P(.72, .5)); p.drawLine(P(.72, .5), P(.53, .31)); p.drawLine(P(.72, .5), P(.53, .69))
    elif name == "chev_left":
        cp = QPen(c, 2.0); cp.setCapStyle(Qt.RoundCap); cp.setJoinStyle(Qt.RoundJoin); p.setPen(cp)
        p.drawPolyline(QPolygonF([P(.6, .24), P(.36, .5), P(.6, .76)]))
    elif name == "chev_right":
        cp = QPen(c, 2.0); cp.setCapStyle(Qt.RoundCap); cp.setJoinStyle(Qt.RoundJoin); p.setPen(cp)
        p.drawPolyline(QPolygonF([P(.4, .24), P(.64, .5), P(.4, .76)]))
    elif name == "library":                      # Raster + Pfeil (wie WMP12)
        p.setPen(Qt.NoPen); p.setBrush(c)
        for x, y in ((.14, .18), (.38, .18), (.14, .42)):
            p.drawRect(QRectF(x * s, y * s, .18 * s, .18 * s))
        p.drawRect(QRectF(.14 * s, .66 * s, .18 * s, .18 * s))
        lp = QPen(c, 1.6); lp.setCapStyle(Qt.RoundCap); lp.setJoinStyle(Qt.RoundJoin); p.setPen(lp)
        p.drawLine(P(.86, .58), P(.46, .58)); p.drawPolyline(QPolygonF([P(.6, .44), P(.46, .58), P(.6, .72)]))
    elif name == "nowplaying":                   # Rahmen mit Pfeil nach oben rechts
        lp = QPen(c, 1.5); lp.setJoinStyle(Qt.RoundJoin); lp.setCapStyle(Qt.RoundCap); p.setPen(lp)
        p.setBrush(Qt.NoBrush)
        p.drawPolyline(QPolygonF([P(.5, .18), P(.18, .18), P(.18, .82), P(.82, .82), P(.82, .5)]))
        p.drawLine(P(.42, .58), P(.82, .18)); p.drawPolyline(QPolygonF([P(.56, .18), P(.82, .18), P(.82, .44)]))
    elif name == "replay":
        lp = QPen(c, 1.7); lp.setCapStyle(Qt.RoundCap); p.setPen(lp); p.setBrush(Qt.NoBrush)
        p.drawArc(QRectF(.2 * s, .2 * s, .6 * s, .6 * s), 100 * 16, 300 * 16)
        fill_poly((.42, .1), (.6, .2), (.42, .32))
    elif name == "mini":
        lp = QPen(c, 1.4); p.setPen(lp); p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(.14 * s, .2 * s, .72 * s, .6 * s))
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawRect(QRectF(.48 * s, .52 * s, .32 * s, .22 * s))
    elif name == "eq":
        lp = QPen(c, 1.5); lp.setCapStyle(Qt.RoundCap); p.setPen(lp)
        for x, y in ((.25, .62), (.5, .36), (.75, .55)):
            p.drawLine(P(x, .16), P(x, .84))
        p.setPen(Qt.NoPen); p.setBrush(c)
        for x, y in ((.25, .62), (.5, .36), (.75, .55)):
            p.drawRoundedRect(QRectF((x - .1) * s, (y - .06) * s, .2 * s, .12 * s), 1, 1)
    elif name == "clock":
        lp = QPen(c, 1.5); lp.setCapStyle(Qt.RoundCap); p.setPen(lp); p.setBrush(Qt.NoBrush)
        p.drawEllipse(P(.5, .5), .34 * s, .34 * s)
        p.drawPolyline(QPolygonF([P(.5, .3), P(.5, .52), P(.64, .62)]))
    elif name == "person":
        p.setPen(Qt.NoPen); p.setBrush(c)
        p.drawEllipse(P(.5, .32), .15 * s, .15 * s)
        pp = QPainterPath(P(.2, .84)); pp.cubicTo(P(.22, .55), P(.78, .55), P(.8, .84)); pp.closeSubpath()
        p.drawPath(pp)
    elif name == "disc":
        lp = QPen(c, 1.5); p.setPen(lp); p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(.16 * s, .16 * s, .68 * s, .68 * s), 2, 2)
        p.drawEllipse(P(.5, .5), .2 * s, .2 * s)
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawEllipse(P(.5, .5), .05 * s, .05 * s)
    elif name == "tag":
        lp = QPen(c, 1.5); lp.setJoinStyle(Qt.RoundJoin); p.setPen(lp); p.setBrush(Qt.NoBrush)
        p.drawPolygon(QPolygonF([P(.18, .18), P(.52, .18), P(.84, .5), P(.5, .84), P(.18, .52)]))
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawEllipse(P(.34, .34), .06 * s, .06 * s)
    elif name == "note":
        p.setPen(Qt.NoPen); p.setBrush(c)
        p.save(); p.translate(P(.36, .72)); p.rotate(-20)
        p.drawEllipse(QPointF(0, 0), .14 * s, .1 * s); p.restore()
        p.drawRect(QRectF(.44 * s, .18 * s, .07 * s, .55 * s))
        p.drawPolygon(QPolygonF([P(.44, .18), P(.76, .26), P(.76, .38), P(.51, .31)]))
    elif name in ("list", "queue"):
        lp = QPen(c, 1.6); lp.setCapStyle(Qt.RoundCap); p.setPen(lp)
        for y in (.28, .5, .72):
            p.drawLine(P(.18 if name == "list" else .42, y), P(.84, y))
        if name == "queue":
            fill_poly((.14, .2), (.32, .32), (.14, .44))
    elif name == "auto":
        lp = QPen(c, 1.6); lp.setCapStyle(Qt.RoundCap); p.setPen(lp)
        for y in (.3, .52):
            p.drawLine(P(.16, y), P(.56, y))
        p.drawLine(P(.16, .74), P(.44, .74))
        star = star_polygon(.74 * s, .66 * s, .17 * s)
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawPolygon(star)
    elif name == "radio":
        lp = QPen(c, 1.5); lp.setCapStyle(Qt.RoundCap); p.setPen(lp); p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(.14 * s, .36 * s, .72 * s, .46 * s), 2, 2)
        p.drawLine(P(.3, .36), P(.66, .16))
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawEllipse(P(.64, .59), .1 * s, .1 * s)
        p.drawRect(QRectF(.24 * s, .52 * s, .18 * s, .04 * s)); p.drawRect(QRectF(.24 * s, .62 * s, .18 * s, .04 * s))
    elif name == "check":                  # Bibliothek prüfen: Klemmbrett mit Haken
        lp = QPen(c, 1.5); lp.setCapStyle(Qt.RoundCap); lp.setJoinStyle(Qt.RoundJoin); p.setPen(lp)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(.22 * s, .18 * s, .56 * s, .66 * s), 2, 2)
        p.drawLine(P(.4, .18), P(.6, .18))
        ck = QPainterPath(P(.34, .52)); ck.lineTo(P(.46, .64)); ck.lineTo(P(.67, .4)); p.drawPath(ck)
    elif name == "server":                 # Jellyfin / Server
        lp = QPen(c, 1.5); lp.setCapStyle(Qt.RoundCap); p.setPen(lp); p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(.16 * s, .2 * s, .68 * s, .26 * s), 2, 2)
        p.drawRoundedRect(QRectF(.16 * s, .54 * s, .68 * s, .26 * s), 2, 2)
        p.setPen(Qt.NoPen); p.setBrush(c)
        p.drawEllipse(P(.3, .33), .035 * s, .035 * s); p.drawEllipse(P(.3, .67), .035 * s, .035 * s)
    elif name == "cloud":
        lp = QPen(c, 1.5); lp.setCapStyle(Qt.RoundCap); p.setPen(lp); p.setBrush(Qt.NoBrush)
        cl = QPainterPath(P(.28, .72)); cl.cubicTo(P(.1, .72), P(.1, .48), P(.28, .48))
        cl.cubicTo(P(.3, .3), P(.55, .26), P(.62, .42)); cl.cubicTo(P(.82, .38), P(.92, .72), P(.72, .72))
        cl.closeSubpath(); p.drawPath(cl)
    elif name == "download":
        lp = QPen(c, 1.6); lp.setCapStyle(Qt.RoundCap); lp.setJoinStyle(Qt.RoundJoin); p.setPen(lp)
        p.drawLine(P(.5, .18), P(.5, .62))
        ar = QPainterPath(P(.32, .46)); ar.lineTo(P(.5, .64)); ar.lineTo(P(.68, .46)); p.drawPath(ar)
        p.drawLine(P(.22, .8), P(.78, .8))
    elif name == "plus":
        lp = QPen(c, 1.6); lp.setCapStyle(Qt.RoundCap); p.setPen(lp)
        p.drawLine(P(.5, .24), P(.5, .76)); p.drawLine(P(.24, .5), P(.76, .5))
    elif name == "minimize":
        p.setPen(QPen(c, 1.2)); p.drawLine(P(.28, .5), P(.72, .5))
    elif name == "maximize":
        p.setPen(QPen(c, 1.2)); p.setBrush(Qt.NoBrush); p.drawRect(QRectF(.3 * s, .3 * s, .4 * s, .4 * s))
    elif name == "restore":
        p.setPen(QPen(c, 1.2)); p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(.28 * s, .36 * s, .34 * s, .34 * s))
        p.drawPolyline(QPolygonF([P(.38, .36), P(.38, .28), P(.72, .28), P(.72, .62), P(.62, .62)]))
    elif name == "close":
        p.setPen(QPen(c, 1.3)); p.drawLine(P(.3, .3), P(.7, .7)); p.drawLine(P(.7, .3), P(.3, .7))
    elif name == "clear":
        p.setPen(pen); p.drawLine(P(.3, .3), P(.7, .7)); p.drawLine(P(.7, .3), P(.3, .7))
    elif name == "search":
        p.setPen(pen); p.setBrush(Qt.NoBrush)
        p.drawEllipse(QRectF(.18 * s, .18 * s, .45 * s, .45 * s)); p.drawLine(P(.56, .56), P(.82, .82))
    elif name == "gear":
        gp = QPen(c, 2.2); gp.setCapStyle(Qt.FlatCap); p.setPen(gp)
        for i in range(8):
            ang = i * math.pi / 4
            p.drawLine(P(.5 + .22 * math.cos(ang), .5 + .22 * math.sin(ang)),
                       P(.5 + .37 * math.cos(ang), .5 + .37 * math.sin(ang)))
        p.setPen(QPen(c, 1.6)); p.setBrush(Qt.NoBrush)
        p.drawEllipse(P(.5, .5), .23 * s, .23 * s); p.drawEllipse(P(.5, .5), .08 * s, .08 * s)
    p.end()
    pm.setDevicePixelRatio(scale)
    return QIcon(pm)


def star_polygon(cx, cy, r):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(QPointF(cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return QPolygonF(pts)


_STAR_CACHE = {}


def draw_stars(p, rect, rating):
    """Sterne als zwischengespeichertes Bild – die Titelliste zeichnet sie bei jedem Scroll-Schritt."""
    dpr = p.device().devicePixelRatioF() if p.device() else 1.0
    key = (int(rating or 0), T.accent.rgba(), T.ov(0.28).rgba(), dpr)
    pm = _STAR_CACHE.get(key)
    if pm is None:
        if len(_STAR_CACHE) > 64:
            _STAR_CACHE.clear()
        pm = QPixmap(int(92 * dpr), int(20 * dpr)); pm.setDevicePixelRatio(dpr); pm.fill(Qt.transparent)
        q = QPainter(pm)
        _draw_stars_raw(q, QRectF(0, 0, 92, 20), rating)
        q.end()
        _STAR_CACHE[key] = pm
    p.drawPixmap(QPointF(rect.left(), rect.center().y() + 0.5 - 10), pm)


def _draw_stars_raw(p, rect, rating):
    p.save()
    p.setRenderHint(QPainter.Antialiasing)
    cy = rect.center().y() + 0.5
    for i in range(5):
        poly = star_polygon(rect.left() + 10 + i * 16, cy, 6.5)
        if i < rating:
            p.setPen(Qt.NoPen); p.setBrush(T.accent)
        else:
            p.setPen(QPen(T.ov(0.28), 1)); p.setBrush(Qt.NoBrush)
        p.drawPolygon(poly)
    p.restore()


# ════════════════════════════════════════════════════════════════════════════
#  Kleine Widgets
# ════════════════════════════════════════════════════════════════════════════
class JumpSlider(QSlider):
    seeked = Signal(int)

    def __init__(self, *a):
        super().__init__(*a)
        self.setCursor(Qt.PointingHandCursor)       # Hand wie bei Links: man kann überall hinklicken
        self.sliderReleased.connect(lambda: self.seeked.emit(self.value()))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            opt = QStyleOptionSlider(); self.initStyleOption(opt)
            groove = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
            handle = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)
            pos = e.position().toPoint()
            if not handle.contains(pos):
                span = max(1, groove.width() - handle.width())
                v = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(),
                                                   pos.x() - groove.x() - handle.width() // 2, span)
                self.setValue(v); self.sliderMoved.emit(v); self.seeked.emit(v)
        super().mousePressEvent(e)


class WaveView(QWidget):
    """Kleine Pegel-Waveform unten links (wie die WMP12-Visualisierung bei Radio ohne Cover)."""
    clicked = Signal()

    def __init__(self, w=64, h=42):
        super().__init__()
        self.setFixedSize(w, h)
        self.levels = [0.0] * 40
        self.live = False
        self.phase = 0
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(tr_("Klicken: Cover / Waveform"))

    def push(self, lv):
        if lv is None:
            if self.live:
                self.live = False; self.levels = [0.0] * len(self.levels); self.update()
            return
        self.live = True
        self.phase += 1
        prev = self.levels[-1]
        self.levels = self.levels[1:] + [prev * 0.35 + lv * 0.65]
        self.update()

    def reset(self):
        self.live = False; self.levels = [0.0] * len(self.levels); self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()

    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(2, 4, -2, -4)
        mid = r.center().y()
        if not self.live or max(self.levels) < 0.01:
            # Ruhezustand: gestrichelte Linie wie im WMP
            pen = QPen(T.dim, 1, Qt.DashLine); pen.setDashPattern([2, 2])
            p.setPen(pen); p.drawLine(QPointF(r.left(), mid), QPointF(r.right(), mid))
            return
        n = len(self.levels)
        step = r.width() / (n - 1)
        amp = r.height() / 2
        top, bot = [], []
        for i, lv in enumerate(self.levels):
            # leichte Wellenform: Pegel moduliert eine Schwingung, damit es lebendig aussieht
            wob = 0.6 + 0.4 * math.sin((i + self.phase) * 1.9)
            a = max(0.5, lv * amp * wob)
            x = r.left() + i * step
            top.append(QPointF(x, mid - a)); bot.append(QPointF(x, mid + a))
        path = QPainterPath(top[0])
        for pt in top[1:]:
            path.lineTo(pt)
        for pt in reversed(bot):
            path.lineTo(pt)
        path.closeSubpath()
        g = QLinearGradient(r.left(), 0, r.right(), 0)
        c0 = T.acc(0.15); c1 = T.acc(0.95)
        g.setColorAt(0, c0); g.setColorAt(1, c1)
        p.setPen(Qt.NoPen); p.setBrush(g); p.drawPath(path)
        p.setPen(QPen(T.acc(0.9), 1)); p.drawLine(QPointF(r.left(), mid), QPointF(r.right(), mid))


class Splash(QWidget):
    """Ladebildschirm beim Start: Logo, Name, Version, Fortschrittsbalken und was gerade passiert."""

    def __init__(self):
        super().__init__(None, Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(460, 270)
        self.pct, self.shown_pct, self.text = 0, 0.0, tr_("Starte …")
        self.icon = app_icon().pixmap(84, 84)
        scr = QGuiApplication.primaryScreen().availableGeometry()
        self.move(scr.center() - self.rect().center())
        self._anim = QTimer(self, interval=16); self._anim.timeout.connect(self._tick)
        self._anim.start()

    def step(self, text, pct):
        self.text, self.pct = text, max(self.pct, pct)
        self.update()
        QApplication.processEvents()

    def _tick(self):
        if abs(self.pct - self.shown_pct) > 0.2:
            self.shown_pct += (self.pct - self.shown_pct) * 0.25
            self.update()

    def finish(self, win):
        self.step(tr_("Fertig"), 100)
        self._anim.stop()
        eff = QGraphicsOpacityEffect(self); self.setGraphicsEffect(eff)
        a = QPropertyAnimation(eff, b"opacity", self); a.setDuration(220)
        a.setStartValue(1.0); a.setEndValue(0.0)
        a.finished.connect(self.close)
        self._fade = a
        a.start()

    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        bg = mix(T.bg, QColor("#000000"), 0.15) if T.dark else QColor(T.bg)
        bg.setAlphaF(0.97)
        p.setPen(QPen(T.ov(0.12), 1)); p.setBrush(bg)
        p.drawRoundedRect(r, 14, 14)
        # Neon-Schimmer hinter dem Symbol
        g = QRadialGradient(QPointF(r.center().x(), 92), 90)
        g.setColorAt(0, T.acc(0.28)); g.setColorAt(1, T.acc(0.0))
        p.setPen(Qt.NoPen); p.setBrush(g); p.drawEllipse(QPointF(r.center().x(), 92), 90, 70)
        p.drawPixmap(int(r.center().x() - 42), 36, self.icon)
        f = QFont(self.font()); f.setPointSizeF(19); f.setWeight(QFont.DemiBold)
        p.setFont(f); p.setPen(T.fg)
        p.drawText(QRectF(0, 128, self.width(), 34), Qt.AlignCenter, APP_NAME)
        f2 = QFont(self.font()); f2.setPointSizeF(9.5)
        p.setFont(f2); p.setPen(T.dim)
        p.drawText(QRectF(0, 160, self.width(), 20), Qt.AlignCenter, tr_("Media Player  ·  Version {0}").format(APP_VERSION))
        # Fortschrittsbalken
        bar = QRectF(48, 206, self.width() - 96, 4)
        p.setBrush(T.ov(0.10)); p.drawRoundedRect(bar, 2, 2)
        done = QRectF(bar.left(), bar.top(), bar.width() * min(100, self.shown_pct) / 100, bar.height())
        if done.width() > 0:
            gl = QRectF(done).adjusted(-2, -3, 2, 3)
            p.setBrush(T.acc(0.25)); p.drawRoundedRect(gl, 4, 4)
            p.setBrush(T.accent); p.drawRoundedRect(done, 2, 2)
        p.setFont(f2); p.setPen(T.dim)
        p.drawText(QRectF(48, 220, self.width() - 96, 22), Qt.AlignLeft | Qt.AlignVCenter, self.text)
        p.drawText(QRectF(48, 220, self.width() - 96, 22), Qt.AlignRight | Qt.AlignVCenter, f"{int(round(self.shown_pct))} %")


_SPLASH = None


def splash_step(text, pct):
    if _SPLASH is not None:
        _SPLASH.step(text, pct)


class RootWidget(QWidget):
    """Fensterfläche: Hintergrund mit Deckkraft und runden Ecken selbst gezeichnet –
    so wirkt der Deckkraft-Regler sofort, ohne alle Stylesheets neu zu setzen."""

    def paintEvent(self, _e):
        p = QPainter(self)
        w = self.window()
        if getattr(w, "_fs", False):
            p.fillRect(self.rect(), QColor(0, 0, 0))
            return
        r = w.corner_radius() if hasattr(w, "corner_radius") else 0
        if not w.testAttribute(Qt.WA_TranslucentBackground):
            p.fillRect(self.rect(), T.bg)                 # deckendes Fenster (Windows mit Systemrahmen)
            return
        bg = T.bga()
        if not r:                                           # eckig (Windows, maximiert): schnelle Füllung
            p.fillRect(self.rect(), bg)
            return
        # Großteil ohne Kantenglättung füllen (schnell), nur die vier Ecken geglättet zeichnen
        W, H = self.width(), self.height()
        p.fillRect(QRect(r, 0, W - 2 * r, H), bg)
        p.fillRect(QRect(0, r, r, H - 2 * r), bg)
        p.fillRect(QRect(W - r, r, r, H - 2 * r), bg)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen); p.setBrush(bg)
        for cx, cy, a0 in ((r, r, 90), (W - r, r, 0), (W - r, H - r, 270), (r, H - r, 180)):
            p.drawPie(QRectF(cx - r, cy - r, 2 * r, 2 * r), a0 * 16, 90 * 16)
        p.setPen(QPen(T.ov(0.14), 1)); p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), r, r)


class MouseNavFilter(QObject):
    """Daumentasten der Maus (Zurück/Vor) überall im Fenster."""

    def __init__(self, win):
        super().__init__(win)
        self.win = win

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Enter:
            # Größenpfeil vom Fensterrand zurücksetzen, sobald die Maus ins Fensterinnere wandert
            # (das Innere erbt sonst den Pfeil, weil der Rand kein „Verlassen“ meldet)
            c = getattr(self.win, "central", None)
            if c is not None and obj is not c and c.testAttribute(Qt.WA_SetCursor) \
                    and isinstance(obj, QWidget) and obj.window() is self.win:
                c.unsetCursor()
            return False
        if ev.type() == QEvent.MouseButtonPress and ev.button() in (Qt.BackButton, Qt.ForwardButton) \
                and isinstance(obj, QWidget) and obj.window() is self.win:
            w = self.win
            if ev.button() == Qt.BackButton:
                w.exit_np_mode() if w.np_mode else w.go_back()
            else:
                w.go_forward()
            return True
        return False


class SmoothScroll(QObject):
    """Weiches Scrollen mit dem Mausrad: der Bildlauf gleitet zum Ziel statt zu springen."""

    def __init__(self, view, step=None):
        super().__init__(view)
        self.view = view
        self.bar = view.verticalScrollBar()
        self.step = step
        self.target = None
        self.anim = QPropertyAnimation(self.bar, b"value", self)
        self.anim.setDuration(220)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.finished.connect(lambda: setattr(self, "target", None))
        self.bar.sliderPressed.connect(self.anim.stop)
        view.viewport().installEventFilter(self)

    def eventFilter(self, obj, ev):
        if ev.type() != QEvent.Wheel or ev.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier):
            return False
        if not ev.pixelDelta().isNull() and ev.phase() != Qt.NoScrollPhase:
            return False                     # Touchpad: liefert schon weiche Pixelschritte
        dy = ev.angleDelta().y()
        if not dy or self.bar.maximum() <= 0:
            return False
        step = self.step or max(40, self.bar.singleStep()) * 3 // 2
        base = self.target if self.anim.state() == QPropertyAnimation.Running and self.target is not None \
            else self.bar.value()
        self.target = max(self.bar.minimum(), min(self.bar.maximum(), int(base - dy / 120 * step)))
        self.anim.stop()
        self.anim.setStartValue(self.bar.value()); self.anim.setEndValue(self.target)
        self.anim.start()
        ev.accept()
        return True


class DragBar(QFrame):
    """Leiste, an der sich ein rahmenloses Fenster verschieben lässt (Doppelklick = maximieren)."""

    def __init__(self, win):
        super().__init__()
        self.win = win

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.win.frameless and self.win.windowHandle():
            self.win.windowHandle().startSystemMove()
            return
        super().mousePressEvent(e)

    def mouseDoubleClickEvent(self, e):
        if self.win.frameless and e.button() == Qt.LeftButton:
            self.win.toggle_maximize()
            return
        super().mouseDoubleClickEvent(e)


class VideoView(QWidget):
    """„Wird gespielt“: zeigt das Video oder – bei Musik – groß das Cover vor leuchtendem Hintergrund."""
    double_clicked = Signal()
    activity = Signal()

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.sink = QVideoSink(self)
        self.sink.videoFrameChanged.connect(self._frame)
        self.sink.subtitleTextChanged.connect(self._embedded_sub)
        self.img = None
        self.has_video = False
        self.ended = False
        self.subtitle = ""
        self.setMouseTracking(True)
        self.setMinimumSize(200, 150)
        # Button oben rechts: zurück zur Bibliothek
        self.lib_btn = QToolButton(self); self.lib_btn.setObjectName("overlayBtn")
        self.lib_btn.setToolTip(tr_("Zur Bibliothek wechseln")); self.lib_btn.setIconSize(QSize(20, 20))
        self.lib_btn.clicked.connect(lambda: self.win.exit_np_mode())
        # Auswahl am Ende der Wiedergabe
        self.end_box = QFrame(self); self.end_box.setObjectName("endBox")
        ev = QVBoxLayout(self.end_box); ev.setContentsMargins(26, 22, 26, 22); ev.setSpacing(8)
        self.btn_replay = QToolButton(); self.btn_replay.setText(tr_("  Erneut wiedergeben"))
        self.btn_tolib = QToolButton(); self.btn_tolib.setText(tr_("  Zur Bibliothek wechseln"))
        for b in (self.btn_replay, self.btn_tolib):
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); b.setIconSize(QSize(18, 18)); b.setObjectName("endBtn")
            b.setCursor(Qt.PointingHandCursor)
            ev.addWidget(b)
        self.btn_replay.clicked.connect(lambda: self.win.replay())
        self.btn_tolib.clicked.connect(lambda: self.win.exit_np_mode())
        self.end_box.hide()
        self.refresh_icons()

    def refresh_icons(self):
        self.lib_btn.setIcon(make_icon("library", 20, "#ffffff"))
        self.btn_replay.setIcon(make_icon("replay", 18, "#ffffff"))
        self.btn_tolib.setIcon(make_icon("library", 18, "#ffffff"))

    def _frame(self, frame):
        if self.has_video and frame.isValid():
            self.img = frame.toImage()
            self.update()

    def _embedded_sub(self, text):
        if self.win.sub_mode == "embedded":
            self.subtitle = text
            self.update()

    def set_subtitle(self, text):
        if text != self.subtitle:
            self.subtitle = text
            self.update()

    def set_has_video(self, v):
        self.has_video = v
        if not v:
            self.img = None
        self.update()

    def show_end(self, on):
        self.ended = on
        self.end_box.setVisible(on)
        if on:
            self.end_box.adjustSize(); self._place(); self.end_box.raise_()
        self.update()

    def set_np_mode(self, on):
        self.lib_btn.setVisible(on)
        self._place()

    def resizeEvent(self, e):
        self._place()
        super().resizeEvent(e)

    def _place(self):
        self.lib_btn.adjustSize()
        self.lib_btn.move(self.width() - self.lib_btn.width() - 12, 12)
        self.end_box.adjustSize()
        self.end_box.move((self.width() - self.end_box.width()) // 2, (self.height() - self.end_box.height()) // 2)

    def _background(self, p, r):
        p.fillRect(r, QColor(0, 0, 0))
        acc = QColor(T.accent)
        band = QLinearGradient(0, r.top(), 0, r.bottom())
        for pos, a in ((0.0, 0.0), (0.38, 0.10), (0.55, 0.42), (0.68, 0.16), (1.0, 0.0)):
            c = mix(QColor("#000000"), acc, 0.55); c.setAlphaF(a); band.setColorAt(pos, c)
        p.fillRect(r, band)
        glow = QRadialGradient(QPointF(r.center().x(), r.height() * 0.55), max(r.width(), r.height()) * 0.55)
        c1 = QColor(acc); c1.setAlphaF(0.18); glow.setColorAt(0, c1)
        c2 = QColor(acc); c2.setAlphaF(0.0); glow.setColorAt(1, c2)
        p.fillRect(r, glow)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        if self.has_video and not self.ended:
            p.fillRect(r, QColor(0, 0, 0))
            if self.img is not None and not self.img.isNull():
                sz = self.img.size().scaled(r.size(), Qt.KeepAspectRatio)
                tgt = QRect(r.left() + (r.width() - sz.width()) // 2, r.top() + (r.height() - sz.height()) // 2,
                            sz.width(), sz.height())
                p.drawImage(tgt, self.img)
            self._paint_subtitle(p, r)
            return
        self._background(p, r)
        t = self.win.cur["t"] if self.win.cur else None
        S = int(max(110, min(r.height() * 0.42, r.width() * 0.4, 380)))
        cr = QRect(r.center().x() - S // 2, int(r.height() * 0.46) - S // 2, S, S)
        pm = self.win.covers.get(t["cover"] if t else "", S)
        if self.ended:
            p.setOpacity(0.25)
        p.setPen(Qt.NoPen); p.setBrush(QColor(0, 0, 0, 120)); p.drawRect(QRectF(cr).translated(0, 8))
        p.drawPixmap(cr, pm)
        # Spiegelung unter dem Cover
        refl = QImage(S, S // 3, QImage.Format_ARGB32_Premultiplied); refl.fill(Qt.transparent)
        rp = QPainter(refl)
        rp.drawImage(0, 0, pm.toImage().mirrored(False, True).copy(0, 0, S, S // 3))
        rp.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        g = QLinearGradient(0, 0, 0, S // 3); g.setColorAt(0, QColor(0, 0, 0, 90)); g.setColorAt(1, QColor(0, 0, 0, 0))
        rp.fillRect(refl.rect(), g); rp.end()
        p.drawImage(cr.left(), cr.bottom() + 3, refl)
        p.setOpacity(1.0)
        if self.ended:
            return
        f = QFont(self.font()); f.setPointSizeF(f.pointSizeF() + 5); f.setWeight(QFont.DemiBold)
        p.setFont(f); p.setPen(QColor("white"))
        ty = cr.bottom() + S // 3 + 6
        tr = QRect(r.left() + 20, ty, r.width() - 40, QFontMetrics(f).height() + 4)
        p.drawText(tr, Qt.AlignCenter, QFontMetrics(f).elidedText(t["title"] if t else tr_("Keine Wiedergabe"),
                                                                  Qt.ElideRight, tr.width()))
        if t:
            f2 = QFont(self.font()); f2.setPointSizeF(f2.pointSizeF() + 1)
            p.setFont(f2); p.setPen(QColor(255, 255, 255, 170))
            sub = self.win.stream_title if t.get("stream") and self.win.stream_title else f"{disp(t['artist'])} – {disp(t['album'])}"
            tr2 = QRect(tr.left(), tr.bottom() + 4, tr.width(), QFontMetrics(f2).height() + 4)
            p.drawText(tr2, Qt.AlignCenter, QFontMetrics(f2).elidedText(sub, Qt.ElideRight, tr2.width()))

    def _paint_subtitle(self, p, r):
        if not self.subtitle:
            return
        f = QFont(self.font()); f.setPointSizeF(max(12.0, r.height() / 32)); f.setWeight(QFont.DemiBold)
        p.setFont(f)
        fm = QFontMetrics(f)
        lines = self.subtitle.strip().split("\n")
        lh = fm.height()
        y = r.bottom() - 30 - lh * len(lines)
        for line in lines:
            rect = QRect(r.left() + 20, y, r.width() - 40, lh)
            path = QPainterPath()
            x = rect.center().x() - fm.horizontalAdvance(line) / 2
            path.addText(QPointF(x, y + fm.ascent()), f, line)
            p.setPen(QPen(QColor(0, 0, 0, 220), 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.setBrush(Qt.NoBrush)
            p.drawPath(path)
            p.setPen(Qt.NoPen); p.setBrush(QColor("white")); p.drawPath(path)
            y += lh

    def mousePressEvent(self, e):
        self.activity.emit()
        self._press = e.position() if e.button() == Qt.LeftButton else None
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._press = None
        super().mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, e):
        self._press = None
        if e.button() == Qt.LeftButton:
            self.double_clicked.emit()

    def mouseMoveEvent(self, e):
        self.activity.emit()
        # ohne Titelleiste (Video): Fenster durch Ziehen im Bild verschieben
        press = getattr(self, "_press", None)
        if (press is not None and e.buttons() & Qt.LeftButton and getattr(self.win, "_winbox_on", False)
                and (e.position() - press).manhattanLength() > 6 and self.win.windowHandle()):
            self._press = None
            self.win.windowHandle().startSystemMove()
            return
        super().mouseMoveEvent(e)


class MiniPlayer(QWidget):
    """Kleiner Player, der über anderen Fenstern liegt."""

    def __init__(self, win):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.win = win
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(tr_("{0} – Mini-Player").format(APP_NAME))
        self.setFixedSize(420, 100)
        lay = QHBoxLayout(self); lay.setContentsMargins(10, 10, 10, 10); lay.setSpacing(12)
        self.cover = QLabel(); self.cover.setFixedSize(80, 80)
        mid = QVBoxLayout(); mid.setSpacing(2)
        self.title = QLabel(); self.title.setObjectName("miniTitle"); self.title.setTextFormat(Qt.PlainText)
        self.artist = QLabel(); self.artist.setObjectName("miniDim"); self.artist.setTextFormat(Qt.PlainText)
        self.seek = JumpSlider(Qt.Horizontal); self.seek.setObjectName("seek")
        self.seek.seeked.connect(lambda v: self.win._user_seek(v))
        btns = QHBoxLayout(); btns.setSpacing(2)
        self.b_prev = QToolButton(); self.b_prev.clicked.connect(win.prev_track)
        self.play = PlayButton(size=34); self.play.clicked.connect(win.toggle_play)
        self.b_next = QToolButton(); self.b_next.clicked.connect(win.next_track)
        self.b_full = QToolButton(); self.b_full.setToolTip(tr_("Zurück zur Vollansicht")); self.b_full.clicked.connect(win.leave_mini)
        for b in (self.b_prev, self.b_next, self.b_full):
            b.setIconSize(QSize(18, 18))
        btns.addWidget(self.b_prev); btns.addWidget(self.play); btns.addWidget(self.b_next); btns.addStretch()
        btns.addWidget(self.b_full)
        mid.addWidget(self.title); mid.addWidget(self.artist); mid.addWidget(self.seek); mid.addLayout(btns)
        lay.addWidget(self.cover); lay.addLayout(mid, 1)
        self.refresh_style()

    def refresh_style(self):
        self.b_prev.setIcon(make_icon("prev", 18)); self.b_next.setIcon(make_icon("next", 18))
        self.b_full.setIcon(make_icon("nowplaying", 16))
        self.setStyleSheet(f"""
            QLabel#miniTitle {{ color: {css(T.fg)}; font-weight: 600; }}
            QLabel#miniDim {{ color: {css(T.dim)}; }}
            QToolButton {{ background: transparent; border: none; border-radius: 4px; padding: 3px; }}
            QToolButton:hover {{ background: {css(T.ov(0.1))}; }}
        """ + common_rules())
        self.update()

    def refresh(self):
        w = self.win
        t = w.cur["t"] if w.cur else None
        fm = self.title.fontMetrics()
        self.title.setText(fm.elidedText(t["title"] if t else tr_("Keine Wiedergabe"), Qt.ElideRight, 290))
        sub = (w.stream_title or tr_("Internetradio")) if t and t.get("stream") else (f"{disp(t['artist'])} – {disp(t['album'])}" if t else "")
        self.artist.setText(self.artist.fontMetrics().elidedText(sub, Qt.ElideRight, 290))
        self.cover.setPixmap(w.covers.get(t["cover"] if t else "", 80))
        self.play.set_playing(w.player.playbackState() == QMediaPlayer.PlayingState)
        self.seek.setRange(0, w.player.duration()); self.seek.setEnabled(w.player.duration() > 0)

    def set_pos(self, pos):
        if not self.seek.isSliderDown():
            self.seek.setValue(pos)

    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        c = QColor(T.solid); c.setAlphaF(max(0.85, T.alpha))
        p.setPen(QPen(T.ov(0.16), 1)); p.setBrush(c)
        p.drawRoundedRect(QRectF(self.rect()).adjusted(.5, .5, -.5, -.5), 8, 8)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.windowHandle():
            self.windowHandle().startSystemMove()

    def mouseDoubleClickEvent(self, e):
        self.win.leave_mini()


NAV_ICON, NAV_KIND, NAV_COUNT = Qt.UserRole + 10, Qt.UserRole + 11, Qt.UserRole + 12
AUTO_LISTS = OrderedDict([("favs", tr_("Lieblingstitel")), ("top", tr_("Meistgespielt")), ("new", tr_("Zuletzt hinzugefügt"))])


# id: (Standardname, Symbol, Art)
NAV_DEF = OrderedDict([
    ("auto:recent", (tr_("Zuletzt gespielt"), "clock", "item")),
    ("artists", (tr_("Interpret"), "person", "item")),
    ("albums", (tr_("Album"), "disc", "item")),
    ("genres", (tr_("Genre"), "tag", "item")),
    ("songs", (tr_("Titel@nav"), "note", "item")),
    ("autohead", (tr_("Automatische Listen"), "auto", "header")),
    ("auto:favs", (tr_("Lieblingstitel"), "auto", "item")),
    ("auto:top", (tr_("Meistgespielt"), "auto", "item")),
    ("auto:new", (tr_("Zuletzt hinzugefügt"), "auto", "item")),
    ("playlists", (tr_("Wiedergabelisten"), "list", "header")),
    ("radio", (tr_("Internetradio"), "radio", "item")),
    ("check", (tr_("Bibliothek prüfen"), "check", "item")),
    ("jellyfin", (tr_("Jellyfin"), "server", "header")),
    ("playing", (tr_("Wird gespielt"), "nowplaying", "item")),
    ("queue", (tr_("Wiedergabeliste"), "queue", "item")),
])
DEFAULT_NAV = ["auto:recent", "artists", "albums", "genres", "songs", "sep", "autohead", "auto:favs", "auto:top",
               "auto:new", "sep", "playlists", "sep", "jellyfin", "sep", "radio", "playing", "check", "sep", "queue"]


def default_nav_layout():
    return [{"id": i, "show": True} for i in DEFAULT_NAV]


class NavDelegate(QStyledItemDelegate):
    """Navigationsleiste: Symbole, Abschnitte, Punkte, Trennlinien, abgerundete Markierung."""

    HEIGHTS = {"sep": 13, "header": 32, "child": 28, "item": 32}

    def __init__(self, win, parent=None):
        super().__init__(parent)
        self.win = win
        self._icons = {}

    def icon(self, name, color):
        key = (name, color.name(QColor.HexArgb))
        if key not in self._icons:
            self._icons[key] = make_icon(name, 16, color).pixmap(16, 16)
        return self._icons[key]

    def sizeHint(self, opt, idx):
        return QSize(opt.rect.width(), self.HEIGHTS.get(idx.data(NAV_KIND) or "item", 32))

    def paint(self, p, opt, idx):
        kind = idx.data(NAV_KIND) or "item"
        r = opt.rect
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        if kind == "sep":
            p.setPen(QPen(T.ov(0.10), 1))
            y = r.center().y()
            p.drawLine(r.left() + 12, y, r.right() - 12, y)
            p.restore()
            return
        sel = bool(opt.state & QStyle.State_Selected) and kind != "header"
        hov = bool(opt.state & QStyle.State_MouseOver) and kind != "header"
        box = QRectF(r).adjusted(6, 2, -6, -2)
        if sel:
            p.setPen(Qt.NoPen)
            p.setBrush(T.acc(0.30) if T.navsel == 1 else T.ov(0.11))
            p.drawRoundedRect(box, 6, 6)
        elif hov:
            p.setPen(Qt.NoPen); p.setBrush(T.ov(0.05)); p.drawRoundedRect(box, 6, 6)
        text = idx.data(Qt.DisplayRole) or ""
        f = QFont(opt.font)
        if kind == "header":
            f.setWeight(QFont.DemiBold)
        elif sel:
            f.setWeight(QFont.Medium)
        p.setFont(f)
        fm = p.fontMetrics()
        x = r.left() + 16
        icon = idx.data(NAV_ICON)
        if kind == "child":
            p.setPen(Qt.NoPen)
            p.setBrush(T.accent if sel else T.ov(0.55))
            p.drawEllipse(QPointF(x + 7, r.center().y() + 0.5), 2.6, 2.6)
            x += 20
        elif icon:
            col = T.accent if sel else (T.ov(0.70) if kind == "header" else T.ov(0.80))
            p.drawPixmap(x, r.center().y() - 8, self.icon(icon, col))
            x += 26
        right = r.right() - 14
        count = idx.data(NAV_COUNT)
        if count:
            p.setPen(T.dim)
            cw = fm.horizontalAdvance(count)
            p.drawText(QRect(right - cw, r.top(), cw, r.height()), Qt.AlignRight | Qt.AlignVCenter, count)
            right -= cw + 10
        if kind == "header" and idx.data(Qt.UserRole) == "playlists":
            p.drawPixmap(right - 16, r.center().y() - 8, self.icon("plus", T.ov(0.55)))
            right -= 24
        p.setPen(T.fg if (sel or kind != "header") else mix(T.fg, T.dim, 0.35))
        tr = QRect(x, r.top(), max(10, right - x), r.height())
        p.drawText(tr, Qt.AlignLeft | Qt.AlignVCenter, fm.elidedText(text, Qt.ElideRight, tr.width()))
        p.restore()


class StationDialog(QDialog):
    def __init__(self, parent, name="", url=""):
        super().__init__(parent)
        self.setWindowTitle(tr_("Radiosender"))
        self.setMinimumWidth(480)
        form = QFormLayout(self); form.setContentsMargins(18, 18, 18, 14); form.setSpacing(10)
        self.e_name = QLineEdit(name); self.e_url = QLineEdit(url)
        self.e_url.setPlaceholderText(tr_("https://… (Stream-Adresse, .mp3/.aac/.m3u/.pls)"))
        form.addRow(tr_("Name"), self.e_name); form.addRow(tr_("Adresse"), self.e_url)
        hint = QLabel(tr_("Die Stream-Adresse steht meist auf der Website des Senders, viele Sender findest du auch "
                      "auf radio-browser.info."))
        hint.setObjectName("hint"); hint.setWordWrap(True)
        form.addRow("", hint)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText(tr_("Speichern")); bb.button(QDialogButtonBox.Cancel).setText(tr_("Abbrechen"))
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        form.addRow(bb)

    def values(self):
        url = self.e_url.text().strip()
        return (self.e_name.text().strip() or url), url


class RadioPage(QWidget):
    """Internetradio: eigene Senderliste."""

    def __init__(self, win):
        super().__init__()
        self.win = win
        lay = QVBoxLayout(self); lay.setContentsMargins(18, 14, 18, 10); lay.setSpacing(10)
        top = QHBoxLayout()
        badd = QPushButton(tr_("Sender hinzufügen…")); badd.clicked.connect(self.add_station)
        bimp = QPushButton(tr_("Aus Datei importieren (PLS/M3U)…")); bimp.clicked.connect(self.import_file)
        top.addWidget(badd); top.addWidget(bimp); top.addStretch()
        lay.addLayout(top)
        self.list = QListWidget(); self.list.setObjectName("radioList")
        self.list.setIconSize(QSize(44, 44))
        self.list.itemActivated.connect(lambda it: self.play(self.list.row(it)))
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._menu)
        lay.addWidget(self.list, 1)
        self.empty = QLabel(tr_("Noch keine Sender gespeichert.\nFüge einen über „Sender hinzufügen…“ hinzu "
                            "oder importiere eine .pls/.m3u-Datei."))
        self.empty.setObjectName("dim"); self.empty.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.empty)

    def stations(self):
        try:
            return json.loads(self.win.settings.value("radio/stations", "[]") or "[]")
        except ValueError:
            return []

    def _save(self, st):
        self.win.settings.setValue("radio/stations", json.dumps(st))
        self.reload()
        self.win._update_count() if self.win.state != "radio" else self.win.count_label.setText(tr_("{0} Sender").format(len(st)))

    def count(self):
        return len(self.stations())

    def reload(self):
        self.list.clear()
        icon = QIcon(CoverCache.placeholder(44))
        for stn in self.stations():
            key = album_key("Internetradio", stn["name"])
            pm = QPixmap(str(cover_path(key)))
            it = QListWidgetItem(QIcon(pm) if not pm.isNull() else icon, f"{stn['name']}\n{stn['url']}")
            it.setToolTip(stn["url"])
            self.list.addItem(it)
        self.empty.setVisible(self.list.count() == 0)

    def add_station(self):
        d = StationDialog(self)
        if d.exec() and d.values()[1]:
            name, url = d.values()
            self._save(self.stations() + [{"name": name, "url": url}])

    def edit_station(self, i):
        st = self.stations()
        d = StationDialog(self, st[i]["name"], st[i]["url"])
        if d.exec() and d.values()[1]:
            st[i] = dict(zip(("name", "url"), d.values()))
            self._save(st)

    def delete_station(self, i):
        st = self.stations()
        if QMessageBox.question(self, APP_NAME, tr_("Sender „{0}“ entfernen?").format(st[i]['name'])) == QMessageBox.Yes:
            del st[i]
            self._save(st)

    def import_file(self):
        fn, _ = QFileDialog.getOpenFileName(self, tr_("Senderliste importieren"), str(Path.home()),
                                            tr_("Wiedergabelisten (*.pls *.m3u *.m3u8)"))
        if not fn:
            return
        new = [{"name": title or Path(fn).stem, "url": url} for url, title in read_playlist_file(fn)
               if url.startswith(("http://", "https://"))]
        if not new:
            QMessageBox.information(self, APP_NAME, tr_("In der Datei wurden keine Stream-Adressen gefunden."))
            return
        self._save(self.stations() + new)

    def play(self, i):
        st = self.stations()
        if 0 <= i < len(st):
            self.win.play_tracks([stream_track(st[i]["url"], st[i]["name"])], 0)

    def _menu(self, pos):
        it = self.list.itemAt(pos)
        if not it:
            return
        i = self.list.row(it)
        m = QMenu(self.win)
        m.addAction(make_icon("play", 14), tr_("Wiedergeben"), lambda: self.play(i))
        m.addAction(tr_("Bearbeiten…"), lambda: self.edit_station(i))
        m.addAction(tr_("Entfernen"), lambda: self.delete_station(i))
        m.addSeparator()
        m.addAction(tr_("Adresse kopieren"), lambda: QApplication.clipboard().setText(self.stations()[i]["url"]))
        m.exec(self.list.viewport().mapToGlobal(pos))


class GripHandle(QSplitterHandle):
    """Gut greifbarer Teiler: feine Linie, beim Drüberfahren in der Akzentfarbe."""

    def __init__(self, o, parent):
        super().__init__(o, parent)
        self._hover = False
        self.setMouseTracking(True)

    def enterEvent(self, e):
        self._hover = True; self.update(); super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False; self.update(); super().leaveEvent(e)

    def paintEvent(self, _e):
        p = QPainter(self)
        x = self.width() // 2
        if self._hover or self.splitter().property("dragging"):
            p.fillRect(QRect(x - 1, 0, 3, self.height()), T.acc(0.75))
        elif not T.seamless:
            p.fillRect(QRect(x, 0, 1, self.height()), T.ov(0.08))
        p.end()

    def mousePressEvent(self, e):
        self.splitter().setProperty("dragging", True); self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.splitter().setProperty("dragging", False); self.update()
        super().mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, e):
        self.splitter().parent_win.reset_panel_sizes()


class GripSplitter(QSplitter):
    def __init__(self, win):
        super().__init__(Qt.Horizontal)
        self.parent_win = win
        self.setHandleWidth(7)
        self.setChildrenCollapsible(False)

    def createHandle(self):
        return GripHandle(self.orientation(), self)


class PlayButton(QAbstractButton):
    """Flacher, runder Play-Button in Akzentfarbe."""

    def __init__(self, parent=None, size=46):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.playing, self._hover = False, False

    def set_playing(self, v):
        self.playing = v; self.update()

    def enterEvent(self, e):
        self._hover = True; self.update(); super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False; self.update(); super().leaveEvent(e)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        c = QColor(T.accent)
        if self.isDown():
            c = c.darker(120)
        elif self._hover:
            c = c.lighter(115)
            p.setPen(Qt.NoPen); p.setBrush(T.acc(0.25)); p.drawEllipse(QRectF(self.rect()))
        p.setPen(Qt.NoPen); p.setBrush(c); p.drawEllipse(r)
        p.setBrush(T.on_acc)
        cx, cy = r.center().x(), r.center().y()
        k = r.width() / 42.0
        if self.playing:
            p.drawRect(QRectF(cx - 6.5 * k, cy - 7.5 * k, 4.5 * k, 15 * k)); p.drawRect(QRectF(cx + 2 * k, cy - 7.5 * k, 4.5 * k, 15 * k))
        else:
            p.drawPolygon(QPolygonF([QPointF(cx - 4.5 * k, cy - 8.5 * k), QPointF(cx + 8.5 * k, cy),
                                     QPointF(cx - 4.5 * k, cy + 8.5 * k)]))
        p.end()


# ════════════════════════════════════════════════════════════════════════════
#  Kachelansicht (Interpret / Album / Genre)
# ════════════════════════════════════════════════════════════════════════════
class GridView(QListView):
    """Kachelansicht. Tippen springt wie im WMP12 zum Eintrag und zeigt ihn oben statt am unteren Rand."""

    def keyboardSearch(self, text):
        before = self.currentIndex()
        super().keyboardSearch(text)
        idx = self.currentIndex()
        if not idx.isValid() or idx == before:
            return
        # Bei einem Buchstaben zur Überschrift dieses Buchstabens, damit der ganze Abschnitt sichtbar ist
        m = self.model()
        r = idx.row()
        if r > 0 and m.index(r - 1, 0).data(ROLE_KIND) == "sep":
            self.scrollTo(m.index(r - 1, 0), QAbstractItemView.PositionAtTop)
        else:
            self.scrollTo(idx, QAbstractItemView.PositionAtTop)


class TileDelegate(QStyledItemDelegate):
    STACK_M = 24            # Rand um das Cover für gedrehte Hintergrund-Cover und Schatten

    def __init__(self, covers, parent=None):
        super().__init__(parent)
        self.covers = covers
        self._stacks = OrderedDict()     # fertig gezeichnete Coverstapel – beim Scrollen nur noch ein drawPixmap
        self._tiles = OrderedDict()      # fertig gezeichnete Kacheln

    # Größe steht als SizeHintRole direkt im Modell (siehe render_grid) – Qt liest sie dann selbst,
    # ohne für jede Kachel Python aufzurufen. Das macht das Ziehen der Fenstergröße deutlich flüssiger.

    def _paint_sep(self, p, opt, idx):
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        r = opt.rect
        f = QFont(opt.font); f.setWeight(QFont.DemiBold)
        p.setFont(f)
        txt = idx.data(Qt.DisplayRole) or ""
        tw = p.fontMetrics().horizontalAdvance(txt)
        tr = QRect(r.left() + 12, r.top() + 10, tw + 2, r.height() - 12)
        p.setPen(T.accent)
        p.drawText(tr, Qt.AlignLeft | Qt.AlignVCenter, txt)
        y = tr.center().y() + 1
        p.setPen(QPen(T.ov(0.14), 1))
        p.drawLine(tr.right() + 10, y, r.right() - 12, y)
        p.restore()

    def _stack(self, kind, keys, dpr):
        """Coverstapel als Bild aus dem Cache; None, solange noch Cover im Hintergrund laden."""
        keys = tuple(keys[:5]) if kind in ("artist", "genre") else tuple(keys[:1])
        ck = (keys, round(dpr * 100), T.accent.name(), self.covers.gen)
        pm = self._stacks.get(ck)
        if pm is not None:
            self._stacks.move_to_end(ck)
            return pm
        pms = [self.covers.peek(k, ART) for k in keys]
        if any(x is None for x in pms):
            return None
        M = self.STACK_M
        pm = QPixmap(round((ART + 2 * M) * dpr), round((ART + 2 * M) * dpr))
        pm.setDevicePixelRatio(dpr); pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
        cr = QRect(M, M, ART, ART)
        if len(pms) > 1:
            # Aufgefächerter Stapel wie in WMP12: hintere Cover leicht gedreht
            angles = [-9, 8, -16, 14][:min(4, len(pms) - 1)]
            c = QPointF(cr.center()) + QPointF(0.5, 0.5)
            for i in reversed(range(len(angles))):
                p.save()
                p.translate(c); p.rotate(angles[i]); p.translate(-c)
                self._cover(p, cr, pms[i + 1], dim=0.25 + 0.08 * i)
                p.restore()
        self._cover(p, cr, pms[0])
        p.end()
        self._stacks[ck] = pm
        while len(self._stacks) > 700:
            self._stacks.popitem(last=False)
        return pm

    def _cover(self, p, rect, key, dim=0.0, shadow=True):
        p.setPen(Qt.NoPen)
        if shadow:
            p.setBrush(QColor(0, 0, 0, 80)); p.drawRect(QRectF(rect).translated(2, 3))
        p.drawPixmap(rect, key if isinstance(key, QPixmap) else self.covers.get(key, rect.width()))
        if dim:
            p.fillRect(rect, QColor(0, 0, 0, int(255 * dim)))
        p.setPen(QPen(QColor(255, 255, 255, 50), 1)); p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5))

    @staticmethod
    def _wrap2(fm, text, width):
        """Bricht einen Namen auf höchstens zwei Zeilen um (zweite Zeile mit „…“)."""
        if fm.horizontalAdvance(text) <= width:
            return [text]
        words, line = text.split(), ""
        for i, w in enumerate(words):
            test = (line + " " + w).strip()
            if fm.horizontalAdvance(test) > width and line:
                rest = " ".join(words[i:])
                return [line, fm.elidedText(rest, Qt.ElideRight, width)]
            line = test
        return [fm.elidedText(text, Qt.ElideRight, width)]

    def paint(self, p, opt, idx):
        if idx.data(ROLE_KIND) == "sep":
            self._paint_sep(p, opt, idx)
            return
        p.save()
        p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
        r = opt.rect.adjusted(3, 3, -3, -3)
        sel, hov = bool(opt.state & QStyle.State_Selected), bool(opt.state & QStyle.State_MouseOver)
        if sel or hov:
            p.setPen(QPen(T.acc(0.6), 1) if sel else Qt.NoPen)
            p.setBrush(T.acc(0.22) if sel else T.ov(0.06))
            p.drawRoundedRect(QRectF(r).adjusted(.5, .5, -.5, -.5), 4, 4)
        kind, keys = idx.data(ROLE_KIND), idx.data(ROLE_COVERS) or [""]
        dpr = p.device().devicePixelRatioF() if p.device() else 1.0
        # Ganze Kachel (Coverstapel, Texte, Sterne) als fertiges Bild – beim Scrollen und beim
        # Ziehen der Fenstergröße wird dann nur noch kopiert statt neu gesetzt.
        text, subs, rating = idx.data(Qt.DisplayRole) or "", tuple(idx.data(ROLE_SUB) or ()), idx.data(ROLE_RATING) or 0
        tk = (kind, tuple(keys[:5]), text, subs, rating, r.width(), r.height(), round(dpr * 100), opt.font.key(),
              T.fg.name(), T.dim.name(), T.accent.name(), self.covers.gen)
        tile = self._tiles.get(tk)
        if tile is None and self._stack(kind, keys, dpr) is not None:
            tile = QPixmap(round(r.width() * dpr), round(r.height() * dpr))
            tile.setDevicePixelRatio(dpr); tile.fill(Qt.transparent)
            q = QPainter(tile)
            q.setRenderHint(QPainter.Antialiasing); q.setRenderHint(QPainter.SmoothPixmapTransform)
            self._paint_content(q, QRect(0, 0, r.width(), r.height()), opt, idx, kind, keys, dpr)
            q.end()
            self._tiles[tk] = tile
            while len(self._tiles) > 600:
                self._tiles.popitem(last=False)
        elif tile is not None:
            self._tiles.move_to_end(tk)
        if tile is not None:
            p.drawPixmap(r.topLeft(), tile)
        else:
            self._paint_content(p, r, opt, idx, kind, keys, dpr)
        p.restore()

    def _paint_content(self, p, r, opt, idx, kind, keys, dpr):
        cr = QRect(r.left() + 16, r.top() + (r.height() - ART) // 2, ART, ART)
        stack = self._stack(kind, keys, dpr)
        if stack is not None:
            p.drawPixmap(cr.topLeft() - QPoint(self.STACK_M, self.STACK_M), stack)
        else:                                            # lädt noch – ruhige Fläche statt Ruckeln
            p.setPen(Qt.NoPen); p.setBrush(T.ov(0.07)); p.drawRect(cr)
        if keys[0].startswith("jf-"):                    # vom Jellyfin-Server: kleines Wolken-Zeichen
            br = QRectF(cr.right() - 22, cr.bottom() - 20, 20, 17)
            p.setPen(Qt.NoPen); p.setBrush(QColor(0, 0, 0, 140)); p.drawRoundedRect(br, 4, 4)
            if getattr(self, "_cloud", None) is None:
                self._cloud = make_icon("cloud", 16, QColor("white")).pixmap(16, 16)
            p.drawPixmap(br.adjusted(2, 0, -2, 0).toRect(), self._cloud)
        # Texte rechts neben dem Cover
        tx = cr.right() + 22
        tw = r.right() - tx - 6
        f = QFont(opt.font); f.setWeight(QFont.DemiBold)
        fm = QFontMetrics(f)
        lh = fm.height() + 1
        y = cr.top() - 2
        p.setFont(f); p.setPen(T.fg)
        for line in self._wrap2(fm, idx.data(Qt.DisplayRole) or "", tw):
            p.drawText(QRect(tx, y, tw, lh), Qt.AlignLeft | Qt.AlignVCenter, line)
            y += lh
        f2 = QFont(opt.font)
        fm2 = QFontMetrics(f2)
        p.setFont(f2); p.setPen(T.dim)
        for line in idx.data(ROLE_SUB) or []:
            if y + lh > r.bottom():
                break
            p.drawText(QRect(tx, y, tw, lh), Qt.AlignLeft | Qt.AlignVCenter, fm2.elidedText(line, Qt.ElideRight, tw))
            y += lh
        rating = idx.data(ROLE_RATING) or 0
        if rating and y + lh <= r.bottom() + 2:
            p.setRenderHint(QPainter.Antialiasing)
            for i in range(5):
                poly = star_polygon(tx + 6 + i * 13, y + lh / 2, 5.2)
                fill = max(0.0, min(1.0, rating - i))
                p.setPen(QPen(T.ov(0.3), 0.8)); p.setBrush(Qt.NoBrush); p.drawPolygon(poly)
                if fill > 0:
                    p.save()
                    p.setClipRect(QRectF(tx + 6 + i * 13 - 6, y, 12 * fill, lh))
                    p.setPen(Qt.NoPen); p.setBrush(T.accent); p.drawPolygon(poly)
                    p.restore()


# ════════════════════════════════════════════════════════════════════════════
#  Titelliste im WMP12-Stil (gruppiert nach Album, mit Cover)
# ════════════════════════════════════════════════════════════════════════════
L_, R_ = Qt.AlignLeft | Qt.AlignVCenter, Qt.AlignRight | Qt.AlignVCenter
# key, Überschrift, Standardbreite, Ausrichtung, standardmäßig sichtbar
COLUMNS = [
    ("cover", tr_("Album"), 300, L_, True),
    ("track", tr_("Nr."), 44, R_, True),
    ("title", tr_("Titel"), 280, L_, True),
    ("length", tr_("Länge"), 60, R_, True),
    ("rating", tr_("Bewertung"), 96, L_, True),
    ("artist", tr_("Mitwirkender Interpret"), 190, L_, True),
    ("albumartist", tr_("Albuminterpret"), 170, L_, False),
    ("album", tr_("Albumtitel"), 180, L_, False),
    ("composer", tr_("Komponist"), 150, L_, False),
    ("year", tr_("Jahr"), 55, L_, False),
    ("genre", tr_("Genre"), 120, L_, True),
    ("size", tr_("Größe"), 75, R_, False),
    ("plays", tr_("Wiedergabeanzahl"), 120, R_, False),
    ("type", tr_("Typ"), 50, L_, False),
    ("bitrate", tr_("Bitrate"), 85, R_, False),
    ("disc", tr_("CD"), 40, R_, False),
    ("path", tr_("Dateipfad"), 320, L_, False),
]
COL = {c[0]: i for i, c in enumerate(COLUMNS)}


class TrackModel(QAbstractItemModel):
    """Flache Liste: Kopfzeile pro Album, Titelzeilen, Füllzeilen (damit das Cover ganz sichtbar ist)."""

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.rows = []      # (art, album, track, k, gruppe, pos)
        self._bold = None
        self.tracks = []
        self.groups = []    # (erste, letzte Titelzeile)
        self.flat = False
        self.orig = []      # bei Wiedergabelisten: Position in der Liste
        self.block_h = None   # Höhe des Albumblocks in px (Cover schrumpft mit der Spalte, Infos ggf. darunter)
        self._src_groups = []

    def set_flat(self, tracks, orig=None):
        """Ungruppierte Liste (sortiert oder Wiedergabeliste)."""
        self.beginResetModel()
        self.flat = True
        la, ja = self.win.local_lib.albums, self.win.jf_lib.albums
        self.rows = [("track", (ja if t.get("remote") else la).get(t.get("akey") or t["cover"]) or {"key": t["cover"], "title": t["album"],
                                                           "artist": t["albumartist"], "year": t.get("year", ""),
                                                           "genre": t.get("genre", "")}, t, 0, -1, i)
                     for i, t in enumerate(tracks)]
        self.tracks, self.groups = list(tracks), []
        self.orig = list(orig) if orig is not None else list(range(len(tracks)))
        self.endResetModel()

    def set_groups(self, groups):
        self.beginResetModel()
        self.flat = False
        rows, tracks, gr = [], [], []
        self._src_groups = groups
        min_rows = math.ceil((self.block_h or (T.cover + 14)) / ROWH)
        for g, (a, tl) in enumerate(groups):
            rows.append(("head", a, None, 0, g, -1))
            first = len(rows)
            for k, t in enumerate(tl):
                rows.append(("track", a, t, k, g, len(tracks)))
                tracks.append(t)
            gr.append((first, len(rows) - 1))
            for k in range(len(tl), max(min_rows, len(tl))):
                rows.append(("pad", a, None, k, g, -1))
        self.rows, self.tracks, self.groups = rows, tracks, gr
        self.endResetModel()

    def refresh(self):
        if self.rows:
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.rows) - 1, len(COLUMNS) - 1))

    def index(self, row, col, parent=QModelIndex()):
        if parent.isValid() or not (0 <= row < len(self.rows)) or not (0 <= col < len(COLUMNS)):
            return QModelIndex()
        return self.createIndex(row, col)

    def parent(self, _idx=QModelIndex()):
        return QModelIndex()

    def hasChildren(self, parent=QModelIndex()):
        return not parent.isValid() and bool(self.rows)

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, _parent=QModelIndex()):
        return len(COLUMNS)

    def headerData(self, section, orient, role=Qt.DisplayRole):
        if orient == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return COLUMNS[section][1]
            if role == Qt.TextAlignmentRole:
                return COLUMNS[section][3]
        return None

    EDITABLE = {"title", "artist", "albumartist", "album", "composer", "year", "genre", "track", "disc"}

    # ItemNeverHasChildren: QTreeView fragt dann beim Layout nicht jede Zeile nach Kindern (große Bibliotheken)
    _F_ON = Qt.ItemIsEnabled | Qt.ItemNeverHasChildren
    _F_SEL = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemNeverHasChildren
    _F_EDIT = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemNeverHasChildren
    _EDIT_COLS = frozenset(i for i, c in enumerate(COLUMNS) if c[0] in {"title", "artist", "albumartist", "album", "composer", "year", "genre", "track", "disc"})

    def flags(self, idx):
        if idx.isValid():
            r = self.rows[idx.row()]
            if r[0] == "track":
                t = r[2]
                if idx.column() in self._EDIT_COLS and not (t.get("stream") or t.get("missing") or t.get("remote")):
                    return self._F_EDIT
                return self._F_SEL
        return self._F_ON

    def setData(self, idx, value, role=Qt.EditRole):
        if role != Qt.EditRole or not idx.isValid():
            return False
        key = COLUMNS[idx.column()][0]
        row = self.rows[idx.row()]
        if row[0] != "track" or key not in self.EDITABLE:
            return False
        view = self.win.tracks
        sel_rows = sorted({i.row() for i in view.selectionModel().selectedIndexes()})
        targets = [row[2]]
        if key not in ("title", "track") and idx.row() in sel_rows and len(sel_rows) > 1:
            targets = [self.rows[r][2] for r in sel_rows if self.rows[r][0] == "track"]
        QTimer.singleShot(0, lambda: self.win.edit_tags(targets, key, str(value)))
        return True

    def text(self, t, key):
        st = self.win.stats
        if key == "track":
            return str(t.get("track") or "")
        if key == "length":
            return fmt_time(t.get("length"))
        if key == "size":
            return fmt_size(t.get("size"))
        if key == "plays":
            return str(st.plays(t["path"]))
        if key == "bitrate":
            return f"{t['bitrate']} kBit/s" if t.get("bitrate") else ""
        if key in ("rating", "cover"):
            return ""
        return disp(str(t.get(key, "") or ""))

    _ROLES = {int(Qt.DisplayRole), int(Qt.EditRole), int(Qt.TextAlignmentRole), int(Qt.ForegroundRole),
              int(Qt.FontRole), int(Qt.ToolTipRole)}

    def data(self, idx, role=Qt.DisplayRole):
        if int(role) not in self._ROLES or not idx.isValid():   # schnell raus: Qt fragt viele Rollen ab
            return None
        row = self.rows[idx.row()]
        if row[0] != "track":
            return None
        t = row[2]
        key = COLUMNS[idx.column()][0]
        if role == Qt.DisplayRole:
            return self.text(t, key)
        if role == Qt.EditRole:
            v = t.get(key, "")
            return "" if v in (0, None) else str(v)
        if role == Qt.TextAlignmentRole:
            return COLUMNS[idx.column()][3]
        if role in (Qt.ForegroundRole, Qt.FontRole):
            if self.win.cur is None or self.win.cur["t"] is not t:
                return None
            if role == Qt.ForegroundRole:
                return T.accent
            if self._bold is None:
                self._bold = QFont(self.win.tracks.font()); self._bold.setBold(True)
            return self._bold
        if role == Qt.ToolTipRole and key in ("path", "title"):
            return t["path"] if key == "path" else t["title"]
        return None


class TrackDelegate(QStyledItemDelegate):
    def __init__(self, win, parent=None):
        super().__init__(parent)
        self.win = win
        self._blocks = OrderedDict()     # Album-Block (Cover + Infos) einmal zeichnen, beim Scrollen nur ausschneiden

    def sizeHint(self, opt, idx):
        return QSize(super().sizeHint(opt, idx).width(), ROWH)

    def paint(self, p, opt, idx):
        m = idx.model()
        kind, a, t, k, _g, _pos = m.rows[idx.row()]
        key = COLUMNS[idx.column()][0]
        if kind == "head":
            if idx.column() == 0:
                self._paint_head(p, opt.rect, a, opt.font)
            return
        if key == "cover":
            if m.flat:
                self._bg(p, opt, t, idx)
                r = opt.rect
                cs = r.height() - 6
                p.save(); p.setRenderHint(QPainter.SmoothPixmapTransform)
                p.drawPixmap(QRect(r.left() + 6, r.top() + 3, cs, cs), self.win.covers.get(a["key"], cs))
                p.setPen(T.fg); p.setFont(opt.font)
                tr = QRect(r.left() + cs + 14, r.top(), r.width() - cs - 18, r.height())
                p.drawText(tr, Qt.AlignLeft | Qt.AlignVCenter, p.fontMetrics().elidedText(a["title"], Qt.ElideRight, tr.width()))
                p.restore()
                return
            self._paint_cover_slice(p, opt.rect, a, k, opt.font)
            return
        if kind == "pad":
            return
        if key == "rating":
            self._bg(p, opt, t, idx)
            draw_stars(p, opt.rect, self.win.stats.rating(t["path"]))
            return
        # Normale Textzelle – selbst gezeichnet (deutlich schneller als der Stylesheet-Weg, wichtig fürs Scrollen)
        cur = self._bg(p, opt, t, idx)
        txt = m.text(t, key)
        if txt:
            if cur:
                if self._bold is None or self._bold.pointSizeF() != opt.font.pointSizeF():
                    self._bold = QFont(opt.font); self._bold.setWeight(QFont.DemiBold)
                p.setFont(self._bold)
            else:
                p.setFont(opt.font)
            p.setPen(T.accent if cur and not opt.state & QStyle.State_Selected else T.fg if not t.get("missing") else T.dim)
            tr = opt.rect.adjusted(6, 0, -6, 0)
            p.drawText(tr, int(COLUMNS[idx.column()][3]) | int(Qt.AlignVCenter),
                       p.fontMetrics().elidedText(txt, Qt.ElideRight, tr.width()))

    _bold = None

    def _bg(self, p, opt, t, idx):
        """Zellhintergrund: Auswahl, Hover und der gerade laufende Titel (deutlich hervorgehoben)."""
        cur = self.win.cur is not None and self.win.cur["t"] is t
        r = opt.rect
        if opt.state & QStyle.State_Selected:
            p.fillRect(r, T.acc(0.34 if cur else 0.28))
        elif cur:
            p.fillRect(r, T.acc(0.12))
        elif opt.state & QStyle.State_MouseOver:
            p.fillRect(r, T.ov(0.06))
        if cur:
            view = self.win.tracks
            hh = view.header()
            first = -1
            for v in range(0 if idx.model().flat else 1, hh.count()):
                li = hh.logicalIndex(v)
                if not hh.isSectionHidden(li):
                    first = li
                    break
            if idx.column() == first:                       # Akzentbalken am Zeilenanfang
                p.fillRect(QRect(r.left(), r.top() + 3, 3, r.height() - 6), T.accent)
        return cur

    def _paint_head(self, p, r, a, font):
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        f = QFont(font); f.setWeight(QFont.DemiBold)
        p.setFont(f)
        txt = a["title"]
        tw = min(p.fontMetrics().horizontalAdvance(txt), r.width() - 60)
        txt = p.fontMetrics().elidedText(txt, Qt.ElideRight, tw + 1)
        tr = QRect(r.left() + 10, r.top() + 4, tw + 4, r.height() - 4)
        p.setPen(T.accent)
        p.drawText(tr, Qt.AlignLeft | Qt.AlignVCenter, txt)
        y = tr.center().y() + 1
        p.setPen(QPen(T.ov(0.12), 1))
        p.drawLine(tr.right() + 10, y, r.right() - 8, y)
        p.restore()

    def _paint_cover_slice(self, p, rect, a, k, font):
        """Zeichnet den Teil des Album-Blocks (Cover + Infos), der in diese Zeile fällt."""
        dpr = p.device().devicePixelRatioF() if p.device() else 1.0
        W, H = rect.width(), rect.height()
        S, beside, bh = album_block(W)
        bh = max(bh, S + 14, 4 * 20 + 8) + H
        ck = (a["key"], W, H, round(dpr * 100), font.key(), self.win.covers.gen, a["title"], a["artist"], a["genre"], a["year"], a.get("edition"))
        pm = self._blocks.get(ck)
        if pm is None:
            cov = self.win.covers.peek(a["key"], S)
            if cov is None:                              # Cover lädt noch: ohne Cache zeichnen, Platzhalterfläche
                p.save(); p.setClipRect(rect); p.translate(rect.left(), rect.top() - k * H)
                self._draw_block(p, W, S, beside, a, font, None)
                p.restore()
                return
            pm = QPixmap(max(1, round(W * dpr)), max(1, round(bh * dpr)))
            pm.setDevicePixelRatio(dpr); pm.fill(Qt.transparent)
            q = QPainter(pm)
            self._draw_block(q, W, S, beside, a, font, cov)
            q.end()
            self._blocks[ck] = pm
            while len(self._blocks) > 160:
                self._blocks.popitem(last=False)
        src = QRectF(0, k * H * dpr, W * dpr, H * dpr)
        if src.top() < pm.height():
            p.drawPixmap(QRectF(rect), pm, src)

    def _draw_block(self, p, W, S, beside, a, font, cov):
        p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
        cr = QRect(10, 6, S, S)
        p.setPen(Qt.NoPen); p.setBrush(QColor(0, 0, 0, 60)); p.drawRect(QRectF(cr).translated(2, 2))
        if cov is not None:
            p.drawPixmap(cr, cov)
        else:
            p.setBrush(T.ov(0.07)); p.drawRect(cr)
        p.setPen(QPen(T.ov(0.12), 1)); p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(cr).adjusted(.5, .5, -.5, -.5))
        if beside:
            tx, ty, tw, lh = cr.right() + 14, 4, W - cr.right() - 20, 20
        else:                                         # schmale Spalte: Infos unter das Cover
            tx, ty, tw, lh = cr.left(), cr.bottom() + 6, W - cr.left() - 6, 18
        if tw > 30:
            f = QFont(font)
            fb = QFont(f); fb.setWeight(QFont.DemiBold)
            lines = [(disp(a["title"]), fb, T.fg), (disp(a["artist"]), f, T.fg),
                     (disp(a["genre"]) or tr_("Unbekanntes Genre"), f, T.dim),
                     ((a["year"] or tr_("Unbekanntes Jahr")) + (f" · {a['edition']}" if a.get("edition") else ""), f, T.dim)]
            for i, (txt, fnt, col) in enumerate(lines):
                p.setFont(fnt); p.setPen(col)
                lr = QRect(tx, ty + i * lh, tw, lh)
                p.drawText(lr, Qt.AlignLeft | Qt.AlignVCenter, QFontMetrics(fnt).elidedText(txt, Qt.ElideRight, tw))

    def editorEvent(self, event, model, opt, idx):
        if (COLUMNS[idx.column()][0] == "rating" and event.type() == QEvent.MouseButtonRelease
                and model.rows[idx.row()][0] == "track"):
            t = model.rows[idx.row()][2]
            x = event.position().x() - opt.rect.left() - 2
            n = max(0, min(5, int(x // 16) + 1)) if x >= 0 else 0
            self.win.set_rating([t], 0 if n == self.win.stats.rating(t["path"]) else n)
            return True
        return super().editorEvent(event, model, opt, idx)


def cover_size_for(col_width):
    return int(max(40, min(T.cover, col_width - 20)))


def album_block(col_width):
    """Covergröße, ob die Albuminfos daneben oder darunter stehen, und die Höhe des ganzen Blocks."""
    S = cover_size_for(col_width)
    beside = col_width - S - 30 >= 110
    return S, beside, (S + 14 if beside else S + 14 + 4 * 18 + 4)


class TrackView(QTreeView):
    play_album = Signal(object)

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setItemsExpandable(False)
        # kein Fokusrahmen über die ganze Zeile (sah aus wie eine hängengebliebene Markierung)
        self.setAllColumnsShowFocus(False)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setMouseTracking(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(ROWH * 2)
        self.setEditTriggers(QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked)
        self.setItemDelegate(TrackDelegate(win, self))
        hh = self.header()
        hh.setSectionsMovable(True)
        hh.setStretchLastSection(False)
        hh.setMinimumSectionSize(30)
        hh.setContextMenuPolicy(Qt.CustomContextMenu)
        hh.customContextMenuRequested.connect(self._header_menu)
        hh.setSectionsClickable(True)
        hh.sectionClicked.connect(lambda c: self.win.sort_by(c))
        hh.sectionMoved.connect(self._keep_cover_first)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(False)
        self._drop_row = -1

    # ── Cover per Drag & Drop ändern (wie im WMP12) ───────────────────────
    def _album_at(self, pos):
        idx = self.indexAt(pos)
        if not idx.isValid():
            return None
        row = self.model().rows[idx.row()]
        a = row[1]
        return a if isinstance(a, dict) and a.get("tracks") else None

    def dragEnterEvent(self, e):
        if mime_has_image(e.mimeData()):
            e.acceptProposedAction()
            return
        e.ignore()

    def dragMoveEvent(self, e):
        if mime_has_image(e.mimeData()) and self._album_at(e.position().toPoint()):
            e.acceptProposedAction()
            return
        e.ignore()

    def dropEvent(self, e):
        a = self._album_at(e.position().toPoint())
        data = image_from_mime(e.mimeData()) if a else None
        if a and data:
            e.acceptProposedAction()
            self.win.set_album_cover(a, data)
            return
        e.ignore()

    def setup_columns(self, settings):
        hh = self.header()
        state = settings.value("trackview/header")
        if not (state and hh.restoreState(state)):
            for i, (_k, _t, w, _al, vis) in enumerate(COLUMNS):
                hh.resizeSection(i, w)
                hh.setSectionHidden(i, not vis)
        hh.setSectionHidden(0, False)
        self._keep_cover_first()

    def _keep_cover_first(self, *_):
        hh = self.header()
        if hh.visualIndex(0) != 0:
            hh.moveSection(hh.visualIndex(0), 0)

    def _header_menu(self, pos):
        hh = self.header()
        m = QMenu(self)
        m.addSection(tr_("Spalten auswählen"))
        for i, (_k, title, *_r) in enumerate(COLUMNS):
            if i == 0:
                continue
            a = m.addAction(title)
            a.setCheckable(True)
            a.setChecked(not hh.isSectionHidden(i))
            a.toggled.connect(lambda on, i=i: self._toggle_col(i, on))
        m.addSeparator()
        m.addAction(tr_("Standardspalten wiederherstellen"), self._reset_cols)
        m.exec(hh.mapToGlobal(pos))

    def _toggle_col(self, i, on):
        hh = self.header()
        hh.setSectionHidden(i, not on)
        if on and hh.sectionSize(i) < 30:
            hh.resizeSection(i, COLUMNS[i][2])
        self.win.settings.setValue("trackview/header", hh.saveState())

    def _reset_cols(self):
        hh = self.header()
        for i, (_k, _t, w, _al, vis) in enumerate(COLUMNS):
            hh.moveSection(hh.visualIndex(i), i)
            hh.resizeSection(i, w if i else T.cover + 170)
            hh.setSectionHidden(i, not vis)
        self.win.settings.setValue("trackview/header", hh.saveState())

    def apply_spans(self):
        """Album-Überschriften zeichnet drawRow über die ganze Zeilenbreite selbst. Echte Qt-Spans
        (setFirstColumnSpanned) sind bei großen Bibliotheken sehr langsam – daher keine."""
        return

    def drawRow(self, p, opt, idx):
        # Füllzeilen unter dem Cover und Album-Überschriften: keine Hover-/Auswahl-/Fokusfläche
        m = self.model()
        kind = m.rows[idx.row()][0] if not m.flat and 0 <= idx.row() < len(m.rows) else None
        if kind in ("pad", "head"):
            i0 = m.index(idx.row(), 0)
            o = QStyleOptionViewItem(opt)
            if kind == "pad":
                o.rect = QRect(self.columnViewportPosition(0), opt.rect.top(), self.columnWidth(0), opt.rect.height())
            o.state &= ~(QStyle.State_Selected | QStyle.State_MouseOver | QStyle.State_HasFocus)
            self.itemDelegate().paint(p, o, i0)
            return
        if kind == "track":
            # Hover- und Auswahlfläche nur über den Titelspalten, nicht über dem Albumcover-Block
            ci = COL.get("cover", 0)
            if not self.header().isSectionHidden(ci):
                x, cw = self.columnViewportPosition(ci), self.columnWidth(ci)
                cover = QRect(x, opt.rect.top(), cw, opt.rect.height())
                p.save()
                p.setClipRegion(QRegion(opt.rect) - QRegion(cover))
                super().drawRow(p, opt, idx)
                p.restore()
                o = QStyleOptionViewItem(opt)
                o.rect = cover
                o.state &= ~(QStyle.State_Selected | QStyle.State_MouseOver | QStyle.State_HasFocus)
                self.itemDelegate().paint(p, o, m.index(idx.row(), ci))
                return
        super().drawRow(p, opt, idx)

    def _group_at(self, idx):
        if idx.isValid() and idx.column() == 0 and not self.model().flat:
            row = self.model().rows[idx.row()]
            if row[0] in ("track", "pad"):
                return row
        return None

    def mousePressEvent(self, e):
        row = self._group_at(self.indexAt(e.position().toPoint()))
        if row and e.button() in (Qt.LeftButton, Qt.RightButton):
            first, last = self.model().groups[row[4]]
            if last >= first:
                m = self.model()
                sel = QItemSelection(m.index(first, 0), m.index(last, len(COLUMNS) - 1))
                self.selectionModel().select(sel, QItemSelectionModel.ClearAndSelect)
                self.selectionModel().setCurrentIndex(m.index(first, 1), QItemSelectionModel.NoUpdate)
            if e.button() == Qt.RightButton:
                super().mousePressEvent(e)
            return
        super().mousePressEvent(e)

    def mouseDoubleClickEvent(self, e):
        row = self._group_at(self.indexAt(e.position().toPoint()))
        if row:
            self.play_album.emit(row[1])
            return
        super().mouseDoubleClickEvent(e)

    def selected_tracks(self):
        m = self.model()
        rows = sorted({i.row() for i in self.selectionModel().selectedIndexes()})
        return [m.rows[r][2] for r in rows if m.rows[r][0] == "track"]


# ════════════════════════════════════════════════════════════════════════════
#  Wiedergabeliste
# ════════════════════════════════════════════════════════════════════════════
class QueueDelegate(QStyledItemDelegate):
    def __init__(self, win, parent=None):
        super().__init__(parent)
        self.win = win

    def sizeHint(self, opt, _idx):
        return QSize(opt.rect.width(), 44)

    def paint(self, p, opt, idx):
        e = self.win.entry_of(idx.data(Qt.UserRole))
        if e is None:
            return
        p.save()
        t, r = e["t"], opt.rect
        cur = e is self.win.cur
        if opt.state & QStyle.State_Selected:
            p.fillRect(r, T.acc(0.28))
        elif opt.state & QStyle.State_MouseOver:
            p.fillRect(r, T.ov(0.06))
        if cur:
            p.fillRect(QRect(r.left(), r.top() + 6, 3, r.height() - 12), T.accent)
        f = QFont(opt.font); f.setBold(cur)
        tr = QRect(r.left() + 12, r.top() + 5, r.width() - 66, 18)
        p.setFont(f); p.setPen(T.accent if cur else T.fg)
        p.drawText(tr, L_, QFontMetrics(f).elidedText(t["title"], Qt.ElideRight, tr.width()))
        f2 = QFont(opt.font); f2.setPointSizeF(max(7.0, f2.pointSizeF() - 1))
        p.setFont(f2); p.setPen(T.dim)
        ar = tr.translated(0, 18)
        p.drawText(ar, L_, QFontMetrics(f2).elidedText(disp(t["artist"]), Qt.ElideRight, ar.width()))
        p.drawText(QRect(r.right() - 54, r.top() + 5, 44, 18), R_, fmt_time(t["length"]))
        p.restore()


# ════════════════════════════════════════════════════════════════════════════
#  Einstellungsdialog „Darstellung“
# ════════════════════════════════════════════════════════════════════════════
class ThemePage(QWidget):
    """Reiter „Darstellung“ – Änderungen werden sofort als Vorschau übernommen."""

    def __init__(self, win, theme):
        super().__init__()
        self.win = win
        self.t = dict(theme)
        form = QFormLayout(self)
        form.setSpacing(12)
        form.setContentsMargins(16, 16, 16, 16)
        self.acc_row, self.acc_btns = self._swatches(ACCENTS, "accent")
        form.addRow(tr_("Akzentfarbe"), self.acc_row)
        self.bg_row, self.bg_btns = self._swatches(BACKGROUNDS, "bg")
        form.addRow(tr_("Hintergrund"), self.bg_row)
        orow = QHBoxLayout()
        self.op = QSlider(Qt.Horizontal); self.op.setRange(35, 100); self.op.setValue(self.t["opacity"])
        self.op_lbl = QLabel(f"{self.t['opacity']} %"); self.op_lbl.setFixedWidth(44)
        self.op.valueChanged.connect(self._opacity)
        orow.addWidget(self.op, 1); orow.addWidget(self.op_lbl)
        form.addRow(tr_("Deckkraft"), orow)
        self.blur = QCheckBox(tr_("Hintergrund weichzeichnen") + ("" if IS_WIN else tr_(" (KDE Plasma)")))
        self.blur.setChecked(self.t["blur"])
        self.blur.toggled.connect(lambda v: self._set("blur", v))
        self.blur_hint = QLabel(); self.blur_hint.setWordWrap(True); self.blur_hint.setObjectName("hint")
        form.addRow("", self.blur)
        form.addRow("", self.blur_hint)
        self.cov = QComboBox()
        self.cov.addItems([n for n, _ in COVER_SIZES]); self.cov.setCurrentIndex(self.t["cover"])
        self.cov.currentIndexChanged.connect(lambda i: self._set("cover", i))
        form.addRow(tr_("Covergröße in Titellisten"), self.cov)
        self.navsel = QComboBox(); self.navsel.addItems([tr_("Neutral (grau)"), tr_("Akzentfarbe")])
        self.navsel.setCurrentIndex(int(self.t.get("navsel", 0)))
        self.navsel.currentIndexChanged.connect(lambda i: self._set("navsel", i))
        form.addRow(tr_("Markierung in der Navigation"), self.navsel)
        self.seam = QCheckBox(tr_("Eine durchgehende Fläche (keine Trennlinien zwischen den Bereichen)"))
        self.seam.setChecked(bool(self.t.get("seamless", True)))
        self.seam.toggled.connect(lambda v: self._set("seamless", v))
        form.addRow("", self.seam)
        self.cmdb = QCheckBox(tr_("Befehlsleiste anzeigen (Organisieren, Alle wiedergeben …)"))
        self.cmdb.setChecked(bool(self.t.get("cmdbar", True)))
        self.cmdb.toggled.connect(lambda v: self._set("cmdbar", v))
        form.addRow("", self.cmdb)
        self.frameless = QCheckBox(tr_("Eigene Fensterleiste (ohne Systemrahmen)"))
        self.frameless.setChecked(win.frameless)
        self.frameless.toggled.connect(lambda v: win.set_frameless(v))
        fh = QLabel(tr_("Verschieben über die obere Leiste, Doppelklick maximiert, Größe ändern an den Fensterrändern."))
        fh.setObjectName("hint"); fh.setWordWrap(True)
        form.addRow(tr_("Fenster"), self.frameless)
        form.addRow("", fh)
        # Sprache (wirkt nach einem Neustart)
        self.lang = QComboBox()
        for code, name in LANGUAGES:
            self.lang.addItem(tr_(name) if code == "auto" else name, code)
        cur = win.settings.value("ui/lang", "auto") or "auto"
        self.lang.setCurrentIndex(max(0, self.lang.findData(cur)))
        lrow = QHBoxLayout(); lrow.addWidget(self.lang, 1)
        self.lang_restart = QPushButton(tr_("Jetzt neu starten")); self.lang_restart.hide()
        self.lang_restart.clicked.connect(win.restart_app)
        lrow.addWidget(self.lang_restart)

        def lang_changed(_i):
            win.settings.setValue("ui/lang", self.lang.currentData())
            self.lang_restart.show()
            self.lang_hint.setText(tr_("Die neue Sprache gilt nach einem Neustart von NeoNote."))
        self.lang.currentIndexChanged.connect(lang_changed)
        form.addRow(tr_("Sprache"), lrow)
        self.lang_hint = QLabel(""); self.lang_hint.setObjectName("hint"); self.lang_hint.setWordWrap(True)
        form.addRow("", self.lang_hint)
        reset = QPushButton(tr_("Standardfarben"))
        reset.clicked.connect(self._defaults)
        form.addRow("", reset)
        self._sync()

    def _swatches(self, items, key):
        w = QWidget(); lay = QHBoxLayout(w); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(6)
        btns = []
        for name, col in items:
            b = QToolButton(); b.setFixedSize(26, 26); b.setToolTip(name); b.setProperty("col", col)
            b.clicked.connect(lambda _=False, c=col: self._set(key, c))
            lay.addWidget(b); btns.append(b)
        more = QToolButton(); more.setText("…"); more.setToolTip(tr_("Eigene Farbe wählen")); more.setFixedSize(26, 26)
        more.clicked.connect(lambda: self._pick(key))
        lay.addWidget(more); lay.addStretch()
        return w, btns

    def _pick(self, key):
        c = QColorDialog.getColor(QColor(self.t[key]), self, tr_("Farbe wählen"))
        if c.isValid():
            self._set(key, c.name())

    def _opacity(self, v):
        self.op_lbl.setText(f"{v} %")
        self.t["opacity"] = v
        T.update(self.t)                         # sofort: nur den Fensterhintergrund neu zeichnen
        self.win.theme_dict = dict(self.t)
        self.win.central.update()
        if not hasattr(self, "_op_timer"):
            self._op_timer = QTimer(self, singleShot=True, interval=350)
            self._op_timer.timeout.connect(lambda: self._set("opacity", self.t["opacity"]))
            self.op.sliderReleased.connect(self._op_timer.start)
        if not self.op.isSliderDown():
            self._op_timer.start()

    def _set(self, key, val):
        self.t[key] = val
        self.win.apply_theme(self.t)
        self._sync()

    def _defaults(self):
        self.t = dict(DEFAULT_THEME)
        for w in (self.op, self.cov, self.blur, self.navsel, self.seam, self.cmdb):
            w.blockSignals(True)
        self.op.setValue(self.t["opacity"]); self.cov.setCurrentIndex(self.t["cover"]); self.blur.setChecked(self.t["blur"])
        self.navsel.setCurrentIndex(self.t["navsel"])
        self.seam.setChecked(self.t["seamless"]); self.cmdb.setChecked(self.t["cmdbar"])
        for w in (self.op, self.cov, self.blur, self.navsel, self.seam, self.cmdb):
            w.blockSignals(False)
        self.op_lbl.setText(f"{self.t['opacity']} %")
        self.win.apply_theme(self.t)
        self._sync()

    def _sync(self):
        for btns, key in ((self.acc_btns, "accent"), (self.bg_btns, "bg")):
            for b in btns:
                col = b.property("col")
                on = col.lower() == str(self.t[key]).lower()
                ring = css(T.fg) if on else css(T.ov(0.15))
                b.setStyleSheet(f"QToolButton {{ background: {col}; border: 2px solid {ring}; border-radius: 13px; }}")
        if not self.t["blur"]:
            self.blur_hint.setText("")
        elif IS_WIN:
            self.blur_hint.setText(tr_("Aktiv. Wirkt, wenn die Deckkraft unter 100 % liegt und in Windows "
                                   "„Transparenzeffekte“ eingeschaltet sind."))
        elif QGuiApplication.platformName() == "xcb":
            self.blur_hint.setText(tr_("Aktiv. Wirkt, wenn die Deckkraft unter 100 % liegt und der KWin-Effekt "
                                   "„Unschärfe“ eingeschaltet ist."))
        else:
            self.blur_hint.setText(tr_("Wird beim nächsten Start des Players aktiviert (läuft dann über XWayland)."))


class SettingsDialog(QDialog):
    TAB_LIBRARY, TAB_LOOK, TAB_ONLINE, TAB_SYSTEM, TAB_NAV, TAB_JF = range(6)

    # ── Reiter Navigation ─────────────────────────────────────────────────
    def _fill_navlist(self, layout):
        self.navlist.blockSignals(True)
        self.navlist.clear()
        for e in layout:
            self.navlist.addItem(self._nav_item(e))
        self.navlist.blockSignals(False)

    def _nav_item(self, e):
        i = e["id"]
        if i == "sep":
            it = QListWidgetItem(tr_("──────────  Trennlinie"))
            it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            it.setForeground(T.dim)
        else:
            name, icon, _k = NAV_DEF[i]
            it = QListWidgetItem(make_icon(icon, 16), e.get("label") or name)
            it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked if e.get("show", True) else Qt.Unchecked)
            if e.get("label"):
                it.setToolTip(tr_("Ursprünglicher Name: {0}").format(name))
        it.setData(Qt.UserRole, json.dumps(e))
        return it

    def _layout_from_list(self):
        out = []
        for r in range(self.navlist.count()):
            it = self.navlist.item(r)
            e = json.loads(it.data(Qt.UserRole))
            if e["id"] != "sep":
                e["show"] = it.checkState() == Qt.Checked
            out.append(e)
        return out

    def _nav_preview(self):
        self.win.apply_nav_layout(self._layout_from_list(), save=False)

    def _nav_move(self, d):
        r = self.navlist.currentRow()
        if r < 0 or not (0 <= r + d < self.navlist.count()):
            return
        self.navlist.blockSignals(True)
        it = self.navlist.takeItem(r)
        self.navlist.insertItem(r + d, it)
        self.navlist.setCurrentRow(r + d)
        self.navlist.blockSignals(False)
        self._nav_preview()

    def _nav_rename(self):
        it = self.navlist.currentItem()
        if not it:
            return
        e = json.loads(it.data(Qt.UserRole))
        if e["id"] == "sep":
            return
        default = NAV_DEF[e["id"]][0]
        text, ok = QInputDialog.getText(self, tr_("Eintrag umbenennen"), tr_("Name (leer = „{0}“):").format(default),
                                        text=e.get("label") or default)
        if not ok:
            return
        text = text.strip()
        if text and text != default:
            e["label"] = text
        else:
            e.pop("label", None)
        e["show"] = it.checkState() == Qt.Checked
        self.navlist.blockSignals(True)
        r = self.navlist.row(it)
        self.navlist.takeItem(r); self.navlist.insertItem(r, self._nav_item(e)); self.navlist.setCurrentRow(r)
        self.navlist.blockSignals(False)
        self._nav_preview()

    def _nav_add_sep(self):
        r = self.navlist.currentRow()
        r = self.navlist.count() if r < 0 else r + 1
        self.navlist.blockSignals(True)
        self.navlist.insertItem(r, self._nav_item({"id": "sep"})); self.navlist.setCurrentRow(r)
        self.navlist.blockSignals(False)
        self._nav_preview()

    def _nav_remove_sep(self):
        it = self.navlist.currentItem()
        if it and json.loads(it.data(Qt.UserRole))["id"] == "sep":
            self.navlist.takeItem(self.navlist.row(it))
            self._nav_preview()

    def _nav_reset(self):
        self._fill_navlist(default_nav_layout())
        self._nav_preview()

    def __init__(self, win, tab=0):
        super().__init__(win)
        self.win = win
        self.setWindowTitle(tr_("Einstellungen"))
        self.setMinimumSize(760, 600)
        self.orig_theme = dict(win.theme_dict)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        self.tabs = QTabWidget()
        lay.addWidget(self.tabs, 1)

        # Bibliothek
        lib = QWidget(); lv = QVBoxLayout(lib); lv.setContentsMargins(16, 16, 16, 16); lv.setSpacing(10)
        lv.addWidget(QLabel(tr_("Diese Ordner (mit allen Unterordnern) gehören zu deiner Musikbibliothek:")))
        frow = QHBoxLayout()
        self.flist = QListWidget(); self.flist.addItems(win.folders())
        self.flist.setSelectionMode(QAbstractItemView.ExtendedSelection)
        fbtns = QVBoxLayout()
        badd = QPushButton(tr_("Hinzufügen…")); badd.clicked.connect(self._add_folder)
        self.brm = QPushButton(tr_("Entfernen")); self.brm.clicked.connect(self._remove_folders)
        fbtns.addWidget(badd); fbtns.addWidget(self.brm); fbtns.addStretch()
        frow.addWidget(self.flist, 1); frow.addLayout(fbtns)
        lv.addLayout(frow, 1)
        hint = QLabel(tr_("Beim Entfernen eines Ordners werden nur die Einträge aus der Bibliothek entfernt, "
                      "deine Dateien bleiben erhalten."))
        hint.setObjectName("hint"); hint.setWordWrap(True)
        lv.addWidget(hint)
        self.scan_start = QCheckBox(tr_("Beim Start automatisch nach neuen und geänderten Dateien suchen"))
        self.scan_start.setChecked(win.settings.value("library/scan_on_start", True, type=bool))
        lv.addWidget(self.scan_start)
        self.watch = QCheckBox(tr_("Musikordner überwachen (neue, geänderte und gelöschte Dateien automatisch übernehmen)"))
        self.watch.setChecked(win.settings.value("library/watch", True, type=bool))
        lv.addWidget(self.watch)
        self.add_opened = QCheckBox(tr_("Aus dem Dateimanager (z. B. %s) geöffnete Musik in die Bibliothek aufnehmen")
                                    % (tr_("Explorer") if IS_WIN else tr_("Dolphin")))
        self.add_opened.setChecked(win.settings.value("library/add_opened", False, type=bool))
        lv.addWidget(self.add_opened)
        ah = QLabel(tr_("Ist das Häkchen aus, werden geöffnete Dateien nur abgespielt. Videos werden nie in die "
                    "Musikbibliothek aufgenommen."))
        ah.setObjectName("hint"); ah.setWordWrap(True)
        lv.addWidget(ah)
        if win.local_lib.hidden:
            ub = QPushButton(tr_("Ausgeblendete Doppelte wieder einblenden ({0})").format(len(win.local_lib.hidden)))

            def unhide():
                win.local_lib.hidden.clear(); win.local_lib.save_hidden()
                ub.setEnabled(False); ub.setText(tr_("Wird beim nächsten Einlesen wieder aufgenommen"))
                win.rescan(full=True)
            ub.clicked.connect(unhide)
            lv.addWidget(ub, 0, Qt.AlignLeft)
        srow = QHBoxLayout()
        n_al = len(win.local_lib.albums)
        self.lib_info = QLabel(tr_("{0} Titel in {1} {2}").format(len(win.local_lib.tracks), n_al, tr_('Album@n') if n_al == 1 else tr_('Alben@n')))
        self.lib_info.setObjectName("hint")
        bscan = QPushButton(tr_("Komplett neu einlesen")); bscan.clicked.connect(self._scan_now)
        bscan.setToolTip(tr_("Liest alle Dateien neu ein, auch unveränderte"))
        srow.addWidget(self.lib_info); srow.addStretch(); srow.addWidget(bscan)
        lv.addLayout(srow)
        self.tabs.addTab(lib, tr_("Bibliothek"))

        # Darstellung
        self.theme = ThemePage(win, win.theme_dict)
        self.tabs.addTab(self.theme, tr_("Darstellung"))

        # Online
        on = QWidget(); ov = QVBoxLayout(on); ov.setContentsMargins(16, 16, 16, 16); ov.setSpacing(10)
        intro = QLabel(tr_("Fehlende Albuminformationen (Jahr, Genre, Titelnummern) und Cover lädt NeoNote von "
                       "<b>MusicBrainz</b> und dem <b>Cover Art Archive</b>. Beides ist kostenlos und ohne Anmeldung "
                       "nutzbar."))
        intro.setWordWrap(True)
        ov.addWidget(intro)
        ov.addSpacing(6)
        ov.addWidget(QLabel(tr_("<b>Gefundene Informationen speichern</b>")))
        self.o_tags = QCheckBox(tr_("Angaben in die Musikdateien schreiben (Tags)"))
        self.o_embed = QCheckBox(tr_("Cover in die Musikdateien einbetten"))
        self.o_folder = QCheckBox(tr_("Cover als „cover.jpg“ im Albumordner ablegen"))
        opts = win.online_opts()
        self.o_tags.setChecked(opts["write_tags"]); self.o_embed.setChecked(opts["embed_cover"])
        self.o_folder.setChecked(opts["folder_cover"])
        for w in (self.o_tags, self.o_embed, self.o_folder):
            ov.addWidget(w)
        ov.addSpacing(4)
        self.o_edit = QCheckBox(tr_("Von Hand bearbeitete Angaben (Titel, Interpret, Album …) in die Dateien schreiben"))
        self.o_edit.setChecked(win.settings.value("edit/write_files", True, type=bool))
        ov.addWidget(self.o_edit)
        oh = QLabel(tr_("Ist nichts davon ausgewählt, speichert NeoNote die Angaben nur in seiner eigenen Bibliothek. "
                    "Deine Dateien bleiben dann unverändert. Andere Programme sehen die Ergänzungen nur, wenn sie in "
                    "die Dateien geschrieben werden."))
        oh.setObjectName("hint"); oh.setWordWrap(True)
        ov.addWidget(oh)
        ov.addSpacing(6)
        brow = QHBoxLayout()
        bbatch = QPushButton(tr_("Jetzt für alle Alben suchen"))
        bbatch.clicked.connect(self._batch_now)
        bh = QLabel(tr_("Sucht nur bei Alben, denen Cover, Jahr oder Genre fehlen."))
        bh.setObjectName("hint"); bh.setWordWrap(True)
        brow.addWidget(bbatch); brow.addWidget(bh, 1)
        ov.addLayout(brow)
        ov.addStretch()
        self.tabs.addTab(on, tr_("Online-Informationen"))

        sysw = QWidget(); sv = QVBoxLayout(sysw); sv.setContentsMargins(16, 16, 16, 16); sv.setSpacing(10)
        sv.addWidget(QLabel(tr_("<b>Systemleiste</b>")))
        self.s_tray = QCheckBox(tr_("Symbol in der Systemleiste anzeigen"))
        self.s_tray.setChecked(win.settings.value("system/tray", True, type=bool))
        self.s_close = QCheckBox(tr_("Schließen-Button minimiert in die Systemleiste, statt den Player zu beenden"))
        self.s_close.setChecked(win.settings.value("system/close_to_tray", False, type=bool))
        self.s_tray.toggled.connect(lambda v: self.s_close.setEnabled(v))
        self.s_close.setEnabled(self.s_tray.isChecked())
        sv.addWidget(self.s_tray); sv.addWidget(self.s_close)
        th = QLabel(tr_("Klick auf das Symbol zeigt oder versteckt das Fenster, Mittelklick startet bzw. pausiert. "
                    "Über das Menü des Symbols kannst du den Player jederzeit ganz beenden."))
        th.setObjectName("hint"); th.setWordWrap(True); sv.addWidget(th)
        if IS_WIN:
            sv.addWidget(QLabel(tr_("<b>Standardplayer</b>")))
            db = QPushButton(tr_("NeoNote als Standardplayer festlegen …"))
            db.clicked.connect(win_open_default_apps)
            sv.addWidget(db, 0, Qt.AlignLeft)
            dh = QLabel(tr_("Öffnet die Windows-Einstellungen bei NeoNote. Dort oben auf „Als Standard festlegen“ "
                        "klicken – dann öffnen sich alle Musik- und Videodateien mit NeoNote."))
            dh.setObjectName("hint"); dh.setWordWrap(True); sv.addWidget(dh)
        sv.addWidget(QLabel(tr_("<b>Start</b>")))
        self.s_splash = QCheckBox(tr_("Ladebildschirm beim Start anzeigen"))
        self.s_splash.setChecked(win.settings.value("ui/splash", True, type=bool))
        sv.addWidget(self.s_splash)
        sv.addSpacing(8)
        sv.addWidget(QLabel(tr_("<b>Updates</b>")))
        ug = QGridLayout(); ug.setHorizontalSpacing(12); ug.setVerticalSpacing(6)
        ug.addWidget(QLabel(tr_("Nach neuen Versionen suchen")), 0, 0)
        self.s_ucheck = QComboBox()
        for key, label in (("start", tr_("Bei jedem Start")), ("daily", tr_("Einmal am Tag")),
                           ("weekly", tr_("Einmal pro Woche")), ("never", tr_("Nie (nur von Hand)"))):
            self.s_ucheck.addItem(label, key)
        self.s_ucheck.setCurrentIndex(max(0, self.s_ucheck.findData(win.settings.value("update/check", "daily"))))
        ug.addWidget(self.s_ucheck, 0, 1)
        self.s_umode = None
        if IS_WIN:
            ug.addWidget(QLabel(tr_("Wenn eine neue Version da ist")), 1, 0)
            self.s_umode = QComboBox()
            self.s_umode.addItem(tr_("Nur Bescheid geben"), "notify")
            self.s_umode.addItem(tr_("Herunterladen und beim Beenden installieren"), "auto")
            self.s_umode.setCurrentIndex(max(0, self.s_umode.findData(win.settings.value("update/mode", "notify"))))
            ug.addWidget(self.s_umode, 1, 1)
        ug.setColumnStretch(2, 1)
        sv.addLayout(ug)
        urow = QHBoxLayout()
        ubtn = QPushButton(tr_("Jetzt nach Updates suchen"))
        ulbl = QLabel(""); ulbl.setObjectName("hint"); ulbl.setWordWrap(True)
        ubtn.clicked.connect(lambda: win.check_updates(manual=True, report=ulbl.setText))
        urow.addWidget(ubtn); urow.addWidget(ulbl, 1); sv.addLayout(urow)
        uh = QLabel(tr_("NeoNote fragt dafür nur die Release-Seite des Projekts auf GitHub ab – es werden keine Daten übertragen.")
                    if IS_WIN or not installed_by_package() else
                    tr_("NeoNote zeigt neue Versionen nur an. Aktualisiert wird über die Paketverwaltung (z. B. „yay -Syu“ oder Discover)."))
        uh.setObjectName("hint"); uh.setWordWrap(True); sv.addWidget(uh)
        sv.addSpacing(8)
        sv.addWidget(QLabel(tr_("<b>Wiedergabe</b>")))
        self.s_mpv = QCheckBox(tr_("Musik und Internetradio über mpv abspielen (Equalizer, lückenlose Wiedergabe)"))
        self.s_mpv.setChecked(win.settings.value("audio/mpv", True, type=bool))
        self.s_gapless = QCheckBox(tr_("Lückenlose Wiedergabe (Gapless)"))
        self.s_gapless.setChecked(win.settings.value("audio/gapless", True, type=bool))
        sv.addWidget(self.s_mpv); sv.addWidget(self.s_gapless)
        self.s_nosleep = QCheckBox(tr_("Kein Standby, solange Musik oder ein Video läuft"))
        self.s_nosleep.setChecked(win.settings.value("system/no_sleep", True, type=bool))
        sv.addWidget(self.s_nosleep)
        dl = None
        if win.player.mp:
            pt = tr_("Status: mpv aktiv. Videos laufen weiter über Qt Multimedia.")
        elif mpv_available():
            pt = tr_("Status: mpv ist installiert, wird nach einem Neustart des Players genutzt.")
        elif IS_WIN:
            pt = (tr_("Status: mpv fehlt noch. NeoNote kann es einmalig herunterladen (ca. 30 MB, von GitHub). "
                  "Bis dahin laufen Equalizer und Gapless nicht, alles andere schon."))
            self.s_mpv.setEnabled(False); self.s_gapless.setEnabled(False)
            dl = QPushButton(tr_("mpv herunterladen…")); dl.clicked.connect(lambda: MpvDownloadDialog(win).exec())
        else:
            pt = (tr_("Status: mpv nicht gefunden. Installieren mit <code>sudo pacman -S mpv python-mpv</code>, "
                  "danach den Player neu starten. Bis dahin laufen Equalizer und Gapless nicht."))
            self.s_mpv.setEnabled(False); self.s_gapless.setEnabled(False)
        ph = QLabel(pt); ph.setObjectName("hint"); ph.setWordWrap(True); ph.setTextFormat(Qt.RichText)
        sv.addWidget(ph)
        if dl:
            sv.addWidget(dl, 0, Qt.AlignLeft)
        beq = QPushButton(tr_("Equalizer öffnen…")); beq.clicked.connect(win.open_equalizer)
        sv.addWidget(beq, 0, Qt.AlignLeft)
        sv.addSpacing(8)
        if IS_WIN:
            sv.addWidget(QLabel(tr_("<b>Windows-Mediensteuerung</b>")))
            self.s_mpris = QCheckBox(tr_("Mit der Windows-Mediensteuerung verbinden"))
            info = (tr_("Der Player erscheint dann in der Medienanzeige von Windows (Lautstärke-Einblendung, "
                    "Schnelleinstellungen, Sperrbildschirm), und die Medientasten der Tastatur funktionieren "
                    "auch, wenn das Fenster nicht aktiv ist. "))
        else:
            sv.addWidget(QLabel(tr_("<b>KDE-Mediensteuerung (MPRIS)</b>")))
            self.s_mpris = QCheckBox(tr_("Mit der KDE-Mediensteuerung verbinden"))
            info = (tr_("Der Player erscheint dann im Medien-Widget der Plasma-Leiste und auf dem Sperrbildschirm, "
                    "und die Medientasten der Tastatur funktionieren auch, wenn das Fenster nicht aktiv ist. "))
        self.s_mpris.setChecked(win.settings.value("system/mpris", True, type=bool))
        sv.addWidget(self.s_mpris)
        if IS_WIN:
            mt = info + (tr_("Status: aktiv.") if win.mpris else
                         tr_("Status: wird nach einem Neustart des Players aktiv.") if smtc_available() else
                         tr_("Status: auf diesem System nicht verfügbar."))
            if not smtc_available():
                self.s_mpris.setEnabled(False)
        elif jeepney_available():
            mt = info + (tr_("Status: aktiv.") if win.mpris else tr_("Status: wird nach einem Neustart des Players aktiv."))
        else:
            mt = info + (tr_("Dafür fehlt das Paket <b>python-jeepney</b>. Installieren mit: "
                  "<code>sudo pacman -S python-jeepney</code>, danach den Player neu starten."))
            self.s_mpris.setEnabled(False)
        mh = QLabel(mt); mh.setObjectName("hint"); mh.setWordWrap(True); mh.setTextFormat(Qt.RichText)
        sv.addWidget(mh)
        sv.addStretch()
        sysa = QScrollArea(); sysa.setWidgetResizable(True); sysa.setFrameShape(QFrame.NoFrame)
        sysa.setWidget(sysw); sysa.viewport().setAutoFillBackground(False); sysw.setAutoFillBackground(False)
        self.tabs.addTab(sysa, tr_("System"))

        navw = QWidget(); nv = QVBoxLayout(navw); nv.setContentsMargins(16, 16, 16, 16); nv.setSpacing(10)
        nh = QLabel(tr_("Häkchen = in der Leiste anzeigen. Die Reihenfolge änderst du per Ziehen oder mit den Pfeilen, "
                    "einen Namen per Doppelklick. Einträge direkt unter „Automatische Listen“ erscheinen als Unterpunkte."))
        nh.setObjectName("hint"); nh.setWordWrap(True)
        nv.addWidget(nh)
        row = QHBoxLayout()
        self.navlist = QListWidget(); self.navlist.setObjectName("navcfg")
        self.navlist.setDragDropMode(QAbstractItemView.InternalMove)
        self.navlist.setIconSize(QSize(16, 16))
        row.addWidget(self.navlist, 1)
        nb = QVBoxLayout(); nb.setSpacing(6)
        for text, slot in ((tr_("▲  Nach oben"), lambda: self._nav_move(-1)), (tr_("▼  Nach unten"), lambda: self._nav_move(1)),
                           (tr_("Umbenennen…"), self._nav_rename), (tr_("Trennlinie einfügen"), self._nav_add_sep),
                           (tr_("Trennlinie entfernen"), self._nav_remove_sep), (tr_("Standard"), self._nav_reset)):
            b = QPushButton(text); b.setAutoDefault(False); b.clicked.connect(slot); nb.addWidget(b)
        nb.addStretch()
        row.addLayout(nb)
        nv.addLayout(row, 1)
        self.tabs.addTab(navw, tr_("Navigation"))
        self.orig_nav = win.nav_layout()
        self._fill_navlist(self.orig_nav)
        self.navlist.itemChanged.connect(lambda _it: self._nav_preview())
        self.navlist.model().rowsMoved.connect(lambda *_: self._nav_preview())
        self.navlist.itemDoubleClicked.connect(lambda _it: self._nav_rename())
        self._build_jf_tab(win)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText(tr_("Übernehmen"))
        bb.button(QDialogButtonBox.Cancel).setText(tr_("Abbrechen"))
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        lay.addWidget(bb)
        self.tabs.setCurrentIndex(tab)

    def _folders(self):
        return [self.flist.item(i).text() for i in range(self.flist.count())]

    def _add_folder(self):
        d = QFileDialog.getExistingDirectory(self, tr_("Musikordner wählen"), str(Path.home()))
        if d and d not in self._folders():
            self.flist.addItem(d)

    def _remove_folders(self):
        for it in self.flist.selectedItems():
            self.flist.takeItem(self.flist.row(it))

    def _save(self):
        w = self.win
        changed = self._folders() != w.folders()
        w.settings.setValue("folders", self._folders())
        w.settings.setValue("library/scan_on_start", self.scan_start.isChecked())
        watch_changed = self.watch.isChecked() != w.settings.value("library/watch", True, type=bool)
        w.settings.setValue("library/watch", self.watch.isChecked())
        if watch_changed:
            QTimer.singleShot(0, lambda: w.rescan(quiet=True))
        w.settings.setValue("library/add_opened", self.add_opened.isChecked())
        w.settings.setValue("online/write_tags", self.o_tags.isChecked())
        w.settings.setValue("online/embed_cover", self.o_embed.isChecked())
        w.settings.setValue("online/folder_cover", self.o_folder.isChecked())
        w.settings.setValue("edit/write_files", self.o_edit.isChecked())
        w.settings.setValue("system/tray", self.s_tray.isChecked())
        w.settings.setValue("system/close_to_tray", self.s_close.isChecked())
        w.settings.setValue("system/mpris", self.s_mpris.isChecked())
        w.settings.setValue("ui/splash", self.s_splash.isChecked())
        w.settings.setValue("update/check", self.s_ucheck.currentData())
        if self.s_umode is not None:
            w.settings.setValue("update/mode", self.s_umode.currentData())
        w.settings.setValue("audio/mpv", self.s_mpv.isChecked())
        w.settings.setValue("audio/gapless", self.s_gapless.isChecked())
        w.settings.setValue("system/no_sleep", self.s_nosleep.isChecked())
        w.update_sleep_guard()
        w.apply_nav_layout(self._layout_from_list(), save=True)
        w._prepare_next()
        if getattr(w, "tray", None):
            w.tray.setVisible(self.s_tray.isChecked())
        w.save_theme(self.theme.t)
        w.settings.setValue("window/frameless", self.theme.frameless.isChecked())
        return changed

    def _scan_now(self):
        self._save()
        self.win.rescan(full=True)
        self.lib_info.setText(tr_("Wird eingelesen …"))

    def _batch_now(self):
        self.accept()
        self.win.start_batch()

    # ── Reiter Jellyfin ───────────────────────────────────────────────────
    def _build_jf_tab(self, win):
        st = win.settings
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(16, 16, 16, 16); v.setSpacing(10)
        v.addWidget(QLabel(tr_("<b>Jellyfin-Server</b>")))
        h = QLabel(tr_("Musik von deinem Jellyfin-Server (z. B. auf dem Raspberry Pi) erscheint links unter "
                   "„Jellyfin“ – mit denselben Ansichten wie deine eigene Bibliothek. NeoNote speichert dabei "
                   "nur ein Anmeldezeichen, nicht dein Passwort."))
        h.setObjectName("hint"); h.setWordWrap(True); v.addWidget(h)
        form = QFormLayout(); form.setSpacing(8)
        self.jf_url = QLineEdit(st.value("jf/url", "")); self.jf_url.setPlaceholderText("http://raspberrypi:8096")
        self.jf_user = QLineEdit(st.value("jf/user", ""))
        self.jf_pw = QLineEdit(); self.jf_pw.setEchoMode(QLineEdit.Password)
        self.jf_pw.setPlaceholderText(tr_("nur zum Verbinden nötig"))
        form.addRow(tr_("Adresse"), self.jf_url); form.addRow(tr_("Benutzer"), self.jf_user); form.addRow(tr_("Passwort"), self.jf_pw)
        self.jf_q = QComboBox()
        for k, label in Jellyfin.QUALITIES:
            self.jf_q.addItem(label, k)
        qi = max(0, self.jf_q.findData(st.value("jf/quality", "orig")))
        self.jf_q.setCurrentIndex(qi)
        form.addRow(tr_("Qualität beim Streamen"), self.jf_q)
        v.addLayout(form)
        row = QHBoxLayout()
        self.jf_btn = QPushButton(tr_("Verbinden")); self.jf_btn.clicked.connect(self._jf_connect)
        self.jf_out = QPushButton(tr_("Trennen")); self.jf_out.clicked.connect(self._jf_disconnect)
        self.jf_reload = QPushButton(tr_("Bibliothek neu laden")); self.jf_reload.clicked.connect(lambda: win.jf_refresh(quiet=False))
        row.addWidget(self.jf_btn); row.addWidget(self.jf_reload); row.addWidget(self.jf_out); row.addStretch()
        v.addLayout(row)
        self.jf_status = QLabel(""); self.jf_status.setWordWrap(True); self.jf_status.setTextFormat(Qt.PlainText)
        v.addWidget(self.jf_status)
        qh = QLabel(tr_("„Original“ spielt die Dateien unverändert (ideal im Heimnetz). Unterwegs, z. B. über "
                    "WireGuard, wandelt Jellyfin auf Wunsch in kleinere MP3s um. Mit Rechtsklick ▸ „Offline "
                    "speichern“ legst du Titel und Alben auf diesem Rechner ab."))
        qh.setObjectName("hint"); qh.setWordWrap(True); v.addWidget(qh)
        n_off = len(win.jf_lib.offline)
        self.jf_off = QPushButton(tr_("Alle Offline-Kopien löschen ({0})").format(n_off))
        self.jf_off.setEnabled(n_off > 0)
        self.jf_off.clicked.connect(lambda: (win.jf_drop_offline(win.jf_lib.tracks), self.jf_off.setEnabled(False)))
        v.addWidget(self.jf_off, 0, Qt.AlignLeft)
        v.addStretch()
        self.tabs.addTab(w, tr_("Jellyfin"))
        self._jf_update()

    def _jf_update(self, msg=None):
        win = self.win
        on = win.jf is not None
        self.jf_out.setEnabled(on); self.jf_reload.setEnabled(on)
        self.jf_btn.setText(tr_("Neu verbinden") if on else tr_("Verbinden"))
        if msg is not None:
            self.jf_status.setText(msg)
        elif on:
            n = len(win.jf_lib.tracks)
            self.jf_status.setText(tr_("✓ Verbunden als {0} mit {1} · {2} Titel").format(
                win.settings.value('jf/user', ''), win.settings.value('jf/server', 'Jellyfin'), fmt_int(n)))
        else:
            self.jf_status.setText(tr_("Nicht verbunden."))

    def _jf_connect(self):
        win = self.win
        url, user, pw = self.jf_url.text().strip().rstrip("/"), self.jf_user.text().strip(), self.jf_pw.text()
        if url and "://" not in url:
            url = "http://" + url
            self.jf_url.setText(url)
        if not url or not user:
            self._jf_update(tr_("Bitte Adresse und Benutzer eintragen."))
            return
        cli = Jellyfin(url, "", "", win.settings.value("jf/device_id", "") or "neonote", self.jf_q.currentData())
        self.jf_btn.setEnabled(False); self._jf_update(tr_("Verbinde …"))

        def ok(info):
            self.jf_btn.setEnabled(True)
            st = win.settings
            st.setValue("jf/url", url); st.setValue("jf/user", info["user"]); st.setValue("jf/token", cli.token)
            st.setValue("jf/user_id", cli.user_id); st.setValue("jf/server", info["server"])
            st.setValue("jf/quality", self.jf_q.currentData())
            self.jf_pw.clear()
            win._jf_setup()
            win.jf_refresh(quiet=False)
            self._jf_update(tr_("✓ Verbunden mit {0} (Jellyfin {1}). Die Bibliothek wird geladen …").format(info['server'], info['version']))

        def fail(msg):
            self.jf_btn.setEnabled(True)
            self._jf_update(f"✗ {msg}")
        win.run_job(lambda: cli.login(user, pw), ok, fail)

    def _jf_disconnect(self):
        win = self.win
        if win.jf:
            cli = win.jf
            win.run_job(cli.logout, lambda _r: None, lambda _m: None)
        for k in ("jf/token", "jf/user_id"):
            win.settings.remove(k)
        win._jf_setup()
        win.jf_lib.clear()
        if win.state.startswith("jf:"):
            win.navigate("artists")
        self._jf_update()

    def accept(self):
        if win_q := getattr(self, "jf_q", None):
            q = win_q.currentData()
            if q != self.win.settings.value("jf/quality", "orig"):
                self.win.settings.setValue("jf/quality", q)
                if self.win.jf:
                    self.win.jf.quality = q
        newly_writing = self.o_tags.isChecked() and not self.win.online_opts()["write_tags"]
        if self._save():
            QTimer.singleShot(0, self.win.rescan)
        super().accept()
        pending = {p: c for p, c in self.win.local_lib.overrides.items() if c}
        if newly_writing and pending:
            if QMessageBox.question(self.win, APP_NAME,
                                    tr_("Für {0} Titel gibt es Ergänzungen, die bisher nur in der Bibliothek gespeichert sind.\n\nSollen diese jetzt auch in die Musikdateien geschrieben werden?").format(len(pending))
                                    ) == QMessageBox.Yes:
                self.win.write_pending()

    def reject(self):
        self.win.apply_theme(self.orig_theme)
        self.win.apply_nav_layout(self.orig_nav, save=False)
        self.win.set_frameless(self.win.settings.value("window/frameless", True, type=bool))
        super().reject()


class LookupDialog(QDialog):
    """Albuminformationen bei MusicBrainz suchen und übernehmen."""

    def __init__(self, win, album):
        super().__init__(win)
        self.win, self.album = win, album
        self.gen, self.release, self.cover = 0, None, None
        self.closed = False
        self.setWindowTitle(tr_("Albuminformationen suchen – {0}").format(album['title']))
        self.resize(980, 600)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 12); lay.setSpacing(10)

        top = QHBoxLayout()
        self.e_album = QLineEdit(album["title"]); self.e_artist = QLineEdit(album["artist"])
        for w in (self.e_album, self.e_artist):
            w.returnPressed.connect(self.search)
        bs = QPushButton(tr_("Suchen")); bs.clicked.connect(self.search)
        top.addWidget(QLabel(tr_("Album"))); top.addWidget(self.e_album, 3)
        top.addWidget(QLabel(tr_("Interpret"))); top.addWidget(self.e_artist, 2); top.addWidget(bs)
        lay.addLayout(top)

        split = QSplitter(Qt.Horizontal)
        self.res = QTreeWidget()
        self.res.setHeaderLabels([tr_("Album"), tr_("Interpret"), tr_("Jahr"), tr_("Land"), tr_("Titel"), tr_("Format"), tr_("Label"), tr_("Treffer")])
        self.res.setRootIsDecorated(False); self.res.setAlternatingRowColors(True)
        hh = self.res.header()
        hh.setStretchLastSection(False)
        for c, wdt in ((0, 230), (1, 130), (2, 45), (3, 40), (4, 40), (5, 70), (7, 55)):
            hh.setSectionResizeMode(c, QHeaderView.Interactive); hh.resizeSection(c, wdt)
        hh.setSectionResizeMode(6, QHeaderView.Stretch)
        self.res.currentItemChanged.connect(lambda cur, _p: cur and self._select(cur))
        split.addWidget(self.res)

        right = QWidget(); rv = QVBoxLayout(right); rv.setContentsMargins(8, 0, 0, 0)
        self.cov = QLabel("—"); self.cov.setFixedSize(220, 220); self.cov.setAlignment(Qt.AlignCenter)
        self.cov.setObjectName("coverbox")
        self.info = QLabel(); self.info.setWordWrap(True)
        self.tl = QListWidget()
        rv.addWidget(self.cov, 0, Qt.AlignHCenter); rv.addWidget(self.info); rv.addWidget(self.tl, 1)
        right.setFixedWidth(280)
        split.addWidget(right)
        split.setStretchFactor(0, 1)
        lay.addWidget(split, 1)

        orow = QHBoxLayout()
        self.r_fill = QRadioButton(tr_("Nur fehlende Angaben ergänzen")); self.r_fill.setChecked(True)
        self.r_over = QRadioButton(tr_("Vorhandene Angaben überschreiben"))
        self.r_over.setToolTip(tr_("Titel, Jahr, Genre und Titelnummern werden durch die Angaben von MusicBrainz ersetzt."))
        has_cover = (cover_path(album['key'])).exists()
        self.c_cover = QCheckBox(tr_("Cover übernehmen") if not has_cover else tr_("Vorhandenes Cover ersetzen"))
        self.c_cover.setChecked(not has_cover)
        for w in (self.r_fill, self.r_over):
            w.toggled.connect(self._update_preview)
        self.c_cover.toggled.connect(self._update_preview)
        orow.addWidget(self.r_fill); orow.addWidget(self.r_over); orow.addSpacing(20); orow.addWidget(self.c_cover)
        orow.addStretch()
        lay.addLayout(orow)

        opts = win.online_opts()
        target = (tr_("Änderungen werden in die Musikdateien geschrieben.") if opts["write_tags"] else
                  tr_("Änderungen werden nur in der NeoNote-Bibliothek gespeichert (Einstellungen ▸ Online-Informationen)."))
        brow = QHBoxLayout()
        self.status = QLabel(); self.status.setObjectName("hint"); self.status.setWordWrap(True)
        tl = QLabel(target); tl.setObjectName("hint")
        sv = QVBoxLayout(); sv.addWidget(self.status); sv.addWidget(tl)
        self.bapply = QPushButton(tr_("Übernehmen")); self.bapply.setDefault(True); self.bapply.setEnabled(False)
        self.bapply.clicked.connect(self.apply)
        bc = QPushButton(tr_("Abbrechen")); bc.clicked.connect(self.reject)
        brow.addLayout(sv, 1); brow.addWidget(self.bapply); brow.addWidget(bc)
        lay.addLayout(brow)
        QTimer.singleShot(0, self.search)

    def _run(self, fn, ok):
        g = self.gen
        self.win.run_job(fn, lambda res: (not self.closed and g == self.gen) and ok(res),
                         lambda msg: (not self.closed and g == self.gen) and self._fail(msg))

    def _fail(self, msg):
        self.status.setText(msg)

    def search(self):
        self.gen += 1
        self.res.clear(); self.tl.clear(); self.info.setText(""); self.cov.setPixmap(QPixmap()); self.cov.setText("—")
        self.release = None; self.bapply.setEnabled(False)
        self.status.setText(tr_("Suche bei MusicBrainz …"))
        a, b = self.e_album.text().strip(), self.e_artist.text().strip()
        self._run(lambda: mb_search(a, b) or mb_search(a, b, fuzzy=True), self._results)

    def _results(self, results):
        n = len(self.album["tracks"])
        for r in results:
            it = QTreeWidgetItem([r["title"], r["artist"], r["year"], r["country"], str(r["tracks"]),
                                  r["format"], r["label"], f"{r['score']} %"])
            it.setData(0, Qt.UserRole, r["id"]); it.setData(1, Qt.UserRole, r["rgid"])
            if r["tracks"] == n:
                f = it.font(4); f.setBold(True); it.setFont(4, f)
            self.res.addTopLevelItem(it)
        if not results:
            self.status.setText(tr_("Keine Treffer. Ändere Album- oder Interpretennamen und suche erneut."))
            return
        self.status.setText(tr_("{0} Treffer. Fett gedruckte Titelanzahl = passt zu deinem Album ({1} Titel).").format(len(results), n))
        best = next((i for i, r in enumerate(results) if r["tracks"] == n and r["score"] >= 80), 0)
        self.res.setCurrentItem(self.res.topLevelItem(best))

    def _select(self, it):
        self.gen += 1
        self.release = self.cover = None
        self.bapply.setEnabled(False)
        self.cov.setPixmap(QPixmap()); self.cov.setText(tr_("Lade …")); self.tl.clear(); self.info.setText("")
        self.status.setText(tr_("Lade Details …"))
        mbid, rgid = it.data(0, Qt.UserRole), it.data(1, Qt.UserRole)
        self._run(lambda: (mb_release(mbid), caa_cover(mbid, rgid)), self._details)

    def _details(self, res):
        rel, cover = res
        self.release, self.cover = rel, cover
        pm = QPixmap()
        if cover and pm.loadFromData(cover):
            self.cov.setPixmap(pm.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.cov.setText(tr_("Kein Cover vorhanden"))
        bits = [b for b in (rel["year"], rel["genre"], rel["label"]) if b]
        self.info.setText(f"<b>{html.escape(rel['title'])}</b><br>{html.escape(rel['artist'])}<br>"
                          f"<span style='color:{T.dim.name()}'>{html.escape(' · '.join(bits))}</span>")
        multi = len({t["disc"] for t in rel["tracks"]}) > 1
        for t in rel["tracks"]:
            num = f"{t['disc']}-{t['pos']}" if multi else str(t["pos"])
            self.tl.addItem(f"{num}.  {t['title']}   {fmt_time(t['length'])}")
        self.bapply.setEnabled(True)
        self._update_preview()

    def _update_preview(self):
        if not self.release:
            return
        ch = plan_changes(self.album, self.release, overwrite=self.r_over.isChecked())
        cover = self.c_cover.isChecked() and self.cover is not None
        parts = []
        if ch:
            parts.append(tr_("{0} von {1} Titeln werden ergänzt bzw. geändert").format(len(ch), len(self.album['tracks'])))
        if cover:
            parts.append(tr_("das Cover wird übernommen"))
        self.status.setText((", ".join(parts) + ".") if parts else tr_("Es gibt nichts zu ergänzen – alle Angaben sind schon vorhanden."))
        self.bapply.setEnabled(bool(parts))

    def apply(self):
        changes = plan_changes(self.album, self.release, overwrite=self.r_over.isChecked())
        cover = self.cover if self.c_cover.isChecked() else None
        opts, album = self.win.online_opts(), self.album
        if opts["write_tags"]:
            changes = with_pending(album, changes, self.win.local_lib.overrides)
        self.bapply.setEnabled(False)
        self.status.setText(tr_("Speichere …"))
        key = album["key"]
        self.win.run_job(lambda: write_album(album, changes, cover, opts, replace_cover=True),
                         lambda failed: self.win.apply_album_result(key, changes, cover is not None, failed),
                         lambda msg: self.win.flash(msg))
        self.closed = True
        super().accept()

    def reject(self):
        self.closed = True
        super().reject()


# ════════════════════════════════════════════════════════════════════════════
#  Hauptfenster
# ════════════════════════════════════════════════════════════════════════════
VIEW_NAMES = {"artists": tr_("Interpret"), "albums": tr_("Album"), "genres": tr_("Genre"), "songs": tr_("Titel@nav")}


class MainWindow(QMainWindow):
    @property
    def lib(self):
        """Bibliothek der aktuellen Ansicht: eigene Musik oder Jellyfin."""
        return self.jf_lib if self._src == "jf" else self.local_lib

    def __init__(self):
        super().__init__()
        self.setObjectName("main")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(APP_TITLE)
        self.resize(1360, 820)
        self.setMinimumSize(960, 580)
        self.settings = QSettings(APP_NAME, APP_NAME)
        self.theme_dict = self.load_theme()
        T.update(self.theme_dict)
        self.local_lib, self.stats, self.covers = Library(), Stats(), CoverCache()
        self.covers.attach_loader(self)
        self._cover_upd = QTimer(self); self._cover_upd.setSingleShot(True); self._cover_upd.setInterval(16)
        self._cover_upd.timeout.connect(lambda: (self.grid.viewport().update(), self.tracks.viewport().update()))
        self.covers.on_loaded.append(lambda _k: self._cover_upd.isActive() or self._cover_upd.start())
        self.jf_lib = JellyfinLibrary()
        self._src = "local"                     # welche Bibliothek die aktuelle Ansicht zeigt
        self.jf = None
        self.history, self.hpos, self.state = [], -1, "artists"
        self.queue, self.cur, self._eid, self._emap = [], None, 0, {}
        self.shuffle = self.settings.value("shuffle", False, type=bool)
        self.repeat = self.settings.value("repeat", 0, type=int)
        self.scanner = None
        self.batch = None
        self._jobs = set()
        self._counted = False
        self._icons = []
        self.frameless = False
        self._blur_timer = QTimer(self, singleShot=True, interval=120)
        self._blur_timer.timeout.connect(lambda: self._apply_blur())
        self.np_mode = False
        self.sort_col, self.sort_desc = None, False
        self._pending_pos = None
        self._resume_ready = False
        self._really_quit = False
        self._mini_was_max = False
        self._sub_auto_done = False
        self._srt, self._srt_file, self._srt_starts = None, None, []
        self._quiet_scan = False
        self.watcher = QFileSystemWatcher(self)
        self._watch_timer = QTimer(self, singleShot=True, interval=4000)
        self._watch_timer.timeout.connect(lambda: self.rescan(quiet=True))
        self.watcher.directoryChanged.connect(lambda _p: self._watch_timer.start())
        self._end_handled = False
        self._end_watchdog = QTimer(self, singleShot=True, interval=1500)
        self._end_watchdog.timeout.connect(self._end_watchdog_check)
        self.stream_title = ""
        self.sub_mode = "off"
        self._fs = False
        self._fs_was_max = False
        self._overlay = False
        self._winbox_on = False
        self._ovl_video = False
        self._fades = {}
        self._fs_timer = QTimer(self, singleShot=True, interval=2500)
        self._fs_timer.timeout.connect(self._fs_hide_controls)
        self.setAcceptDrops(True)
        self.setWindowIcon(app_icon())
        splash_step(tr_("Baue die Oberfläche auf …"), 18)
        self._build_ui()
        self.mini = MiniPlayer(self)
        splash_step(tr_("Bereite die Wiedergabe vor …"), 32)
        self._build_player()
        self.set_frameless(self.settings.value("window/frameless", True, type=bool), initial=True)
        splash_step(tr_("Wende das Design an …"), 44)
        self.apply_theme(self.theme_dict)

        splash_step(tr_("Lade die Bibliothek …"), 55)
        self.local_lib.load()
        self.jf_lib.load()
        self._jf_setup()
        splash_step(tr_("Bibliothek geladen: {0} Titel").format(fmt_int(len(self.local_lib.tracks))), 66)
        if not self.folders():
            for cand in (Path.home() / tr_("Musik"), Path.home() / "Music"):
                if cand.is_dir():
                    self.settings.setValue("folders", [str(cand)])
                    break
        splash_step(tr_("Öffne die letzte Ansicht …"), 72)
        last = self.settings.value("session/view", "artists") or "artists"
        try:
            self.navigate(last)
        except Exception:
            self.history, self.hpos = [], -1
            self.navigate("artists")
        self.refresh_playlists_nav()
        splash_step(tr_("Verbinde die Mediensteuerung …"), 86)
        self.setup_tray()
        self.mpris = None
        if media_control_available() and self.settings.value("system/mpris", True, type=bool):
            try:
                self.mpris = Smtc(self) if IS_WIN else Mpris(self)
            except Exception:
                self.mpris = None
        splash_step(tr_("Stelle die letzte Sitzung wieder her …"), 94)
        self.restore_session()
        self._mark_current()
        if _SPLASH is not None:
            splash_step(tr_("Lade die Cover …"), 97)
            self._prewarm_covers()
        if self.jf:
            QTimer.singleShot(1500, self.jf_refresh)
        if self.folders() and (not self.local_lib.tracks or self.local_lib.outdated):
            QTimer.singleShot(200, lambda: self.rescan(full=self.local_lib.outdated))
        elif self.folders() and (self.settings.value("library/scan_on_start", True, type=bool)
                                 or self.settings.value("library/watch", True, type=bool)):
            QTimer.singleShot(2500, lambda: self.rescan(quiet=True))   # erst, wenn das Fenster steht
        QTimer.singleShot(8000, self._auto_update_check)

    def _relayout_covers(self):
        """Albumspalte schmaler/breiter gezogen: Cover passt sich an, die Blöcke werden passend hoch."""
        m = self.track_model
        ci = next(i for i, c in enumerate(COLUMNS) if c[0] == "cover")
        eff = album_block(self.tracks.header().sectionSize(ci))[2]
        if m.flat or not m._src_groups:
            m.block_h = eff
            return
        old = math.ceil((m.block_h or (T.cover + 14)) / ROWH)
        m.block_h = eff
        if math.ceil(eff / ROWH) == old:
            self.tracks.viewport().update()
            return
        sel = {id(m.rows[i.row()][2]) for i in self.tracks.selectionModel().selectedRows() if m.rows[i.row()][2]}
        bar = self.tracks.verticalScrollBar()
        frac = bar.value() / max(1, bar.maximum())
        m.set_groups(m._src_groups)
        if sel:
            from PySide6.QtCore import QItemSelection, QItemSelectionModel
            qs = QItemSelection()
            for r, row in enumerate(m.rows):
                if row[2] is not None and id(row[2]) in sel:
                    qs.select(m.index(r, 0), m.index(r, len(COLUMNS) - 1))
            self.tracks.selectionModel().select(qs, QItemSelectionModel.Select)
        bar.setValue(int(frac * bar.maximum()))

    def _prewarm_covers(self):
        """Erste Ansicht einmal unsichtbar zeichnen: lädt alle sichtbaren Cover schon hinter dem Ladebildschirm."""
        self.covers.sync_mode = True
        try:
            self.centralWidget().grab()
        except Exception:
            pass
        finally:
            self.covers.sync_mode = False

    # ── Theme ─────────────────────────────────────────────────────────────
    def load_theme(self):
        d = {}
        for k, v in DEFAULT_THEME.items():
            d[k] = self.settings.value(f"theme/{k}", v, type=type(v))
        return d

    def save_theme(self, d):
        for k, v in d.items():
            self.settings.setValue(f"theme/{k}", v)

    def apply_theme(self, d):
        old_cover = T.cover
        self.theme_dict = dict(d)
        T.update(d)
        app = QApplication.instance()
        app.setPalette(build_palette())
        app.setStyleSheet(app_style())
        self.setStyleSheet(main_style())
        for btn, name, size in self._icons:
            btn.setIcon(make_icon(name, size))
        self.btn_repeat.setIcon(make_icon("repeat1" if self.repeat == 2 else "repeat", 20))
        self.btn_mute.setIcon(make_icon("mute" if self.audio.isMuted() else "volume", 20))
        self.search_act.setIcon(make_icon("search", 16, T.dim))
        if hasattr(self, "video"):
            self.video.refresh_icons(); self.video.update()
        if hasattr(self, "mini"):
            self.mini.refresh_style()
        if hasattr(self, "nav"):
            self.nav.itemDelegate()._icons.clear(); self.nav.viewport().update()
        self._update_corners()
        if hasattr(self, "top_menu"):
            self._apply_cmdbar()
        if hasattr(self, "split"):
            for i in range(self.split.count()):
                self.split.handle(i).update()
        self.covers.clear()
        if self.cur:
            self.np_cover.setPixmap(self.covers.get(self.cur["t"]["cover"], 42))
        else:
            self.np_cover.setPixmap(CoverCache.placeholder(42))
        hh = self.tracks.header()
        if T.cover != old_cover:
            hh.resizeSection(0, max(hh.sectionSize(0), T.cover + 170) if T.cover > old_cover else T.cover + 170)
            if self.stack.currentWidget() is self.tracks:
                self.render()
        self._render_crumbs()
        if self.isVisible():
            self._apply_blur()
        for w in (self.grid, self.tracks, self.qlist):
            w.viewport().update()
        self.btn_play.update()

    # ── Video & Vollbild ──────────────────────────────────────────────────
    def _has_video_changed(self, v):
        self.video.set_has_video(v)
        self._tracks_changed()
        if v:
            self.enter_np_mode()
        self._sync_overlay()
        self._fs_activity()

    def enter_np_mode(self):
        """WMP12-„Wird gespielt“-Modus: Bibliothek ausblenden, nur Cover/Video und Steuerleiste."""
        if self.np_mode:
            return
        self.np_mode = True
        widgets = [self.cmdbar, self.nav, self.qpanel, self.update_bar]
        if not self.frameless:
            widgets.append(self.topbar)
        for w in widgets:
            w.hide()
        self.crumb.setText(tr_("<span style=\"color:{0}\">Wird gespielt</span>").format(T.fg.name()))
        self.stack.setCurrentWidget(self.video)
        self.video.set_np_mode(True)
        self._update_mode_btn()
        self._sync_overlay()
        self._fs_timer.start()

    def exit_np_mode(self):
        if self._fs:
            self.toggle_fullscreen()
        if not self.np_mode:
            return
        self.np_mode = False
        self._fs_timer.stop()
        self._sync_overlay()
        for w in (self.topbar, self.nav, self.controls):
            w.show()
        self.cmdbar.setVisible(bool(self.theme_dict.get("cmdbar", True)))
        self.qpanel.setVisible(self.queue_visible)
        self.update_bar.setVisible(self._update_bar_wanted())
        self.video.unsetCursor()
        self.video.set_np_mode(False)
        self._update_mode_btn()
        self.render()

    def toggle_np_mode(self):
        self.exit_np_mode() if self.np_mode else self.enter_np_mode()

    def _update_mode_btn(self):
        name = "library" if self.np_mode else "nowplaying"
        self.btn_mode.setIcon(make_icon(name, 18))
        self.btn_mode.setToolTip(tr_("Zur Bibliothek wechseln") if self.np_mode else tr_("Zu „Wird gespielt“ wechseln"))
        self._icons = [(b, n, sz) for b, n, sz in self._icons if b is not self.btn_mode] + [(self.btn_mode, name, 18)]

    def toggle_fullscreen(self):
        if not self._fs:
            self._fs = True
            self._fs_was_max = self.isMaximized()
            self.enter_np_mode()
            self.topbar.hide()
            self.central.layout().setContentsMargins(0, 0, 0, 0)
            self._update_corners()
            self.showFullScreen()
            QTimer.singleShot(0, self._sync_overlay)
            self._fs_timer.start()
        else:
            self._fs = False
            self.controls.show()
            self.video.unsetCursor()
            if self.frameless:
                self.topbar.show()
            self.showMaximized() if self._fs_was_max else self.showNormal()
            self._update_frame_margin()
            if IS_WIN:
                QTimer.singleShot(0, self._win_anim_style)
            QTimer.singleShot(0, self._sync_overlay)
            self._fs_timer.start()

    # ── Steuerleiste als Overlay über dem Video ───────────────────────────
    def _ovl_items(self):
        """Was über dem Video ein- und ausblendet. Bei Musik bleibt die schmale Leiste einfach stehen."""
        items = [self.controls]
        if self._winbox_on and self._ovl_video:
            items.append(self.winbox)
        return items

    def _sync_overlay(self):
        """Läuft ein Video im „Wird gespielt“-Modus, schwebt die Steuerleiste transparent über dem Bild;
        oben bleiben nur Minimieren/Maximieren/Schließen."""
        # „Wird gespielt“ (Musik wie Video): Steuerleiste schwebt transparent über dem Bild,
        # oben statt Titelleiste mit Suche nur die schmale Leiste. Ausblenden nur bei Videos.
        want = bool(self.np_mode)
        vid = bool(want and self.video.has_video)
        winbox = bool(self.np_mode and self.frameless and not self._fs)
        if want == self._overlay and winbox == self._winbox_on and vid == self._ovl_video:
            self.video.lib_btn.setVisible(self.np_mode and not want and not winbox)
            if want or winbox:
                self._place_overlay()
            return
        root = self.central.layout()
        c = self.controls
        for w in (self.controls, self.winbox):
            if self._fades.get(w):
                self._fades[w].stop()
            w.setGraphicsEffect(None)
        self._fades = {}
        self._ovl_video = vid
        if want != self._overlay:
            if want:
                root.removeWidget(c)
            else:
                root.addWidget(c)
            c.setProperty("overlay", want)
            c.style().unpolish(c); c.style().polish(c)
        self._overlay = want
        self._winbox_on = winbox
        self.winbox.setVisible(winbox)
        # schlanke Ansicht: Titelleiste weg, Bibliotheks-Knopf im Bild weg (gibt es unten in der Leiste)
        if want or winbox:
            self.topbar.hide()
        self.video.lib_btn.setVisible(self.np_mode and not want and not winbox)
        if want:
            for w in (self._ovl_items() if vid else []):
                eff = QGraphicsOpacityEffect(w); eff.setOpacity(1.0); w.setGraphicsEffect(eff)
                a = QPropertyAnimation(eff, b"opacity", self); a.setDuration(260)
                a.finished.connect(lambda w=w: self._fade_done(w))
                self._fades[w] = a
                w.show()
            c.show()
            self._place_overlay()
        else:
            c.show()
            if winbox:
                self._place_overlay()

    def _place_overlay(self):
        if not (self._overlay or self._winbox_on):
            return
        m = self.central.layout().contentsMargins()
        if self._overlay:
            h = self.controls.height()
            self.controls.setGeometry(m.left(), self.central.height() - m.bottom() - h,
                                      self.central.width() - m.left() - m.right(), h)
            self.controls.raise_()
        if self._winbox_on:
            t = self.cur["t"]["title"] if self.cur else ""
            self.ovl_title.setText(disp(t))
            self.winbox.setGeometry(m.left(), m.top(), self.central.width() - m.left() - m.right(),
                                    self.winbox.sizeHint().height())
            self.winbox.raise_()

    def _fade_to(self, visible):
        target = 1.0 if visible else 0.0
        for w in self._ovl_items():
            a = self._fades.get(w)
            if not a:
                w.setVisible(visible)
                continue
            eff = w.graphicsEffect()
            if visible and w.isHidden():
                eff.setOpacity(0.0)
                w.show(); w.raise_()
            if a.state() == QPropertyAnimation.Running and a.endValue() == target:
                continue
            if not visible and w.isHidden():
                continue
            a.stop(); a.setStartValue(eff.opacity()); a.setEndValue(target); a.start()

    def _fade_done(self, w):
        a = self._fades.get(w)
        if a and a.endValue() == 0.0:
            w.hide()

    def _fs_activity(self):
        if self._fs or self.np_mode:
            if self._overlay:
                self._fade_to(True)
            else:
                self.controls.show()
            self.video.unsetCursor()
            self._fs_timer.start()

    def _fs_hide_controls(self):
        if ((self._fs or self.np_mode) and self.video.has_video and not self.video.ended
                and self.player.playbackState() == QMediaPlayer.PlayingState
                and not any(w.underMouse() for w in self._ovl_items())):
            if self._overlay:
                self._fade_to(False)
            else:
                self.controls.hide()
            self.video.setCursor(Qt.BlankCursor)

    def replay(self):
        self.video.show_end(False)
        if self.queue:
            self.play_entry(self.queue[0])

    def _playback_finished(self):
        self.video.show_end(True)
        self._fs_activity()

    # ── Sortieren ─────────────────────────────────────────────────────────
    def sort_by(self, col):
        if col == 0 or COLUMNS[col][0] == "cover":
            self.sort_col = None
        elif col == self.sort_col:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_col, self.sort_desc = col, False
        self.render()

    def _sort_key(self, key):
        num = {"track", "length", "size", "bitrate", "disc"}
        if key in num:
            return lambda t: (t.get(key) or 0)
        if key == "year":
            return lambda t: to_num(t.get("year")) or 0
        if key == "rating":
            return lambda t: self.stats.rating(t["path"])
        if key == "plays":
            return lambda t: self.stats.plays(t["path"])
        if key in ("artist", "albumartist"):
            return lambda t: sort_name(t.get(key, ""))
        return lambda t: str(t.get(key, "") or "").casefold()

    def _sorted(self, tracks):
        key = COLUMNS[self.sort_col][0]
        return sorted(tracks, key=self._sort_key(key), reverse=self.sort_desc)

    def _update_sort_indicator(self):
        hh = self.tracks.header()
        if self.sort_col is None:
            hh.setSortIndicatorShown(False)
        else:
            hh.setSortIndicatorShown(True)
            hh.setSortIndicator(self.sort_col, Qt.DescendingOrder if self.sort_desc else Qt.AscendingOrder)

    # ── Wiedergabelisten ──────────────────────────────────────────────────
    def auto_tracks(self, key):
        L, st = self.local_lib.tracks + self.jf_lib.tracks, self.stats
        if key == "recent":
            r = [t for t in L if st.last(t["path"])]
            r.sort(key=lambda t: -st.last(t["path"]))
            return r[:200]
        if key == "favs":
            r = [t for t in L if st.rating(t["path"]) >= 4]
            r.sort(key=lambda t: (-st.rating(t["path"]), sort_name(t["artist"]), t["album"].lower(), t.get("track", 0)))
            return r
        if key == "top":
            r = [t for t in L if st.plays(t["path"])]
            r.sort(key=lambda t: -st.plays(t["path"]))
            return r[:100]
        if key == "new":
            return sorted(L, key=lambda t: -(t.get("mtime") or 0))[:100]
        return []

    def playlist_names(self):
        try:
            return sorted((p.stem for p in PLAYLIST_DIR.glob("*.m3u8")), key=str.casefold)
        except OSError:
            return []

    def _pl_path(self, name):
        return PLAYLIST_DIR / f"{name}.m3u8"

    # ── Jellyfin ──────────────────────────────────────────────────────────
    def _jf_setup(self):
        """Client aus den Einstellungen bauen (falls verbunden)."""
        global JF_FETCHER
        st = self.settings
        dev = st.value("jf/device_id", "")
        if not dev:
            import uuid
            dev = uuid.uuid4().hex; st.setValue("jf/device_id", dev)
        url, tok, uid = st.value("jf/url", ""), st.value("jf/token", ""), st.value("jf/user_id", "")
        self.jf = Jellyfin(url, tok, uid, dev, st.value("jf/quality", "orig")) if url and tok and uid else None
        if not hasattr(self, "_jf_fetcher"):
            self._jf_fetcher = JfCoverFetcher(self)
            self._jf_fetcher.loaded.connect(self._jf_cover_loaded)
        self._jf_fetcher.client = self.jf
        JF_FETCHER = self._jf_fetcher if self.jf else None
        if hasattr(self, "nav"):
            self.refresh_jellyfin_nav()

    def _jf_cover_loaded(self, key):
        self.covers.forget(key)
        self.grid.viewport().update(); self.tracks.viewport().update()
        if self.cur and self.cur["t"].get("cover") == key:
            self.np_cover.setPixmap(self.covers.get(key, 42))

    def jf_refresh(self, quiet=True):
        """Bibliothek vom Server holen (im Hintergrund)."""
        if not self.jf or getattr(self, "_jf_loading", False):
            return
        self._jf_loading = True
        cli = self.jf
        if not quiet:
            self.flash(tr_("Lade die Jellyfin-Bibliothek …"), 60000)

        def work():
            return cli.fetch_tracks(), cli.fetch_playlists()

        def ok(res):
            self._jf_loading = False
            tracks, pls = res
            # Favoriten vom Server als 5 Sterne übernehmen, wo NeoNote noch keine Bewertung hat
            for t in tracks:
                if t.get("jf_fav") and not self.stats.rating(t["path"]):
                    self.stats.set_rating(t["path"], 5)
            self.jf_lib.playlists = pls
            self.jf_lib.set_tracks(tracks); self.jf_lib.save()
            self.refresh_jellyfin_nav()
            if self.state.startswith("jf:") and not self.np_mode:
                self.render()
            if not quiet:
                self.flash(tr_("Jellyfin: {0} Titel geladen").format(fmt_int(len(tracks))))

        def fail(msg):
            self._jf_loading = False
            if not quiet:
                self.flash(tr_("Jellyfin: {0}").format(msg))
        self.run_job(work, ok, fail)

    def media_src(self, t):
        """Was der Player abspielen soll: Datei, Offline-Kopie oder Stream vom Jellyfin-Server."""
        if t.get("remote"):
            off = self.jf_lib.offline_path(t)
            if off:
                return off
            return self.jf.stream_url(t["jf_id"]) if self.jf else None
        return t["path"]

    def jf_report_play(self, t):
        if self.jf and t.get("remote"):
            cli, iid = self.jf, t["jf_id"]
            self.run_job(lambda: cli.mark_played(iid), lambda _r: None, lambda _m: None)

    def jf_set_favorite(self, tracks, on):
        if not self.jf:
            return
        cli, ids = self.jf, [t["jf_id"] for t in tracks if t.get("remote")]
        if ids:
            self.run_job(lambda: [cli.set_favorite(i, on) for i in ids], lambda _r: None, lambda _m: None)

    def jf_make_offline(self, tracks):
        if not self.jf:
            return
        todo = [t for t in tracks if t.get("remote") and not self.jf_lib.offline_path(t)]
        if not todo:
            self.flash(tr_("Schon offline gespeichert."))
            return
        cli = self.jf
        JF_OFFLINE_DIR.mkdir(parents=True, exist_ok=True)

        def work():
            done = {}
            for t in todo:
                ext = (t.get("container") or "mp3").lower()
                dest = JF_OFFLINE_DIR / f"{t['jf_id']}.{ext}"
                cli.download(t["jf_id"], dest)
                done[t["jf_id"]] = str(dest)
            return done

        def ok(done):
            self.jf_lib.offline.update(done); self.jf_lib.save()
            self.flash(tr_("{0} Titel offline gespeichert").format(len(done)))
            self.grid.viewport().update(); self.tracks.viewport().update()
        self.flash(tr_("Speichere {0} Titel offline …").format(len(todo)), 120000)
        self.run_job(work, ok)

    def jf_drop_offline(self, tracks):
        n = 0
        for t in tracks:
            p = self.jf_lib.offline.pop(t.get("jf_id", ""), None)
            if p:
                try:
                    os.remove(p); n += 1
                except OSError:
                    pass
        self.jf_lib.save()
        self.flash(tr_("{0} Offline-Kopien gelöscht").format(n))

    def reveal_track(self, t):
        """Titel in der Titelliste auswählen und hinscrollen."""
        m = self.track_model
        for r, row in enumerate(m.rows):
            if row[2] is t:
                idx = m.index(r, 1)
                self.tracks.setCurrentIndex(idx)
                self.tracks.scrollTo(idx, QAbstractItemView.PositionAtCenter)
                break

    def tracks_from_paths(self, items):
        """[(pfad, titel)] -> Track-Dicts (aus der Bibliothek, sonst aus der Datei)."""
        bypath = {t["path"]: t for t in self.local_lib.tracks}
        bypath.update({t["path"]: t for t in self.jf_lib.tracks})
        out = []
        for path, title in items:
            if path.startswith(("http://", "https://")):
                out.append(stream_track(path, title))
                continue
            t = bypath.get(path)
            if t is None and os.path.exists(path):
                t = read_track(path) or basic_track(path)
            if t is None:
                t = basic_track(path) or {**stream_track(path, title or Path(path).stem), "stream": False,
                                          "artist": tr_("Datei fehlt")}
                t["missing"] = True
            out.append(t)
        return out

    def playlist_tracks(self, name):
        try:
            return self.tracks_from_paths(read_playlist_file(self._pl_path(name)))
        except OSError:
            return []

    def save_playlist(self, name, tracks):
        PLAYLIST_DIR.mkdir(parents=True, exist_ok=True)
        write_m3u(self._pl_path(name), tracks)
        self.refresh_playlists_nav()

    def _ask_name(self, title, default=""):
        name, ok = QInputDialog.getText(self, title, tr_("Name der Wiedergabeliste:"), text=default)
        name = name.strip().replace("/", "-")
        if not ok or not name:
            return None
        return name

    def new_playlist(self, tracks=None):
        name = self._ask_name(tr_("Neue Wiedergabeliste"))
        if not name:
            return None
        if self._pl_path(name).exists():
            if QMessageBox.question(self, APP_NAME, tr_("Die Wiedergabeliste „{0}“ gibt es schon. Ersetzen?").format(name)) != QMessageBox.Yes:
                return None
        self.save_playlist(name, tracks or [])
        self.flash(tr_("Wiedergabeliste „{0}“ gespeichert.").format(name))
        return name

    def add_to_playlist(self, name, tracks):
        cur = self.playlist_tracks(name)
        self.save_playlist(name, cur + list(tracks))
        self.flash(tr_("{0} Titel zu „{1}“ hinzugefügt.").format(len(tracks), name))
        if self.state == f"playlist:{name}":
            self.render()

    def remove_from_playlist(self, name, orig_indices):
        cur = self.playlist_tracks(name)
        rm = set(orig_indices)
        self.save_playlist(name, [t for i, t in enumerate(cur) if i not in rm])
        self.render()

    def rename_playlist(self, name):
        new = self._ask_name(tr_("Wiedergabeliste umbenennen"), name)
        if new and new != name:
            if self._pl_path(new).exists():
                QMessageBox.warning(self, APP_NAME, tr_("Es gibt schon eine Wiedergabeliste „{0}“.").format(new))
                return
            self._pl_path(name).rename(self._pl_path(new))
            self.refresh_playlists_nav()
            if self.state == f"playlist:{name}":
                self.navigate(f"playlist:{new}")

    def delete_playlist(self, name):
        if QMessageBox.question(self, APP_NAME, tr_("Wiedergabeliste „{0}“ löschen?\n(Die Musikdateien bleiben erhalten.)").format(name)) == QMessageBox.Yes:
            self._pl_path(name).unlink(missing_ok=True)
            self.refresh_playlists_nav()
            if self.state == f"playlist:{name}":
                self.navigate("artists")

    def export_playlist(self, name=None):
        tracks = self.playlist_tracks(name) if name else [e["t"] for e in self.queue]
        fn, _ = QFileDialog.getSaveFileName(self, tr_("Wiedergabeliste exportieren"),
                                            str(Path.home() / f"{name or tr_('Wiedergabeliste')}.m3u8"),
                                            tr_("Wiedergabeliste (*.m3u8 *.m3u)"))
        if fn:
            write_m3u(fn, tracks)
            self.flash(tr_("Exportiert: {0}").format(fn))

    def import_playlist(self):
        fn, _ = QFileDialog.getOpenFileName(self, tr_("Wiedergabeliste importieren"), str(Path.home()),
                                            tr_("Wiedergabelisten (*.m3u *.m3u8 *.pls *.wpl *.zpl)"))
        if not fn:
            return
        items = read_playlist_file(fn)
        tracks = self.tracks_from_paths(items)
        missing = sum(1 for t in tracks if t.get("missing"))
        name = Path(fn).stem
        while self._pl_path(name).exists():
            name += " (2)"
        self.save_playlist(name, tracks)
        self.navigate(f"playlist:{name}")
        self.flash(tr_("„{0}“ importiert: {1} Titel").format(name, len(tracks)) + (tr_(", {0} Dateien nicht gefunden.").format(missing) if missing else "."), 10000)

    def save_queue_as_playlist(self):
        if not self.queue:
            self.flash(tr_("Die Wiedergabeliste ist leer."))
            return
        self.new_playlist([e["t"] for e in self.queue])

    # ── Navigationsleiste aus der Konfiguration aufbauen ───────────────────
    def nav_layout(self):
        try:
            lay = json.loads(self.settings.value("nav/layout", "") or "null")
        except ValueError:
            lay = None
        if not isinstance(lay, list):
            return default_nav_layout()
        lay = [e for e in lay if isinstance(e, dict) and (e.get("id") == "sep" or e.get("id") in NAV_DEF)]
        known = {e["id"] for e in lay}
        for i in NAV_DEF:                      # neue Einträge späterer Versionen ergänzen
            if i not in known:
                lay.append({"id": i, "show": True})
        return lay

    def build_nav(self, layout=None):
        layout = layout if layout is not None else self.nav_layout()
        self.nav.clear()
        self.nav_items = {}
        # nur sichtbare Einträge, ohne doppelte/randständige Trennlinien
        vis = [e for e in layout if e["id"] == "sep" or e.get("show", True)]
        clean = []
        for e in vis:
            if e["id"] == "sep" and (not clean or clean[-1]["id"] == "sep"):
                continue
            clean.append(e)
        while clean and clean[-1]["id"] == "sep":
            clean.pop()

        def add(kind, text, state, icon=None, parent=None):
            it = QTreeWidgetItem([text])
            it.setData(0, Qt.UserRole, state); it.setData(0, NAV_KIND, kind); it.setData(0, NAV_ICON, icon)
            if kind == "sep":
                it.setFlags(Qt.NoItemFlags)
            elif kind == "header":
                it.setFlags(Qt.ItemIsEnabled)
            (parent.addChild if parent else self.nav.addTopLevelItem)(it)
            if state:
                self.nav_items[state] = it
            return it

        auto_head = None
        for e in clean:
            i = e["id"]
            if i == "sep":
                add("sep", "", None); auto_head = None
                continue
            name, icon, kind = NAV_DEF[i]
            label = e.get("label") or name
            if i == "autohead":
                auto_head = add("header", label, i, icon)
            elif i.startswith("auto:") and i != "auto:recent" and auto_head is not None:
                add("child", label, i, None, auto_head)        # Unterpunkt direkt unter „Automatische Listen“
            else:
                add(kind, label, i, icon)
                auto_head = None
        self.nav.expandAll()
        if "playlists" in self.nav_items:
            self.refresh_playlists_nav()
        if "jellyfin" in self.nav_items:
            self.refresh_jellyfin_nav()
        if "queue" in self.nav_items:
            self.nav_items["queue"].setData(0, NAV_COUNT, str(len(self.queue)) if getattr(self, "queue", None) else "")
        st = getattr(self, "state", "")
        nk = st if st.startswith(("playlist:", "auto:")) else \
            {"artist": "artists", "genre": "genres", "album": "albums"}.get(st.split(":")[0], st.split(":")[0])
        if nk in self.nav_items:
            self.nav.setCurrentItem(self.nav_items[nk])

    def apply_nav_layout(self, layout, save=True):
        if save:
            self.settings.setValue("nav/layout", json.dumps(layout))
        self.build_nav(layout)

    def refresh_jellyfin_nav(self):
        if "jellyfin" not in self.nav_items:
            return
        root = self.nav_items["jellyfin"]
        for k in [k for k in self.nav_items if k.startswith("jf:")]:
            del self.nav_items[k]
        root.takeChildren()

        def child(text, state):
            it = QTreeWidgetItem([text]); it.setData(0, Qt.UserRole, state); it.setData(0, NAV_KIND, "child")
            root.addChild(it); self.nav_items[state] = it

        if not self.jf:
            child(tr_("Server verbinden …"), "jf:connect")
        else:
            for st, label in (("jf:artists", tr_("Interpreten")), ("jf:albums", tr_("Alben")), ("jf:genres", tr_("Genres")),
                              ("jf:songs", tr_("Titel@nav"))):
                child(label, st)
            for p in self.jf_lib.playlists:
                child(p["name"], f"jf:playlist:{p['id']}")
        root.setExpanded(True)
        if self.state in self.nav_items:
            self.nav.setCurrentItem(self.nav_items[self.state])

    def refresh_playlists_nav(self):
        if "playlists" not in self.nav_items:
            return
        root = self.nav_items["playlists"]
        cur = self.state
        root.takeChildren()
        for name in self.playlist_names():
            it = QTreeWidgetItem([name]); it.setData(0, Qt.UserRole, f"playlist:{name}")
            it.setData(0, NAV_KIND, "child")
            root.addChild(it)
            self.nav_items[f"playlist:{name}"] = it
        root.setExpanded(True)
        if cur.startswith("playlist:") and cur in self.nav_items:
            self.nav.setCurrentItem(self.nav_items[cur])

    def _nav_menu(self, pos):
        it = self.nav.itemAt(pos)
        if not it or not (it.data(0, Qt.UserRole) or "").startswith(("playlist", "auto:", "radio")):
            m = QMenu(self)
            m.addAction(tr_("Leiste anpassen…"), lambda: self.open_settings(SettingsDialog.TAB_NAV))
            m.exec(self.nav.viewport().mapToGlobal(pos))
            return
        st = it.data(0, Qt.UserRole) or ""
        m = QMenu(self)
        if st == "playlists":
            m.addAction(tr_("Neue Wiedergabeliste…"), self.new_playlist)
            m.addAction(tr_("Wiedergabeliste importieren…"), self.import_playlist)
        elif st.startswith("playlist:"):
            name = st[9:]
            m.addAction(make_icon("play", 14), tr_("Wiedergeben"), lambda: self.play_tracks(self.playlist_tracks(name), 0))
            m.addAction(tr_("Zur aktuellen Wiedergabeliste hinzufügen"), lambda: self.add_tracks(self.playlist_tracks(name)))
            m.addSeparator()
            m.addAction(tr_("Umbenennen…"), lambda: self.rename_playlist(name))
            m.addAction(tr_("Exportieren…"), lambda: self.export_playlist(name))
            m.addAction(tr_("Löschen"), lambda: self.delete_playlist(name))
        elif st.startswith("auto:"):
            key = st[5:]
            m.addAction(make_icon("play", 14), tr_("Wiedergeben"), lambda: self.play_tracks(self.auto_tracks(key), 0))
            m.addAction(tr_("Zur aktuellen Wiedergabeliste hinzufügen"), lambda: self.add_tracks(self.auto_tracks(key)))
            m.addAction(tr_("Als Wiedergabeliste speichern…"), lambda: self.new_playlist(self.auto_tracks(key)))
        elif st == "radio":
            m.addAction(tr_("Sender hinzufügen…"), self.radio.add_station)
        m.addSeparator()
        m.addAction(tr_("Leiste anpassen…"), lambda: self.open_settings(SettingsDialog.TAB_NAV))
        m.exec(self.nav.viewport().mapToGlobal(pos))

    def _playlist_menu_into(self, m, tracks):
        sub = m.addMenu(tr_("Hinzufügen zu"))
        sub.addAction(tr_("Aktuelle Wiedergabeliste"), lambda: self.add_tracks(tracks))
        sub.addSeparator()
        for name in self.playlist_names():
            sub.addAction(name, lambda n=name: self.add_to_playlist(n, tracks))
        if self.playlist_names():
            sub.addSeparator()
        sub.addAction(tr_("Neue Wiedergabeliste…"), lambda: self.new_playlist(tracks))

    # ── Sitzung speichern / wiederherstellen ──────────────────────────────
    def save_session(self):
        st = self.settings
        st.setValue("session/queue", json.dumps([[e["t"]["path"], e["t"]["title"]] for e in self.queue]))
        st.setValue("session/index", self._cur_index())
        st.setValue("session/position", int(self.player.position()) if self.cur else 0)

    def restore_session(self):
        try:
            items = json.loads(self.settings.value("session/queue", "[]") or "[]")
        except ValueError:
            return
        if not items:
            return
        tracks = [t for t in self.tracks_from_paths([tuple(x) for x in items]) if not t.get("missing")]
        if not tracks:
            return
        self._emap = {}
        self.queue = [self._new_entry(t) for t in tracks]
        idx = self.settings.value("session/index", 0, type=int)
        idx = max(0, min(idx, len(self.queue) - 1))
        self.cur = self.queue[idx]
        self._rebuild_queue_view()
        t = self.cur["t"]
        if not t.get("stream"):
            self._pending_pos = self.settings.value("session/position", 0, type=int)
            self.player.setSource(QUrl.fromLocalFile(t["path"]))
            self._resume_ready = True
        self._show_now_playing(t)
        self._mark_current()

    def open_dialog(self):
        pats = " ".join("*" + e for e in sorted(MEDIA_EXT))
        files, _ = QFileDialog.getOpenFileNames(self, tr_("Dateien öffnen"), str(Path.home()),
                                                tr_("Medien ({0});;Alle Dateien (*)").format(pats))
        if files:
            self.open_files(files)

    def extra_files(self):
        v = self.settings.value("library/extra_files", [])
        return [v] if isinstance(v, str) else list(v or [])

    def open_files(self, paths):
        """Von außen geöffnete Dateien (Dolphin, Kommandozeile, Drag & Drop) abspielen."""
        files = []
        for p in paths:
            if os.path.isdir(p):
                for root, _d, names in os.walk(p):
                    files += sorted(os.path.join(root, n) for n in names if Path(n).suffix.lower() in MEDIA_EXT)
            elif os.path.isfile(p) and Path(p).suffix.lower() in MEDIA_EXT:
                files.append(p)
        if not files:
            self.flash(tr_("Keine abspielbaren Dateien gefunden."))
            return
        bypath = {t["path"]: t for t in self.local_lib.tracks}
        tracks, new = [], []
        for f in files:
            t = bypath.get(f)
            if t is None:
                t = read_track(f) or basic_track(f)
                if t is None:
                    continue
                if not (cover_path(t['cover'])).exists():
                    try:
                        save_cover(f, t["cover"])
                    except Exception:
                        pass
                if Path(f).suffix.lower() in AUDIO_EXT - {".mp4"}:     # nur Musik, keine Videos
                    new.append(t)
            tracks.append(t)
        if self.settings.value("library/add_opened", False, type=bool) and new:
            self._add_to_library(new)
        self.play_tracks(tracks, 0)

    def _add_to_library(self, tracks):
        folders = [os.path.join(os.path.abspath(f), "") for f in self.folders()]
        extra = self.extra_files()
        for t in tracks:
            if not any(t["path"].startswith(f) for f in folders) and t["path"] not in extra:
                extra.append(t["path"])
        self.settings.setValue("library/extra_files", extra)
        self.local_lib.set_tracks(self.local_lib.tracks + tracks)
        self.local_lib.save()
        if self.state != "playing":
            self.render()
        self.flash(tr_("{0} Titel zur Bibliothek hinzugefügt.").format(len(tracks)))

    def receive_message(self, conn):
        conn.waitForReadyRead(1500)
        data = bytes(conn.readAll())
        while conn.bytesAvailable() or conn.waitForReadyRead(100):
            data += bytes(conn.readAll())
        conn.disconnectFromServer()
        try:
            files = json.loads(data[:1_000_000].decode("utf-8") or "[]")
        except (ValueError, UnicodeDecodeError):
            files = []
        if not isinstance(files, list):
            files = []
        files = [f for f in files if isinstance(f, str)][:5000]
        self.show_window()        # auch aus Systemleiste oder Mini-Player zurückholen
        if files:
            self.open_files(files)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
        if paths:
            self.open_files(paths)

    # ── Eigene Fensterleiste ──────────────────────────────────────────────
    def set_frameless(self, on, initial=False):
        self.frameless = bool(on)
        self.btn_min.setVisible(self.frameless)
        self.btn_max.setVisible(self.frameless)
        self._update_frame_margin()
        # Windows: durchsichtige Fenster mit Systemrahmen werden falsch beschnitten → dann deckend
        if IS_WIN:
            self.setAttribute(Qt.WA_TranslucentBackground, self.frameless)
        if initial:
            self.setWindowFlag(Qt.FramelessWindowHint, self.frameless)
            return
        if bool(self.windowFlags() & Qt.FramelessWindowHint) != self.frameless:
            geo = self.geometry()
            self.setWindowFlag(Qt.FramelessWindowHint, self.frameless)
            self.setGeometry(geo)
            self.show()
            if IS_WIN and self.frameless:
                QTimer.singleShot(50, self._win_anim_style)

    def _update_frame_margin(self):
        m = 5 if self.frameless and not self.isMaximized() and not self._fs else 0
        self.central.layout().setContentsMargins(m, m, m, m)
        self._update_corners()

    CORNER = 10

    def corner_radius(self):
        # Windows: Ecken rundet Windows 11 selbst (DWM) – eigene Rundung + Weichzeichner ergäbe einen eckigen Rand
        if IS_WIN:
            return 0
        return self.CORNER if self.frameless and not (self.isMaximized() or self.isFullScreen() or self._fs) else 0

    def _update_corners(self):
        if not hasattr(self, "central"):
            return
        if self._fs:
            css = "#root { background: #000000; border-radius: 0px; border: none; }"
            if self.central.styleSheet() != css:
                self.central.setStyleSheet(css)
        else:
            r = self.corner_radius()
            m = self.central.layout().contentsMargins().left()
            ir = max(0, r - m)
            css = (f"#root {{ border-radius: {r}px; border: none; }}"
                   f"#root QFrame#topbar, #root QFrame#winbox {{ border-top-left-radius: {ir}px; border-top-right-radius: {ir}px; }}"
                   f"#root QFrame#controls {{ border-bottom-left-radius: {ir}px; border-bottom-right-radius: {ir}px; }}")
            if self.central.styleSheet() != css:      # neu setzen zwingt alle Listen zu einem neuen Layout
                self.central.setStyleSheet(css)
        self._apply_blur()

    def _apply_blur(self):
        if IS_WIN and not self.frameless:
            return
        if self.isVisible():
            set_window_blur(self, bool(self.theme_dict.get("blur")), self.corner_radius())

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if getattr(self, "_blur_timer", None):
            self._blur_timer.start()

    def toggle_maximize(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def changeEvent(self, e):
        if e.type() == QEvent.WindowStateChange and hasattr(self, "btn_max"):
            maxed = self.isMaximized()
            self._icons = [(b, n, sz) for b, n, sz in self._icons if b is not self.btn_max]
            self._icons.append((self.btn_max, "restore" if maxed else "maximize", 16))
            self.btn_max.setIcon(make_icon("restore" if maxed else "maximize", 16))
            self.btn_max.setToolTip(tr_("Wiederherstellen") if maxed else tr_("Maximieren"))
            if hasattr(self, "ovl_max"):
                self._icons = [(b, n, sz) for b, n, sz in self._icons if b is not self.ovl_max]
                self._icons.append((self.ovl_max, "restore" if maxed else "maximize", 14))
                self.ovl_max.setIcon(make_icon("restore" if maxed else "maximize", 14))
                self.ovl_max.setToolTip(tr_("Wiederherstellen") if maxed else tr_("Maximieren"))
            self._update_frame_margin()
        super().changeEvent(e)

    def _edges_at(self, pos):
        m, r = 7, self.central.rect()
        e = Qt.Edges()
        if pos.x() <= m: e |= Qt.LeftEdge
        if pos.x() >= r.width() - m: e |= Qt.RightEdge
        if pos.y() <= m: e |= Qt.TopEdge
        if pos.y() >= r.height() - m: e |= Qt.BottomEdge
        return e

    def eventFilter(self, obj, ev):
        if getattr(self, "grid", None) is not None and obj is self.grid.viewport() and ev.type() == QEvent.Resize:
            w = max(TILE_W, obj.width() - 2)
            if w != getattr(self, "_grid_sep_w", None):
                self._grid_sep_w = w
                for sep in getattr(self, "_grid_seps", []):
                    sep.setData(QSize(w, 36), Qt.SizeHintRole)
            return False
        if getattr(self, "grid", None) is not None and obj is self.grid.viewport() and ev.type() in (
                QEvent.DragEnter, QEvent.DragMove, QEvent.Drop):
            md = ev.mimeData()
            if not mime_has_image(md):
                return False
            album = None
            if ev.type() != QEvent.DragEnter:
                idx = self.grid.indexAt(ev.position().toPoint())
                if idx.isValid() and idx.data(ROLE_KIND) == "album":
                    album = self.lib.albums.get(idx.data(ROLE_KEY))
            if ev.type() == QEvent.DragEnter or album:
                ev.acceptProposedAction()
                if ev.type() == QEvent.Drop:
                    data = image_from_mime(md)
                    if data:
                        self.set_album_cover(album, data)
            else:
                ev.ignore()
            return True
        if getattr(self, "nav", None) is not None and obj is self.nav.viewport() and ev.type() == QEvent.MouseButtonPress:
            it = self.nav.itemAt(ev.position().toPoint())
            if it is not None and it.data(0, Qt.UserRole) == "playlists" and \
                    ev.position().x() > self.nav.viewport().width() - 40:
                QTimer.singleShot(0, self.new_playlist)
                return True
            return False
        if obj is getattr(self, "controls", None) and ev.type() == QEvent.Resize:
            self._layout_controls()
            return False
        if obj is getattr(self, "central", None) and ev.type() == QEvent.Resize and (self._overlay or self._winbox_on):
            QTimer.singleShot(0, self._place_overlay)
        if obj is getattr(self, "central", None) and self.frameless and not self.isMaximized():
            t = ev.type()
            if t in (QEvent.MouseMove, QEvent.HoverMove):
                e = self._edges_at(ev.position().toPoint())
                L, R, Tp, B = Qt.LeftEdge, Qt.RightEdge, Qt.TopEdge, Qt.BottomEdge
                if e in (L | Tp, R | B):
                    obj.setCursor(Qt.SizeFDiagCursor)
                elif e in (R | Tp, L | B):
                    obj.setCursor(Qt.SizeBDiagCursor)
                elif e & (L | R):
                    obj.setCursor(Qt.SizeHorCursor)
                elif e & (Tp | B):
                    obj.setCursor(Qt.SizeVerCursor)
                else:
                    obj.unsetCursor()
            elif t == QEvent.MouseButtonPress and ev.button() == Qt.LeftButton:
                e = self._edges_at(ev.position().toPoint())
                if e and self.windowHandle():
                    self.windowHandle().startSystemResize(e)
                    return True
            elif t == QEvent.Leave:
                obj.unsetCursor()
        return super().eventFilter(obj, ev)

    def showEvent(self, e):
        super().showEvent(e)
        QTimer.singleShot(0, self._update_corners)
        if IS_WIN:
            QTimer.singleShot(0, self._win_anim_style)

    # ── Windows: Animationen beim Minimieren/Wiederherstellen trotz eigener Fensterleiste ─────────
    # Rahmenlose Fenster (WS_POPUP) animiert Windows nicht. Mit WS_CAPTION + Min-/Max-Box animiert DWM wie
    # bei normalen Programmen; WM_NCCALCSIZE sorgt dafür, dass trotzdem keine Systemtitelleiste erscheint.
    _WS_CAPTION, _WS_SYSMENU, _WS_MINBOX, _WS_MAXBOX = 0x00C00000, 0x00080000, 0x00020000, 0x00010000

    def _win_anim_style(self):
        if not (IS_WIN and self.frameless) or self._fs:
            return
        try:
            u = ctypes.windll.user32
            hwnd = ctypes.c_void_p(int(self.winId()))
            get = getattr(u, "GetWindowLongPtrW", u.GetWindowLongW)
            setl = getattr(u, "SetWindowLongPtrW", u.SetWindowLongW)
            get.restype = ctypes.c_ssize_t; get.argtypes = [ctypes.c_void_p, ctypes.c_int]
            setl.restype = ctypes.c_ssize_t; setl.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_ssize_t]
            style = get(hwnd, -16)
            want = style | self._WS_CAPTION | self._WS_SYSMENU | self._WS_MINBOX | self._WS_MAXBOX
            if want != style:
                setl(hwnd, -16, want)
                # SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE
                u.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0020 | 0x0002 | 0x0001 | 0x0004 | 0x0010)
        except Exception:
            pass

    def nativeEvent(self, etype, message):
        if IS_WIN and self.frameless and etype == b"windows_generic_MSG":
            try:
                from ctypes import wintypes
                msg = wintypes.MSG.from_address(int(message))
                if msg.message == 0x0083 and msg.wParam:          # WM_NCCALCSIZE: ganze Fläche ist Inhalt
                    u = ctypes.windll.user32
                    if u.IsZoomed(msg.hWnd):
                        # maximiert legt Windows den (unsichtbaren) Rahmen über den Bildschirmrand → auf Arbeitsfläche begrenzen
                        class MONITORINFO(ctypes.Structure):
                            _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                                        ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]
                        u.MonitorFromWindow.restype = ctypes.c_void_p
                        u.MonitorFromWindow.argtypes = [ctypes.c_void_p, wintypes.DWORD]
                        mon = u.MonitorFromWindow(msg.hWnd, 2)
                        mi = MONITORINFO(); mi.cbSize = ctypes.sizeof(MONITORINFO)
                        if mon and u.GetMonitorInfoW(ctypes.c_void_p(mon), ctypes.byref(mi)):
                            rc = wintypes.RECT.from_address(int(msg.lParam))   # NCCALCSIZE_PARAMS.rgrc[0]
                            rc.left, rc.top, rc.right, rc.bottom = (mi.rcWork.left, mi.rcWork.top,
                                                                    mi.rcWork.right, mi.rcWork.bottom)
                    return True, 0
            except Exception:
                pass
        return super().nativeEvent(etype, message)

    def open_settings(self, tab=0):
        SettingsDialog(self, tab).exec()

    # ── Online-Informationen ──────────────────────────────────────────────
    def online_opts(self):
        g = self.settings.value
        return {"write_tags": g("online/write_tags", False, type=bool),
                "embed_cover": g("online/embed_cover", False, type=bool),
                "folder_cover": g("online/folder_cover", False, type=bool)}

    def run_job(self, fn, ok, fail=None):
        j = Job(fn, self)
        self._jobs.add(j)
        j.done.connect(ok)
        j.failed.connect(fail or self.flash)
        j.finished.connect(lambda: self._jobs.discard(j))
        j.start()
        return j

    def write_pending(self):
        pending = {p: dict(c) for p, c in self.local_lib.overrides.items() if c and os.path.exists(p)}

        def work():
            failed = []
            for path, ch in pending.items():
                try:
                    write_tags(path, ch)
                except Exception:
                    failed.append(path)
            return failed

        def done(failed):
            for path in pending:
                if path not in failed:
                    self.local_lib.overrides.pop(path, None)
            self.local_lib.save_overrides()
            self.flash(tr_("{0} Titel in die Dateien geschrieben").format(len(pending) - len(failed))
                       + (tr_(", {0} fehlgeschlagen.").format(len(failed)) if failed else "."), 9000)
        self.flash(tr_("Schreibe Angaben in die Dateien …"))
        self.run_job(work, done)

    def edit_tags(self, tracks, key, value):
        value = value.strip()
        if key in ("track", "disc"):
            if value and not value.isdigit():
                self.flash(tr_("Bitte eine Zahl eingeben.")); return
            value = int(value) if value else 0
        elif key == "year":
            value = value[:4]
            if value and not value.isdigit():
                self.flash(tr_("Bitte eine Jahreszahl eingeben.")); return
        elif key in ("title", "album", "artist") and not value:
            self.flash(tr_("Das Feld darf nicht leer sein.")); return
        changes = {t["path"]: {key: value} for t in tracks if t.get(key) != value}
        if not changes:
            return
        # Albumwechsel: vorhandenes Cover für den neuen Albumschlüssel übernehmen
        for t in tracks:
            if key in ("album", "albumartist", "artist"):
                aa = value if key == "albumartist" else t.get("albumartist") or t["artist"]
                al = value if key == "album" else t["album"]
                new_key = album_key(aa, al)
                src, dst = cover_path(t['cover']), cover_path(new_key)
                if src.exists() and not dst.exists():
                    try:
                        dst.write_bytes(src.read_bytes())
                    except OSError:
                        pass
        write = self.settings.value("edit/write_files", True, type=bool)

        def work():
            failed = []
            if write:
                for path, ch in changes.items():
                    try:
                        write_tags(path, ch)
                    except Exception:
                        failed.append(path)
            return failed

        def done(failed):
            bypath = {t["path"]: t for t in self.local_lib.tracks}
            for path, ch in changes.items():
                t = bypath.get(path)
                if t:
                    t.update(ch)
                    try:
                        t["mtime"] = os.stat(path).st_mtime; t["size"] = os.stat(path).st_size
                    except OSError:
                        pass
                if not write or path in failed:
                    self.local_lib.overrides.setdefault(path, {}).update(ch)
                elif path in self.local_lib.overrides:
                    self.local_lib.overrides[path].pop(key, None)
            self.local_lib.save_overrides()
            if failed:
                self.flash(tr_("{0} Datei(en) konnten nicht beschrieben werden. Die Änderung ist in der Bibliothek gespeichert.").format(len(failed)), 9000)
            self._refresh_library()
            if self.cur and self.cur["t"]["path"] in changes:
                self._show_now_playing(self.cur["t"])
        self.run_job(work, done)

    def lookup_album(self, album):
        LookupDialog(self, album).exec()

    def set_album_cover(self, album, data):
        """Neues Albumcover (Drag & Drop, Datei oder Zwischenablage) übernehmen."""
        if not album or not data or QImage.fromData(data).isNull():
            self.flash(tr_("Das ist kein Bild, das NeoNote lesen kann."))
            return
        opts, key = self.online_opts(), album["key"]
        where = []
        if opts["embed_cover"]:
            where.append(tr_("in die Dateien geschrieben"))
        if opts["folder_cover"]:
            where.append(tr_("als cover.jpg im Ordner abgelegt"))
        self.run_job(lambda: write_album(album, {}, data, opts, replace_cover=True),
                     lambda failed: (self.apply_album_result(key, {}, True, failed, rerender=False),
                                     self.flash(tr_("Cover für „{0}“ geändert").format(album['title'])
                                                + (tr_(" und ") + tr_(" und ").join(where) if where else "") + ".")))

    def change_cover_dialog(self, album):
        fn, _ = QFileDialog.getOpenFileName(self, tr_("Cover für „{0}“ wählen").format(album['title']),
                                            str(Path(album["tracks"][0]["path"]).parent) if album.get("tracks") else str(Path.home()),
                                            tr_("Bilder (*.jpg *.jpeg *.png *.webp *.bmp)"))
        if fn:
            try:
                self.set_album_cover(album, Path(fn).read_bytes())
            except OSError as e:
                self.flash(str(e))

    def apply_album_result(self, key, changes, cover_written, failed, rerender=True):
        bypath = {t["path"]: t for t in self.local_lib.tracks}
        write = self.online_opts()["write_tags"]
        for path, ch in changes.items():
            t = bypath.get(path)
            if t:
                t.update(ch)
            if not write or path in failed:
                self.local_lib.overrides.setdefault(path, {}).update(ch)
            elif path in self.local_lib.overrides:
                for k in ch:
                    self.local_lib.overrides[path].pop(k, None)
        self.local_lib.save_overrides()
        if cover_written:
            self.covers.clear()
            if self.cur:
                self.np_cover.setPixmap(self.covers.get(self.cur["t"]["cover"], 42))
        if failed:
            self.flash(tr_("{0} Datei(en) konnten nicht beschrieben werden (schreibgeschützt?). Die Angaben sind trotzdem in der Bibliothek gespeichert.").format(len(failed)), 9000)
        if rerender:
            self._refresh_library()
        else:
            self.grid.viewport().update(); self.tracks.viewport().update()

    def _refresh_library(self):
        sb = (self.tracks if self.stack.currentWidget() is self.tracks else self.grid).verticalScrollBar()
        pos = sb.value()
        self.local_lib.set_tracks(self.local_lib.tracks)
        self.local_lib.save()
        self.render()
        QTimer.singleShot(0, lambda: sb.setValue(pos))

    def albums_needing_info(self, albums=None):
        out = []
        for a in (albums if albums is not None else self.local_lib.albums.values()):
            if a["title"] in UNKNOWN:
                continue
            if (not (cover_path(a['key'])).exists() or not a["year"]
                    or a["genre"] in UNKNOWN or any(not t.get("track") for t in a["tracks"])):
                out.append(a)
        return out

    def start_batch(self, albums=None):
        if self.batch or self.scanner:
            self.flash(tr_("Es läuft bereits ein Vorgang."))
            return
        todo = self.albums_needing_info(albums)
        if not todo:
            self.flash(tr_("Alle Alben haben bereits Cover, Jahr und Genre."))
            return
        opts = self.online_opts()
        pending = json.loads(json.dumps(self.local_lib.overrides)) if opts["write_tags"] else {}
        self.batch = BatchLookup(todo, opts, self, pending)
        self.batch.progress.connect(self._batch_progress)
        self.batch.album_done.connect(lambda k, ch, cov, f: self.apply_album_result(k, ch, cov, f, rerender=False))
        self.batch.finished_batch.connect(self._batch_done)
        self.progress.setRange(0, len(todo)); self.progress.setValue(0); self.progress.show()
        self.btn_cancel.show()
        self.batch.start()

    def cancel_batch(self):
        if self.batch:
            self.batch.requestInterruption()
            self.count_label.setText(tr_("Wird abgebrochen …"))

    def _batch_progress(self, i, n, title):
        self.progress.setRange(0, max(1, n)); self.progress.setValue(i)
        if title:
            self.count_label.setText(tr_("Suche Infos {0}/{1}: {2}").format(i + 1, n, title))

    def _batch_done(self, ok, missing, errors, msg):
        last_err = self.batch_last_err = msg
        self.batch.wait(); self.batch = None
        self.progress.hide(); self.btn_cancel.hide()
        self._refresh_library()
        if msg == "abgebrochen":
            text = tr_("Online-Suche abgebrochen – {0} {1} ergänzt.").format(ok, tr_('Album@n') if ok == 1 else tr_('Alben@n'))
        elif msg == "stop":
            text = tr_("Online-Suche gestoppt: Keine Verbindung zu MusicBrainz. Bitte Internetverbindung prüfen.")
        else:
            alb = tr_("Album@n") if ok == 1 else tr_("Alben@n")
            text = tr_("Online-Suche fertig: {0} {1} ergänzt, {2} nicht gefunden").format(ok, alb, missing)
            text += tr_(", {0} Fehler – {1}.").format(errors, last_err.rstrip('.')) if errors else "."
        self.flash(text, 15000)

    # ── UI-Aufbau ─────────────────────────────────────────────────────────
    def _icon_btn(self, name, size=20, tip="", slot=None, checkable=False, obj=None):
        b = QToolButton()
        b.setIconSize(QSize(size, size)); b.setToolTip(tip); b.setCheckable(checkable)
        if slot:
            b.clicked.connect(slot)
        if obj:
            b.setObjectName(obj)
        self._icons.append((b, name, size))
        return b

    def _build_ui(self):
        central = RootWidget(); central.setObjectName("root")
        root = QVBoxLayout(central); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        top = DragBar(self); top.setObjectName("topbar"); self.topbar = top
        tl = QHBoxLayout(top); tl.setContentsMargins(8, 7, 6, 7); tl.setSpacing(4)
        self.btn_back = self._icon_btn("chev_left", 16, tr_("Zurück (Alt+←)"), self.go_back, obj="navbtn")
        self.btn_fwd = self._icon_btn("chev_right", 16, tr_("Vor (Alt+→)"), self.go_forward, obj="navbtn")
        self.crumb = QLabel(); self.crumb.setObjectName("crumb"); self.crumb.setTextFormat(Qt.RichText)
        self.crumb.linkActivated.connect(self.navigate)
        self.search = QLineEdit(); self.search.setObjectName("search"); self.search.setPlaceholderText(tr_("Suchen"))
        self.search_act = self.search.addAction(make_icon("search", 16), QLineEdit.TrailingPosition)
        self.search.setFixedWidth(250); self.search.setClearButtonEnabled(True)
        self._search_timer = QTimer(self, singleShot=True, interval=200)
        self._search_timer.timeout.connect(self.render)
        self.search.textChanged.connect(lambda: self._search_timer.start())
        tl.addWidget(self.btn_back); tl.addWidget(self.btn_fwd); tl.addSpacing(8)
        tl.addWidget(self.crumb); tl.addStretch(1); tl.addWidget(self.search)
        # wenn die Befehlsleiste ausgeblendet ist: ihre Funktionen über diese zwei Knöpfe oben
        self.top_queue = self._icon_btn("queue", 16, tr_("Wiedergabeliste rechts ein-/ausblenden (Strg+L)"),
                                        lambda on: self.set_queue_visible(on), checkable=True, obj="navbtn")
        self.top_menu = self._icon_btn("gear", 16, tr_("Menü"), None, obj="navbtn")
        self.top_menu.setPopupMode(QToolButton.InstantPopup)
        tl.addSpacing(4); tl.addWidget(self.top_queue); tl.addWidget(self.top_menu)
        tl.addSpacing(8)
        self.btn_min = self._icon_btn("minimize", 16, tr_("Minimieren"), self.showMinimized, obj="winbtn")
        self.btn_max = self._icon_btn("maximize", 16, tr_("Maximieren"), self.toggle_maximize, obj="winbtn")
        self.btn_close = self._icon_btn("close", 16, tr_("NeoNote beenden"), self.close, obj="closebtn")
        for b in (self.btn_min, self.btn_max, self.btn_close):
            tl.addWidget(b)
        root.addWidget(top)
        # Bei Videos: statt der Titelleiste nur Minimieren/Maximieren/Schließen oben rechts über dem Bild
        wb = DragBar(self); wb.setParent(central); wb.setObjectName("winbox"); self.winbox = wb
        wl = QHBoxLayout(wb); wl.setContentsMargins(12, 1, 2, 12); wl.setSpacing(0)   # unten Platz zum sanften Auslaufen
        self.ovl_title = QLabel(); self.ovl_title.setObjectName("ovlTitle"); self.ovl_title.setTextFormat(Qt.PlainText)
        wl.addWidget(self.ovl_title); wl.addStretch(1)
        self.ovl_min = self._icon_btn("minimize", 14, tr_("Minimieren"), self.showMinimized, obj="ovlwin")
        self.ovl_max = self._icon_btn("maximize", 14, tr_("Maximieren"), self.toggle_maximize, obj="ovlwin")
        self.ovl_close = self._icon_btn("close", 14, tr_("NeoNote beenden"), self.close, obj="ovlclose")
        for b in (self.ovl_min, self.ovl_max, self.ovl_close):
            wl.addWidget(b)
        wb.hide()

        cmd = QFrame(); cmd.setObjectName("cmdbar"); self.cmdbar = cmd
        cl = QHBoxLayout(cmd); cl.setContentsMargins(8, 2, 10, 2); cl.setSpacing(2)
        org = QToolButton(); org.setText(tr_("Organisieren  ▾")); org.setPopupMode(QToolButton.InstantPopup)
        m = QMenu(org)
        m.addAction(tr_("Datei öffnen…\tStrg+O"), self.open_dialog)
        m.addSeparator()
        m.addAction(tr_("Neue Wiedergabeliste…"), self.new_playlist)
        m.addAction(tr_("Wiedergabeliste importieren…"), self.import_playlist)
        m.addAction(tr_("Aktuelle Wiedergabeliste exportieren…"), lambda: self.export_playlist(None))
        m.addSeparator()
        m.addAction(tr_("Musikordner hinzufügen…"), self.add_folder)
        m.addAction(tr_("Bibliothek neu einlesen"), self.rescan)
        m.addSeparator()
        m.addAction(tr_("Fehlende Albuminfos und Cover suchen"), self.start_batch)
        m.addAction(tr_("Bibliothek prüfen…"), lambda: self.navigate("check"))
        m.addSeparator()
        m.addAction(tr_("Equalizer…\tStrg+E"), self.open_equalizer)
        m.addAction(tr_("Einstellungen…"), self.open_settings)
        m.addAction(tr_("Darstellung…"), lambda: self.open_settings(SettingsDialog.TAB_LOOK))
        m.addSeparator()
        m.addAction(tr_("Über {0}").format(APP_NAME), lambda: AboutDialog(self).exec())
        org.setMenu(m)
        tm = QMenu(self.top_menu)
        tm.addAction(tr_("Alle wiedergeben"), self.play_all_visible)
        tm.addSeparator()
        tm.addActions(m.actions())
        tm.addSeparator()
        tm.addAction(tr_("Befehlsleiste wieder einblenden"), lambda: self.set_cmdbar_visible(True))
        self.top_menu.setMenu(tm)
        playall = QToolButton(); playall.setText(tr_("Alle wiedergeben")); playall.clicked.connect(self.play_all_visible)
        cl.addWidget(org); cl.addWidget(playall); cl.addStretch()
        self.progress = QProgressBar(); self.progress.setFixedSize(180, 6); self.progress.setTextVisible(False)
        self.progress.hide()
        self.count_label = QLabel(); self.count_label.setObjectName("dim")
        gear = self._icon_btn("gear", 18, tr_("Einstellungen"), self.open_settings)
        self.btn_queue = self._icon_btn("queue", 18, tr_("Wiedergabeliste rechts ein-/ausblenden (Strg+L)"),
                                        lambda on: self.set_queue_visible(on), checkable=True)
        self.btn_cancel = self._icon_btn("clear", 14, tr_("Online-Suche abbrechen"), self.cancel_batch)
        self.btn_cancel.hide()
        cl.addWidget(self.progress); cl.addWidget(self.btn_cancel); cl.addSpacing(8); cl.addWidget(self.count_label); cl.addSpacing(6); cl.addWidget(self.btn_queue); cl.addWidget(gear)
        root.addWidget(cmd)

        # Hinweis auf eine neue Version (dezent, unter der Befehlsleiste)
        ub = QFrame(); ub.setObjectName("updatebar"); self.update_bar = ub
        ubl = QHBoxLayout(ub); ubl.setContentsMargins(14, 5, 6, 5); ubl.setSpacing(8)
        self.update_lbl = QLabel(); self.update_lbl.setTextFormat(Qt.PlainText)
        self.update_new = QPushButton(tr_("Was ist neu?")); self.update_new.setObjectName("ghost")
        self.update_go = QPushButton(tr_("Jetzt aktualisieren"))
        self.update_close = self._icon_btn("close", 12, tr_("Später"),
                                           lambda: (setattr(self, "_update_dismissed", True), self.update_bar.hide()))
        self.update_prog = QProgressBar(); self.update_prog.setFixedSize(140, 6); self.update_prog.setTextVisible(False)
        self.update_prog.hide()
        ubl.addWidget(self.update_lbl, 1); ubl.addWidget(self.update_prog); ubl.addWidget(self.update_new)
        ubl.addWidget(self.update_go); ubl.addWidget(self.update_close)
        self.update_new.clicked.connect(lambda: self._update_info and WhatsNewDialog(self, self._update_info).exec())
        self.update_go.clicked.connect(self._update_action)
        ub.hide()
        root.addWidget(ub)
        self._update_info = None
        self._update_file = None
        self._update_checker = None
        self._update_dl = None

        split = GripSplitter(self); self.split = split
        self.nav = QTreeWidget(); self.nav.setObjectName("nav"); self.nav.setHeaderHidden(True)
        self.nav.setIndentation(0); self.nav.setRootIsDecorated(False); self.nav.setItemsExpandable(False)
        self.nav.setMouseTracking(True); self.nav.setUniformRowHeights(False)
        self.nav.setItemDelegate(NavDelegate(self, self.nav))
        self.nav_items = {}
        self.build_nav()
        self.nav.viewport().installEventFilter(self)
        self.nav.setContextMenuPolicy(Qt.CustomContextMenu)
        self.nav.customContextMenuRequested.connect(self._nav_menu)
        self.nav.itemClicked.connect(self._nav_clicked)
        split.addWidget(self.nav)

        self.stack = QStackedWidget()
        self.grid = GridView()
        self.grid.setViewMode(QListView.IconMode); self.grid.setResizeMode(QListView.Adjust)
        self.grid.setMovement(QListView.Static); self.grid.setUniformItemSizes(False)
        self.grid.setFlow(QListView.LeftToRight); self.grid.setWrapping(True)
        self.grid.setSpacing(0); self.grid.setMouseTracking(True)
        self.grid.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.grid.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.grid.verticalScrollBar().setSingleStep(30)
        self.grid_model = QStandardItemModel(self)
        self.grid.setModel(self.grid_model)
        self.grid.setItemDelegate(TileDelegate(self.covers, self.grid))
        self.grid.activated.connect(self._grid_activated)
        self.grid.setContextMenuPolicy(Qt.CustomContextMenu)
        self.grid.setAcceptDrops(True); self.grid.viewport().setAcceptDrops(True)
        self.grid.viewport().installEventFilter(self)
        self.grid.customContextMenuRequested.connect(self._grid_menu)
        self.stack.addWidget(self.grid)

        self.tracks = TrackView(self)
        self.track_model = TrackModel(self)
        self.tracks.setModel(self.track_model)
        self.tracks.setup_columns(self.settings)
        self.tracks.activated.connect(self._track_activated)
        self.tracks.play_album.connect(lambda a: self.play_tracks(a["tracks"], 0))
        self.tracks.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tracks.customContextMenuRequested.connect(self._tracks_menu)
        self.tracks.header().sectionResized.connect(lambda *_: self._save_header_later())
        self._cover_relayout = QTimer(self, singleShot=True, interval=150)
        self._cover_relayout.timeout.connect(self._relayout_covers)
        self.tracks.header().sectionResized.connect(
            lambda li, *_: self._cover_relayout.start() if COLUMNS[li][0] == "cover" else None)
        self._hdr_timer = QTimer(self, singleShot=True, interval=800)
        self._hdr_timer.timeout.connect(lambda: self.settings.setValue("trackview/header", self.tracks.header().saveState()))
        self.stack.addWidget(self.tracks)

        self.empty = QLabel(); self.empty.setAlignment(Qt.AlignCenter); self.empty.setObjectName("empty")
        self.empty.setWordWrap(True)
        self.stack.addWidget(self.empty)
        self.radio = RadioPage(self)
        self.stack.addWidget(self.radio)
        self.check = CheckPage(self)
        self.stack.addWidget(self.check)
        self.video = VideoView(self)
        self.video.double_clicked.connect(self.toggle_fullscreen)
        self.video.activity.connect(self._fs_activity)
        self.stack.addWidget(self.video)
        split.addWidget(self.stack)

        qpanel = QFrame(); qpanel.setObjectName("queue"); self.qpanel = qpanel
        ql = QVBoxLayout(qpanel); ql.setContentsMargins(0, 0, 0, 0); ql.setSpacing(0)
        qh = QFrame(); qh.setObjectName("queueHead")
        qhl = QHBoxLayout(qh); qhl.setContentsMargins(12, 6, 6, 6)
        lbl = QLabel(tr_("Wiedergabeliste")); lbl.setObjectName("queueTitle")
        bclr = self._icon_btn("close", 14, tr_("Wiedergabeliste ausblenden (Strg+L)"), lambda: self.set_queue_visible(False))
        bsave = QToolButton(); bsave.setText(tr_("Liste ▾")); bsave.setToolTip(tr_("Liste speichern oder leeren"))
        bsave.setPopupMode(QToolButton.InstantPopup)
        qm = QMenu(bsave)
        qm.addAction(tr_("Als Wiedergabeliste speichern…"), self.save_queue_as_playlist)
        qm.addAction(tr_("Liste exportieren…"), lambda: self.export_playlist(None))
        qm.addSeparator()
        qm.addAction(tr_("Liste löschen"), self.clear_queue)
        bsave.setMenu(qm)
        lbl.setMinimumWidth(40)
        qhl.addWidget(lbl, 1); qhl.addWidget(bsave); qhl.addWidget(bclr)
        ql.addWidget(qh)
        self.qlist = QListWidget(); self.qlist.setObjectName("qlist")
        self.qlist.setItemDelegate(QueueDelegate(self, self.qlist))
        self.qlist.setMouseTracking(True)
        self.qlist.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.qlist.setDragDropMode(QAbstractItemView.InternalMove)
        self.qlist.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.qlist.itemActivated.connect(lambda it: self.play_entry(self.entry_of(it.data(Qt.UserRole))))
        self.qlist.model().rowsMoved.connect(self._queue_reordered)
        self.qlist.setContextMenuPolicy(Qt.CustomContextMenu)
        self.qlist.customContextMenuRequested.connect(self._queue_menu)
        QShortcut(QKeySequence.Delete, self.qlist, self.remove_selected_from_queue, context=Qt.WidgetShortcut)
        ql.addWidget(self.qlist, 1)
        self.qfoot = QLabel(); self.qfoot.setObjectName("qfoot")
        ql.addWidget(self.qfoot)
        split.addWidget(qpanel)
        split.setStretchFactor(0, 0); split.setStretchFactor(1, 1); split.setStretchFactor(2, 0)
        self.nav.setMinimumWidth(150); self.qpanel.setMinimumWidth(200); self.stack.setMinimumWidth(320)
        state = self.settings.value("layout/splitter")
        if not (state and split.restoreState(state)):
            split.setSizes([215, 865, 280])
        self._split_timer = QTimer(self, singleShot=True, interval=600)
        self._split_timer.timeout.connect(lambda: self.settings.setValue("layout/splitter", self.split.saveState()))
        split.splitterMoved.connect(lambda *_: self._split_timer.start())
        root.addWidget(split, 1)

        self.controls = self._build_controls()
        root.addWidget(self.controls)
        # weiches Scrollen in den Listen
        self._smooth = [SmoothScroll(self.tracks, ROWH * 4), SmoothScroll(self.grid, 110),
                        SmoothScroll(self.qlist, 110), SmoothScroll(self.nav, 80)]
        self.setCentralWidget(central)
        self.central = central
        central.setMouseTracking(True)
        central.installEventFilter(self)

        QShortcut(QKeySequence(Qt.Key_Escape), self, lambda: self._fs and self.toggle_fullscreen())
        self._xbuttons = MouseNavFilter(self)                 # Maustasten Zurück/Vor
        QApplication.instance().installEventFilter(self._xbuttons)
        self.queue_visible = self.settings.value("layout/queue", True, type=bool)
        self.btn_queue.setChecked(self.queue_visible); self.top_queue.setChecked(self.queue_visible)
        self.qpanel.setVisible(self.queue_visible)
        for seq, slot in (("Ctrl+L", lambda: self.set_queue_visible(not self.queue_visible)),
                          ("F11", self.toggle_fullscreen), ("Ctrl+O", self.open_dialog), ("Ctrl+M", self.show_mini), ("Ctrl+E", self.open_equalizer),
                          ("Ctrl+P", self.toggle_play), ("Ctrl+Right", self.next_track),
                          ("Ctrl+Left", self.prev_track), ("Ctrl+F", self.search.setFocus),
                          ("Alt+Left", self.go_back), ("Alt+Right", self.go_forward),
                          (Qt.Key_MediaPlay, self.toggle_play), (Qt.Key_MediaTogglePlayPause, self.toggle_play),
                          (Qt.Key_MediaNext, self.next_track), (Qt.Key_MediaPrevious, self.prev_track),
                          (Qt.Key_MediaStop, self.stop)):
            QShortcut(QKeySequence(seq), self, slot)

    def set_cmdbar_visible(self, on):
        d = dict(self.theme_dict); d["cmdbar"] = bool(on)
        self.apply_theme(d)
        self.save_theme(d)

    def _apply_cmdbar(self):
        on = bool(self.theme_dict.get("cmdbar", True))
        if not (self.np_mode or self._fs):
            self.cmdbar.setVisible(on)
        self.top_queue.setVisible(not on); self.top_menu.setVisible(not on)

    def set_queue_visible(self, on):
        """Wiedergabeliste rechts ein-/ausblenden (wird gemerkt)."""
        self.queue_visible = bool(on)
        self.settings.setValue("layout/queue", self.queue_visible)
        self.btn_queue.setChecked(self.queue_visible)
        self.top_queue.setChecked(self.queue_visible)
        if not self.np_mode:
            self.qpanel.setVisible(self.queue_visible)

    def reset_panel_sizes(self):
        """Doppelklick auf einen Teiler: Standardbreiten wiederherstellen."""
        total = sum(self.split.sizes())
        self.split.setSizes([215, max(320, total - 215 - 280), 280])
        self.settings.setValue("layout/splitter", self.split.saveState())

    def _save_header_later(self):
        self._hdr_timer.start()

    def _build_controls(self):
        bar = QFrame(); bar.setObjectName("controls"); bar.setFixedHeight(82)
        v = QVBoxLayout(bar); v.setContentsMargins(14, 6, 14, 6); v.setSpacing(2)
        seekrow = QHBoxLayout(); seekrow.setSpacing(10)
        self.seek = JumpSlider(Qt.Horizontal); self.seek.setObjectName("seek"); self.seek.setRange(0, 0)
        self.seek.seeked.connect(self._user_seek)
        self.seek.sliderMoved.connect(lambda v: self._update_time(v))
        seekrow.addWidget(self.seek, 1)
        v.addLayout(seekrow)

        row = QHBoxLayout(); row.setSpacing(4)
        info = QHBoxLayout(); info.setSpacing(10)
        self.np_cover = QLabel(); self.np_cover.setFixedSize(42, 42)
        tv = QVBoxLayout(); tv.setSpacing(0)
        self.np_title = QLabel(tr_("Keine Wiedergabe")); self.np_title.setObjectName("npTitle")
        self.np_artist = QLabel(""); self.np_artist.setObjectName("dim")
        for _l in (self.np_title, self.np_artist):        # Titel aus Dateien nie als HTML deuten
            _l.setTextFormat(Qt.PlainText)
        tv.addStretch(); tv.addWidget(self.np_title); tv.addWidget(self.np_artist); tv.addStretch()
        self.np_wave = WaveView(64, 42); self.np_wave.clicked.connect(self._toggle_vis)
        self.np_cover.setCursor(Qt.PointingHandCursor); self.np_cover.setToolTip(tr_("Klicken: Cover / Waveform"))
        self.np_cover.mousePressEvent = lambda e: e.button() == Qt.LeftButton and self._toggle_vis()
        info.addWidget(self.np_cover); info.addWidget(self.np_wave); info.addLayout(tv)
        self._vis_mode = self.settings.value("ui/vis_mode", "auto")     # auto | cover | wave
        self._vis_timer = QTimer(self, interval=40); self._vis_timer.timeout.connect(self._vis_tick)
        infow = QWidget(); infow.setLayout(info); infow.setFixedWidth(320); self._ctl_left = infow
        row.addWidget(infow); row.addStretch()

        self.btn_shuffle = self._icon_btn("shuffle", 20, tr_("Zufällige Wiedergabe"), self.toggle_shuffle, True, "ctl")
        self.btn_repeat = QToolButton(); self.btn_repeat.setObjectName("ctl"); self.btn_repeat.setCheckable(True)
        self.btn_repeat.setIconSize(QSize(20, 20)); self.btn_repeat.clicked.connect(self.cycle_repeat)
        self.btn_stop = self._icon_btn("stop", 20, tr_("Beenden"), self.stop, obj="ctl")
        self.btn_prev = self._icon_btn("prev", 22, tr_("Zurück"), self.prev_track, obj="ctl")
        self.btn_play = PlayButton(); self.btn_play.setToolTip(tr_("Wiedergabe / Pause")); self.btn_play.clicked.connect(self.toggle_play)
        self.btn_next = self._icon_btn("next", 22, tr_("Weiter"), self.next_track, obj="ctl")
        self.btn_mute = QToolButton(); self.btn_mute.setObjectName("ctl"); self.btn_mute.setIconSize(QSize(20, 20))
        self.btn_mute.setToolTip(tr_("Stumm")); self.btn_mute.clicked.connect(self.toggle_mute)
        self.vol = JumpSlider(Qt.Horizontal); self.vol.setObjectName("vol"); self.vol.setRange(0, 100); self.vol.setFixedWidth(96)
        self.vol.valueChanged.connect(self._set_volume)
        # Zeitanzeige wie im WMP12: „33:44 / 58:35“ – Klick wechselt auf Restzeit
        self.lbl_time = QToolButton(); self.lbl_time.setObjectName("timeBtn")
        self.lbl_time.setToolTip(tr_("Klicken: verstrichene Zeit / Restzeit"))
        self.lbl_time.clicked.connect(self._toggle_remaining)
        self._time_remaining = self.settings.value("ui/time_remaining", False, type=bool)
        self.lbl_time.setText("0:00 / 0:00")
        # feste Breite nach Schrift, damit nichts springt, aber eng an den Knöpfen
        self.lbl_time.setFixedWidth(QFontMetrics(self.lbl_time.font()).horizontalAdvance("00:00 / 00:00") + 10)
        # Mittelgruppe: Zeit | Knöpfe | Lautstärke – als kompakter Block mittig
        ctr = QWidget(); self._ctl_center = ctr
        cl = QHBoxLayout(ctr); cl.setContentsMargins(0, 0, 0, 0); cl.setSpacing(4)
        cl.addWidget(self.lbl_time); cl.addSpacing(2)
        cl.addWidget(self.btn_shuffle); cl.addWidget(self.btn_repeat); cl.addSpacing(12)
        for w in (self.btn_stop, self.btn_prev, self.btn_play, self.btn_next):
            cl.addWidget(w)
        cl.addSpacing(12); cl.addWidget(self.btn_mute); cl.addWidget(self.vol)
        # Gegengewicht: Knöpfe + Lautstärke sind rechts breiter als Zeit + Zufall/Wiederholen links
        self._ctl_pad = QWidget(); self._ctl_pad.setFixedWidth(0); cl.addWidget(self._ctl_pad)
        row.addWidget(ctr)
        row.addStretch()
        rightw = QWidget(); rightw.setFixedWidth(320); self._ctl_right = rightw
        rl = QHBoxLayout(rightw); rl.setContentsMargins(0, 0, 0, 0); rl.setSpacing(2); rl.addStretch()
        self.btn_tracks = QToolButton(); self.btn_tracks.setObjectName("ctl"); self.btn_tracks.setText(tr_("Spuren"))
        self.btn_tracks.setPopupMode(QToolButton.InstantPopup); self.btn_tracks.setToolTip(tr_("Tonspur und Untertitel"))
        self.btn_tracks.hide()
        self.btn_mode = QToolButton(); self.btn_mode.setObjectName("ctl"); self.btn_mode.setIconSize(QSize(18, 18))
        self.btn_mode.clicked.connect(self.toggle_np_mode)
        self.btn_mini = self._icon_btn("mini", 18, tr_("Mini-Player (Strg+M)"), self.show_mini, obj="ctl")
        self.btn_eq = self._icon_btn("eq", 18, tr_("Equalizer (Strg+E)"), self.open_equalizer, obj="ctl")
        rl.addWidget(self.btn_tracks); rl.addWidget(self.btn_eq); rl.addWidget(self.btn_mini); rl.addWidget(self.btn_mode)
        row.addWidget(rightw)
        v.addLayout(row)
        bar.installEventFilter(self)
        return bar

    def _layout_controls(self):
        """Seitenbereiche gleich breit halten (schrumpfen bei kleinen Fenstern), Play-Button exakt mittig."""
        c = self.controls
        if not hasattr(self, "_ctl_center"):
            return
        cw = self._ctl_center.layout().sizeHint().width()
        side = int(max(150, min(320, (c.width() - 28 - cw) / 2 - 6)))
        if self._ctl_left.width() != side:
            self._ctl_left.setFixedWidth(side); self._ctl_right.setFixedWidth(side)

    def _build_player(self):
        use_mpv = self.settings.value("audio/mpv", True, type=bool) and mpv_available()
        self.player = Engine(self, use_mpv)
        self.audio = self.player.audio
        self.player.setVideoSink(self.video.sink)
        self.player.advanced.connect(self._gapless_advanced)
        self._next_entry = None
        self.apply_audio_settings()
        self.player.hasVideoChanged.connect(self._has_video_changed)
        self.player.metaDataChanged.connect(self._meta_changed)
        self.player.tracksChanged.connect(self._tracks_changed)
        self._update_mode_btn()
        self.player.positionChanged.connect(self._pos_changed)
        self.player.durationChanged.connect(self._dur_changed)
        self.player.playbackStateChanged.connect(self._state_changed)
        self.sleep_guard = SleepGuard()
        self.player.hasVideoChanged.connect(self.update_sleep_guard)
        self.player.mediaStatusChanged.connect(self._status_changed)
        self.player.errorOccurred.connect(lambda _e, msg: self.flash(tr_("Wiedergabefehler: {0}").format(msg)))
        self.vol.setValue(self.settings.value("volume", 70, type=int))
        self._set_volume(self.vol.value())
        self.btn_shuffle.setChecked(self.shuffle)
        self._update_repeat_btn()
        self._update_vis()

    def flash(self, msg, ms=6000):
        self.count_label.setTextFormat(Qt.PlainText)
        self.count_label.setText(msg)
        QTimer.singleShot(ms, self._update_count)

    # ── Navigation ────────────────────────────────────────────────────────
    def navigate(self, state, push=True):
        if state == "playing":
            self.enter_np_mode()
            return
        if self.np_mode:
            self.exit_np_mode()
        if push:
            self.history = self.history[:self.hpos + 1]
            if not self.history or self.history[-1] != state:
                self.history.append(state)
            self.hpos = len(self.history) - 1
        self.state = state
        if self.search.text():
            self.search.blockSignals(True); self.search.clear(); self.search.blockSignals(False)
        self.render()
        if self.stack.currentWidget() is self.tracks:
            self.tracks.scrollToTop()
        else:
            self.grid.scrollToTop()

    def go_back(self):
        if self.hpos > 0:
            self.hpos -= 1
            self.navigate(self.history[self.hpos], push=False)

    def go_forward(self):
        if self.hpos < len(self.history) - 1:
            self.hpos += 1
            self.navigate(self.history[self.hpos], push=False)

    def _nav_clicked(self, item, _col):
        st = item.data(0, Qt.UserRole)
        kind = item.data(0, NAV_KIND)
        if kind in ("sep", None) and not st:
            return
        if st == "queue":
            if self.qpanel.isHidden():
                self.set_queue_visible(True)
            self.qlist.setFocus()
        elif st == "playlists":
            if not self.playlist_names():
                self.new_playlist()
        elif st == "autohead":
            return
        elif st == "jellyfin":
            if self.jf:
                self.navigate("jf:artists")
            else:
                self.open_settings(SettingsDialog.TAB_JF)
        elif st == "jf:connect":
            self.open_settings(SettingsDialog.TAB_JF)
        else:
            self.navigate(st)

    def _render_crumbs(self):
        st = self.state
        parts = [(tr_("Medienbibliothek"), "artists"), (tr_("Musik"), "artists")]
        if st.startswith("jf:"):
            sub = st[3:]
            parts = [("Jellyfin", "jf:artists")]
            if sub in VIEW_NAMES:
                parts.append((VIEW_NAMES[sub], None))
            elif sub.startswith("artist:"):
                parts += [(tr_("Interpret"), "jf:artists"), (sub[7:], None)]
            elif sub.startswith("genre:"):
                parts += [(tr_("Genre"), "jf:genres"), (sub[6:], None)]
            elif sub.startswith("album:"):
                a = self.jf_lib.albums.get(sub[6:])
                parts += [(tr_("Album"), "jf:albums"), (a["title"] if a else "?", None)]
            elif sub.startswith("playlist:"):
                pl = next((p for p in self.jf_lib.playlists if p["id"] == sub[9:]), None)
                parts += [(tr_("Wiedergabelisten"), None), (pl["name"] if pl else "?", None)]
            st = "\x00"
        if st == "\x00":
            pass
        elif st == "playing":
            parts = [(tr_("Wird gespielt"), None)]
        elif st in VIEW_NAMES:
            parts.append((VIEW_NAMES[st], None))
        elif st.startswith("artist:"):
            parts += [(tr_("Interpret"), "artists"), (st[7:], None)]
        elif st.startswith("genre:"):
            parts += [(tr_("Genre"), "genres"), (st[6:], None)]
        elif st.startswith("playlist:"):
            parts = [(tr_("Medienbibliothek"), "artists"), (tr_("Wiedergabelisten"), None), (st[9:], None)]
        elif st == "auto:recent":
            parts = [(tr_("Medienbibliothek"), "artists"), (tr_("Zuletzt gespielt"), None)]
        elif st.startswith("auto:"):
            parts = [(tr_("Medienbibliothek"), "artists"), (tr_("Automatische Listen"), None),
                     (AUTO_LISTS.get(st[5:], "?"), None)]
        elif st == "radio":
            parts = [(tr_("Medienbibliothek"), "artists"), (tr_("Internetradio"), None)]
        elif st == "check":
            parts = [(tr_("Medienbibliothek"), "artists"), (tr_("Bibliothek prüfen"), None)]
        elif st.startswith("album:"):
            a = self.lib.albums.get(st[6:])
            parts += [(tr_("Album"), "albums"), (a["title"] if a else "?", None)]
        out = []
        for text, link in parts:
            t = html.escape(text)
            if link:
                out.append(f'<a href="{html.escape(link, quote=True)}" style="color:{T.fg.name()};'
                           f'text-decoration:none">{t}</a>')
            else:
                out.append(f'<span style="color:{T.fg.name()}">{t}</span>')
        self.crumb.setText(f'<span style="color:{T.dim.name()}">&nbsp;&nbsp;›&nbsp;&nbsp;</span>'.join(out))

    def render(self):
        st = self.state
        # Jellyfin-Ansichten heißen „jf:…“ und zeigen die zweite Bibliothek mit denselben Ansichten
        self._src = "jf" if st.startswith("jf:") else "local"
        q = self.search.text().strip().lower()
        self._render_crumbs()
        self.btn_back.setEnabled(self.hpos > 0)
        self.btn_fwd.setEnabled(self.hpos < len(self.history) - 1)
        pre = "jf:" if self._src == "jf" else ""
        if pre:
            st = st[3:]
        base = st.split(":")[0]
        nk = {"artist": "artists", "genre": "genres", "album": "albums"}.get(base, base)
        if st.startswith(("playlist:", "auto:")):
            nk = st
        nk = pre + nk
        if nk in self.nav_items:
            self.nav.setCurrentItem(self.nav_items[nk])
        if pre and st.startswith("playlist:"):
            pl = next((p for p in self.jf_lib.playlists if p["id"] == st[9:]), None)
            byid = self.jf_lib.by_id()
            tracks = [byid[i] for i in (pl["items"] if pl else []) if i in byid]
            if q:
                tracks = [t for t in tracks if q in t["title"].lower() or q in t["artist"].lower()
                          or q in t["album"].lower()]
            if self.sort_col is not None:
                tracks = self._sorted(tracks)
            self.track_model.set_flat(tracks)
            self._update_sort_indicator()
            self.stack.setCurrentWidget(self.tracks)
            self._update_count()
            return
        if pre and not self.jf_lib.tracks:
            self.empty.setText(tr_("Die Jellyfin-Bibliothek wird geladen …") if self.jf else
                               tr_("Noch kein Jellyfin-Server verbunden.\n\nEinstellungen ▸ Jellyfin"))
            self.stack.setCurrentWidget(self.empty)
            self.count_label.setText("")
            return

        if st == "check":
            self.stack.setCurrentWidget(self.check)
            if self.check.res is None:
                self.check.run()
            self.count_label.setText("")
            return

        if st == "radio":
            self.radio.reload()
            self.stack.setCurrentWidget(self.radio)
            self.count_label.setText(tr_("{0} Sender").format(self.radio.count()))
            return

        if st.startswith("auto:"):
            tracks = self.auto_tracks(st[5:])
            if q:
                tracks = [t for t in tracks if q in t["title"].lower() or q in t["artist"].lower()
                          or q in t["album"].lower()]
            if self.sort_col is not None:
                tracks = self._sorted(tracks)
            if not tracks and not q:
                self.empty.setText({
                    "recent": tr_("Hier erscheinen die Titel, die du zuletzt gehört hast."),
                    "favs": tr_("Hier erscheinen alle Titel, die du mit 4 oder 5 Sternen bewertet hast."),
                    "top": tr_("Hier erscheinen deine meistgespielten Titel."),
                    "new": tr_("Hier erscheinen die zuletzt hinzugefügten Titel.")}.get(st[5:], ""))
                self.stack.setCurrentWidget(self.empty)
                self.count_label.setText(tr_("0 Titel"))
                return
            self.track_model.set_flat(tracks)
            self._update_sort_indicator()
            self.stack.setCurrentWidget(self.tracks)
            self._update_count()
            return

        if st.startswith("playlist:"):
            tracks = self.playlist_tracks(st[9:])
            orig = list(range(len(tracks)))
            pairs = list(zip(orig, tracks))
            if q:
                pairs = [(i, t) for i, t in pairs if q in t["title"].lower() or q in t["artist"].lower()
                         or q in t["album"].lower()]
            if self.sort_col is not None:
                key = self._sort_key(COLUMNS[self.sort_col][0])
                pairs.sort(key=lambda it: key(it[1]), reverse=self.sort_desc)
            self.track_model.set_flat([t for _i, t in pairs], [i for i, _t in pairs])
            self._update_sort_indicator()
            self.stack.setCurrentWidget(self.tracks)
            self._update_count()
            return

        if not self.lib.tracks:
            self.empty.setText(
                tr_("Die Bibliothek ist leer.\n\nÜber „Organisieren ▸ Musikordner hinzufügen…“ kannst du deine Musik einbinden.")
                if not self.folders() else tr_("Bibliothek wird eingelesen …") if self.scanner else
                tr_("In den Musikordnern wurden keine Audiodateien gefunden."))
            self.stack.setCurrentWidget(self.empty)
            self.count_label.setText("")
            return

        if st == "songs":
            albums = list(self.lib.albums.values())
        elif st.startswith("artist:"):
            albums = sorted((a for a in self.lib.albums.values() if a["artist"] == st[7:]),
                            key=lambda a: (a["year"] or "9999", a["title"].lower()))
        elif st.startswith("album:"):
            a = self.lib.albums.get(st[6:])
            albums = [a] if a else []
        else:
            self._render_grid(st, q)
            return
        groups = []
        for a in albums:
            tl = a["tracks"]
            if q:
                tl = [t for t in tl if q in t["title"].lower() or q in t["artist"].lower()
                      or q in t["album"].lower() or q in (t.get("composer") or "").lower()]
            if tl:
                groups.append((a, tl))
        if self.sort_col is not None:
            self.track_model.set_flat(self._sorted([t for _a, tl in groups for t in tl]))
        else:
            ci = next(i for i, c in enumerate(COLUMNS) if c[0] == "cover")
            self.track_model.block_h = album_block(self.tracks.header().sectionSize(ci))[2]
            self.track_model.set_groups(groups)
            self.tracks.apply_spans()
        self._update_sort_indicator()
        self.stack.setCurrentWidget(self.tracks)
        self._update_count()

    def _update_count(self):
        if self.scanner:
            return
        if self.stack.currentWidget() is self.tracks:
            tl = self.track_model.tracks
            self.count_label.setText(tr_("{0} Titel  ·  {1}").format(len(tl), fmt_time(sum(t['length'] for t in tl))))
        elif self.stack.currentWidget() is self.grid:
            noun = {"artists": tr_("Interpreten@n"), "genres": tr_("Genres@n")}.get(self.state.replace("jf:", "", 1), tr_("Alben@n"))
            self.count_label.setText(f"{getattr(self, '_grid_count', 0)} {noun}")

    @staticmethod
    def _fmt_duration(sec):
        if sec < 3600:
            m = max(1, round(sec / 60))
            return tr_("{0} Minute").format(m) if m == 1 else tr_("{0} Minuten").format(m)
        return tr_("{0} Stunden").format(f"{sec / 3600:.1f}".replace(".", "," if LANG == "de" else "."))

    def _avg_rating(self, tracks):
        rs = [self.stats.rating(t["path"]) for t in tracks]
        rs = [r for r in rs if r]
        return sum(rs) / len(rs) if rs else 0

    def _render_grid(self, st, q):
        self.grid_model.clear()
        sections = OrderedDict()          # Überschrift -> Kacheln
        if st in ("artists", "genres"):
            field = "artist" if st == "artists" else "genre"
            for name, albums in self.lib.group_albums(field).items():
                albums = sorted(albums, key=lambda a: a["year"] or "0000", reverse=True)
                tracks = [t for a in albums for t in a["tracks"]]
                n = len(tracks)
                songs = tr_("{0} Song").format(n) if n == 1 else tr_("{0} Songs").format(n)
                lines = [songs if len(albums) == 1 else tr_("{0} Alben, {1} Titel").format(len(albums), n),
                         self._fmt_duration(sum(t["length"] for t in tracks))]
                sections.setdefault(index_letter(name), []).append(
                    ("artist" if st == "artists" else "genre", name, lines,
                     [a["key"] for a in albums], name, self._avg_rating(tracks)))
        else:
            if st.startswith("genre:"):
                albums = [a for a in self.lib.albums.values() if a["genre"] == st[6:]]
            else:
                albums = list(self.lib.albums.values())
            for a in albums:
                yl = a["year"] or tr_("Unbekanntes Jahr")
                if a.get("edition"):                       # getrennte Ausgaben (FLAC/MP3) unterscheidbar machen
                    yl = f"{yl} · {a['edition']}"
                lines = [disp(a["artist"]), disp(a["genre"]) or tr_("Unbekanntes Genre"), yl]
                sections.setdefault(a["artist"], []).append(
                    ("album", a["title"], lines, [a["key"]], a["key"], self._avg_rating(a["tracks"])))
        n = 0
        seps, tile_size = [], QSize(TILE_W, TILE_H)
        sep_w = max(TILE_W, self.grid.viewport().width() - 2)
        self._grid_seps, self._grid_sep_w = seps, sep_w
        for head, items in sections.items():
            items = [x for x in items if not q or q in x[1].lower() or any(q in l.lower() for l in x[2])]
            if not items:
                continue
            sep = QStandardItem(head); sep.setEditable(False)
            sep.setFlags(Qt.ItemIsEnabled); sep.setData("sep", ROLE_KIND)
            sep.setData(QSize(sep_w, 36), Qt.SizeHintRole)
            self.grid_model.appendRow(sep)
            seps.append(sep)
            for kind, title, lines, keys, key, rating in items:
                it = QStandardItem(disp(title)); it.setEditable(False)
                it.setData(tile_size, Qt.SizeHintRole)
                it.setData(kind, ROLE_KIND); it.setData(keys, ROLE_COVERS); it.setData(lines, ROLE_SUB)
                it.setData(key, ROLE_KEY); it.setData(rating, ROLE_RATING)
                it.setToolTip(title + "\n" + "\n".join(lines))
                self.grid_model.appendRow(it)
                n += 1
        self._grid_count = n
        # Cover aller Kacheln im Hintergrund vorladen, damit Scrollen nicht auf die Festplatte warten muss
        pre = []
        for r in range(self.grid_model.rowCount()):
            ks = self.grid_model.item(r).data(ROLE_COVERS)
            if ks:
                pre.extend(ks[:5])
        self.covers.prefetch(pre, ART)
        self.stack.setCurrentWidget(self.grid)
        self._update_count()

    # ── Aktionen in den Ansichten ─────────────────────────────────────────
    def tracks_for_item(self, kind, key):
        if kind == "album":
            a = self.lib.albums.get(key)
            return list(a["tracks"]) if a else []
        field = "artist" if kind == "artist" else "genre"
        albums = sorted((a for a in self.lib.albums.values() if a[field] == key),
                        key=lambda a: (a["year"] or "9999", a["title"].lower()))
        return [t for a in albums for t in a["tracks"]]

    def _grid_activated(self, idx):
        kind, key = idx.data(ROLE_KIND), idx.data(ROLE_KEY)
        if kind == "sep":
            return
        self.navigate(("jf:" if self._src == "jf" else "") + {"artist": "artist:", "genre": "genre:"}.get(kind, "album:") + key)

    def _grid_menu(self, pos):
        idx = self.grid.indexAt(pos)
        if not idx.isValid() or idx.data(ROLE_KIND) == "sep":
            return
        if not self.grid.selectionModel().isSelected(idx):
            self.grid.setCurrentIndex(idx)
        tracks = []
        for i in sorted(self.grid.selectionModel().selectedIndexes(), key=lambda i: i.row()):
            tracks += self.tracks_for_item(i.data(ROLE_KIND), i.data(ROLE_KEY))
        kind, key = idx.data(ROLE_KIND), idx.data(ROLE_KEY)
        album = self.lib.albums.get(key) if kind == "album" else None
        group = None
        if kind in ("artist", "genre"):
            group = [a for a in self.lib.albums.values() if a["artist" if kind == "artist" else "genre"] == key]
        self._track_menu(self.grid, tracks, pos, open_idx=idx, album=album, group=group)

    def _tracks_menu(self, pos):
        idx = self.tracks.indexAt(pos)
        album = self.track_model.rows[idx.row()][1] if idx.isValid() else None
        self._track_menu(self.tracks, self.tracks.selected_tracks(), pos, album=album)

    def _track_menu(self, view, tracks, pos, open_idx=None, album=None, group=None):
        if not tracks:
            return
        m = QMenu(self)
        m.addAction(make_icon("play", 14), tr_("Wiedergeben"), lambda: self.play_tracks(tracks, 0))
        m.addAction(tr_("Als Nächstes wiedergeben"), lambda: self.add_tracks(tracks, next_up=True))
        self._playlist_menu_into(m, tracks)
        if view is self.tracks:
            idx = self.tracks.currentIndex()
            if idx.isValid() and self.track_model.flags(idx) & Qt.ItemIsEditable:
                m.addAction(tr_("Bearbeiten\tF2"), lambda: self.tracks.edit(idx))
        if view is self.tracks and self.state.startswith("playlist:"):
            name = self.state[9:]
            rows = sorted({i.row() for i in self.tracks.selectionModel().selectedIndexes()})
            orig = [self.track_model.orig[self.track_model.rows[r][5]] for r in rows]
            m.addAction(tr_("Aus Wiedergabeliste entfernen"), lambda: self.remove_from_playlist(name, orig))
        if open_idx is not None:
            m.addSeparator(); m.addAction(tr_("Öffnen"), lambda: self._grid_activated(open_idx))
        else:
            rm = m.addMenu(tr_("Bewerten"))
            for n in range(5, -1, -1):
                rm.addAction("★" * n + "☆" * (5 - n) if n else tr_("Keine Bewertung"),
                             lambda n=n: self.set_rating(tracks, n))
        m.addSeparator()
        if tracks[0].get("remote"):
            m.addAction(make_icon("download", 14), tr_("Offline speichern"), lambda: self.jf_make_offline(tracks))
            if any(self.jf_lib.offline_path(t) for t in tracks):
                m.addAction(tr_("Offline-Kopie löschen"), lambda: self.jf_drop_offline(tracks))
            m.exec(view.viewport().mapToGlobal(pos))
            return
        if album is not None:
            m.addAction(tr_("Albuminformationen suchen…"), lambda: self.lookup_album(album))
            cm = m.addMenu(tr_("Albumcover"))
            cm.addAction(tr_("Bild auswählen…"), lambda: self.change_cover_dialog(album))
            clip = QApplication.clipboard().mimeData()
            ca = cm.addAction(tr_("Aus der Zwischenablage einfügen"),
                              lambda: self.set_album_cover(album, image_from_mime(QApplication.clipboard().mimeData())))
            ca.setEnabled(mime_has_image(clip))
            cm.addSeparator()
            hint = cm.addAction(tr_("Tipp: Bild einfach auf das Cover ziehen")); hint.setEnabled(False)
        if group:
            m.addAction(tr_("Fehlende Infos für alle {0} Alben suchen").format(len(group)), lambda: self.start_batch(group))
        first = tracks[0]["path"]
        m.addAction(tr_("Dateispeicherort öffnen"), lambda: show_in_file_manager(first))
        if open_idx is None:
            m.addAction(tr_("Dateipfad kopieren"), lambda: QApplication.clipboard().setText(
                "\n".join(t["path"] for t in tracks)))
        m.exec(view.viewport().mapToGlobal(pos))

    def _track_activated(self, idx):
        row = self.track_model.rows[idx.row()]
        if row[0] == "track":
            self.play_tracks(self.track_model.tracks, row[5])

    def set_rating(self, tracks, n):
        for t in tracks:
            self.stats.set_rating(t["path"], n)
        self.track_model.refresh()
        remote = [t for t in tracks if t.get("remote")]
        if remote:                               # 4–5 Sterne = Favorit auf dem Jellyfin-Server
            self.jf_set_favorite(remote, n >= 4)

    def play_all_visible(self):
        if self.stack.currentWidget() is self.tracks:
            tracks = list(self.track_model.tracks)
        else:
            tracks = []
            for r in range(self.grid_model.rowCount()):
                i = self.grid_model.index(r, 0)
                if i.data(ROLE_KIND) != "sep":
                    tracks += self.tracks_for_item(i.data(ROLE_KIND), i.data(ROLE_KEY))
        if tracks:
            self.play_tracks(tracks, 0)

    # ── Bibliothek verwalten ──────────────────────────────────────────────
    def folders(self):
        v = self.settings.value("folders", [])
        if isinstance(v, str):
            v = [v]
        return [f for f in (v or []) if f]

    def add_folder(self):
        d = QFileDialog.getExistingDirectory(self, tr_("Musikordner wählen"), str(Path.home()))
        if d:
            fl = self.folders()
            if d not in fl:
                fl.append(d); self.settings.setValue("folders", fl)
            self.rescan()

    def rescan(self, quiet=False, full=False):
        if self.scanner or self.batch:
            if quiet:
                self._watch_timer.start()
            return
        self._quiet_scan = quiet
        folders = self.folders()
        if not folders and not self.extra_files():
            self.local_lib.set_tracks([]); self.local_lib.save(); self.render(); return
        known = {} if full else {t["path"]: t for t in self.local_lib.tracks}
        self.scanner = Scanner(folders, self, self.extra_files(), known)
        self.scanner.progress.connect(self._scan_progress)
        self.scanner.finished_scan.connect(self._scan_done)
        self.scanner.dirs_found.connect(self._watch_dirs)
        if not quiet:
            self.progress.setRange(0, 0); self.progress.show()
        self.scanner.start()
        if not quiet:
            self.render()

    def _watch_dirs(self, dirs):
        if not self.settings.value("library/watch", True, type=bool):
            if self.watcher.directories():
                self.watcher.removePaths(self.watcher.directories())
            return
        old = set(self.watcher.directories())
        new = set(dirs[:20000])
        if old - new:
            self.watcher.removePaths(list(old - new))
        if new - old:
            self.watcher.addPaths(list(new - old))

    def _scan_progress(self, i, total):
        if self._quiet_scan:
            return
        self.progress.setRange(0, max(1, total)); self.progress.setValue(i)
        self.count_label.setText(tr_("Lese ein … {0}/{1}").format(i, total))

    def _scan_done(self, tracks):
        changed = self.scanner.changed or len(tracks) != len(self.local_lib.tracks)
        self.scanner.wait(); self.scanner = None
        self.progress.hide()
        self.local_lib.outdated = False
        if self._quiet_scan and not changed:
            self._update_count()
            return
        self.covers.clear()
        self.local_lib.set_tracks(tracks); self.local_lib.save()
        if hasattr(self, "check"):
            self.check.res = None
        # Bewertungen aus dem Windows Media Player übernehmen (nur wo NeoNote noch keine hat)
        took = 0
        for t in tracks:
            if t.get("wr") and not self.stats.rating(t["path"]):
                self.stats.set_rating(t["path"], t["wr"]); took += 1
        if took:
            self.flash(tr_("{0} Bewertungen aus den Dateien übernommen").format(took))
        if self.np_mode:
            return
        st = self.state
        gone = (st.startswith("artist:") and not any(a["artist"] == st[7:] for a in self.lib.albums.values())) or \
               (st.startswith("album:") and st[6:] not in self.lib.albums) or \
               (st.startswith("genre:") and not any(a["genre"] == st[6:] for a in self.lib.albums.values()))
        if gone:
            self.navigate("artists")
        elif self._quiet_scan:
            self._refresh_library()
        else:
            self.render()

    # ── Wiedergabeliste ───────────────────────────────────────────────────
    def _new_entry(self, t):
        self._eid += 1
        e = {"id": self._eid, "t": t}
        self._emap[self._eid] = e
        return e

    def entry_of(self, eid):
        return self._emap.get(eid)

    def _rebuild_queue_view(self):
        self.qlist.clear()
        for e in self.queue:
            it = QListWidgetItem(e["t"]["title"]); it.setData(Qt.UserRole, e["id"])
            it.setToolTip(f"{disp(e['t']['title'])}\n{disp(e['t']['artist'])} – {disp(e['t']['album'])}")
            self.qlist.addItem(it)
        self._mark_current()

    def _mark_current(self):
        # Titelwechsel: steht die Auswahl nur auf dem vorherigen Titel (z. B. per Doppelklick gestartet),
        # wird sie aufgehoben – sonst sieht sie aus wie eine hängengebliebene Markierung
        nowt = self.cur["t"] if self.cur else None
        prev = getattr(self, "_marked_t", None)
        if prev is not None and nowt is not prev and hasattr(self, "tracks"):
            sm = self.tracks.selectionModel()
            rows = sm.selectedRows() if sm else []
            m = self.track_model
            if rows and all(m.rows[i.row()][2] is prev for i in rows if 0 <= i.row() < len(m.rows)):
                sm.clearSelection()
        self._marked_t = nowt
        if getattr(self, "nav_items", None) and "queue" in self.nav_items:
            self.nav_items["queue"].setData(0, NAV_COUNT, str(len(self.queue)) if self.queue else "")
        if getattr(self, "player", None) and self.cur is not None:
            QTimer.singleShot(0, self._prepare_next)
        n = len(self.queue)
        total = sum(e["t"]["length"] for e in self.queue)
        self.qfoot.setText(tr_("{0} Titel  ·  {1}").format(n, fmt_time(total)) if n else tr_("Liste ist leer"))
        self.qlist.viewport().update()
        self.track_model.refresh()
        if IS_WIN and self.testAttribute(Qt.WA_TranslucentBackground):
            # Windows (durchsichtiges Fenster mit Weichzeichner): einmal das ganze Fenster neu zeichnen,
            # damit keine Reste von Teil-Aktualisierungen stehen bleiben
            QTimer.singleShot(30, self.update)

    def _queue_reordered(self, *_):
        self.queue = [self.entry_of(self.qlist.item(i).data(Qt.UserRole)) for i in range(self.qlist.count())]
        self._prepare_next()

    def _queue_menu(self, pos):
        it = self.qlist.itemAt(pos)
        if not it:
            return
        m = QMenu(self)
        e = self.entry_of(it.data(Qt.UserRole))
        m.addAction(tr_("Wiedergeben"), lambda: self.play_entry(e))
        m.addAction(tr_("Aus Liste entfernen"), self.remove_selected_from_queue)
        m.addSeparator()
        m.addAction(tr_("Dateispeicherort öffnen"), lambda: show_in_file_manager(e["t"]["path"]))
        m.addAction(tr_("Dateipfad kopieren"), lambda: QApplication.clipboard().setText(e["t"]["path"]))
        m.exec(self.qlist.viewport().mapToGlobal(pos))

    def remove_selected_from_queue(self):
        rm = {it.data(Qt.UserRole) for it in self.qlist.selectedItems()}
        self.queue = [e for e in self.queue if e["id"] not in rm]
        if self.cur is not None and self.cur["id"] in rm:
            self.cur = None
        self._rebuild_queue_view()

    def clear_queue(self):
        self.stop()
        self.queue, self.cur, self._emap = [], None, {}
        self._rebuild_queue_view()
        self._show_now_playing(None)

    def play_tracks(self, tracks, start=0):
        self._emap = {}
        self.queue = [self._new_entry(t) for t in tracks]
        self._rebuild_queue_view()
        if self.queue:
            self.play_entry(self.queue[max(0, min(start, len(self.queue) - 1))])

    def add_tracks(self, tracks, next_up=False):
        new = [self._new_entry(t) for t in tracks]
        if next_up and self.cur is not None:
            i = self._cur_index() + 1
            self.queue[i:i] = new
        else:
            self.queue += new
        self._rebuild_queue_view()
        if self.cur is None and self.player.playbackState() != QMediaPlayer.PlayingState and new:
            self.play_entry(new[0])

    # ── Lückenlose Wiedergabe ─────────────────────────────────────────────
    def apply_audio_settings(self):
        if not getattr(self, "player", None) or not self.player.mp:
            return
        st = self.settings
        try:
            gains = [int(x) for x in json.loads(st.value("eq/gains", "[]") or "[]")] or [0] * 10
        except ValueError:
            gains = [0] * 10
        self.player.mp.set_filter(st.value("eq/enabled", False, type=bool), gains, st.value("eq/preamp", 0, type=int))
        self.player.mp.set_replaygain(st.value("eq/replaygain", "no"))
        self._prepare_next()

    def open_equalizer(self):
        if getattr(self, "_eq_dlg", None) and self._eq_dlg.isVisible():
            self._eq_dlg.raise_(); self._eq_dlg.activateWindow(); return
        self._eq_dlg = EqualizerDialog(self)
        self._eq_dlg.show()

    def _peek_next(self):
        """Der Eintrag, der beim automatischen Weiterschalten käme."""
        if not self.queue or self.cur is None:
            return None
        if self.repeat == 2:
            return self.cur
        i = self._cur_index()
        if i < 0:
            return None
        if self.shuffle and len(self.queue) > 1:
            if self._next_entry is None or self._next_entry is self.cur or \
                    not any(e is self._next_entry for e in self.queue):
                self._next_entry = random.choice([e for k, e in enumerate(self.queue) if k != i])
            return self._next_entry
        j = i + 1
        if j >= len(self.queue):
            return self.queue[0] if self.repeat == 1 else None
        return self.queue[j]

    def _prepare_next(self):
        if not getattr(self, "player", None) or not self.player.on_mpv():
            return
        if not self.settings.value("audio/gapless", True, type=bool) or self.cur is None \
                or self.cur["t"].get("stream"):
            self.player.set_next(None); self._next_entry = None
            return
        e = self._peek_next()
        self._next_entry = e
        t = e["t"] if e else None
        nsrc = self.media_src(t) if t and not t.get("stream") else None
        if nsrc and (t.get("remote") or os.path.exists(nsrc)) and self.player.uses_mpv_for(nsrc):
            self.player.set_next(nsrc)
        else:
            self.player.set_next(None)

    def _gapless_advanced(self):
        """mpv ist lückenlos zum vorgeladenen Titel gewechselt."""
        e = self._next_entry
        self._next_entry = None
        if e is None or not any(x is e for x in self.queue):
            return
        self.cur = e
        self._counted = False
        self._end_handled = False
        self._end_watchdog.stop()
        self.stream_title = ""
        self._mark_current()
        i = self._cur_index()
        if i >= 0:
            self.qlist.scrollToItem(self.qlist.item(i))
        self._show_now_playing(e["t"])
        self._prepare_next()

    def _cur_index(self):
        for i, e in enumerate(self.queue):
            if e is self.cur:
                return i
        return -1

    # ── Wiedergabe ────────────────────────────────────────────────────────
    def play_entry(self, e):
        if e is None:
            return
        self._resume_ready = False
        self.video.show_end(False)
        self.sub_mode, self._srt, self._srt_file, self._sub_auto_done = "off", None, None, False
        self.video.set_subtitle("")
        self.btn_tracks.hide()
        self.cur = e
        t = e["t"]
        self.stream_title = ""
        if t.get("stream"):
            self._counted = True
            self._end_handled = False
            self.player.setSource(QUrl(t["path"]))
            self.player.play()
            self._mark_current()
            self._show_now_playing(t)
            return
        src = self.media_src(t)
        if not src or (not t.get("remote") and not os.path.exists(src)):
            self.flash(tr_("Jellyfin ist nicht verbunden.") if t.get("remote") else tr_("Datei nicht gefunden: {0}").format(t['path']))
            QTimer.singleShot(0, lambda: self.next_track(auto=True))
            return
        self._counted = False
        self._end_handled = False
        self._end_watchdog.stop()
        self.player.setSource(QUrl(src) if src.startswith(("http://", "https://")) else QUrl.fromLocalFile(src))
        self.player.play()
        self._mark_current()
        i = self._cur_index()
        if i >= 0:
            self.qlist.scrollToItem(self.qlist.item(i))
        self._show_now_playing(t)
        self._next_entry = None
        self._prepare_next()

    def _show_now_playing(self, t):
        self.video.update()
        self._tray_update()
        if getattr(self, "mini", None) and self.mini.isVisible():
            self.mini.refresh()
        if getattr(self, "mpris", None):
            self.mpris.set_position(0)
            QTimer.singleShot(0, self._mpris_update)
        if t:
            self.np_title.setText(disp(t["title"])); self.np_artist.setText(f"{disp(t['artist'])} – {disp(t['album'])}")
            self.np_cover.setPixmap(self.covers.get(t["cover"], 42))
            self.setWindowTitle(f"{disp(t['title'])} – {disp(t['artist'])}  |  {APP_NAME}")
        else:
            self.np_title.setText(tr_("Keine Wiedergabe")); self.np_artist.setText("")
            self.np_cover.setPixmap(CoverCache.placeholder(42))
            self.setWindowTitle(APP_TITLE)
        self.ovl_title.setText(disp(t["title"]) if t else "")
        self._update_vis()

    def toggle_play(self):
        s = self.player.playbackState()
        if self._resume_ready and s == QMediaPlayer.StoppedState and self.cur is not None:
            self._resume_ready = False
            self._end_handled = False
            self.player.play()
            return
        if s == QMediaPlayer.PlayingState:
            self.player.pause()
        elif s == QMediaPlayer.PausedState:
            self.player.play()
        elif self.cur is not None:
            self.play_entry(self.cur)
        elif self.queue:
            self.play_entry(self.queue[0])
        else:
            self.play_all_visible()

    def stop(self):
        self.player.stop()

    def next_track(self, auto=False):
        if not self.queue:
            return
        i = self._cur_index()
        if auto and self.repeat == 2 and self.cur is not None:
            self.play_entry(self.cur); return
        if self.shuffle and len(self.queue) > 1:
            pre = self._next_entry if auto else None
            ks = [k for k, x in enumerate(self.queue) if x is pre and k != i]
            j = ks[0] if ks else random.choice([k for k in range(len(self.queue)) if k != i])
        else:
            j = i + 1
            if j >= len(self.queue):
                if self.repeat == 1 or not auto:
                    j = 0
                else:
                    self.player.stop(); self._playback_finished(); return
        self.play_entry(self.queue[j])

    def prev_track(self):
        if self.player.position() > 3000:
            self.player.setPosition(0); return
        if self.queue:
            self.play_entry(self.queue[(self._cur_index() - 1) % len(self.queue)])

    def toggle_shuffle(self):
        self.shuffle = self.btn_shuffle.isChecked()
        self.settings.setValue("shuffle", self.shuffle)
        self._next_entry = None
        self._prepare_next()
        self._mpris_update()

    def cycle_repeat(self):
        self.repeat = (self.repeat + 1) % 3
        self.settings.setValue("repeat", self.repeat)
        self._prepare_next()
        self._update_repeat_btn()
        self._mpris_update()

    def _update_repeat_btn(self):
        self.btn_repeat.setChecked(self.repeat > 0)
        self.btn_repeat.setIcon(make_icon("repeat1" if self.repeat == 2 else "repeat", 20))
        self.btn_repeat.setToolTip([tr_("Wiederholen: aus"), tr_("Wiederholen: alle"), tr_("Wiederholen: einen Titel")][self.repeat])

    def toggle_mute(self):
        m = not self.audio.isMuted()
        self.audio.setMuted(m)
        self.btn_mute.setIcon(make_icon("mute" if m else "volume", 20))

    def _set_volume(self, v):
        self.audio.setVolume((v / 100.0) ** 2)
        self.settings.setValue("volume", v)
        self._mpris_update()

    def _pos_changed(self, pos):
        self._update_srt(pos)
        if self.mini.isVisible():
            self.mini.set_pos(pos)
        if getattr(self, "mpris", None) and abs(pos - self.mpris.pos_us / 1000 - (time.monotonic() - self.mpris.pos_time) * 1000 * self.mpris.playing) > 1500:
            self.mpris.set_position(pos)
        d0 = self.player.duration()
        if d0 > 0 and pos >= d0 - 250 and not self._end_handled and not self._end_watchdog.isActive():
            self._end_watchdog.start()
        if not self.seek.isSliderDown():
            self.seek.setValue(pos)
            self._update_time(pos)
        d = self.player.duration()
        if not self._counted and self.cur and d > 0 and pos >= min(30000, d * 0.5):
            self._counted = True
            self.stats.add_play(self.cur["t"]["path"])
            self.jf_report_play(self.cur["t"])
            self.track_model.refresh()

    def _state_changed(self, s):
        self.btn_play.set_playing(s == QMediaPlayer.PlayingState)
        self._update_vis()
        if self.mpris:
            self.mpris.set_position(self.player.position())
            self.mpris.update_all()
        self._state_hook(s)

    def update_sleep_guard(self, *_):
        playing = self.player.playbackState() == QMediaPlayer.PlayingState
        if not playing or not self.settings.value("system/no_sleep", True, type=bool):
            mode = None
        else:
            try:
                mode = "video" if self.player.hasVideo() else "audio"
            except Exception:
                mode = "audio"
        self.sleep_guard.set(mode)

    def _state_hook(self, s):
        self.update_sleep_guard()
        self._tray_update()
        if self.mini.isVisible():
            self.mini.refresh()

    def _mpris_update(self):
        if getattr(self, "mpris", None):
            self.mpris.update_all()

    def show_window(self):
        if getattr(self, "mini", None) and self.mini.isVisible():
            self.mini.hide()
        if self.isHidden() or self.isMinimized():
            self.showMaximized() if self._mini_was_max else self.showNormal()
        self.raise_(); self.activateWindow()

    # ── Systemleiste ──────────────────────────────────────────────────────
    def setup_tray(self):
        self.tray = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(app_icon(), self)
        m = QMenu()
        self.tray_menu = m
        self.tray_play = m.addAction(tr_("Wiedergabe"), self.toggle_play)
        m.addAction(tr_("Weiter"), self.next_track)
        m.addAction(tr_("Zurück"), self.prev_track)
        m.addSeparator()
        m.addAction(tr_("Mini-Player"), self.show_mini)
        m.addAction(tr_("NeoNote anzeigen"), self.show_window)
        m.addSeparator()
        m.addAction(tr_("Beenden"), self.quit_app)
        self.tray.setContextMenu(m)
        self.tray.activated.connect(self._tray_activated)
        self.tray.setToolTip(APP_NAME)
        self.tray.setVisible(self.settings.value("system/tray", True, type=bool))

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible() and not self.isMinimized() and self.isActiveWindow():
                self.hide()
            else:
                self.show_window()
        elif reason == QSystemTrayIcon.MiddleClick:
            self.toggle_play()

    def _tray_update(self):
        if not getattr(self, "tray", None):
            return
        playing = self.player.playbackState() == QMediaPlayer.PlayingState
        self.tray_play.setText("Pause" if playing else tr_("Wiedergabe"))
        t = self.cur["t"] if self.cur else None
        self.tray.setToolTip(f"{disp(t['title'])} – {disp(t['artist'])}" if t else APP_NAME)

    # ── Mini-Player ───────────────────────────────────────────────────────
    def show_mini(self):
        if self._fs:
            self.toggle_fullscreen()
        self._mini_was_max = self.isMaximized()
        self.mini.refresh_style(); self.mini.refresh(); self.mini.set_pos(self.player.position())
        scr = (self.screen() or QGuiApplication.primaryScreen()).availableGeometry()
        self.mini.move(scr.right() - self.mini.width() - 24, scr.bottom() - self.mini.height() - 24)
        self.mini.show()
        self.hide()

    def leave_mini(self):
        self.mini.hide()
        self.show_window()

    # ── Tonspuren und Untertitel ──────────────────────────────────────────
    @staticmethod
    def _track_label(md, i):
        title = md.stringValue(QMediaMetaData.Key.Title)
        lang = md.value(QMediaMetaData.Key.Language)
        lname = ""
        try:
            if lang is not None and lang != QLocale.Language.AnyLanguage:
                lname = QLocale(QLocale.Language(lang)).nativeLanguageName()
                lname = lname[:1].upper() + lname[1:]
        except Exception:
            lname = ""
        if title and lname and lname.lower() in title.lower():
            lname = ""
        return " – ".join(x for x in (title, lname) if x) or f"Spur {i + 1}"

    def _external_subs(self):
        if not self.cur or self.cur["t"].get("stream"):
            return []
        pth = Path(self.cur["t"]["path"])
        try:
            return sorted(Path(x) for x in globmod.glob(globmod.escape(str(pth.with_suffix(""))) + "*.srt"))
        except OSError:
            return []

    def _tracks_changed(self):
        audio = self.player.audioTracks()
        subs = self.player.subtitleTracks()
        ext = self._external_subs()
        if self.sub_mode == "off" and not self._sub_auto_done:
            self._sub_auto_done = True
            exact = [x for x in ext if x.stem == Path(self.cur["t"]["path"]).stem] if self.cur else []
            if exact:
                self._load_srt(exact[0])
        m = QMenu(self)
        if audio:
            am = m.addMenu(tr_("Tonspur"))
            g = QActionGroup(am)
            for i, md in enumerate(audio):
                a = am.addAction(self._track_label(md, i)); a.setCheckable(True)
                a.setChecked(i == self.player.activeAudioTrack()); g.addAction(a)
                a.triggered.connect(lambda _=False, i=i: self.player.setActiveAudioTrack(i))
        sm = m.addMenu(tr_("Untertitel"))
        g2 = QActionGroup(sm)
        off = sm.addAction(tr_("Aus")); off.setCheckable(True); off.setChecked(self.sub_mode == "off"); g2.addAction(off)
        off.triggered.connect(self._subs_off)
        for i, md in enumerate(subs):
            a = sm.addAction(self._track_label(md, i)); a.setCheckable(True); g2.addAction(a)
            a.setChecked(self.sub_mode == "embedded" and i == self.player.activeSubtitleTrack())
            a.triggered.connect(lambda _=False, i=i: self._subs_embedded(i))
        for f in ext:
            a = sm.addAction(tr_("Datei: {0}").format(f.name)); a.setCheckable(True); g2.addAction(a)
            a.setChecked(self.sub_mode == "srt" and self._srt_file == f)
            a.triggered.connect(lambda _=False, f=f: self._load_srt(f))
        sm.addSeparator()
        sm.addAction(tr_("Untertiteldatei laden…"), self._pick_srt)
        self.btn_tracks.setMenu(m)
        self.btn_tracks.setVisible(self.video.has_video or len(audio) > 1)

    def _subs_off(self):
        self.sub_mode = "off"; self._srt = None; self._srt_file = None
        self.player.setActiveSubtitleTrack(-1)
        self.video.set_subtitle("")
        self._tracks_changed()

    def _subs_embedded(self, i):
        self._srt = None; self._srt_file = None
        self.sub_mode = "embedded"
        self.player.setActiveSubtitleTrack(i)
        self._tracks_changed()

    def _load_srt(self, f):
        try:
            cues = parse_srt(f)
        except OSError as e:
            self.flash(tr_("Untertitel konnten nicht geladen werden: {0}").format(e))
            return
        self.player.setActiveSubtitleTrack(-1)
        self.sub_mode, self._srt, self._srt_file = "srt", cues, Path(f)
        self._srt_starts = [c[0] for c in cues]
        self._update_srt(self.player.position())
        if self.btn_tracks.menu():
            QTimer.singleShot(0, self._tracks_changed)

    def _pick_srt(self):
        start = str(Path(self.cur["t"]["path"]).parent) if self.cur and not self.cur["t"].get("stream") else str(Path.home())
        fn, _ = QFileDialog.getOpenFileName(self, tr_("Untertitel laden"), start, tr_("Untertitel (*.srt)"))
        if fn:
            self._load_srt(fn)

    def _update_srt(self, pos):
        if self.sub_mode != "srt" or not self._srt:
            return
        i = bisect.bisect_right(self._srt_starts, pos) - 1
        text = self._srt[i][2] if i >= 0 and pos <= self._srt[i][1] else ""
        self.video.set_subtitle(text)

    # ── Updates ──────────────────────────────────────────────────────────
    def _auto_update_check(self):
        mode = self.settings.value("update/check", "daily")
        if mode == "never":
            return
        last = float(self.settings.value("update/last_check", 0) or 0)
        gap = {"start": 0, "daily": 20 * 3600, "weekly": 6.5 * 86400}.get(mode, 20 * 3600)
        if time.time() - last >= gap:
            self.check_updates(manual=False)

    def check_updates(self, manual=False, report=None):
        """Neueste Version auf GitHub nachsehen. report: Rückruf für einen Statustext (Einstellungen, „Über“)."""
        if self._update_checker is not None and self._update_checker.isRunning():
            return
        if report:
            report(tr_("Suche nach Updates …"))
        th = UpdateCheck(self)
        self._update_checker = th

        def ok(info):
            self.settings.setValue("update/last_check", time.time())
            if not is_newer(info["version"]):
                if report:
                    report(tr_("NeoNote ist auf dem neuesten Stand ({0}).").format(APP_VERSION))
                return
            if report:
                report(tr_("Version {0} ist verfügbar.").format(info["version"]))
            self._update_found(info, manual)

        def bad(_e):
            if report:
                report(tr_("Keine Verbindung zu GitHub – bitte später noch einmal versuchen."))

        th.result.connect(ok); th.failed.connect(bad)
        th.start()

    def _update_asset(self, info):
        name = f"NeoNote-Setup-{info['version']}.exe"
        a = info["assets"].get(name)
        if a is None:   # sonst irgendein Windows-Installer der Release
            for n, x in info["assets"].items():
                if n.lower().startswith("neonote-setup") and n.lower().endswith(".exe"):
                    return n, x
            return None, None
        return name, a

    def _update_bar_wanted(self):
        return self._update_info is not None and not self.np_mode and not getattr(self, "_update_dismissed", False)

    def _update_found(self, info, manual):
        self._update_info = info
        self._update_dismissed = False
        can_install = IS_WIN and getattr(sys, "frozen", False) and self._update_asset(info)[0]
        if can_install:
            self.update_go.setText(tr_("Jetzt aktualisieren")); self.update_go.show()
        elif not IS_WIN and installed_by_package():
            self.update_go.hide()
        else:
            self.update_go.setText(tr_("Zur Downloadseite")); self.update_go.show()
        if can_install and self._update_file and Path(self._update_file).exists():
            self._update_ready()
        else:
            msg = tr_("NeoNote {0} ist verfügbar.").format(info["version"])
            if not IS_WIN and installed_by_package():
                msg += " " + tr_("Aktualisieren über die Paketverwaltung (z. B. „yay -Syu“).")
            self.update_lbl.setText(msg)
            if can_install and not manual and self.settings.value("update/mode", "notify") == "auto":
                self._download_update(install_now=False)
        self.update_bar.setVisible(self._update_bar_wanted())

    def _update_action(self):
        info = self._update_info
        if not info:
            return
        if not (IS_WIN and getattr(sys, "frozen", False) and self._update_asset(info)[0]):
            QDesktopServices.openUrl(QUrl(info.get("url") or RELEASES_URL))
            return
        if self._update_file and Path(self._update_file).exists():
            self._install_update(restart=True)
        else:
            self._download_update(install_now=True)

    def _download_update(self, install_now):
        if self._update_dl is not None and self._update_dl.isRunning():
            self._update_install_now = self._update_install_now or install_now
            return
        name, a = self._update_asset(self._update_info)
        if not a:
            return
        self._update_install_now = install_now
        th = UpdateDownload(a["url"], name, a["size"], a["digest"])
        self._update_dl = th
        self.update_lbl.setText(tr_("Lade NeoNote {0} herunter …").format(self._update_info["version"]))
        self.update_prog.setRange(0, 0); self.update_prog.show(); self.update_go.setEnabled(False)

        def prog(got, total):
            if total:
                self.update_prog.setRange(0, total); self.update_prog.setValue(got)

        def done(path):
            self._update_file = path
            self.update_prog.hide(); self.update_go.setEnabled(True)
            if self._update_install_now:
                self._install_update(restart=True)
            else:
                self._update_ready()

        def bad(e):
            self.update_prog.hide(); self.update_go.setEnabled(True)
            self.update_lbl.setText(tr_("Das Update konnte nicht geladen werden: {0}").format(e))

        th.progress.connect(prog); th.done.connect(done); th.failed.connect(bad)
        th.start()

    def _update_ready(self):
        self.update_lbl.setText(tr_("NeoNote {0} ist geladen und wird beim Beenden installiert.").format(
            self._update_info["version"]))
        self.update_go.setText(tr_("Jetzt neu starten")); self.update_go.show()

    def _install_update(self, restart):
        f = self._update_file
        if not (f and Path(f).exists()):
            return
        self._update_file = None
        try:
            win_run_update(f, restart)
        except Exception as e:
            self.update_lbl.setText(tr_("Das Update konnte nicht gestartet werden: {0}").format(e))
            return
        if restart:
            self.quit_app()
            QApplication.instance().quit()

    def quit_app(self):
        self._really_quit = True
        self.close()

    def restart_app(self):
        """Neustart (z. B. nach dem mpv-Download): neue Instanz wartet, bis diese beendet ist."""
        if getattr(sys, "frozen", False):
            QProcess.startDetached(sys.executable, ["--restart"])
        else:
            QProcess.startDetached(sys.executable, [os.path.abspath(sys.argv[0]), "--restart"])
        self.quit_app()
        QApplication.instance().quit()

    def _meta_changed(self):
        if not (self.cur and self.cur["t"].get("stream")):
            return
        md = self.player.metaData()
        title = ""
        for key in (QMediaMetaData.Key.Title, QMediaMetaData.Key.Description, QMediaMetaData.Key.Comment):
            v = md.stringValue(key)
            if v and v != self.cur["t"]["title"]:
                title = v
                break
        if title != self.stream_title:
            self.stream_title = title
            self.np_artist.setText(title or tr_("Internetradio"))
            self.video.update()
            if getattr(self, "mpris", None):
                self.mpris.update_track()

    def _user_seek(self, v):
        self.player.setPosition(v)
        if getattr(self, "mpris", None):
            self.mpris.set_position(v, seeked=True)

    def _update_time(self, pos):
        d = max(0, self.player.duration()) if hasattr(self, "player") else 0
        if self._time_remaining and d > 0:
            left = f"-{fmt_time(max(0, d - pos) / 1000)}"
        else:
            left = fmt_time(pos / 1000)
        txt = f"{left} / {fmt_time(d / 1000)}"
        if txt != self.lbl_time.text():
            self.lbl_time.setText(txt)

    # ── Waveform unten links ─────────────────────────────────────────────
    def _show_wave(self):
        if self._vis_mode == "wave":
            return True
        if self._vis_mode == "cover":
            return False
        t = self.cur["t"] if self.cur else None          # auto: Waveform, wenn es kein echtes Cover gibt
        return bool(t) and not t.get("cover")

    def _update_vis(self):
        wave = self._show_wave()
        self.np_wave.setVisible(wave); self.np_cover.setVisible(not wave)
        playing = self.player.playbackState() == QMediaPlayer.PlayingState if hasattr(self, "player") else False
        if wave and playing:
            self._vis_timer.start()
        else:
            self._vis_timer.stop()
            if not playing:
                self.np_wave.reset()

    def _toggle_vis(self):
        self._vis_mode = "cover" if self._show_wave() else "wave"
        self.settings.setValue("ui/vis_mode", self._vis_mode)
        self._update_vis()

    def _vis_tick(self):
        self.np_wave.push(self.player.level())

    def _toggle_remaining(self):
        self._time_remaining = not self._time_remaining
        self.settings.setValue("ui/time_remaining", self._time_remaining)
        self._update_time(self.seek.value())

    def _dur_changed(self, d):
        self.seek.setRange(0, d)
        self.seek.setEnabled(d > 0)
        if self.mini.isVisible():
            self.mini.refresh()
        self._mpris_update()
        self._update_time(self.seek.value())

    def _status_changed(self, s):
        if s == QMediaPlayer.LoadedMedia and self._pending_pos:
            self.player.setPosition(self._pending_pos)
            self._pending_pos = None
        if s == QMediaPlayer.EndOfMedia:
            self._track_ended()

    def _track_ended(self):
        if self._end_handled:
            return
        self._end_handled = True
        self.next_track(auto=True)

    def _end_watchdog_check(self):
        d = self.player.duration()
        if (d > 0 and self.player.position() >= d - 250
                and self.player.playbackState() == QMediaPlayer.PlayingState):
            self._track_ended()

    def closeEvent(self, e):
        if (not self._really_quit and getattr(self, "tray", None) and self.tray.isVisible()
                and self.settings.value("system/close_to_tray", False, type=bool)):
            self.hide()
            e.ignore()
            if not self.settings.value("system/tray_hint_shown", False, type=bool):
                self.settings.setValue("system/tray_hint_shown", True)
                self.tray.showMessage(APP_NAME, tr_("NeoNote läuft in der Systemleiste weiter."), app_icon(), 4000)
            return
        self.mini.close()
        if getattr(self, "tray", None):
            self.tray.hide()
        self.save_session()
        # Fenstergröße, -position und zuletzt geöffnete Ansicht merken
        if not self._fs:
            self.settings.setValue("window/geometry", self.saveGeometry())
            self.settings.setValue("window/maximized", self.isMaximized())
        if self.state and not str(self.state).startswith(("search", "np", "playing")):
            self.settings.setValue("session/view", self.state)
        if self.mpris:
            self.mpris.stop()
        self.player.shutdown()
        if self.covers.loader is not None:
            self.covers.loader.stop()
        if IS_WIN and self._update_file and Path(self._update_file).exists():   # „beim Beenden installieren“
            self._install_update(restart=False)
        self.sleep_guard.set(None)
        self.settings.setValue("layout/splitter", self.split.saveState())
        self.settings.setValue("trackview/header", self.tracks.header().saveState())
        self.stats.save()
        if self.batch:
            self.batch.requestInterruption(); self.batch.wait(3000)
        for j in list(self._jobs):
            j.wait(3000)
        if self.scanner:
            self.scanner.requestInterruption(); self.scanner.wait(2000)
        super().closeEvent(e)


# ════════════════════════════════════════════════════════════════════════════
#  Stylesheets (werden aus dem Farbschema erzeugt)
# ════════════════════════════════════════════════════════════════════════════
def build_palette():
    pal = QPalette()
    for role, col in ((QPalette.Window, T.solid), (QPalette.Base, mix(T.solid, T.ovc, 0.03)),
                      (QPalette.AlternateBase, mix(T.solid, T.ovc, 0.06)), (QPalette.Button, mix(T.solid, T.ovc, 0.06)),
                      (QPalette.Text, T.fg), (QPalette.WindowText, T.fg), (QPalette.ButtonText, T.fg),
                      (QPalette.Highlight, T.accent), (QPalette.HighlightedText, QColor("white")),
                      (QPalette.ToolTipBase, T.solid), (QPalette.ToolTipText, T.fg),
                      (QPalette.PlaceholderText, T.dim), (QPalette.Link, T.accent)):
        pal.setColor(role, col)
    return pal


def _ova(a):
    """Hintergrundfarbe des Schemas mit Deckkraft a – für Overlays über dem Video."""
    c = mix(T.bg, QColor("#000000"), 0.25) if T.dark else QColor(T.bg)
    c.setAlphaF(a)
    return c


def common_rules():
    """Regeln für Bedienelemente – gelten im Fenster und in Dialogen."""
    fg, dim, acc = css(T.fg), css(T.dim), css(T.accent)
    return f"""
QToolButton {{ background: transparent; border: none; border-radius: 4px; padding: 5px; color: {fg}; }}
QToolButton:hover {{ background: {css(T.ov(0.08))}; }}
QToolButton:pressed {{ background: {css(T.ov(0.14))}; }}
QToolButton:checked {{ background: {css(T.acc(0.25))}; }}
QToolButton::menu-indicator {{ image: none; }}
QPushButton {{ background: {css(T.ov(0.07))}; border: 1px solid {css(T.ov(0.10))}; border-radius: 4px;
               padding: 6px 14px; color: {fg}; }}
QPushButton:hover {{ background: {css(T.ov(0.12))}; }}
QPushButton:default {{ background: {acc}; border-color: {acc}; color: {css(T.on_acc)}; }}
QSlider {{ background: transparent; }}
QSlider::groove:horizontal {{ height: 4px; background: {css(T.ov(0.14))}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {acc}; border-radius: 2px; }}
QSlider::handle:horizontal {{ width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; background: {fg}; }}
QSlider::handle:horizontal:hover {{ background: {css(T.accent.lighter(130))}; }}
QSlider::groove:vertical {{ width: 4px; background: {css(T.ov(0.14))}; border-radius: 2px; }}
QSlider::add-page:vertical {{ background: {acc}; border-radius: 2px; }}
QSlider::sub-page:vertical {{ background: {css(T.ov(0.14))}; border-radius: 2px; }}
QSlider::handle:vertical {{ width: 14px; height: 14px; margin: 0 -5px; border-radius: 7px; background: {fg}; }}
QSlider::handle:vertical:hover {{ background: {css(T.accent.lighter(130))}; }}
QComboBox {{ background: {css(T.ov(0.07))}; border: 1px solid {css(T.ov(0.12))}; border-radius: 4px;
             padding: 4px 10px; color: {fg}; }}
QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox QAbstractItemView {{ background: {css(T.solid)}; color: {fg}; border: 1px solid {css(T.ov(0.15))};
             selection-background-color: {css(T.acc(0.4))}; outline: 0; }}
QCheckBox {{ color: {fg}; spacing: 8px; background: transparent; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 3px; border: 1px solid {css(T.ov(0.3))};
             background: {css(T.ov(0.05))}; }}
QCheckBox::indicator:checked {{ background: {acc}; border-color: {acc}; }}
QLabel#hint {{ color: {dim}; font-size: 9pt; }}
QMenu {{ background: {css(T.solid)}; color: {fg}; border: 1px solid {css(T.ov(0.14))}; padding: 4px; }}
QMenu::item {{ padding: 6px 26px 6px 22px; border-radius: 3px; background: transparent; }}
QMenu::item:selected {{ background: {css(T.acc(0.35))}; }}
QMenu::separator {{ height: 1px; background: {css(T.ov(0.12))}; margin: 4px 8px; }}
QMenu::indicator {{ width: 14px; height: 14px; left: 4px; }}
QMenu::section {{ color: {dim}; padding: 4px 8px; }}
QToolTip {{ background: {css(T.solid)}; color: {fg}; border: 1px solid {css(T.ov(0.18))}; padding: 4px 6px; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {css(T.ov(0.18))}; min-height: 30px; border-radius: 3px; margin: 2px; }}
QScrollBar::handle:vertical:hover {{ background: {css(T.ov(0.30))}; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {css(T.ov(0.18))}; min-width: 30px; border-radius: 3px; margin: 2px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
"""


def app_style():
    return f"""
QDialog, QMessageBox {{ background: {css(T.solid)}; color: {css(T.fg)}; }}
QDialog QLabel, QMessageBox QLabel {{ color: {css(T.fg)}; background: transparent; }}
QLineEdit {{ background: {css(T.ov(0.06))}; border: 1px solid {css(T.ov(0.12))}; border-radius: 4px; padding: 5px; color: {css(T.fg)}; }}
QLineEdit:focus {{ border-color: {css(T.accent)}; }}
QTabWidget::pane {{ border: 1px solid {css(T.ov(0.10))}; border-radius: 4px; top: -1px; }}
QTabBar::tab {{ background: transparent; color: {css(T.dim)}; padding: 7px 16px; border: none;
               border-bottom: 2px solid transparent; }}
QTabBar::tab:selected {{ color: {css(T.fg)}; border-bottom: 2px solid {css(T.accent)}; }}
QTabBar::tab:hover {{ color: {css(T.fg)}; }}
QDialog QListWidget, QDialog QTreeWidget {{ background: {css(T.ov(0.04))}; border: 1px solid {css(T.ov(0.10))};
               border-radius: 4px; color: {css(T.fg)}; outline: 0; }}
QDialog QTreeWidget::item:selected, QDialog QListWidget::item:selected {{ background: {css(T.acc(0.35))}; color: {css(T.fg)}; }}
QDialog QListWidget::indicator {{ width: 14px; height: 14px; border-radius: 3px; border: 1px solid {css(T.ov(0.35))};
               background: {css(T.ov(0.05))}; }}
QDialog QListWidget::indicator:checked {{ background: {css(T.accent)}; border-color: {css(T.accent)}; }}
QDialog QHeaderView::section {{ background: transparent; color: {css(T.dim)}; border: none;
               border-bottom: 1px solid {css(T.ov(0.10))}; padding: 4px 6px; }}
QRadioButton {{ color: {css(T.fg)}; spacing: 8px; background: transparent; }}
QRadioButton::indicator {{ width: 14px; height: 14px; border-radius: 8px; border: 1px solid {css(T.ov(0.3))}; }}
QRadioButton::indicator:checked {{ background: {css(T.accent)}; border: 3px solid {css(T.solid)}; }}
QLabel#coverbox {{ background: {css(T.ov(0.05))}; border: 1px solid {css(T.ov(0.10))}; color: {css(T.dim)}; }}
QDialog QPushButton:disabled {{ color: {css(T.dim)}; background: {css(T.ov(0.03))}; }}
""" + common_rules()


def main_style():
    fg, dim, acc = css(T.fg), css(T.dim), css(T.accent)
    line = css(T.ov(0.08))
    # nahtlos: keine Trennlinien, alle Bereiche auf einer Fläche
    sep = "none" if T.seamless else f"1px solid {line}"
    sep_col = "none" if T.seamless else f"1px solid {css(T.ov(0.06))}"

    def pan(a):
        return "transparent" if T.seamless else css(T.ov(a))
    return f"""
QMainWindow#main {{ background: transparent; }}
#root {{ background: transparent; }}
#root QWidget {{ background: transparent; color: {fg}; font-size: 10pt; }}
#root QLabel#dim {{ color: {dim}; }}
#root QLabel#empty {{ color: {dim}; font-size: 12pt; }}
#root QLabel#crumb {{ font-size: 10.5pt; padding-left: 6px; }}
#root QLabel#npTitle {{ font-weight: 600; }}
#root QToolButton#timeBtn {{ color: {dim}; font-size: 9pt; background: transparent; border: none; padding: 2px 2px; }}
#root QToolButton#timeBtn:hover {{ color: {fg}; }}
#root QLabel#queueTitle {{ font-weight: 600; font-size: 10.5pt; }}
#root QLabel#qfoot {{ color: {dim}; padding: 7px 12px; border-top: {sep}; }}

#root QFrame#topbar {{ background: {pan(0.035)}; border-bottom: {sep}; }}
#root QFrame#cmdbar {{ border-bottom: {sep}; }}
#root QFrame#updatebar {{ background: {css(T.acc(0.16))}; border-bottom: {sep}; }}
#root QFrame#updatebar QPushButton {{ padding: 3px 12px; }}
#root QFrame#cmdbar QToolButton {{ padding: 5px 10px; }}
#root QTreeWidget#nav {{ background: {pan(0.025)}; border: none; padding-top: 6px;
                         show-decoration-selected: 0; }}
#root QTreeWidget#nav::item, #root QTreeWidget#nav::item:selected, #root QTreeWidget#nav::item:hover {{
        background: transparent; border: none; }}
#root QFrame#queue {{ background: {pan(0.025)}; }}
#root QFrame#queueHead {{ border-bottom: {sep}; }}
#root QFrame#controls {{ background: {pan(0.045)}; border-top: {sep}; }}
#root QFrame#winbox {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {css(_ova(0.42))}, stop:0.55 {css(_ova(0.16))}, stop:1 {css(_ova(0.0))});
    border: none; }}
#root QLabel#ovlTitle {{ color: {fg}; font-size: 9pt; }}
#root QFrame#controls[overlay="true"] {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {css(_ova(0.0))}, stop:0.35 {css(_ova(0.35))}, stop:1 {css(_ova(0.72))}); border: none; }}
#root QToolButton#navbtn {{ background: transparent; border: none; border-radius: 6px; padding: 6px; }}
#root QToolButton#navbtn:hover {{ background: {css(T.ov(0.09))}; }}
#root QToolButton#navbtn:pressed {{ background: {css(T.ov(0.15))}; }}
#root QToolButton#navbtn:disabled {{ background: transparent; }}
#root QListWidget#radioList::item {{ padding: 6px 8px; border-bottom: 1px solid {css(T.ov(0.05))}; }}
#root QListWidget#radioList::item:selected {{ background: {css(T.acc(0.30))}; }}
#root QListWidget#radioList::item:hover {{ background: {css(T.ov(0.06))}; }}
#root QToolButton#overlayBtn {{ background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
                               border-radius: 4px; padding: 6px; }}
#root QToolButton#overlayBtn:hover {{ background: {css(T.acc(0.4))}; }}
#root QFrame#endBox {{ background: rgba(10,14,20,0.72); border: 1px solid rgba(255,255,255,0.14); border-radius: 6px; }}
#root QToolButton#endBtn {{ color: white; font-size: 11pt; padding: 6px 14px 6px 8px; border-radius: 4px; }}
#root QToolButton#endBtn:hover {{ background: {css(T.acc(0.45))}; }}
#root QToolButton#winbtn, #root QToolButton#closebtn {{ border-radius: 4px; padding: 6px 9px; }}
#root QToolButton#closebtn:hover {{ background: #e81123; }}
#root QToolButton#ovlwin, #root QToolButton#ovlclose {{ border-radius: 3px; padding: 3px 9px; }}
#root QToolButton#ovlclose:hover {{ background: #e81123; }}
#root QToolButton#closebtn:pressed {{ background: #b50e1c; }}
#root QToolButton#ctl {{ border-radius: 16px; padding: 6px; }}

#root QLineEdit#search {{ background: {css(T.ov(0.06))}; border: 1px solid {css(T.ov(0.10))}; border-radius: 4px;
                         padding: 5px 6px; color: {fg}; }}
#root QLineEdit#search:focus {{ border-color: {acc}; background: {css(T.ov(0.09))}; }}

#root QTreeView, #root QListView, #root QListWidget {{ border: none; outline: 0; }}
#root QTreeView::item {{ padding: 0 4px; border: none; }}
#root QTreeView::item:hover, #root QListView::item:hover {{ background: {css(T.ov(0.06))}; }}
#root QTreeView::item:selected {{ background: {css(T.acc(0.30))}; color: {fg}; }}
#root QTreeView::branch {{ background: transparent; }}

#root QHeaderView {{ background: transparent; }}
#root QHeaderView::section {{ background: transparent; color: {dim}; border: none;
        border-right: {sep_col}; border-bottom: {sep}; padding: 6px 6px; }}
#root QHeaderView::section:hover {{ background: {css(T.ov(0.05))}; color: {fg}; }}
#root QSplitter::handle {{ background: transparent; }}
#root QToolButton#checkCard {{ background: {css(T.ov(0.05))}; border: none; border-radius: 8px; padding: 10px 14px;
    text-align: left; font-size: 10pt; }}
#root QToolButton#checkCard:hover {{ background: {css(T.ov(0.09))}; }}
#root QLabel#checkTitle {{ font-size: 14pt; font-weight: 600; }}
#root QLabel#checkOk {{ color: {css(T.dim)}; }}
#root QTreeView::indicator {{ width: 14px; height: 14px; border-radius: 3px; border: 1px solid {css(T.ov(0.32))};
    background: {css(T.ov(0.05))}; }}
#root QTreeView::indicator:checked {{ background: {acc}; border-color: {acc}; }}
#root QAbstractScrollArea::corner {{ background: transparent; border: none; }}
#root QProgressBar {{ background: {css(T.ov(0.1))}; border: none; border-radius: 3px; }}
#root QProgressBar::chunk {{ background: {acc}; border-radius: 3px; }}
#root QSlider#seek::groove:horizontal {{ height: 3px; }}
#root QSlider#seek::handle:horizontal {{ width: 10px; height: 10px; margin: -4px 0; border-radius: 5px; }}
""" + scoped(common_rules(), "#root")


def scoped(rules, scope):
    """Stellt jedem Selektor einer Regelliste den Bereich voran (z. B. „#root“)."""
    out = []
    for line in rules.splitlines():
        if "{" in line and not line.startswith(" "):
            sel, rest = line.split("{", 1)
            sel = ", ".join(f"{scope} {x.strip()}" for x in sel.split(",") if x.strip())
            line = f"{sel} {{{rest}"
        out.append(line)
    return "\n".join(out)


def migrate_from_darkplayer():
    """Übernimmt beim ersten Start Einstellungen, Bibliothek, Wiedergabelisten und Cover von DarkPlayer."""
    new = QSettings(APP_NAME, APP_NAME)
    old = QSettings(OLD_NAME, OLD_NAME)
    if not new.allKeys() and old.allKeys():
        for k in old.allKeys():
            new.setValue(k, old.value(k))
        new.sync()
    base_data = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    base_cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    import shutil
    for old_dir, new_dir in ((base_data / "darkplayer", DATA_DIR), (base_cache / "darkplayer", COVER_DIR.parent)):
        if old_dir.is_dir() and not new_dir.exists():
            try:
                shutil.copytree(old_dir, new_dir)
            except OSError:
                pass



# ════════════════════════════════════════════════════════════════════════════
#  Windows-Installer im NeoNote-Look (NeoNote.exe --setup, gestartet von NeoNote-Setup-x.y.z.exe)
# ════════════════════════════════════════════════════════════════════════════
def _ps_quote(x):
    return "'" + str(x).replace("'", "''") + "'"


def win_make_shortcut(lnk, target, workdir, desc=""):
    """Verknüpfung (.lnk) über PowerShell/WScript.Shell anlegen."""
    cmd = (f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut({_ps_quote(lnk)});"
           f"$s.TargetPath={_ps_quote(target)};$s.WorkingDirectory={_ps_quote(workdir)};"
           f"$s.IconLocation={_ps_quote(str(target) + ',0')};$s.Description={_ps_quote(desc)};$s.Save()")
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                   capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), timeout=60)


DEFAULT_APPS_URI = "ms-settings:defaultapps?registeredAppMachine=NeoNote"


def win_open_default_apps():
    """Windows-Einstellungen direkt bei „Standard-Apps ▸ NeoNote“ öffnen (Windows 11; sonst die Übersicht).
    Direkt über ShellExecute – der Explorer versteht Links mit „?…“ nicht und öffnet sonst nur ein Ordnerfenster."""
    for uri in (DEFAULT_APPS_URI, "ms-settings:defaultapps"):
        try:
            os.startfile(uri)
            return
        except Exception:
            continue
    try:
        subprocess.Popen(["cmd", "/c", "start", "", "ms-settings:defaultapps"],
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception:
        pass


def win_default_install_dir():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\NeoNote", 0,
                            winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as k:
            d = winreg.QueryValueEx(k, "InstallDir")[0]
            try:
                v = winreg.QueryValueEx(k, "Version")[0]
            except OSError:
                v = ""
            if d:
                return d, v
    except OSError:
        pass
    pf = os.environ.get("ProgramW6432") or os.environ.get("ProgramFiles") or r"C:\Program Files"
    return str(Path(pf) / "NeoNote"), ""


class SetupWorker(QThread):
    progress = Signal(int, str)
    done = Signal(bool, str)

    def __init__(self, src, dst, desktop, assoc, version):
        super().__init__()
        self.src, self.dst, self.desktop, self.assoc, self.version = Path(src), Path(dst), desktop, assoc, version

    def run(self):
        try:
            self._run()
            self.done.emit(True, "")
        except Exception as e:
            self.done.emit(False, str(e))

    def _run(self):
        import shutil
        import winreg
        nw = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        # 1. alte Installation pro Benutzer (bis 1.0.3 in %LOCALAPPDATA%\Programs) selbst entfernen.
        #    Nicht deren Uninstall.exe starten: die beendet alle „NeoNote.exe“ – also auch dieses Setup.
        self.progress.emit(2, tr_("Räume ältere Version auf …"))
        old = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "NeoNote"
        if old.exists() and old.resolve() != self.dst.resolve():
            shutil.rmtree(old, ignore_errors=True)
            appdata = Path(os.environ.get("APPDATA", ""))
            for lnk in (appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NeoNote Media Player.lnk",
                        Path.home() / "Desktop" / "NeoNote Media Player.lnk"):
                try:
                    lnk.unlink(missing_ok=True)
                except OSError:
                    pass
            HKCU = winreg.HKEY_CURRENT_USER

            def delete_tree(root, path):
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as k:
                        while True:
                            try:
                                sub = winreg.EnumKey(k, 0)
                            except OSError:
                                break
                            delete_tree(root, path + "\\" + sub)
                    winreg.DeleteKey(root, path)
                except OSError:
                    pass

            def delete_value(root, path, name):
                try:
                    with winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE) as k:
                        winreg.DeleteValue(k, name)
                except OSError:
                    pass

            for e in sorted(AUDIO_EXT | VIDEO_EXT):
                delete_value(HKCU, rf"Software\Classes\{e}\OpenWithProgids", "NeoNote.Media")
            for pth in (r"Software\Classes\NeoNote.Media", r"Software\Classes\Applications\NeoNote.exe",
                        r"Software\NeoNote\Capabilities",
                        r"Software\Microsoft\Windows\CurrentVersion\Uninstall\NeoNote"):
                delete_tree(HKCU, pth)
            delete_value(HKCU, r"Software\RegisteredApplications", "NeoNote")
            delete_value(HKCU, r"Software\NeoNote", "InstallDir")
        # 2. Dateien kopieren (alte Programmdateien vorher weg, Einstellungen liegen woanders)
        self.progress.emit(5, tr_("Bereite den Zielordner vor …"))
        self.dst.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(self.dst / "_internal", ignore_errors=True)
        files = [p for p in self.src.rglob("*") if p.is_file()]
        total = sum(p.stat().st_size for p in files) or 1
        done = 0
        for i, f in enumerate(files):
            rel = f.relative_to(self.src)
            out = self.dst / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, out)
            done += f.stat().st_size
            if i % 15 == 0 or i == len(files) - 1:
                self.progress.emit(5 + int(80 * done / total), tr_("Kopiere Dateien …"))
        exe = self.dst / "NeoNote.exe"
        # 3. Verknüpfungen
        self.progress.emit(87, tr_("Lege Verknüpfungen an …"))
        progdata = Path(os.environ.get("ProgramData", r"C:\ProgramData"))
        startmenu = progdata / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        startmenu.mkdir(parents=True, exist_ok=True)
        try:
            win_make_shortcut(startmenu / "NeoNote Media Player.lnk", exe, self.dst, APP_TITLE)
            pub_desk = Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop"
            if self.desktop:
                win_make_shortcut(pub_desk / "NeoNote Media Player.lnk", exe, self.dst, APP_TITLE)
            else:
                (pub_desk / "NeoNote Media Player.lnk").unlink(missing_ok=True)
        except Exception:
            pass
        # 4. Registrierung: Programme und Features, Öffnen mit, Standard-Apps
        self.progress.emit(93, tr_("Melde NeoNote bei Windows an …"))
        HK = winreg.HKEY_LOCAL_MACHINE

        def setv(path, name, value, kind=winreg.REG_SZ):
            with winreg.CreateKeyEx(HK, path, 0, winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY) as k:
                winreg.SetValueEx(k, name, 0, kind, value)

        setv(r"Software\NeoNote", "InstallDir", str(self.dst))
        setv(r"Software\NeoNote", "Version", self.version)
        un = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\NeoNote"
        size_kb = int(total / 1024)
        for n, v in (("DisplayName", APP_TITLE), ("DisplayVersion", self.version), ("DisplayIcon", str(exe)),
                     ("UninstallString", f'"{self.dst / "Uninstall.exe"}"'), ("InstallLocation", str(self.dst)),
                     ("Publisher", "NeoNote")):
            setv(un, n, v)
        for n, v in (("NoModify", 1), ("NoRepair", 1), ("EstimatedSize", size_kb)):
            setv(un, n, v, winreg.REG_DWORD)
        if self.assoc:
            exts = sorted(AUDIO_EXT | VIDEO_EXT)
            cls = r"Software\Classes"
            icons = self.dst / "_internal" / "icons"
            # alte Sammel-Klasse (bis 1.0.6) bleibt für bestehende Standard-Zuordnungen bestehen
            setv(cls + r"\NeoNote.Media", "", "Mediendatei (NeoNote)")
            setv(cls + r"\NeoNote.Media\DefaultIcon", "", str(icons / "audio.ico"))
            setv(cls + r"\NeoNote.Media\shell\open\command", "", f'"{exe}" "%1"')
            setv(cls + r"\Applications\NeoNote.exe", "FriendlyAppName", APP_TITLE)
            setv(cls + r"\Applications\NeoNote.exe\shell\open\command", "", f'"{exe}" "%1"')
            setv(r"Software\NeoNote\Capabilities", "ApplicationName", APP_TITLE)
            setv(r"Software\NeoNote\Capabilities", "ApplicationDescription",
                 tr_("Musik und Videos im Stil des Windows Media Player 12"))
            setv(r"Software\RegisteredApplications", "NeoNote", r"Software\NeoNote\Capabilities")
            for e in exts:
                name = e[1:]
                video = e in VIDEO_EXT
                prog = f"NeoNote.{name}"
                ico = icons / f"{name}.ico"
                setv(cls + "\\" + prog, "", f"{name.upper()}-{'Videodatei' if video else 'Audiodatei'}")
                setv(cls + "\\" + prog + r"\DefaultIcon", "", str(ico if ico.exists() else exe))
                setv(cls + "\\" + prog + r"\shell\open", "FriendlyAppName", APP_TITLE)
                setv(cls + "\\" + prog + r"\shell\open\command", "", f'"{exe}" "%1"')
                setv(cls + rf"\{e}\OpenWithProgids", prog, "")
                try:   # Sammel-Klasse nicht mehr doppelt unter „Öffnen mit“
                    with winreg.OpenKey(HK, cls + rf"\{e}\OpenWithProgids", 0,
                                        winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as k:
                        winreg.DeleteValue(k, "NeoNote.Media")
                except OSError:
                    pass
                setv(cls + r"\Applications\NeoNote.exe\SupportedTypes", e, "")
                setv(r"Software\NeoNote\Capabilities\FileAssociations", e, prog)
        try:
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, None, None)
        except Exception:
            pass
        self.progress.emit(100, tr_("Fertig"))


class NeoCheck(QCheckBox):
    """Runde Checkbox in Akzentfarbe mit gezeichnetem Häkchen."""

    def sizeHint(self):
        fm = self.fontMetrics()
        return QSize(26 + fm.horizontalAdvance(self.text()), max(22, fm.height() + 4))

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        y = self.height() / 2
        box = QRectF(0.5, y - 8, 16, 16)
        on = self.isChecked()
        p.setPen(QPen(T.accent if on else T.ov(0.30), 1)); p.setBrush(T.accent if on else T.ov(0.05))
        if not self.isEnabled():
            p.setOpacity(0.55)
        p.drawRoundedRect(box, 4, 4)
        if on:
            p.setPen(QPen(T.on_acc, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.setBrush(Qt.NoBrush)
            path = QPainterPath(QPointF(4.5, y)); path.lineTo(7.5, y + 3); path.lineTo(12.5, y - 3.5)
            p.drawPath(path)
        p.setPen(T.fg)
        p.drawText(QRectF(26, 0, self.width() - 26, self.height()), Qt.AlignVCenter | Qt.AlignLeft, self.text())


class SetupWindow(QWidget):
    """Ein Fenster im Look des Players: Neon-Note, Ordner, Optionen, Fortschritt."""

    def __init__(self, src, version):
        super().__init__(None, Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(tr_("{0} {1} – Setup").format(APP_TITLE, version))
        self.setWindowIcon(app_icon())
        self.src, self.version = src, version
        self.setFixedSize(540, 570)
        self.icon = app_icon().pixmap(96, 96)
        dst, old_ver = win_default_install_dir() if IS_WIN else (str(Path.home() / "NeoNote"), "")
        self.old_ver = old_ver
        self.result_ok = False
        lay = QVBoxLayout(self); lay.setContentsMargins(36, 14, 36, 28); lay.setSpacing(10)
        top = QHBoxLayout(); top.addStretch()
        self.btn_x = QToolButton(); self.btn_x.setObjectName("sx"); self.btn_x.setText("✕")
        self.btn_x.clicked.connect(self.close)
        top.addWidget(self.btn_x); lay.addLayout(top)
        lay.addSpacing(168)
        sub = (tr_("Update von Version {0} auf {1}").format(old_ver, version) if old_ver and old_ver != version
               else f"Media Player  ·  Version {version}")
        self.sub = QLabel(sub); self.sub.setAlignment(Qt.AlignCenter); self.sub.setObjectName("dim")
        lay.addWidget(self.sub); lay.addSpacing(14)
        lay.addWidget(QLabel(tr_("Installieren nach")))
        row = QHBoxLayout()
        self.path = QLineEdit(dst); self.path.setObjectName("path")
        self.btn_browse = QPushButton(tr_("Ändern …")); self.btn_browse.setObjectName("ghost")
        self.btn_browse.clicked.connect(self._browse)
        row.addWidget(self.path, 1); row.addWidget(self.btn_browse); lay.addLayout(row)
        # Alles freiwillig (Opt-in): der Nutzer setzt selbst die Haken, die er möchte
        self.cb_desk = NeoCheck(tr_("Verknüpfung auf dem Desktop")); self.cb_desk.setChecked(False)
        self.cb_assoc = NeoCheck(tr_("Für Musik und Videos anbieten (Öffnen mit, Standard-Apps)"))
        self.cb_assoc.setChecked(False)
        self.cb_default = NeoCheck(tr_("NeoNote als Standardplayer für alle Musik- und Videodateien festlegen"))
        self.cb_default.setChecked(False); self.cb_default.setEnabled(False)
        self.cb_assoc.toggled.connect(lambda v: (self.cb_default.setEnabled(v), v or self.cb_default.setChecked(False)))
        lay.addWidget(self.cb_desk); lay.addWidget(self.cb_assoc); lay.addWidget(self.cb_default)
        lay.addStretch()
        self.bar = QProgressBar(); self.bar.setRange(0, 100); self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6); self.bar.hide()
        self.status = QLabel(""); self.status.setObjectName("dim"); self.status.setWordWrap(True)
        lay.addWidget(self.bar); lay.addWidget(self.status)
        brow = QHBoxLayout(); brow.addStretch()
        self.btn_close = QPushButton(tr_("Schließen")); self.btn_close.setObjectName("ghost")
        self.btn_close.clicked.connect(self.close); self.btn_close.hide()
        self.btn_go = QPushButton(tr_("Installieren") if not old_ver else tr_("Aktualisieren"))
        self.btn_go.setObjectName("primary"); self.btn_go.setDefault(True)
        self.btn_go.clicked.connect(self._go)
        brow.addWidget(self.btn_close); brow.addWidget(self.btn_go); brow.addStretch()
        lay.addLayout(brow)
        acc, fg, dim = css(T.accent), css(T.fg), css(T.dim)
        self.setStyleSheet(f"""
            QWidget {{ color: {fg}; font-size: 10pt; background: transparent; }}
            QLabel#dim {{ color: {dim}; }}
            QLineEdit#path {{ background: {css(T.ov(0.06))}; border: 1px solid {css(T.ov(0.12))};
                              border-radius: 6px; padding: 7px 9px; }}
            QLineEdit#path:focus {{ border-color: {acc}; }}
            QPushButton {{ border-radius: 17px; padding: 8px 26px; min-height: 18px; }}
            QPushButton#primary {{ background: {acc}; color: {css(T.on_acc)}; border: none; font-weight: 600; }}
            QPushButton#primary:hover {{ background: {css(T.accent.lighter(115))}; }}
            QPushButton#primary:disabled {{ background: {css(T.ov(0.12))}; color: {dim}; }}
            QPushButton#ghost {{ background: {css(T.ov(0.07))}; border: 1px solid {css(T.ov(0.12))};
                                 border-radius: 6px; padding: 6px 14px; }}
            QPushButton#ghost:hover {{ background: {css(T.ov(0.12))}; }}
            QToolButton#sx {{ border: none; border-radius: 4px; padding: 4px 9px; color: {dim}; }}
            QToolButton#sx:hover {{ background: #e81123; color: white; }}
            QCheckBox {{ spacing: 8px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px;
                                    border: 1px solid {css(T.ov(0.28))}; background: {css(T.ov(0.05))}; }}
            QCheckBox::indicator:checked {{ background: {acc}; border-color: {acc};
                                            image: none; }}
            QProgressBar {{ background: {css(T.ov(0.10))}; border: none; border-radius: 3px; }}
            QProgressBar::chunk {{ background: {acc}; border-radius: 3px; }}
        """)
        self._drag = None

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and e.position().y() < 300 and self.windowHandle():
            self.windowHandle().startSystemMove()

    def paintEvent(self, _e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        bg = mix(T.bg, QColor("#000000"), 0.15) if T.dark else QColor(T.bg)
        bg.setAlphaF(0.985)
        p.setPen(QPen(T.ov(0.12), 1)); p.setBrush(bg); p.drawRoundedRect(r, 16, 16)
        cx = r.center().x()
        g = QRadialGradient(QPointF(cx, 120), 130)
        g.setColorAt(0, T.acc(0.30)); g.setColorAt(1, T.acc(0.0))
        p.setPen(Qt.NoPen); p.setBrush(g); p.drawEllipse(QPointF(cx, 120), 150, 110)
        p.drawPixmap(int(cx - 48), 64, self.icon)
        f = QFont(self.font()); f.setPointSizeF(22); f.setWeight(QFont.DemiBold)
        p.setFont(f); p.setPen(T.fg)
        p.drawText(QRectF(0, 168, self.width(), 40), Qt.AlignCenter, APP_NAME)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, tr_("Installationsordner wählen"), self.path.text())
        if d:
            d = os.path.normpath(d)
            if Path(d).name.lower() != "neonote":
                d = os.path.join(d, "NeoNote")
            self.path.setText(d)

    def _go(self):
        for w in (self.path, self.btn_browse, self.cb_desk, self.cb_assoc, self.cb_default, self.btn_go, self.btn_x):
            w.setEnabled(False)
        self.bar.show(); self.status.setText(tr_("Starte …"))
        self.th = SetupWorker(self.src, self.path.text().strip(), self.cb_desk.isChecked(),
                              self.cb_assoc.isChecked(), self.version)
        self.th.progress.connect(lambda v, t: (self.bar.setValue(v), self.status.setText(t)))
        self.th.done.connect(self._done)
        self.th.start()

    def _done(self, ok, err):
        self.th.wait()
        self.btn_x.setEnabled(True)
        if not ok:
            self.status.setText(tr_("<span style='color:#ff6b6b'>Das hat nicht geklappt: {0}</span>").format(err))
            for w in (self.path, self.btn_browse, self.cb_desk, self.cb_assoc, self.cb_default, self.btn_go):
                w.setEnabled(True)
            self.btn_go.setText(tr_("Erneut versuchen"))
            return
        self.result_ok = True
        self.bar.setValue(100)
        self.status.setText(tr_("NeoNote ist installiert. Viel Spaß mit deiner Musik!"))
        if self.cb_default.isChecked() and self.cb_assoc.isChecked() and self.isVisible():
            # Windows lässt Programme den Standard nicht selbst setzen – wir öffnen die passende Seite
            win_open_default_apps()
            self.status.setText(tr_("NeoNote ist installiert. In den Windows-Einstellungen, die sich gerade öffnen, "
                                "oben bei NeoNote auf <b>„Als Standard festlegen“</b> klicken – fertig."))
            self.status.setTextFormat(Qt.RichText)
        self.cb_desk.hide(); self.cb_assoc.hide(); self.cb_default.hide()
        self.btn_go.setText(tr_("NeoNote starten")); self.btn_go.setEnabled(True)
        self.btn_go.clicked.disconnect(); self.btn_go.clicked.connect(self._launch)
        self.btn_close.show(); self.update()

    def _launch(self):
        exe = str(Path(self.path.text().strip()) / "NeoNote.exe")
        # über den Explorer starten: so läuft NeoNote nicht mit Administratorrechten weiter
        subprocess.Popen(["explorer.exe", exe])
        self.close()

    def closeEvent(self, e):
        if getattr(self, "th", None) and self.th.isRunning():
            e.ignore()
            return
        QApplication.instance().exit(0 if self.result_ok else 1)
        super().closeEvent(e)


def _win_has_desktop_link():
    pub = Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop" / "NeoNote Media Player.lnk"
    return pub.exists()


def _win_has_assoc():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\RegisteredApplications", 0,
                            winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as k:
            winreg.QueryValueEx(k, "NeoNote")
        return True
    except OSError:
        return False


def run_setup():
    """Einstieg für den Installer: NeoNote.exe --setup --version x.y.z"""
    args = sys.argv
    version = args[args.index("--version") + 1] if "--version" in args else APP_VERSION
    src = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(args[0]).resolve().parent
    if "--src" in args:
        src = Path(args[args.index("--src") + 1])
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    st = QSettings(APP_NAME, APP_NAME)        # Farben des Benutzers übernehmen, falls schon eingestellt
    T.update({k: st.value(f"theme/{k}", v, type=type(v)) for k, v in DEFAULT_THEME.items()})
    w = SetupWindow(src, version)
    if "--silent" in args:                     # NeoNote-Setup.exe /S (z. B. Update aus NeoNote): ohne Fenster
        # Bestehende Einrichtung beibehalten: Desktop-Verknüpfung und „Öffnen mit“ nur, wenn schon vorhanden
        w.cb_desk.setChecked(_win_has_desktop_link())
        w.cb_assoc.setChecked(_win_has_assoc())
        w.cb_default.setChecked(False)
        w.th = None
        w._go()
        w.th.done.connect(lambda ok, _e: (w.th.wait(), QApplication.instance().exit(0 if ok else 1)))
    else:
        w.show()
    return app.exec()


def _selftest():
    """Prüft im fertigen Paket, ob alle Bausteine geladen werden (NEONOTE_SELFTEST=1)."""
    out = []
    for mod in ("py7zr", "ssl", "mutagen", "winrt.windows.media.playback", "winrt.windows.storage",
                "PySide6.QtMultimedia", "xml.etree.ElementTree", "urllib.request"):
        try:
            __import__(mod); out.append(f"{mod}: ok")
        except Exception as e:
            out.append(f"{mod}: FEHLT ({e})")
    out.append(f"mpv: {'ok' if mpv_available() else 'nicht vorhanden'}")
    try:
        import ssl
        ctx = ssl.create_default_context(); out.append(f"Zertifikate: {len(ctx.get_ca_certs())}")
    except Exception as e:
        out.append(f"Zertifikate: {e}")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "selftest.txt").write_text("\n".join(out), encoding="utf-8")


def main():
    if "--setup" in sys.argv:
        sys.exit(run_setup())
    if os.environ.get("NEONOTE_SELFTEST"):
        _selftest()
        return
    migrate_from_darkplayer()
    s = QSettings(APP_NAME, APP_NAME)
    blur = s.value("theme/blur", DEFAULT_THEME["blur"], type=bool)
    opacity = s.value("theme/opacity", DEFAULT_THEME["opacity"], type=int)
    # KWin kann Fenster nur über eine X11-Eigenschaft weichzeichnen lassen. Unter Wayland
    # läuft der Player dafür über XWayland – nur wenn alles Nötige vorhanden ist.
    if (blur and opacity < 100 and os.environ.get("XDG_SESSION_TYPE") == "wayland"
            and "QT_QPA_PLATFORM" not in os.environ and os.environ.get("DISPLAY")
            and "KDE" in os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
            and ctypes.util.find_library("xcb-cursor") and ctypes.util.find_library("X11")):
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    if IS_WIN and not getattr(sys, "frozen", False):
        # Nur beim Start aus dem Quelltext (sonst gruppiert Windows mit python.exe). Die installierte NeoNote.exe
        # bekommt bewusst keine eigene Kennung: dann gehören angeheftete Verknüpfungen auf NeoNote.exe
        # (auch mit eigenem Symbol) und das laufende Fenster zum selben Taskleisten-Knopf.
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("NeoNote.MediaPlayer")
        except Exception:
            pass
    QApplication.setApplicationName(APP_NAME)
    QApplication.setDesktopFileName("neonote")
    app = QApplication(sys.argv)
    if "--restart" in sys.argv:       # warten, bis die alte Instanz ihren Server freigegeben hat
        for _ in range(50):
            probe = QLocalSocket(); probe.connectToServer(SERVER_NAME)
            if not probe.waitForConnected(100):
                break
            probe.disconnectFromServer(); time.sleep(0.1)
    files = [arg_to_path(a) for a in sys.argv[1:] if not a.startswith("-")]
    # Läuft NeoNote schon? Dann Dateien dorthin schicken und beenden.
    sock = QLocalSocket()
    sock.connectToServer(SERVER_NAME)
    if sock.waitForConnected(400):
        if IS_WIN:
            try:   # die laufende Instanz darf ihr Fenster nach vorn holen (Klick kam ja vom Benutzer)
                ctypes.windll.user32.AllowSetForegroundWindow(-1)
            except Exception:
                pass
        sock.write(json.dumps(files).encode("utf-8"))
        sock.flush(); sock.waitForBytesWritten(1500)
        sock.disconnectFromServer()
        return
    app.setStyle("Fusion")
    global _SPLASH
    if s.value("ui/splash", True, type=bool) and not os.environ.get("NEONOTE_NOSPLASH"):
        T.update({k: s.value(f"theme/{k}", v, type=type(v)) for k, v in DEFAULT_THEME.items()})
        _SPLASH = Splash(); _SPLASH.show()
        splash_step(tr_("Lade die Einstellungen …"), 8)
    w = MainWindow()
    server = QLocalServer(w)
    server.setSocketOptions(QLocalServer.UserAccessOption)   # nur der eigene Benutzer darf Dateien schicken
    QLocalServer.removeServer(SERVER_NAME)
    server.listen(SERVER_NAME)
    server.newConnection.connect(lambda: w.receive_message(server.nextPendingConnection()))
    geo = s.value("window/geometry")
    if geo:
        w.restoreGeometry(geo)
    if s.value("window/maximized", False, type=bool):
        w.showMaximized()
    else:
        w.show()
    if _SPLASH is not None:
        w._splash = _SPLASH          # Referenz halten, bis das Ausblenden fertig ist
        _SPLASH.finish(w)
        _SPLASH = None
    if files:
        QTimer.singleShot(300, lambda: w.open_files(files))
    if IS_WIN and not mpv_available() and not s.value("win/mpv_asked", False, type=bool):
        def ask():
            s.setValue("win/mpv_asked", True)
            MpvDownloadDialog(w).exec()
        QTimer.singleShot(1200, ask)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
