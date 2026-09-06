Edgeware++ Pretty Configuration Manager v5

INSTALL
1. Open your EdgewarePlusPlus-21\edgeware folder.
2. Back up your existing config.pyw (for example: config_original.pyw).
3. Replace config.pyw with the config.pyw in this ZIP.
4. Do not replace Edgeware's other source files manually.
5. Run config.pyw normally.

WHAT IS NEW IN v5
- Renamed "Allow buttonless popups" to "Force buttonless popups". The underlying Edgeware setting is unchanged.
- Removed the non-functional Edgeware Appearance control from the Start page. Manager Appearance remains available and only changes the configuration manager.
- Improved the light manager themes (Original and Bimbo) so the main window, navigation, fields, scrollbars, and comboboxes use the selected light palette instead of leaving dark controls behind.
- Added a Change Panic Wallpaper button directly under Wallpaper. The selected image is converted to data\panic_wallpaper.png so Edgeware uses it for Panic. Animated source images use their first frame. A Restore Default button is also included.
- Added small group headers and extra spacing to Popup Details, Modes, and Corruption to make related settings easier to scan.
- The popup-check delay is explicitly labeled in milliseconds.
- Added/clarified Subliminals Chance and Notification Chance in the popup settings.
- New/default settings requested for the prettier manager are now migrated automatically when an existing value is still equal to Edgeware's original default. User-customized values are preserved.
- Default ON settings: Show Startup Screen, Show Captions, Change Wallpaper, Enable Corruption, Cycle Wallpaper with Corruption, Cycle Themes with Corruption, and Allow Full Corruption Permissions.
- Default chances: Image 100%, Video 25%, Audio 100%, Prompt 0%, Website 0%, Subliminals 100%, Notification 100%.
- Pack config.json files can override those seven chance defaults when the selected value is still at the manager/default value. Other pack settings are not automatically imported.
- Corrected the two corruption cycle toggles to account for Edgeware's internal inverted config values, so their ON/OFF display matches actual Edgeware behavior.
- Slider controls have a stronger border, visible trough, and outlined slider handle.
- The v4 WebP-to-GIF progress window and shared-palette conversion remain included.

PANIC WALLPAPER
The manager writes the selected panic wallpaper to data\panic_wallpaper.png, which matches Edgeware's CustomAssets panic-wallpaper path. A backup named panic_wallpaper.before_pretty_v5.bak is made before replacing an existing custom wallpaper.

GIF QUALITY
GIF is inherently limited to 256 colors and will not be as faithful as WebP. The included converter uses a shared animation palette to reduce frame-to-frame color flicker and performs conversion in the background with progress and cancellation.

EDGEWARE THEME BACKGROUND
The Troubleshooting tab still includes the separate "Fix Edgeware theme background" compatibility tool from v4. It patches src\features\popup.py only when the installed file matches the expected layout and keeps a .before_pretty_v5.bak backup. Restart Edgeware after applying it. This is separate from Manager Appearance.

SAFETY
The WebP converter changes the selected pack permanently and deletes each WebP only after a successful GIF is written.
The Panic Wallpaper tool changes data\panic_wallpaper.png and keeps a backup before replacement.
