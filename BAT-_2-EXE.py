"""
bat_to_exe_gui.py
=================
Konwerter BAT -> EXE z graficznym interfejsem uzytkownika.
Uruchom dwuklikiem lub:  python bat_to_exe_gui.py

Wymagania: pip install pyinstaller
Tylko standardowa biblioteka Python + tkinter (wbudowany w Windows).

Company : polsoft.ITS\u2122 Group
Author  : Sebastian Januchowski
E-mail  : polsoft.its@fastservice.com
GitHub  : https://github.com/seb07uk
License : 2026\u00a9 polsoft.ITS\u2122 DEV. All rights reserved.
"""

__author__    = "Sebastian Januchowski"
__company__   = "polsoft.ITS™ Group"
__email__     = "polsoft.its@fastservice.com"
__github__    = "https://github.com/seb07uk"
__copyright__ = "2026© polsoft.ITS™ DEV. All rights reserved."
__version__   = "1.0.0"
import os
import sys
import json
import shutil
import struct
import lzma
import hashlib
import tempfile
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

# Pillow — sprawdzenie dostepnosci (dla okna About i _ensure_ico)
try:
    from PIL import Image as _PILImage  # noqa: F401
    _PIL_OK = True
except ImportError:
    _PIL_OK = False


# ─────────────────────────────────────────────
#  System tłumaczeń PL / EN
# ─────────────────────────────────────────────

LANG: dict[str, dict[str, str]] = {
    "pl": {
        # --- GUI główne ---
        "app_title":            "BAT/CMD-2-EXE Converter by Sebastian Januchowski",
        "app_subtitle":         "BAT/CMD-2-EXE Converter",
        "status_ready":         "Gotowy.",
        "status_topmost_on":    "Okno zawsze na wierzchu.",
        "status_topmost_off":   "Gotowy.",
        "status_converting":    "Konwertowanie…",
        "status_cancelled":     "Anulowano — plik nie został nadpisany.",
        "status_pwd_active":    "Ochrona hasłem aktywna ✔",
        "status_pwd_off":       "Ochrona hasłem wyłączona.",
        # --- Etykiety formularza ---
        "lbl_bat":              "Plik .BAT:",
        "lbl_out":              "Folder wyjściowy:",
        "lbl_icon":             "Ikona:",
        "lbl_exe_name":         "Nazwa EXE:",
        "btn_browse":           "Przeglądaj…",
        "btn_convert":          "▶  Konwertuj",
        "btn_converting":       "⏳  Konwertuję…",
        "btn_dist":             "📁  Dist",
        "btn_metadata":         "🏷  Metadane",
        "lbl_log":              "Dziennik",
        "lbl_console":          "Konsola",
        # --- Dialogi pliku ---
        "dlg_pick_bat_title":   "Wybierz plik BAT",
        "dlg_bat_filter":       "Pliki wsadowe",
        "dlg_all_filter":       "Wszystkie",
        "dlg_pick_out_title":   "Wybierz folder wyjściowy",
        "dlg_pick_ico_title":   "Wybierz ikonę",
        "dlg_ico_filter":       "Obrazy ikon",
        "dlg_ico_ico":          "ICO",
        "dlg_ico_png":          "PNG",
        "dlg_ico_jpg":          "JPEG",
        # --- Komunikaty konwersji ---
        "msg_no_file_title":    "Brak pliku",
        "msg_no_file_body":     "Wybierz plik .BAT!",
        "msg_bad_file_title":   "Błąd",
        "msg_bad_file_body":    "Plik nie istnieje:\n{path}",
        "msg_exists_title":     "Plik już istnieje",
        "msg_exists_body":      "Plik już istnieje:\n{path}\n\nNadpisać?",
        "msg_ok_title":         "Sukces!",
        "msg_ok_body":          "Plik EXE został wygenerowany:\n\n{path}",
        "msg_err_title":        "Błąd konwersji",
        "log_done":             "\n✔  Gotowe: {path}",
        "log_err":              "\n✘  Błąd: {msg}",
        "status_ok":            "✔  Sukces: {name}",
        "status_err":           "✘  Błąd konwersji",
        "log_upx":              "\n─── Kompresja UPX ───",
        "log_lzma":             "\n─── Kompresja LZMA (własny algorytm) ───",
        # --- Hasło ---
        "pwd_dialog_title":     "🔑  Hasło do EXE",
        "pwd_header":           "🔑  Ochrona hasłem",
        "pwd_lbl_pwd":          "Hasło:",
        "pwd_lbl_confirm":      "Potwierdź:",
        "pwd_show":             "Pokaż hasło",
        "pwd_info":             "Hasło jest hashowane SHA-256 i wbudowane w EXE.\nUżytkownik ma 3 próby przy każdym uruchomieniu.",
        "pwd_err_empty":        "⚠  Hasło nie może być puste!",
        "pwd_err_short":        "⚠  Hasło musi mieć min. 4 znaki!",
        "pwd_err_mismatch":     "⚠  Hasła nie są zgodne!",
        "pwd_lbl_active":       "Hasło ✔",
        "pwd_lbl_inactive":     "Hasło",
        "pwd_ask_remove_title": "Hasło",
        "pwd_ask_remove_body":  "Usunąć ochronę hasłem?",
        "btn_save":             "Zapisz",
        "btn_cancel":           "Anuluj",
        # --- Guard (wstrzykiwany do EXE) ---
        "guard_title":          "Weryfikacja",
        "guard_prompt":         "Podaj hasło aby uruchomić program:",
        "guard_err_title":      "Błąd",
        "guard_err_body":       "Nieprawidłowe hasło. Próba {n}/3.",
        "log_pwd_active":       "Hasło: ochrona SHA-256 aktywna ✔",
        # --- Embed / Wrapper ---
        "embed_wrapper":        "Wrapper",
        "embed_embed":          "Embed",
        # --- Kompresja ---
        "cmp_none":             "Kompresja",
        # --- Metadane ---
        "meta_dialog_title":    "Metadane EXE",
        "meta_header":          "🏷  Metadane pliku EXE",
        "meta_product":         "Nazwa produktu:",
        "meta_version":         "Wersja (x.x.x.x):",
        "meta_company":         "Firma / Author:",
        "meta_description":     "Opis:",
        "meta_copyright":       "Copyright:",
        "meta_info":            "Metadane beda osadzone w pliku .exe",
        # --- Logi błędów konwersji ---
        "err_no_access":        "Brak dostępu do pliku — '{name}.exe' jest prawdopodobnie uruchomiony.\nZamknij program i spróbuj ponownie.",
        "err_pyinstaller":      "PyInstaller zakończył się błędem (kod {code})",
        "err_no_exe":           "Brak pliku: {path}",
        "err_icon_fmt":         "Nieobslugiwany format ikony: '{ext}'\nDozwolone: .ico .jpg .jpeg .png",
        "log_pillow_install":   "Pillow niedostepny — instalowanie: pip install pillow ...",
        "log_pillow_ok":        "Pillow zainstalowany pomyslnie.",
        "log_pillow_err":       "Blad instalacji Pillow:\n",
        "log_icon_conv":        "Konwersja ikony: {name} -> .ico ...",
        "log_icon_ok":          "Ikona skonwertowana -> {name}",
        "log_ver_info":         "Version-info: {prod} v{ver}",
        "log_embed_attach":     "Tryb embed: dolaczam {name} jako zasob",
        # --- About ---
        "about_title":          "O programie",
        "about_converts":       "Konwertuje pliki .BAT do .EXE",
        "about_via":            "przy uzyciu PyInstaller.",
        "about_icons":          "Obslugiwane ikony:",
        "about_pillow_ok":      "dostepny ✔",
        "about_pillow_no":      "niedostepny  (pip install pillow)",
        "about_requirements":   "Wymagania:",
        # --- Pomoc: tytuły zakładek ---
        "help_title":           "Pomoc  -  BAT/CMD-2-EXE Converter by Sebastian Januchowski",
        "help_header":          "?  Pomoc  -  BAT/CMD-2-EXE Converter by Sebastian Januchowski",
        "help_tab_desc":        "📋  Opis",
        "help_tab_form":        "📝  Formularz",
        "help_tab_btns":        "🖱  Przyciski",
        "help_tab_log":         "📜  Dziennik",
        "help_tab_req":         "⚙  Wymagania",
        "help_close":           "Zamknij",
        # --- Pomoc: Opis ---
        "help_desc_h1":         "BAT/CMD-2-EXE  —  Konwerter BAT/CMD → EXE",
        "help_desc_how_h":      "Jak to dziala?",
        "help_desc_how1":       "1. Zawartosc pliku .bat zostaje osadzona w skrypcie Python.",
        "help_desc_how2":       "2. PyInstaller pakuje skrypt w jeden plik .exe (--onefile).",
        "help_desc_how3":       "3. Po uruchomieniu .exe skrypt .bat jest wyodrebniony do katalogu",
        "help_desc_how3b":      "   tymczasowego i wykonywany przez cmd.exe, po czym usuwany.",
        "help_desc_feat_h":     "Mozliwosci",
        "help_desc_req_h":      "Wymagania",
        "help_desc_pillow":     "  (Pillow instalowany automatycznie gdy potrzebny)",
        # --- Pomoc: Formularz ---
        "help_form_h1":         "Opis pol formularza",
        "help_form_bat_h":      "Plik .BAT",
        "help_form_bat1":       "Sciezka do pliku wsadowego (.bat) ktory chcesz skonwertowac.",
        "help_form_bat2":       "Kliknij [Przegladaj] lub wpisz sciezke recznie.",
        "help_form_bat3":       "  \u2714 Po wyborze pliku folder wyjsciowy i nazwa EXE",
        "help_form_bat4":       "    wypelniane sa automatycznie.",
        "help_form_out_h":      "Folder wyjsciowy",
        "help_form_out1":       "Katalog gdzie zostanie zapisany gotowy plik .exe.",
        "help_form_out2":       "Jezeli pozostawiony pusty  \u2192  tworzony jest podkatalog",
        "help_form_out3":       "Katalog jest tworzony automatycznie jesli nie istnieje.",
        "help_form_ico_h":      "Ikona (.ico / .png / .jpg)",
        "help_form_ico1":       "Opcjonalna ikona widoczna na pliku .exe i na pasku zadan.",
        "help_form_name_h":     "Nazwa EXE",
        "help_form_name1":      "Nazwa wynikowego pliku bez rozszerzenia .exe.",
        "help_form_name2":      "Domyslnie: nazwa pliku .bat.",
        "help_form_con_h":      "Przelacznik Konsola ON / OFF",
        "help_form_cmp_h":      "Przelacznik Kompresja (3 stany — klikaj cyklicznie)",
        "help_form_pwd_h":      "Przelacznik Haslo",
        # --- Pomoc: Przyciski ---
        "help_btns_h1":         "Przyciski, przelaczniki i pasek statusu",
        # --- Pomoc: Dziennik ---
        "help_log_h1":          "Okno dziennika (log konwersji)",
        "help_log_colors_h":    "Kolorowanie linii:",
        "help_log_watermark_h": "Watermark",
        # --- Pomoc: Wymagania ---
        "help_req_h1":          "Wymagania i instalacja",
        "help_req_compat_h":    "Kompatybilnosc",
        # --- Język ---
        "lang_switch_label":    "EN",   # etykieta na przycisku (pokazuje dokąd przełączy)
    },

    "en": {
        # --- GUI główne ---
        "app_title":            "BAT/CMD-2-EXE Converter by Sebastian Januchowski",
        "app_subtitle":         "BAT/CMD-2-EXE Converter",
        "status_ready":         "Ready.",
        "status_topmost_on":    "Window always on top.",
        "status_topmost_off":   "Ready.",
        "status_converting":    "Converting…",
        "status_cancelled":     "Cancelled — file was not overwritten.",
        "status_pwd_active":    "Password protection active ✔",
        "status_pwd_off":       "Password protection disabled.",
        # --- Etykiety formularza ---
        "lbl_bat":              ".BAT File:",
        "lbl_out":              "Output folder:",
        "lbl_icon":             "Icon:",
        "lbl_exe_name":         "EXE name:",
        "btn_browse":           "Browse…",
        "btn_convert":          "▶  Convert",
        "btn_converting":       "⏳  Converting…",
        "btn_dist":             "📁  Dist",
        "btn_metadata":         "🏷  Metadata",
        "lbl_log":              "Log",
        "lbl_console":          "Console",
        # --- Dialogi pliku ---
        "dlg_pick_bat_title":   "Select BAT file",
        "dlg_bat_filter":       "Batch files",
        "dlg_all_filter":       "All files",
        "dlg_pick_out_title":   "Select output folder",
        "dlg_pick_ico_title":   "Select icon",
        "dlg_ico_filter":       "Icon images",
        "dlg_ico_ico":          "ICO",
        "dlg_ico_png":          "PNG",
        "dlg_ico_jpg":          "JPEG",
        # --- Komunikaty konwersji ---
        "msg_no_file_title":    "No file selected",
        "msg_no_file_body":     "Please select a .BAT file!",
        "msg_bad_file_title":   "Error",
        "msg_bad_file_body":    "File does not exist:\n{path}",
        "msg_exists_title":     "File already exists",
        "msg_exists_body":      "File already exists:\n{path}\n\nOverwrite?",
        "msg_ok_title":         "Success!",
        "msg_ok_body":          "EXE file has been generated:\n\n{path}",
        "msg_err_title":        "Conversion error",
        "log_done":             "\n✔  Done: {path}",
        "log_err":              "\n✘  Error: {msg}",
        "status_ok":            "✔  Success: {name}",
        "status_err":           "✘  Conversion error",
        "log_upx":              "\n─── UPX compression ───",
        "log_lzma":             "\n─── LZMA compression (built-in algorithm) ───",
        # --- Hasło ---
        "pwd_dialog_title":     "🔑  EXE Password",
        "pwd_header":           "🔑  Password protection",
        "pwd_lbl_pwd":          "Password:",
        "pwd_lbl_confirm":      "Confirm:",
        "pwd_show":             "Show password",
        "pwd_info":             "Password is SHA-256 hashed and embedded in EXE.\nUser has 3 attempts on each launch.",
        "pwd_err_empty":        "⚠  Password cannot be empty!",
        "pwd_err_short":        "⚠  Password must be at least 4 characters!",
        "pwd_err_mismatch":     "⚠  Passwords do not match!",
        "pwd_lbl_active":       "Password ✔",
        "pwd_lbl_inactive":     "Password",
        "pwd_ask_remove_title": "Password",
        "pwd_ask_remove_body":  "Remove password protection?",
        "btn_save":             "Save",
        "btn_cancel":           "Cancel",
        # --- Guard (wstrzykiwany do EXE) ---
        "guard_title":          "Verification",
        "guard_prompt":         "Enter password to run the program:",
        "guard_err_title":      "Error",
        "guard_err_body":       "Wrong password. Attempt {n}/3.",
        "log_pwd_active":       "Password: SHA-256 protection active ✔",
        # --- Embed / Wrapper ---
        "embed_wrapper":        "Wrapper",
        "embed_embed":          "Embed",
        # --- Kompresja ---
        "cmp_none":             "Compress",
        # --- Metadane ---
        "meta_dialog_title":    "EXE Metadata",
        "meta_header":          "🏷  EXE file metadata",
        "meta_product":         "Product name:",
        "meta_version":         "Version (x.x.x.x):",
        "meta_company":         "Company / Author:",
        "meta_description":     "Description:",
        "meta_copyright":       "Copyright:",
        "meta_info":            "Metadata will be embedded in the .exe file",
        # --- Logi błędów konwersji ---
        "err_no_access":        "Access denied — '{name}.exe' is probably running.\nClose the program and try again.",
        "err_pyinstaller":      "PyInstaller exited with error (code {code})",
        "err_no_exe":           "File not found: {path}",
        "err_icon_fmt":         "Unsupported icon format: '{ext}'\nAllowed: .ico .jpg .jpeg .png",
        "log_pillow_install":   "Pillow not available — installing: pip install pillow ...",
        "log_pillow_ok":        "Pillow installed successfully.",
        "log_pillow_err":       "Pillow installation error:\n",
        "log_icon_conv":        "Converting icon: {name} -> .ico ...",
        "log_icon_ok":          "Icon converted -> {name}",
        "log_ver_info":         "Version-info: {prod} v{ver}",
        "log_embed_attach":     "Embed mode: attaching {name} as resource",
        # --- About ---
        "about_title":          "About",
        "about_converts":       "Converts .BAT files to .EXE",
        "about_via":            "using PyInstaller.",
        "about_icons":          "Supported icons:",
        "about_pillow_ok":      "available ✔",
        "about_pillow_no":      "not available  (pip install pillow)",
        "about_requirements":   "Requirements:",
        # --- Pomoc: tytuły zakładek ---
        "help_title":           "Help  -  BAT/CMD-2-EXE Converter by Sebastian Januchowski",
        "help_header":          "?  Help  -  BAT/CMD-2-EXE Converter by Sebastian Januchowski",
        "help_tab_desc":        "📋  Description",
        "help_tab_form":        "📝  Form",
        "help_tab_btns":        "🖱  Buttons",
        "help_tab_log":         "📜  Log",
        "help_tab_req":         "⚙  Requirements",
        "help_close":           "Close",
        # --- Pomoc: Opis ---
        "help_desc_h1":         "BAT/CMD-2-EXE  —  BAT/CMD → EXE Converter",
        "help_desc_how_h":      "How it works?",
        "help_desc_how1":       "1. The contents of the .bat file are embedded in a Python script.",
        "help_desc_how2":       "2. PyInstaller packages the script into a single .exe (--onefile).",
        "help_desc_how3":       "3. When the .exe runs, the .bat is extracted to a temp folder",
        "help_desc_how3b":      "   and executed by cmd.exe, then deleted.",
        "help_desc_feat_h":     "Features",
        "help_desc_req_h":      "Requirements",
        "help_desc_pillow":     "  (Pillow installed automatically when needed)",
        # --- Pomoc: Formularz ---
        "help_form_h1":         "Form field descriptions",
        "help_form_bat_h":      ".BAT File",
        "help_form_bat1":       "Path to the batch file (.bat) you want to convert.",
        "help_form_bat2":       "Click [Browse] or type the path manually.",
        "help_form_bat3":       "  \u2714 After selecting a file, output folder and EXE name",
        "help_form_bat4":       "    are filled in automatically.",
        "help_form_out_h":      "Output folder",
        "help_form_out1":       "Directory where the finished .exe will be saved.",
        "help_form_out2":       "If left empty  \u2192  a subdirectory is created:",
        "help_form_out3":       "Directory is created automatically if it does not exist.",
        "help_form_ico_h":      "Icon (.ico / .png / .jpg)",
        "help_form_ico1":       "Optional icon visible on the .exe file and in the taskbar.",
        "help_form_name_h":     "EXE name",
        "help_form_name1":      "Output filename without the .exe extension.",
        "help_form_name2":      "Default: the name of the .bat file.",
        "help_form_con_h":      "Console ON / OFF toggle",
        "help_form_cmp_h":      "Compression toggle (3 states — click cyclically)",
        "help_form_pwd_h":      "Password toggle",
        # --- Pomoc: Przyciski ---
        "help_btns_h1":         "Buttons, toggles and status bar",
        # --- Pomoc: Dziennik ---
        "help_log_h1":          "Log window (conversion log)",
        "help_log_colors_h":    "Line coloring:",
        "help_log_watermark_h": "Watermark",
        # --- Pomoc: Wymagania ---
        "help_req_h1":          "Requirements and installation",
        "help_req_compat_h":    "Compatibility",
        # --- Język ---
        "lang_switch_label":    "PL",   # etykieta na przycisku
    },
}

