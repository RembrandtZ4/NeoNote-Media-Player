"""Erzeugt die Dateisymbole für Windows (helle Dokumente mit Neon-Symbol und Formatkürzel).

Aufruf:  python make_icons.py <Zielordner>
Ergebnis: <ext>.ico je Format (16–256 px), dazu audio.ico / video.ico ohne Kürzel.
"""
import io
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import neonote as nn  # noqa: E402
from PySide6.QtCore import QBuffer, QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import (QColor, QFont, QGuiApplication, QImage, QLinearGradient, QPainter,  # noqa: E402
                           QPainterPath, QPen)
from PIL import Image  # noqa: E402

ACC = QColor("#2f86e0")          # NeoNote-Blau
ACC_V = ACC                      # Videos ebenfalls in NeoNote-Blau
SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)


def film_path(s, cx, cy, w, h):
    """Filmklappe/Filmstreifen: abgerundeter Rahmen mit Lochreihen und Play-Dreieck."""
    outer = QPainterPath(); outer.addRoundedRect(QRectF(cx - w / 2, cy - h / 2, w, h), w * 0.12, w * 0.12)
    holes = QPainterPath()
    hw, hh = w * 0.085, h * 0.11
    for i in range(5):
        x = cx - w / 2 + w * 0.08 + i * (w * 0.84 - hw) / 4
        for y in (cy - h / 2 + h * 0.07, cy + h / 2 - h * 0.07 - hh):
            holes.addRoundedRect(QRectF(x, y, hw, hh), hw * 0.3, hw * 0.3)
    tri = QPainterPath()
    tw = w * 0.26
    tri.moveTo(cx - tw * 0.42, cy - tw * 0.55); tri.lineTo(cx + tw * 0.62, cy); tri.lineTo(cx - tw * 0.42, cy + tw * 0.55)
    tri.closeSubpath()
    return outer, holes, tri


