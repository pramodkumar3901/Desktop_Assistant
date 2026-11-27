@echo off
rem One-click launcher: double-click this file to start Blip (nothing happens if
rem it's already running). Works from wherever the repo folder is.
cd /d "%~dp0"
where pyw >nul 2>nul && (start "" pyw "%~dp0blip_control.pyw" start & exit /b 0)
where pythonw >nul 2>nul && (start "" pythonw "%~dp0blip_control.pyw" start & exit /b 0)
echo Blip needs Python 3 for Windows: https://www.python.org/downloads/
pause
