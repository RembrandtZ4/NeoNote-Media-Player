"""Zeichnet das Bild des Installer-Startfensters (NeoNote-Look) als Rohdaten für neonote-splash.exe.
Aufruf: python3 make_splash.py <version> <neonote.png>  →  splash_<lang>_<scale>.bin + splash.rc"""
import struct, sys, os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (QGuiApplication, QImage, QPainter, QColor, QLinearGradient, QRadialGradient, QFont,
                           QPainterPath, QPen)

VER, ICON = sys.argv[1], sys.argv[2]
ACC = QColor("#3d8fe0")
TEXT = {"de": "Setup wird vorbereitet …", "en": "Preparing setup …"}
SCALES = (1.0, 1.25, 1.5, 2.0)
app = QGuiApplication([])
icon = QImage(ICON)
rc = []
rid = 101
for lang in ("de", "en"):
    for sc in SCALES:
        M = 26                                   # Rand für den Schatten
        CW, CH = 420, 200
        W, H = int((CW + 2 * M) * sc), int((CH + 2 * M + 6) * sc)
        img = QImage(W, H, QImage.Format_ARGB32_Premultiplied); img.fill(Qt.transparent)
        p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.scale(sc, sc)
        card = QRectF(M, M - 4, CW, CH)
        R = 14
        # weicher Schatten
        for i in range(18, 0, -1):
            a = int(5.5 * (1 - i / 19) ** 1.6 * 10)
            path = QPainterPath(); path.addRoundedRect(card.adjusted(-i, -i + 6, i, i + 6), R + i, R + i)
            p.fillPath(path, QColor(0, 0, 0, max(1, int(a / 1.6))))
        # Glasfläche
        path = QPainterPath(); path.addRoundedRect(card, R, R)
        g = QLinearGradient(card.topLeft(), card.bottomLeft())
        g.setColorAt(0, QColor(30, 35, 44, 250)); g.setColorAt(1, QColor(16, 19, 24, 250))
        p.fillPath(path, g)
        p.save(); p.setClipPath(path)
        glow = QRadialGradient(QPointF(card.left() + 92, card.center().y() - 8), 150)
        c = QColor(ACC); c.setAlpha(70); glow.setColorAt(0, c); c.setAlpha(0); glow.setColorAt(1, c)
        p.fillRect(card, glow)
        band = QLinearGradient(card.topLeft(), card.bottomLeft())
        for pos, a in ((0.0, 0), (0.62, 0), (0.78, 26), (1.0, 0)):
            c = QColor(ACC); c.setAlpha(a); band.setColorAt(pos, c)
        p.fillRect(card, band)
        p.restore()
        p.setPen(QPen(QColor(255, 255, 255, 30), 1)); p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(card.adjusted(0.5, 0.5, -0.5, -0.5), R, R)
        # Neon-Note
        S = 96
        ir = QRectF(card.left() + 44, card.top() + 34, S, S)
        p.drawImage(ir, icon.scaled(int(S * sc), int(S * sc), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # Texte
        x = ir.right() + 26
        f = QFont(); f.setPixelSize(22); f.setWeight(QFont.DemiBold)
        p.setFont(f); p.setPen(QColor(255, 255, 255))
        p.drawText(QRectF(x, card.top() + 44, card.right() - x - 20, 30), Qt.AlignLeft | Qt.AlignVCenter, "NeoNote")
        f2 = QFont(); f2.setPixelSize(15)
        p.setFont(f2); p.setPen(QColor(255, 255, 255, 200))
        p.drawText(QRectF(x, card.top() + 74, card.right() - x - 20, 22), Qt.AlignLeft | Qt.AlignVCenter,
                   f"Media Player {VER}")
        f3 = QFont(); f3.setPixelSize(13)
        p.setFont(f3); p.setPen(QColor(255, 255, 255, 140))
        p.drawText(QRectF(x, card.top() + 104, card.right() - x - 20, 20), Qt.AlignLeft | Qt.AlignVCenter, TEXT[lang])
        # Spur des Fortschrittsbalkens (den laufenden Teil zeichnet neonote-splash.exe)
        bar = QRectF(card.left() + 44, card.bottom() - 36, CW - 88, 4)
        p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, 22)); p.drawRoundedRect(bar, 2, 2)
        p.end()
        bx, by, bw, bh = (int(round(v * sc)) for v in (bar.left(), bar.top(), bar.width(), bar.height()))
        # Kopf: Breite, Höhe, Balken x/y/b/h, Maßstab ×100 – danach BGRA (vormultipliert), Zeile für Zeile von oben
        raw = struct.pack("<7i", W, H, bx, by, bw, bh, int(sc * 100)) + bytes(img.constBits())[:W * H * 4]
        name = f"splash_{lang}_{int(sc * 100)}.bin"
        open(name, "wb").write(raw)
        rc.append(f'{rid} RCDATA "{name}"')
        if lang == "de" and sc == 1.0:
            img.save("preview_de.png")
        rid += 1
open("splash.rc", "w").write("\n".join(rc) + '\n1 ICON "neonote.ico"\n')
print("ok", rid - 101, "Bilder")
