@echo off
:: ============================================================
::  build.bat  —  BAT-2-EXE  Full Portable Builder
::  ============================================================
::  Company  : polsoft.ITS™ Group
::  Author   : Sebastian Januchowski
::  E-mail   : polsoft.its@fastservice.com
::  GitHub   : https://github.com/seb07uk
::  License  : 2026© polsoft.ITS™ DEV. All rights reserved.
:: ============================================================
::
::  USAGE:
::    build.bat              — interactive build (default options)
::    build.bat --upx        — build + UPX compression
::    build.bat --lzma       — build + LZMA compression
::    build.bat --debug      — build with console window (debug)
::    build.bat --clean-only — clean build artifacts only
::    build.bat --help       — show this help
::
:: ============================================================

setlocal EnableDelayedExpansion

:: ── Generate ESC character for ANSI colors ──────────────────
for /f "delims=" %%e in ('python -c "import sys; sys.stdout.buffer.write(bytes([27])); sys.stdout.flush()" 2^>nul') do set "ESC=%%e"

:: ── ANSI Color Definitions ───────────────────────────────────
set "RED=%ESC%[91m"
set "GRN=%ESC%[92m"
set "YLW=%ESC%[93m"
set "BLU=%ESC%[94m"
set "MAG=%ESC%[95m"
set "CYN=%ESC%[96m"
set "WHT=%ESC%[97m"
set "DIM=%ESC%[90m"
set "RST=%ESC%[0m"
set "BLD=%ESC%[1m"
set "UND=%ESC%[4m"

:: ── ─────────────────────────────────────────────────────────
::    C O N F I G U R A T I O N
:: ────────────────────────────────────────────────────────────

set APP_NAME=BAT-2-EXE
set APP_VERSION=1.0.0
set APP_SCRIPT=BAT-_2-EXE.py
set ICON_FILE=icon.ico
set VERSION_FILE=version_info.txt
set SPEC_FILE=BAT-2-EXE.spec
set DIST_DIR=dist
set BUILD_DIR=build

:: PyInstaller hidden imports (all modules used by the app)
set HIDDEN=PIL,PIL.Image,PIL.ImageTk,PIL.ImageFilter,PIL.ImageDraw,PIL.ImageFont
set HIDDEN=%HIDDEN%,hashlib,lzma,struct,json,threading,subprocess,tempfile,shutil

:: ── Build flags (can be overridden by CLI args) ──────────────
set FLAG_WINDOWED=1
set FLAG_ONEFILE=1
set FLAG_UPX=0
set FLAG_LZMA=0
set FLAG_CLEAN_ONLY=0
set FLAG_DEBUG=0
set FLAG_SPEC=0
set FLAG_HELP=0

:: ── Parse command line arguments ────────────────────────────
:parse_args
if "%~1"=="" goto :done_args
if /i "%~1"=="--upx"        set FLAG_UPX=1
if /i "%~1"=="--lzma"       set FLAG_LZMA=1
if /i "%~1"=="--debug"      set FLAG_WINDOWED=0 & set FLAG_DEBUG=1
if /i "%~1"=="--console"    set FLAG_WINDOWED=0
if /i "%~1"=="--spec"       set FLAG_SPEC=1
if /i "%~1"=="--clean-only" set FLAG_CLEAN_ONLY=1
if /i "%~1"=="--help"       set FLAG_HELP=1
if /i "%~1"=="-h"           set FLAG_HELP=1
shift
goto :parse_args
:done_args

