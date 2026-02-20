import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
import subprocess
import sys
import webbrowser
import os
import shutil
import tempfile
import json
import logging
import threading
import math
from datetime import datetime
from PIL import Image, ImageTk, ImageFilter, ImageDraw

# ── PATHS ──────────────────────────────────────────────────────────────────
_BASE_DIR  = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")),
                          ".polsoft", "software", "compilers", "bat2exe")
_LOG_DIR     = os.path.join(_BASE_DIR, "log")
_LOG_FILE    = os.path.join(_LOG_DIR,  "bat2exe.log")
_JSON_FILE   = os.path.join(_BASE_DIR, "bat2exe.json")
_HISTORY_DIR = os.path.join(_BASE_DIR, "history")

os.makedirs(_LOG_DIR,     exist_ok=True)
os.makedirs(_HISTORY_DIR, exist_ok=True)

# Katalog skryptu — używany do wyszukiwania icon.ico niezależnie od CWD
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def _find_icon() -> str:
    """Return first existing icon path, or empty string."""
    for candidate in [
        os.path.join(_SCRIPT_DIR, "icon.ico"),
        os.path.join(_SCRIPT_DIR, "logo.ico"),
        "icon.ico",
    ]:
        if os.path.isfile(candidate):
            return candidate
    return ""

_APP_ICON = _find_icon()   # resolved once at startup

logging.basicConfig(
    filename=_LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
_log = logging.getLogger("bat2exe")


TRANSLATIONS = {
    "en": {
        "title":          "BAT → EXE  |  2026© Sebastian Januchowski",
        "header_title":   "polsoft.ITS™ BAT → EXE Converter",
        "label_bat":      "BAT file:",
        "label_icon":     "Icon .ico/.png/.jpg (optional):",
        "label_output":   "Output directory:",
        "label_outname":  "Output filename (optional):",
        "hint_outname":   "Leave empty to use BAT filename",
        "label_preview":  "BAT preview:",
        "opt_onefile":    "Onefile",
        "opt_console":    "Console",
        "opt_lock":       "Lock size",
        "opt_topmost":    "Top most",
        "btn_compile":    "CONVERT",
        "btn_history":    "🕐 Recent",
        "status_ready":   "Status: Ready",
        "status_compile": "Status: Converting...",
        "status_ok":      "Status: Success!",
        "status_err":     "Status: Convert error",
        "status_crit":    "Status: Error",
        "warn_title":     "Warning",
        "warn_msg":       "Select a BAT file and output folder!",
        "ok_title":       "Done",
        "ok_msg":         "Output file:\n{}",
        "err_title":      "Error",
        "err_msg":        "Conversion failed. Check the log for details.",
        "crit_title":     "Critical error",
        "lang_btn":       "PL",
        "help_title":     "Help",
        "help_msg":       "BAT->EXE Converter -- User Guide\n\nCONVERTS .bat to .exe using PyInstaller. No Python on target PC.\n\nHOW TO USE:\n 1. BAT File     - click ... and select your .bat script\n 2. Icon opt     - pick a custom .ico (optional)\n 3. Output dir   - choose where to save the .exe\n 4. Output name  - custom .exe filename (optional, default = BAT name)\n 5. Options:\n    Onefile   = single .exe file\n    Console   = show console window\n    Lock size = prevent window resize\n    sun/moon  = theme toggle (next to Lock size)\n 6. Click CONVERT\n\nBOTTOM BAR: LOG | ? | i | PL/EN | pin\nRECENT: click 'Recent' button to reload past conversions\n\nINSTALL: pip install pyinstaller customtkinter pillow",
        "about_title":    "About",
        "history_title":  "Recent files",
        "history_empty":  "No conversion history yet.",
        "history_load":   "Load",
        "history_clear":  "Clear history",
    },
    "pl": {
        "title":          "BAT → EXE  |  2026© Sebastian Januchowski",
        "header_title":   "polsoft.ITS™ BAT → EXE Converter",
        "label_bat":      "Plik .bat:",
        "label_icon":     "Ikona .ico/.png/.jpg (opcjonalnie):",
        "label_output":   "Katalog wyjściowy:",
        "label_outname":  "Nazwa pliku wyjściowego (opcjonalnie):",
        "hint_outname":   "Puste = nazwa pliku BAT",
        "label_preview":  "Podgląd BAT:",
        "opt_onefile":    "Onefile",
        "opt_console":    "Konsola",
        "opt_lock":       "Zablokuj rozmiar",
        "opt_topmost":    "Na wierzchu",
        "btn_compile":    "KONWERTUJ",
        "btn_history":    "🕐 Ostatnie",
        "status_ready":   "Status: Gotowy",
        "status_compile": "Status: Konwersja...",
        "status_ok":      "Status: Sukces!",
        "status_err":     "Status: Błąd konwersji",
        "status_crit":    "Status: Błąd",
        "warn_title":     "Błąd",
        "warn_msg":       "Wybierz plik BAT i folder wyjściowy!",
        "ok_title":       "OK",
        "ok_msg":         "Gotowe:\n{}",
        "err_title":      "Błąd",
        "err_msg":        "Konwersja nieudana. Sprawdź log po szczegóły.",
        "crit_title":     "Błąd krytyczny",
        "lang_btn":       "EN",
        "help_title":     "Pomoc",
        "help_msg":       "BAT->EXE Converter -- Instrukcja\n\nKonwertuje .bat na .exe za pomoca PyInstaller.\n\nJAK UZYWAC:\n 1. Plik BAT     - wybierz skrypt .bat\n 2. Ikona opt    - wybierz ikone .ico (opcjonalnie)\n 3. Katalog wyj  - gdzie zapisany bedzie .exe\n 4. Nazwa pliku  - wlasna nazwa .exe (opcjonalne, domyslnie = nazwa BAT)\n 5. Opcje:\n    Onefile   = jeden plik .exe\n    Konsola   = okno konsoli przy uruchomieniu\n    Zablokuj  = blokuje zmiane rozmiaru\n    slonce/ks = motyw (obok Zablokuj)\n 6. Kliknij KONWERTUJ\n\nPASEK: LOG | ? | i | PL/EN | pin\nOSTATNIE: przycisk 'Ostatnie' wczytuje poprzednie konwersje\n\nWYMAGANIA: pip install pyinstaller customtkinter pillow",
        "about_title":    "O programie",
        "history_title":  "Ostatnie pliki",
        "history_empty":  "Brak historii konwersji.",
        "history_load":   "Wczytaj",
        "history_clear":  "Wyczyść historię",
    },
}

PALETTES = {
    "dark": {
        "header_top":   "#0a1628",
        "header_bot":   "#040a12",
        "main":         "#0e1926",
        "aero_border":  "#1e3a5f",
        "input_card":   "#121e30",
        "input_card2":  "#1c3050",
        "btn_misc":     "#182840",
        "btn_misc_h":   "#243858",
        "accent":       "#2e6fd0",
        "bottom_bg":    "#060c16",
        # ── text tokens ──────────────────────────────────────────────────
        "text_primary": "#dce8ff",   # main label / checkbox text  (bright, high contrast)
        "text_label":   "#a8c4e8",   # secondary field labels       (visible but not glaring)
        "text_dim":     "#8eaece",   # status bar                   (was #6a90b8 — too dark)
        "text_entry":   "#c8deff",   # text inside entry/log boxes
    },
    "light": {
        "header_top":   "#d0e8ff",
        "header_bot":   "#a8ccee",
        "main":         "#e4f0fc",
        "aero_border":  "#7aaad8",
        "input_card":   "#cce4f8",
        "input_card2":  "#b0cce8",
        "btn_misc":     "#98b8d4",
        "btn_misc_h":   "#7a9abe",
        "accent":       "#2060b8",
        "bottom_bg":    "#b0ccec",
        # ── text tokens ──────────────────────────────────────────────────
        "text_primary": "#0a1e40",   # main label / checkbox text
        "text_label":   "#1a3560",   # secondary field labels
        "text_dim":     "#2a4a80",   # status bar               (was #3a5a90 — too light)
        "text_entry":   "#0d2050",   # text inside entry/log boxes
    },
}


def make_gradient_image(w, h, color_top, color_bot, alpha_top=255, alpha_bot=255):
    """Fast vertical gradient, optional alpha fade (returns RGBA Image).

    Previously this built the pixel buffer row-by-row in a pure-Python loop
    which creates h intermediate bytes objects and joins them at the end.
    Now we build a single flat bytearray (4*w*h bytes) with in-place slice
    assignment — roughly 5-10x faster for typical header/bottom-bar sizes
    without requiring numpy.
    """
    r1, g1, b1 = int(color_top[1:3], 16), int(color_top[3:5], 16), int(color_top[5:7], 16)
    r2, g2, b2 = int(color_bot[1:3], 16), int(color_bot[3:5], 16), int(color_bot[5:7], 16)
    span = max(h - 1, 1)
    buf  = bytearray(4 * w * h)
    idx  = 0
    for y in range(h):
        t   = y / span
        row = bytes([
            int(r1 + (r2 - r1) * t),
            int(g1 + (g2 - g1) * t),
            int(b1 + (b2 - b1) * t),
            int(alpha_top + (alpha_bot - alpha_top) * t),
        ]) * w
        buf[idx: idx + 4 * w] = row
        idx += 4 * w
    return Image.frombytes("RGBA", (w, h), bytes(buf))



def _make_frosted_panel(w, h, base_color, alpha=160):
    """Frosted-glass RGBA panel: solid colour at given alpha."""
    r,g,b = int(base_color[1:3],16), int(base_color[3:5],16), int(base_color[5:7],16)
    return Image.new("RGBA", (w, h), (r, g, b, alpha))


def _paste_rgba(base_rgba: Image.Image, overlay_rgba: Image.Image, x=0, y=0) -> Image.Image:
    """Paste an RGBA overlay onto an RGBA base at (x,y) using alpha compositing."""
    tmp = Image.new("RGBA", base_rgba.size, (0, 0, 0, 0))
    tmp.paste(overlay_rgba, (x, y))
    return Image.alpha_composite(base_rgba, tmp)


def _glow_circle(size, color_hex, blur=14):
    """Soft circular glow image (RGBA)."""
    r,g,b = int(color_hex[1:3],16), int(color_hex[3:5],16), int(color_hex[5:7],16)
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    d   = ImageDraw.Draw(img)
    d.ellipse([0,0,size-1,size-1], fill=(r,g,b,200))
    return img.filter(ImageFilter.GaussianBlur(blur))





def _convert_image_to_ico(src_path: str, dest_dir: str) -> str:
    """Convert PNG/JPG/ICO to a proper .ico file in dest_dir. Returns path to .ico."""
    ext = os.path.splitext(src_path)[1].lower()
    if ext == ".ico":
        return src_path  # already ICO
    dest = os.path.join(dest_dir, "_icon_converted.ico")
    img = Image.open(src_path).convert("RGBA")
    # Resize to multiple ICO sizes for best quality
    sizes = [(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)]
    imgs = [img.resize(s, Image.LANCZOS) for s in sizes]
    imgs[0].save(dest, format="ICO", sizes=[(i.width, i.height) for i in imgs],
                 append_images=imgs[1:])
    return dest


def _banner_try_font(size):
    """Try to load a bold TrueType font at given size; fall back to PIL default."""
    from PIL import ImageFont as _IF
    for _fn in ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]:
        try:
            return _IF.truetype(_fn, size)
        except Exception:
            pass
    try:
        return _IF.load_default()
    except Exception:
        return None


