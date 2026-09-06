import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import zipfile
import threading
from queue import Queue, Empty
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP = "Edgeware++ Configuration"
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CONFIG = DATA / "config.json"
DEFAULT = HERE / "assets" / "default_config.json"
PACKS = DATA / "packs"
MAIN = HERE / "src" / "main_edgeware.py"

# The manager has its own visual theme preference so it can stay pretty without
# changing Edgeware's actual theme setting. The Edgeware theme selector still
# writes themeType for the running program.
MANAGER_THEMES = ["Crimson/Violet", "Original", "Dark", "The One", "Ransom", "Goth", "Bimbo"]
EDGEWARE_THEMES = ["Original", "Dark", "The One", "Ransom", "Goth", "Bimbo"]

PRETTY_DEFAULTS = {
    "showLoadingFlair": 1,
    "showCaptions": 1,
    "rotateWallpaper": 1,
    "corruptionMode": 1,
    # Edgeware internally inverts these two settings: 0 means enabled.
    "corruptionWallpaperCycle": 0,
    "corruptionThemeCycle": 0,
    "corruptionFullPerm": 1,
    "popupMod": 100,
    "vidMod": 25,
    "audioMod": 100,
    "promptMod": 0,
    "webMod": 0,
    "subliminalsChance": 100,
    "notificationChance": 100,
}
PACK_CHANCE_KEYS = {"popupMod", "vidMod", "audioMod", "promptMod", "webMod", "subliminalsChance", "notificationChance"}
INVERTED_BOOL_KEYS = {"corruptionWallpaperCycle", "corruptionThemeCycle"}

BASE = {
    "bg": "#100C16", "panel": "#17111F", "panel2": "#1E1628", "panel3": "#261A31",
    "border": "#382544", "accent": "#C51F4A", "accent2": "#7B3FE4", "accent_dark": "#8E1637",
    "white": "#F8F5FA", "muted": "#B9AFBF", "dim": "#817588", "danger": "#FF667F",
    "entry": "#0D0912", "trough": "#2B1D35",
}
THEME_PALETTES = {
    "Crimson/Violet": BASE,
    "Original": {**BASE, "bg":"#ECE9EE", "panel":"#F5F3F6", "panel2":"#FFFFFF", "panel3":"#E4DFE8", "border":"#CBC4D0", "accent":"#9E1D3E", "accent2":"#6630B7", "accent_dark":"#7E1732", "white":"#201A24", "muted":"#625A67", "dim":"#817787", "entry":"#FFFFFF", "trough":"#C9C2CC"},
    "Dark": {**BASE, "bg":"#1B1E24", "panel":"#22262E", "panel2":"#2A2F38", "panel3":"#343A45", "border":"#414854", "accent":"#C51F4A", "accent2":"#7B3FE4", "accent_dark":"#8E1637", "white":"#F5F5F7", "muted":"#B9BDC5", "dim":"#858B96", "entry":"#171A20", "trough":"#343A45"},
    "The One": {**BASE, "bg":"#101812", "panel":"#172119", "panel2":"#1E2B21", "panel3":"#293A2D", "border":"#395340", "accent":"#C51F4A", "accent2":"#4D9B68", "accent_dark":"#8E1637", "white":"#F3F8F4", "muted":"#B7C5BA", "dim":"#7F9183", "entry":"#0D130E", "trough":"#304537"},
    "Ransom": {**BASE, "bg":"#180D0D", "panel":"#251111", "panel2":"#321717", "panel3":"#452020", "border":"#663333", "accent":"#E33A3A", "accent2":"#C98530", "accent_dark":"#9E2222", "white":"#FFF6F6", "muted":"#D3B6B6", "dim":"#967878", "entry":"#100707", "trough":"#4C2525"},
    "Goth": {**BASE, "bg":"#110D16", "panel":"#1C1622", "panel2":"#261D2E", "panel3":"#34253F", "border":"#513B60", "accent":"#C51F4A", "accent2":"#A55BD0", "accent_dark":"#8E1637", "white":"#F7F0FA", "muted":"#C2B6C8", "dim":"#8E7D98", "entry":"#0C0910", "trough":"#3A2945"},
    "Bimbo": {**BASE, "bg":"#FFF0F4", "panel":"#FFE0E8", "panel2":"#FFF7F9", "panel3":"#F5C5D3", "border":"#D99BAD", "accent":"#B43A72", "accent2":"#9A55B8", "accent_dark":"#8D2858", "white":"#321724", "muted":"#70485A", "dim":"#946F7E", "entry":"#FFFFFF", "trough":"#E8B4C5"},
}

