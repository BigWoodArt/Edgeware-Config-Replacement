# Edgeware++ Pretty Configuration Manager v21.2.9

#### WHAT IT DOES

Replaces Edgeware++'s config.pyw with a prettier one — same capabilities, plus theme/pack switching without restarting, and a WebP→GIF converter (fixes WebP files that show up black).



#### INSTALL

1. Open your EdgewarePlusPlus-21\\edgeware folder.
2. Back up your existing config.pyw (e.g. config\_original.pyw).
3. Replace it with the config.pyw in this ZIP. Don't replace other source files.
4. Run config.pyw normally.



#### GIF CONVERTER

v21 does not handle WebP files. Use this to convert the files in your packs, if needed. GIF is capped at 256 colors, less faithful than WebP — but uses a shared animation palette to reduce flicker, with background conversion, progress, and cancellation. Deletes each WebP only after its GIF is written successfully.



#### CHANGELOG

**v21.2.9** — Removed Spiral+Binaural overlay, Gelbooru API key/user ID fields (site picker now a single dropdown), and Image resize quality — none exist in v21. Disabled the update checker (compared against an incompatible v22 fork).

**v9** — Skipped v7-8 to match another config.pyw project. Fixed Pack Priority, with a note per affected setting.

**v6** — Added Do Not Press (runs on startup after random hibernation, with warnings). Added Pack Priority vs Default Priority. Greyed out settings when their parent is off. Save-issue fixes.

**v5** — Renamed "Allow buttonless" to "Force buttonless." Removed non-functional Edgeware Appearance control. Fixed light theme colors. Added Change/Restore Panic Wallpaper. Grouped related settings. Labeled popup delay in ms. Auto-migrates new defaults without touching customized values. Corrected inverted corruption-cycle toggles. Improved slider styling.

