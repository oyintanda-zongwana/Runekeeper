@echo off
<<<<<<< HEAD
echo Updating repository...
git fetch origin
git checkout enhancement/discord-features
git pull origin enhancement/discord-features
echo.
echo Stopping old bot instances...
taskkill /IM python.exe /F >nul 2>&1
echo.
echo Activating virtual environment and installing dependencies...

call ".venv\Scripts\activate.bat"
pip install -r requirements.txt
pip install yt-dlp
echo.
echo Starting Runekeeper bot in foreground...
python main.py
=======
REM Simple start script for Runekeeper (Windows)
cd /d "%~dp0"
call .venv\Scripts\activate
python -m bot.core
pause
>>>>>>> 1e118554b3af41dc36fae600d0cc7d0f6d50274b
