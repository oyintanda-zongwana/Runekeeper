# Runekeeper - Quick Start (Windows) for enhancement/discord-features

This branch provides the MVP feature set (music via YouTube, levels, invite tracking, Brawlhalla polling, moderation, and basic games). Below are the minimal files and scripts added to help hosts run the bot on a personal Windows PC.

<<<<<<< HEAD
Quickstart
1. Copy `.env.example` to `.env` and set `DISCORD_TOKEN` (and `BRAWLHALLA_API_KEY`, `BRAWLHALLA_API_ENDPOINT`, `BRAWLHALLA_POLL_INTERVAL` if you want Brawlhalla integration).
2. Create a virtual environment and install requirements:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
3. Run the bot:
   python main.py

Note: install `ffmpeg` and add it to your PATH if you want music playback support.
=======
Files added
- scripts/setup_runekeeper.ps1  — PowerShell installer that installs tools (via winget), clones repo, creates venv, installs deps, creates .env, and starts the bot in a new window.
- .env.example                  — example environment file to copy to .env and edit
- runekeeper_start.bat          — simple Windows start script
- deploy/runekeeper.service     — example systemd unit (for Linux VPS users)
- Dockerfile & docker-compose.yml — optional containerized run (advanced)

Minimum required on the host
- Python 3.10+ (on PATH)
- Git
- ffmpeg on PATH (for voice/music)
- Virtualenv (.venv in repo)
- .env with DISCORD_TOKEN set

Quick Windows instructions (host copy/paste)
1) Open PowerShell as Administrator and run (in repository folder):
   git fetch origin
   git checkout enhancement/discord-features
   git pull origin enhancement/discord-features

2) If you haven't run the installer script, you can run it now (as Admin):
   .\scripts\setup_runekeeper.ps1

3) Or manually ensure venv and deps and start the bot:
   taskkill /IM python.exe /F
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   pip install yt-dlp PyNaCl
   python -m bot.core > runekeeper_start.log 2>&1
   Get-Content .\runekeeper_start.log -Tail 200
>>>>>>> 1e118554b3af41dc36fae600d0cc7d0f6d50274b

After host restarts the bot
- In Discord (server admin), run: /sync_commands <GUILD_ID>
  (Guild sync registers slash commands immediately)

If commands still don't appear
- Paste the last 200 lines from runekeeper_start.log here and the bot ID (Right-click bot → Copy ID) and I will diagnose.

