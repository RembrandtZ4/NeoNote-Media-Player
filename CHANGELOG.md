# Changelog

🇬🇧 **English** | 🇩🇪 [Deutsch](CHANGELOG.de.md)

## Next version (in progress)

### ✨ New features
- **Casting – DLNA, Chromecast and AirPlay:** the new cast button next to the volume slider plays music and videos on devices in your home network – AV receivers (e.g. Yamaha MusicCast), smart TVs, Chromecast/Google TV, network speakers and AirPlay speakers. NeoNote finds them by itself and becomes the remote: play/pause, skip, seeking and volume control the device, the next track follows automatically, and title, artist and cover appear on the device. “Continue on this PC” switches back at the same position. AirPlay: music only, for devices that accept unencrypted streaming (devices that require pairing are shown as not supported). Firewall: on Windows the installer allows NeoNote for your home network automatically; on Linux NeoNote detects an active firewall (ufw, firewalld) and opens it with one click and your password – on first use it offers this by itself (also in Settings ▸ System). Suggested by Holgi in the Deskmodder forum.

### ⚡ Improvements
- “Always on top” now uses **Ctrl+Alt+T** (Ctrl+Shift+T is “reopen closed tab” in browsers and was easy to hit by accident), and a short hint shows when it is switched on or off. Thanks to Holgi from the Deskmodder forum, whose reports led to this.
- Tooltips can now be switched separately: on buttons and icons (on by default) and on tracks and albums in lists (off by default) – Settings ▸ Appearance.

### 🐞 Bug fixes
- “Always on top” is only restored a few seconds after startup, once NeoNote is running smoothly – if it froze at startup, a frozen window could otherwise cover everything. In safe mode it stays off. Also, with “always on top”, dialogs (settings, “What’s new?” …) opened behind the main window and blocked it – NeoNote looked frozen. Dialogs now open on top, and for the Windows settings NeoNote steps back until you return. Reported by Holgi in the Deskmodder forum.
- Windows: “Default apps ▸ NeoNote” no longer shows an empty page when file associations are switched off – leftovers of earlier installations are removed.

## 1.3.2 – 2026-11-26

### ✨ New features
- **Updates and beta channel for the Arch package:** if NeoNote was installed from the Arch zip, the updater now downloads new versions itself and installs them in a terminal window (makepkg asks for your password there), then restarts NeoNote. Test versions (beta) are now also available as an Arch zip.
- **Safe mode and crash report:** if NeoNote closes unexpectedly shortly after starting, it starts once in safe mode next time (without hardware video decoding, background blur and media controls) and shows a report to copy – on Windows including the entry from the Windows Event Viewer. Safe mode can also be turned on permanently (Settings ▸ About).
- **Open music and videos with NeoNote** like VLC does: the installer option (and the button under Settings ▸ System) now makes NeoNote the default for every format that has no app chosen yet. Formats you or Windows already assigned stay protected by Windows – those you switch by hand. You can pick which formats: music and videos separately or one by one – in the installer and later under Settings ▸ System. Suggested by Holgi in the Deskmodder forum.
- **Animated dialogs:** settings and other dialogs fade in and glide up slightly when opening, and fade out when closing (Settings ▸ Appearance, can be turned off).
- **Update progress:** when NeoNote updates itself, a small window in the installer's look now shows the progress instead of nothing happening until NeoNote restarts.
- **Start in the background when signing in** (Settings ▸ System): NeoNote loads invisibly into the system tray when you sign in – clicking NeoNote then opens the window instantly. Closing only hides it; quit from the tray icon's menu.
- **What's new after an update:** after updating, NeoNote shows once what's new in this version (Settings ▸ About, can be turned off). “What's new?” in the update bar now starts right with the changes. Both are sorted into “New features”, “Improvements” and “Bug fixes”.
- **Uninstall:** like VLC, the uninstaller now offers to also delete your library, playlists, settings and cached covers (default: keep everything; music and video files are never touched). Suggested by Holgi in the Deskmodder forum.
- **Smoother window moving on older PCs (Windows):** Settings ▸ Appearance ▸ “Pause blur while moving the window” – the blur is switched off only while dragging or resizing.
- **Beta channel:** Settings ▸ System or ▸ About ▸ “Also offer test versions (beta)” – the updater then also offers test versions before they are officially released.

