"""
Hall Information System
Displays guild lore, rules, and important information about Hall of the Slain.
"""
import discord
from discord.ext import commands
from discord import app_commands
from config import get_config
from utils.themes import create_info_embed, Colors, Lore, Emojis
from utils.decorators import require_guild_configured

class HallInfo(commands.Cog):
    """Hall of the Slain information commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="hallinfo", description="View Hall of the Slain information")
    @app_commands.describe(section="Which section to view (rules, lore, roles, or all)")
    async def hallinfo(
        self,
        interaction: discord.Interaction,
        section: str = "all"
    ):
        """Display Hall information."""
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        if not settings:
            embed = discord.Embed(
                title="❌ Guild Not Configured",
                description="This guild has not been configured for Runekeeper.",
                color=Colors.WARNING
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        hall_info = settings.get("hall_info", {})
        section = section.lower()
        
        if section in ["rules", "all"]:
            rules = hall_info.get("rules", "No rules configured.")
            embed = create_info_embed(
                "Rules of the Hall",
                rules,
                color=Colors.GOLD
            )
            await interaction.response.send_message(embed=embed)
        
        if section in ["lore", "all"]:
            lore = hall_info.get("lore", "No lore configured.")
            embed = create_info_embed(
                "The Lore of the Hall",
                lore,
                color=Colors.RUNE
            )
            if section == "all":
                await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(embed=embed)
        
        if section in ["roles", "all"]:
            guild_roles = settings.get("guild_roles", {})
            if guild_roles:
                role_text = "\n".join([f"{Emojis.CROWN} **{name}** - <@&{role_id}>" 
                                       for name, role_id in guild_roles.items()])
            else:
                role_text = "No roles configured."
            
            embed = create_info_embed(
                "Hall Positions",
                role_text,
                color=Colors.BLOOD
            )
            if section == "all":
                await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="members", description="View hall membership")
    async def members(self, interaction: discord.Interaction):
        """Display active members of the Hall."""
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        if not settings:
            embed = discord.Embed(
                title="❌ Guild Not Configured",
                description="This guild has not been configured for Runekeeper.",
                color=Colors.WARNING
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        trial_role_id = settings.get("trial_role_id")
        if trial_role_id:
            trial_role = interaction.guild.get_role(trial_role_id)
            if trial_role:
                members = ", ".join([m.mention for m in trial_role.members]) or "None"
                embed = create_info_embed(
                    "Trial Candidates",
                    members,
                    color=Colors.INFO
                )
                await interaction.response.send_message(embed=embed)
                return
        
        # Fallback: show all members
        embed = create_info_embed(
            "Hall Members",
            f"{interaction.guild.member_count} warriors",
            color=Colors.GOLD
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HallInfo(bot))
