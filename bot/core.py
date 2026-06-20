import discord
from discord import app_commands
from discord.ext import commands
from bot.db import init_db
import logging

load_dotenv = None
try:
    from dotenv import load_dotenv as _lod
    load_dotenv = _lod
except Exception:
    pass

if load_dotenv:
    load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("runekeeper")

BOT_PREFIX = "/"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

COG_PATH = "bot.cogs"

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    # Initialize DB if needed
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.exception(f"Database initialization failed: {e}")
    # Sync app commands (slash commands)
    try:
        await bot.tree.sync()
        logger.info("Synced application commands")
    except Exception as e:
        logger.warning(f"Failed to sync application commands: {e}")

async def load_cogs():
    # Load all cogs from the cogs package
    cogs = [
        "bot.cogs.help",
        "bot.cogs.economy",
        "bot.cogs.levels",
        "bot.cogs.fun",
        "bot.cogs.admin",
        "bot.cogs.minigames",
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"Loaded cog: {cog}")
        except Exception as e:
            logger.exception(f"Failed to load cog {cog}: {e}")


def main():
    token = None
    try:
        token = __import__('os').environ.get("DISCORD_TOKEN")
    except Exception:
        pass
    if not token:
        logger.error("DISCORD_TOKEN is not set in the environment")
        return

    import asyncio
    asyncio.run(_run(token))

async def _run(token: str):
    await load_cogs()
    await bot.start(token)

if __name__ == "__main__":
    main()
