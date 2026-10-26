# Edgeware++ Pretty Configuration Manager v21 Edition (config.pyw 21.1.2)

#### WHAT IT DOES

Replaces Edgeware++'s config.pyw with a prettier one — same capabilities, plus theme/pack switching without restarting, and a WebP→GIF converter (fixes WebP files that show up black).



#### INSTALL

1. Open your EdgewarePlusPlus-21\\edgeware folder.
2. Back up your existing config.pyw (e.g. config\_original.pyw).
3. Replace it with the config.pyw in this ZIP. Don't replace other source files.
4. Run config.pyw normally.



#### GIF CONVERTER

v21 does not handle WebP files. Use this to convert the files in your packs, if needed. GIF is capped at 256 colors, less faithful than WebP — but uses a shared animation palette to reduce flicker, with background conversion, progress, and cancellation. Deletes each WebP only after its GIF is written successfully.



#### NOT IN THIS VERSION

**Do Not Press, Pack Priority, spiral/binaural overlay, multi-site booru picker, and web video takeover are not available here.** They need the modified v22 engine (`main_edgeware.py` and others), which stock v21 does not have. This config only edits settings; it can't add engine features. To use Do Not Press, switch to Edgeware++ v22. Stock v21's own Panic Lockout setting still works normally.

In v21, use **Load Pack Configuration** (Start page) to copy a pack's own settings into yours.



#### RUN LOG

Save, Exit, and Run records Edgeware's output to `data/logs/edgeware_run.log`, warns about settings that make it look broken (e.g. all chances at 0), and reports a startup crash. "View last run log" is in the sidebar.



#### CHANGELOG

**v21.1.2** — Added run log, startup-crash detection, and pre-run warnings.

**v21.1.1** — Rebuilt from the v22.3.6 config limited to v21 features. Removed Do Not Press (needs v22 engine), Pack Priority, and other v22-only settings. Added Load Pack Configuration.

**v21.2.9** — Removed Spiral+Binaural overlay, Gelbooru API key/user ID fields (site picker now a single dropdown), and Image resize quality — none exist in v21. Disabled the update checker (compared against an incompatible v22 fork).

**v9** — Skipped v7-8 to match another config.pyw project. Fixed Pack Priority, with a note per affected setting.

**v6** — (older build; Do Not Press and Pack Priority were later removed, see above)   Greyed out settings when their parent is off. Save-issue fixes.

**v5** — Renamed "Allow buttonless" to "Force buttonless." Removed non-functional Edgeware Appearance control. Fixed light theme colors. Added Change/Restore Panic Wallpaper. Grouped related settings. Labeled popup delay in ms. Auto-migrates new defaults without touching customized values. Corrected inverted corruption-cycle toggles. Improved slider styling.

