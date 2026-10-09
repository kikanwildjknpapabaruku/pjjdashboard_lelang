@echo off
setlocal
cd /d "%~dp0"
set "setup_result=0"

if not exist ".venv\Scripts\python.exe" (
    python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>&1
    if errorlevel 1 goto python_missing
    python -m venv .venv
    if errorlevel 1 goto failed
)

".venv\Scripts\python.exe" -m pip install -r requirements-lock.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip check
if errorlevel 1 goto failed
echo.
echo Environment siap di folder .venv.
echo Jalankan jalankan_dashboard.bat untuk membuka dashboard.
goto finish

:python_missing
echo Python 3.12 atau lebih baru belum tersedia. Pasang Python lalu jalankan kembali file ini.
set "setup_result=1"
goto finish

:failed
echo Pemasangan belum selesai. Periksa pesan di atas dan koneksi internet, lalu jalankan kembali.
set "setup_result=1"

:finish
if /I not "%~1"=="--no-pause" pause
endlocal & exit /b %setup_result%
