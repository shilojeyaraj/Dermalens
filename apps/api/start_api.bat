@echo off
echo 🚀 Starting Dermalens API Server...
echo.

cd /d "%~dp0"

REM Suppress Python warnings for cleaner output
set PYTHONWARNINGS=ignore

REM Start the server
python main.py

pause
