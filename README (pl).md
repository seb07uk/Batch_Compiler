# polsoft.ITS™ BAT → EXE Converter — Build Package

**Wersja:** 2.0.2.6  
**Autor:** Sebastian Januchowski  
**© 2026 polsoft.ITS London**

---

## Zawartość paczki

| Plik | Opis |
|------|------|
| `BAT-2-EXE.py` | Główny kod aplikacji |
| `BAT-2-EXE.spec` | Plik konfiguracyjny PyInstaller |
| `version_info.txt` | Metadane wersji wbudowane w EXE (PE header) |
| `icon.ico` | Ikona aplikacji (multi-size ICO) |
| `logo.ico` | Ikona zastępcza |
| `BUILD.bat` | Skrypt automatycznej kompilacji |

---

## Jak zbudować EXE

### Metoda 1 — automatyczna (zalecana)
```
Kliknij dwukrotnie:  BUILD.bat
```

### Metoda 2 — ręczna
```bat
pip install pyinstaller customtkinter pillow
pyinstaller --noconfirm BAT-2-EXE.spec
```

Wynikowy plik znajdziesz w: `dist\BAT-2-EXE.exe`

---

## Wymagania do budowania

- Python 3.9+ (64-bit)
- PyInstaller
- customtkinter
- Pillow

Aplikacja po kompilacji jest **w pełni standalone** — nie wymaga Pythona na docelowym PC.

---

## Metadane EXE (version_info.txt)

Po kompilacji plik EXE będzie zawierał w nagłówku PE:

| Pole | Wartość |
|------|---------|
| Product Name | polsoft.ITS BAT → EXE Converter |
| Company | polsoft.ITS |
| Copyright | © 2026 Sebastian Januchowski / polsoft.ITS London |
| File Version | 2.0.2.6 |
| Internal Name | BAT2EXE |

---

## Uwagi

- Opcja `--onefile` w spec zapewnia **jeden przenośny plik EXE**
- Opcja `--noconsole` ukrywa okno CMD przy uruchamianiu
- UPX compression włączony (`upx=True`) — zmniejsza rozmiar EXE
- Wykluczone zbędne biblioteki (numpy, matplotlib, Qt) dla mniejszego rozmiaru