:: ── Help ─────────────────────────────────────────────────────
if %FLAG_HELP%==1 (
    cls
    echo.
    echo  %BLD%%CYN%  BAT-2-EXE Build Script — Help%RST%
    echo  %DIM%  ─────────────────────────────────────────────%RST%
    echo.
    echo  %WHT%  USAGE:%RST%
    echo    %YLW%build.bat%RST%              Interactive build ^(windowed, onefile^)
    echo    %YLW%build.bat --upx%RST%        Build + UPX compression ^(requires upx.exe^)
    echo    %YLW%build.bat --lzma%RST%       Build + custom LZMA stub compression
    echo    %YLW%build.bat --debug%RST%      Build with console visible ^(debug mode^)
    echo    %YLW%build.bat --console%RST%    Same as --debug
    echo    %YLW%build.bat --spec%RST%       Use existing .spec file instead of CLI flags
    echo    %YLW%build.bat --clean-only%RST% Remove build/ dist/ and temp files only
    echo    %YLW%build.bat --help%RST%       Show this message
    echo.
    echo  %WHT%  OUTPUT:%RST%
    echo    %DIM%  dist\%APP_NAME%.exe  —  portable standalone executable%RST%
    echo.
    echo  %WHT%  REQUIREMENTS:%RST%
    echo    %DIM%  Python 3.10+, PyInstaller, Pillow%RST%
    echo    %DIM%  UPX (optional): https://upx.github.io/%RST%
    echo.
    echo  %DIM%  polsoft.ITS™ Group  |  2026© All rights reserved.%RST%
    echo.
    exit /b 0
)

:: ── Banner ───────────────────────────────────────────────────
cls
echo.
echo  %BLD%%CYN%╔══════════════════════════════════════════════════════════╗%RST%
echo  %BLD%%CYN%║%RST%  %BLD%%WHT%  ps BAT-2-EXE  •  Portable Builder  v%APP_VERSION%%RST%                 %BLD%%CYN%║%RST%
echo  %BLD%%CYN%║%RST%  %DIM%  polsoft.ITS™ Group  |  Sebastian Januchowski%RST%          %BLD%%CYN%║%RST%
echo  %BLD%%CYN%║%RST%  %DIM%  polsoft.its@fastservice.com  |  github.com/seb07uk%RST%    %BLD%%CYN%║%RST%
echo  %BLD%%CYN%╚══════════════════════════════════════════════════════════╝%RST%
echo.

:: ── Clean-only mode ──────────────────────────────────────────
if %FLAG_CLEAN_ONLY%==1 (
    echo  %YLW%[CLEAN]%RST% Removing build artifacts...
    call :do_clean
    echo  %GRN%[DONE]%RST%  Clean complete.
    echo.
    exit /b 0
)

:: ── Print build configuration ────────────────────────────────
echo  %BLD%%WHT%Build Configuration:%RST%
echo  %DIM%  ─────────────────────────────────────────%RST%
echo  %DIM%  Script    :%RST%  %WHT%%APP_SCRIPT%%RST%
echo  %DIM%  Output    :%RST%  %WHT%%DIST_DIR%\%APP_NAME%.exe%RST%
echo  %DIM%  Mode      :%RST%  %CYN%Portable --onefile%RST%

if %FLAG_WINDOWED%==1 (
    echo  %DIM%  Window    :%RST%  %CYN%Windowed ^(no console^)%RST%
) else (
    echo  %DIM%  Window    :%RST%  %YLW%Console ^(debug mode^)%RST%
)

if %FLAG_UPX%==1   echo  %DIM%  Compress  :%RST%  %MAG%UPX ^(max level 9^)%RST%
if %FLAG_LZMA%==1  echo  %DIM%  Compress  :%RST%  %MAG%LZMA ^(preset 9 extreme^)%RST%
if %FLAG_SPEC%==1  echo  %DIM%  Spec file :%RST%  %CYN%%SPEC_FILE%%RST%

echo  %DIM%  ─────────────────────────────────────────%RST%
echo.

:: ════════════════════════════════════════════════════════════
::  STEP 1 — CHECK PYTHON
:: ════════════════════════════════════════════════════════════
echo  %YLW%[1/7]%RST% Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  %RED%[ERROR]%RST% Python not found in PATH.
    echo  %DIM%         Download from https://python.org and add to PATH.%RST%
    goto :error
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  %GRN%[OK]%RST%    %PY_VER%