### ⚡ Improvements
- Tooltips look lighter: more translucent, finer border, properly rounded corners on Windows too (without the hard Windows shadow).
- Tooltips are now off by default (Settings ▸ Appearance ▸ “Show tooltips when hovering with the mouse”).
- Test versions show “Beta” next to the version number.
- **Faster start:** the finished library (albums, compilations, editions) is kept in a quick-start cache – with large libraries the library step takes only about a third of the time.
- **Instant start feedback (Windows):** a start screen appears right when you click NeoNote, before Python and Qt are loaded – previously nothing happened for about two seconds.
- **Reopening a running NeoNote is much faster (Windows):** it hands over to the running instance before loading Qt – especially noticeable with “Start in the background when signing in” and when opening files.

### 🐞 Bug fixes
- Arch zip: `./install.sh` stopped with “en.json was not found” (1.3.1). Fixed.
- Windows: after installing or updating, an empty folder “NeoNote-Setup.tmp” could be left behind in “Program Files”. The installer now removes it reliably; the uninstaller also cleans up leftovers from older versions. Reported by Holgi in the Deskmodder forum.
- Appearance: changing colors or the blur reacted slowly. The blur now switches instantly, and color changes no longer reload every cover from disk.
- Settings open faster: the audio device list and file associations load right after the window appears.
- Settings: the window opens at its usual size again and can be made smaller; long tabs scroll instead of being squeezed.
- **Frozen NeoNote in the background (Windows):** if a running (e.g. preloaded) NeoNote no longer responds, clicking NeoNote used to do nothing at all. NeoNote now notices this after a few seconds and offers to end the frozen instance and start fresh.
- The start screen shown on click is now closed again as a safety measure if it stays up for some reason; dialogs always close even if their fade-out animation gets stuck.

## 1.3.1 – 2026-11-24

### ⚡ Improvements
- **Always on top:** pin button next to “Minimize” (and in the ☰ menu, Ctrl+Shift+T). Suggested by Holgi in the Deskmodder forum.
- Tooltips and right-click menus now match the window: translucent, rounded corners and blur. Can be turned off under Settings ▸ Appearance.

### 🐞 Bug fixes
- Update check: if the GitHub API can't be reached (e.g. rate limit), NeoNote falls back to the release page; the message now shows the reason.
- Update check and all online features failed on fresh Windows installations (e.g. Windows Sandbox) with “No connection to GitHub”: Windows only downloads missing root certificates when a browser needs them. NeoNote now ships its own certificate list as a fallback.
- Windows: “Always on top” didn't keep the window on top – fixed in the 1.3.1 download on release day.
- Settings: the window is tall enough for the largest tab (rows were squeezed together before).

## 1.3 – 2026-11-23

