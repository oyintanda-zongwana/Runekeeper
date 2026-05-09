"""
Trial Candidate System
Handles trial applications, approvals, denials, and automatic role management.
"""
import discord
from discord.ext import commands
from discord import app_commands
import time
from config import get_config
from utils import db
from utils.themes import (
    create_trial_embed, create_success_embed, create_error_embed,
    Colors, Lore, Emojis
)
from utils.decorators import require_trial_reviewer
from utils.interactions import InteractionHandler, PermissionHelper, cooldown_manager

class TrialButtons(discord.ui.View):
    """Approval/Denial buttons for trial candidates."""
    
    def __init__(self, trial_id: str, guild_id: int, user_id: int, bot):
        super().__init__(timeout=None)
        self.trial_id = trial_id
        self.guild_id = guild_id
        self.user_id = user_id
        self.bot = bot
        self.custom_id = f"trial_buttons_{trial_id}_{guild_id}"
    
    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji=Emojis.CHECK)
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = get_config()
        settings = config.get_guild_settings(self.guild_id)
        
        if not settings:
            embed = create_error_embed("Guild Not Configured", Lore.not_configured())
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        # Check reviewer permissions
        reviewer_roles = config.get_trial_reviewers(self.guild_id)
        perm_issue = PermissionHelper.get_missing_permissions(interaction.user, reviewer_roles)
        
        if perm_issue:
            embed = create_error_embed("Permission Denied", perm_issue)
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        # Check cooldown to prevent duplicate approvals
        if cooldown_manager.is_on_cooldown(interaction.user.id, f"trial_approve_{self.trial_id}", 2):
            embed = create_error_embed("Too Fast", "Please wait before approving this trial again.")
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        # Get trial and approve
        trial = db.get_trial(self.guild_id, self.trial_id)
        if not trial:
            embed = create_error_embed("Trial Not Found", "This trial has been deleted.")
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        # Check if already decided (index 4 is status column)
        if trial[4] != "pending":
            embed = create_error_embed("Already Decided", f"This trial was already {trial[4]}.")
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        # Approve
        db.approve_trial(self.guild_id, self.trial_id, interaction.user.id)
        cooldown_manager.set_cooldown(interaction.user.id, f"trial_approve_{self.trial_id}")
        
        # Assign role
        trial_role_id = settings.get("trial_role_id")
        if trial_role_id:
            try:
                guild = self.bot.get_guild(self.guild_id)
                member = guild.get_member(self.user_id)
                role = guild.get_role(int(trial_role_id))
                if member and role:
                    await member.add_roles(role)
            except discord.Forbidden:
                # Bot lacks permission to assign role, but approval still goes through
                pass
            except Exception as e:
                print(f"Error assigning trial role: {e}")
        
        embed = create_success_embed(
            "Trial Approved",
            f"{Lore.trial_approved()}\n\nApproved by {interaction.user.mention}"
        )
        await InteractionHandler.safe_respond(interaction, embed)
        
        # Notify candidate
        try:
            user = await self.bot.fetch_user(self.user_id)
            await user.send(embed=create_success_embed(
                f"{Emojis.CHECK} Your Trial Has Been Approved",
                Lore.trial_approved()
            ))
        except:
            pass
    
    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, emoji=Emojis.CROSS)
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = get_config()
        settings = config.get_guild_settings(self.guild_id)
        
        if not settings:
            embed = create_error_embed("Guild Not Configured", Lore.not_configured())
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        # Check reviewer permissions
        reviewer_roles = config.get_trial_reviewers(self.guild_id)
        perm_issue = PermissionHelper.get_missing_permissions(interaction.user, reviewer_roles)
        
        if perm_issue:
            embed = create_error_embed("Permission Denied", perm_issue)
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        # Check cooldown to prevent duplicate denials
        if cooldown_manager.is_on_cooldown(interaction.user.id, f"trial_deny_{self.trial_id}", 2):
            embed = create_error_embed("Too Fast", "Please wait before denying this trial again.")
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        # Get trial and deny
        trial = db.get_trial(self.guild_id, self.trial_id)
        if not trial:
            embed = create_error_embed("Trial Not Found", "This trial has been deleted.")
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        # Check if already decided
        if trial[4] != "pending":
            embed = create_error_embed("Already Decided", f"This trial was already {trial[4]}.")
            return await InteractionHandler.safe_respond(interaction, embed, ephemeral=True)
        
        db.deny_trial(self.guild_id, self.trial_id, interaction.user.id)
        cooldown_manager.set_cooldown(interaction.user.id, f"trial_deny_{self.trial_id}")
        
        embed = create_error_embed(
            "Trial Denied",
            f"{Lore.trial_denied()}\n\nDenied by {interaction.user.mention}"
        )
        await InteractionHandler.safe_respond(interaction, embed)
        
        # Notify candidate
        try:
            user = await self.bot.fetch_user(self.user_id)
            await user.send(embed=create_error_embed(
                f"{Emojis.CROSS} Your Trial Has Been Denied",
                Lore.trial_denied()
            ))
        except:
            pass


