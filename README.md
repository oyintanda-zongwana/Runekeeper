# Runekeeper (Discord Bot)

The Runekeeper Discord bot provides economy, levels, fun commands, and a range of mini-games. This branch extends the earlier scaffold with admin utilities and minigames.

Quickstart
1. Copy `.env.example` to `.env` and set `DISCORD_TOKEN` (and other optional vars).
2. Create a virtual environment and install requirements:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
3. Run the bot:
   python -m bot.core

New features added in this update
- Admin cog: `/list_cogs`, `/reload_cog <cog>`, `/sync_commands [guild_id]` for on-demand reload/sync by admins or bot owner.
- Minigames cog: `/guess_start`, `/guess_try`, `/scramble`, `/trivia` — small, fun games usable in-channel.
- Expanded Fun cog (roasts, jokes, quotes, songs) and Economy cog (shop, gamble, leaderboard).

Why your commands might not appear or work
1. The running bot process is not using the updated code. Pushing to GitHub doesn't change a running process — you must restart or hot-reload cogs in the running instance.
2. Cogs may fail to load due to errors on startup; check logs for exceptions like import errors or missing dependencies.
3. Slash commands register globally (can take up to 1 hour to show). For immediate testing, sync commands to a dev guild using `/sync_commands <guild_id>`.
4. Required environment variables (DISCORD_TOKEN) or dependencies might be missing; check startup logs.
5. DB not initialized — the code now runs init_db() in on_ready to create the SQLite schema if missing.

If you want me to continue adding more mini-games (blackjack, hangman, word chains), leaderboards for minigames, or integrate external APIs for memes/music, say which ones and I will implement them next.