:: Check Python version >= 3.10
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_FULL=%%v
for /f "tokens=1,2 delims=." %%a in ("%PY_FULL%") do (
    set PY_MAJOR=%%a
    set PY_MINOR=%%b
)
if !PY_MAJOR! LSS 3 (
    echo  %RED%[ERROR]%RST% Python 3.10+ required. Found: %PY_FULL%
    goto :error
)
if !PY_MAJOR%==3 if !PY_MINOR! LSS 10 (
    echo  %YLW%[WARN]%RST%  Python 3.10+ recommended. Found: %PY_FULL%
    echo  %DIM%          Continuing anyway...%RST%
)

:: ════════════════════════════════════════════════════════════
::  STEP 2 — CHECK / INSTALL PYINSTALLER
:: ════════════════════════════════════════════════════════════
echo  %YLW%[2/7]%RST% Checking PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo  %YLW%[WARN]%RST%  PyInstaller not found. Installing...
    python -m pip install pyinstaller --quiet --upgrade
    if errorlevel 1 (
        echo  %RED%[ERROR]%RST% Failed to install PyInstaller.
        goto :error
    )
    echo  %GRN%[OK]%RST%    PyInstaller installed.
) else (
    for /f "tokens=*" %%v in ('python -m PyInstaller --version 2^>^&1') do set PI_VER=%%v
    echo  %GRN%[OK]%RST%    PyInstaller !PI_VER!
)

:: ════════════════════════════════════════════════════════════
::  STEP 3 — CHECK / INSTALL PILLOW
:: ════════════════════════════════════════════════════════════
echo  %YLW%[3/7]%RST% Checking Pillow...
python -c "from PIL import Image; print('ok')" >nul 2>&1
if errorlevel 1 (
    echo  %YLW%[WARN]%RST%  Pillow not found. Installing...
    python -m pip install pillow --quiet --upgrade
    if errorlevel 1 (
        echo  %YLW%[WARN]%RST%  Pillow install failed. Icon conversion from PNG/JPG may not work.
    ) else (
        echo  %GRN%[OK]%RST%    Pillow installed.
    )
) else (
    for /f "tokens=*" %%v in ('python -c "import PIL; print(PIL.__version__)" 2^>^&1') do set PIL_VER=%%v
    echo  %GRN%[OK]%RST%    Pillow !PIL_VER!
)

:: ════════════════════════════════════════════════════════════
::  STEP 4 — CHECK SOURCE FILES
:: ════════════════════════════════════════════════════════════
echo  %YLW%[4/7]%RST% Checking source files...

:: Main script
if not exist "%APP_SCRIPT%" (
    echo  %RED%[ERROR]%RST% Source script not found: %APP_SCRIPT%
    echo  %DIM%         Make sure %APP_SCRIPT% is in the same folder as build.bat%RST%
    goto :error
)
echo  %GRN%[OK]%RST%    Script   : %APP_SCRIPT%

:: Icon
set ICON_ARG=
if exist "%ICON_FILE%" (
    echo  %GRN%[OK]%RST%    Icon     : %ICON_FILE%
    set ICON_ARG=--icon="%ICON_FILE%"
) else (
    echo  %YLW%[WARN]%RST%  Icon not found (%ICON_FILE%) — building without custom icon.
)

:: Version info
set VER_ARG=
if exist "%VERSION_FILE%" (
    echo  %GRN%[OK]%RST%    Version  : %VERSION_FILE%
    set VER_ARG=--version-file="%VERSION_FILE%"
) else (
    echo  %YLW%[WARN]%RST%  %VERSION_FILE% not found — generating from defaults...
    call :generate_version_info
    if exist "%VERSION_FILE%" (
        echo  %GRN%[OK]%RST%    Version  : %VERSION_FILE% ^(auto-generated^)
        set VER_ARG=--version-file="%VERSION_FILE%"
    ) else (
        echo  %YLW%[WARN]%RST%  Could not generate version info — skipping.
    )
)

:: Spec file check
if %FLAG_SPEC%==1 (
    if not exist "%SPEC_FILE%" (
        echo  %YLW%[WARN]%RST%  Spec file not found: %SPEC_FILE% — switching to CLI mode.
        set FLAG_SPEC=0
    ) else (
        echo  %GRN%[OK]%RST%    Spec     : %SPEC_FILE%
    )
)

