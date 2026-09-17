# Edgeware++ Pretty Configuration Manager v21.2.9



#### \---WHAT IT DOES---


This config.pyw replaces the current config file in Edgeware++'s current release to make it prettier. It should have the same capabilities, plus a few new ones. Namely, it allows you to select themes and select packs without restarting the whole window. There's also a WEBP-to-GIF converter. Sometimes WEBP files show up black on Edgeware, so this built-in converter will fix those images.



##### \---INSTALL---



1. Open your EdgewarePlusPlus-21\\edgeware folder.
2. Back up your existing config.pyw (for example: config\_original.pyw).
3. Replace config.pyw with the config.pyw in this ZIP.
4. Do not replace Edgeware's other source files manually.
5. Run config.pyw normally.

PANIC WALLPAPER
The manager writes the selected panic wallpaper to data\\panic\_wallpaper.png, which matches Edgeware's CustomAssets panic-wallpaper path. A backup named panic\_wallpaper.before\_pretty\_v5.bak is made before replacing an existing custom wallpaper.



##### \---GIF CONVERTER---


GIF QUALITY
GIF is inherently limited to 256 colors and will not be as faithful as WebP. The included converter uses a shared animation palette to reduce frame-to-frame color flicker and performs conversion in the background with progress and cancellation.
SAFETY
The WebP converter changes the selected pack permanently and deletes each WebP only after a successful GIF is written.
The Panic Wallpaper tool changes data\\panic\_wallpaper.png and keeps a backup before replacement.

Note for this v21 build: only WebP → GIF is offered. GIF → WebP is left out on purpose — v21 sends every popup (img and hypno/subliminal alike) through mpv, and mpv can't decode animated WebP anywhere, so converting to WebP would just reintroduce the black-square problem.



##### \---EDGEWARE THEME BACKGROUND---



The Troubleshooting tab still includes the separate "Fix Edgeware theme background" compatibility tool from v4. It patches src\\features\\popup.py only when the installed file matches the expected layout and keeps a .before\_pretty\_v5.bak backup. Restart Edgeware after applying it. This is separate from Manager Appearance.



###### \---WHAT IS NEW IN v21.2.9 (this v21 build)---

* Removed the Full-Screen Spiral + Binaural Audio option and its image picker — this is a newer engine feature v21 doesn't have, so it would have shown up in the manager but done nothing.
* Removed the Gelbooru API key / user ID fields, and changed "Sites to search" from a multi-site checklist back to a single Site dropdown. v21's downloader only ever reads one site name (`booruName`), not a list — the checklist was silently writing to a key v21 never reads.
* Removed the Image resize quality (Bilinear/Bicubic/Lanczos) option — not a setting v21's image code reads.
* Disabled the version-update checker. It was checking against an unofficial v22 fork's version numbers, which would always look "newer" than this v21 build's version and send you to an incompatible download.
* (Carried over from earlier v21 fixes, still true here): Pack Priority is applied by writing the pack's values in at Save time, since v21 has no per-launch auto-merge like v22 does. GIF→WebP conversion stays removed for the reason noted above.

###### \---WHAT IS NEW IN v9---

* Skipped v7-8 to match this config.pyw with another config.pyw project I'm working on.
* Fixes for Pack Priority and a clear note for each setting that is affected by it.





###### \---WHAT IS NEW IN v6---

* Added a DO NOT PRESS button that will cause the program to run on startup after a varying hibernation time. Warnings and descriptions appear on first press. Be careful!
* There's now a selection of PACK PRIORITY vs DEFAULT PRIORITY. This setting determines which settings take place during the session- the pack's or config's.
* Greyed out child settings when parent settings are turned OFF.
* Several bug fixes including save issues.



###### \---WHAT IS NEW IN v5---

* Renamed "Allow buttonless popups" to "Force buttonless popups". The underlying Edgeware setting is unchanged.
* Removed the non-functional Edgeware Appearance control from the Start page. Manager Appearance remains available and only changes the configuration manager.
* Improved the light manager themes (Original and Bimbo) so the main window, navigation, fields, scrollbars, and comboboxes use the selected light palette instead of leaving dark controls behind.
* Added a Change Panic Wallpaper button directly under Wallpaper. The selected image is converted to data\\panic\_wallpaper.png so Edgeware uses it for Panic. Animated source images use their first frame. A Restore Default button is also included.
* Added small group headers and extra spacing to Popup Details, Modes, and Corruption to make related settings easier to scan.
* The popup-check delay is explicitly labeled in milliseconds.
* Added/clarified Subliminals Chance and Notification Chance in the popup settings.
* New/default settings requested for the prettier manager are now migrated automatically when an existing value is still equal to Edgeware's original default. User-customized values are preserved.
* Default ON settings: Show Startup Screen, Show Captions, Change Wallpaper, Enable Corruption, Cycle Wallpaper with Corruption, Cycle Themes with Corruption, and Allow Full Corruption Permissions.
* Default chances: Image 100%, Video 25%, Audio 100%, Prompt 0%, Website 0%, Subliminals 100%, Notification 100%.
* Pack config.json files can override those seven chance defaults when the selected value is still at the manager/default value. Other pack settings are not automatically imported.
* Corrected the two corruption cycle toggles to account for Edgeware's internal inverted config values, so their ON/OFF display matches actual Edgeware behavior.
* Slider controls have a stronger border, visible trough, and outlined slider handle.
* The v4 WebP-to-GIF progress window and shared-palette conversion remain included.