def _banner_gold_label(text, font_size):
    """Return (ImageTk.PhotoImage, text_w, text_h) with gold mirror-gradient.

    The returned PhotoImage must be kept alive by the caller (store on self).
    """
    _fnt = _banner_try_font(font_size)
    _tmp = Image.new("RGBA", (1, 1))
    _td  = ImageDraw.Draw(_tmp)
    try:
        _bb = _td.textbbox((0, 0), text, font=_fnt)
        _tw, _th = _bb[2] - _bb[0], _bb[3] - _bb[1]
    except Exception:
        _tw, _th = len(text) * font_size // 2, font_size
    _tw = max(_tw, 1)
    _th = max(_th, 1)
    pad = 4

    # Text mask
    _msk = Image.new("L", (_tw + pad * 2, _th + pad * 2), 0)
    ImageDraw.Draw(_msk).text((pad, pad), text, font=_fnt, fill=255)

    # 8-stop gold mirror gradient
    _stops = [
        (0.00, (45,  30,   4)),
        (0.10, (120, 85,  18)),
        (0.25, (210, 160, 45)),
        (0.40, (255, 228, 120)),
        (0.50, (255, 252, 210)),   # white flash
        (0.62, (245, 195, 75)),
        (0.78, (175, 125, 28)),
        (1.00, (50,  34,   5)),
    ]
    _grad = Image.new("RGBA", (_tw + pad * 2, _th + pad * 2), (0, 0, 0, 0))
    _gd   = ImageDraw.Draw(_grad)
    for _row in range(_th + pad * 2):
        _t2 = _row / max(_th + pad * 2 - 1, 1)
        _c  = _stops[0][1]
        for _i in range(len(_stops) - 1):
            _t0, _c0 = _stops[_i]
            _t1, _c1 = _stops[_i + 1]
            if _t0 <= _t2 <= _t1:
                _f  = (_t2 - _t0) / max(_t1 - _t0, 0.001)
                _c  = tuple(max(0, min(255, int(_c0[j] + (_c1[j] - _c0[j]) * _f)))
                            for j in range(3))
                break
        _gd.line([(0, _row), (_tw + pad * 2, _row)], fill=_c + (255,))

    # Diagonal shine
    _shine = Image.new("RGBA", (_tw + pad * 2, _th + pad * 2), (0, 0, 0, 0))
    _sd    = ImageDraw.Draw(_shine)
    for _si in range((_th + pad * 2) // 2):
        _sa = max(0, 55 - _si * 6)
        _sd.line([(0, _si), (_si, 0)], fill=(255, 255, 255, _sa), width=1)

    _result = Image.new("RGBA", (_tw + pad * 2, _th + pad * 2), (0, 0, 0, 0))
    _result.paste(_grad, mask=_msk)
    _result = Image.alpha_composite(_result, _shine)

    # Drop-shadow layer (4 px larger to avoid clipping)
    _out_sz = (_tw + pad * 2 + 4, _th + pad * 2 + 4)
    _sh  = Image.new("RGBA", _out_sz, (0, 0, 0, 0))
    ImageDraw.Draw(_sh).text((pad + 2, pad + 2), text, font=_fnt, fill=(0, 0, 0, 160))
    _sh  = _sh.filter(ImageFilter.GaussianBlur(2))
    _out = Image.new("RGBA", _out_sz, (0, 0, 0, 0))
    _out = Image.alpha_composite(_out, _sh)
    _out.paste(_result, (0, 0), _result)
    return ImageTk.PhotoImage(_out), _tw, _th


class BatToExeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        ctk.set_widget_scaling(0.85)
        ctk.set_window_scaling(0.85)

        self.current_lang = "en"
        self.current_mode = "dark"

        self.geometry("520x700")
        self.minsize(460, 600)

        self.lock_size_var = ctk.BooleanVar(value=False)
        self.topmost_var   = ctk.BooleanVar(value=False)
        self._themed:       dict   = {}
        self._anim_job:     object = None
        self._anim_frame:   int    = 0
        self._particles:    list   = []
        self._current_icon_path: str   = ""
        self._history_popup: object    = None   # reference to open history window

        # ── Application icon ───────────────────────────────────────────────
        if _APP_ICON:
            try:
                self.iconbitmap(_APP_ICON)
            except Exception:
                pass

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_ui()
        self.load_settings()   # <-- wczytaj ustawienia po zbudowaniu UI
        self.apply_lang()

        self.bind("<Configure>", self.on_window_resize)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        _log.info("Aplikacja uruchomiona.")

        # ── PyInstaller availability check ─────────────────────────────────
        # Done after setup_ui so we can write to the log box and status bar.
        # We defer by 200 ms so the window has time to appear first.
        self.after(200, self._check_pyinstaller)

    # ------------------------------------------------------------------ #
    # PYINSTALLER CHECK
    # ------------------------------------------------------------------ #
    def _check_pyinstaller(self):
        """Verify PyInstaller is reachable on PATH; warn user if not.

        This runs once, 200 ms after the window opens, so it never blocks
        startup.  We try `pyinstaller --version` rather than just shutil.which
        so we also catch broken installations where the script exists but the
        package itself is broken.
        """
        try:
            result = subprocess.run(
                ["pyinstaller", "--version"],
                capture_output=True, text=True, timeout=8,
            )
            version = result.stdout.strip() or result.stderr.strip()
            msg = f"[OK] PyInstaller found: {version}\n"
            _log.info("PyInstaller check OK: %s", version)
            self._append_log(msg)
        except FileNotFoundError:
            warn = (
                "[WARN] PyInstaller NOT found on PATH.\n"
                "       Install it with:  pip install pyinstaller\n"
                "       The CONVERT button will fail until it is installed.\n"
            )
            _log.warning("PyInstaller not found on PATH at startup.")
            self._append_log(warn)
            self._set_status("Status: PyInstaller missing!", "red")
        except subprocess.TimeoutExpired:
            _log.warning("PyInstaller version check timed out.")
            self._append_log("[WARN] PyInstaller version check timed out.\n")
        except Exception as exc:
            _log.warning("PyInstaller check error: %s", exc)
            self._append_log(f"[WARN] PyInstaller check error: {exc}\n")

    # ------------------------------------------------------------------ #
    # HISTORY
    # ------------------------------------------------------------------ #
    _HISTORY_MAX = 20   # keep at most this many entries on disk

    def _save_history_entry(self, bat_path: str, out_dir: str, icon: str,
                             onefile: bool, console: bool, out_name: str,
                             result_path: str):
        """Write one JSON file to _HISTORY_DIR describing this conversion."""
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:20]
        data = {
            "ts":          datetime.now().isoformat(timespec="seconds"),
            "bat_path":    bat_path,
            "out_dir":     out_dir,
            "icon_path":   icon,
            "onefile":     onefile,
            "console":     console,
            "out_name":    out_name,
            "result_path": result_path,
        }
        fpath = os.path.join(_HISTORY_DIR, f"{ts}.json")
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            _log.info("Historia zapisana: %s", fpath)
        except Exception as exc:
            _log.warning("Nie można zapisać historii: %s", exc)
        # Prune oldest entries beyond max
        try:
            entries = sorted(
                [os.path.join(_HISTORY_DIR, fn) for fn in os.listdir(_HISTORY_DIR)
                 if fn.endswith(".json")]
            )
            for old in entries[:-self._HISTORY_MAX]:
                os.remove(old)
        except Exception:
            pass

    def _load_history(self) -> list:
        """Return list of history dicts, newest first."""
        entries = []
        try:
            for fn in sorted(os.listdir(_HISTORY_DIR), reverse=True):
                if not fn.endswith(".json"):
                    continue
                fpath = os.path.join(_HISTORY_DIR, fn)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        entries.append(json.load(f))
                except Exception:
                    pass
        except Exception:
            pass
        return entries[:self._HISTORY_MAX]

    def _clear_history(self):
        """Delete all history JSON files."""
        try:
            for fn in os.listdir(_HISTORY_DIR):
                if fn.endswith(".json"):
                    os.remove(os.path.join(_HISTORY_DIR, fn))
            _log.info("Historia wyczyszczona.")
        except Exception as exc:
            _log.warning("Błąd czyszczenia historii: %s", exc)

    def _load_history_entry(self, entry: dict):
        """Populate all input fields from a history dict."""
        self.update_entry(self.entry_bat,     entry.get("bat_path",  ""))
        self.update_entry(self.entry_icon,    entry.get("icon_path", ""))
        self.update_entry(self.entry_output,  entry.get("out_dir",   ""))
        self.update_entry(self.entry_outname, entry.get("out_name",  ""))
        if hasattr(self, "onefile_var"):
            self.onefile_var.set(entry.get("onefile", True))
        if hasattr(self, "console_var"):
            self.console_var.set(entry.get("console", True))
        ip = entry.get("icon_path", "")
        if ip and os.path.isfile(ip):
            self._current_icon_path = ip
            self.after(50, self._draw_header)
        bat = entry.get("bat_path", "")
        if bat and os.path.isfile(bat):
            self.after(80, lambda: self._preview_bat(bat))

    def show_history(self):
        """Open (or re-focus) the history popup window."""
        # Close existing popup if already open
        if self._history_popup and self._history_popup.winfo_exists():
            self._history_popup.focus_force()
            return

        p       = PALETTES[self.current_mode]
        is_dark = self.current_mode == "dark"
        entries = self._load_history()

        win = ctk.CTkToplevel(self)
        win.title(self.t("history_title"))
        win.geometry("560x420")
        win.resizable(True, True)
        win.grab_set()
        self._history_popup = win
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(),
                                                   setattr(self, "_history_popup", None)))

        # ── Header ──────────────────────────────────────────────────────
        hdr = Canvas(win, height=46, bd=0, highlightthickness=0)
        hdr.pack(fill="x")
        def _draw_hdr(event=None):
            hw = hdr.winfo_width() or 560
            base = make_gradient_image(hw, 46, p["header_top"], p["header_bot"])
            hdr._bg = ImageTk.PhotoImage(base.convert("RGB"))
            hdr.delete("all")
            hdr.create_image(0, 0, anchor="nw", image=hdr._bg)
            hdr.create_text(16, 23, text="🕐  " + self.t("history_title"),
                fill="#ddeeff" if is_dark else "#0a1e40",
                font=("Segoe UI", 12, "bold"), anchor="w")
        win.after(40, _draw_hdr)
        hdr.bind("<Configure>", _draw_hdr)

        # ── Scrollable list ──────────────────────────────────────────────
        list_frame = ctk.CTkScrollableFrame(
            win, fg_color=p["main"],
            scrollbar_button_color=p["btn_misc"],
            scrollbar_button_hover_color=p["btn_misc_h"],
        )
        list_frame.pack(fill="both", expand=True, padx=0, pady=0)

        if not entries:
            ctk.CTkLabel(
                list_frame, text=self.t("history_empty"),
                font=ctk.CTkFont(size=12), text_color=p["text_dim"],
            ).pack(pady=30)
        else:
            for i, entry in enumerate(entries):
                self._make_history_row(list_frame, entry, i, p, is_dark, win)

        # ── Footer ───────────────────────────────────────────────────────
        foot = ctk.CTkFrame(win, fg_color=p["header_bot"], height=44, corner_radius=0)
        foot.pack(fill="x", side="bottom")
        foot.pack_propagate(False)

        def _do_clear():
            self._clear_history()
            win.destroy()
            self._history_popup = None

        ctk.CTkButton(
            foot, text=self.t("history_clear"), width=130, height=28,
            fg_color="#c0392b", hover_color="#922b21",
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8, command=_do_clear,
        ).place(relx=0.25, rely=0.5, anchor="center")

        ctk.CTkButton(
            foot,
            text="Close" if self.current_lang == "en" else "Zamknij",
            width=120, height=28, corner_radius=8,
            fg_color=p["accent"], hover_color=p["btn_misc_h"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: (win.destroy(), setattr(self, "_history_popup", None)),
        ).place(relx=0.75, rely=0.5, anchor="center")

    def _make_history_row(self, parent, entry, idx, p, is_dark, win):
        """Build one card row in the history list."""
        card = ctk.CTkFrame(
            parent, corner_radius=8,
            fg_color=p["input_card"],
            border_width=1, border_color=p["input_card2"],
        )
        card.pack(fill="x", padx=10, pady=4)

        bat_name = os.path.basename(entry.get("bat_path", "?"))
        ts       = entry.get("ts", "")[:16].replace("T", "  ")
        out_name = entry.get("out_name", "") or os.path.splitext(bat_name)[0] + ".exe"
        mode_tag = "onefile" if entry.get("onefile") else "folder"

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(
            top, text=f"📄  {bat_name}  →  {out_name}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=p["text_primary"], anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=f"[{mode_tag}]",
            font=ctk.CTkFont(size=10),
            text_color=p["text_dim"], anchor="e",
        ).pack(side="right")

        bot = ctk.CTkFrame(card, fg_color="transparent")
        bot.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(
            bot, text=f"🕐 {ts}    📁 {entry.get('out_dir', '')}",
            font=ctk.CTkFont(size=10), text_color=p["text_label"], anchor="w",
        ).pack(side="left")

        def _load(e=entry, w=win):
            self._load_history_entry(e)
            w.destroy()
            self._history_popup = None

        ctk.CTkButton(
            bot, text=self.t("history_load"), width=70, height=24,
            fg_color=p["accent"], hover_color=p["btn_misc_h"],
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=6, command=_load,
        ).pack(side="right")

    # ------------------------------------------------------------------ #
    # BAT PREVIEW
    # ------------------------------------------------------------------ #
    def _preview_bat(self, path: str):
        """Load the contents of a .bat file into the preview textbox."""
        if not hasattr(self, "bat_preview"):
            return
        self.bat_preview.configure(state="normal")
        self.bat_preview.delete("1.0", "end")
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(4096)   # cap at 4 KB for safety
            self.bat_preview.insert("end", content)
        except Exception as exc:
            self.bat_preview.insert("end", f"[Cannot read file: {exc}]")
        self.bat_preview.configure(state="disabled")

    # ------------------------------------------------------------------ #
    # PROGRESS BAR  (thread-safe)
    # ------------------------------------------------------------------ #
    def _progress_start(self):
        """Show and animate the progress bar (call from main thread via after)."""
        def _do():
            self.progress_bar.pack(fill="x", padx=15, pady=(0, 4))
            self.progress_bar.start()
        self.after(0, _do)

    def _progress_stop(self, success: bool):
        """Stop and hide the progress bar; flash green or red."""
        def _do():
            self.progress_bar.stop()
            color = "#2ecc71" if success else "#e74c3c"
            self.progress_bar.configure(progress_color=color)
            # reset to indeterminate blue after a short delay
            self.after(1200, lambda: (
                self.progress_bar.configure(progress_color=PALETTES[self.current_mode]["accent"]),
                self.progress_bar.pack_forget(),
            ))
        self.after(0, _do)


    def save_settings(self):
        # Zapisz bieżący rozmiar i pozycję okna
        try:
            win_geometry = self.geometry()
        except Exception:
            win_geometry = ""
        data = {
            "lang":        self.current_lang,
            "mode":        self.current_mode,
            "onefile":     self.onefile_var.get()    if hasattr(self, "onefile_var")   else True,
            "console":     self.console_var.get()    if hasattr(self, "console_var")   else True,
            "lock_size":   self.lock_size_var.get()  if hasattr(self, "lock_size_var") else False,
            "bat_path":    self.entry_bat.get()      if hasattr(self, "entry_bat")     else "",
            "icon_path":   self.entry_icon.get()     if hasattr(self, "entry_icon")    else "",
            "output_dir":  self.entry_output.get()   if hasattr(self, "entry_output")  else "",
            "out_name":    self.entry_outname.get()  if hasattr(self, "entry_outname") else "",
            "window_geometry": win_geometry,
            "saved_at":    datetime.now().isoformat(timespec="seconds"),
        }
        try:
            with open(_JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            _log.info("Ustawienia zapisane do: %s", _JSON_FILE)
        except Exception as exc:
            _log.error("Błąd zapisu ustawień: %s", exc)

    def load_settings(self):
        if not os.path.isfile(_JSON_FILE):
            _log.info("Brak pliku ustawień – używam domyślnych.")
            return
        try:
            with open(_JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.current_lang = data.get("lang", "en")
            mode = data.get("mode", "dark")
            if mode != self.current_mode:
                self.current_mode = mode
                ctk.set_appearance_mode(mode)
                self._apply_palette()
            if hasattr(self, "onefile_var"):
                self.onefile_var.set(data.get("onefile", True))
            if hasattr(self, "console_var"):
                self.console_var.set(data.get("console", True))
            if hasattr(self, "lock_size_var"):
                self.lock_size_var.set(data.get("lock_size", False))
                self.toggle_size_lock()
            if hasattr(self, "entry_bat"):
                self.update_entry(self.entry_bat,    data.get("bat_path",   ""))
            if hasattr(self, "entry_icon"):
                ip = data.get("icon_path",  "")
                self.update_entry(self.entry_icon, ip)
                if ip and os.path.isfile(ip):
                    self._current_icon_path = ip
            if hasattr(self, "entry_output"):
                self.update_entry(self.entry_output, data.get("output_dir", ""))
            if hasattr(self, "entry_outname"):
                self.update_entry(self.entry_outname, data.get("out_name", ""))
            # Wczytaj rozmiar i pozycję okna (tylko gdy lock_size jest wyłączony)
            saved_geo = data.get("window_geometry", "")
            if saved_geo and not data.get("lock_size", False):
                try:
                    self.geometry(saved_geo)
                except Exception:
                    pass
            _log.info("Ustawienia wczytane z: %s", _JSON_FILE)
        except Exception as exc:
            _log.error("Błąd wczytywania ustawień: %s", exc)

    def _on_close(self):
        self.save_settings()
        if hasattr(self, '_anim_job') and self._anim_job:
            try: self.after_cancel(self._anim_job)
            except Exception: pass
        _log.info("Aplikacja zamknięta.")
        self.destroy()

    # ------------------------------------------------------------------ #
    # LANGUAGE
    # ------------------------------------------------------------------ #
    def t(self, key):
        return TRANSLATIONS[self.current_lang].get(key, key)

    def toggle_lang(self):
        self.current_lang = "pl" if self.current_lang == "en" else "en"
        self.apply_lang()

    def show_help(self):
        """Styled Help window with scrollable content."""
        win = ctk.CTkToplevel(self)
        win.title(self.t("help_title"))
        win.geometry("480x520")
        win.resizable(False, False)
        win.grab_set()
        p       = PALETTES[self.current_mode]
        is_dark = self.current_mode == "dark"

        # Header strip
        hdr = Canvas(win, height=54, bd=0, highlightthickness=0)
        hdr.pack(fill="x")

        def _draw_hdr(event=None):
            hw = hdr.winfo_width() or 480
            base = make_gradient_image(hw, 54, p["header_top"], p["header_bot"])
            ed   = ImageDraw.Draw(base)
            ed.line([(0,0),(hw,0)],   fill=(120,170,230,140) if is_dark else (80,130,190,100), width=1)
            ed.line([(0,53),(hw,53)], fill=(5,8,20,120)      if is_dark else (100,140,180,80),  width=1)
            hdr._bg = ImageTk.PhotoImage(base.convert("RGB"))
            hdr.delete("all")
            hdr.create_image(0, 0, anchor="nw", image=hdr._bg)
            # icon
            try:
                _ico_path = _APP_ICON
                if _ico_path:
                    ico = Image.open(_ico_path).convert("RGBA").resize((32,32), Image.LANCZOS)
                    tg  = ico.copy().filter(ImageFilter.GaussianBlur(3))
                    hdr._tg  = ImageTk.PhotoImage(tg)
                    hdr._ico = ImageTk.PhotoImage(ico)
                    hdr.create_image(28, 27, anchor="center", image=hdr._tg)
                    hdr.create_image(28, 27, anchor="center", image=hdr._ico)
                else:
                    raise FileNotFoundError
            except Exception:
                hdr.create_text(28, 27, text="?", fill="#4488ff",
                                font=("Segoe UI", 18, "bold"), anchor="center")
            # title
            title = self.t("help_title") + "  —  BAT → EXE Converter"
            hdr.create_text(58, 29, text=title,
                fill="#ddeeff" if is_dark else "#1a3560",
                font=("Segoe UI", 13, "bold"), anchor="w")
        win.after(40, _draw_hdr)
        hdr.bind("<Configure>", _draw_hdr)

        # Scrollable text body
        body = ctk.CTkTextbox(
            win, font=("Consolas", 10),
            fg_color=p["input_card"], text_color="#c8deff" if is_dark else "#1a2d50",
            border_width=0, corner_radius=0, wrap="word",
            scrollbar_button_color=p["btn_misc"],
            scrollbar_button_hover_color=p["btn_misc_h"],
        )
        body.pack(fill="both", expand=True, padx=0, pady=0)
        body.insert("end", self.t("help_msg"))
        body.configure(state="disabled")

        # Footer close button
        foot = ctk.CTkFrame(win, fg_color=p["header_bot"], height=44, corner_radius=0)
        foot.pack(fill="x", side="bottom")
        foot.pack_propagate(False)
        ctk.CTkButton(
            foot,
            text="Close" if self.current_lang == "en" else "Zamknij",
            width=120, height=30, corner_radius=8,
            fg_color=p["accent"], hover_color=p["btn_misc_h"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=win.destroy
        ).place(relx=0.5, rely=0.5, anchor="center")


    def open_page(self):
        """Open the product HTML page in the default browser."""
        html_path = os.path.join(_SCRIPT_DIR, "BAT-2-EXE_Converter_EN.html")
        if os.path.isfile(html_path):
            webbrowser.open(f"file:///{html_path.replace(os.sep, '/')}")
        else:
            messagebox.showinfo(
                "Page not found",
                f"HTML page not found:\n{html_path}\n\nMake sure BAT-2-EXE_Converter_EN.html is in the same folder as this script."
            )

    def show_log(self):
        """Styled Log viewer - reads and parses bat2exe.log."""
        win = ctk.CTkToplevel(self)
        win.title("LOG  --  BAT to EXE Converter")
        win.geometry("660x540")
        win.resizable(True, True)
        win.grab_set()
        p       = PALETTES[self.current_mode]
        is_dark = self.current_mode == "dark"

        # Header
        hdr = Canvas(win, height=52, bd=0, highlightthickness=0)
        hdr.pack(fill="x")
        def _draw_hdr(event=None):
            hw = hdr.winfo_width() or 660
            base = make_gradient_image(hw, 52, p["header_top"], p["header_bot"])
            ed = ImageDraw.Draw(base)
            ed.line([(0,0),(hw,0)],   fill=(120,170,230,140) if is_dark else (80,130,190,100), width=1)
            ed.line([(0,51),(hw,51)], fill=(5,8,20,120)      if is_dark else (100,140,180,80),  width=1)
            hdr._bg = ImageTk.PhotoImage(base.convert("RGB"))
            hdr.delete("all")
            hdr.create_image(0, 0, anchor="nw", image=hdr._bg)
            try:
                _ico_path2 = _APP_ICON
                if _ico_path2:
                    ico = Image.open(_ico_path2).convert("RGBA").resize((28,28), Image.LANCZOS)
                    tg  = ico.copy().filter(ImageFilter.GaussianBlur(2))
                    hdr._tg = ImageTk.PhotoImage(tg);  hdr._ic = ImageTk.PhotoImage(ico)
                    hdr.create_image(26, 26, anchor="center", image=hdr._tg)
                    hdr.create_image(26, 26, anchor="center", image=hdr._ic)
                else:
                    raise FileNotFoundError
            except Exception:
                hdr.create_text(26, 26, text="L", fill="#4488ff",
                                font=("Segoe UI", 14, "bold"), anchor="center")
            hdr.create_text(54, 26, text="Activity Log   " + _LOG_FILE,
                fill="#ddeeff" if is_dark else "#1a3560",
                font=("Segoe UI", 10, "bold"), anchor="w")
        win.after(40, _draw_hdr)
        hdr.bind("<Configure>", _draw_hdr)

        # Filter/stats bar
        bar = ctk.CTkFrame(win, fg_color=p["input_card"], corner_radius=0, height=34)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        lbl_count = ctk.CTkLabel(bar, text="", font=ctk.CTkFont(size=10),
                                  text_color=p["text_dim"], fg_color="transparent")
        lbl_count.pack(side="left", padx=12)

        def _refresh():
            log_box.configure(state="normal")
            log_box.delete("1.0", "end")
            if not os.path.isfile(_LOG_FILE):
                log_box.insert("end",
                    "Log file not found:\n" + _LOG_FILE + "\n\n"
                    "The file will be created after the first conversion.")
                lbl_count.configure(text="No log file")
                log_box.configure(state="disabled")
                return
            try:
                with open(_LOG_FILE, "r", encoding="utf-8", errors="replace") as fh:
                    log_lines = fh.readlines()
            except Exception as exc:
                log_box.insert("end", "Cannot read log: " + str(exc))
                log_box.configure(state="disabled")
                return

            # Parse conversion records
            conversions = []
            current = None
            for raw in log_lines:
                raw = raw.rstrip()
                if not raw:
                    continue
                ts = raw[:19] if len(raw) >= 19 else ""
                if "Rozpocz" in raw and "konwersji" in raw:
                    bat = ""
                    if "bat=" in raw:
                        bat = raw.split("bat=")[1].split(",")[0].strip()
                    current = {"ts": ts, "bat": bat, "status": "?", "out": ""}
                elif current and "sukcesem" in raw:
                    out = raw.split("sukcesem:")[-1].strip() if "sukcesem:" in raw else ""
                    current["status"] = "OK"; current["out"] = out
                    conversions.append(current); current = None
                elif current and ("nieudana" in raw or "Krytyczny" in raw):
                    current["status"] = "FAIL"
                    conversions.append(current); current = None

            if not conversions:
                log_box.insert("end",
                    "No conversion records found yet.\n\n"
                    "Log file: " + _LOG_FILE + "\n\n"
                    "Run a conversion and come back here to see history.")
                lbl_count.configure(text="0 conversions")
            else:
                ok_cnt   = sum(1 for c in conversions if c["status"] == "OK")
                fail_cnt = len(conversions) - ok_cnt
                lbl_count.configure(
                    text=str(len(conversions)) + " conversion(s)   "
                         + str(ok_cnt) + " OK   "
                         + str(fail_cnt) + " failed")
                log_box.insert("end", "Log file: " + _LOG_FILE + "\n")
                log_box.insert("end", "-" * 72 + "\n\n")
                for c in reversed(conversions):
                    ts_str  = c["ts"] if c["ts"] else "unknown time"
                    bat_str = os.path.basename(c["bat"]) if c["bat"] else "(unknown)"
                    marker  = "[OK]  " if c["status"] == "OK" else "[FAIL]"
                    log_box.insert("end", "  " + marker + "  " + ts_str + "   " + bat_str + "\n")
                    if c["out"]:
                        log_box.insert("end", "         -> " + c["out"] + "\n")
                    log_box.insert("end", "\n")
            log_box.configure(state="disabled")
            log_box.see("1.0")

        def _open_raw():
            if not os.path.isfile(_LOG_FILE):
                return
            try:
                # os.startfile exists only on Windows
                if hasattr(os, "startfile"):
                    os.startfile(_LOG_FILE)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", _LOG_FILE])
                else:
                    # Linux / other POSIX
                    subprocess.Popen(["xdg-open", _LOG_FILE])
            except Exception as _e:
                _log.warning("Cannot open log file in system viewer: %s", _e)

        ctk.CTkButton(bar, text="Refresh", width=76, height=24,
                      fg_color=p["btn_misc"], hover_color=p["btn_misc_h"],
                      font=ctk.CTkFont(size=10), corner_radius=5,
                      command=_refresh).pack(side="right", padx=8, pady=5)
        ctk.CTkButton(bar, text="Open raw log", width=96, height=24,
                      fg_color=p["btn_misc"], hover_color=p["btn_misc_h"],
                      font=ctk.CTkFont(size=10), corner_radius=5,
                      command=_open_raw).pack(side="right", padx=(0,4), pady=5)

        # Log textbox
        log_box = ctk.CTkTextbox(
            win, font=("Consolas", 10),
            fg_color=p["input_card"], text_color="#c8deff" if is_dark else "#1a2d50",
            border_width=0, corner_radius=0, wrap="none",
            scrollbar_button_color=p["btn_misc"],
            scrollbar_button_hover_color=p["btn_misc_h"],
        )
        log_box.pack(fill="both", expand=True)

        # Footer
        foot = ctk.CTkFrame(win, fg_color=p["header_bot"], height=42, corner_radius=0)
        foot.pack(fill="x", side="bottom")
        foot.pack_propagate(False)
        ctk.CTkButton(foot,
            text="Close" if self.current_lang == "en" else "Zamknij",
            width=110, height=28, corner_radius=8,
            fg_color=p["accent"], hover_color=p["btn_misc_h"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=win.destroy).place(relx=0.5, rely=0.5, anchor="center")

        _refresh()

    def show_about(self):
        """Clean modern About window."""
        win = ctk.CTkToplevel(self)
        win.title(self.t("about_title"))
        win.geometry("400x514")
        win.resizable(False, False)
        win.grab_set()
        p       = PALETTES[self.current_mode]
        is_dark = self.current_mode == "dark"

        bg = Canvas(win, bd=0, highlightthickness=0)
        bg.pack(fill="both", expand=True)

        def _draw(event=None):
            bw = bg.winfo_width()  or 400
            bh = bg.winfo_height() or 514
            bg.delete("all")

            # ── Background: two-tone gradient ──────────────────────────────
            top_c  = "#0f1624" if is_dark else "#e8f2ff"
            bot_c  = "#0d1520" if is_dark else "#ccdff5"
            base   = make_gradient_image(bw, bh, top_c, bot_c)

            # Subtle dot-grid texture overlay
            dot_layer = Image.new("RGBA", (bw, bh), (0,0,0,0))
            dl = ImageDraw.Draw(dot_layer)
            dot_col = (80,120,200,18) if is_dark else (60,100,180,12)
            for gx in range(0, bw, 18):
                for gy in range(0, bh, 18):
                    dl.ellipse([gx-1, gy-1, gx+1, gy+1], fill=dot_col)
            base = _paste_rgba(base, dot_layer, 0, 0)

            # Accent gradient band at top
            # FIX: ImageDraw.Draw() was re-created on every loop iteration —
            # moved outside so we create exactly one Draw object per redraw.
            accent_h = 6
            dl2 = ImageDraw.Draw(base)
            for ax in range(bw):
                t   = ax / max(bw - 1, 1)
                r   = int(0x3a + (0x00 - 0x3a) * t)
                g   = int(0x7b + (0xcc - 0x7b) * t)
                b_c = int(0xd5 + (0xff - 0xd5) * t)
                dl2.line([(ax, 0), (ax, accent_h)], fill=(r, g, b_c, 255), width=1)

            # Thin line under accent band
            dl2.line([(0, accent_h), (bw, accent_h)],
                     fill=(20, 30, 50, 180) if is_dark else (150, 180, 220, 120), width=1)

            bg._base = ImageTk.PhotoImage(base.convert("RGB"))
            bg.create_image(0, 0, anchor="nw", image=bg._base)

            # ── Circular logo area ─────────────────────────────────────────
            cx, cy_logo = bw//2, 90
            ring_r = 52

            # Outer glow ring
            glow = _glow_circle(ring_r*2+28, "#3a7bd5" if is_dark else "#6699dd", blur=18)
            bg._glow = ImageTk.PhotoImage(glow)
            bg.create_image(cx, cy_logo, anchor="center", image=bg._glow)

            # Circle with gradient fill (PIL)
            circ = Image.new("RGBA", (ring_r*2, ring_r*2), (0,0,0,0))
            cd   = ImageDraw.Draw(circ)
            # radial-ish: dark bottom, lighter top
            for cy2 in range(ring_r*2):
                t2  = cy2 / (ring_r*2)
                if is_dark:
                    rc = int(0x1a + (0x0d-0x1a)*t2)
                    gc = int(0x28 + (0x18-0x28)*t2)
                    bc = int(0x50 + (0x30-0x50)*t2)
                else:
                    rc = int(0xe8 + (0xd0-0xe8)*t2)
                    gc = int(0xf0 + (0xe0-0xf0)*t2)
                    bc = int(0xff + (0xf0-0xff)*t2)
                # clip to circle
                half = ring_r
                dx   = int((half**2 - (cy2-half)**2)**0.5) if abs(cy2-half) <= half else 0
                if dx > 0:
                    cd.line([(half-dx, cy2),(half+dx, cy2)], fill=(rc,gc,bc,230), width=1)
            # highlight arc top-left
            cd.arc([6,6,ring_r*2-7,ring_r*2-7], start=200, end=320,
                   fill=(220,240,255,100) if is_dark else (255,255,255,160), width=3)
            # shadow arc bottom-right
            cd.arc([6,6,ring_r*2-7,ring_r*2-7], start=20, end=140,
                   fill=(0,5,15,80) if is_dark else (100,130,170,60), width=2)
            circ = circ.filter(ImageFilter.GaussianBlur(0.8))
            bg._circ = ImageTk.PhotoImage(circ)
            bg.create_image(cx, cy_logo, anchor="center", image=bg._circ)

            # Logo icon
            try:
                _ico_path3 = _APP_ICON
                if not _ico_path3:
                    raise FileNotFoundError
                raw = Image.open(_ico_path3).convert("RGBA")
                ico = raw.resize((ring_r*2-22, ring_r*2-22), Image.LANCZOS)
                tg  = ico.copy().filter(ImageFilter.GaussianBlur(3))
                bg._ico_tg = ImageTk.PhotoImage(tg)
                bg._ico    = ImageTk.PhotoImage(ico)
                bg.create_image(cx, cy_logo, anchor="center", image=bg._ico_tg)
                bg.create_image(cx, cy_logo, anchor="center", image=bg._ico)
            except Exception:
                bg.create_text(cx, cy_logo, text="⚙", fill="#4488ff",
                               font=("Segoe UI", 34, "bold"), anchor="center")

            # Version badge (small pill)
            badge_w, badge_h2 = 56, 18
            bx1 = cx + ring_r - badge_w//2 - 2
            by1 = cy_logo + ring_r - badge_h2//2 - 2
            badge = Image.new("RGBA", (badge_w, badge_h2), (0,0,0,0))
            bd    = ImageDraw.Draw(badge)
            bd.rounded_rectangle([0,0,badge_w-1,badge_h2-1], radius=9,
                                  fill=(0x3a,0x7b,0xd5,220))
            bg._badge = ImageTk.PhotoImage(badge)
            bg.create_image(bx1+badge_w//2, by1+badge_h2//2, anchor="center", image=bg._badge)
            bg.create_text(bx1+badge_w//2, by1+badge_h2//2, text="v 2026",
                fill="white", font=("Segoe UI", 7, "bold"), anchor="center")

            # ── App name ───────────────────────────────────────────────────
            ny = cy_logo + ring_r + 20
            bg.create_text(cx, ny+1, text="BAT → EXE Converter",
                fill="#000a18", font=("Segoe UI", 16, "bold"), anchor="center")
            bg.create_text(cx, ny, text="BAT → EXE Converter",
                fill="#e8f4ff" if is_dark else "#0d2550", font=("Segoe UI", 16, "bold"), anchor="center")

            # Tagline
            bg.create_text(cx, ny+22, text="Batch to Executable • Powered by PyInstaller",
                fill="#6688bb" if is_dark else "#4466aa", font=("Segoe UI", 9), anchor="center")

            # ── Separator ──────────────────────────────────────────────────
            sep_y = ny + 42
            # gradient line
            sep_img = Image.new("RGBA", (bw-80, 1), (0,0,0,0))
            for sx in range(bw-80):
                t3 = abs(sx - (bw-80)//2) / ((bw-80)//2)
                sa = int(130 * (1 - t3**2))
                col3 = (80,130,210,sa) if is_dark else (60,100,180,sa)
                sep_img.putpixel((sx,0), col3)
            bg._sep = ImageTk.PhotoImage(sep_img)
            bg.create_image(40, sep_y, anchor="nw", image=bg._sep)

            # ── Info rows ──────────────────────────────────────────────────
            rows = [
                ("👤", "Author",   "Sebastian Januchowski"),
                ("🏢", "Company",  "polsoft.ITS™"),
                ("©",     "Year",     "2026"),
                ("💻", "Built with","Python 3  +  CustomTkinter  +  Pillow"),
                ("🔒", "License",  "All rights reserved"),
            ]
            label_col = "#8899bb" if is_dark else "#5577aa"
            value_col = "#c8dcff" if is_dark else "#0d2040"
            ry = sep_y + 14
            for icon_ch, label, value in rows:
                # icon circle bg
                ic_r = 13
                ic_img = Image.new("RGBA", (ic_r*2, ic_r*2), (0,0,0,0))
                ic_d   = ImageDraw.Draw(ic_img)
                ic_d.ellipse([0,0,ic_r*2-1,ic_r*2-1],
                             fill=(0x2a,0x40,0x70,120) if is_dark else (0xb8,0xd0,0xee,140))
                setattr(bg, f'_ic_{ry}', ImageTk.PhotoImage(ic_img))
                bg.create_image(32, ry, anchor="center", image=getattr(bg, f'_ic_{ry}'))
                bg.create_text(32, ry, text=icon_ch, fill="#7aabff" if is_dark else "#3366bb",
                               font=("Segoe UI", 9), anchor="center")
                bg.create_text(58, ry, text=label, fill=label_col,
                               font=("Segoe UI", 9), anchor="w")
                bg.create_text(130, ry, text=value, fill=value_col,
                               font=("Segoe UI", 9, "bold"), anchor="w")
                ry += 22

            # ── Close button — created once, repositioned on resize ─────────
            if not hasattr(win, "_close_btn"):
                win._close_btn = ctk.CTkButton(
                    win,
                    text="Close" if self.current_lang == "en" else "Zamknij",
                    width=130, height=32, corner_radius=10,
                    fg_color="#3a7bd5", hover_color="#2a5baa",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    command=win.destroy
                )
            bg.create_window(bw//2, bh-22, window=win._close_btn)

        win.after(60, _draw)
        bg.bind("<Configure>", _draw)

    def apply_lang(self):
        self.title(self.t("title"))
        self.header_title_label.configure(text=self.t("header_title"))
        self.label_bat.configure(text=self.t("label_bat"))
        self.label_icon.configure(text=self.t("label_icon"))
        self.label_output.configure(text=self.t("label_output"))
        self.label_outname.configure(text=self.t("label_outname"))
        self.label_preview.configure(text=self.t("label_preview"))
        self.btn_history.configure(text=self.t("btn_history"))
        self.entry_outname.configure(placeholder_text=self.t("hint_outname"))
        self.cb_onefile.configure(text=self.t("opt_onefile"))
        self.cb_console.configure(text=self.t("opt_console"))
        self.cb_lock.configure(text=self.t("opt_lock"))
        self.cb_topmost.configure(text=self.t("opt_topmost"))
        self.btn_compile.configure(text=self.t("btn_compile"))
        self.lang_btn.configure(text=self.t("lang_btn"))
        current_status = self.status_label.cget("text")
        for lang in TRANSLATIONS.values():
            if current_status == lang["status_ready"]:
                self.status_label.configure(text=self.t("status_ready"))
                break

    # ------------------------------------------------------------------ #
    # GUI SETUP
    # ------------------------------------------------------------------ #
    def setup_ui(self):
        p = PALETTES[self.current_mode]

        # ── HEADER (Canvas gradient + centered icon + title) ────────────
        self.header_canvas = Canvas(
            self, height=110, bd=0, highlightthickness=0, relief="flat"
        )
        self.header_canvas.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self._draw_header()

        # ── MAIN FRAME ──────────────────────────────────────────────────
        main_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=p["main"],
                                   border_width=1, border_color=p.get("aero_border", p["input_card2"]))
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))
        self._themed[main_frame] = "main"

        self.entry_bat,    self.label_bat    = self.create_input_group(main_frame, "", self.browse_file)
        self.entry_icon,   self.label_icon   = self.create_input_group(main_frame, "", self.browse_icon)
        # Register labels so _apply_palette keeps their text_color up-to-date
        self._themed[self.label_bat]    = "label"
        self._themed[self.label_icon]   = "label"
        # Update header when icon path changes
        def _on_icon_change(*_):
            p = self.entry_icon.get().strip()
            ext = os.path.splitext(p)[1].lower()
            if ext in (".ico", ".png", ".jpg", ".jpeg") and os.path.isfile(p):
                self._current_icon_path = p
                self.after(50, self._draw_header)
        self.entry_icon.bind("<FocusOut>", _on_icon_change)
        self.entry_icon.bind("<Return>",   _on_icon_change)
        self.entry_output, self.label_output = self.create_input_group(main_frame, "", self.browse_output)
        self._themed[self.label_output] = "label"

        # ── History button (sits just below the BAT entry card) ─────────
        hist_bar = ctk.CTkFrame(main_frame, fg_color="transparent")
        hist_bar.pack(fill="x", padx=14, pady=(0, 2))
        self.btn_history = ctk.CTkButton(
            hist_bar, text=self.t("btn_history"),
            width=110, height=24,
            fg_color=p["btn_misc"], hover_color=p["btn_misc_h"],
            text_color=p["text_primary"],
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=6, border_width=1, border_color=p["input_card2"],
            command=self.show_history,
        )
        self.btn_history.pack(side="right")
        self._themed[self.btn_history] = "btn_misc"

        # ── BAT preview ─────────────────────────────────────────────────
        preview_card = ctk.CTkFrame(main_frame, corner_radius=8,
                                    fg_color=p["input_card"],
                                    border_width=1, border_color=p["input_card2"])
        preview_card.pack(fill="x", padx=10, pady=(0, 3))
        self._themed[preview_card] = "input_card"

        self.label_preview = ctk.CTkLabel(
            preview_card, text=self.t("label_preview"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=p["text_label"],
        )
        self.label_preview.pack(anchor="w", padx=10, pady=(5, 0))
        self._themed[self.label_preview] = "label"

        self.bat_preview = ctk.CTkTextbox(
            preview_card, height=72, font=("Consolas", 10),
            fg_color=p["input_card"], text_color=p["text_entry"],
            border_width=0, corner_radius=0, wrap="none", state="disabled",
            scrollbar_button_color=p["btn_misc"],
            scrollbar_button_hover_color=p["btn_misc_h"],
        )
        self.bat_preview.pack(fill="x", padx=8, pady=(2, 6))

        # ── Custom output name ──────────────────────────────────────────
        self.entry_outname, self.label_outname = self.create_input_group(
            main_frame, "", lambda: None)
        self._themed[self.label_outname] = "label"
        # The browse button is irrelevant here — hide it by overriding with a hint label
        # (create_input_group already built the layout; we just repurpose the entry)
        self.entry_outname.configure(
            placeholder_text=self.t("hint_outname"),
        )

        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=10, pady=5)

        self.onefile_var = ctk.BooleanVar(value=True)
        self.console_var = ctk.BooleanVar(value=True)

        self.cb_onefile = ctk.CTkCheckBox(
            options_frame, text="", variable=self.onefile_var,
            font=ctk.CTkFont(size=12, weight="bold"),    # was size=11, no bold
            text_color=p["text_primary"],
        )
        self.cb_onefile.pack(side="left", padx=10)

        self.cb_console = ctk.CTkCheckBox(
            options_frame, text="", variable=self.console_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=p["text_primary"],
        )
        self.cb_console.pack(side="left", padx=10)

        self.cb_lock = ctk.CTkCheckBox(
            options_frame, text="",
            variable=self.lock_size_var,
            command=self.toggle_size_lock,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=p["text_primary"],
            fg_color="#e74c3c", hover_color="#c0392b"
        )
        self.cb_lock.pack(side="left", padx=10)

        self.cb_topmost = ctk.CTkCheckBox(
            options_frame, text="",
            variable=self.topmost_var,
            command=self.toggle_topmost,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=p["text_primary"],
            fg_color="#e67e22", hover_color="#d35400"
        )
        self.cb_topmost.pack(side="left", padx=10)

        # 3D-style compile button
        self.btn_compile = ctk.CTkButton(
            main_frame, text="", height=36,
            fg_color="#27ae60", hover_color="#1e8449",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8,
            border_width=2, border_color="#1a6b38",
            command=self.start_conversion
        )
        self.btn_compile.pack(fill="x", padx=15, pady=10)

        # ── Progress bar (indeterminate, shown only during conversion) ───
        self.progress_bar = ctk.CTkProgressBar(
            main_frame, mode="indeterminate",
            height=8, corner_radius=4,
            fg_color=p["input_card2"],
            progress_color=p["accent"],
        )
        # Not packed here — shown/hidden by _progress_start / _progress_stop

        self.log_box = ctk.CTkTextbox(
            main_frame, height=140, font=("Consolas", 11),          # was 10
            text_color=p["text_entry"],                              # was: default
            corner_radius=8, border_width=1, border_color=p["input_card2"],
            fg_color=p["input_card"]
        )
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self._themed[self.log_box] = "log"

        # ── BOTTOM BAR ──────────────────────────────────────────────────
        self.bottom_canvas = Canvas(
            self, height=36, bd=0, highlightthickness=0, relief="flat"   # was 30
        )
        self.bottom_canvas.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self._draw_bottom()

    def _draw_header(self):
        """3D animated banner header — particle shimmer + sweep glow."""
        p       = PALETTES[self.current_mode]
        is_dark = self.current_mode == "dark"
        self.update_idletasks()
        w = self.header_canvas.winfo_width() or 520
        h = 96
        self.header_canvas.configure(height=h, bg=p["header_bot"])

        # ── Static background layers (PIL) ──────────────────────────────────
        # Rich Aero glass gradient - deep blue-black to midnight blue
        top_c = "#0a1428" if is_dark else "#d8eeff"
        bot_c = "#040810" if is_dark else "#a4c8ee"
        base  = make_gradient_image(w, h, top_c, bot_c)

        # Aero glass reflection band - bright stripe across upper third
        glass_h = h // 3
        glass = Image.new("RGBA", (w, glass_h), (0,0,0,0))
        gd2   = ImageDraw.Draw(glass)
        for gy in range(glass_h):
            ta2 = gy / max(glass_h-1, 1)
            a2  = int((28 if is_dark else 40) * (1 - ta2 * ta2))
            gd2.line([(0,gy),(w,gy)], fill=(180,210,255,a2) if is_dark else (255,255,255,a2), width=1)
        base = _paste_rgba(base, glass, 0, 0)

        # Diagonal gloss (top-left shimmer) - stronger Aero style
        gloss = Image.new("RGBA", (w, h), (0,0,0,0))
        gd    = ImageDraw.Draw(gloss)
        shine = 42 if is_dark else 24
        for i in range(min(w, h)):
            a = max(0, shine - int(i * shine / min(w, h)))
            gd.line([(0, i), (i, 0)], fill=(255,255,255,a), width=1)
        base = _paste_rgba(base, gloss, 0, 0)

        # Bottom-right counter-glow
        cr_glow = Image.new("RGBA", (w, h), (0,0,0,0))
        for i in range(min(w, h) // 2):
            a = max(0, 12 - int(i * 12 / (min(w,h)//2)))
            gd3 = ImageDraw.Draw(cr_glow)
            gd3.line([(w, h-i), (w-i, h)], fill=(60,120,220,a), width=1)
        base = _paste_rgba(base, cr_glow, 0, 0)

        # Top accent stripe (colourful thin gradient line)
        acc = Image.new("RGBA", (w, 4), (0,0,0,0))
        for ax in range(w):
            t  = ax / max(w-1, 1)
            ar = int(0x3a + (0x00-0x3a)*t)
            ag = int(0x7b + (0xaa-0x7b)*t)
            ab = int(0xd5 + (0xff-0xd5)*t)
            ImageDraw.Draw(acc).line([(ax,0),(ax,3)], fill=(ar,ag,ab,255), width=1)
        base = _paste_rgba(base, acc, 0, 0)

        # Aero glow — gradient fade at bottom blending into main panel
        for ay in range(20):
            ta   = ay / 19
            alph = int(60 * (1 - ta))
            if is_dark:
                col_a = (30, 80, 180, alph)
            else:
                col_a = (100, 160, 230, alph)
            ImageDraw.Draw(base).line([(0, h-1-ay),(w, h-1-ay)], fill=col_a, width=1)
        # Bottom hard shadow line
        ImageDraw.Draw(base).line([(0,h-1),(w,h-1)],
            fill=(2,6,16,220) if is_dark else (60,90,130,150), width=2)

        self._header_bg = ImageTk.PhotoImage(base.convert("RGB"))
        self.header_canvas.delete("all")
        self.header_canvas.create_image(0, 0, anchor="nw", image=self._header_bg)

        # ── Icon platform (3D plinth) ───────────────────────────────────────
        cx, cy_ico = w // 2, 52
        disc_r = 38

        # Large soft glow halo
        halo = _glow_circle(disc_r*2+36, "#3a7bd5" if is_dark else "#6699ee", blur=20)
        self._halo_ph = ImageTk.PhotoImage(halo)
        self.header_canvas.create_image(cx, cy_ico, anchor="center", image=self._halo_ph)

        # 3D circle: gradient-filled disc
        dsz = disc_r * 2
        disc = Image.new("RGBA", (dsz, dsz), (0,0,0,0))
        dd   = ImageDraw.Draw(disc)
        for dy in range(dsz):
            tt  = dy / dsz
            if is_dark:
                dr2 = int(0x22 + (0x0e-0x22)*tt)
                dg2 = int(0x32 + (0x1c-0x32)*tt)
                db2 = int(0x58 + (0x30-0x58)*tt)
            else:
                dr2 = int(0xd8 + (0xc0-0xd8)*tt)
                dg2 = int(0xe8 + (0xd4-0xe8)*tt)
                db2 = int(0xff + (0xee-0xff)*tt)
            half = disc_r
            dx2  = int((half**2 - (dy-half)**2)**0.5) if abs(dy-half) <= half else 0
            if dx2 > 0:
                dd.line([(half-dx2, dy),(half+dx2, dy)], fill=(dr2,dg2,db2,220), width=1)
        # rim highlight top-left
        dd.arc([4,4,dsz-5,dsz-5], start=200, end=320, fill=(210,230,255,130) if is_dark else (255,255,255,180), width=3)
        # rim shadow bottom-right
        dd.arc([4,4,dsz-5,dsz-5], start=20, end=140, fill=(0,4,12,100) if is_dark else (80,110,150,80), width=2)
        disc = disc.filter(ImageFilter.GaussianBlur(0.7))
        self._disc_ph = ImageTk.PhotoImage(disc)
        self.header_canvas.create_image(cx, cy_ico, anchor="center", image=self._disc_ph)

        # ── Logo ────────────────────────────────────────────────────────────
        icon_path = getattr(self, "_current_icon_path", None) or ""
        # Try user-selected icon first, then fallback candidates
        _fallbacks = ["icon.ico", "icon.png", "icon.jpg"]
        _icon_candidates = ([icon_path] if icon_path else []) + [f for f in _fallbacks if f != icon_path]
        _icon_loaded = False
        for _ic_path in _icon_candidates:
            try:
                raw    = Image.open(_ic_path).convert("RGBA")
                ico_sz = disc_r*2 - 14
                ico    = raw.resize((ico_sz, ico_sz), Image.LANCZOS)
                tg     = ico.copy().filter(ImageFilter.GaussianBlur(4))
                self._ico_tg = ImageTk.PhotoImage(tg)
                self._ico_ph = ImageTk.PhotoImage(ico)
                self.header_canvas.create_image(cx, cy_ico, anchor="center", image=self._ico_tg)
                self.header_canvas.create_image(cx, cy_ico, anchor="center", image=self._ico_ph)
                # specular glint
                spec = Image.new("RGBA", (16,10), (0,0,0,0))
                ImageDraw.Draw(spec).ellipse([0,0,15,9], fill=(255,255,255,90))
                spec = spec.filter(ImageFilter.GaussianBlur(2))
                self._spec_ph = ImageTk.PhotoImage(spec)
                self.header_canvas.create_image(cx-disc_r//3, cy_ico-disc_r//3,
                                                anchor="center", image=self._spec_ph)
                _icon_loaded = True
                break
            except Exception:
                pass
        if not _icon_loaded:
            for off,col,sz in [(2,"#001133",32),(1,"#2255aa",30),(0,"#4488ff",28)]:
                self.header_canvas.create_text(cx+off, cy_ico+off, text="⚙",
                    fill=col, font=("Segoe UI",sz,"bold"), anchor="center")

        # ── .BAT (lewo) i .EXE (prawo) – złoty mirror-gradient ────────────────
        # font size = ~36% of header height
        _lbl_sz   = max(10, int(h * 0.36))
        _side_pad = int(w * 0.045)    # odległość od krawędzi
        _cy_lbl   = h // 2 - 12       # trochę wyżej niż środek

        # .BAT – left side
        _bat_ph, _bat_w, _bat_h = _banner_gold_label(".BAT", _lbl_sz)
        self._bat_lbl_ph = _bat_ph
        _bat_x = _side_pad
        _bat_y = _cy_lbl - _bat_h // 2
        self.header_canvas.create_image(_bat_x, _bat_y, anchor="nw", image=self._bat_lbl_ph)

        # .EXE – right side
        _exe_ph, _exe_w, _exe_h = _banner_gold_label(".EXE", _lbl_sz)
        self._exe_lbl_ph = _exe_ph
        _exe_x = w - _side_pad - _exe_w - 4
        _exe_y = _cy_lbl - _exe_h // 2
        self.header_canvas.create_image(_exe_x, _exe_y, anchor="nw", image=self._exe_lbl_ph)

        # invisible label for apply_lang to update — tworzyć tylko raz
        if not hasattr(self, "header_title_label") or not self.header_title_label.winfo_exists():
            self.header_title_label = ctk.CTkLabel(self, text="")
            self.header_title_label.place_forget()

        # ── Start animation (particle shimmer + sweep glow) ─────────────────
        self._start_banner_animation(w, h, cx, cy_ico, disc_r, p, is_dark)

    def _start_banner_animation(self, w, h, cx, cy_ico, disc_r, p, is_dark):
        """Animate sweep glow + floating particles on the header canvas."""
        import math, random

        # Cancel previous animation if running
        if hasattr(self, '_anim_job') and self._anim_job:
            try: self.after_cancel(self._anim_job)
            except Exception: pass
        self._anim_job   = None
        self._anim_frame = 0

        # Particles: (x, y, speed, size, phase) — reinit lub reclamp po resize
        if not hasattr(self, '_particles') or len(self._particles) != 18:
            self._particles = [
                (random.uniform(20, w-20),
                 random.uniform(8, h-8),
                 random.uniform(0.3, 0.9),
                 random.uniform(1.5, 3.5),
                 random.uniform(0, 6.28))
                for _ in range(18)
            ]
        else:
            # Reclamp existing particle positions to new canvas dimensions
            self._particles = [
                (max(4, min(w-4, px)), max(4, min(h-4, py)), spd, sz, ph)
                for px, py, spd, sz, ph in self._particles
            ]

        sweep_col = "#5599ff" if is_dark else "#4477cc"
        part_col  = "#7ab0ff" if is_dark else "#5588dd"

        def _frame():
            if not self.winfo_exists():
                return
            # Only animate if header canvas still has same width (no resize race)
            cw = self.header_canvas.winfo_width() or w
            if abs(cw - w) > 4:
                return   # resize in progress, let _draw_header restart animation

            self.header_canvas.delete("anim")
            t = self._anim_frame

            # ── Sweep glow (horizontal band moving left→right) ──────────────
            sweep_x = int(((t * 2) % (w + 80)) - 40)
            for sx in range(max(0, sweep_x-18), min(w, sweep_x+18)):
                dist = abs(sx - sweep_x)
                a    = max(0, 55 - dist*3)
                if a > 0:
                    fill = sweep_col
                    self.header_canvas.create_line(
                        sx, 4, sx, h-1, fill=fill, width=1,
                        tags="anim", stipple="gray25" if a < 30 else ""
                    )

            # ── Particles (floating dots) ────────────────────────────────────
            for i,(px,py,spd,sz,ph) in enumerate(self._particles):
                # drift upward, wobble x
                ny2 = py - spd * 0.4
                nx  = px + math.sin(t * 0.05 + ph) * 0.5
                if ny2 < 4:
                    ny2 = h - 8
                    nx  = self._particles[i][0]
                self._particles[i] = (nx, ny2, spd, sz, ph)
                # pulse alpha
                alpha_f = (math.sin(t * 0.08 + ph) + 1) / 2  # 0..1
                if alpha_f > 0.15:
                    stip = "" if alpha_f > 0.6 else "gray50"
                    self.header_canvas.create_oval(
                        nx-sz, ny2-sz, nx+sz, ny2+sz,
                        fill=part_col, outline="", tags="anim",
                        stipple=stip
                    )

            # ── Rim pulse on icon disc ───────────────────────────────────────
            pulse = (math.sin(t * 0.07) + 1) / 2  # 0..1
            rim_col = "#4488ee" if is_dark else "#3366cc"
            extent  = int(20 + pulse * 30)
            start   = int(180 + t * 1.2) % 360
            if extent > 2:
                self.header_canvas.create_arc(
                    cx-disc_r-2, cy_ico-disc_r-2,
                    cx+disc_r+2, cy_ico+disc_r+2,
                    start=start, extent=extent,
                    outline=rim_col, width=2, style="arc", tags="anim"
                )

            self._anim_frame += 1
            self._anim_job = self.after(42, _frame)   # ~24 fps

        _frame()

    def _draw_bottom(self):
        """Smooth frosted-glass bottom bar."""
        p       = PALETTES[self.current_mode]
        is_dark = self.current_mode == "dark"
        self.update_idletasks()
        w = self.bottom_canvas.winfo_width() or 520
        h = 36   # was 30 — increased to fit larger font in status label and buttons
        self.bottom_canvas.configure(height=h, bg=p["bottom_bg"])

        # Base gradient (RGBA)
        base = make_gradient_image(w, h, p["header_bot"], p["bottom_bg"],
                                   alpha_top=255, alpha_bot=255)

        # Frosted glass overlay (very subtle)
        frost_c = "#0f1520" if is_dark else "#b8ccdf"
        frost   = _make_frosted_panel(w, h, frost_c, alpha=18)
        base    = _paste_rgba(base, frost, 0, 0)

        # Feathered top edge (separator from main frame)
        ed = ImageDraw.Draw(base)
        ed.line([(0,0),(w,0)], fill=(100,150,220,140) if is_dark else (80,120,180,100), width=1)
        ed.line([(0,1),(w,1)], fill=(5,8,18,120)     if is_dark else (60,90,130,60),   width=1)
        # Feathered bottom edge
        ed.line([(0,h-1),(w,h-1)], fill=(150,190,255,60) if is_dark else (180,210,240,80), width=1)

        self._bottom_bg = ImageTk.PhotoImage(base.convert("RGB"))
        self.bottom_canvas.delete("all")
        self.bottom_canvas.create_image(0, 0, anchor="nw", image=self._bottom_bg)

        # Centre brand (very small, italic)
        self.bottom_canvas.create_text(w//2, h//2, text="polsoft.ITS™",
            fill="#3d5580" if is_dark else "#4466aa", font=("Segoe UI", 7, "italic"), anchor="center")

        # place utility buttons right side over the canvas
        self._place_bottom_buttons(p, w)

    def _place_bottom_buttons(self, p, canvas_w):
        """Place lang / theme / pin buttons over the bottom canvas."""
        # destroy old if exist
        for attr in ("log_btn", "help_btn", "about_btn", "theme_btn", "lang_btn", "pin_btn", "_bottom_btn_frame"):
            if hasattr(self, attr):
                try:
                    getattr(self, attr).destroy()
                except Exception:
                    pass

        frame = ctk.CTkFrame(self.bottom_canvas, fg_color="transparent")
        self._bottom_btn_frame = frame
        # position it on the canvas via place
        frame.place(relx=1.0, rely=0.5, anchor="e", x=-4)

        # Page (HTML) button
        self.page_btn = ctk.CTkButton(
            frame, text="🌐", width=28, height=22,
            fg_color=p["btn_misc"], hover_color=p["btn_misc_h"],
            font=ctk.CTkFont(size=12),
            corner_radius=6, border_width=1, border_color=p["input_card2"],
            command=self.open_page
        )
        self.page_btn.pack(side="left", padx=(0, 3))
        self._themed[self.page_btn] = "btn_misc"

        # Log button
        self.log_btn = ctk.CTkButton(
            frame, text="LOG", width=40, height=24,          # was width=36 height=22
            fg_color=p["btn_misc"], hover_color=p["btn_misc_h"],
            text_color=p["text_primary"],                    # was: default
            font=ctk.CTkFont(size=11, weight="bold"),        # was size=9
            corner_radius=6, border_width=1, border_color=p["input_card2"],
            command=self.show_log
        )
        self.log_btn.pack(side="left", padx=(0, 3))
        self._themed[self.log_btn] = "btn_misc"

        # Help button
        self.help_btn = ctk.CTkButton(
            frame, text="?", width=30, height=24,            # was 28/22
            fg_color=p["btn_misc"], hover_color=p["btn_misc_h"],
            text_color=p["text_primary"],
            font=ctk.CTkFont(size=13, weight="bold"),        # was size=12
            corner_radius=6, border_width=1, border_color=p["input_card2"],
            command=self.show_help
        )
        self.help_btn.pack(side="left", padx=(0, 3))
        self._themed[self.help_btn] = "btn_misc"

        # About button
        self.about_btn = ctk.CTkButton(
            frame, text="ℹ", width=30, height=24,
            fg_color=p["btn_misc"], hover_color=p["btn_misc_h"],
            text_color=p["text_primary"],
            font=ctk.CTkFont(size=13),
            corner_radius=6, border_width=1, border_color=p["input_card2"],
            command=self.show_about
        )
        self.about_btn.pack(side="left", padx=(0, 3))
        self._themed[self.about_btn] = "btn_misc"

        # Theme toggle button
        self.theme_btn = ctk.CTkButton(
            frame, text="🌙" if self.current_mode == "light" else "☀",
            width=30, height=24,
            fg_color=p["btn_misc"], hover_color=p["btn_misc_h"],
            text_color=p["text_primary"],
            font=ctk.CTkFont(size=13),
            corner_radius=6, border_width=1, border_color=p["input_card2"],
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", padx=(0, 3))
        self._themed[self.theme_btn] = "btn_misc"

        self.lang_btn = ctk.CTkButton(
            frame, text=self.t("lang_btn"), width=44, height=24,   # was 40/22
            fg_color=p["btn_misc"], hover_color=p["btn_misc_h"],
            text_color=p["text_primary"],
            font=ctk.CTkFont(size=12, weight="bold"),              # was size=11
            corner_radius=6, border_width=1, border_color=p["input_card2"],
            command=self.toggle_lang
        )
        self.lang_btn.pack(side="left", padx=(0, 3))
        self._themed[self.lang_btn] = "btn_misc"

        # status label just left of the buttons
        if hasattr(self, "status_label"):
            self.status_label.destroy()
        self.status_label = ctk.CTkLabel(
            self.bottom_canvas, text=self.t("status_ready"),
            font=ctk.CTkFont(size=11, weight="bold"),    # was size=9, no bold
            fg_color="transparent",
            text_color=p["text_dim"]
        )
        self.status_label.place(x=10, rely=0.5, anchor="w")

    def create_input_group(self, parent, label_text, command):
        p = PALETTES[self.current_mode]
        frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=p["input_card"],
                              border_width=1, border_color=p["input_card2"])
        frame.pack(fill="x", padx=10, pady=3)
        self._themed[frame] = "input_card"

        lbl = ctk.CTkLabel(
            frame, text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),   # was 11
            text_color=p["text_label"],                  # was: default (often invisible)
        )
        lbl.pack(anchor="w", padx=10, pady=(5, 0))

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=6, pady=(0, 6))

        entry = ctk.CTkEntry(
            inner, height=28,                            # was 26
            font=ctk.CTkFont(size=12),                  # was 11
            text_color=p["text_entry"],                  # was: default
            corner_radius=6, border_width=1, border_color=p["input_card2"],
        )
        entry.pack(side="left", fill="x", expand=True, padx=(4, 2))

        ctk.CTkButton(inner, text="…", width=32, height=28, corner_radius=6,  # was 26
                       border_width=1, border_color=p["input_card2"],
                       command=command).pack(side="right", padx=(2, 4))
        return entry, lbl

    # ------------------------------------------------------------------ #
    # WINDOW / THEME LOGIC
    # ------------------------------------------------------------------ #
    def on_window_resize(self, event):
        if event.widget is self:
            self.after(10, self._redraw_canvases)

    def _redraw_canvases(self):
        self._draw_header()
        self._draw_bottom()

    def toggle_theme(self):
        self.current_mode = "light" if self.current_mode == "dark" else "dark"
        ctk.set_appearance_mode(self.current_mode)
        self._apply_palette()
        self._redraw_canvases()  # recreates theme_btn with correct icon

    def _apply_palette(self):
        p = PALETTES[self.current_mode]
        for widget, role in list(self._themed.items()):
            try:
                if role == "btn_misc":
                    widget.configure(fg_color=p[role], hover_color=p["btn_misc_h"],
                                     text_color=p["text_primary"])
                elif role == "log":
                    widget.configure(fg_color=p["input_card"],
                                     border_color=p["input_card2"],
                                     text_color=p["text_entry"])
                elif role == "main":
                    widget.configure(fg_color=p[role],
                                     border_color=p.get("aero_border", p["input_card2"]))
                elif role == "input_card":
                    widget.configure(fg_color=p[role],
                                     border_color=p["input_card2"])
                elif role == "label":
                    widget.configure(text_color=p["text_label"])
                elif role == "label_primary":
                    widget.configure(text_color=p["text_primary"])
                else:
                    widget.configure(fg_color=p[role])
            except Exception:
                pass
        # status label color
        try:
            self.status_label.configure(text_color=p["text_dim"])
        except Exception:
            pass

    def toggle_topmost(self):
        self.attributes("-topmost", self.topmost_var.get())

    def toggle_size_lock(self):
        self.resizable(not self.lock_size_var.get(), not self.lock_size_var.get())

    # ------------------------------------------------------------------ #
    # HELPERS
    # ------------------------------------------------------------------ #
    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Batch Files", "*.bat")])
        if path:
            self.update_entry(self.entry_bat, path)
            self._preview_bat(path)
            # Auto-suggest output name only if user hasn't typed one yet
            if hasattr(self, "entry_outname") and not self.entry_outname.get().strip():
                stem = os.path.splitext(os.path.basename(path))[0]
                self.update_entry(self.entry_outname, stem + ".exe")

    def browse_icon(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Icon / Image Files", "*.ico *.png *.jpg *.jpeg"),
            ("ICO Files", "*.ico"),
            ("PNG Files", "*.png"),
            ("JPEG Files", "*.jpg *.jpeg"),
        ])
        if path:
            self.update_entry(self.entry_icon, path)
            # Preview selected image as disc icon in header
            self._current_icon_path = path
            self.after(50, self._draw_header)

    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.update_entry(self.entry_output, path)

    def update_entry(self, entry, text):
        entry.delete(0, "end")
        entry.insert(0, text)

    # ------------------------------------------------------------------ #
    # THREAD-SAFE GUI HELPERS
    # ------------------------------------------------------------------ #
    def _append_log(self, line: str):
        self.after(0, lambda: (self.log_box.insert("end", line), self.log_box.see("end")))

    def _set_status(self, text: str, color: str):
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    def _set_compile_btn(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.after(0, lambda: self.btn_compile.configure(state=state))

    def _show_info(self, title: str, message: str):
        self.after(0, lambda: messagebox.showinfo(title, message))

    def _show_error(self, title: str, message: str):
        self.after(0, lambda: messagebox.showerror(title, message))

    def _show_warning(self, title: str, message: str):
        self.after(0, lambda: messagebox.showwarning(title, message))

    # ------------------------------------------------------------------ #
    # COMPILATION
    # ------------------------------------------------------------------ #
    def start_conversion(self):
        # Read ALL widget values in the main (Tkinter) thread
        bat_path = self.entry_bat.get().strip()
        out_dir  = self.entry_output.get().strip()
        icon     = self.entry_icon.get().strip()
        onefile  = self.onefile_var.get()
        console  = self.console_var.get()

        # Custom output name — strip .exe suffix if typed, we re-add it later
        raw_name = self.entry_outname.get().strip()
        out_name = os.path.splitext(raw_name)[0] if raw_name else ""

        if not os.path.isfile(bat_path) or not out_dir:
            self._show_warning(self.t("warn_title"), self.t("warn_msg"))
            return

        self.btn_compile.configure(state="disabled")
        self._progress_start()
        threading.Thread(
            target=self.convert,
            args=(bat_path, out_dir, icon, onefile, console, out_name),
            daemon=True,
        ).start()

    def convert(self, bat_path: str, out_dir: str, icon: str,
                onefile: bool, console: bool, out_name: str = ""):
        # All parameters already read from the GUI in the main thread.
        # out_name is the desired stem (no .exe); empty → use bat stem.

        self._set_status(self.t("status_compile"), "orange")
        self.after(0, lambda: self.log_box.delete("1.0", "end"))
        _log.info("Rozpoczęcie konwersji: bat=%s, out=%s, onefile=%s, console=%s, icon=%s, out_name=%s",
                  bat_path, out_dir, onefile, console, icon or "brak", out_name or "(auto)")

        temp_dir = tempfile.mkdtemp()
        success  = False
        result_path = ""
        try:
            wrapper_py   = os.path.join(temp_dir, "wrapper.py")
            bat_basename = os.path.basename(bat_path)
            bat_stem     = os.path.splitext(bat_basename)[0]
            # Effective output stem: custom name wins, otherwise bat filename
            out_stem     = out_name.strip() if out_name.strip() else bat_stem

            with open(wrapper_py, "w", encoding="utf-8") as f:
                f.write(
                    "import subprocess, os, sys\n"
                    "base = sys._MEIPASS if getattr(sys, 'frozen', False) "
                    "else os.path.dirname(os.path.abspath(__file__))\n"
                    f"subprocess.call(['cmd.exe', '/c', os.path.join(base, {repr(bat_basename)})])"
                )

            shutil.copy(bat_path, os.path.join(temp_dir, bat_basename))

            cmd = [
                "pyinstaller", "--noconfirm", "--clean",
                "--distpath", os.path.join(temp_dir, "dist"),
                "--workpath", os.path.join(temp_dir, "build"),
                "--specpath", temp_dir,
                "--add-data", f"{os.path.join(temp_dir, bat_basename)}{os.pathsep}.",
            ]

            if onefile:
                cmd.append("--onefile")
            if not console:
                cmd.append("--noconsole")
            if icon and os.path.isfile(icon):
                icon_ext = os.path.splitext(icon)[1].lower()
                if icon_ext in (".png", ".jpg", ".jpeg"):
                    try:
                        icon = _convert_image_to_ico(icon, temp_dir)
                        self._append_log(f"[INFO] Icon converted to ICO: {icon}\n")
                    except Exception as ce:
                        self._append_log(f"[WARN] Icon conversion failed: {ce}\n")
                        icon = ""
                if icon:
                    cmd.append(f"--icon={icon}")
            cmd.append(wrapper_py)

            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
            except FileNotFoundError:
                raise RuntimeError(
                    "PyInstaller not found. Install it with:\n  pip install pyinstaller"
                )
            if proc.stdout:
                for line in proc.stdout:
                    self._append_log(line)
                    _log.debug("[PyInstaller] %s", line.rstrip())
            proc.wait()

            if proc.returncode == 0:
                os.makedirs(out_dir, exist_ok=True)

                if onefile:
                    src_exe  = os.path.join(temp_dir, "dist", "wrapper.exe")
                    dest_exe = os.path.join(out_dir, out_stem + ".exe")
                    if os.path.exists(dest_exe):
                        os.remove(dest_exe)
                    shutil.move(src_exe, dest_exe)
                    result_path = dest_exe
                else:
                    src_folder   = os.path.join(temp_dir, "dist", "wrapper")
                    src_exe_orig = os.path.join(src_folder, "wrapper.exe")
                    src_exe_new  = os.path.join(src_folder, out_stem + ".exe")
                    if os.path.isfile(src_exe_orig):
                        os.rename(src_exe_orig, src_exe_new)
                    else:
                        raise FileNotFoundError(
                            f"PyInstaller dist folder not found or wrapper.exe missing:\n{src_folder}"
                        )
                    dest_folder = os.path.join(out_dir, out_stem)
                    if os.path.exists(dest_folder):
                        shutil.rmtree(dest_folder)
                    shutil.move(src_folder, dest_folder)
                    result_path = os.path.join(dest_folder, out_stem + ".exe")
                    self._append_log(
                        f"[INFO] Non-onefile mode: folder → {dest_folder}\n"
                        f"       Run: {result_path}\n"
                    )

                success = True
                # Save history entry
                self._save_history_entry(
                    bat_path, out_dir, icon, onefile, console,
                    out_name, result_path
                )
                _log.info("Konwersja zakończona sukcesem: %s", result_path)
                self._set_status(self.t("status_ok"), "#2ecc71")
                self._show_info(self.t("ok_title"), self.t("ok_msg").format(result_path))

            else:
                _log.error("Konwersja nieudana. Kod wyjścia: %d", proc.returncode)
                self._set_status(self.t("status_err"), "red")
                self._show_error(self.t("err_title"), self.t("err_msg"))

        except Exception as e:
            _log.exception("Krytyczny błąd konwersji: %s", e)
            self._set_status(self.t("status_crit"), "red")
            self._show_error(self.t("crit_title"), str(e))
        finally:
            self._set_compile_btn(True)
            self._progress_stop(success)
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    app = BatToExeApp()
    app.mainloop()