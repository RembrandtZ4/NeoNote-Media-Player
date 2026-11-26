#!/usr/bin/env bash
# Baut NeoNote als Arch-/CachyOS-Paket und installiert es samt aller Abhängigkeiten.
set -e
cd "$(dirname "$(readlink -f "$0")")"

if ! command -v makepkg >/dev/null 2>&1; then
  echo "makepkg wurde nicht gefunden. Dieses Skript ist für Arch Linux / CachyOS gedacht."
  exit 1
fi
if [ "$(id -u)" -eq 0 ]; then
  echo "Bitte nicht als root bzw. mit sudo starten – das Skript fragt selbst nach dem Passwort."
  exit 1
fi

# makepkg sucht lokale Quellen direkt in diesem Ordner
[ -f en.json ] || cp i18n/en.json en.json

echo "NeoNote wird gebaut und installiert."
echo "Fehlende Pakete (PySide6, mpv, …) installiert pacman automatisch mit – dafür wird dein Passwort abgefragt."
echo
makepkg -si --cleanbuild
rm -rf src pkg neonote-*.pkg.tar.* en.json

echo
echo "Fertig! NeoNote findest du im Anwendungsmenü oder startest ihn mit:  neonote"
