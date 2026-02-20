# BAT/CMD-2-EXE Converter

> **Convert Windows batch scripts (.BAT / .CMD) into standalone executable files (.EXE) — with a modern graphical interface, no command-line required.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [How It Works](#how-it-works)
- [Interface Guide](#interface-guide)
  - [Form Fields](#form-fields)
  - [Toggle Controls](#toggle-controls)
  - [Action Buttons](#action-buttons)
  - [Status Bar](#status-bar)
  - [Log Panel](#log-panel)
- [Themes](#themes)
- [Password Protection](#password-protection)
- [EXE Metadata](#exe-metadata)
- [Compression](#compression)
- [Conversion Modes](#conversion-modes)
- [Settings Persistence](#settings-persistence)
- [Developer Notes](#developer-notes)

---

## Overview

**BAT/CMD-2-EXE Converter** is a Windows desktop application written in Python that wraps your `.bat` or `.cmd` scripts into self-contained `.exe` files using [PyInstaller](https://pyinstaller.org/). The resulting EXE runs on any Windows machine — no Python, no batch interpreter visible to the end user.

The GUI is built entirely in `tkinter` (no external UI framework required) and supports two languages (**Polish** and **English**), six visual themes, SHA-256 password protection, custom EXE icons, PE metadata embedding, and two optional compression algorithms.

---

## Features

| Feature | Details |
|---|---|
| 🔄 BAT → EXE conversion | Powered by PyInstaller `--onefile` |
| 🎨 6 visual themes | Dark, Light, Cyberpunk, Hacker/Matrix, Ocean, Sunset |
| 🌐 Bilingual UI | Polish / English, switchable live without restart |
| 🔑 Password protection | SHA-256 hash embedded in EXE, 3 attempts per launch |
| 🖼 Custom icon | `.ico`, `.png`, `.jpg` — auto-converted via Pillow |
| 🏷 PE metadata | Product name, version, company, description, copyright |
| 📦 Two conversion modes | Wrapper (BAT embedded as string) or Embed (BAT as resource) |
| 🗜 Two compression options | UPX (external tool) or custom LZMA stub |
| 💻 Console toggle | Show or hide the console window of the generated EXE |
| 💾 Settings persistence | Last-used folder, skin, language saved in `%APPDATA%` |
| 📌 Always-on-top pin | Keep the window floating above others |

---

## Requirements

| Dependency | Purpose | Required |
|---|---|---|
| Python 3.10+ | Runtime | ✅ Yes |
| `pyinstaller` | Core conversion engine | ✅ Yes |
| `pillow` | Icon conversion (PNG/JPG → ICO) | ⚠️ Auto-installed if missing |
| `tkinter` | GUI (built into Windows Python) | ✅ Bundled |
| `upx.exe` | UPX compression (optional) | ❌ Optional |

**Install PyInstaller before first use:**

```bash
pip install pyinstaller
```

> `pillow` is installed automatically by the application if you choose a PNG or JPG icon and it is not already present.

---

## Installation

No installation wizard required. The entire application is a single Python script.

```bash
# 1. Clone or download
git clone https://github.com/seb07uk/bat2exe-gui
cd bat2exe-gui

# 2. Install the only hard dependency
pip install pyinstaller

# 3. Run
python bat_to_exe_gui.py
```

Or simply double-click `bat_to_exe_gui.py` if Python is associated with `.py` files on your system.

---

## How It Works

The conversion pipeline runs entirely in a background thread so the GUI stays responsive:

```
.BAT file
    │
    ▼
[1] Python wrapper script is generated
    │   • Wrapper mode  →  BAT content embedded as a Python string literal
    │   • Embed mode    →  BAT file attached as a PyInstaller data resource
    │
    ▼
[2] Optional: SHA-256 password guard injected at the top of the wrapper
    │
    ▼
[3] Optional: PE version-info file generated (metadata)
    │
    ▼
[4] PyInstaller packages everything → single --onefile .exe
    │
    ▼
[5] Optional: UPX or LZMA compression applied to the .exe
    │
    ▼
  output.exe  ✔
```

When the generated EXE runs on the end user's machine:

- **Wrapper mode** — the BAT content is written to a temporary file and executed via `cmd.exe /c`, then deleted.
- **Embed mode** — the BAT file is extracted from `sys._MEIPASS` (PyInstaller's temp bundle directory) and executed directly.

---

## Interface Guide

### Form Fields

| Field | Description |
|---|---|
| **.BAT File** | Path to the source `.bat` or `.cmd` file. Use the **Browse…** button or type/paste the path manually. Selecting a file auto-fills the Output Folder and EXE Name fields. |
| **Output Folder** | Directory where the finished `.exe` will be saved. Created automatically if it does not exist. Defaults to the parent folder of the selected BAT file. |
| **Icon** | Optional icon for the EXE. Accepts `.ico`, `.png`, and `.jpg/.jpeg`. PNG/JPG files are converted to multi-resolution ICO automatically using Pillow. If left empty, the application's own built-in icon is used. |
| **EXE Name** | Filename for the output (without `.exe`). Defaults to the name of the source BAT file. |

### Toggle Controls

The four toggle switches in the middle of the form are animated sliders:

| Toggle | States | Default |
|---|---|---|
| **Console** | ON (console shown) / OFF (hidden window) | ON |
| **Wrapper / Embed** | Wrapper (BAT as string) / Embed (BAT as file resource) | Wrapper |
| **Compression** | None → UPX → LZMA → None (cycles on each click) | None |
| **Password** | Inactive / Active (opens password dialog) | Inactive |

### Action Buttons

| Button | Function |
|---|---|
| **▶ Convert** | Starts the conversion. Disabled while a conversion is running. |
| **📁 Dist** | Opens the output folder in Windows Explorer after a successful conversion. |
| **🏷 Metadata** | Opens the metadata editor dialog (product name, version, company, description, copyright). |

### Status Bar

The bottom status bar contains several interactive elements:

| Element | Position | Function |
|---|---|---|
| `●` status dot | Left | Green = ready / Orange = converting / Red = error |
| Status text | Left | Describes current state |
| Elapsed timer | Right | Shows `mm:ss` during conversion |
| Current filename | Right | BAT or EXE name depending on state |
| `?` | Far right | Opens the built-in **Help** window (5-tab reference guide) |
| `ⓘ` | Far right | Opens the **About** dialog |
| Language switch (`EN` / `PL`) | Far right | Switches UI language live |
| Theme icon (e.g. `🌑`) | Far right | Left-click: cycles through themes. Right-click: opens the visual theme picker |
| `📌` pin | Far right | Toggles always-on-top window mode |

### Log Panel

The scrollable log panel at the bottom of the window shows the real-time output of PyInstaller and all compression steps. Lines are colour-coded:

| Colour | Meaning |
|---|---|
| 🟢 Green (bold) | Success messages |
| 🔴 Red (bold) | Errors |
| 🟡 Yellow / Orange | Warnings |
| 🔵 Blue | Informational |
| 🟣 Purple | File paths |
| 🩵 Cyan (bold) | Section headers (e.g. `─── UPX compression ───`) |
| Grey (dim) | Low-priority PyInstaller output |

---

## Themes

Six themes are available and can be cycled by clicking the theme icon in the status bar. Right-clicking opens a picker dialog showing all themes at once.

| Theme | Icon | Description |
|---|---|---|
| Dark | 🌑 | Deep navy blue — the default |
| Light | ☀ | Light grey with red accents |
| Cyberpunk | ⚡ | Near-black with neon yellow |
| Hacker / Matrix | 💻 | Pure black with bright green terminal text |
| Ocean | 🌊 | Dark teal with cyan accents |
| Sunset | 🌅 | Dark purple with orange accents |

The selected theme is saved and restored automatically on next launch.

---

## Password Protection

When the **Password** toggle is activated, a dialog prompts you to set a password before conversion.

- The password is hashed with **SHA-256** and the hash is embedded directly into the generated EXE source.
- On every launch of the generated EXE, the user is shown a tkinter password prompt.
- The user has **3 attempts**. After 3 wrong entries, the EXE exits automatically.
- The password prompt respects the language selected at conversion time (Polish or English).
- No plaintext password is stored anywhere — only the SHA-256 hex digest.

---

## EXE Metadata

Clicking the **🏷 Metadata** button opens a dialog where you can fill in Windows PE version information that appears in the file's Properties window:

| Field | Description |
|---|---|
| Product Name | The software product name |
| Version | Four-part version number (e.g. `1.2.3.4`) |
| Company / Author | Organisation or author name |
| Description | Short file description |
| Copyright | Copyright string |

These fields are passed to PyInstaller as a `version_info.txt` file and embedded in the `.exe` PE header. They appear under **Right-click → Properties → Details** in Windows Explorer.

---

## Compression

After the EXE is generated, optional compression can be applied:

### UPX
- Uses the external `upx.exe` tool.
- Searched in `PATH`, the script's own directory, and common `%ProgramFiles%` subdirectories.
- Compression level: `-9` (maximum).
- Typical size reduction: 40–60% for Python EXEs.
- Download UPX from [https://upx.github.io/](https://upx.github.io/) and place it next to the script or add it to `PATH`.

### LZMA (built-in)
- Custom self-extracting stub approach — no external tool required.
- The original EXE is compressed with Python's `lzma` module at preset `9|PRESET_EXTREME`.
- A new PyInstaller stub EXE is built that decompresses and launches the payload at runtime.
- ⚠️ **Note:** Because the stub itself is a full PyInstaller EXE, the final file may be *larger* than the original. This is reported honestly in the log. LZMA compression is most effective for very large EXEs where the payload savings exceed the stub overhead.

---

## Conversion Modes

| Mode | How it works | Best for |
|---|---|---|
| **Wrapper** (default) | The full content of the `.bat` file is stored as a Python string literal inside the wrapper script. At runtime, it is written to a temp file and executed. | General use — the BAT content is fully self-contained in the EXE. |
| **Embed** | The `.bat` file is attached as a PyInstaller data resource (`--add-data`). At runtime it is accessed via `sys._MEIPASS`. | When you want the original `.bat` file to be extractable or when the BAT references relative paths. |

---

## Settings Persistence

Application settings are stored as a JSON file:

```
%APPDATA%\bat2exe_gui\settings.json
```

The following settings are saved automatically on exit and restored on launch:

- Selected language (`pl` / `en`)
- Selected theme / skin name
- Window geometry (position and size)
- Last used output folder

---

## Developer Notes

**Author:** Sebastian Januchowski  
**Company:** polsoft.ITS™ Group  
**Email:** polsoft.its@fastservice.com  
**GitHub:** [https://github.com/seb07uk](https://github.com/seb07uk)  
**Version:** 1.0.0  
**License:** © 2026 polsoft.ITS™ DEV. All rights reserved.

### Script Architecture

```
bat_to_exe_gui.py
├── LANG dict          — All PL/EN UI strings
├── T()                — Translation lookup function
├── _ensure_ico()      — Icon format conversion (Pillow)
├── _check_pyinstaller() — Pre-flight PyInstaller validation
├── convert()          — Core conversion logic (runs in thread)
├── _find_upx()        — UPX binary discovery
├── _compress_upx()    — UPX compression wrapper
├── _compress_lzma()   — Custom LZMA stub-based compression
├── _load_cfg()        — Load settings from JSON
├── _save_cfg()        — Save settings to JSON
├── THEMES dict        — 6 colour theme definitions
├── ICON_B64           — App icon embedded as base64 PNG
├── WATERMARK_B64      — Watermark graphic embedded as base64 PNG
└── App(tk.Tk)         — Main GUI class
    ├── _build_ui()
    ├── _row_bat/out/icon/name/flags/btn()
    ├── _toggle_console/embed/compress/password()
    ├── _show_about/help/metadata/skin_picker()
    ├── _apply_theme()
    ├── _toggle_lang() / _refresh_ui_lang()
    └── worker()        — Background conversion thread
```

### Key Technical Decisions

- **Single-file script** — the entire application (GUI, conversion logic, themes, translations, embedded graphics) is in one `.py` file for maximum portability.
- **Threading** — conversion runs in a `daemon` thread; UI updates are dispatched back to the main thread via `self.after()`.
- **Embedded icons** — both the app icon and watermark are stored as base64-encoded PNG strings, eliminating the need for external asset files.
- **Windows-only** — the tool uses `cmd.exe`, `%APPDATA%`, Windows `mbcs` encoding, and `%ProgramFiles%` path heuristics. It is not portable to Linux/macOS by design.

### Known Limitations

- PyInstaller must be installed and accessible via `python -m PyInstaller` (validated before each conversion).
- LZMA compression may increase file size when the stub overhead exceeds the payload savings.
- The generated EXE requires the end user to have the Visual C++ Redistributable installed (standard on modern Windows versions).
- Pillow is required for icon conversion; it is installed automatically at conversion time if absent, which adds a one-time delay on first use with a PNG/JPG icon.