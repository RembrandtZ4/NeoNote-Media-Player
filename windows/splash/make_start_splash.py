"""Erzeugt start_splash.png für den PyInstaller-Startbildschirm: erscheint sofort beim Klick auf NeoNote,
noch bevor Python und Qt geladen sind, und wird dann nahtlos vom Startbild in NeoNote abgelöst.
Aufruf:  python make_start_splash.py <pfad/zu/neonote.py> <ziel.png>
Magenta (#ff00ff) markiert für den Startbildschirm durchsichtige Stellen (runde Ecken)."""
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("NEONOTE_NOSPLASH", "1")
src, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.dirname(os.path.abspath(src)))
sys.argv = [sys.argv[0]]
import importlib.util
spec = importlib.util.spec_from_file_location("neonote", src)
nn = importlib.util.module_from_spec(spec); spec.loader.exec_module(nn)
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPainter, QColor
app = QApplication.instance() or QApplication([])
nn.T.update(dict(nn.DEFAULT_THEME))
s = nn.Splash(); s._anim.stop(); s.pct = s.shown_pct = 0
img = s.grab().toImage().convertToFormat(QImage.Format_ARGB32)
bg = QColor("#0e1014")                      # Kanten vorab auf Dunkel mischen, damit kein rosa Saum entsteht
outimg = QImage(img.size(), QImage.Format_RGB32)
for y in range(img.height()):
    for x in range(img.width()):
        c = img.pixelColor(x, y); a = c.alphaF()
        if a < 0.5:
            outimg.setPixelColor(x, y, QColor(255, 0, 255))
        else:
            outimg.setPixelColor(x, y, QColor(round(c.red() * a + bg.red() * (1 - a)),
                                              round(c.green() * a + bg.green() * (1 - a)),
                                              round(c.blue() * a + bg.blue() * (1 - a))))
outimg.save(out)
print(out, outimg.width(), outimg.height())
