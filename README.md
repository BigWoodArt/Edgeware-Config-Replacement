# Edgeware++ Pretty Configuration Manager — v21 Edition (21.1.2)

#### WHAT IT DOES

Replaces Edgeware++ v21's config.pyw with a prettier one: same settings, plus theme and pack switching without restarting, intensity presets, a Corruption Preview tab, and a WebP→GIF converter (fixes WebP files that show up black).



#### INSTALL

1. Open your EdgewarePlusPlus-21\\edgeware folder.
2. Back up your existing config.pyw (e.g. as config\_original.pyw).
3. Replace it with the config.pyw from this repo. Don't replace other source files.
4. Run config.pyw normally.

Note: running EdgewareSetup.bat again recreates the plain config.pyw. Keep a copy of this one.



#### FEATURES

- **Load Pack Configuration** (Start page): copies a pack's own settings into yours.
- **Run log:** Save, Exit, and Run records Edgeware's output to `data/logs/edgeware_run.log`, warns about settings that make it look broken (for example, all chances at 0), and reports a startup crash. "View last run log" is in the sidebar.
- **GIF converter:** v21 does not handle animated WebP. This converts a pack's WebP files to GIF (256 colors, shared palette to reduce flicker, progress and cancel). Each WebP is deleted only after its GIF is written successfully.



#### WANT MORE?

**Edgeware++ v22** adds Do Not Press, Pack Priority, a full-screen spiral with binaural audio, multi-site booru downloads, web video takeover, and many bug fixes.

**Switch here:** https://github.com/BigWoodArt/Edgeware-Unofficial-v22



#### CHANGELOG

**21.1.2** — Added run log, startup-crash detection, and pre-run warnings.

**21.1.1** — Rebuilt to match exactly what stock v21 supports. Added Load Pack Configuration.

**v5** — Renamed "Allow buttonless" to "Force buttonless." Fixed light theme colors. Added Change/Restore Panic Wallpaper. Grouped related settings. Labeled popup delay in ms. Auto-migrates new defaults without touching customized values. Corrected inverted corruption-cycle toggles. Improved slider styling.
