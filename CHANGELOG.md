# Changelog

🇬🇧 **English** | 🇩🇪 [Deutsch](CHANGELOG.de.md)

## Next version (in progress)

**New**
- **Crossfade** between tracks (Settings ▸ System ▸ Transitions, 1–12 seconds): the next track fades in while the current one fades out. Within an album NeoNote stays gapless if you like, so live and concept albums aren't cut up.
- **Playback speed** 0.5× to 2× with pitch correction (☰ menu) – great for audiobooks and podcasts; a badge in the control bar shows when it's not 1×.
- **Choose the output device and bit-perfect playback** for external DACs (Settings ▸ System ▸ Audio output): exclusive access (WASAPI exclusive on Windows), music goes to the device unchanged at the file's sample rate and bit depth – without volume, equalizer, ReplayGain or resampling.
- **Folder view:** browse your music folders like in a file manager – folders as tiles with cover stacks, the tracks of a folder as a list (new “Folders” entry in the navigation).
- **Rename and organize files** by pattern, e.g. `{albumartist}/{album}/{track} {title}` – with a preview before anything moves. `.lrc` files move along; stars, play counts and playlists are updated; empty folders are removed. Organize ▸ “Undo last organize” moves everything back.
- **Scrobbling** to ListenBrainz (user token) and Last.fm (your own free API key, the password isn't stored): tracks count once you've actually listened to half (or 4 minutes); without a connection they're sent later.
- **Artist info** in “Now playing” and in the right column (button next to lyrics, `Ctrl+I`): biography from Wikipedia, years active, origin and genres from MusicBrainz, similar artists from ListenBrainz – the ones in your collection are clickable.
- **Visualization** in “Now playing” (right-click ▸ Visualization, `Ctrl+Shift+V`): spectrum bars with falling peaks or flowing waves in your accent color – based on real frequency bands of the music.
- **Auto DJ:** right-click a track ▸ “Auto DJ from this track”, or ☰ ▸ Auto DJ – endless matching music from your own collection (same genre, similar artists, similar era, your ratings), never the same artist twice in a row.
- **Star ratings are now written into the music files**, just like Windows Media Player does: MP3 and WMA in WMP's own format (so WMP12 shows them too), FLAC, Ogg and Opus as `FMPS_RATING` (read by Strawberry, Clementine, Amarok). Your stars survive crashes, reinstalls and switching between Windows and Linux. Ratings you already gave in NeoNote are added to the files once. The file's modification date stays the same, so backup and sync tools don't treat the files as new. The track that is currently playing is written after it ends. Can be turned off under Settings ▸ Online information.

**Improved**
- Installer: instead of the gray “Preparing setup …” box, a start window in NeoNote's look appears while the files are unpacked – with the neon note, version and a running progress bar; it fades out as soon as the setup window opens.

**Fixes**
- Lyrics: if a file only contains plain lyrics without timestamps (common in ripped MP3s), NeoNote now also looks for synced lyrics on LRCLIB and prefers them – so the lyrics scroll along. Plain lyrics now also move along slowly with the song.
- With the playlist hidden, the lyrics button no longer jumps to “Now playing”; it shows the playlist together with the lyrics below it.
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