### ✨ New features
- **Crossfade** between tracks (Settings ▸ System ▸ Transitions, 1–12 seconds): the next track fades in while the current one fades out. Within an album NeoNote stays gapless if you like, so live and concept albums aren't cut up.
- **Playback speed** 0.5× to 2× with pitch correction (☰ menu) – great for audiobooks and podcasts; a badge in the control bar shows when it's not 1×.
- **Choose the output device and bit-perfect playback** for external DACs (Settings ▸ System ▸ Audio output): exclusive access (WASAPI exclusive on Windows), music goes to the device unchanged at the file's sample rate and bit depth – without volume, equalizer, ReplayGain or resampling. If you'd still rather use NeoNote's volume slider, there's an option for that (exclusive, but no longer strictly bit-perfect).
- **Folder view:** browse your music folders like in a file manager – folders as tiles with cover stacks, the tracks of a folder as a list (new “Folders” entry in the navigation).
- **Rename and organize files** by pattern, e.g. `{albumartist}/{album}/{track} {title}` – with a preview before anything moves. `.lrc` files move along; stars, play counts and playlists are updated; empty folders are removed. Organize ▸ “Undo last organize” moves everything back.
- **Scrobbling** to ListenBrainz (user token) and Last.fm (your own free API key, the password isn't stored): tracks count once you've actually listened to half (or 4 minutes); without a connection they're sent later.
- **Artist info** in “Now playing” and in the right column (button next to lyrics, `Ctrl+I`): biography from Wikipedia, years active, origin and genres from MusicBrainz, similar artists from ListenBrainz – the ones in your collection are clickable.
- **Visualization** in “Now playing” (right-click ▸ Visualization, `Ctrl+Shift+V`): spectrum bars with falling peaks or flowing waves in your accent color – based on real frequency bands of the music.
- **Auto DJ:** right-click a track ▸ “Auto DJ from this track”, or ☰ ▸ Auto DJ – endless matching music from your own collection (same genre, similar artists, similar era, your ratings), never the same artist twice in a row.
- **Star ratings are now written into the music files**, just like Windows Media Player does: MP3 and WMA in WMP's own format (so WMP12 shows them too), FLAC, Ogg and Opus as `FMPS_RATING` (read by Strawberry, Clementine, Amarok). Your stars survive crashes, reinstalls and switching between Windows and Linux. Ratings you already gave in NeoNote are added to the files once. The file's modification date stays the same, so backup and sync tools don't treat the files as new. The track that is currently playing is written after it ends. Can be turned off under Settings ▸ Online information.

### ⚡ Improvements
- Installer: instead of the gray “Preparing setup …” box, a start window in NeoNote's look appears while the files are unpacked – with the neon note, version and a running progress bar; it fades out as soon as the setup window opens.
- Settings now have **OK**, **Apply** and **Cancel**: “Apply” saves without closing the window. The window is wide enough for all tabs.
- Dialogs have exactly the same opacity as the main window, and the opacity slider reacts instantly (only repaints instead of rebuilding the whole look).

### 🐞 Bug fixes
- Movies with 5.1/7.1 audio (e.g. DTS) had no voices on stereo speakers and headphones because the center channel got lost. NeoNote now downmixes movie audio to stereo itself; with a surround system you can switch to unchanged multichannel output (Settings ▸ Video).
- Flatpak: mpv didn't start (missing Lua options), so everything ran through the less capable Qt Multimedia fallback – no image subtitles, no DTS audio, freezes. Fixed; the fallback itself no longer crashes on Linux either.
- Lyrics: if a file only contains plain lyrics without timestamps (common in ripped MP3s), NeoNote now also looks for synced lyrics on LRCLIB and prefers them – so the lyrics scroll along. Plain lyrics now also move along slowly with the song.
- With the playlist hidden, the lyrics button no longer jumps to “Now playing”; it shows the playlist together with the lyrics below it.
- Clearing a track's stars in NeoNote now stays cleared – a full rescan no longer brings back an old rating from the file.
- Linux: dialogs were opaque with black corners instead of translucent with rounded corners. Fixed.
- Linux/KDE: NeoNote's window was missing from the task manager (and pinned launchers weren't marked as running); the app icon now has a margin so the “running” line underneath is visible.
- Flatpak: music folders on other drives (e.g. `/media/…` or internal NTFS disks) can now be added; if a folder isn't readable, NeoNote says so clearly. Dialog buttons no longer show KDE icons.

## 1.2 – 2026-11-20

### ✨ New features
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

### 🐞 Bug fixes
- When editing directly in the track list (F2), the selected text was white on a light background and hard to read; the input field also cut off the text at the top and bottom.
- After a movie, the “Tracks” button stayed visible while listening to music.
- Library, statistics (ratings, play counts, “Recently played”), edits and playlists are now saved safely: first to a temporary file, then swapped, with the previous version kept as `.bak`. If NeoNote crashes while saving, nothing is lost – the backup is read at the next start.

## Earlier versions

The changes up to 1.1.9 are described in German in [CHANGELOG.de.md](CHANGELOG.de.md); English descriptions are in the [release notes](https://github.com/RembrandtZ4/NeoNote-Media-Player/releases).