# (key, label, explanation, type, choices)
SECTIONS = {
    "Start": [
        ("packPath", "Pack to run", "Choose the pack folder from data\\packs. This is the pack Edgeware will use when it starts.", "pack", None),
        ("showLoadingFlair", "Show startup screen", "Show Edgeware's startup image when it begins.", "bool", None),
        ("desktopIcons", "Create Edgeware desktop shortcuts", "When Edgeware starts, create shortcuts for Edgeware, its configuration window, and Panic. This does not hide your normal Windows icons.", "bool", None),
        ("safeMode", "Safe mode", "Keeps some of Edgeware's more disruptive features turned off.", "bool", None),
        ("globalPanicButton", "Global panic key", "The emergency key that should work even when another program has focus. Click Set Key, then press the key you want.", "global_key", None),
        ("runOnSaveQuit", "Run when Save and Exit is used", "If ON, saving and closing this window also starts Edgeware. Save, Exit, and Run always starts it.", "bool", None),
    ],
    "Popups": [
        ("delay", "Time between popup checks (ms)", "How long Edgeware waits before trying another popup. Lower numbers mean more activity.", "ms", None),
        ("popupMod", "Image popup chance", "Chance from 0 to 100 that a popup attempt becomes an image.", "pct", None),
        ("vidMod", "Video popup chance", "Chance from 0 to 100 that a popup attempt becomes a video.", "pct", None),
        ("audioMod", "Audio chance", "Chance from 0 to 100 that Edgeware plays an audio clip.", "pct", None),
        ("promptMod", "Prompt chance", "Chance from 0 to 100 that Edgeware asks you to type something.", "pct", None),
        ("webMod", "Website chance", "Chance from 0 to 100 that Edgeware opens a web page.", "pct", None),
        ("maxVideos", "Maximum videos", "Maximum number of videos that can play at once.", "int", None),
        ("maxAudio", "Maximum sounds", "Maximum number of audio clips that can play at once.", "int", None),
        ("videoVolume", "Video volume", "Video loudness from 0 to 100.", "pct", None),
        ("audioVolume", "Audio volume", "Audio loudness from 0 to 100.", "pct", None),
        ("webPopup", "Open a website after closing a popup", "Allows Edgeware to open configured websites after a popup closes.", "bool", None),
        ("singleMode", "Only one popup at a time", "Prevents several normal popups from appearing at once.", "bool", None),
    ],
    "Popup Details": [
        ("showCaptions", "Show captions", "Lets image popups display their captions.", "bool", None),
        ("denialChance", "Popup denial chance", "Chance that a popup refuses to close normally.", "pct", None),
        ("buttonless", "Force buttonless popups", "Removes the normal close button from popups. Clicking the popup itself closes it instead.", "bool", None),
        ("multiClick", "Require multiple clicks", "Some popups may require more than one click before they close.", "bool", None),
        ("lkScaling", "Popup size", "General popup size. 100 is normal size.", "pct", None),
        ("timeoutPopups", "Automatically close popups", "Lets popups close themselves after a timer.", "bool", None),
        ("popupTimeout", "Automatic close time", "How many seconds a popup stays before closing itself.", "sec", None),
        ("movingChance", "Moving popup chance", "Chance from 0 to 100 that a popup moves around the screen.", "pct", None),
        ("movingSpeed", "Moving popup speed", "How quickly moving popups travel.", "int", None),
        ("clickthroughPopups", "Allow clicks through popups", "Makes popup windows ignore mouse clicks.", "bool", None),
        ("fadeInDuration", "Fade in time", "How long popups take to appear, in milliseconds.", "ms", None),
        ("fadeOutDuration", "Fade out time", "How long popups take to disappear, in milliseconds.", "ms", None),
        ("capPopChance", "Subliminal caption chance", "Chance from 0 to 100 that brief caption messages appear.", "pct", None),
        ("capPopTimer", "Subliminal message time", "How long a subliminal caption stays visible.", "sec", None),
        ("capPopOpacity", "Subliminal caption opacity", "How visible subliminal captions are, from 0 to 100.", "pct", None),
        ("subliminalsChance", "Subliminals chance", "Chance from 0 to 100 that a visual overlay is put over an image.", "pct", None),
        ("subliminalsAlpha", "Image overlay opacity", "How strong the visual overlay is, from 0 to 100.", "pct", None),
        ("notificationChance", "Notification chance", "Chance from 0 to 100 that Edgeware creates a system-style notification.", "pct", None),
        ("notificationImageChance", "Notification image chance", "Chance from 0 to 100 that a notification includes an image.", "pct", None),
        ("promptMistakes", "Prompt mistakes allowed", "How many wrong answers can be entered before a prompt changes behavior.", "int", None),
    ],
    "Wallpaper": [
        ("rotateWallpaper", "Change wallpaper", "Allow Edgeware to rotate or change the desktop wallpaper.", "bool", None),
        ("wallpaperTimer", "Wallpaper change time", "How many seconds Edgeware waits before changing wallpaper.", "sec", None),
        ("wallpaperVariance", "Wallpaper timing variation", "Adds this many seconds of randomness to the wallpaper timer.", "sec", None),
    ],
    "Internet": [
        ("downloadEnabled", "Allow online image downloads", "Allows Edgeware to download images from its configured online source.", "bool", None),
        ("tagList", "Online image tags", "Words used when choosing online images.", "text", None),
        ("toggleInternet", "Disable internet features", "Turns off Edgeware features that need the internet.", "bool", None),
    ],
    "Modes": [
        ("lkToggle", "Low-key mode", "Keeps activity concentrated in one corner of the screen.", "bool", None),
        ("lkCorner", "Low-key corner", "Choose the corner used by low-key mode.", "corner", ["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"]),
        ("mitosisMode", "Mitosis mode", "Allows popups to create additional popup activity. High settings can load the computer heavily.", "bool", None),
        ("mitosisStrength", "Mitosis strength", "Controls how strongly mitosis multiplies activity.", "int", None),
        ("hibernateMode", "Hibernate mode", "Lets Edgeware pause and wake up according to its hibernate rules.", "bool", None),
        ("hibernateType", "Hibernate style", "Choose a behavior preset. Selecting one updates the numbers below; you can still fine-tune them afterward.", "hibernate", ["Original", "Spaced", "Glitch", "Ramp", "Pump-Scare", "Chaos"]),
        ("hibernateMin", "Shortest hibernate delay", "Minimum seconds before a hibernate wake-up.", "sec", None),
        ("hibernateMax", "Longest hibernate delay", "Maximum seconds before a hibernate wake-up.", "sec", None),
        ("wakeupActivity", "Wake-up activity", "How many popup attempts can happen during wake-up activity.", "int", None),
        ("hibernateLength", "Wake-up activity length", "How many seconds the wake-up activity lasts.", "sec", None),
        ("fixWallpaper", "Restore wallpaper after hibernate", "Try to restore the wallpaper when hibernate mode ends.", "bool", None),
    ],
    "Corruption": [
        ("corruptionMode", "Enable corruption", "Gradually increases Edgeware activity over time.", "bool", None),
        ("corruptionTrigger", "How corruption advances", "Choose what causes corruption to move to the next level.", "choice", ["Timed", "Popup", "Launch", "Script"]),
        ("corruptionTime", "Time between levels", "For timed corruption, how many seconds each level lasts.", "sec", None),
        ("corruptionFadeType", "Level transition", "Choose whether corruption changes gradually or suddenly.", "choice", ["Normal", "Abrupt"]),
        ("corruptionPopups", "Popups needed", "For popup-triggered corruption, how many popups are needed.", "int", None),
        ("corruptionLaunches", "Launches needed", "For launch-triggered corruption, how many launches are needed.", "int", None),
        ("corruptionWallpaperCycle", "Cycle wallpapers with corruption", "Allows corruption to change wallpapers as it progresses.", "bool", None),
        ("corruptionThemeCycle", "Cycle themes with corruption", "Allows corruption to change themes as it progresses.", "bool", None),
        ("corruptionPurityMode", "Corruption purity mode", "Restricts which moods can be used as corruption changes.", "bool", None),
        ("corruptionFullPerm", "Allow full corruption permissions", "Allows corruption to use settings that are normally protected.", "bool", None),
    ],
    "Scheduling": [
        ("schedule", "Use a schedule", "Automatically start Edgeware according to a schedule.", "bool", None),
        ("timeType", "Schedule unit", "Choose minutes, hours, or days.", "choice", ["Minutes", "Hours", "Days"]),
        ("scheduleTime", "Start after", "How long to wait before starting Edgeware.", "int", None),
        ("varianceTime", "Random extra time", "Adds a random amount of extra waiting time.", "int", None),
        ("varianceType", "Random time unit", "The unit used for the random extra time.", "choice", ["Minutes", "Hours", "Days"]),
        ("repeatSchedule", "Repeat the schedule", "Starts Edgeware again after the schedule finishes.", "bool", None),
        ("repeatType", "Repeat unit", "Choose minutes, hours, or days.", "choice", ["Minutes", "Hours", "Days"]),
        ("repeatTime", "Repeat after", "How long to wait before the next scheduled start.", "int", None),
    ],
    "Computer Changes": [
        ("fill", "Fill a folder with images", "Allows Edgeware to create many image files. Leave this OFF unless you specifically want it.", "bool", "danger"),
        ("fill_delay", "Delay between file fills", "Controls how quickly files are created when file filling is enabled.", "int", None),
        ("drivePath", "Folder used for computer changes", "The starting folder for file-changing features.", "text", None),
        ("avoidList", "Protected folders", "One protected folder per line. These are converted to Edgeware's internal format when saved.", "multiline", None),
        ("replace", "Replace images", "Allows Edgeware to replace existing image files. This can overwrite files.", "bool", "danger"),
        ("replaceThresh", "Replacement threshold", "Controls how much activity is needed before image replacement occurs.", "int", None),
        ("start_on_logon", "Run when Windows starts", "Starts Edgeware automatically when you log in to Windows.", "bool", "danger"),
        ("timerMode", "Panic lockout", "Can prevent the emergency stop from being used until a set time.", "bool", "danger"),
        ("timerSetupTime", "Panic lockout time", "How long the panic lockout lasts, in minutes.", "min", None),
        ("safeword", "Panic lockout password", "The word needed to end a panic lockout.", "text", None),
        ("panicDisabled", "Disable emergency stop", "Removes the easy emergency stop. Do not enable unless you understand the consequences.", "bool", "danger"),
    ],
    "Troubleshooting": [
        ("lanczos", "Use Lanczos image resizing", "Recommended ON for normal image resizing. Note: animated WebP files use the video player, so this switch cannot fix an animated-WebP decoding problem by itself.", "bool", None),
        ("videoHardwareAcceleration", "Use video hardware acceleration", "Lets your graphics hardware help play videos.", "bool", None),
        ("mpvSubprocess", "Use a separate video process", "Runs the video player separately so a video problem is less likely to take down Edgeware.", "bool", None),
        ("toggleHibSkip", "Allow hibernate skip", "Adds the hibernate skip behavior.", "bool", None),
        ("toggleMoodSet", "Allow mood set toggle", "Enables the mood-set troubleshooting switch.", "bool", None),
        ("messageOff", "Hide messages", "Suppresses some Edgeware messages.", "bool", None),
    ],
}