:: UPX check
if %FLAG_UPX%==1 (
    call :find_upx
    if "!UPX_PATH!"=="" (
        echo  %YLW%[WARN]%RST%  UPX not found — disabling UPX compression.
        echo  %DIM%          Download from https://upx.github.io/ and place next to build.bat%RST%
        set FLAG_UPX=0
    ) else (
        echo  %GRN%[OK]%RST%    UPX      : !UPX_PATH!
    )
)

:: ════════════════════════════════════════════════════════════
::  STEP 5 — CLEAN PREVIOUS BUILD
:: ════════════════════════════════════════════════════════════
echo  %YLW%[5/7]%RST% Cleaning previous build...
call :do_clean
echo  %GRN%[OK]%RST%    Clean done.

:: ════════════════════════════════════════════════════════════
::  STEP 6 — BUILD EXE
:: ════════════════════════════════════════════════════════════
echo  %YLW%[6/7]%RST% Building portable standalone EXE...
echo.
echo  %DIM%  ── PyInstaller command ──────────────────────────────────────%RST%

:: ── Window mode flag ────────────────────────────────────────
set WIN_FLAG=--windowed
if %FLAG_WINDOWED%==0 set WIN_FLAG=

:: ── BUILD via SPEC or CLI ────────────────────────────────────
if %FLAG_SPEC%==1 (
    echo  %DIM%  python -m PyInstaller "%SPEC_FILE%" [using spec file]%RST%
    echo.
    python -m PyInstaller ^
        --distpath="%DIST_DIR%" ^
        --workpath="%BUILD_DIR%" ^
        --noconfirm ^
        --clean ^
        "%SPEC_FILE%"
) else (
    echo  %DIM%  pyinstaller --onefile %WIN_FLAG% --name="%APP_NAME%" ...%RST%
    echo.
    python -m PyInstaller ^
        --onefile ^
        %WIN_FLAG% ^
        --name="%APP_NAME%" ^
        --distpath="%DIST_DIR%" ^
        --workpath="%BUILD_DIR%" ^
        --specpath="." ^
        %ICON_ARG% ^
        %VER_ARG% ^
        --collect-all tkinter ^
        --hidden-import=PIL ^
        --hidden-import=PIL.Image ^
        --hidden-import=PIL.ImageTk ^
        --hidden-import=PIL.ImageFilter ^
        --hidden-import=PIL.ImageDraw ^
        --hidden-import=PIL.ImageFont ^
        --hidden-import=PIL.ImageOps ^
        --hidden-import=hashlib ^
        --hidden-import=lzma ^
        --hidden-import=struct ^
        --hidden-import=json ^
        --hidden-import=threading ^
        --hidden-import=subprocess ^
        --hidden-import=tempfile ^
        --hidden-import=shutil ^
        --hidden-import=pathlib ^
        --hidden-import=tkinter ^
        --hidden-import=tkinter.ttk ^
        --hidden-import=tkinter.filedialog ^
        --hidden-import=tkinter.messagebox ^
        --hidden-import=tkinter.simpledialog ^
        --hidden-import=tkinter.font ^
        --exclude-module=numpy ^
        --exclude-module=pandas ^
        --exclude-module=matplotlib ^
        --exclude-module=scipy ^
        --exclude-module=cv2 ^
        --exclude-module=sklearn ^
        --exclude-module=tensorflow ^
        --exclude-module=torch ^
        --exclude-module=IPython ^
        --exclude-module=jupyter ^
        --exclude-module=unittest ^
        --exclude-module=doctest ^
        --exclude-module=pydoc ^
        --exclude-module=email ^
        --exclude-module=html ^
        --exclude-module=http ^
        --exclude-module=xml ^
        --exclude-module=xmlrpc ^
        --exclude-module=ftplib ^
        --exclude-module=imaplib ^
        --exclude-module=smtplib ^
        --exclude-module=poplib ^
        --exclude-module=telnetlib ^
        --exclude-module=nntplib ^
        --exclude-module=turtle ^
        --noupx ^
        --clean ^
        --noconfirm ^
        "%APP_SCRIPT%"
)

