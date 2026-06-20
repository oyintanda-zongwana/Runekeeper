@echo off
REM Simple start script for Runekeeper (Windows)
cd /d "%~dp0"
call .venv\Scripts\activate
python -m bot.core
pause