class Trials(commands.Cog):
    """Trial candidate system for Hall of the Slain."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="applyfortrial", description="Apply to become a trial candidate")
    @app_commands.describe(reason="Why you wish to join the Hall of the Slain")
    async def apply(self, interaction: discord.Interaction, reason: str):
        """Submit a trial application."""
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        if not settings:
            embed = create_error_embed("Guild Not Configured", "This guild hasn't set up the trial system.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Check if already pending
        existing = db.get_pending_trials(interaction.guild.id, interaction.user.id)
        if existing:
            embed = create_error_embed(
                "Already Pending",
                "You already have a pending trial application. Please wait for a decision."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Create trial
        trial_id = db.add_trial(
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
            application_text=reason
        )
        
        embed = create_trial_embed(
            "Trial Submitted",
            Lore.trial_submitted(),
            fields=[
                ("Applicant", interaction.user.mention, True),
                ("Application", reason, False)
            ],
            status="pending"
        )
        
        # Send to trial channel
        trial_channel_id = settings.get("trial_channel")
        if trial_channel_id:
            channel = interaction.guild.get_channel(trial_channel_id)
            if channel:
                view = TrialButtons(trial_id, interaction.guild.id, interaction.user.id, self.bot)
                message = await channel.send(embed=embed, view=view)
                self.bot.add_view(view, message_id=message.id)
                # Update trial with message_id
                db._execute("UPDATE trial_candidates SET message_id = ? WHERE guild_id = ? AND trial_id = ?", (str(message.id), str(interaction.guild.id), trial_id))
        
        await interaction.response.send_message(
            embed=create_success_embed("Application Submitted", Lore.trial_submitted()),
            ephemeral=True
        )
    
    @app_commands.command(name="trialstatus", description="Check your trial status")
    async def status(self, interaction: discord.Interaction):
        """Check trial application status."""
        trials = db.get_user_trials(interaction.guild.id, interaction.user.id)
        
        if not trials:
            embed = create_error_embed(
                "No Trials Found",
                "You have no trial applications."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        latest = trials[0]
        status_text = f"**Status**: {latest[2].upper()}"
        
        if latest[2] == "approved":
            status_text += f"\n**Approved by**: <@{latest[4]}>"
            status_text += f"\n**Date**: <t:{int(latest[5])}:f>"
        elif latest[2] == "denied":
            status_text += f"\n**Denied by**: <@{latest[4]}>"
            status_text += f"\n**Date**: <t:{int(latest[5])}:f>"
        
        embed = create_trial_embed(
            "Your Trial Status",
            status_text,
            status=latest[2]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="viewtrials", description="View pending trials")
    @app_commands.describe(status="Filter by status (pending, approved, denied, or all)")
    async def viewtrials(
        self,
        interaction: discord.Interaction,
        status: str = "pending"
    ):
        """View trials (reviewer only)."""
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        
        if not has_perm:
            embed = create_error_embed(
                "Permission Denied",
                "You don't have permission to view trials."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        trials = db.get_all_trials(interaction.guild.id)
        if status != "all":
            trials = [t for t in trials if t[2] == status]
        
        if not trials:
            embed = create_error_embed(
                "No Trials",
                f"No {status} trials found."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        trials_text = "\n".join([
            f"{Emojis.SCROLL} **<@{t[1]}>** - {t[2].upper()} (Applied: <t:{int(t[3])}:R>)"
            for t in trials[:10]  # Show first 10
        ])
        
        embed = create_trial_embed(
            f"Trials ({status.upper()})",
            trials_text,
            status=status if status != "all" else "pending"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Trials(bot))
    
    # Load persistent trial views
    trials = db._fetchall("SELECT guild_id, trial_id, user_id, message_id FROM trial_candidates WHERE status = 'pending' AND message_id IS NOT NULL")
    for trial in trials:
        guild_id = int(trial[0])
        trial_id = trial[1]
        user_id = int(trial[2])
        message_id = int(trial[3])
        view = TrialButtons(trial_id, guild_id, user_id, bot)
        bot.add_view(view, message_id=message_id)
