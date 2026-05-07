"""
Internal Logging System
Tracks all Runekeeper actions (separate from Sapphire moderation logs).
Logs trial decisions, tournament results, role assignments, appeals, etc.
"""
import discord
from discord.ext import commands
from discord import app_commands
from config import get_config
from utils import db
from utils.themes import (
    create_info_embed, Colors, Lore, Emojis
)

class Logging(commands.Cog):
    """Internal logging system for Runekeeper."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="viewlogs", description="View Runekeeper action logs")
    @app_commands.describe(
        action="Filter by action type (or 'all')",
        limit="Number of logs to show (default 10)"
    )
    async def view_logs(
        self,
        interaction: discord.Interaction,
        action: str = "all",
        limit: int = 10
    ):
        """View internal action logs."""
        # Check if user has permission to view logs
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        if not settings:
            embed = discord.Embed(
                title="❌ Guild Not Configured",
                description="This guild has not been configured for Runekeeper.",
                color=Colors.WARNING
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Get logs
        logs = db.get_logs(interaction.guild.id, limit=min(limit, 50))
        
        if not logs:
            embed = discord.Embed(
                title="📜 No Logs",
                description="No action logs found.",
                color=Colors.INFO
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Filter by action if specified
        if action != "all":
            logs = [l for l in logs if l[2].lower() == action.lower()]
        
        if not logs:
            embed = discord.Embed(
                title="📜 No Logs",
                description=f"No logs found for action: {action}",
                color=Colors.INFO
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Format logs
        logs_text = ""
        for log in logs[:10]:
            log_id, guild_id, action_type, actor_id, target_id, details, timestamp = log
            actor = f"<@{actor_id}>" if actor_id else "System"
            target = f"<@{target_id}>" if target_id else "N/A"
            time_str = f"<t:{int(timestamp)}:R>"
            
            logs_text += f"**{action_type.upper()}** - {time_str}\n"
            logs_text += f"  Actor: {actor} | Target: {target}\n"
            if details:
                logs_text += f"  Details: {details}\n"
            logs_text += "\n"
        
        embed = create_info_embed(
            "Action Logs",
            logs_text,
            color=Colors.BLACK,
            footer="Runekeeper Internal Logs"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="logaction", description="Manually log an action")
    @app_commands.describe(
        action="Type of action",
        target="Target user",
        details="Additional details"
    )
    async def log_action(
        self,
        interaction: discord.Interaction,
        action: str,
        target: discord.User,
        details: str = ""
    ):
        """Manually log an action (admin only)."""
        # Check if user is bot owner or admin
        if not interaction.user.id == interaction.client.owner_id:
            if not interaction.user.guild_permissions.administrator:
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="Only administrators can manually log actions.",
                    color=Colors.WARNING
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Log the action
        db.log_action(
            guild_id=interaction.guild.id,
            action=action,
            actor_id=interaction.user.id,
            target_id=target.id,
            details=details
        )
        
        embed = discord.Embed(
            title="✅ Action Logged",
            description=f"**Action**: {action}\n**Target**: {target.mention}\n**Details**: {details or 'N/A'}",
            color=Colors.SUCCESS
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Logging(bot))