_current_lang: str = "pl"


def T(key: str, **kwargs) -> str:
    """Zwróć przetłumaczony string dla aktualnego języka."""
    s = LANG.get(_current_lang, LANG["pl"]).get(key)
    if s is None:
        s = LANG["pl"].get(key, key)   # fallback do PL, potem do klucza
    return s.format(**kwargs) if kwargs else s


def _set_lang(lang: str) -> None:
    global _current_lang
    _current_lang = lang if lang in LANG else "pl"


def _ensure_ico(icon_path: str, temp_dir: str, log_callback=None) -> str:
    """
    Jesli .ico — zwraca bez zmian.
    Jesli .jpg/.jpeg/.png — konwertuje do .ico w temp_dir i zwraca nowa sciezke.
    Pillow importowany lokalnie; jesli brak — instaluje w locie przez pip.
    """
    ext = os.path.splitext(icon_path)[1].lower()
    if ext == ".ico":
        return icon_path
    if ext not in (".jpg", ".jpeg", ".png"):
        raise RuntimeError(T("err_icon_fmt", ext=ext))

    # sprobuj zaimportowac Pillow; jesli brak — zainstaluj
    try:
        from PIL import Image as PILImg
    except ImportError:
        if log_callback:
            log_callback(T("log_pillow_install"))
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pillow", "--quiet"],
            capture_output=True, text=True, timeout=90
        )
        if result.returncode != 0:
            raise RuntimeError(T("log_pillow_err") + result.stderr.strip())
        if log_callback:
            log_callback(T("log_pillow_ok"))
        from PIL import Image as PILImg

    if log_callback:
        log_callback(T("log_icon_conv", name=os.path.basename(icon_path)))

    img = PILImg.open(icon_path).convert("RGBA")
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    resized = [img.resize(s, PILImg.LANCZOS) for s in sizes]
    ico_path = os.path.join(temp_dir, "_icon_converted.ico")
    resized[0].save(ico_path, format="ICO", append_images=resized[1:], sizes=sizes)

    if log_callback:
        log_callback(T("log_icon_ok", name=os.path.basename(ico_path)))
    return ico_path


# ─────────────────────────────────────────────
#  Logika konwersji (bez GUI)
# ─────────────────────────────────────────────

def convert(bat_path: str, output_dir: str, icon: str | None,
            noconsole: bool, log_callback, exe_name: str | None = None,
            metadata: dict | None = None, embed: bool = False,
            password: str | None = None):
    """
    Konwertuje .bat → .exe za pomocą PyInstaller.
    log_callback(msg) wywoływany dla każdej linii logu.
    Zwraca ścieżkę do .exe lub rzuca wyjątek.
    """
    bat_path   = os.path.abspath(bat_path)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    bat_name = (exe_name.strip() if exe_name and exe_name.strip()
               else os.path.splitext(os.path.basename(bat_path))[0])

    with open(bat_path, "r", encoding="utf-8", errors="replace") as f:
        bat_content = f.read()

    bat_filename = os.path.basename(bat_path)

    # ── blok hasła (wstrzykiwany na początku wrapperów) ──
    if password and password.strip():
        pwd_hash = hashlib.sha256(password.strip().encode("utf-8")).hexdigest()
        _g_title  = T("guard_title")
        _g_prompt = T("guard_prompt")
        _g_err_t  = T("guard_err_title")
        _g_err_b  = T("guard_err_body", n="{_attempt+1}")   # placeholder – wypełni guard
        password_guard = f'''\
import hashlib, sys
def _check_password():
    import tkinter as _tk
    from tkinter import simpledialog as _sd, messagebox as _mb
    _root = _tk.Tk(); _root.withdraw()
    for _attempt in range(3):
        _pwd = _sd.askstring(
            {repr(_g_title)}, {repr(_g_prompt)},
            show="*", parent=_root)
        if _pwd is None:
            _root.destroy(); sys.exit(0)
        if hashlib.sha256(_pwd.encode("utf-8")).hexdigest() == {repr(pwd_hash)}:
            _root.destroy(); return
        _mb.showerror({repr(_g_err_t)}, f"{"Nieprawidłowe hasło. Próba"} {{_attempt+1}}/3.", parent=_root)
    _root.destroy(); sys.exit(1)
_check_password()
'''
        log_callback(T("log_pwd_active"))
    else:
        password_guard = ""

    if embed:
        # Tryb embed: .bat jako zasob --add-data, wyciagany przez sys._MEIPASS
        wrapper = f'''\
import os, sys, subprocess
{password_guard}
def _base():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))
def main():
    bat = os.path.join(_base(), {repr(bat_filename)})
    sys.exit(subprocess.run(["cmd.exe", "/c", bat]).returncode)
if __name__ == "__main__": main()
'''
    else:
        # Tryb wrapper: zawartosc .bat zaszyfrowana w stringu Python
        wrapper = f'''\
import os, sys, tempfile, subprocess
{password_guard}
BAT = {repr(bat_content)}
def main():
    with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bat", delete=False,
            encoding="mbcs", errors="replace") as t:
        t.write(BAT); tmp = t.name
    try:
        sys.exit(subprocess.run(["cmd.exe","/c",tmp]).returncode)
    finally:
        try: os.unlink(tmp)
        except OSError: pass
if __name__ == "__main__": main()
'''

    temp_dir = tempfile.mkdtemp(prefix="bat2exe_")
    try:
        py_path = os.path.join(temp_dir, f"{bat_name}.py")
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(wrapper)

        # generuj version-info jesli podano metadane
        ver_file = None
        if metadata:
            def _parse_ver(s):
                parts = (s or "1.0.0.0").split(".")
                parts = [p for p in parts if p.isdigit()]
                while len(parts) < 4:
                    parts.append("0")
                return tuple(int(x) for x in parts[:4])

            ver   = _parse_ver(metadata.get("meta_version", "") or "1.0.0.0")
            prod  = metadata.get("meta_product",     "") or "BAT/CMD-2-EXE"
            comp  = metadata.get("meta_company",     "") or "Sebastian Januchowski"
            desc  = metadata.get("meta_description", "") or "polsoft.ITS Batch Compiler"
            copy_ = metadata.get("meta_copyright",   "") or "2026 Free License"
            vs    = ".".join(str(x) for x in ver)
            lines = [
                "VSVersionInfo(",
                f"  ffi=FixedFileInfo(filevers={ver}, prodvers={ver},",
                "    mask=0x3f, flags=0x0, OS=0x4, fileType=0x1,",
                "    subtype=0x0, date=(0,0)),",
                "  kids=[",
                "    StringFileInfo([StringTable('040904B0', [",
                f"      StringStruct('CompanyName', {repr(comp)}),",
                f"      StringStruct('FileDescription', {repr(desc)}),",
                f"      StringStruct('FileVersion', {repr(vs)}),",
                f"      StringStruct('InternalName', {repr(bat_name)}),",
                f"      StringStruct('LegalCopyright', {repr(copy_)}),",
                f"      StringStruct('OriginalFilename', {repr(bat_name+'.exe')}),",
                f"      StringStruct('ProductName', {repr(prod)}),",
                f"      StringStruct('ProductVersion', {repr(vs)}),",
                "    ])]),",
                "    VarFileInfo([VarStruct('Translation', [1033, 1200])])",
                "  ]",
                ")",
            ]
            ver_file = os.path.join(temp_dir, "version_info.txt")
            with open(ver_file, "w", encoding="utf-8") as vf:
                vf.write("\n".join(lines))
            log_callback(T("log_ver_info", prod=prod, ver=vs))

        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            f"--distpath={output_dir}",
            f"--workpath={os.path.join(temp_dir,'build')}",
            f"--specpath={temp_dir}",
            f"--name={bat_name}",
        ]
        if ver_file:
            cmd.append(f"--version-file={ver_file}")
        if embed:
            # dolacz plik .bat jako zasob (dostepny przez sys._MEIPASS)
            cmd.append(f"--add-data={bat_path}{os.pathsep}.")
            log_callback(T("log_embed_attach", name=bat_filename))
        if noconsole:
            cmd.append("--noconsole")
        if icon and os.path.isfile(icon):
            ico = _ensure_ico(icon, temp_dir, log_callback)
            cmd.append(f"--icon={ico}")
        cmd.append(py_path)

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        log_buf = []
        for line in proc.stdout:
            stripped = line.rstrip()
            log_buf.append(stripped)
            log_callback(stripped)
        proc.wait()

        log_text = "\n".join(log_buf)

        if proc.returncode != 0:
            if "PermissionError" in log_text or "WinError 5" in log_text or "Access is denied" in log_text:
                raise PermissionError(T("err_no_access", name=bat_name))
            raise RuntimeError(T("err_pyinstaller", code=proc.returncode))

        exe_path = os.path.join(output_dir, f"{bat_name}.exe")
        if not os.path.isfile(exe_path):
            raise FileNotFoundError(T("err_no_exe", path=exe_path))
        return exe_path
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ─────────────────────────────────────────────
#  Kompresja EXE (UPX / LZMA)
# ─────────────────────────────────────────────

