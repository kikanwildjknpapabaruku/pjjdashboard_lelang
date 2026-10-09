@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto setup
".venv\Scripts\python.exe" -c "import streamlit, pandas, plotly.express, openpyxl" >nul 2>&1
if errorlevel 1 goto setup
goto run

:setup
call setup_environment.bat --no-pause
if errorlevel 1 goto failure

:run
".venv\Scripts\python.exe" -m streamlit run src/app.py --server.headless false
goto done
:failure
echo.
echo Environment belum siap. Baca PANDUAN_ENVIRONMENT.md untuk petunjuk.
echo Untuk melihat hasil langsung, buka output\dashboard_lelang.html.
:done
pause
endlocal
