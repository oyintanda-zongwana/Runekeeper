@echo off
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