GROUPS = {
    "Popup Details": [
        (0, "Popup behavior", "Rules that affect how individual popups close, move, and respond to clicks."),
        (12, "Subliminals and notifications", "Caption flashes, visual overlays, and system-style notifications."),
    ],
    "Modes": [
        (0, "Low-Key Mode", "Keep popup activity concentrated in a chosen corner."),
        (2, "Mitosis", "Allow popup activity to multiply itself."),
        (4, "Hibernate Mode", "Pause Edgeware and wake it according to a selected behavior."),
    ],
    "Corruption": [
        (0, "Corruption", "Core corruption behavior and how it advances."),
        (6, "Corruption visuals", "Wallpaper and theme changes as corruption progresses."),
        (8, "Advanced corruption", "Additional restrictions and full-permission behavior."),
    ],
}

DANGER_TEXT = {
    "fill": "This can create a large number of files on your computer.",
    "replace": "This can overwrite or replace existing image files.",
    "start_on_logon": "This makes Edgeware start automatically with Windows.",
    "timerMode": "This can temporarily prevent the emergency stop from working normally.",
    "panicDisabled": "This removes an easy way to stop Edgeware.",
}
DESCRIPTIONS = {
    "Start":"The few things you should decide before running Edgeware.",
    "Popups":"How often Edgeware throws different kinds of things onto the screen.",
    "Popup Details":"Smaller rules that change what individual popups do.",
    "Wallpaper":"How Edgeware handles your desktop wallpaper.",
    "Internet":"Features that need an internet connection.",
    "Modes":"Optional behavior that changes how Edgeware acts.",
    "Corruption":"Make Edgeware become more intense as time passes.",
    "Scheduling":"Make Edgeware start automatically later or repeatedly.",
    "Computer Changes":"Settings that can create, replace, or change files. Read these carefully.",
    "Troubleshooting":"Compatibility tools, a WebP conversion utility, and a small Edgeware theme compatibility fix.",
}

PERCENT_KEYS = {item[0] for section in SECTIONS.values() for item in section if item[3] == "pct"}
HIBERNATE_PRESETS = {
    "Original": {"hibernateMin":240, "hibernateMax":300, "wakeupActivity":20, "hibernateLength":15},
    "Spaced": {"hibernateMin":300, "hibernateMax":600, "wakeupActivity":20, "hibernateLength":20},
    "Glitch": {"hibernateMin":120, "hibernateMax":300, "wakeupActivity":20, "hibernateLength":15},
    "Ramp": {"hibernateMin":180, "hibernateMax":360, "wakeupActivity":20, "hibernateLength":30},
    "Pump-Scare": {"hibernateMin":300, "hibernateMax":600, "wakeupActivity":1, "hibernateLength":1},
    "Chaos": {"hibernateMin":60, "hibernateMax":600, "wakeupActivity":20, "hibernateLength":15},
}


