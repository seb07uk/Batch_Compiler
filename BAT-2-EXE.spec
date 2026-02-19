# -*- mode: python ; coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════╗
# ║  polsoft.ITS™  BAT → EXE Converter  —  PyInstaller SPEC     ║
# ║  Version : 2.0.2.6                                           ║
# ║  Author  : Sebastian Januchowski                             ║
# ║  Build   : portable / standalone onefile                     ║
# ╚══════════════════════════════════════════════════════════════╝

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Data files bundled into the EXE ─────────────────────────────────────────
datas = [
    ('icon.ico',  '.'),   # application icon (accessible at runtime)
    ('logo.ico',  '.'),   # fallback icon
]

# Collect customtkinter theme / image assets
try:
    import customtkinter
    ctk_dir = os.path.dirname(customtkinter.__file__)
    datas += [(ctk_dir, 'customtkinter')]
except ImportError:
    pass

# ── Hidden imports ────────────────────────────────────────────────────────────
hiddenimports = [
    'customtkinter',
    'PIL',
    'PIL._imagingtk',
    'PIL.ImageFilter',
    'PIL.ImageDraw',
    'PIL.ImageTk',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    '_tkinter',
]

hiddenimports += collect_submodules('customtkinter')
hiddenimports += collect_submodules('PIL')

# ── Analysis ─────────────────────────────────────────────────────────────────
a = Analysis(
    ['BAT-2-EXE.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'pandas',
        'PyQt5', 'PyQt6', 'wx', 'gi',
        'IPython', 'jupyter', 'notebook',
        'test', 'unittest', 'email', 'html',
        'http', 'urllib3', 'requests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── EXE — single portable file ───────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BAT-2-EXE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,              # GUI app — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    version='version_info.txt', # embed metadata into PE header
)
