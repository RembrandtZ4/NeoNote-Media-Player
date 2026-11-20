# Changelog

🇬🇧 **English** | 🇩🇪 [Deutsch](CHANGELOG.de.md)

## Next version (in progress)

**New**
- **Star ratings are now written into the music files**, just like Windows Media Player does: MP3 and WMA in WMP's own format (so WMP12 shows them too), FLAC, Ogg and Opus as `FMPS_RATING` (read by Strawberry, Clementine, Amarok). Your stars survive crashes, reinstalls and switching between Windows and Linux. Ratings you already gave in NeoNote are added to the files once. The file's modification date stays the same, so backup and sync tools don't treat the files as new. The track that is currently playing is written after it ends. Can be turned off under Settings ▸ Online information.

**Fixes**
- Clearing a track's stars in NeoNote now stays cleared – a full rescan no longer brings back an old rating from the file.

## 1.2 – 2026-11-20

**New**
- **Videos via mpv:** videos now play through mpv, which renders directly on the graphics card – smooth 4K, HDR videos with correct colors on regular screens, hardware decoding via D3D11VA, VA-API or NVDEC. Image subtitles from Blu-rays and DVDs (PGS, VobSub) now work, as do .ass and .vtt subtitles. Subtitles move up while the control bar is visible. Can be turned off under Settings ▸ Video; without mpv, videos play through Qt Multimedia as before.
- **Lyrics** in “Now playing”: the cover moves to the left, the lyrics appear on the right. Synced lyrics scroll along with the current line highlighted; click a line to jump there, scroll with the mouse wheel. Sources in this order: a `.lrc` file with the same name next to the track, lyrics stored in the file (MP3, FLAC, OGG, M4A, WMA …), otherwise online from **LRCLIB** (can be turned off under Settings ▸ Online information). Toggle with the new button in the control bar or `Ctrl+T`. In the library the lyrics appear on the right below the playlist (height adjustable with the splitter). Right-click to save lyrics found online as a `.lrc` file next to the track.
- **Smart playlists** like in WMP12: rules for artist, album artist, album, title, genre, year, rating, play count, last played, date added, length, file type and folder – e.g. “genre contains rock” and “year between 1980 and 1989”, or “never played”. Match all or any rule, limit to a number of tracks or minutes, sort as you like (including random, reshuffled daily). The editor shows right away how many tracks match. The lists update themselves and appear with a lightning icon under Playlists (Organize ▸ “New smart playlist…” or right-click “Playlists”).
- **Sleep timer** (☰ menu and system tray): after 15, 30, 45, 60, 90 minutes or a custom time, after this track or after this album. At the end the volume fades out over 10 seconds and playback pauses – “Play” later continues at the same spot. While it runs, a moon in the control bar shows the remaining time; click it to change or stop the timer.
- **Dialogs in the window's look:** with the custom title bar, Settings, Equalizer, album info, confirmations and all other dialogs now have no system frame either, but their own title bar, rounded corners and the same translucent, blurred background as the main window (slightly more opaque so text stays readable). Move them by the title bar, resize at the edges. Can be turned off under Settings ▸ Appearance.
- **Resume:** long videos and audiobooks (20 minutes or more) remember where you stopped and continue there next time. If you watched almost to the end, it starts from the beginning. Can be turned off under Settings ▸ Video.
- **Chapters:** movies with chapters show a chapter list in the tracks menu; `Ctrl+PgDown` / `Ctrl+PgUp` jumps to the next or previous chapter.
- **Crash protection for videos:** if NeoNote crashes while starting a video, it decodes without hardware acceleration next time; if it crashes again, videos play through Qt Multimedia. A notice says what was changed. On Windows, mpv uses the stable copy modes (e.g. `d3d11va-copy`) – decoding still happens on the graphics card.
- If a video was open last, NeoNote no longer shows its still frame at startup; the video just sits in the queue and continues where you left off when played. To get the still frame back: Settings ▸ Video.
- **Flatpak** for all Linux systems (Fedora, Ubuntu, Mint, openSUSE, Steam Deck …): `NeoNote-1.2-x86_64.flatpak` is attached to the release; install with a double-click in Discover/GNOME Software or with `flatpak install`. Includes libmpv and everything else needed; NeoNote shows updates, which you install via Discover or `flatpak update`.

**Fixes**
- When editing directly in the track list (F2), the selected text was white on a light background and hard to read; the input field also cut off the text at the top and bottom.
- After a movie, the “Tracks” button stayed visible while listening to music.
- Library, statistics (ratings, play counts, “Recently played”), edits and playlists are now saved safely: first to a temporary file, then swapped, with the previous version kept as `.bak`. If NeoNote crashes while saving, nothing is lost – the backup is read at the next start.

## Earlier versions

The changes up to 1.1.9 are described in German in [CHANGELOG.de.md](CHANGELOG.de.md); English descriptions are in the [release notes](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases).
