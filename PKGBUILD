# NeoNote – Paket für Arch Linux / CachyOS
# Installation:  ./install.sh   (oder: makepkg -si)
# Entfernen:     sudo pacman -R neonote

pkgname=neonote
pkgver=1.3.2
pkgrel=1
epoch=1
pkgdesc="NeoNote Media Player – Musik- und Videoplayer im Stil von Windows Media Player 12"
arch=('any')
url='https://github.com/RembrandtZ4/NeoNote-Media-Player'
license=('GPL-3.0-only')
depends=(
  'python'
  'pyside6'
  'qt6-multimedia'
  'qt6-multimedia-ffmpeg'
  'python-mutagen'
  'mpv'
  'python-mpv'
  'python-jeepney'
)
optdepends=(
  'xdg-utils: Ordner öffnen, falls kein Dateimanager über D-Bus erreichbar ist'
)
source=('neonote.py' 'neonote.sh' 'neonote.desktop' 'neonote.png' 'README.md' 'en.json' 'LICENSE' 'THIRD_PARTY_NOTICES.md')
sha256sums=('SKIP' 'SKIP' 'SKIP' 'SKIP' 'SKIP' 'SKIP' 'SKIP' 'SKIP')

package() {
  install -Dm644 neonote.py      "$pkgdir/usr/share/neonote/neonote.py"
  install -Dm755 neonote.sh      "$pkgdir/usr/bin/neonote"
  install -Dm644 neonote.desktop "$pkgdir/usr/share/applications/neonote.desktop"
  install -Dm644 neonote.png     "$pkgdir/usr/share/icons/hicolor/256x256/apps/neonote.png"
  install -Dm644 en.json        "$pkgdir/usr/share/neonote/i18n/en.json"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/neonote/LICENSE"
  install -Dm644 THIRD_PARTY_NOTICES.md "$pkgdir/usr/share/licenses/neonote/THIRD_PARTY_NOTICES.md"
  install -Dm644 README.md          "$pkgdir/usr/share/doc/neonote/README.md"
  # woher das Paket stammt – der Updater in NeoNote richtet sich danach
  echo zip | install -Dm644 /dev/stdin "$pkgdir/usr/share/neonote/package-source"
}