if errorlevel 1 (
    echo.
    echo  %RED%╔══════════════════════════════════════════╗%RST%
    echo  %RED%║   BUILD FAILED — check output above      ║%RST%
    echo  %RED%╚══════════════════════════════════════════╝%RST%
    goto :error
)

:: ── Verify EXE was created ───────────────────────────────────
if not exist "%DIST_DIR%\%APP_NAME%.exe" (
    echo  %RED%[ERROR]%RST% EXE not found after build: %DIST_DIR%\%APP_NAME%.exe
    goto :error
)

:: ── Record pre-compression size ──────────────────────────────
for %%f in ("%DIST_DIR%\%APP_NAME%.exe") do set PRE_SIZE=%%~zf

:: ════════════════════════════════════════════════════════════
::  STEP 7 — OPTIONAL COMPRESSION
:: ════════════════════════════════════════════════════════════
echo  %YLW%[7/7]%RST% Post-processing...

:: ── UPX compression ─────────────────────────────────────────
if %FLAG_UPX%==1 (
    echo.
    echo  %MAG%  ── UPX Compression ─────────────────────────────%RST%
    echo  %DIM%  Running UPX level 9 on %DIST_DIR%\%APP_NAME%.exe ...%RST%
    "!UPX_PATH!" -9 --force "%DIST_DIR%\%APP_NAME%.exe"
    if errorlevel 1 (
        echo  %YLW%[WARN]%RST%  UPX compression failed — using uncompressed EXE.
    ) else (
        for %%f in ("%DIST_DIR%\%APP_NAME%.exe") do set POST_SIZE=%%~zf
        set /a SAVED=(!PRE_SIZE! - !POST_SIZE!) / 1024
        set /a PCT=(!PRE_SIZE! - !POST_SIZE!) * 100 / !PRE_SIZE!
        echo  %GRN%[OK]%RST%    UPX done. Saved ~!SAVED! KB ^(!PCT!%%^)
    )
)

:: ── LZMA compression ─────────────────────────────────────────
if %FLAG_LZMA%==1 (
    echo.
    echo  %MAG%  ── LZMA Compression ────────────────────────────%RST%
    echo  %DIM%  Applying LZMA preset=9|EXTREME to %DIST_DIR%\%APP_NAME%.exe ...%RST%
    call :compress_lzma
)

echo  %GRN%[OK]%RST%    Post-processing done.

:: ════════════════════════════════════════════════════════════
::  FINAL REPORT
:: ════════════════════════════════════════════════════════════
for %%f in ("%DIST_DIR%\%APP_NAME%.exe") do set FINAL_SIZE=%%~zf
set /a FINAL_MB=!FINAL_SIZE! / 1048576
set /a FINAL_KB=(!FINAL_SIZE! - !FINAL_MB! * 1048576) / 1024

:: Compute build time using Python
for /f "tokens=*" %%t in ('python -c "import time; print(int(time.time()))"') do set BUILD_END=%%t

set /a PRE_MB=!PRE_SIZE! / 1048576
set /a PRE_KB=(!PRE_SIZE! - !PRE_MB! * 1048576) / 1024

echo.
echo  %BLD%%GRN%╔══════════════════════════════════════════════════════════╗%RST%
echo  %BLD%%GRN%║   BUILD SUCCESSFUL                                        ║%RST%
echo  %GRN%╚══════════════════════════════════════════════════════════╝%RST%
echo.
echo  %WHT%  Output     :%RST%  %BLD%%CYN%%DIST_DIR%\%APP_NAME%.exe%RST%
echo  %WHT%  Version    :%RST%  %APP_VERSION%
echo  %WHT%  Mode       :%RST%  Portable --onefile standalone

if %FLAG_WINDOWED%==1 (
    echo  %WHT%  Window     :%RST%  Windowed ^(no console^)
) else (
    echo  %WHT%  Window     :%RST%  Console ^(debug^)
)

