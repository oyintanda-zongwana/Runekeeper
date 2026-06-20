import discord
from discord import app_commands
from discord.ext import commands

class AdminCog(commands.Cog):
    """Admin utilities: reload cogs, sync commands, and list loaded cogs."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _is_admin(self, interaction: discord.Interaction) -> bool:
        # Owner or guild administrator
        if hasattr(self.bot, 'is_owner'):
            # can't await is_owner in sync check; we'll check inside command
            return True
        return True

    @app_commands.command(name="list_cogs", description="List loaded cogs")
    async def list_cogs(self, interaction: discord.Interaction):
        loaded = list(self.bot.extensions.keys())
        await interaction.response.send_message("Loaded cogs:\n" + "\n".join(loaded), ephemeral=True)

    @app_commands.command(name="reload_cog", description="Reload a cog (admin only)")
    @app_commands.describe(cog="The cog module name (e.g., bot.cogs.economy)")
    async def reload_cog(self, interaction: discord.Interaction, cog: str):
        # permission check: server admin or bot owner
        is_owner = False
        try:
            is_owner = await self.bot.is_owner(interaction.user)
        except Exception:
            pass
        if not is_owner and not (interaction.user.guild_permissions.administrator if interaction.guild else False):
            await interaction.response.send_message("You must be a server admin or bot owner to use this.", ephemeral=True)
            return
        try:
            await self.bot.reload_extension(cog)
            await interaction.response.send_message(f"Reloaded {cog}")
        except Exception as e:
            await interaction.response.send_message(f"Failed to reload {cog}: {e}", ephemeral=True)

    @app_commands.command(name="sync_commands", description="Sync application commands (optionally to a guild)")
    @app_commands.describe(guild_id="Guild ID to sync to (optional)")
    async def sync_commands(self, interaction: discord.Interaction, guild_id: str = None):
        is_owner = False
        try:
            is_owner = await self.bot.is_owner(interaction.user)
        except Exception:
            pass
        if not is_owner and not (interaction.user.guild_permissions.administrator if interaction.guild else False):
            await interaction.response.send_message("You must be a server admin or bot owner to use this.", ephemeral=True)
            return
        try:
            if guild_id:
                guild_obj = discord.Object(id=int(guild_id))
                await self.bot.tree.sync(guild=guild_obj)
                await interaction.response.send_message(f"Synced commands to guild {guild_id}")
            else:
                await self.bot.tree.sync()
                await interaction.response.send_message("Synced global commands")
        except Exception as e:
            await interaction.response.send_message(f"Sync failed: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
