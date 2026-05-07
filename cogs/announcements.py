"""
Announcement & Embed System
Creates themed announcements for Hall of the Slain.
"""
import discord
from discord.ext import commands
from discord import app_commands
from config import get_config
from utils.themes import (
    create_embed, create_success_embed, create_error_embed,
    Colors, Lore, Emojis
)

class Announcements(commands.Cog):
    """Announcement system for Hall of the Slain."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="announce", description="Make a themed announcement")
    @app_commands.describe(
        title="Announcement title",
        message="Announcement content",
        channel="Channel to post in (defaults to current)",
        color="Color theme (gold, blood, rune, or black)"
    )
    async def announce(
        self,
        interaction: discord.Interaction,
        title: str,
        message: str,
        channel: discord.TextChannel = None,
        color: str = "gold"
    ):
        """Create a themed announcement."""
        # Check if user has permission
        if not interaction.user.guild_permissions.administrator:
            embed = create_error_embed(
                "Permission Denied",
                "Only administrators can make announcements."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Map color names to values
        colors = {
            "gold": Colors.GOLD,
            "blood": Colors.BLOOD,
            "rune": Colors.RUNE,
            "black": Colors.BLACK,
            "white": Colors.WHITE,
            "steel": Colors.STEEL
        }
        
        selected_color = colors.get(color.lower(), Colors.GOLD)
        
        # Create embed
        embed = create_embed(
            title=f"📢 {title}",
            description=message,
            color=selected_color,
            footer_text="Hall of the Slain"
        )
        
        # Post announcement
        target_channel = channel or interaction.channel
        await target_channel.send(embed=embed)
        
        # Confirm
        confirm_embed = create_success_embed(
            "Announcement Posted",
            f"Your announcement has been posted to {target_channel.mention}"
        )
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
    
    @app_commands.command(name="celebratevictory", description="Celebrate a victory with a themed announcement")
    @app_commands.describe(
        winner="The victor",
        achievement="What was achieved"
    )
    async def victory(
        self,
        interaction: discord.Interaction,
        winner: discord.User,
        achievement: str
    ):
        """Post a victory announcement."""
        embed = create_embed(
            title="⚔️ VICTORY!",
            description=f"{Lore.tournament_victory(winner.mention)}\n\n**Achievement**: {achievement}",
            color=Colors.TRIUMPH,
            footer_text="Hall of Glory"
        )
        
        await interaction.channel.send(embed=embed)
        
        await interaction.response.send_message(
            embed=create_success_embed("Victory Announced", "The victory has been announced!"),
            ephemeral=True
        )
    
    @app_commands.command(name="themedmessage", description="Create a custom themed message")
    @app_commands.describe(
        title="Message title",
        content="Message content",
        theme="Theme (trial, tournament, event, appeal, or custom)"
    )
    async def themed_message(
        self,
        interaction: discord.Interaction,
        title: str,
        content: str,
        theme: str = "custom"
    ):
        """Create a custom themed message."""
        # Check if user has permission
        if not interaction.user.guild_permissions.administrator:
            embed = create_error_embed(
                "Permission Denied",
                "Only administrators can post themed messages."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Map themes to colors
        theme_colors = {
            "trial": Colors.RUNE,
            "tournament": Colors.BLOOD,
            "event": Colors.RUNE,
            "appeal": Colors.INFO,
            "custom": Colors.GOLD
        }
        
        selected_color = theme_colors.get(theme.lower(), Colors.GOLD)
        emoji = {
            "trial": "🛡️",
            "tournament": "⚔️",
            "event": "📢",
            "appeal": "⚖️",
            "custom": "📜"
        }.get(theme.lower(), "📜")
        
        # Create embed
        embed = create_embed(
            title=f"{emoji} {title}",
            description=content,
            color=selected_color,
            footer_text="Hall of the Slain"
        )
        
        await interaction.channel.send(embed=embed)
        
        await interaction.response.send_message(
            embed=create_success_embed("Message Posted", "Your themed message has been posted!"),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Announcements(bot))