if %FLAG_UPX%==1  echo  %WHT%  Compress   :%RST%  UPX level 9
if %FLAG_LZMA%==1 echo  %WHT%  Compress   :%RST%  LZMA preset=9^|EXTREME

echo  %WHT%  File size  :%RST%  !FINAL_MB! MB  (!FINAL_KB! KB)
echo.
echo  %DIM%  Hidden imports : tkinter, PIL, hashlib, lzma, struct, ...%RST%
echo  %DIM%  Excluded       : numpy, pandas, scipy, cv2, torch, ml libs%RST%
echo  %DIM%  polsoft.ITS™ Group  |  2026© All rights reserved.%RST%
echo.

:: ── Open dist folder ─────────────────────────────────────────
echo  Opening output folder...
start "" explorer "%DIST_DIR%"

goto :eof


:: ════════════════════════════════════════════════════════════
::  SUBROUTINE: find_upx
::  Searches for upx.exe in PATH, local dir, and %ProgramFiles%
:: ════════════════════════════════════════════════════════════
:find_upx
set UPX_PATH=
:: 1. Beside build.bat
if exist "%~dp0upx.exe" (
    set "UPX_PATH=%~dp0upx.exe"
    goto :eof
)
:: 2. In PATH
for %%p in (upx.exe) do (
    if not "%%~$PATH:p"=="" (
        set "UPX_PATH=%%~$PATH:p"
        goto :eof
    )
)
:: 3. Common install locations
for %%d in (
    "%ProgramFiles%\UPX\upx.exe"
    "%ProgramFiles(x86)%\UPX\upx.exe"
    "%ProgramFiles%\upx-4.2.4-win64\upx.exe"
    "%ProgramFiles%\upx-4.2.2-win64\upx.exe"
    "%ProgramFiles%\upx-4.2.1-win64\upx.exe"
    "%SystemDrive%\upx\upx.exe"
    "%SystemDrive%\tools\upx.exe"
    "%USERPROFILE%\tools\upx.exe"
    "%USERPROFILE%\scoop\apps\upx\current\upx.exe"
) do (
    if exist "%%~d" (
        set "UPX_PATH=%%~d"
        goto :eof
    )
)
goto :eof


:: ════════════════════════════════════════════════════════════
::  SUBROUTINE: compress_lzma
::  Creates a self-extracting LZMA wrapper stub
:: ════════════════════════════════════════════════════════════
:compress_lzma
python -c "
import lzma, struct, sys, os, tempfile, subprocess, shutil
from pathlib import Path

src  = Path(r'%DIST_DIR%') / r'%APP_NAME%.exe'
tmp  = Path(r'%BUILD_DIR%')
tmp.mkdir(exist_ok=True)

# Read and compress payload
print('  Reading payload...')
data = src.read_bytes()
orig_size = len(data)
print(f'  Original size : {orig_size / 1048576:.2f} MB')

print('  Compressing LZMA preset=9|EXTREME ...')
compressed = lzma.compress(data, preset=9 | lzma.PRESET_EXTREME)
comp_size = len(compressed)
print(f'  Compressed    : {comp_size / 1048576:.2f} MB ({100 - comp_size*100//orig_size}%% reduction)')

# Build Python stub that decompresses & runs the payload
stub_code = r'''
import lzma, struct, sys, os, tempfile, subprocess, atexit
PAYLOAD = __PAYLOAD__
def main():
    data = lzma.decompress(PAYLOAD)
    tmp = tempfile.mktemp(suffix='.exe')
    with open(tmp,'wb') as f: f.write(data)
    os.chmod(tmp, 0o755)
    atexit.register(lambda: os.unlink(tmp) if os.path.exists(tmp) else None)
    result = subprocess.run([tmp] + sys.argv[1:])
    sys.exit(result.returncode)
main()
'''.replace('__PAYLOAD__', repr(compressed))

stub_path = tmp / '_stub_lzma.py'
stub_path.write_text(stub_code, encoding='utf-8')

