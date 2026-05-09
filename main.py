import discord
import os
from discord.ext import commands
from discord import app_commands
from difflib import get_close_matches
from utils import db
from config import init_config, get_config

# Initialize configuration
config_obj = init_config("config.json")

# Get token and settings
TOKEN = config_obj.get_token()
OWNER_ID = config_obj.get_owner_id()
GUILD_ID = config_obj.get_guild_id()
APPLICATION_ID = config_obj.get_application_id()
DEFAULT_PREFIX = config_obj.config.get("prefix", "*")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

async def get_prefix(bot, message):
    if message.guild:
        prefix = db.get_setting(message.guild.id, "prefix", DEFAULT_PREFIX)
    else:
        prefix = DEFAULT_PREFIX
    return commands.when_mentioned_or(prefix)(bot, message)

class RunekeeperBot(commands.Bot):
    """Runekeeper - Hall of the Slain Guild Management Bot"""
    
    async def setup_hook(self):
        self.owner_id = OWNER_ID

        # Load all cogs
        cog_files = [
            "config_manager",
            "admin_tools",
            "help",
            "hall_info",
            "trials",
            "tournaments",
            "events",
            "appeals",
            "logging",
            "announcements",
            "moderation",
            "roles",
            "server"
        ]
        
        for cog_file in cog_files:
            try:
                await self.load_extension(f"cogs.{cog_file}")
                print(f"✅ Loaded {cog_file}")
            except Exception as e:
                print(f"❌ Failed to load {cog_file}: {e}")

        # Sync commands
        try:
            if GUILD_ID:
                guild = discord.Object(id=GUILD_ID)
                self.tree.clear_commands(guild=guild)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f"✅ Synced commands to test guild {GUILD_ID}")
            else:
                synced = await self.tree.sync()
                print(f"✅ Synced {len(synced)} slash commands globally")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

bot = RunekeeperBot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None,
    application_id=APPLICATION_ID
)

# Initialize database
db.init_db()

def error_embed(ctx, title, desc):
    from utils.themes import create_error_embed
    return create_error_embed(title, desc)

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="over the Hall of the Slain"
        )
    )
    print(f"✅ {bot.user} is ready")
    
    # Start background tasks
    events_cog = bot.get_cog('Events')
    if events_cog:
        events_cog.event_reminder.start()
    
    moderation_cog = bot.get_cog('Moderation')
    if moderation_cog:
        moderation_cog.check_mutes.start()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandNotFound):
        print(f"⚠️ Ignoring stale app command: {interaction.data.get('name') if interaction.data else 'unknown'}")
        return

    description = str(error)
    if interaction.response.is_done():
        await interaction.followup.send(embed=error_embed(interaction, "⚠️ Error", description), ephemeral=True)
    else:
        await interaction.response.send_message(embed=error_embed(interaction, "⚠️ Error", description), ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    prefix = getattr(ctx, "prefix", DEFAULT_PREFIX)
    
    if isinstance(error, commands.CommandNotFound):
        invoked = ctx.invoked_with.lower()
        all_cmds = [cmd.qualified_name for cmd in bot.commands if not cmd.hidden]
        matches = get_close_matches(invoked, all_cmds, n=1, cutoff=0.6)
        if matches:
            cmd = bot.get_command(matches[0])
            embed = discord.Embed(
                title="⚔️ Command Not Found",
                description=f"Did you mean `{prefix}{cmd.qualified_name}`?",
                color=0xD4AF37
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=error_embed(ctx, "⚠️ Unknown Command", f"The command `{prefix}{invoked}` does not exist."))
    
    elif isinstance(error, commands.CheckFailure):
        await ctx.send(embed=error_embed(ctx, "⚠️ Permission Denied", str(error)))
    
    elif isinstance(error, commands.MissingRequiredArgument):
        cmd = ctx.command.name if ctx.command else ctx.invoked_with
        await ctx.send(embed=error_embed(ctx, "⚠️ Missing Arguments", f"Usage: `{prefix}{cmd} {ctx.command.signature if ctx.command else ''}`"))
    
    elif isinstance(error, commands.BadArgument):
        await ctx.send(embed=error_embed(ctx, "⚠️ Invalid Input", "One or more arguments are invalid."))
    
    else:
        await ctx.send(embed=error_embed(ctx, "⚠️ Error", str(error)))

@bot.command(hidden=True, aliases=["shutdown", "off"])
async def stop(ctx):
    """Shutdown the bot (owner only)."""
    if ctx.author.id != OWNER_ID:
        await ctx.send(embed=error_embed(ctx, "⚠️ Error", "Only the bot owner can stop the bot."))
        return
    
    await ctx.send("⚔️ Runekeeper is retreating from the battlefield...")
    await bot.close()

if __name__ == "__main__":
    bot.run(TOKEN)