def draw_icon(size, kind, label):
    img = QImage(size, size, QImage.Format_ARGB32_Premultiplied); img.fill(Qt.transparent)
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
    s = size / 256.0
    small = size <= 32
    acc = ACC_V if kind == "video" else ACC
    # Blatt mit Eselsohr
    L, T, R, B = 40 * s, 14 * s, 216 * s, 242 * s
    if small:
        L, T, R, B = 30 * s, 8 * s, 226 * s, 248 * s
    fold = 52 * s if not small else 64 * s
    rad = 14 * s
    page = QPainterPath()
    page.moveTo(L + rad, T); page.lineTo(R - fold, T); page.lineTo(R, T + fold); page.lineTo(R, B - rad)
    page.quadTo(R, B, R - rad, B); page.lineTo(L + rad, B); page.quadTo(L, B, L, B - rad); page.lineTo(L, T + rad)
    page.quadTo(L, T, L + rad, T); page.closeSubpath()
    if size >= 48:                                            # weicher Schatten
        p.setPen(Qt.NoPen)
        for i, a in enumerate((18, 12, 7)):
            p.setBrush(QColor(0, 0, 0, a)); p.drawPath(page.translated(0, (2 + i * 2) * s))
    g = QLinearGradient(0, T, 0, B)
    g.setColorAt(0, QColor("#ffffff")); g.setColorAt(1, QColor("#eef1f5"))
    p.setBrush(g); p.setPen(QPen(QColor("#b9c1cc"), max(1.0, 3 * s)))
    p.drawPath(page)
    ear = QPainterPath(); ear.moveTo(R - fold, T); ear.lineTo(R - fold, T + fold - rad * 0.6)
    ear.quadTo(R - fold, T + fold, R - fold + rad * 0.6, T + fold); ear.lineTo(R, T + fold); ear.closeSubpath()
    eg = QLinearGradient(R - fold, T + fold, R, T)
    eg.setColorAt(0, QColor("#dfe4ea")); eg.setColorAt(1, QColor("#f7f9fb"))
    p.setBrush(eg); p.drawPath(ear)
    # Symbol in Neon-Optik (Schein + Röhre + heller Kern)
    cx = (L + R) / 2
    cy = (T + B) / 2 - (26 * s if label and size >= 40 else 0) + 6 * s
    if kind == "audio":
        outline, inner = nn.CoverCache._note_shape(1.0)
        paths = [outline, inner]
        target = (150 if small else 112) * s
    else:
        outer, holes, tri = film_path(1.0, 0, 0, 100, 78)
        paths = [outer, holes, tri]
        target = (168 if small else 128) * s
    # sauber zentrieren und auf Zielbreite skalieren
    box = QRectF()
    for pa in paths:
        box = box.united(pa.boundingRect())
    from PySide6.QtGui import QTransform
    k = target / max(box.width(), box.height() * 1.1)
    tf = QTransform().translate(cx, cy).scale(k, k).translate(-box.center().x(), -box.center().y())
    paths = [tf.map(pa) for pa in paths]
    if size >= 32:
        for wdt, a in ((14, 0.07), (9, 0.12), (6, 0.18)):
            c = QColor(acc); c.setAlphaF(a)
            p.setPen(QPen(c, wdt * s, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.setBrush(Qt.NoBrush)
            for pa in paths:
                p.drawPath(pa)
    p.setPen(QPen(acc, max(1.2, (5.2 if not small else 9) * s), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.setBrush(Qt.NoBrush)
    for pa in paths:
        p.drawPath(pa)
    if kind == "video":                                       # Play-Dreieck gefüllt
        p.setPen(Qt.NoPen); p.setBrush(acc); p.drawPath(paths[2])
    if size >= 64:
        core = QColor(255, 255, 255, 170)
        p.setPen(QPen(core, 1.4 * s, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.setBrush(Qt.NoBrush)
        for pa in paths[:1]:
            p.drawPath(pa)
    # Formatkürzel als Etikett unten
    if label and size >= 40:
        f = QFont("Segoe UI"); f.setWeight(QFont.Bold)
        f.setPixelSize(int((34 if len(label) <= 3 else 30 if len(label) == 4 else 25) * s))
        p.setFont(f)
        tw = p.fontMetrics().horizontalAdvance(label)
        bw, bh = max(tw + 30 * s, 92 * s), 46 * s
        br = QRectF(cx - bw / 2, B - 22 * s - bh, bw, bh)
        p.setPen(Qt.NoPen); p.setBrush(acc); p.drawRoundedRect(br, bh / 2, bh / 2)
        p.setPen(QColor("white")); p.drawText(br, Qt.AlignCenter, label)
    p.end()
    return img


def to_pil(img):
    buf = QBuffer(); buf.open(QBuffer.WriteOnly); img.save(buf, "PNG")
    return Image.open(io.BytesIO(bytes(buf.data()))).convert("RGBA")


def write_ico(path, kind, label):
    frames = [to_pil(draw_icon(sz, kind, label)) for sz in SIZES]
    big = frames[-1]
    big.save(path, format="ICO", sizes=[(sz, sz) for sz in SIZES], append_images=frames[:-1])
    # Pillow nimmt für jede Größe das große Bild verkleinert – wir wollen die eigenen Zeichnungen:
    _write_ico_exact(path, frames)


def _write_ico_exact(path, frames):
    import struct
    pngs = []
    for im in frames:
        b = io.BytesIO(); im.save(b, "PNG"); pngs.append(b.getvalue())
    head = struct.pack("<HHH", 0, 1, len(frames))
    off = 6 + 16 * len(frames)
    dirs, data = b"", b""
    for im, png in zip(frames, pngs):
        w = im.width if im.width < 256 else 0
        dirs += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(png), off + len(data))
        data += png
    Path(path).write_bytes(head + dirs + data)


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "icons"); out.mkdir(parents=True, exist_ok=True)
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)  # noqa: F841
    for e in sorted(nn.AUDIO_EXT | nn.VIDEO_EXT):
        kind = "video" if e in nn.VIDEO_EXT else "audio"
        write_ico(out / f"{e[1:]}.ico", kind, e[1:].upper())
    write_ico(out / "audio.ico", "audio", "")
    write_ico(out / "video.ico", "video", "")
    print(f"{len(list(out.glob('*.ico')))} Symbole in {out}")


if __name__ == "__main__":
    main()