# Build the stub as a new EXE using PyInstaller
print('  Building LZMA stub EXE...')
result = subprocess.run([
    sys.executable, '-m', 'PyInstaller',
    '--onefile', '--windowed', '--noconfirm', '--clean',
    f'--name=%APP_NAME%_lzma',
    f'--distpath=%DIST_DIR%_lzma',
    f'--workpath={tmp / \"_lzma_build\"}',
    str(stub_path)
], capture_output=True, text=True)

stub_exe = Path(r'%DIST_DIR%_lzma') / '%APP_NAME%_lzma.exe'
if stub_exe.exists():
    stub_size = stub_exe.stat().st_size
    if stub_size < orig_size:
        saved = (orig_size - stub_size) / 1024
        pct   = 100 - stub_size*100//orig_size
        shutil.copy2(stub_exe, src)
        print(f'  LZMA stub OK  : {stub_size / 1048576:.2f} MB  (saved {saved:.0f} KB / {pct}%%)')
    else:
        overhead = (stub_size - orig_size) / 1024
        print(f'  NOTE: Stub ({stub_size/1048576:.2f} MB) larger than original ({orig_size/1048576:.2f} MB)')
        print(f'  Stub overhead : +{overhead:.0f} KB — keeping original EXE.')
    # Cleanup lzma dist
    shutil.rmtree(r'%DIST_DIR%_lzma', ignore_errors=True)
else:
    print('  LZMA stub build failed — keeping original EXE.')
    print(result.stdout[-1000:] if result.stdout else '')
    print(result.stderr[-500:]  if result.stderr else '')
"
goto :eof


:: ════════════════════════════════════════════════════════════
::  SUBROUTINE: generate_version_info
::  Writes a PyInstaller VSVersionInfo file
:: ════════════════════════════════════════════════════════════
:generate_version_info
python -c "
ver = '1.0.0.0'
v   = tuple(int(x) for x in ver.split('.'))
txt = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={v},
    prodvers={v},
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [
          StringStruct(u'CompanyName',      u'polsoft.ITS\u2122 Group'),
          StringStruct(u'FileDescription',  u'BAT to EXE Converter - polsoft.ITS\u2122'),
          StringStruct(u'FileVersion',      u'{ver}'),
          StringStruct(u'InternalName',     u'ps-BAT-2-EXE'),
          StringStruct(u'LegalCopyright',   u'2026\u00a9 Sebastian Januchowski. All rights reserved.'),
          StringStruct(u'LegalTrademarks',  u'polsoft.ITS\u2122 is a trademark of polsoft.ITS\u2122 Group'),
          StringStruct(u'OriginalFilename', u'BAT-2-EXE.exe'),
          StringStruct(u'ProductName',      u'ps-BAT-2-EXE Converter'),
          StringStruct(u'ProductVersion',   u'{ver}'),
          StringStruct(u'Comments',         u'https://github.com/seb07uk'),
          StringStruct(u'Contact',          u'polsoft.its@fastservice.com'),
        ]
      )
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
open('version_info.txt', 'w', encoding='utf-8').write(txt)
print('Generated version_info.txt')
"
goto :eof


:: ════════════════════════════════════════════════════════════
::  SUBROUTINE: do_clean
::  Removes build artifacts
:: ════════════════════════════════════════════════════════════
:do_clean
if exist "%DIST_DIR%\%APP_NAME%.exe" (
    del /f /q "%DIST_DIR%\%APP_NAME%.exe" >nul 2>&1
    echo  %DIM%         Removed %DIST_DIR%\%APP_NAME%.exe%RST%
)
if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%" >nul 2>&1
    echo  %DIM%         Removed %BUILD_DIR%\%RST%
)
if exist "%APP_NAME%.spec" (
    del /f /q "%APP_NAME%.spec" >nul 2>&1
    echo  %DIM%         Removed %APP_NAME%.spec%RST%
)
if exist "__pycache__" (
    rmdir /s /q "__pycache__" >nul 2>&1
)
goto :eof


:: ════════════════════════════════════════════════════════════
::  ERROR HANDLER
:: ════════════════════════════════════════════════════════════
:error
echo.
echo  %RED%  Build aborted. See errors above.%RST%
echo.
pause
exit /b 1
