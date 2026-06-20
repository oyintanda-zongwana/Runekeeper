import discord
from discord import app_commands
from discord.ext import commands

class HelpCog(commands.Cog):
    """Auto-generated help based on registered application commands and cogs."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show the Runekeeper help and command listing")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Runekeeper Help", color=discord.Color.blurple())
        for cog_name, cog in self.bot.cogs.items():
            # collect commands for this cog
            lines = []
            for command in self.bot.tree.get_commands():
                # command is app_commands.Command
                if command.parent is None and command.callback:
                    # Try to filter by cog if possible
                    # The mapping between app_commands and cogs isn't always direct; show top-level commands
                    lines.append(f"/{command.name} — {command.description}")
            if lines:
                embed.add_field(name=cog_name, value="\n".join(lines)[:1024], inline=False)
        # Fallback: list global commands
        if not embed.fields:
            lines = [f"/{c.name} — {c.description}" for c in self.bot.tree.get_commands()]
            embed.description = "\n".join(lines)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
