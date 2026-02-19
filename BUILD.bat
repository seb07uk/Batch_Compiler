@echo off
:: ╔══════════════════════════════════════════════════════════════╗
:: ║  polsoft.ITS™  BAT → EXE Converter — Build Script           ║
:: ║  Uruchom ten plik aby zbudowac portable EXE                  ║
:: ╚══════════════════════════════════════════════════════════════╝

title polsoft.ITS - BAT2EXE Build

echo.
echo  ================================================
echo   polsoft.ITS(TM)  BAT to EXE Converter Builder
echo   Version: 2.0.2.6
echo  ================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nie jest zainstalowany lub niedostepny w PATH.
    pause & exit /b 1
)

:: Install dependencies
echo [1/3] Instalacja zaleznosci...
pip install pyinstaller customtkinter pillow --quiet
if errorlevel 1 (
    echo [ERROR] Nie udalo sie zainstalowac zaleznosci.
    pause & exit /b 1
)

:: Clean previous build
echo [2/3] Czyszczenie poprzedniego buildu...
if exist dist\BAT-2-EXE.exe del /f /q dist\BAT-2-EXE.exe
if exist build rmdir /s /q build

:: Build
echo [3/3] Kompilacja...
pyinstaller --noconfirm BAT-2-EXE.spec
if errorlevel 1 (
    echo [ERROR] Kompilacja nieudana. Sprawdz log powyzej.
    pause & exit /b 1
)

echo.
echo  ================================================
echo   SUKCES!  Plik: dist\BAT-2-EXE.exe
echo  ================================================
echo.

if exist dist\BAT-2-EXE.exe (
    explorer dist
)

pause
