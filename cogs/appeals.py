"""
Appeal System
Handles punishment appeals for banned or muted members.
"""
import discord
from discord.ext import commands
from discord import app_commands
import time
from config import get_config
from utils import db
from utils.themes import (
    create_appeal_embed, create_success_embed, create_error_embed,
    Colors, Lore, Emojis
)
from utils.decorators import require_appeal_reviewer
from utils.interactions import InteractionHandler, PermissionHelper, cooldown_manager

class AppealButtons(discord.ui.View):
    """Approval/Denial buttons for appeals."""
    
    def __init__(self, appeal_id: str, guild_id: int, user_id: int, bot):
        super().__init__(timeout=None)
        self.appeal_id = appeal_id
        self.guild_id = guild_id
        self.user_id = user_id
        self.bot = bot
    
    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji=Emojis.CHECK)
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = get_config()
        
        # Check reviewer permissions
        reviewer_roles = config.get_appeal_reviewers(self.guild_id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        
        if not has_perm:
            return await interaction.response.send_message(
                "You don't have permission to review appeals.",
                ephemeral=True
            )
        
        # Get appeal and approve
        appeal = db.get_appeal(self.guild_id, self.appeal_id)
        if not appeal or appeal[4] != "pending":
            return await interaction.response.send_message(
                "This appeal has already been decided.",
                ephemeral=True
            )
        
        db.approve_appeal(self.guild_id, self.appeal_id, interaction.user.id)
        db.log_action(self.guild_id, "appeal_approved", interaction.user.id, self.user_id, f"Appeal '{self.appeal_id}' approved")
        
        embed = create_success_embed(
            "Appeal Approved",
            f"{Lore.appeal_approved()}\n\nApproved by {interaction.user.mention}"
        )
        await interaction.response.send_message(embed=embed)
        
        # Notify appellant
        try:
            user = await self.bot.fetch_user(self.user_id)
            await user.send(embed=create_success_embed(
                "Your Appeal Has Been Approved",
                Lore.appeal_approved()
            ))
        except:
            pass
    
    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, emoji=Emojis.CROSS)
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = get_config()
        
        # Check reviewer permissions
        reviewer_roles = config.get_appeal_reviewers(self.guild_id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        
        if not has_perm:
            return await interaction.response.send_message(
                "You don't have permission to review appeals.",
                ephemeral=True
            )
        
        # Get appeal and deny
        appeal = db.get_appeal(self.guild_id, self.appeal_id)
        if not appeal or appeal[4] != "pending":
            return await interaction.response.send_message(
                "This appeal has already been decided.",
                ephemeral=True
            )
        
        db.deny_appeal(self.guild_id, self.appeal_id, interaction.user.id)
        db.log_action(self.guild_id, "appeal_denied", interaction.user.id, self.user_id, f"Appeal '{self.appeal_id}' denied")
        
        embed = create_error_embed(
            "Appeal Denied",
            f"Your appeal has been denied.\n\nDenied by {interaction.user.mention}"
        )
        await interaction.response.send_message(embed=embed)
        
        # Notify appellant
        try:
            user = await self.bot.fetch_user(self.user_id)
            await user.send(embed=create_error_embed(
                "Your Appeal Has Been Denied",
                "Unfortunately, your appeal has been denied. The Council's judgment stands."
            ))
        except:
            pass


class Appeals(commands.Cog):
    """Appeal system for Hall of the Slain."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="appeal", description="Submit an appeal")
    @app_commands.describe(reason="Reason for your appeal")
    async def submit_appeal(
        self,
        interaction: discord.Interaction,
        reason: str
    ):
        """Submit an appeal for a punishment."""
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        if not settings:
            embed = create_error_embed("Guild Not Configured", "This guild hasn't set up appeals.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Check if user already has pending appeal
        pending = db.get_user_pending_appeals(interaction.guild.id, interaction.user.id)
        if pending:
            embed = create_error_embed(
                "Already Pending",
                "You already have a pending appeal. Please wait for a decision."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Submit appeal
        appeal_id = db.submit_appeal(
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
            reason=reason
        )
        db.log_action(interaction.guild.id, "appeal_submitted", interaction.user.id, None, f"Appeal '{appeal_id}' submitted")
        
        embed = create_appeal_embed(
            "Appeal Submitted",
            Lore.appeal_submitted(),
            fields=[
                ("Appellant", interaction.user.mention, True),
                ("Reason", reason, False)
            ],
            status="pending"
        )
        
        # Send to appeals channel
        appeals_channel_id = settings.get("appeals_channel")
        if appeals_channel_id:
            channel = interaction.guild.get_channel(appeals_channel_id)
            if channel:
                view = AppealButtons(appeal_id, interaction.guild.id, interaction.user.id, self.bot)
                await channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(
            embed=create_success_embed("Appeal Submitted", Lore.appeal_submitted()),
            ephemeral=True
        )
    
    @app_commands.command(name="appealstatus", description="Check your appeal status")
    async def appeal_status(self, interaction: discord.Interaction):
        """Check appeal status."""
        appeals = db.get_user_appeals(interaction.guild.id, interaction.user.id)
        
        if not appeals:
            embed = create_error_embed(
                "No Appeals",
                "You have no appeals."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        latest = appeals[0]
        status_text = f"**Status**: {latest[4].upper()}"
        
        if latest[4] == "approved":
            status_text += f"\n**Approved by**: <@{latest[5]}>"
            status_text += f"\n**Date**: <t:{int(latest[6])}:f>"
        elif latest[4] == "denied":
            status_text += f"\n**Denied by**: <@{latest[5]}>"
            status_text += f"\n**Date**: <t:{int(latest[6])}:f>"
        
        embed = create_appeal_embed(
            "Your Appeal Status",
            status_text,
            status=latest[4]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="viewappeals", description="View pending appeals")
    @app_commands.describe(status="Filter by status (pending, approved, denied, or all)")
    async def view_appeals(
        self,
        interaction: discord.Interaction,
        status: str = "pending"
    ):
        """View appeals (reviewer only)."""
        config = get_config()
        reviewer_roles = config.get_appeal_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        
        if not has_perm:
            embed = create_error_embed(
                "Permission Denied",
                "You don't have permission to view appeals."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        appeals = db.get_all_appeals(interaction.guild.id)
        if status != "all":
            appeals = [a for a in appeals if a[4] == status]
        
        if not appeals:
            embed = create_error_embed(
                "No Appeals",
                f"No {status} appeals found."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        appeals_text = "\n".join([
            f"{Emojis.JUDGE} **<@{a[2]}>** - {a[4].upper()} (Submitted: <t:{int(a[5])}:R>)"
            for a in appeals[:10]  # Show first 10
        ])
        
        embed = create_appeal_embed(
            f"Appeals ({status.upper()})",
            appeals_text,
            status=status if status != "all" else "pending"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Appeals(bot))
