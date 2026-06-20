# Runekeeper (Discord Bot)

The Runekeeper Discord bot provides economy, levels, fun commands, and Brawlhalla handle bindings. This branch scaffolds the bot with slash commands and a small SQLite-backed database.

Quickstart
1. Copy `.env.example` to `.env` and set `DISCORD_TOKEN` (and `BRAWLHALLA_API_KEY` if you want Brawlhalla features).
2. Create a virtual environment and install requirements:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
3. Run the bot:
   python -m bot.core

Features implemented in this branch
- Help command (slash /help) that lists available commands.
- Economy: /balance, /daily, /transfer
- Levels: XP per message, /profile
- Fun: /coinflip, /8ball, /rps
- Brawlhalla: /bind_brawlhalla, /brawlhalla_profile (stores handles, optional API integration)

Development notes
- Uses SQLAlchemy with a default sqlite:///runekeeper.db. You can set DATABASE_URL to a Postgres URL for production.
- Slash commands are registered on startup (bot.tree.sync()). You may need to invite the bot with applications.commands and proper permissions.

What I will do next
- Add more economy features (shop, leaderboards), more fun/entertainment commands, and Brawlhalla match-tracing once you provide an API key.
- Add tests and CI configuration.

If you want me to proceed further, say "continue" and provide (optionally) BRAWLHALLA_API_KEY and any preferences (currency name, per-server/global economy, library choice).