def load_json(path, fallback=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {} if fallback is None else fallback


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def truth(v):
    try:
        return bool(int(v))
    except Exception:
        return bool(v)


def safe_backup():
    if CONFIG.exists():
        stamp = "config.json.before_pretty_v5.bak"
        target = DATA / stamp
        if not target.exists():
            shutil.copy2(CONFIG, target)


def run_edgeware(pack_value=None):
    if not MAIN.exists():
        raise FileNotFoundError(f"Could not find Edgeware's main program:\n{MAIN}")
    return subprocess.Popen([sys.executable, str(MAIN)], cwd=str(HERE))


def key_to_display(value):
    return value or "Not set"


def pack_candidates_from_zip(zpath):
    with tempfile.TemporaryDirectory(prefix="edgeware_pack_") as td:
        root = Path(td)
        with zipfile.ZipFile(zpath) as z:
            for info in z.infolist():
                name = Path(info.filename)
                if name.is_absolute() or ".." in name.parts:
                    raise ValueError("The ZIP contains an unsafe file path and was not imported.")
            z.extractall(root)
        candidates = []
        for p in [root, *[x for x in root.rglob("*") if x.is_dir()]]:
            if (p / "index.json").is_file() or (p / "info.json").is_file() or (p / "img").is_dir():
                candidates.append(p)
        # Prefer the shallowest candidate, unless it is a resource folder inside a full Edgeware install.
        candidates.sort(key=lambda p: (len(p.relative_to(root).parts), str(p).lower()))
        candidate = candidates[0] if candidates else None
        if candidate is None:
            raise ValueError("I could not find a pack inside that ZIP. A pack normally contains index.json, info.json, or an img folder.")
        return root, candidate


def import_pack(parent):
    zpath = filedialog.askopenfilename(parent=parent, title="Import Edgeware Pack", filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")])
    if not zpath:
        return None
    try:
        with tempfile.TemporaryDirectory(prefix="edgeware_import_") as td:
            root = Path(td)
            with zipfile.ZipFile(zpath) as z:
                for info in z.infolist():
                    name = Path(info.filename)
                    if name.is_absolute() or ".." in name.parts:
                        raise ValueError("The ZIP contains an unsafe file path and was not imported.")
                z.extractall(root)
            candidates = []
            for p in [root, *[x for x in root.rglob("*") if x.is_dir()]]:
                if (p / "index.json").is_file() or (p / "info.json").is_file() or (p / "img").is_dir():
                    candidates.append(p)
            candidates.sort(key=lambda p: (len(p.relative_to(root).parts), str(p).lower()))
            candidate = candidates[0] if candidates else None
            if candidate is None:
                raise ValueError("I could not find a pack inside that ZIP.")
            zip_stem = Path(zpath).stem
            name = candidate.name if candidate != root else zip_stem
            if name.lower() == "resource" and candidate.parent != root:
                name = zip_stem
            dest = PACKS / name
            if dest.exists():
                base = name
                n = 2
                while dest.exists():
                    dest = PACKS / f"{base} ({n})"
                    n += 1
            PACKS.mkdir(parents=True, exist_ok=True)
            shutil.copytree(candidate, dest)
            return dest.name
    except zipfile.BadZipFile:
        messagebox.showerror(APP, "That file is not a valid ZIP archive.")
    except Exception as e:
        messagebox.showerror(APP, f"The pack could not be imported.\n\n{e}")
    return None


def _make_gif_palette(im, sample_count=12):
    """Build one palette for an animated image so colors do not jump every frame."""
    from PIL import Image
    n = getattr(im, "n_frames", 1)
    if n <= 1:
        return None
    picks = sorted(set(int(i * (n - 1) / max(1, sample_count - 1)) for i in range(min(n, sample_count))))
    thumbs = []
    for i in picks:
        im.seek(i)
        frame = im.convert("RGB")
        frame.thumbnail((320, 320), Image.Resampling.LANCZOS)
        thumbs.append(frame.copy())
    if not thumbs:
        return None
    cols = min(4, len(thumbs))
    rows = (len(thumbs) + cols - 1) // cols
    cell_w = max(x.width for x in thumbs)
    cell_h = max(x.height for x in thumbs)
    mosaic = Image.new("RGB", (cell_w * cols, cell_h * rows), "black")
    for idx, frame in enumerate(thumbs):
        mosaic.paste(frame, ((idx % cols) * cell_w, (idx // cols) * cell_h))
    # Reserve one palette entry for transparency when needed.
    return mosaic.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)


def convert_webp_to_gif(pack_dir, progress=None, cancel_event=None):
    if not pack_dir or not pack_dir.is_dir():
        raise ValueError("Select a pack first.")
    try:
        from PIL import Image
    except Exception as e:
        raise RuntimeError("Pillow is not available in this Python environment.") from e
    files = list(pack_dir.rglob("*.webp")) + list(pack_dir.rglob("*.WEBP"))
    files = sorted(set(files), key=lambda p: str(p).lower())
    if not files:
        return 0
    converted = 0
    failures = []
    total = len(files)
    for file_index, src in enumerate(files, 1):
        if cancel_event and cancel_event.is_set():
            break
        dst = src.with_suffix(".gif")
        try:
            with Image.open(src) as im:
                n = getattr(im, "n_frames", 1)
                palette = _make_gif_palette(im) if n > 1 else None
                frames = []
                durations = []
                for i in range(n):
                    if cancel_event and cancel_event.is_set():
                        raise InterruptedError("Conversion cancelled.")
                    im.seek(i)
                    frame = im.convert("RGBA")
                    alpha = frame.getchannel("A")
                    rgb = Image.new("RGB", frame.size, "black")
                    rgb.paste(frame, mask=alpha)
                    if palette is not None:
                        indexed = rgb.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG)
                    else:
                        indexed = rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
                    frames.append(indexed)
                    durations.append(max(10, int(im.info.get("duration", 100) or 100)))
                    if progress:
                        progress({"stage":"frame", "file":file_index, "total":total, "name":src.name, "frame":i+1, "frames":n})
                if len(frames) > 1:
                    tmp = dst.with_suffix(".gif.tmp")
                    frames[0].save(tmp, format="GIF", save_all=True, append_images=frames[1:], duration=durations, loop=0, disposal=2, optimize=True)
                    os.replace(tmp, dst)
                else:
                    tmp = dst.with_suffix(".gif.tmp")
                    frames[0].save(tmp, format="GIF", optimize=True)
                    os.replace(tmp, dst)
            src.unlink()
            converted += 1
            if progress:
                progress({"stage":"file", "file":file_index, "total":total, "name":src.name, "frame":n, "frames":n, "converted":converted})
        except InterruptedError:
            try:
                if dst.with_suffix(".gif.tmp").exists():
                    dst.with_suffix(".gif.tmp").unlink()
            except OSError:
                pass
            break
        except Exception as e:
            try:
                if dst.with_suffix(".gif.tmp").exists():
                    dst.with_suffix(".gif.tmp").unlink()
            except OSError:
                pass
            failures.append(f"{src.name}: {e}")
            if progress:
                progress({"stage":"error", "file":file_index, "total":total, "name":src.name, "error":str(e)})
    if failures:
        raise RuntimeError(f"Converted {converted} file(s), but {len(failures)} failed:\n\n" + "\n".join(failures[:8]))
    return converted


def apply_edgeware_theme_background_fix():
    popup = HERE / "src" / "features" / "popup.py"
    if not popup.is_file():
        raise FileNotFoundError(f"Could not find Edgeware's popup.py:\n{popup}")
    text = popup.read_text(encoding="utf-8")
    if "super().__init__(bg=self.theme.bg)" in text:
        return False, "The Edgeware theme background fix is already applied."
    old = '        super().__init__(bg="black")\n\n        self.root = root\n'
    new = '        self.theme = settings.theme\n        super().__init__(bg=self.theme.bg)\n\n        self.root = root\n'
    old2 = '        self.theme = settings.theme\n        self.denial = roll(self.settings.denial_chance)\n'
    new2 = '        self.denial = roll(self.settings.denial_chance)\n'
    if old not in text or old2 not in text:
        raise RuntimeError("The installed popup.py does not match the expected Edgeware++ layout. No changes were made.")
    backup = popup.with_suffix(popup.suffix + ".before_pretty_v5.bak")
    if not backup.exists():
        shutil.copy2(popup, backup)
    popup.write_text(text.replace(old, new, 1).replace(old2, new2, 1), encoding="utf-8")
    return True, "Applied the Edgeware theme background fix. Restart Edgeware for the change to take effect."


class App:
    def __init__(self):
        DATA.mkdir(parents=True, exist_ok=True)
        config_was_missing = not CONFIG.exists()
        if config_was_missing:
            if not DEFAULT.exists():
                raise FileNotFoundError(f"Could not find Edgeware's default config:\n{DEFAULT}")
            shutil.copy2(DEFAULT, CONFIG)
        self.original_defaults = load_json(DEFAULT, {})
        self.defaults = dict(self.original_defaults)
        self.defaults.update(PRETTY_DEFAULTS)
        self.cfg = load_json(CONFIG, dict(self.defaults))
        for k, v in self.defaults.items():
            self.cfg.setdefault(k, v)
        # Migrate untouched old-default values to the prettier manager defaults,
        # while leaving settings the user already customized alone.
        for key, desired in PRETTY_DEFAULTS.items():
            if key in self.original_defaults and self.cfg.get(key) == self.original_defaults.get(key):
                self.cfg[key] = desired
        if config_was_missing:
            self.cfg.update(PRETTY_DEFAULTS)
        self.cfg.setdefault("lanczos", 1)
        self.cfg.setdefault("_prettyConfigTheme", "Crimson/Violet")
        self.root = tk.Tk()
        self.root.title(APP)
        self.root.geometry("1060x700")
        self.root.minsize(900, 600)
        self.vars = {}
        self.current_section = "Start"
        self.pack_map = {}
        self.theme_name = self.cfg.get("_prettyConfigTheme", "Crimson/Violet")
        if self.theme_name not in MANAGER_THEMES:
            self.theme_name = "Crimson/Violet"
        self.palette = THEME_PALETTES[self.theme_name]
        self.build_shell()
        self.apply_manager_theme()
        self.refresh_packs()
        self.apply_pack_chance_overrides(self.cfg.get("packPath"), only_if_default=True)
        self.render(self.current_section)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def build_shell(self):
        self.root.configure(bg=self.palette["bg"])
        self.top = tk.Frame(self.root, bg=self.palette["bg"])
        self.top.pack(fill="x", padx=18, pady=(12, 6))
        self.title = tk.Label(self.top, text="EDGEWARE++", bg=self.palette["bg"], fg=self.palette["white"], font=("Segoe UI", 20, "bold"))
        self.title.pack(side="left")
        self.subtitle = tk.Label(self.top, text="CONFIGURATION MANAGER", bg=self.palette["bg"], fg=self.palette["accent2"], font=("Segoe UI", 8, "bold"))
        self.subtitle.pack(side="left", padx=(10,0), pady=(7,0))
        self.status_label = tk.Label(self.top, text="READY", bg=self.palette["bg"], fg=self.palette["muted"], font=("Segoe UI", 8, "bold"))
        self.status_label.pack(side="right", pady=(5,0))

        self.body = tk.Frame(self.root, bg=self.palette["bg"])
        self.body.pack(fill="both", expand=True, padx=14, pady=2)
        self.nav = tk.Frame(self.body, width=178, bg=self.palette["panel"], highlightthickness=1, highlightbackground=self.palette["border"])
        self.nav.pack(side="left", fill="y", padx=(0,8)); self.nav.pack_propagate(False)
        self.nav_title=tk.Label(self.nav, text="SETTINGS", bg=self.palette["panel"], fg=self.palette["dim"], font=("Segoe UI",7,"bold"))
        self.nav_title.pack(anchor="w", padx=12, pady=(10,4))
        self.nav_buttons = {}
        for section in SECTIONS:
            b = tk.Button(self.nav, text=section, anchor="w", relief="flat", bd=0, padx=11, pady=5, cursor="hand2", font=("Segoe UI",8,"bold"), command=lambda s=section:self.render(s))
            b.pack(fill="x", padx=5, pady=1)
            self.nav_buttons[section] = b
        self.nav_divider=tk.Frame(self.nav, bg=self.palette["border"], height=1)
        self.nav_divider.pack(fill="x", padx=9, pady=7)
        self.nav_action_buttons=[]
        for text,cmd,bold in [("Import Pack",self.import_pack_ui,True),("Reset to defaults",self.reset_defaults,False),("Open Edgeware folder",self.open_root,False)]:
            b=tk.Button(self.nav, text=text, anchor="w", relief="flat", bd=0, padx=11, pady=5, cursor="hand2", font=("Segoe UI",8,"bold" if bold else "normal"), command=cmd)
            b.pack(fill="x", padx=5); self.nav_action_buttons.append(b)

        self.content = tk.Frame(self.body, bg=self.palette["panel"], highlightthickness=1, highlightbackground=self.palette["border"])
        self.content.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(self.content, bg=self.palette["panel"], highlightthickness=0)
        self.scroll = ttk.Scrollbar(self.content, orient="vertical", command=self.canvas.yview, style="Pretty.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True); self.scroll.pack(side="right", fill="y")
        self.page = tk.Frame(self.canvas, bg=self.palette["panel"])
        self.win = self.canvas.create_window((0,0), window=self.page, anchor="nw")
        self.page.bind("<Configure>", lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e:self.canvas.itemconfigure(self.win,width=e.width))
        self.canvas.bind_all("<MouseWheel>", self.mousewheel)

        self.bottom = tk.Frame(self.root, bg=self.palette["bg"])
        self.bottom.pack(fill="x", padx=18, pady=(4,9))
        self.status = tk.StringVar(value="No changes saved.")
        self.bottom_status_label=tk.Label(self.bottom, textvariable=self.status, bg=self.palette["bg"], fg=self.palette["dim"], font=("Segoe UI",7))
        self.bottom_status_label.pack(side="left")
        self.bottom_buttons=[]
        for text,cmd,primary,sidepad in [("Save",self.save,False,(6,0)),("Save, Exit, and Run",self.save_exit_run,True,(6,0)),("Save and Exit",self.save_exit,False,(0,0))]:
            b=self.make_button(self.bottom,text,cmd,primary=primary); b.pack(side="right", padx=sidepad); self.bottom_buttons.append(b)

    def make_button(self,parent,text,command,primary=False):
        return tk.Button(parent,text=text,command=command,relief="flat",bd=0,padx=11,pady=6,cursor="hand2",font=("Segoe UI",8,"bold"),bg=self.palette["accent"] if primary else self.palette["panel3"],fg=self.palette["white"],activebackground=self.palette["accent2"],activeforeground=self.palette["white"])

    def mousewheel(self,event):
        try:self.canvas.yview_scroll(int(-event.delta/120),"units")
        except Exception:pass

    def refresh_packs(self):
        self.pack_map={"Default pack":None}
        PACKS.mkdir(parents=True,exist_ok=True)
        for p in sorted(PACKS.iterdir(),key=lambda x:x.name.lower()):
            if p.is_dir(): self.pack_map[p.name]=p.name

    def render(self,section):
        self.current_section=section
        for w in self.page.winfo_children(): w.destroy()
        self.vars={}
        self.select_nav(section)
        self.refresh_packs()
        tk.Label(self.page,text=section.upper(),bg=self.palette["panel"],fg=self.palette["white"],font=("Segoe UI",15,"bold")).pack(anchor="w",padx=16,pady=(13,1))
        tk.Label(self.page,text=DESCRIPTIONS[section],bg=self.palette["panel"],fg=self.palette["muted"],font=("Segoe UI",8),wraplength=760,justify="left").pack(anchor="w",padx=16,pady=(0,8))
        groups = {index: (title, text) for index, title, text in GROUPS.get(section, [])}
        for index, (key,label,helptext,typ,choices) in enumerate(SECTIONS[section]):
            if index in groups:
                self.add_group_header(*groups[index])
            self.add_setting(key,label,helptext,typ,choices)
        if section == "Wallpaper":
            self.add_panic_wallpaper_preview()
        self.canvas.yview_moveto(0)

    def select_nav(self,active):
        for name,b in self.nav_buttons.items():
            b.configure(bg=self.palette["accent_dark"] if name==active else self.palette["panel"],fg=self.palette["white"] if name==active else self.palette["muted"],activebackground=self.palette["accent_dark"] if name==active else self.palette["panel3"])

    def raw_value(self,key,typ):
        v=self.cfg.get(key,0 if typ in ("bool","pct","int","ms","sec","min") else "")
        if typ=="bool":
            result = truth(v)
            return (not result) if key in INVERTED_BOOL_KEYS else result
        if typ=="pack": return "Default pack" if not v else str(v)
        if typ=="corner":
            names=["Top-Left","Top-Right","Bottom-Left","Bottom-Right"]
            try:return names[max(0,min(3,int(v)))]
            except:return "Top-Left"
        if typ=="multiline": return "\n".join(str(v).split(">")) if v else ""
        return str(v)

    def add_panic_wallpaper_preview(self):
        card=tk.Frame(self.page,bg=self.palette["panel3"],highlightthickness=1,highlightbackground=self.palette["border"])
        card.pack(fill="x",padx=14,pady=7)
        tk.Label(card,text="PANIC WALLPAPER",bg=self.palette["panel3"],fg=self.palette["white"],font=("Segoe UI",8,"bold")).pack(anchor="w",padx=10,pady=(7,1))
        tk.Label(card,text="This is the wallpaper Edgeware restores when Panic is activated.",bg=self.palette["panel3"],fg=self.palette["muted"],font=("Segoe UI",7),wraplength=650,justify="left").pack(anchor="w",padx=10)
        row=tk.Frame(card,bg=self.palette["panel3"]); row.pack(fill="x",padx=10,pady=7)
        image_path=DATA/"panic_wallpaper.png"
        if not image_path.is_file():
            image_path=HERE/"assets"/"default_panic_wallpaper.jpg"
        try:
            from PIL import Image, ImageTk
            if image_path.is_file():
                im=Image.open(image_path).convert("RGB")
                im.thumbnail((300,170), Image.Resampling.LANCZOS)
                self._panic_preview_image=ImageTk.PhotoImage(im)
                tk.Label(row,image=self._panic_preview_image,bg=self.palette["panel3"],highlightthickness=1,highlightbackground=self.palette["border"]).pack(side="left")
            else:
                tk.Label(row,text="No panic wallpaper file found.",bg=self.palette["panel3"],fg=self.palette["danger"],font=("Segoe UI",8,"bold")).pack(side="left")
        except Exception as e:
            tk.Label(row,text=f"Could not preview wallpaper: {e}",bg=self.palette["panel3"],fg=self.palette["danger"],font=("Segoe UI",7)).pack(side="left")
        info=tk.Frame(row,bg=self.palette["panel3"]); info.pack(side="left",padx=(10,0),anchor="n",fill="y")
        tk.Label(info,text=str(image_path),bg=self.palette["panel3"],fg=self.palette["dim"],font=("Segoe UI",7),wraplength=320,justify="left").pack(anchor="w")
        btnrow=tk.Frame(info,bg=self.palette["panel3"]); btnrow.pack(anchor="w",pady=(8,0))
        self.make_button(btnrow,"Change Panic Wallpaper",self.change_panic_wallpaper,primary=True).pack(side="left",padx=(0,5))
        self.make_button(btnrow,"Restore Default",self.restore_default_panic_wallpaper).pack(side="left")

    def change_panic_wallpaper(self):
        source=filedialog.askopenfilename(parent=self.root,title="Choose Panic Wallpaper",filetypes=[("Image files","*.png *.jpg *.jpeg *.bmp *.webp"),("All files","*.*")])
        if not source: return
        target=DATA/"panic_wallpaper.png"
        try:
            from PIL import Image
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():
                backup=DATA/"panic_wallpaper.before_pretty_v5.bak"
                if not backup.exists(): shutil.copy2(target,backup)
            with Image.open(source) as im:
                if getattr(im,"n_frames",1)>1: im.seek(0)
                frame=im.convert("RGB")
                tmp=target.with_suffix(".png.tmp")
                frame.save(tmp,"PNG")
                os.replace(tmp,target)
            self.status.set("Panic wallpaper changed. It will be used by Panic after Edgeware restarts.")
            self.render("Wallpaper")
        except Exception as e:
            try:
                tmp=target.with_suffix(".png.tmp")
                if tmp.exists(): tmp.unlink()
            except OSError: pass
            messagebox.showerror(APP,f"Could not change the panic wallpaper.\n\n{e}")

    def restore_default_panic_wallpaper(self):
        source=HERE/"assets"/"default_panic_wallpaper.jpg"
        target=DATA/"panic_wallpaper.png"
        if not source.is_file():
            messagebox.showerror(APP,f"Default panic wallpaper not found:\n{source}"); return
        if not messagebox.askyesno(APP,"Restore the default panic wallpaper? The current custom panic wallpaper will be replaced."): return
        try:
            from PIL import Image
            if target.exists():
                backup=DATA/"panic_wallpaper.before_pretty_v5.bak"
                if not backup.exists(): shutil.copy2(target,backup)
            with Image.open(source) as im:
                frame=im.convert("RGB")
                tmp=target.with_suffix(".png.tmp")
                frame.save(tmp,"PNG")
                os.replace(tmp,target)
            self.status.set("Default panic wallpaper restored.")
            self.render("Wallpaper")
        except Exception as e:
            messagebox.showerror(APP,f"Could not restore the default panic wallpaper.\n\n{e}")

    def add_group_header(self,title,text):
        wrap=tk.Frame(self.page,bg=self.palette["panel"])
        wrap.pack(fill="x",padx=14,pady=(9,2))
        tk.Frame(wrap,bg=self.palette["border"],height=1).pack(fill="x",pady=(0,6))
        tk.Label(wrap,text=title.upper(),bg=self.palette["panel"],fg=self.palette["accent2"],font=("Segoe UI",7,"bold")).pack(anchor="w",padx=3)
        tk.Label(wrap,text=text,bg=self.palette["panel"],fg=self.palette["dim"],font=("Segoe UI",7),wraplength=700,justify="left").pack(anchor="w",padx=3,pady=(1,3))

    def add_setting(self,key,label,helptext,typ,choices):
        card=tk.Frame(self.page,bg=self.palette["panel2"],highlightthickness=1,highlightbackground=self.palette["border"])
        card.pack(fill="x",padx=14,pady=3)
        left=tk.Frame(card,bg=self.palette["panel2"]); left.pack(side="left",fill="both",expand=True,padx=10,pady=7)
        tk.Label(left,text=label,bg=self.palette["panel2"],fg=self.palette["white"],font=("Segoe UI",8,"bold")).pack(anchor="w")
        tk.Label(left,text=helptext,bg=self.palette["panel2"],fg=self.palette["muted"],font=("Segoe UI",7),wraplength=560,justify="left").pack(anchor="w",pady=(1,0))
        if key in DANGER_TEXT:
            tk.Label(left,text="CAUTION: "+DANGER_TEXT[key],bg=self.palette["panel2"],fg=self.palette["danger"],font=("Segoe UI",7,"bold"),wraplength=560,justify="left").pack(anchor="w",pady=(2,0))
        right=tk.Frame(card,bg=self.palette["panel2"]); right.pack(side="right",padx=10,pady=7)
        if typ=="bool": self.add_bool(right,key)
        elif typ in ("choice","edge_theme","corner","hibernate"): self.add_combo(right,key,typ,choices)
        elif typ=="pack": self.add_pack(right,key)
        elif typ=="global_key": self.add_global_key(right,key)
        elif typ=="pct": self.add_percent(right,key)
        elif typ=="multiline": self.add_multiline(right,key)
        else: self.add_entry(right,key,typ)

    def add_bool(self,parent,key):
        var=tk.BooleanVar(value=self.raw_value(key,"bool"))
        label=tk.Label(parent,text="ON" if var.get() else "OFF",width=4,bg=self.palette["accent_dark"] if var.get() else self.palette["panel3"],fg=self.palette["white"],font=("Segoe UI",8,"bold"),cursor="hand2")
        def flip(*_):
            var.set(not var.get()); label.configure(text="ON" if var.get() else "OFF",bg=self.palette["accent_dark"] if var.get() else self.palette["panel3"])
        label.bind("<Button-1>",flip); label.pack(ipady=4)
        self.vars[key]=(var,"bool")

    def add_combo(self,parent,key,typ,choices):
        val=self.raw_value(key,typ)
        var=tk.StringVar(value=val)
        combo=ttk.Combobox(parent,textvariable=var,values=[str(x) for x in choices],state="readonly",width=18,style="Pretty.TCombobox")
        combo.pack()
        if typ=="edge_theme": combo.bind("<<ComboboxSelected>>",lambda e:self.edge_theme_changed(var.get()))
        if typ=="hibernate": combo.bind("<<ComboboxSelected>>",lambda e:self.hibernate_changed(var.get()))
        if typ=="corner": combo.bind("<<ComboboxSelected>>",lambda e:self.corner_changed(key,var.get()))
        self.vars[key]=(var,typ)

    def add_pack(self,parent,key):
        var=tk.StringVar(value=self.raw_value(key,"pack"))
        combo=ttk.Combobox(parent,textvariable=var,values=list(self.pack_map),state="readonly",width=24,style="Pretty.TCombobox")
        combo.pack()
        combo.bind("<<ComboboxSelected>>",lambda e:self.pack_changed(var.get()))
        self.vars[key]=(var,"pack")

    def add_global_key(self,parent,key):
        row=tk.Frame(parent,bg=self.palette["panel2"]); row.pack()
        var=tk.StringVar(value=str(self.cfg.get(key,"Key.esc")))
        display=tk.Label(row,text=key_to_display(var.get()),width=13,bg=self.palette["entry"],fg=self.palette["white"],font=("Segoe UI",8),padx=5,pady=4)
        display.pack(side="left",padx=(0,5))
        btn=tk.Button(row,text="Set Key",command=lambda:self.capture_global_key(var,display),relief="flat",bd=0,padx=8,pady=4,bg=self.palette["accent2"],fg=self.palette["white"],activebackground=self.palette["accent"],activeforeground=self.palette["white"],font=("Segoe UI",8,"bold"),cursor="hand2")
        btn.pack(side="left")
        self.vars[key]=(var,"global_key")

    def capture_global_key(self,var,display):
        win=tk.Toplevel(self.root); win.title("Set Global Panic Key"); win.geometry("360x150"); win.resizable(False,False); win.transient(self.root); win.grab_set(); win.configure(bg=self.palette["bg"])
        tk.Label(win,text="Press the key you want to use",bg=self.palette["bg"],fg=self.palette["white"],font=("Segoe UI",11,"bold")).pack(pady=(24,4))
        tk.Label(win,text="The first key press will be saved.",bg=self.palette["bg"],fg=self.palette["muted"],font=("Segoe UI",8)).pack()
        def got(event):
            # pynput represents special keys as Key.xxx and ordinary keys as 'x'.
            keyname = event.keysym
            special={"Escape":"Key.esc","Return":"Key.enter","space":"Key.space","Tab":"Key.tab","BackSpace":"Key.backspace","Delete":"Key.delete","Insert":"Key.insert","Home":"Key.home","End":"Key.end","Prior":"Key.page_up","Next":"Key.page_down","Up":"Key.up","Down":"Key.down","Left":"Key.left","Right":"Key.right","F1":"Key.f1","F2":"Key.f2","F3":"Key.f3","F4":"Key.f4","F5":"Key.f5","F6":"Key.f6","F7":"Key.f7","F8":"Key.f8","F9":"Key.f9","F10":"Key.f10","F11":"Key.f11","F12":"Key.f12"}
            value=special.get(keyname, keyname.lower())
            var.set(value); display.configure(text=value); win.destroy(); self.status.set(f"Global panic key set to {value}.")
        win.bind("<KeyPress>",got); win.focus_force()

    def add_percent(self,parent,key):
        var=tk.IntVar(value=max(0,min(100,int(self.cfg.get(key,0)))))
        row=tk.Frame(parent,bg=self.palette["panel2"]); row.pack()
        entry=tk.Entry(row,textvariable=var,width=5,justify="center",bg=self.palette["entry"],fg=self.palette["white"],insertbackground=self.palette["white"],relief="flat",highlightthickness=1,highlightbackground=self.palette["border"],font=("Segoe UI",8))
        entry.pack(side="right",padx=(5,0))
        scale_frame=tk.Frame(row,bg=self.palette["border"],highlightthickness=0,padx=1,pady=1)
        scale_frame.pack(side="left")
        scale=tk.Scale(scale_frame,from_=0,to=100,orient="horizontal",variable=var,length=125,showvalue=False,bg=self.palette["panel3"],fg=self.palette["white"],troughcolor=self.palette["trough"],highlightthickness=0,bd=0,relief="flat",activebackground=self.palette["accent2"],sliderrelief="solid",sliderlength=18)
        scale.pack()
        def clamp(*_):
            try:
                v=max(0,min(100,int(var.get())))
                if v!=var.get(): var.set(v)
            except: pass
        var.trace_add("write",clamp)
        self.vars[key]=(var,"pct")

    def add_multiline(self,parent,key):
        text=tk.Text(parent,width=26,height=3,wrap="none",bg=self.palette["entry"],fg=self.palette["white"],insertbackground=self.palette["white"],relief="flat",highlightthickness=1,highlightbackground=self.palette["border"],font=("Segoe UI",8))
        text.insert("1.0",self.raw_value(key,"multiline")); text.pack()
        self.vars[key]=(text,"multiline")

    def add_entry(self,parent,key,typ):
        var=tk.StringVar(value=self.raw_value(key,typ))
        entry=tk.Entry(parent,textvariable=var,width=18,bg=self.palette["entry"],fg=self.palette["white"],insertbackground=self.palette["white"],relief="flat",highlightthickness=1,highlightbackground=self.palette["border"],font=("Segoe UI",8))
        entry.pack(); self.vars[key]=(var,typ)

    def edge_theme_changed(self,value):
        self.cfg["themeType"]=value
        self.status.set(f"Edgeware appearance set to {value}. Save to keep it.")
        self.status_label.configure(text=f"EDGEWARE: {value.upper()}")

    def pack_changed(self,value):
        self.cfg["packPath"]=self.pack_map.get(value)
        applied=self.apply_pack_chance_overrides(self.cfg.get("packPath"), only_if_default=True)
        if applied:
            self.status.set(f"Pack selected: {value}. Applied pack overrides to: {', '.join(applied)}.")
            self.render(self.current_section)
        else:
            self.status.set(f"Pack selected: {value}. Save to keep it.")

    def apply_pack_chance_overrides(self, pack_name, only_if_default=False):
        if not pack_name: return []
        pack_config=PACKS/str(pack_name)/"config.json"
        if not pack_config.is_file(): return []
        overrides=load_json(pack_config,{})
        if not isinstance(overrides,dict): return []
        applied=[]
        for key in PACK_CHANCE_KEYS:
            if key not in overrides: continue
            try:
                value=int(overrides[key]); value=max(0,min(100,value))
            except Exception:
                continue
            if only_if_default and key in self.cfg and self.cfg.get(key) not in (self.defaults.get(key), self.original_defaults.get(key)): continue
            self.cfg[key]=value; applied.append(key)
        return applied

    def corner_changed(self,key,value):
        names={"Top-Left":0,"Top-Right":1,"Bottom-Left":2,"Bottom-Right":3}
        self.cfg[key]=names[value]

    def hibernate_changed(self,value):
        preset=HIBERNATE_PRESETS.get(value)
        if not preset:return
        for key,val in preset.items(): self.cfg[key]=val
        # Re-render so the four numeric fields immediately show the preset.
        self.status.set(f"Hibernate preset '{value}' applied. You can fine-tune the numbers below.")
        self.render("Modes")

    def apply_manager_theme(self):
        p=self.palette
        try:
            style=ttk.Style(self.root)
            style.theme_use("clam")
            style.configure("Pretty.TCombobox",fieldbackground=p["entry"],background=p["panel3"],foreground=p["white"],arrowcolor=p["white"],bordercolor=p["border"],lightcolor=p["border"],darkcolor=p["border"])
            style.map("Pretty.TCombobox",fieldbackground=[("readonly",p["entry"])],foreground=[("readonly",p["white"])])
            style.configure("Pretty.Vertical.TScrollbar",background=p["panel3"],troughcolor=p["panel"],arrowcolor=p["white"],bordercolor=p["border"],lightcolor=p["border"],darkcolor=p["border"])
            style.configure("Pretty.Horizontal.TProgressbar",background=p["accent2"],troughcolor=p["trough"],bordercolor=p["border"],lightcolor=p["accent2"],darkcolor=p["accent2"])
        except Exception:
            pass
        self.root.configure(bg=p["bg"])
        if not hasattr(self,"top"):
            return
        for w in (self.top,self.bottom,self.body):
            w.configure(bg=p["bg"])
        self.title.configure(bg=p["bg"],fg=p["white"])
        self.subtitle.configure(bg=p["bg"],fg=p["accent2"])
        self.status_label.configure(bg=p["bg"],fg=p["muted"])
        self.bottom_status_label.configure(bg=p["bg"],fg=p["dim"])
        self.nav.configure(bg=p["panel"],highlightbackground=p["border"])
        self.nav_title.configure(bg=p["panel"],fg=p["dim"])
        self.nav_divider.configure(bg=p["border"])
        for b in self.nav_action_buttons:
            b.configure(bg=p["panel"],fg=p["muted"],activebackground=p["panel3"],activeforeground=p["white"])
        for b in self.bottom_buttons:
            b.configure(bg=p["accent"] if b.cget("text")=="Save, Exit, and Run" else p["panel3"],fg=p["white"],activebackground=p["accent2"],activeforeground=p["white"])
        self.content.configure(bg=p["panel"],highlightbackground=p["border"])
        self.canvas.configure(bg=p["panel"])
        self.render(self.current_section)

    def manager_theme_changed(self,value):
        self.theme_name=value; self.palette=THEME_PALETTES[value]; self.cfg["_prettyConfigTheme"]=value; self.apply_manager_theme(); self.status.set(f"Manager appearance changed to {value}.")

    def select_manager_theme(self):
        pass

    def collect(self):
        for key,(var,typ) in self.vars.items():
            if typ=="bool":
                value = 1 if var.get() else 0
                self.cfg[key] = (1 - value) if key in INVERTED_BOOL_KEYS else value
            elif typ=="pct": self.cfg[key]=max(0,min(100,int(var.get())))
            elif typ=="multiline": self.cfg[key]=">".join(x.strip() for x in var.get("1.0","end").splitlines() if x.strip())
            elif typ=="pack": self.cfg[key]=self.pack_map.get(var.get())
            elif typ=="corner": self.cfg[key]={"Top-Left":0,"Top-Right":1,"Bottom-Left":2,"Bottom-Right":3}.get(var.get(),0)
            elif typ=="global_key": self.cfg[key]=var.get()
            elif typ in ("int","ms","sec","min"):
                value=int(str(var.get()).strip())
                if value<0: raise ValueError(f"{key} cannot be negative.")
                self.cfg[key]=value
            elif typ=="edge_theme": self.cfg[key]=var.get()
            else: self.cfg[key]=var.get()
        self.cfg["_prettyConfigTheme"]=self.theme_name

    def save(self,quiet=False):
        try:
            self.collect(); safe_backup(); save_json(CONFIG,self.cfg); self.status.set("Saved.")
            if not quiet: messagebox.showinfo(APP,"Settings saved.")
            return True
        except Exception as e:
            messagebox.showerror(APP,str(e)); return False

    def reset_defaults(self):
        if not messagebox.askyesno(APP,"Reset Edgeware settings to its defaults? Your current config will be backed up first."): return
        safe_backup(); self.cfg=dict(self.defaults); self.cfg.setdefault("lanczos",1); self.cfg["_prettyConfigTheme"]=self.theme_name
        pack=self.cfg.get("packPath")
        applied=self.apply_pack_chance_overrides(pack, only_if_default=False)
        self.render(self.current_section)
        self.status.set("Defaults loaded" + (f" with pack overrides: {', '.join(applied)}." if applied else ". Save to apply them."))

    def save_exit(self):
        if not self.save(True): return
        if truth(self.cfg.get("runOnSaveQuit", 0)):
            try:
                run_edgeware(self.cfg.get("packPath"))
            except Exception as e:
                messagebox.showerror(APP, f"Settings were saved, but Edgeware could not be started.\n\n{e}")
                return
        self.root.destroy()

    def save_exit_run(self):
        if not self.save(True): return
        try:
            run_edgeware(self.cfg.get("packPath")); self.root.destroy()
        except Exception as e:
            messagebox.showerror(APP,f"Settings were saved, but Edgeware could not be started.\n\n{e}")

    def import_pack_ui(self):
        name=import_pack(self.root)
        if name:
            self.refresh_packs(); self.cfg["packPath"]=name; self.render(self.current_section); self.status.set(f"Imported '{name}' and selected it.")

    def convert_webp_ui(self):
        self.refresh_packs(); current=self.cfg.get("packPath")
        pack_dir=(PACKS/current) if current else None
        if not pack_dir or not pack_dir.is_dir():
            messagebox.showinfo(APP,"Select a pack first."); return
        files=list(pack_dir.rglob("*.webp"))+list(pack_dir.rglob("*.WEBP"))
        if not files:
            messagebox.showinfo(APP,"No WebP files were found in the selected pack."); return
        if not messagebox.askyesno("Convert WebP to GIF",f"This will convert {len(files)} WebP file(s) in the selected pack to GIF and delete each WebP only after its GIF is created successfully.\n\nThis changes the pack files permanently. Continue?"): return
        if getattr(self,"conversion_running",False):
            return
        self.conversion_running=True
        cancel=threading.Event()
        q=Queue()
        win=tk.Toplevel(self.root)
        win.title("Converting WebP to GIF")
        win.geometry("560x220")
        win.resizable(False,False)
        win.transient(self.root)
        win.grab_set()
        win.configure(bg=self.palette["bg"])
        tk.Label(win,text="Converting WebP files",bg=self.palette["bg"],fg=self.palette["white"],font=("Segoe UI",12,"bold")).pack(anchor="w",padx=18,pady=(16,3))
        current_label=tk.Label(win,text="Preparing...",bg=self.palette["bg"],fg=self.palette["muted"],font=("Segoe UI",8))
        current_label.pack(anchor="w",padx=18,pady=(0,8))
        bar=ttk.Progressbar(win,mode="determinate",maximum=len(files),length=520,style="Pretty.Horizontal.TProgressbar")
        bar.pack(padx=18)
        percent=tk.Label(win,text="0%",bg=self.palette["bg"],fg=self.palette["white"],font=("Segoe UI",9,"bold"))
        percent.pack(pady=(6,2))
        frame_label=tk.Label(win,text="Frame 0 / 0",bg=self.palette["bg"],fg=self.palette["dim"],font=("Segoe UI",7))
        frame_label.pack()
        cancel_btn=tk.Button(win,text="Cancel",command=cancel.set,relief="flat",bd=0,padx=12,pady=5,bg=self.palette["panel3"],fg=self.palette["white"],activebackground=self.palette["accent"],activeforeground=self.palette["white"],font=("Segoe UI",8,"bold"))
        cancel_btn.pack(pady=(9,12))
        def progress(info): q.put(info)
        def worker():
            try:
                n=convert_webp_to_gif(pack_dir,progress,cancel)
                q.put({"stage":"done","converted":n,"cancelled":cancel.is_set()})
            except Exception as e:
                q.put({"stage":"failed","error":str(e)})
        threading.Thread(target=worker,daemon=True).start()
        def poll():
            try:
                while True:
                    info=q.get_nowait()
                    stage=info.get("stage")
                    if stage in ("frame","file","error"):
                        idx=info.get("file",0); total=info.get("total",len(files)); name=info.get("name","")
                        bar["value"]=idx
                        percent.configure(text=f"{int(idx/max(1,total)*100)}%")
                        current_label.configure(text=f"{idx} of {total}: {name}")
                        frame_label.configure(text=f"Frame {info.get('frame',0)} / {info.get('frames',0)}")
                    elif stage=="done":
                        self.conversion_running=False; win.grab_release(); win.destroy()
                        if info.get("cancelled"):
                            messagebox.showinfo(APP,f"Conversion cancelled. {info.get('converted',0)} file(s) were converted before cancellation.")
                        else:
                            messagebox.showinfo(APP,f"Converted {info.get('converted',0)} WebP file(s) to GIF.")
                        return
                    elif stage=="failed":
                        self.conversion_running=False; win.grab_release(); win.destroy(); messagebox.showerror(APP,info.get("error","Conversion failed.")); return
            except Empty:
                pass
            if win.winfo_exists():
                self.root.after(80,poll)
        self.root.after(80,poll)

    def add_troubleshooting_tool(self):
        if self.current_section!="Troubleshooting": return
        # Tool card is added after settings; avoid duplicate by checking marker.
        if getattr(self,"tool_added",False): return
        self.tool_added=True
        card=tk.Frame(self.page,bg=self.palette["panel3"],highlightthickness=1,highlightbackground=self.palette["border"]); card.pack(fill="x",padx=14,pady=7)
        tk.Label(card,text="WebP compatibility",bg=self.palette["panel3"],fg=self.palette["white"],font=("Segoe UI",8,"bold")).pack(anchor="w",padx=10,pady=(7,1))
        tk.Label(card,text="Animated WebP files are handed to the video player, so Lanczos cannot repair every black-WebP problem. This utility converts the selected pack's WebP files to GIF with a shared palette for better animation quality, shows progress, and removes the originals only after successful conversion.",bg=self.palette["panel3"],fg=self.palette["muted"],font=("Segoe UI",7),wraplength=650,justify="left").pack(anchor="w",padx=10,pady=(0,5))
        self.make_button(card,"Convert selected pack's WebP files to GIF",self.convert_webp_ui,primary=True).pack(anchor="w",padx=10,pady=(0,6))
        theme_btn=self.make_button(card,"Fix Edgeware theme background",self.fix_edgeware_theme_ui)
        theme_btn.pack(anchor="w",padx=10,pady=(0,8))

    def fix_edgeware_theme_ui(self):
        if not messagebox.askyesno(APP,"Apply the Edgeware theme background fix?\n\nThis makes popup windows use the selected Edgeware theme background instead of a hard-coded black background. A backup of popup.py will be kept before changing it."):
            return
        try:
            changed,message=apply_edgeware_theme_background_fix()
            messagebox.showinfo(APP,message)
            self.status.set(message)
        except Exception as e:
            messagebox.showerror(APP,str(e))

    def open_root(self):
        try:
            if os.name=="nt": os.startfile(str(HERE))
            elif sys.platform=="darwin": subprocess.Popen(["open",str(HERE)])
            else: subprocess.Popen(["xdg-open",str(HERE)])
        except Exception: messagebox.showinfo(APP,str(HERE))

    def close(self): self.root.destroy()

    def run(self): self.root.mainloop()


# Manager Appearance is intentionally separate from Edgeware's own theme settings.
old_start=SECTIONS["Start"]
SECTIONS["Start"]=[("_managerTheme","Manager appearance","This changes this configuration window immediately. It does not change Edgeware's runtime theme.","manager_theme",MANAGER_THEMES)]+old_start

# Patch App.add_setting for manager theme.
_original_add_setting=App.add_setting
def _add_setting(self,key,label,helptext,typ,choices):
    if typ=="manager_theme":
        card=tk.Frame(self.page,bg=self.palette["panel2"],highlightthickness=1,highlightbackground=self.palette["border"]); card.pack(fill="x",padx=14,pady=3)
        left=tk.Frame(card,bg=self.palette["panel2"]); left.pack(side="left",fill="both",expand=True,padx=10,pady=7)
        tk.Label(left,text=label,bg=self.palette["panel2"],fg=self.palette["white"],font=("Segoe UI",8,"bold")).pack(anchor="w")
        tk.Label(left,text=helptext,bg=self.palette["panel2"],fg=self.palette["muted"],font=("Segoe UI",7),wraplength=560,justify="left").pack(anchor="w",pady=(1,0))
        right=tk.Frame(card,bg=self.palette["panel2"]); right.pack(side="right",padx=10,pady=7)
        var=tk.StringVar(value=self.theme_name); combo=ttk.Combobox(right,textvariable=var,values=choices,state="readonly",width=18,style="Pretty.TCombobox"); combo.pack(); combo.bind("<<ComboboxSelected>>",lambda e:self.manager_theme_changed(var.get()))
        self.vars[key]=(var,typ); return
    _original_add_setting(self,key,label,helptext,typ,choices)
App.add_setting=_add_setting

_original_render=App.render
def _render(self,section):
    self.tool_added=False
    _original_render(self,section)
    if section=="Troubleshooting": self.add_troubleshooting_tool()
App.render=_render

if __name__=="__main__":
    try: App().run()
    except Exception as e:
        root=tk.Tk(); root.withdraw(); messagebox.showerror(APP,f"Could not start the configuration manager.\n\n{e}"); root.destroy()
