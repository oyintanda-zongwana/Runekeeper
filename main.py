import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from difflib import get_close_matches
from utils import db
from config import init_config

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
    prefix = DEFAULT_PREFIX
    if message.guild:
        try:
            result = await asyncio.to_thread(db.get_setting, message.guild.id, "prefix", DEFAULT_PREFIX)
            if result:
                prefix = result
        except Exception:
            prefix = "!"
    return commands.when_mentioned_or(prefix)(bot, message)

class RunekeeperBot(commands.Bot):
    """Runekeeper - Hall of the Slain Guild Management Bot"""
    
    async def setup_hook(self):
        self.owner_id = OWNER_ID
        self.remove_command('help')

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

        try:
            if GUILD_ID:
                guild = discord.Object(id=GUILD_ID)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f"✅ Synced commands to test guild {GUILD_ID}")
            else:
                synced = await self.tree.sync()
                print(f"✅ Synced {len(synced)} slash commands globally")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

        await self.register_persistent_views()

    async def register_persistent_views(self):
        try:
            from cogs.trials import TrialQueueView, SubmitResultView

            pending_views = await asyncio.to_thread(
                db._fetchall,
                "SELECT guild_id, trial_id, user_id, message_id FROM trial_candidates WHERE status = 'pending' AND message_id IS NOT NULL"
            )
            restored = 0
            for row in pending_views:
                try:
                    guild_id = int(row[0])
                    trial_id = row[1]
                    user_id = int(row[2])
                    message_id = int(row[3])
                except (TypeError, ValueError):
                    continue

                view = TrialQueueView(trial_id, user_id, self)
                self.add_view(view, message_id=message_id)
                restored += 1

            in_progress_trials = await asyncio.to_thread(
                db._fetchall,
                "SELECT trial_id, guild_id, user_id, approved_by FROM trial_candidates WHERE status = 'in_progress'"
            )
            restored_result_views = 0
            for row in in_progress_trials:
                try:
                    trial_id = row[0]
                    guild_id = int(row[1])
                    user_id = int(row[2])
                    gatekeeper_id = int(row[3]) if row[3] else None
                except (TypeError, ValueError, IndexError):
                    continue

                if gatekeeper_id is None:
                    continue

                view = SubmitResultView(trial_id, user_id, gatekeeper_id)
                self.add_view(view)
                restored_result_views += 1

            if restored:
                print(f"✅ Restored {restored} persistent trial queue views")
            if restored_result_views:
                print(f"✅ Restored {restored_result_views} persistent trial result views")
        except Exception as e:
            print(f"⚠️ Failed to register persistent trial views: {e}")

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

@bot.event
async def on_member_join(member: discord.Member):
    embed = discord.Embed(
        title="🛡️ Hail, Warrior!",
        description=(
            "Welcome to the gates of the **Hall Of The Slain**. The Norns have guided your steps here, but to truly stand among our ranks, you must prove your worth.\n\n"
            "If you seek to pledge your axe to our clan and become a full member, step into the server and type `/applyfortrial` in the bot commands channel to begin your journey.\n\n"
            "*If the winds of fate blew you here by mistake, or you do not seek to join the Hall, simply ignore this message and go in peace.*"
        ),
        color=0xFFD700
    )
    try:
        await member.send(embed=embed)
        print(f"✅ Sent welcome DM to {member} ({member.id})")
    except discord.Forbidden:
        print(f"⚠️ Could not DM new member {member} ({member.id}); DMs may be disabled.")

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