def _find_upx() -> str | None:
    """Szuka upx.exe w PATH i typowych lokalizacjach. Zwraca ścieżkę lub None."""
    found = shutil.which("upx") or shutil.which("upx.exe")
    if found:
        return found
    for base in (os.path.dirname(os.path.abspath(__file__)), os.getcwd()):
        for name in ("upx.exe", "upx"):
            c = os.path.join(base, name)
            if os.path.isfile(c):
                return c
    for root in (
        os.environ.get("ProgramFiles", ""),
        os.environ.get("ProgramFiles(x86)", ""),
        os.path.expanduser("~"),
    ):
        for sub in ("upx", "upx-win64", "upx-win32", "tools\\upx"):
            c = os.path.join(root, sub, "upx.exe")
            if os.path.isfile(c):
                return c
    return None


def _compress_upx(exe_path: str, level: int = 9, log_callback=None) -> None:
    """Kompresuje EXE przez UPX. Rzuca wyjątek jeśli UPX niedostępny."""
    def _log(m):
        if log_callback: log_callback(m)
    upx = _find_upx()
    if not upx:
        raise FileNotFoundError(
            "UPX not found!\nDownload from https://upx.github.io/ and place next to the script or add to PATH."
        )
    size_before = os.path.getsize(exe_path)
    _log(f"[UPX] Size before: {size_before:,} B  →  compressing (level -{level})...")
    proc = subprocess.run(
        [upx, f"-{level}", exe_path],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    for line in (proc.stdout + proc.stderr).splitlines():
        s = line.strip()
        if s:
            _log(f"[UPX] {s}")
    if proc.returncode not in (0, 1, 2):
        raise RuntimeError(f"[UPX] exited with error (code {proc.returncode})")
    size_after = os.path.getsize(exe_path)
    saved = size_before - size_after
    pct   = int(saved * 100 / size_before) if size_before else 0
    _log(f"[UPX] ✔  {size_before:,} B  →  {size_after:,} B  (saved {saved:,} B = {pct}%)")


def _compress_lzma(exe_path: str, log_callback=None) -> None:
    """
    Własny algorytm: odczytuje EXE, kompresuje LZMA i dołącza
    samouwalniający się stub + payload.
    """
    def _log(m):
        if log_callback: log_callback(m)

    size_before = os.path.getsize(exe_path)
    _log(f"[LZMA] Size before: {size_before:,} B  →  compressing (preset 9)...")

    with open(exe_path, "rb") as f:
        original_data = f.read()

    compressed = lzma.compress(original_data, preset=9 | lzma.PRESET_EXTREME)
    _log(f"[LZMA] Payload compressed: {len(compressed):,} B")

    stub_code = r'''
import os, sys, lzma, tempfile, subprocess, struct
def _main():
    exe_self = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    with open(exe_self, "rb") as f:
        data = f.read()
    MARKER = b"\x00LZMA_BAT2EXE\x00"
    pos = data.rfind(MARKER)
    if pos == -1:
        print("[stub] Payload nie znaleziony!", file=sys.stderr); sys.exit(1)
    plen = struct.unpack_from("<I", data, pos + len(MARKER))[0]
    payload = data[pos + len(MARKER) + 4 : pos + len(MARKER) + 4 + plen]
    original = lzma.decompress(payload)
    fd, tmp = tempfile.mkstemp(suffix=".exe", prefix="_b2e_")
    try:
        os.write(fd, original); os.close(fd)
        r = subprocess.run([tmp] + sys.argv[1:])
        sys.exit(r.returncode)
    finally:
        try: os.unlink(tmp)
        except OSError: pass
if __name__ == "__main__": _main()
'''

    tmp_dir = tempfile.mkdtemp(prefix="lzma_stub_")
    try:
        stub_py = os.path.join(tmp_dir, "_stub.py")
        with open(stub_py, "w", encoding="utf-8") as sf:
            sf.write(stub_code)
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            f"--distpath={tmp_dir}",
            f"--workpath={os.path.join(tmp_dir, 'build')}",
            f"--specpath={tmp_dir}",
            "--name=_stub",
            "--noconsole",
            stub_py,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            raise RuntimeError("PyInstaller (stub LZMA) zakończył się błędem:\n"
                               + "\n".join(proc.stdout.splitlines()[-10:]))
        stub_exe = os.path.join(tmp_dir, "_stub.exe")
        if not os.path.isfile(stub_exe):
            raise FileNotFoundError("Brak pliku stub.exe po kompilacji LZMA!")
        with open(stub_exe, "rb") as f:
            stub_data = f.read()
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    MARKER = b"\x00LZMA_BAT2EXE\x00"
    final = stub_data + MARKER + struct.pack("<I", len(compressed)) + compressed
    with open(exe_path, "wb") as f:
        f.write(final)

    size_after = os.path.getsize(exe_path)
    saved = size_before - size_after
    pct   = int(saved * 100 / size_before) if size_before else 0
    sign  = "zaoszczędzono" if saved >= 0 else "powiększono o"
    _log(f"[LZMA] ✔  {size_before:,} B  →  {size_after:,} B  "
         f"({sign} {abs(saved):,} B = {abs(pct)}%)")


# ─────────────────────────────────────────────
#  Persystencja ustawień
# ─────────────────────────────────────────────

_CFG_DIR  = Path(os.environ.get("APPDATA", Path.home())) / "bat2exe_gui"
_CFG_FILE = _CFG_DIR / "settings.json"

def _load_cfg() -> dict:
    try:
        return json.loads(_CFG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_cfg(data: dict):
    try:
        _CFG_DIR.mkdir(parents=True, exist_ok=True)
        _CFG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass



DARK_BG    = "#1a1a2e"
PANEL_BG   = "#16213e"
ACCENT     = "#e94560"
ACCENT2    = "#0f3460"
TEXT_LIGHT = "#eaeaea"
TEXT_DIM   = "#8888aa"
FONT_MONO  = ("Consolas", 8)
FONT_UI    = ("Segoe UI", 9)
FONT_HEAD  = ("Segoe UI Semibold", 9)

THEMES = {
    # ── oryginalne motywy ──────────────────────────────────────
    "dark": {
        "DARK_BG":    "#1a1a2e",
        "PANEL_BG":   "#16213e",
        "ACCENT":     "#e94560",
        "ACCENT2":    "#0f3460",
        "TEXT_LIGHT": "#eaeaea",
        "TEXT_DIM":   "#8888aa",
        "STATUS_BG":  "#0d1117",
        "LOG_BG":     "#0d0d1a",
        "ENTRY_BG":   "#0f1f3d",
        "LOG_FG":     "#c8d6e5",
    },
    "light": {
        "DARK_BG":    "#f0f2f8",
        "PANEL_BG":   "#dde3f0",
        "ACCENT":     "#c0392b",
        "ACCENT2":    "#2980b9",
        "TEXT_LIGHT": "#1a1a2e",
        "TEXT_DIM":   "#555577",
        "STATUS_BG":  "#cdd3e0",
        "LOG_BG":     "#ffffff",
        "ENTRY_BG":   "#e8ecf5",
        "LOG_FG":     "#1a1a2e",
    },
    # ── SKIN: Cyberpunk (neon żółty + czarny) ─────────────────
    "cyberpunk": {
        "DARK_BG":    "#0a0a0f",
        "PANEL_BG":   "#11111a",
        "ACCENT":     "#f0e030",
        "ACCENT2":    "#1a1a2a",
        "TEXT_LIGHT": "#f5f5c8",
        "TEXT_DIM":   "#888866",
        "STATUS_BG":  "#050508",
        "LOG_BG":     "#050508",
        "ENTRY_BG":   "#14140f",
        "LOG_FG":     "#c8c870",
    },
    # ── SKIN: Hacker / Matrix (zielony terminal) ───────────────
    "hacker": {
        "DARK_BG":    "#030f03",
        "PANEL_BG":   "#051405",
        "ACCENT":     "#00ff41",
        "ACCENT2":    "#003300",
        "TEXT_LIGHT": "#a0ffa0",
        "TEXT_DIM":   "#336633",
        "STATUS_BG":  "#010801",
        "LOG_BG":     "#010801",
        "ENTRY_BG":   "#041004",
        "LOG_FG":     "#33ff66",
    },
    # ── SKIN: Ocean (morski błękit) ────────────────────────────
    "ocean": {
        "DARK_BG":    "#0b1d2e",
        "PANEL_BG":   "#0e2a40",
        "ACCENT":     "#00b4d8",
        "ACCENT2":    "#023e58",
        "TEXT_LIGHT": "#caf0f8",
        "TEXT_DIM":   "#5588aa",
        "STATUS_BG":  "#060f18",
        "LOG_BG":     "#060f18",
        "ENTRY_BG":   "#0a1e30",
        "LOG_FG":     "#90e0ef",
    },
    # ── SKIN: Sunset / Warm (pomarańczowo-fioletowy) ──────────
    "sunset": {
        "DARK_BG":    "#1e0e2e",
        "PANEL_BG":   "#2a1040",
        "ACCENT":     "#ff6b35",
        "ACCENT2":    "#4a1060",
        "TEXT_LIGHT": "#fde8d8",
        "TEXT_DIM":   "#996688",
        "STATUS_BG":  "#0f0718",
        "LOG_BG":     "#0f0718",
        "ENTRY_BG":   "#221030",
        "LOG_FG":     "#ffbb88",
    },
}

# Kolejność skinów w cyklu (kliknięcie przycisku 🎨 przeskakuje do następnego)
SKIN_CYCLE = ["dark", "light", "cyberpunk", "hacker", "ocean", "sunset"]

# Etykiety wyświetlane w tooltipie / oknie wyboru
SKIN_LABELS = {
    "dark":      "🌑  Dark (default)",
    "light":     "☀  Light",
    "cyberpunk": "⚡  Cyberpunk",
    "hacker":    "💻  Hacker / Matrix",
    "ocean":     "🌊  Ocean",
    "sunset":    "🌅  Sunset",
}


# ─────────────────────────────────────────────
#  Ikona aplikacji (osadzona base64 PNG 256x256)
# ─────────────────────────────────────────────
ICON_B64 = (
    "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"
    "RU5ErkJggg=="
)

WATERMARK_B64 = (
    "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"
)


def _get_app_icon(size: int = 64):
    """
    Zwraca PhotoImage z osadzonej ikony PNG przeskalowanej do <size>x<size>.
    Wymaga Pillow. Jeśli Pillow niedostępny – zwraca None.
    """
    try:
        import base64 as _b64, io as _io
        from PIL import Image as _PI, ImageTk as _PITk
        raw = _b64.b64decode(ICON_B64)
        img = _PI.open(_io.BytesIO(raw)).convert("RGBA").resize(
            (size, size), _PI.LANCZOS)
        return _PITk.PhotoImage(img)
    except Exception:
        return None
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self._cfg = _load_cfg()

        # wczytaj język z ustawień
        global _current_lang
        _current_lang = self._cfg.get("lang", "pl")

        # wczytaj skin wcześnie — potrzebny przed _build_ui (globalne stałe kolorów)
        _saved_skin = self._cfg.get("skin", "dark")
        if _saved_skin not in THEMES:
            _saved_skin = "dark"
        self._theme_mode = _saved_skin
        # Ustaw globalne stałe na wartości wybranego skinu od razu
        _st = THEMES[_saved_skin]
        global DARK_BG, PANEL_BG, ACCENT, ACCENT2, TEXT_LIGHT, TEXT_DIM
        DARK_BG    = _st["DARK_BG"]
        PANEL_BG   = _st["PANEL_BG"]
        ACCENT     = _st["ACCENT"]
        ACCENT2    = _st["ACCENT2"]
        TEXT_LIGHT = _st["TEXT_LIGHT"]
        TEXT_DIM   = _st["TEXT_DIM"]

        self.title(T("app_title"))
        self.minsize(480, 560)
        self.resizable(True, True)
        self.configure(bg=DARK_BG)

        # ── ikona okna z osadzonej grafiki ──
        self._app_icon_img = _get_app_icon(64)   # trzymaj referencję (GC!)
        if self._app_icon_img:
            try:
                self.iconphoto(True, self._app_icon_img)
            except Exception:
                pass

        self._build_ui()

        # zastosuj skin (odświeża kolory widgetów stworzonych przez _build_ui)
        self._apply_theme(self._theme_mode)

        # przywróć geometrię lub wyśrodkuj
        geo = self._cfg.get("geometry")
        if geo:
            try:
                self.geometry(geo)
            except Exception:
                self._center()
        else:
            self.geometry("520x620")
            self._center()

        # przywróć ostatni folder output
        last_out = self._cfg.get("last_output_dir", "")
        if last_out and os.path.isdir(last_out):
            self.out_var.set(last_out)

        # zapisz geometrię przy zamknięciu
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── układanie widgetów ─────────────────

    def _build_ui(self):
        # ─ Nagłówek ─
        hdr = tk.Frame(self, bg=ACCENT2, height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # ikona w nagłówku
        self._hdr_icon_img = _get_app_icon(54)
        if self._hdr_icon_img:
            tk.Label(hdr, image=self._hdr_icon_img,
                     bg=ACCENT2, bd=0).pack(side="left", padx=(10, 4), pady=10)
            self._hdr_title_lbl = tk.Label(hdr, text=T("app_subtitle"),
                     font=("Segoe UI Semibold", 22), bg=ACCENT2,
                     fg=TEXT_LIGHT)
            self._hdr_title_lbl.pack(side="left", padx=(0, 10), pady=15)
        else:
            self._hdr_title_lbl = tk.Label(hdr, text="⚙  " + T("app_subtitle"),
                     font=("Segoe UI Semibold", 25), bg=ACCENT2,
                     fg=TEXT_LIGHT)
            self._hdr_title_lbl.pack(side="left", padx=10, pady=15)

        tk.Label(hdr, text="polsoft.ITS™",
                 font=("Segoe UI", 13), bg=ACCENT2,
                 fg=TEXT_DIM).pack(side="right", padx=12)

        # ─ Panel opcji ─
        opt = tk.Frame(self, bg=PANEL_BG, padx=10, pady=6)
        opt.pack(fill="x", padx=0, pady=(0, 0))

        self._row_bat(opt)
        self._row_out(opt)
        self._row_icon(opt)
        self._row_name(opt)
        self._row_flags(opt)
        self._row_btn(opt)

        # ─ Separator ─
        sep = tk.Frame(self, bg=ACCENT, height=2)
        sep.pack(fill="x")

        # ─ Konsola logu ─
        log_frame = tk.Frame(self, bg=DARK_BG)
        log_frame.pack(fill="both", expand=True, padx=6, pady=4)

        self._log_lbl = tk.Label(log_frame, text=T("lbl_log"), font=FONT_HEAD,
                 bg=DARK_BG, fg=TEXT_DIM)
        self._log_lbl.pack(anchor="w")

        txt_frame = tk.Frame(log_frame, bg="#0d0d1a",
                             highlightbackground=ACCENT2,
                             highlightthickness=1)
        txt_frame.pack(fill="both", expand=True)

        self.log = tk.Text(
            txt_frame,
            font=FONT_MONO,
            bg="#0d0d1a", fg="#c8d6e5",
            insertbackground=ACCENT,
            selectbackground=ACCENT2,
            relief="flat", bd=0,
            wrap="word", state="disabled",
        )
        # ── tagi kolorów logu ──
        self.log.tag_configure("err",     foreground="#ff5f5f", font=("Consolas", 8, "bold"))
        self.log.tag_configure("warn",    foreground="#f0a500")
        self.log.tag_configure("ok",      foreground="#4caf50", font=("Consolas", 8, "bold"))
        self.log.tag_configure("info",    foreground="#5599dd")
        self.log.tag_configure("path",    foreground="#a78bfa")   # ścieżki plików
        self.log.tag_configure("section", foreground="#38bdf8", font=("Consolas", 8, "bold"))  # nagłówki etapów
        self.log.tag_configure("dim",     foreground="#4a4a6a")   # mało ważne linie
        sb = ttk.Scrollbar(txt_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True, padx=6, pady=4)


        # ─ Pasek statusu ─
        status_bar = tk.Frame(self, bg="#0d1117", height=26)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        # lewa strona: ikona + tekst statusu
        left = tk.Frame(status_bar, bg="#0d1117")
        left.pack(side="left", fill="y")

        self._status_icon_var = tk.StringVar(value="●")
        self._status_icon_lbl = tk.Label(
            left, textvariable=self._status_icon_var,
            font=("Segoe UI", 9), bg="#0d1117", fg="#4caf50",
            padx=8)
        self._status_icon_lbl.pack(side="left", fill="y")

        self.status_var = tk.StringVar(value=T("status_ready"))
        tk.Label(left, textvariable=self.status_var,
                 font=("Segoe UI", 9), bg="#0d1117",
                 fg=TEXT_DIM, anchor="w").pack(side="left", fill="y")

        # prawa strona (pack side=right kolejność: najpierw = najdalej z prawej)
        # 1. szpilka — skrajnie prawa
        self._topmost = False
        self._pin_btn = tk.Label(
            status_bar,
            text="📌",
            font=("Segoe UI", 11),
            bg="#0d1117", fg=TEXT_DIM,
            cursor="hand2",
            padx=8,
        )
        self._pin_btn.pack(side="right", fill="y")
        self._pin_btn.bind("<Button-1>", self._toggle_topmost)
        self._pin_btn.bind("<Enter>", lambda e: self._pin_btn.configure(fg=ACCENT))
        self._pin_btn.bind("<Leave>", lambda e: self._pin_btn.configure(
            fg=ACCENT if self._topmost else TEXT_DIM))

        # 2. separator | szpilka
        tk.Frame(status_bar, bg=ACCENT2, width=1).pack(side="right", fill="y")

        # 3. ikona skin/theme — miedzy szpilka a about
        skin_icons = {
            "dark": "🌑", "light": "☀",
            "cyberpunk": "⚡", "hacker": "💻",
            "ocean": "🌊", "sunset": "🌅",
        }
        self._theme_btn = tk.Label(
            status_bar, text=skin_icons.get(self._theme_mode, "🎨"),
            font=("Segoe UI", 12), bg="#0d1117", fg=THEMES[self._theme_mode]["ACCENT"],
            cursor="hand2", padx=8,
        )
        self._theme_btn.pack(side="right", fill="y")
        self._theme_btn.bind("<Button-1>", lambda e: self._toggle_theme())
        self._theme_btn.bind("<Button-3>", self._show_skin_picker)  # PKM → selektor
        self._theme_btn.bind("<Enter>", lambda e: self._theme_btn.configure(fg=ACCENT))
        self._theme_btn.bind("<Leave>", lambda e: self._theme_btn.configure(
            fg="#f0a500" if self._theme_mode == "dark" else "#5599dd"))

        # separator | theme
        tk.Frame(status_bar, bg=ACCENT2, width=1).pack(side="right", fill="y")

        # 🌐 przełącznik języka PL/EN
        self._lang_btn = tk.Label(
            status_bar, text=T("lang_switch_label"),
            font=("Segoe UI Semibold", 9), bg="#0d1117", fg=TEXT_DIM,
            cursor="hand2", padx=8,
        )
        self._lang_btn.pack(side="right", fill="y")
        self._lang_btn.bind("<Button-1>", lambda e: self._toggle_lang())
        self._lang_btn.bind("<Enter>", lambda e: self._lang_btn.configure(fg="#38bdf8"))
        self._lang_btn.bind("<Leave>", lambda e: self._lang_btn.configure(fg=TEXT_DIM))

        # separator | lang
        tk.Frame(status_bar, bg=ACCENT2, width=1).pack(side="right", fill="y")

        # separator | theme
        tk.Frame(status_bar, bg=ACCENT2, width=1).pack(side="right", fill="y")

        # 4. ikona info About
        self._info_btn = tk.Label(
            status_bar, text="ⓘ",
            font=("Segoe UI", 11), bg="#0d1117", fg=TEXT_DIM,
            cursor="hand2", padx=8,
        )
        self._info_btn.pack(side="right", fill="y")
        self._info_btn.bind("<Button-1>", lambda e: self._show_about())
        self._info_btn.bind("<Enter>", lambda e: self._info_btn.configure(fg="#38bdf8"))
        self._info_btn.bind("<Leave>", lambda e: self._info_btn.configure(fg=TEXT_DIM))

        # 4. separator | info
        tk.Frame(status_bar, bg=ACCENT2, width=1).pack(side="right", fill="y")

        # 5. ikona pomocy ?
        self._help_btn = tk.Label(
            status_bar, text="?",
            font=("Segoe UI Semibold", 10), bg="#0d1117", fg=TEXT_DIM,
            cursor="hand2", padx=8,
        )
        self._help_btn.pack(side="right", fill="y")
        self._help_btn.bind("<Button-1>", lambda e: self._show_help())
        self._help_btn.bind("<Enter>", lambda e: self._help_btn.configure(fg="#f0a500"))
        self._help_btn.bind("<Leave>", lambda e: self._help_btn.configure(fg=TEXT_DIM))

        # 6. separator | ?
        tk.Frame(status_bar, bg=ACCENT2, width=1).pack(side="right", fill="y")

        # 3. licznik czasu
        self._elapsed_var = tk.StringVar(value="")
        tk.Label(status_bar, textvariable=self._elapsed_var,
                 font=("Consolas", 9), bg="#0d1117",
                 fg=TEXT_DIM, anchor="e", padx=10).pack(side="right", fill="y")

        # 4. separator | licznik
        tk.Frame(status_bar, bg=ACCENT2, width=1).pack(side="right", fill="y")

        # 5. nazwa pliku
        self._file_var = tk.StringVar(value="")
        tk.Label(status_bar, textvariable=self._file_var,
                 font=("Segoe UI", 9), bg="#0d1117",
                 fg="#5577aa", anchor="center").pack(side="right", padx=12, fill="y")

        self._timer_id  = None
        self._start_ts  = None

    # ── wiersze formularza ─────────────────

    def _lbl(self, parent, text, row):
        lbl = tk.Label(parent, text=text, font=FONT_UI,
                       bg=PANEL_BG, fg=TEXT_DIM,
                       width=12, anchor="e")
        lbl.grid(row=row, column=0, sticky="e", pady=2, padx=(0, 6))
        # przechowaj referencję wg numeru wiersza
        if not hasattr(self, "_form_lbls"):
            self._form_lbls = {}
        self._form_lbls[row] = lbl
        return lbl

    def _entry(self, parent, var, row):
        e = tk.Entry(parent, textvariable=var,
                     font=FONT_UI, bg="#0f1f3d", fg=TEXT_LIGHT,
                     insertbackground=ACCENT,
                     relief="flat", bd=0,
                     highlightbackground=ACCENT2,
                     highlightthickness=1)
        e.grid(row=row, column=1, sticky="ew", ipady=2)
        return e

    def _browse_btn(self, parent, text, cmd, row):
        b = tk.Button(parent, text=text, font=FONT_UI,
                      bg=ACCENT2, fg=TEXT_LIGHT,
                      activebackground=ACCENT,
                      activeforeground=TEXT_LIGHT,
                      relief="flat", bd=0, padx=10,
                      cursor="hand2", command=cmd)
        b.grid(row=row, column=2, padx=(6, 0), pady=2, sticky="ew")
        # przechowaj referencję wg numeru wiersza
        if not hasattr(self, "_browse_btns"):
            self._browse_btns = {}
        self._browse_btns[row] = b
        return b

    def _row_bat(self, p):
        self.bat_var = tk.StringVar()
        self._lbl(p, T("lbl_bat"), 0)
        self._entry(p, self.bat_var, 0)
        self._browse_btn(p, T("btn_browse"), self._pick_bat, 0)
        p.columnconfigure(1, weight=1)

    def _row_out(self, p):
        self.out_var = tk.StringVar()
        self._lbl(p, T("lbl_out"), 1)
        self._entry(p, self.out_var, 1)
        self._browse_btn(p, T("btn_browse"), self._pick_out, 1)

    def _row_icon(self, p):
        self.ico_var = tk.StringVar()
        self._lbl(p, T("lbl_icon"), 2)
        self._entry(p, self.ico_var, 2)
        self._browse_btn(p, T("btn_browse"), self._pick_ico, 2)

    def _save_builtin_ico(self) -> str | None:
        """
        Eksportuje wbudowaną ikonę PNG jako .ico do folderu tymczasowego.
        Zwraca ścieżkę do .ico lub None gdy Pillow niedostępny.
        Plik jest usuwany przy zamknięciu aplikacji.
        """
        try:
            import base64 as _b64, io as _io
            from PIL import Image as _PI
            raw = _b64.b64decode(ICON_B64)
            img = _PI.open(_io.BytesIO(raw)).convert("RGBA")
            sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
            imgs  = [img.resize(s, _PI.LANCZOS) for s in sizes]
            ico_path = os.path.join(
                tempfile.gettempdir(), "_bat2exe_builtin_icon.ico")
            imgs[0].save(ico_path, format="ICO",
                         append_images=imgs[1:], sizes=sizes)
            return ico_path
        except Exception:
            return None

    def _row_name(self, p):
        self.name_var = tk.StringVar()
        self._lbl(p, T("lbl_exe_name"), 3)   # zapisuje do self._form_lbls[3]
        e = tk.Entry(p, textvariable=self.name_var,
                     font=FONT_UI, bg="#0f1f3d", fg=TEXT_LIGHT,
                     insertbackground=ACCENT,
                     relief="flat", bd=0,
                     highlightbackground=ACCENT2,
                     highlightthickness=1)
        e.grid(row=3, column=1, sticky="ew", ipady=2)
        tk.Label(p, text=".exe", font=FONT_UI,
                 bg=PANEL_BG, fg=TEXT_DIM).grid(row=3, column=2, sticky="w", padx=(6, 0))

    def _row_flags(self, p):
        self.noconsole_var  = tk.BooleanVar(value=False)
        self.embed_var      = tk.BooleanVar(value=False)   # False=wrapper, True=embed
        self._compress_mode = "none"                        # none / upx / lzma
        self._password      = ""                            # hasło lub ""

        flags = tk.Frame(p, bg=PANEL_BG)
        flags.grid(row=4, column=0, columnspan=3, sticky="ew", pady=3)
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)
        p.columnconfigure(2, weight=1)

        W, H = 42, 22

        # ── Konsola ──
        col_con = tk.Frame(flags, bg=PANEL_BG)
        col_con.pack(side="left", expand=True)

        self._sw_canvas = tk.Canvas(col_con, width=W, height=H,
                                    bg=PANEL_BG, highlightthickness=0,
                                    cursor="hand2")
        self._sw_canvas.pack()
        self._sw_canvas.create_oval(0, 0, H, H,   fill="#4caf50", outline="", tags="track_l")
        self._sw_canvas.create_oval(W-H, 0, W, H, fill="#4caf50", outline="", tags="track_r")
        self._sw_canvas.create_rectangle(H//2, 0, W-H//2, H, fill="#4caf50", outline="", tags="track_m")
        self._sw_canvas.create_oval(2, 2, H-2, H-2, fill="white", outline="", tags="thumb")
        self._sw_canvas.bind("<Button-1>", lambda e: self._toggle_console())
        self._console_lbl = tk.Label(col_con, text=T("lbl_console"), font=("Segoe UI", 8),
                 bg=PANEL_BG, fg=TEXT_DIM)
        self._console_lbl.pack()

        # ── Wrapper / Embed ──
        col_we = tk.Frame(flags, bg=PANEL_BG)
        col_we.pack(side="left", expand=True)

        self._em_canvas = tk.Canvas(col_we, width=W, height=H,
                                    bg=PANEL_BG, highlightthickness=0,
                                    cursor="hand2")
        self._em_canvas.pack()
        self._em_canvas.create_oval(0, 0, H, H,   fill="#4caf50", outline="", tags="em_l")
        self._em_canvas.create_oval(W-H, 0, W, H, fill="#4caf50", outline="", tags="em_r")
        self._em_canvas.create_rectangle(H//2, 0, W-H//2, H, fill="#4caf50", outline="", tags="em_m")
        self._em_canvas.create_oval(2, 2, H-2, H-2, fill="white", outline="", tags="em_thumb")
        self._em_canvas.bind("<Button-1>", lambda e: self._toggle_embed())

        self._embed_lbl = tk.Label(col_we, text=T("embed_wrapper"),
                                   font=("Segoe UI", 8),
                                   bg=PANEL_BG, fg="#4caf50")
        self._embed_lbl.pack()

        # ── Kompresja (3-stanowy: none → UPX → LZMA → none) ──
        col_cmp = tk.Frame(flags, bg=PANEL_BG)
        col_cmp.pack(side="left", expand=True)

        self._cmp_canvas = tk.Canvas(col_cmp, width=W, height=H,
                                     bg=PANEL_BG, highlightthickness=0,
                                     cursor="hand2")
        self._cmp_canvas.pack()
        self._cmp_canvas.create_oval(0, 0, H, H,   fill="#555577", outline="", tags="cmp_l")
        self._cmp_canvas.create_oval(W-H, 0, W, H, fill="#555577", outline="", tags="cmp_r")
        self._cmp_canvas.create_rectangle(H//2, 0, W-H//2, H, fill="#555577", outline="", tags="cmp_m")
        self._cmp_canvas.create_oval(2, 2, H-2, H-2, fill="white", outline="", tags="cmp_thumb")
        self._cmp_canvas.bind("<Button-1>", lambda e: self._toggle_compress())

        self._cmp_lbl = tk.Label(col_cmp, text=T("cmp_none"),
                                 font=("Segoe UI", 8),
                                 bg=PANEL_BG, fg=TEXT_DIM)
        self._cmp_lbl.pack()

        # ── Hasło (toggle: brak ↔ aktywne) ──
        col_pwd = tk.Frame(flags, bg=PANEL_BG)
        col_pwd.pack(side="left", expand=True)

        self._pwd_canvas = tk.Canvas(col_pwd, width=W, height=H,
                                     bg=PANEL_BG, highlightthickness=0,
                                     cursor="hand2")
        self._pwd_canvas.pack()
        self._pwd_canvas.create_oval(0, 0, H, H,   fill="#555577", outline="", tags="pwd_l")
        self._pwd_canvas.create_oval(W-H, 0, W, H, fill="#555577", outline="", tags="pwd_r")
        self._pwd_canvas.create_rectangle(H//2, 0, W-H//2, H, fill="#555577", outline="", tags="pwd_m")
        self._pwd_canvas.create_oval(2, 2, H-2, H-2, fill="white", outline="", tags="pwd_thumb")
        self._pwd_canvas.bind("<Button-1>", lambda e: self._toggle_password())

        self._pwd_lbl = tk.Label(col_pwd, text=T("pwd_lbl_inactive"),
                                 font=("Segoe UI", 8),
                                 bg=PANEL_BG, fg=TEXT_DIM)
        self._pwd_lbl.pack()

    def _toggle_embed(self):
        self.embed_var.set(not self.embed_var.get())
        on = self.embed_var.get()   # True = embed
        W, H = 42, 22
        color = "#38bdf8" if on else "#4caf50"
        for tag in ("em_l", "em_r", "em_m"):
            self._em_canvas.itemconfigure(tag, fill=color)
        if on:
            self._em_canvas.coords("em_thumb", W-H+2, 2, W-2, H-2)
            self._embed_lbl.configure(text=T("embed_embed"), fg="#38bdf8")
        else:
            self._em_canvas.coords("em_thumb", 2, 2, H-2, H-2)
            self._embed_lbl.configure(text=T("embed_wrapper"), fg="#4caf50")

    def _toggle_console(self):
        self.noconsole_var.set(not self.noconsole_var.get())
        off = self.noconsole_var.get()
        W, H = 42, 22
        color = "#e94560" if off else "#4caf50"
        for tag in ("track_l", "track_r", "track_m"):
            self._sw_canvas.itemconfigure(tag, fill=color)
        if off:
            self._sw_canvas.coords("thumb", W-H+2, 2, W-2, H-2)
        else:
            self._sw_canvas.coords("thumb", 2, 2, H-2, H-2)

    def _toggle_compress(self):
        """
        Cykliczny przełącznik kompresji:
          none (szary, lewo) → UPX (pomarańczowy, środek) → LZMA (fioletowy, prawo) → none
        """
        cycle = {"none": "upx", "upx": "lzma", "lzma": "none"}
        self._compress_mode = cycle.get(self._compress_mode, "none")
        mode = self._compress_mode
        W, H = 42, 22

        if mode == "none":
            color, txt, txt_fg = "#555577", T("cmp_none"), TEXT_DIM
            self._cmp_canvas.coords("cmp_thumb", 2, 2, H-2, H-2)
        elif mode == "upx":
            color, txt, txt_fg = "#f0a500", "UPX", "#f0a500"
            mid = W // 2
            self._cmp_canvas.coords("cmp_thumb", mid-H//2+2, 2, mid+H//2-2, H-2)
        else:  # lzma
            color, txt, txt_fg = "#a78bfa", "LZMA", "#a78bfa"
            self._cmp_canvas.coords("cmp_thumb", W-H+2, 2, W-2, H-2)

        for tag in ("cmp_l", "cmp_r", "cmp_m"):
            self._cmp_canvas.itemconfigure(tag, fill=color)
        self._cmp_lbl.configure(text=txt, fg=txt_fg)

    def _toggle_password(self):
        """
        Przełącznik hasła:
          brak → otwiera dialog ustawiania hasła
          aktywne → pyta czy usunąć hasło
        """
        W, H = 42, 22
        if not self._password:
            # Otwórz dialog ustawiania hasła
            self._show_password_dialog()
        else:
            # Hasło już ustawione — zapytaj o usunięcie
            if messagebox.askyesno(T("pwd_ask_remove_title"), T("pwd_ask_remove_body"), default="no"):
                self._password = ""
                for tag in ("pwd_l", "pwd_r", "pwd_m"):
                    self._pwd_canvas.itemconfigure(tag, fill="#555577")
                self._pwd_canvas.coords("pwd_thumb", 2, 2, H-2, H-2)
                self._pwd_lbl.configure(text=T("pwd_lbl_inactive"), fg=TEXT_DIM)
                self.status_var.set(T("status_pwd_off"))

    def _show_password_dialog(self):
        """Okno dialogowe ustawiania/zmiany hasła do EXE."""
        dlg = tk.Toplevel(self)
        dlg.title(T("pwd_dialog_title"))
        dlg.configure(bg=DARK_BG)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        self.update_idletasks()
        w, h = 360, 260
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        # nagłówek
        hdr = tk.Frame(dlg, bg=ACCENT2, height=32)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=T("pwd_header"),
                 font=("Segoe UI Semibold", 10), bg=ACCENT2,
                 fg=TEXT_LIGHT).pack(side="left", padx=10, pady=6)

        body = tk.Frame(dlg, bg=DARK_BG, padx=14, pady=14)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=T("pwd_lbl_pwd"), font=FONT_UI,
                 bg=DARK_BG, fg=TEXT_DIM,
                 anchor="e", width=14).grid(row=0, column=0, sticky="e", pady=4)
        pwd_var = tk.StringVar(value=self._password)
        e_pwd = tk.Entry(body, textvariable=pwd_var, show="●",
                         font=FONT_UI, bg="#0f1f3d", fg=TEXT_LIGHT,
                         insertbackground=ACCENT, relief="flat", bd=0,
                         highlightbackground=ACCENT2, highlightthickness=1)
        e_pwd.grid(row=0, column=1, sticky="ew", ipady=3)

        tk.Label(body, text=T("pwd_lbl_confirm"), font=FONT_UI,
                 bg=DARK_BG, fg=TEXT_DIM,
                 anchor="e", width=14).grid(row=1, column=0, sticky="e", pady=4)
        rep_var = tk.StringVar()
        e_rep = tk.Entry(body, textvariable=rep_var, show="●",
                         font=FONT_UI, bg="#0f1f3d", fg=TEXT_LIGHT,
                         insertbackground=ACCENT, relief="flat", bd=0,
                         highlightbackground=ACCENT2, highlightthickness=1)
        e_rep.grid(row=1, column=1, sticky="ew", ipady=3)

        # pokaż/ukryj hasło
        show_var = tk.BooleanVar(value=False)
        def _toggle_show():
            ch = "" if show_var.get() else "●"
            e_pwd.configure(show=ch)
            e_rep.configure(show=ch)
        tk.Checkbutton(body, text=T("pwd_show"),
                       variable=show_var, command=_toggle_show,
                       font=("Segoe UI", 8), bg=DARK_BG, fg=TEXT_DIM,
                       selectcolor=ACCENT2, activebackground=DARK_BG,
                       activeforeground=TEXT_DIM
                       ).grid(row=2, column=1, sticky="w", pady=(2, 0))

        body.columnconfigure(1, weight=1)

        # info
        info = tk.Label(body, text=T("pwd_info"),
                        font=("Segoe UI", 8), bg=DARK_BG, fg=TEXT_DIM,
                        justify="left", wraplength=280)
        info.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="w")

        err_lbl = tk.Label(body, text="", font=("Segoe UI", 8),
                           bg=DARK_BG, fg="#e94560")
        err_lbl.grid(row=4, column=0, columnspan=2, pady=(4, 0))

        def _save():
            p1 = pwd_var.get()
            p2 = rep_var.get()
            if not p1:
                err_lbl.configure(text=T("pwd_err_empty"))
                return
            if len(p1) < 4:
                err_lbl.configure(text=T("pwd_err_short"))
                return
            if p1 != p2:
                err_lbl.configure(text=T("pwd_err_mismatch"))
                return
            self._password = p1
            W2, H2 = 42, 22
            for tag in ("pwd_l", "pwd_r", "pwd_m"):
                self._pwd_canvas.itemconfigure(tag, fill="#e94560")
            self._pwd_canvas.coords("pwd_thumb", W2-H2+2, 2, W2-2, H2-2)
            self._pwd_lbl.configure(text=T("pwd_lbl_active"), fg="#e94560")
            self.status_var.set(T("status_pwd_active"))
            dlg.destroy()

        e_pwd.bind("<Return>", lambda e: e_rep.focus_set())
        e_rep.bind("<Return>", lambda e: _save())

        btn_row = tk.Frame(dlg, bg=DARK_BG, pady=8)
        btn_row.pack()
        tk.Button(btn_row, text=T("btn_save"), font=FONT_UI,
                  bg=ACCENT, fg=TEXT_LIGHT,
                  activebackground="#c73652", relief="flat", bd=0,
                  padx=14, pady=3, cursor="hand2",
                  command=_save).pack(side="left", padx=4)
        tk.Button(btn_row, text=T("btn_cancel"), font=FONT_UI,
                  bg=ACCENT2, fg=TEXT_LIGHT,
                  activebackground="#1a4a8a", relief="flat", bd=0,
                  padx=14, pady=3, cursor="hand2",
                  command=dlg.destroy).pack(side="left", padx=4)

        e_pwd.focus_set()

    def _row_btn(self, p):
        # wiersz 1: przyciski — outer frame rozciągnięty, inner wyśrodkowany
        btn_outer = tk.Frame(p, bg=PANEL_BG)
        btn_outer.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        btn_frame = tk.Frame(btn_outer, bg=PANEL_BG)
        btn_frame.pack(anchor="center")

        self.btn = tk.Button(
            btn_frame,
            text=T("btn_convert"),
            font=("Segoe UI Semibold", 9),
            bg=ACCENT, fg=TEXT_LIGHT,
            activebackground="#c73652",
            activeforeground=TEXT_LIGHT,
            relief="flat", bd=0,
            padx=12, pady=4,
            cursor="hand2",
            command=self._start,
        )
        self.btn.pack(side="left")

        self.dist_btn = tk.Button(
            btn_frame,
            text=T("btn_dist"),
            font=("Segoe UI Semibold", 9),
            bg=ACCENT2, fg=TEXT_LIGHT,
            activebackground="#1a4a8a",
            activeforeground=TEXT_LIGHT,
            relief="flat", bd=0,
            padx=12, pady=4,
            cursor="hand2",
            command=self._open_dist,
        )
        self.dist_btn.pack(side="left", padx=(6, 0))

        self.meta_btn = tk.Button(
            btn_frame,
            text=T("btn_metadata"),
            font=("Segoe UI Semibold", 9),
            bg="#2a2a4a", fg=TEXT_LIGHT,
            activebackground="#3a3a6a",
            activeforeground=TEXT_LIGHT,
            relief="flat", bd=0,
            padx=12, pady=4,
            cursor="hand2",
            command=self._show_metadata,
        )
        self.meta_btn.pack(side="left", padx=(6, 0))

        # wiersz 2: pasek postepu pod przyciskami
        prog_frame = tk.Frame(p, bg=PANEL_BG)
        prog_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(4, 2))

        self.progress = ttk.Progressbar(
            prog_frame, mode="indeterminate")
        self.progress.pack(fill="x")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar",
                        troughcolor=PANEL_BG,
                        background=ACCENT,
                        bordercolor=PANEL_BG,
                        lightcolor=ACCENT,
                        darkcolor=ACCENT)

    # ── dialogi wyboru pliku ───────────────

    def _show_metadata(self):
        """Okno dialogowe metadanych EXE (VersionInfo dla PyInstaller)."""
        dlg = tk.Toplevel(self)
        dlg.title(T("meta_dialog_title"))
        dlg.configure(bg=DARK_BG)
        dlg.resizable(False, False)
        dlg.grab_set()

        # wycentruj wzgledem glownego okna
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 340) // 2
        dlg.geometry(f"380x340+{x}+{y}")

        # naglowek
        hdr = tk.Frame(dlg, bg=ACCENT2, height=32)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=T("meta_header"),
                 font=("Segoe UI Semibold", 10), bg=ACCENT2,
                 fg=TEXT_LIGHT).pack(side="left", padx=10, pady=6)

        body = tk.Frame(dlg, bg=DARK_BG, padx=14, pady=10)
        body.pack(fill="both", expand=True)

        fields = [
            (T("meta_product"),     "meta_product",     "BAT/CMD-2-EXE"),
            (T("meta_version"),     "meta_version",     "1.0.0.0"),
            (T("meta_company"),     "meta_company",     "Sebastian Januchowski"),
            (T("meta_description"), "meta_description", "polsoft.ITS Batch Compiler"),
            (T("meta_copyright"),   "meta_copyright",   "2026 Free License"),
        ]

        if not hasattr(self, "_meta_vars"):
            self._meta_vars = {}
            for _, key, default in fields:
                self._meta_vars[key] = tk.StringVar(value=default)

        for row, (label, key, _) in enumerate(fields):
            tk.Label(body, text=label, font=FONT_UI,
                     bg=DARK_BG, fg=TEXT_DIM,
                     anchor="e", width=18).grid(row=row, column=0,
                                                sticky="e", pady=3, padx=(0, 6))
            tk.Entry(body, textvariable=self._meta_vars[key],
                     font=FONT_UI, bg="#0f1f3d", fg=TEXT_LIGHT,
                     insertbackground=ACCENT, relief="flat", bd=0,
                     highlightbackground=ACCENT2,
                     highlightthickness=1).grid(row=row, column=1,
                                                sticky="ew", ipady=2)
        body.columnconfigure(1, weight=1)

        tk.Label(body, text=T("meta_info"),
                 font=("Segoe UI", 8), bg=DARK_BG,
                 fg=TEXT_DIM).grid(row=len(fields), column=0,
                                   columnspan=2, pady=(10, 0))

        # przyciski
        btn_row = tk.Frame(dlg, bg=DARK_BG, pady=8)
        btn_row.pack()
        tk.Button(btn_row, text=T("btn_save"), font=FONT_UI,
                  bg=ACCENT, fg=TEXT_LIGHT,
                  activebackground="#c73652", relief="flat", bd=0,
                  padx=14, pady=3, cursor="hand2",
                  command=dlg.destroy).pack(side="left", padx=4)
        tk.Button(btn_row, text=T("btn_cancel"), font=FONT_UI,
                  bg=ACCENT2, fg=TEXT_LIGHT,
                  activebackground="#1a4a8a", relief="flat", bd=0,
                  padx=14, pady=3, cursor="hand2",
                  command=dlg.destroy).pack(side="left", padx=4)

    def _open_dist(self):
        out = self.out_var.get().strip()
        if not out:
            bat = self.bat_var.get().strip()
            out = os.path.dirname(os.path.abspath(bat)) if bat else os.getcwd()
        os.makedirs(out, exist_ok=True)
        try:
            os.startfile(out)
        except Exception:
            subprocess.Popen(["explorer", out], shell=True)

    def _on_close(self):
        geo = self.geometry()
        self._cfg["geometry"] = geo
        out = self.out_var.get().strip()
        if out:
            self._cfg["last_output_dir"] = out
        _save_cfg(self._cfg)
        self.destroy()

    def _pick_bat(self):
        path = filedialog.askopenfilename(
            title=T("dlg_pick_bat_title"),
            filetypes=[(T("dlg_bat_filter"), "*.bat"), (T("dlg_all_filter"), "*.*")])
        if path:
            self.bat_var.set(path)
            if not self.out_var.get():
                self.out_var.set(os.path.dirname(path))
            if not self.name_var.get().strip():
                self.name_var.set(os.path.splitext(os.path.basename(path))[0])

    def _pick_out(self):
        path = filedialog.askdirectory(title=T("dlg_pick_out_title"))
        if path:
            self.out_var.set(path)
            self._cfg["last_output_dir"] = path
            _save_cfg(self._cfg)

    def _pick_ico(self):
        path = filedialog.askopenfilename(
            title=T("dlg_pick_ico_title"),
            filetypes=[
                (T("dlg_ico_filter"), "*.ico *.png *.jpg *.jpeg"),
                (T("dlg_ico_ico"), "*.ico"),
                (T("dlg_ico_png"), "*.png"),
                (T("dlg_ico_jpg"), "*.jpg *.jpeg"),
                (T("dlg_all_filter"), "*.*"),
            ])
        if path:
            self.ico_var.set(path)

    # ── konwersja ─────────────────────────

    def _start(self):
        bat = self.bat_var.get().strip()
        out = self.out_var.get().strip()

        if not bat:
            messagebox.showwarning(T("msg_no_file_title"), T("msg_no_file_body"))
            return
        if not os.path.isfile(bat):
            messagebox.showerror(T("msg_bad_file_title"), T("msg_bad_file_body", path=bat))
            return
        if not out:
            out = os.path.join(os.path.dirname(os.path.abspath(bat)), "dist")
            self.out_var.set(out)

        # zawsze twórz katalog wyjściowy
        os.makedirs(out, exist_ok=True)

        self._log_clear()
        self._set_busy(True)

        # sprawdź czy .exe już istnieje
        bat_name = self.name_var.get().strip() or os.path.splitext(os.path.basename(bat))[0]
        exe_path = os.path.join(out, f"{bat_name}.exe")
        if os.path.isfile(exe_path):
            answer = messagebox.askyesno(
                T("msg_exists_title"),
                T("msg_exists_body", path=exe_path),
                icon="warning",
                default="no",
            )
            if not answer:
                self._set_busy(False)
                self.status_var.set(T("status_cancelled"))
                return

        def worker():
            try:
                meta = {}
                if hasattr(self, "_meta_vars"):
                    meta = {k: v.get().strip() for k, v in self._meta_vars.items()}
                # ikona: użyj wybranej lub wbudowanej domyślnej
                _icon_path = self.ico_var.get().strip()
                if not _icon_path:
                    _icon_path = self._save_builtin_ico() or ""
                exe = convert(
                    bat_path=bat,
                    output_dir=out,
                    icon=_icon_path or None,
                    noconsole=self.noconsole_var.get(),
                    log_callback=self._log,
                    exe_name=bat_name,
                    metadata=meta,
                    embed=self.embed_var.get(),
                    password=getattr(self, "_password", "") or None,
                )
                # ── kompresja (jeśli włączona) ──
                cmode = getattr(self, "_compress_mode", "none")
                if cmode == "upx":
                    self._log(T("log_upx"))
                    _compress_upx(exe, log_callback=self._log)
                elif cmode == "lzma":
                    self._log(T("log_lzma"))
                    _compress_lzma(exe, log_callback=self._log)
                self.after(0, self._done_ok, exe)
            except Exception as e:
                self.after(0, self._done_err, str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _done_ok(self, exe_path):
        self._set_busy(False)
        self._log(T("log_done", path=exe_path))
        self.status_var.set(T("status_ok", name=os.path.basename(exe_path)))
        self._status_icon_var.set("●")
        self._status_icon_lbl.configure(fg="#4caf50")
        self._file_var.set(exe_path)
        messagebox.showinfo(T("msg_ok_title"), T("msg_ok_body", path=exe_path))

    def _done_err(self, msg):
        self._set_busy(False)
        self._log(T("log_err", msg=msg))
        self.status_var.set(T("status_err"))
        self._status_icon_var.set("●")
        self._status_icon_lbl.configure(fg="#e94560")
        self._file_var.set("")
        messagebox.showerror(T("msg_err_title"), msg)

    # ── narzędzia ─────────────────────────

    def _set_busy(self, busy: bool):
        if busy:
            self.btn.configure(state="disabled", text=T("btn_converting"))
            self.progress.start(12)
            self.status_var.set(T("status_converting"))
            self._status_icon_lbl.configure(fg="#f0a500")
            self._status_icon_var.set("◉")
            bat_name = os.path.basename(self.bat_var.get().strip())
            self._file_var.set(bat_name)
            import time as _time
            self._start_ts = _time.time()
            self._tick_timer()
        else:
            self.btn.configure(state="normal", text=T("btn_convert"))
            self.progress.stop()
            if self._timer_id:
                self.after_cancel(self._timer_id)
                self._timer_id = None

    def _tick_timer(self):
        import time as _time
        if self._start_ts is None:
            return
        elapsed = _time.time() - self._start_ts
        m, s = divmod(int(elapsed), 60)
        self._elapsed_var.set(f"⏱ {m:02d}:{s:02d}")
        self._timer_id = self.after(1000, self._tick_timer)

    def _log(self, msg: str):
        lo = msg.lower()
        if any(k in lo for k in ("error", "błąd", "✘", "failed", "exception", "traceback")):
            tag = "err"
        elif any(k in lo for k in ("warning", "warn", "ostrzeże")):
            tag = "warn"
        elif any(k in lo for k in ("✔", "gotowe", "done", "sukces", "success", "completed successfully")):
            tag = "ok"
        elif any(k in lo for k in ("info", "building", "copying", "checking")):
            tag = "info"
        else:
            tag = None
        self.after(0, self._log_insert, msg + "\n", tag)

    def _log_insert(self, msg: str, tag=None):
        self.log.configure(state="normal")
        start = self.log.index("end")
        self.log.insert("end", msg)
        if tag:
            self.log.tag_add(tag, start, "end-1c")
        # keep only last 200 lines
        lines = int(self.log.index("end-1c").split(".")[0])
        if lines > 200:
            self.log.delete("1.0", f"{lines - 200}.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _log_clear(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _show_help(self):
        """Okno pomocy z zakladkami ttk.Notebook."""
        dlg = tk.Toplevel(self)
        dlg.title(T("help_title"))
        dlg.configure(bg=DARK_BG)
        dlg.resizable(True, True)
        dlg.minsize(500, 440)
        dlg.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width()  - 540) // 2
        y = self.winfo_y() + (self.winfo_height() - 500) // 2
        dlg.geometry(f"540x500+{x}+{y}")

        # naglowek
        hdr = tk.Frame(dlg, bg=ACCENT2, height=36)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=T("help_header"),
                 font=("Segoe UI Semibold", 10), bg=ACCENT2,
                 fg=TEXT_LIGHT).pack(side="left", padx=12, pady=6)

        # styl zakladek
        style = ttk.Style()
        style.configure("Help.TNotebook",
                        background=DARK_BG, borderwidth=0)
        style.configure("Help.TNotebook.Tab",
                        background=PANEL_BG, foreground=TEXT_DIM,
                        font=("Segoe UI", 9), padding=[10, 4])
        style.map("Help.TNotebook.Tab",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", TEXT_LIGHT)])

        nb = ttk.Notebook(dlg, style="Help.TNotebook")
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        def _tab(title, sections):
            """Tworzy zakladke z przewijalnym tekstem."""
            frame = tk.Frame(nb, bg=DARK_BG)
            nb.add(frame, text=title)

            txt = tk.Text(frame,
                          font=("Segoe UI", 9),
                          bg="#0d0d1a", fg="#c8d6e5",
                          relief="flat", bd=0, wrap="word",
                          padx=10, pady=8,
                          state="normal", cursor="arrow")
            sb = ttk.Scrollbar(frame, command=txt.yview)
            txt.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            txt.pack(fill="both", expand=True)

            # tagi
            txt.tag_configure("h1",   font=("Segoe UI Semibold", 11),
                              foreground="#38bdf8")
            txt.tag_configure("h2",   font=("Segoe UI Semibold", 9),
                              foreground="#f0a500")
            txt.tag_configure("body", font=("Segoe UI", 9),
                              foreground="#c8d6e5")
            txt.tag_configure("code", font=("Consolas", 8),
                              foreground="#a78bfa",
                              background="#0f1929")
            txt.tag_configure("ok",   font=("Segoe UI", 9),
                              foreground="#4caf50")
            txt.tag_configure("warn", font=("Segoe UI", 9),
                              foreground="#e94560")
            txt.tag_configure("sep",  foreground="#1a2a4a")

            for item in sections:
                kind = item[0]
                text = item[1]
                txt.insert("end", text + "\n", kind)

            txt.configure(state="disabled")
            return frame

        # ── ZAKLADKA 1: Opis aplikacji ─────────────────────────────────
        _tab(T("help_tab_desc"), [
            ("h1",   T("help_desc_h1")),
            ("sep",  "\u2500" * 60),
            ("body", ""),
            ("body", "Aplikacja umozliwia zamiane skryptow wsadowych Windows (.bat)"),
            ("body", "w samodzielne pliki wykonywalne (.exe) bez koniecznosci"),
            ("body", "posiadania Pythona na docelowym komputerze."),
            ("body", ""),
            ("h2",   T("help_desc_how_h")),
            ("body", T("help_desc_how1")),
            ("body", T("help_desc_how2")),
            ("body", T("help_desc_how3")),
            ("body", T("help_desc_how3b")),
            ("body", ""),
            ("h2",   T("help_desc_feat_h")),
            ("ok",   "  \u2714  Konwersja dowolnego pliku .BAT do .EXE"),
            ("ok",   "  \u2714  Wbudowana ikona aplikacji (polsoft.ITS\u2122)"),
            ("ok",   "  \u2714  Dodawanie wlasnej ikony (.ico / .png / .jpg)"),
            ("ok",   "  \u2714  Auto-konwersja PNG/JPG do ICO w locie"),
            ("ok",   "  \u2714  Osadzanie metadanych (wersja, firma, copyright)"),
            ("ok",   "  \u2714  Tryb bez konsoli (ukryte okno cmd)"),
            ("ok",   "  \u2714  Kompresja EXE: UPX lub wbudowany algorytm LZMA"),
            ("ok",   "  \u2714  Ochrona haslem (SHA-256, 3 proby przy uruchomieniu)"),
            ("ok",   "  \u2714  Dowolna nazwa wynikowego pliku .exe"),
            ("ok",   "  \u2714  Automatyczne tworzenie katalogu dist/"),
            ("ok",   "  \u2714  Dziennik konwersji z kolorowym logiem"),
            ("ok",   "  \u2714  Watermark aplikacji w oknie dziennika"),
            ("ok",   "  \u2714  Zapamietywanie ostatnich ustawien"),
            ("ok",   "  \u2714  Tryb ciemny / jasny (przelacznik w pasku statusu)"),
            ("ok",   "  \u2714  Tryb 'zawsze na wierzchu' (szpilka)"),
            ("body", ""),
            ("h2",   T("help_desc_req_h")),
            ("code", "  pip install pyinstaller"),
            ("body", T("help_desc_pillow")),
        ])

        # ── ZAKLADKA 2: Formularz ──────────────────────────────────────
        _tab(T("help_tab_form"), [
            ("h1",   T("help_form_h1")),
            ("sep",  "\u2500" * 60),
            ("body", ""),
            ("h2",   T("help_form_bat_h")),
            ("body", T("help_form_bat1")),
            ("body", T("help_form_bat2")),
            ("ok",   T("help_form_bat3")),
            ("ok",   T("help_form_bat4")),
            ("body", ""),
            ("h2",   T("help_form_out_h")),
            ("body", T("help_form_out1")),
            ("body", T("help_form_out2")),
            ("code", "  <lokalizacja pliku .bat>\\dist\\"),
            ("body", T("help_form_out3")),
            ("body", ""),
            ("h2",   T("help_form_ico_h")),
            ("body", T("help_form_ico1")),
            ("body", "Obslugiwane formaty:"),
            ("code", "  .ico   - natywny format ikon Windows (bez konwersji)"),
            ("code", "  .png   - konwertowany automatycznie do .ico"),
            ("code", "  .jpg / .jpeg - konwertowany automatycznie do .ico"),
            ("body", "Konwersja tworzy ikone w rozmiarach: 256/128/64/48/32/16 px."),
            ("warn", "  \u26a0  Jezeli Pillow nie jest zainstalowany,"),
            ("warn", "    aplikacja zainstaluje go automatycznie (pip install pillow)."),
            ("body", ""),
            ("h2",   T("help_form_name_h")),
            ("body", T("help_form_name1")),
            ("body", T("help_form_name2")),
            ("body", "Mozna wpisac dowolna nazwe, np.:"),
            ("code", "  MojProgram  \u2192  MojProgram.exe"),
            ("body", ""),
            ("h2",   T("help_form_con_h")),
            ("ok",   "  ON  (zielony)  \u2192  okno konsoli widoczne podczas dzialania"),
            ("warn", "  OFF (czerwony) \u2192  okno konsoli ukryte (flaga --noconsole)"),
            ("body", "Uzyj OFF dla aplikacji ktore nie wymagaja interakcji z uzytkownikiem."),
            ("body", ""),
            ("h2",   T("help_form_cmp_h")),
            ("body", "  Kompresja (szary, lewo)      \u2192  brak kompresji"),
            ("warn", "  UPX        (pomaranczowy, srod) \u2192  kompresor UPX"),
            ("code", "    Wymaga upx.exe w PATH lub obok skryptu."),
            ("code", "    Pobierz: https://upx.github.io/"),
            ("body", "  LZMA       (fioletowy, prawo) \u2192  wbudowany algorytm Python"),
            ("code", "    Nie wymaga zadnych zewnetrznych narzedzi."),
            ("body", ""),
            ("h2",   T("help_form_pwd_h")),
            ("body", "Kliknij aby otworzyc dialog ustawiania hasla."),
            ("warn", "  Aktywne (czerwony) \u2192  EXE pyta o haslo przy uruchomieniu"),
            ("body", "  Uzytkownik ma 3 proby. Bledne haslo = zamkniecie programu."),
            ("body", "  Haslo jest hashowane SHA-256 \u2014 nie mozna go odczytac z EXE."),
            ("ok",   "  \u2714 Kliknij ponownie aby usunac haslo."),
        ])

                # ── ZAKLADKA 3: Przyciski ──────────────────────────────────────
        _tab(T("help_tab_btns"), [
            ("h1",   T("help_btns_h1")),
            ("sep",  "\u2500" * 60),
            ("body", ""),
            ("h2",   "\u25ba  Konwertuj"),
            ("body", "Rozpoczyna proces konwersji .bat \u2192 .exe."),
            ("body", "Przycisk jest zablokowany podczas konwersji."),
            ("body", "Jezeli plik .exe juz istnieje  \u2192  pytanie o nadpisanie."),
            ("body", ""),
            ("h2",   "\U0001f4c1  Dist"),
            ("body", "Otwiera folder wyjsciowy w Eksploratorze Windows."),
            ("body", "Jesli folder nie istnieje  \u2192  zostaje utworzony."),
            ("body", ""),
            ("h2",   "\U0001f3f7  Metadane"),
            ("body", "Otwiera okno edycji metadanych osadzanych w pliku .exe."),
            ("body", "Metadane widoczne w: PPM na pliku \u2192 Wlasciwosci \u2192 Szczegoly."),
            ("code", "  Nazwa produktu / Wersja / Firma / Opis / Copyright"),
            ("body", ""),
            ("h2",   "Przelaczniki (4 suwaki, wycentrowane)"),
            ("body", ""),
            ("h2",   "  [1] Konsola"),
            ("ok",   "    ON  (zielony)  \u2192  okno cmd widoczne"),
            ("warn", "    OFF (czerwony) \u2192  okno cmd ukryte (--noconsole)"),
            ("body", ""),
            ("h2",   "  [2] Wrapper / Embed"),
            ("ok",   "    Wrapper (zielony)  \u2192  .bat osadzony jako string Python"),
            ("body", "    Embed   (niebieski) \u2192  .bat dolaczony jako plik zasobu"),
            ("body", ""),
            ("h2",   "  [3] Kompresja  (3 stany, klikaj cyklicznie)"),
            ("body", "    Szary  (lewo)      \u2192  brak kompresji"),
            ("warn", "    Pomaranczowy (srod) \u2192  UPX  (wymaga upx.exe w PATH)"),
            ("body", "    Fioletowy (prawo)  \u2192  LZMA (wbudowany, bez zewnetrznych narzedzi)"),
            ("body", "    Kompresja uruchamia sie automatycznie po konwersji."),
            ("body", ""),
            ("h2",   "  [4] Haslo"),
            ("body", "    Szary   \u2192  brak ochrony haslem"),
            ("warn", "    Czerwony \u2192  EXE pyta o haslo przy kazdym uruchomieniu"),
            ("body", "    3 proby, haslo SHA-256 (nie mozna odczytac z EXE)."),
            ("ok",   "    Kliknij ponownie aby usunac haslo."),
            ("body", ""),
            ("h2",   "Pasek postepu"),
            ("body", "Aktywny podczas konwersji i kompresji (tryb indeterminate)."),
            ("body", ""),
            ("h2",   "Pasek statusu (dol okna)  \u2014  od lewej do prawej:"),
            ("ok",   "  \u25cf  Wskaznik (zielony=OK / czerwony=blad / zolty=praca)"),
            ("body", "  Tekst statusu  \u2014  opis aktualnego stanu"),
            ("body", "  Nazwa pliku  \u2014  aktualnie przetwarzany plik"),
            ("body", "  \u23f1 Timer  \u2014  czas trwania konwersji (mm:ss)"),
            ("code", "  ?       \u2014  Pomoc (to okno)"),
            ("code", "  \u24d8       \u2014  About (informacje o programie)"),
            ("code", "  \u2600/\U0001f319  \u2014  Przelacznik ciemny/jasny motyw"),
            ("code", "  \U0001f4cc     \u2014  Szpilka: tryb 'zawsze na wierzchu'"),
        ])

        # ── ZAKLADKA 4: Dziennik ───────────────────────────────────────
        _tab(T("help_tab_log"), [
            ("h1",   T("help_log_h1")),
            ("sep",  "\u2500" * 60),
            ("body", ""),
            ("body", "Wyswietla pelny output PyInstaller oraz etapy kompresji"),
            ("body", "i weryfikacji hasla w czasie rzeczywistym."),
            ("body", ""),
            ("h2",   T("help_log_colors_h")),
            ("warn", "  Czerwony    \u2014 bledy (error, failed, traceback)"),
            ("body", "  Zolty       \u2014 ostrzezenia (warning, warn)"),
            ("ok",   "  Zielony     \u2014 sukces (\u2714, gotowe, completed)"),
            ("h2",   "  Niebieski jasny \u2014 etapy budowania (Building, Collected)"),
            ("body", "  Niebieski   \u2014 info (copying, analyzing, pyi-)"),
            ("body", "  Fioletowy   \u2014 sciezki plikow (.exe, .ico, distpath)"),
            ("body", "  Szary       \u2014 linie mniej istotne"),
            ("body", ""),
            ("h2",   T("help_log_watermark_h")),
            ("body", "  Logo polsoft.ITS\u2122 widoczne w prawym dolnym rogu dziennika."),
            ("body", "  Przyciemniony do ~13% \u2014 nie przeszkadza w czytaniu logu."),
            ("body", "  Przesunieta od scrollbara, nie zaklada GUI."),
            ("body", ""),
            ("body", "Bufor: max 200 linii (starsze sa usuwane automatycznie)."),
            ("body", "Log jest czyszczony przed kazdym nowym uruchomieniem."),
        ])

        # ── ZAKLADKA 5: Wymagania ──────────────────────────────────────
        _tab(T("help_tab_req"), [
            ("h1",   T("help_req_h1")),
            ("sep",  "\u2500" * 60),
            ("body", ""),
            ("h2",   "Python"),
            ("body", "Python 3.10 lub nowszy (wymagana skladnia X | Y)."),
            ("body", ""),
            ("h2",   "PyInstaller  (wymagany)"),
            ("code", "  pip install pyinstaller"),
            ("body", "Uzywany do budowania pliku .exe."),
            ("body", "Bez PyInstaller konwersja nie jest mozliwa."),
            ("body", ""),
            ("h2",   "Pillow  (opcjonalny)"),
            ("code", "  pip install pillow"),
            ("body", "Potrzebny tylko do konwersji ikon .png / .jpg."),
            ("ok",   "  \u2714 Jezeli brak  \u2192  aplikacja zainstaluje go automatycznie"),
            ("ok",   "    podczas pierwszej konwersji z ikona PNG/JPG."),
            ("body", ""),
            ("h2",   "Pliki konfiguracyjne"),
            ("body", "Ustawienia (ostatni folder, rozmiar okna) zapisywane w:"),
            ("code", "  %APPDATA%\\bat2exe_gui\\settings.json"),
            ("body", ""),
            ("h2",   "UPX  (opcjonalny)"),
            ("body", "Zewnetrzny kompresor plikow EXE."),
            ("code", "  Pobierz: https://upx.github.io/"),
            ("body", "Umies upx.exe obok skryptu lub dodaj do PATH."),
            ("body", "Jesli niedostepny  \u2192  uzyj kompresji LZMA (wbudowanej)."),
            ("body", ""),
            ("h2",   T("help_req_compat_h")),
            ("ok",   "  \u2714 Windows 10 / 11"),
            ("warn", "  \u26a0 Linux / macOS  \u2014 brak pelnej obslugi (cmd.exe)"),
        ])

        # przycisk zamknij
        tk.Button(dlg, text=T("help_close"), font=FONT_UI,
                  bg=ACCENT2, fg=TEXT_LIGHT,
                  activebackground=ACCENT, activeforeground=TEXT_LIGHT,
                  relief="flat", bd=0, padx=20, pady=4,
                  cursor="hand2", command=dlg.destroy).pack(pady=(0, 10))

    def _show_about(self):
        pil_status = T("about_pillow_ok") if _PIL_OK else T("about_pillow_no")
        lines = [
            T("app_title") + "  v" + __version__,
            "─" * 38,
            T("about_converts"),
            T("about_via"),
            "",
            T("about_icons"),
            "  .ico  .png  .jpg  .jpeg",
            f"Pillow (PNG/JPG→ICO): {pil_status}",
            "",
            T("about_requirements"),
            "  pip install pyinstaller",
            "  pip install pillow   (optional)",
            "",
            "─" * 38,
            f"Company : {__company__}",
            f"Author  : {__author__}",
            f"E-mail  : {__email__}",
            f"GitHub  : {__github__}",
            "",
            __copyright__,
        ]
        messagebox.showinfo(T("about_title"), "\n".join(lines))

    def _toggle_theme(self):
        """Przeskakuje do następnego skinu w cyklu."""
        idx = SKIN_CYCLE.index(self._theme_mode) if self._theme_mode in SKIN_CYCLE else 0
        self._theme_mode = SKIN_CYCLE[(idx + 1) % len(SKIN_CYCLE)]
        self._cfg["skin"] = self._theme_mode
        _save_cfg(self._cfg)
        self._apply_theme(self._theme_mode)

    def _show_skin_picker(self, event=None):
        """Okno wyboru skinu — kliknięcie prawym przyciskiem na 🎨."""
        win = tk.Toplevel(self)
        win.title("🎨  Wybierz skin / Select skin")
        win.resizable(False, False)
        win.configure(bg=THEMES[self._theme_mode]["DARK_BG"])
        win.grab_set()

        t = THEMES[self._theme_mode]

        tk.Label(win, text="🎨  Wybierz motyw / Select skin",
                 font=("Segoe UI Semibold", 11),
                 bg=t["DARK_BG"], fg=t["TEXT_LIGHT"],
                 pady=10).pack(fill="x", padx=16)

        sep = tk.Frame(win, bg=t["ACCENT"], height=2)
        sep.pack(fill="x", padx=0)

        frame = tk.Frame(win, bg=t["DARK_BG"], padx=20, pady=12)
        frame.pack(fill="both")

        for skin_key in SKIN_CYCLE:
            skin_t = THEMES[skin_key]
            is_active = (skin_key == self._theme_mode)

            row = tk.Frame(frame,
                           bg=skin_t["PANEL_BG"] if is_active else t["DARK_BG"],
                           pady=4, padx=8,
                           highlightthickness=2 if is_active else 1,
                           highlightbackground=skin_t["ACCENT"] if is_active else t["ACCENT2"])
            row.pack(fill="x", pady=3)

            # Podgląd kolorów (3 prostokąty)
            preview = tk.Frame(row, bg=t["DARK_BG"])
            preview.pack(side="left", padx=(0, 8))
            for col in [skin_t["DARK_BG"], skin_t["ACCENT"], skin_t["PANEL_BG"]]:
                tk.Frame(preview, bg=col, width=16, height=20,
                         highlightthickness=1,
                         highlightbackground=skin_t["TEXT_DIM"]).pack(side="left", padx=1)

            # Etykieta
            lbl = tk.Label(row, text=SKIN_LABELS.get(skin_key, skin_key),
                           font=("Segoe UI", 10),
                           bg=skin_t["PANEL_BG"] if is_active else t["DARK_BG"],
                           fg=skin_t["ACCENT"] if is_active else skin_t["TEXT_LIGHT"],
                           cursor="hand2", anchor="w")
            lbl.pack(side="left", fill="x", expand=True)

            # Kliknięcie — zastosuj skin i zamknij
            def _pick(k=skin_key, w=win):
                self._theme_mode = k
                self._cfg["skin"] = k
                _save_cfg(self._cfg)
                self._apply_theme(k)
                w.destroy()

            row.bind("<Button-1>", lambda e, fn=_pick: fn())
            lbl.bind("<Button-1>", lambda e, fn=_pick: fn())

        tk.Frame(win, bg=t["ACCENT2"], height=1).pack(fill="x")
        tk.Button(win, text="Zamknij / Close",
                  font=("Segoe UI", 9),
                  bg=t["ACCENT2"], fg=t["TEXT_LIGHT"],
                  relief="flat", cursor="hand2",
                  command=win.destroy,
                  padx=10, pady=4).pack(pady=10)

        win.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - win.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{x}+{y}")

    def _apply_theme(self, mode: str):
        if mode not in THEMES:
            mode = "dark"
        t = THEMES[mode]
        is_dark_mode = (mode == "dark")

        # ── ikona przycisku skinu ──────────────────────────────
        skin_icons = {
            "dark": "🌑", "light": "☀",
            "cyberpunk": "⚡", "hacker": "💻",
            "ocean": "🌊", "sunset": "🌅",
        }
        self._theme_btn.configure(
            text=skin_icons.get(mode, "🎨"),
            fg=t["ACCENT"],
        )

        # ── tło główne ────────────────────────────────────────
        self.configure(bg=t["DARK_BG"])

        # Zbuduj set wszystkich znanych kolorów tła ze wszystkich skinów,
        # żeby _recolor mógł rozpoznać KAŻDY kolor niezależnie od poprzedniego skinu.
        _all_dark_bgs    = {th["DARK_BG"]   for th in THEMES.values()}
        _all_panel_bgs   = {th["PANEL_BG"]  for th in THEMES.values()}
        _all_status_bgs  = {th["STATUS_BG"] for th in THEMES.values()} | {"#0d1117"}
        _all_text_dims   = {th["TEXT_DIM"]  for th in THEMES.values()}
        _all_text_lights = {th["TEXT_LIGHT"] for th in THEMES.values()}
        _all_accents     = {th["ACCENT"]    for th in THEMES.values()}
        _all_accent2s    = {th["ACCENT2"]   for th in THEMES.values()}

        def _recolor(widget):
            wtype = widget.winfo_class()
            try:
                if wtype in ("Frame", "Label", "Checkbutton"):
                    cur = widget.cget("bg")
                    if cur in _all_status_bgs:
                        widget.configure(bg=t["STATUS_BG"])
                        if wtype == "Label":
                            widget.configure(fg=t["TEXT_DIM"])
                    elif cur in _all_dark_bgs:
                        widget.configure(bg=t["DARK_BG"])
                        if wtype == "Label":
                            fg = widget.cget("fg")
                            if fg in _all_text_dims:
                                widget.configure(fg=t["TEXT_DIM"])
                            elif fg in _all_text_lights:
                                widget.configure(fg=t["TEXT_LIGHT"])
                            elif fg in _all_accents:
                                widget.configure(fg=t["ACCENT"])
                    elif cur in _all_panel_bgs:
                        widget.configure(bg=t["PANEL_BG"])
                        if wtype == "Label":
                            fg = widget.cget("fg")
                            if fg in _all_text_dims:
                                widget.configure(fg=t["TEXT_DIM"])
                            elif fg in _all_text_lights:
                                widget.configure(fg=t["TEXT_LIGHT"])
                    elif cur in _all_accent2s:
                        widget.configure(bg=t["ACCENT2"])
                elif wtype == "Entry":
                    widget.configure(bg=t["ENTRY_BG"],
                                     fg=t["TEXT_LIGHT"],
                                     highlightbackground=t["ACCENT2"],
                                     insertbackground=t["ACCENT"])
                elif wtype == "Text":
                    widget.configure(bg=t["LOG_BG"], fg=t["LOG_FG"])
                elif wtype == "Button":
                    cur = widget.cget("bg")
                    if cur in _all_accent2s:
                        widget.configure(bg=t["ACCENT2"], fg=t["TEXT_LIGHT"],
                                         activebackground=t["ACCENT"],
                                         activeforeground=t["TEXT_LIGHT"])
                    elif cur in _all_accents:
                        widget.configure(bg=t["ACCENT"], fg=t["TEXT_LIGHT"],
                                         activebackground=t["ACCENT2"],
                                         activeforeground=t["TEXT_LIGHT"])
            except tk.TclError:
                pass
            for child in widget.winfo_children():
                _recolor(child)

        _recolor(self)

        # ── log ──────────────────────────────────────────────
        try:
            self.log.configure(bg=t["LOG_BG"], fg=t["LOG_FG"])
        except Exception:
            pass

        # Aktualizuj globalne stałe, żeby nowe widgety tworzone po zmianie
        # skinu też używały właściwych kolorów.
        global DARK_BG, PANEL_BG, ACCENT, ACCENT2, TEXT_LIGHT, TEXT_DIM
        DARK_BG    = t["DARK_BG"]
        PANEL_BG   = t["PANEL_BG"]
        ACCENT     = t["ACCENT"]
        ACCENT2    = t["ACCENT2"]
        TEXT_LIGHT = t["TEXT_LIGHT"]
        TEXT_DIM   = t["TEXT_DIM"]

    def _toggle_topmost(self, event=None):
        self._topmost = not self._topmost
        self.attributes("-topmost", self._topmost)
        if self._topmost:
            self._pin_btn.configure(fg="#e94560")
            self.status_var.set(T("status_topmost_on"))
        else:
            self._pin_btn.configure(fg=TEXT_DIM)
            self.status_var.set(T("status_topmost_off"))

    def _toggle_lang(self):
        """Przełącza język PL ↔ EN i odświeża wszystkie etykiety GUI."""
        global _current_lang
        _current_lang = "en" if _current_lang == "pl" else "pl"
        # Zapisz w cfg
        self._cfg["lang"] = _current_lang
        _save_cfg(self._cfg)
        self._refresh_ui_lang()

    def _refresh_ui_lang(self):
        """Odświeża wszystkie dynamiczne etykiety po zmianie języka."""
        self.title(T("app_title"))
        # nagłówek
        if hasattr(self, "_hdr_title_lbl"):
            txt = T("app_subtitle")
            cur = self._hdr_title_lbl.cget("text")
            if cur.startswith("⚙"):
                self._hdr_title_lbl.configure(text="⚙  " + txt)
            else:
                self._hdr_title_lbl.configure(text=txt)
        # log label
        if hasattr(self, "_log_lbl"):
            self._log_lbl.configure(text=T("lbl_log"))
        # status bar
        self.status_var.set(T("status_ready"))
        # lang button
        if hasattr(self, "_lang_btn"):
            self._lang_btn.configure(text=T("lang_switch_label"))
        # etykiety formularza (wiersze 0-3)
        if hasattr(self, "_form_lbls"):
            _form_keys = {0: "lbl_bat", 1: "lbl_out", 2: "lbl_icon", 3: "lbl_exe_name"}
            for row, key in _form_keys.items():
                if row in self._form_lbls:
                    self._form_lbls[row].configure(text=T(key))
        # przyciski Przeglądaj (wiersze 0-2)
        if hasattr(self, "_browse_btns"):
            for btn in self._browse_btns.values():
                btn.configure(text=T("btn_browse"))
        # główne przyciski
        if hasattr(self, "btn"):
            self.btn.configure(text=T("btn_convert"))
        if hasattr(self, "dist_btn"):
            self.dist_btn.configure(text=T("btn_dist"))
        if hasattr(self, "meta_btn"):
            self.meta_btn.configure(text=T("btn_metadata"))
        # etykiety toggleów
        if hasattr(self, "_console_lbl"):
            self._console_lbl.configure(text=T("lbl_console"))
        if hasattr(self, "_cmp_lbl"):
            if self._compress_mode == "none":
                self._cmp_lbl.configure(text=T("cmp_none"))
        if hasattr(self, "_pwd_lbl"):
            cur_txt = self._pwd_lbl.cget("text")
            if "✔" in cur_txt:
                self._pwd_lbl.configure(text=T("pwd_lbl_active"))
            else:
                self._pwd_lbl.configure(text=T("pwd_lbl_inactive"))
        if hasattr(self, "_embed_lbl"):
            on = self.embed_var.get()
            self._embed_lbl.configure(
                text=T("embed_embed") if on else T("embed_wrapper"))

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")


# ─────────────────────────────────────────────
#  Start
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()