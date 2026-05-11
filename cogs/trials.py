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
    create_trial_embed, create_success_embed, create_error_embed, create_info_embed,
    Colors, Lore, Emojis
)
from utils.decorators import require_trial_reviewer
from utils.interactions import InteractionHandler, PermissionHelper, cooldown_manager

class TrialApplicationModal(discord.ui.Modal, title="Trial Application"):
    age = discord.ui.TextInput(
        label="Age",
        placeholder="Your age",
        required=True,
        max_length=3
    )
    region = discord.ui.TextInput(
        label="Region",
        placeholder="Your region/country",
        required=True,
        max_length=50
    )
    rank = discord.ui.TextInput(
        label="Current Brawl Stars Rank",
        placeholder="e.g., Mythic III",
        required=True,
        max_length=20
    )
    experience = discord.ui.TextInput(
        label="Gaming Experience",
        style=discord.TextStyle.paragraph,
        placeholder="How long have you played Brawl Stars? Any other games?",
        required=True,
        max_length=500
    )
    why_join = discord.ui.TextInput(
        label="Why do you want to join the Hall?",
        style=discord.TextStyle.paragraph,
        placeholder="What interests you about our guild?",
        required=True,
        max_length=500
    )
    availability = discord.ui.TextInput(
        label="Availability",
        placeholder="When are you usually available to play?",
        required=True,
        max_length=100
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
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
        
        # Create trial with full data
        application_data = {
            "age": self.age.value,
            "region": self.region.value,
            "rank": self.rank.value,
            "experience": self.experience.value,
            "why_join": self.why_join.value,
            "availability": self.availability.value
        }
        import json
        trial_id = db.add_trial(
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
            application_text=json.dumps(application_data)
        )
        
        # Assign Aspirant role
        aspirant_role_id = settings.get("aspirant_role_id")
        if aspirant_role_id:
            try:
                role = interaction.guild.get_role(int(aspirant_role_id))
                if role:
                    await interaction.user.add_roles(role)
            except Exception as e:
                print(f"Error assigning aspirant role: {e}")
        
        # Post to gatekeeper channel
        gatekeeper_channel_id = settings.get("gatekeeper_channel")
        if gatekeeper_channel_id:
            try:
                gatekeeper_channel_id = int(gatekeeper_channel_id)
            except (TypeError, ValueError):
                pass
            channel = interaction.guild.get_channel(gatekeeper_channel_id)
            if channel:
                embed = create_trial_embed(
                    f"New Trial Application - {interaction.user.display_name}",
                    f"**Age:** {self.age.value}\n**Region:** {self.region.value}\n**Rank:** {self.rank.value}\n**Experience:** {self.experience.value}\n**Why Join:** {self.why_join.value}\n**Availability:** {self.availability.value}",
                    fields=[
                        ("Applicant", interaction.user.mention, True),
                        ("Applied At", discord.utils.format_dt(discord.utils.utcnow(), style="f"), True)
                    ],
                    status="pending"
                )
                view = TrialQueueView(trial_id, interaction.user.id, self.cog.bot)
                message = await channel.send(embed=embed, view=view)
                db.update_trial_message_id(interaction.guild.id, trial_id, message.id)
        
        embed = create_success_embed("Application Submitted", Lore.trial_submitted())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class TrialQueueView(discord.ui.View):
    def __init__(self, trial_id, applicant_id, bot):
        super().__init__(timeout=None)
        self.add_item(TrialAssignmentButton(trial_id, applicant_id, bot))
        self.add_item(TrialRejectButton(trial_id, applicant_id, bot))
        self.add_item(TrialHoldButton(trial_id, applicant_id, bot))

class TrialAssignmentButton(discord.ui.Button):
    def __init__(self, trial_id, applicant_id, bot):
        super().__init__(label="⚔️ I Will Test", style=discord.ButtonStyle.primary, emoji="⚔️")
        self.trial_id = trial_id
        self.applicant_id = applicant_id
        self.bot = bot
        self.custom_id = f"trial_assign_{trial_id}"

    async def callback(self, interaction: discord.Interaction):
        # Check if already assigned
        trial = db.get_trial(interaction.guild.id, self.trial_id)
        if not trial:
            embed = create_error_embed("Trial Not Found", "This trial does not exist.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if trial[6] or trial[4] != "pending":
            embed = create_error_embed("Already Assigned", "This trial has already been assigned or processed.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        applicant = interaction.guild.get_member(self.applicant_id)
        if not applicant:
            embed = create_error_embed("Applicant Missing", "The applicant is no longer in the guild.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Assign
        db.assign_gatekeeper(interaction.guild.id, self.trial_id, interaction.user.id)
        
        # Create channel
        channel_name = f"trial-{applicant.name}"
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            applicant: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await interaction.guild.create_text_channel(channel_name, overwrites=overwrites)
        
        # Send form in channel
        embed = create_trial_embed(
            "📋 Trial Evaluation Form",
            f"Applicant: {applicant.mention}\nGatekeeper: {interaction.user.mention}\n\nConduct the trial and submit the result below.",
            status="in_progress"
        )
        view = TrialChannelView(self.trial_id, self.applicant_id, interaction.user.id, channel)
        view.add_item(TrialResultButton(self.trial_id, self.applicant_id, interaction.user.id, channel))
        await channel.send(embed=embed, view=view)
        
        # Update original message
        await interaction.message.edit(content=f"Assigned Gatekeeper: {interaction.user.mention}", view=None)
        
        embed = create_success_embed("Trial Assigned", f"You have been assigned to test {applicant.mention}. Channel: {channel.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class TrialRejectButton(discord.ui.Button):
    def __init__(self, trial_id, applicant_id, bot):
        super().__init__(label="❌ Reject", style=discord.ButtonStyle.danger, emoji="❌")
        self.trial_id = trial_id
        self.applicant_id = applicant_id
        self.bot = bot
        self.custom_id = f"trial_reject_{trial_id}"

    async def callback(self, interaction: discord.Interaction):
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        if not has_perm:
            return await interaction.response.send_message("No permission.", ephemeral=True)
        
        db.deny_trial(interaction.guild.id, self.trial_id, interaction.user.id)
        db.log_action(interaction.guild.id, "trial_rejected", interaction.user.id, self.applicant_id, "Application rejected")
        
        # Remove role
        settings = config.get_guild_settings(interaction.guild.id)
        aspirant_role_id = settings.get("aspirant_role_id")
        if aspirant_role_id:
            try:
                member = interaction.guild.get_member(self.applicant_id)
                role = interaction.guild.get_role(int(aspirant_role_id))
                if member and role:
                    await member.remove_roles(role)
            except:
                pass
        
        await interaction.message.edit(content=f"Rejected by {interaction.user.mention}", view=None)
        await interaction.response.send_message("Application rejected.", ephemeral=True)

class TrialHoldButton(discord.ui.Button):
    def __init__(self, trial_id, applicant_id, bot):
        super().__init__(label="⏳ Hold", style=discord.ButtonStyle.secondary, emoji="⏳")
        self.trial_id = trial_id
        self.applicant_id = applicant_id
        self.bot = bot
        self.custom_id = f"trial_hold_{trial_id}"

    async def callback(self, interaction: discord.Interaction):
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        if not has_perm:
            return await interaction.response.send_message("No permission.", ephemeral=True)
        
        db.update_trial_status(interaction.guild.id, self.trial_id, "on_hold")
        await interaction.message.edit(content=f"Put on hold by {interaction.user.mention}", view=None)
        await interaction.response.send_message("Application put on hold.", ephemeral=True)

class TrialResultButton(discord.ui.Button):
    def __init__(self, trial_id, applicant_id, gatekeeper_id, channel):
        super().__init__(label="📝 Submit Trial Result", style=discord.ButtonStyle.success, emoji="📝")
        self.trial_id = trial_id
        self.applicant_id = applicant_id
        self.gatekeeper_id = gatekeeper_id
        self.channel = channel
        self.custom_id = f"trial_result_{trial_id}"

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.gatekeeper_id:
            return await interaction.response.send_message("Only the assigned gatekeeper can submit the result.", ephemeral=True)
        modal = TrialResultModal(self.trial_id, self.applicant_id, self.gatekeeper_id, self.channel)
        await interaction.response.send_modal(modal)

class TrialResultModal(discord.ui.Modal, title="Trial Result"):
    result = discord.ui.TextInput(
        label="Approve or Deny",
        placeholder="approve or deny",
        required=True,
        max_length=10
    )
    score = discord.ui.TextInput(
        label="Trial Score (1-10)",
        placeholder="e.g., 8",
        required=True,
        max_length=2
    )
    rank = discord.ui.TextInput(
        label="Rank in Brawl Stars",
        placeholder="e.g., Legendary I",
        required=True,
        max_length=20
    )
    recommended_role = discord.ui.TextInput(
        label="Recommended Hall Role",
        placeholder="e.g., Elder, Member",
        required=True,
        max_length=50
    )
    strengths = discord.ui.TextInput(
        label="Strengths",
        style=discord.TextStyle.paragraph,
        placeholder="What did they do well?",
        required=True,
        max_length=500
    )
    weaknesses = discord.ui.TextInput(
        label="Weaknesses",
        style=discord.TextStyle.paragraph,
        placeholder="Areas for improvement",
        required=False,
        max_length=500
    )
    notes = discord.ui.TextInput(
        label="Final Notes",
        style=discord.TextStyle.paragraph,
        placeholder="Any additional comments",
        required=False,
        max_length=500
    )

    def __init__(self, trial_id, applicant_id, gatekeeper_id, channel):
        super().__init__()
        self.trial_id = trial_id
        self.applicant_id = applicant_id
        self.gatekeeper_id = gatekeeper_id
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        result = self.result.value.lower().strip()
        if result not in ["approve", "deny"]:
            embed = create_error_embed("Invalid Result", "Please enter 'approve' or 'deny'.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        if result == "approve":
            db.approve_trial(interaction.guild.id, self.trial_id, self.gatekeeper_id)
            db.log_action(interaction.guild.id, "trial_approved", self.gatekeeper_id, self.applicant_id, f"Trial approved: Score {self.score.value}, Rank {self.rank.value}, Role {self.recommended_role.value}")
            
            # Assign role
            trial_role_id = settings.get("trial_role_id")
            if trial_role_id:
                try:
                    member = interaction.guild.get_member(self.applicant_id)
                    role = interaction.guild.get_role(int(trial_role_id))
                    if member and role:
                        await member.add_roles(role)
                except Exception as e:
                    print(f"Error assigning trial role: {e}")
        else:
            db.deny_trial(interaction.guild.id, self.trial_id, self.gatekeeper_id)
            db.log_action(interaction.guild.id, "trial_denied", self.gatekeeper_id, self.applicant_id, f"Trial denied: Score {self.score.value}, Rank {self.rank.value}")
            
            # Remove Aspirant role
            aspirant_role_id = settings.get("aspirant_role_id")
            if aspirant_role_id:
                try:
                    member = interaction.guild.get_member(self.applicant_id)
                    role = interaction.guild.get_role(int(aspirant_role_id))
                    if member and role:
                        await member.remove_roles(role)
                except Exception as e:
                    print(f"Error removing aspirant role: {e}")
        
        # Post report to gatekeeper channel
        gatekeeper_channel_id = settings.get("gatekeeper_channel")
        if gatekeeper_channel_id:
            try:
                gatekeeper_channel_id = int(gatekeeper_channel_id)
            except (TypeError, ValueError):
                pass
            channel = interaction.guild.get_channel(gatekeeper_channel_id)
            if channel:
                report_embed = create_trial_embed(
                    "⚔️ Trial Result",
                    f"Applicant: <@{self.applicant_id}>\n"
                    f"Gatekeeper: <@{self.gatekeeper_id}>\n"
                    f"Result: {'Approved ✅' if result == 'approve' else 'Denied ❌'}\n\n"
                    f"📊 Performance\n"
                    f"Score: {self.score.value}/10\n"
                    f"Rank: {self.rank.value}\n"
                    f"Recommended Role: {self.recommended_role.value}\n\n"
                    f"💪 Strengths\n{self.strengths.value}\n\n"
                    f"⚠️ Weaknesses\n{self.weaknesses.value or 'None'}\n\n"
                    f"📝 Notes\n{self.notes.value or 'None'}",
                    status="approved" if result == "approve" else "denied"
                )
                await channel.send(embed=report_embed)
        
        # Notify applicant
        try:
            user = await interaction.guild.fetch_member(self.applicant_id)
            embed = create_success_embed(
                f"⚔️ Trial {'Approved' if result == 'approve' else 'Denied'}",
                f"Score: {self.score.value}/10\nRank: {self.rank.value}\nRecommended Role: {self.recommended_role.value}\nStrengths: {self.strengths.value}"
            ) if result == "approve" else create_error_embed(
                "⚔️ Trial Denied",
                f"Score: {self.score.value}/10\nWeaknesses: {self.weaknesses.value or 'None'}"
            )
            await user.send(embed=embed)
        except:
            pass
        
        await interaction.response.send_message(embed=create_success_embed("Result Submitted", "Trial completed."), ephemeral=True)
        
        # Ask to close channel
        view = CleanupView(self.channel)
        await self.channel.send(embed=create_info_embed("Trial Complete", "Should we close this trial channel?", color=Colors.INFO), view=view)

class CleanupView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=86400)  # 24 hours
        self.channel = channel

    @discord.ui.button(label="✅ Close Now", style=discord.ButtonStyle.success)
    async def close_now(self, interaction: discord.Interaction):
        await interaction.response.send_message("Closing channel...", ephemeral=True)
        try:
            await self.channel.delete(reason="Trial completed")
        except:
            pass

    @discord.ui.button(label="🕒 Keep For 24h", style=discord.ButtonStyle.secondary)
    async def keep_24h(self, interaction: discord.Interaction):
        await interaction.response.send_message("Channel will be kept for 24 hours.", ephemeral=True)
        # In 24h, delete, but for now, just acknowledge

class TrialChannelView(discord.ui.View):
    def __init__(self, trial_id, applicant_id, gatekeeper_id, channel):
        super().__init__(timeout=None)
        self.add_item(TrialReassignButton(trial_id, applicant_id, gatekeeper_id, channel))
        self.add_item(TrialCancelButton(trial_id, applicant_id, gatekeeper_id, channel))

class TrialReassignButton(discord.ui.Button):
    def __init__(self, trial_id, applicant_id, gatekeeper_id, channel):
        super().__init__(label="🔄 Reassign", style=discord.ButtonStyle.secondary, emoji="🔄")
        self.trial_id = trial_id
        self.applicant_id = applicant_id
        self.gatekeeper_id = gatekeeper_id
        self.channel = channel
        self.custom_id = f"trial_reassign_{trial_id}"

    async def callback(self, interaction: discord.Interaction):
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        if not has_perm:
            return await interaction.response.send_message("No permission.", ephemeral=True)
        
        # Reset assignment
        db.reset_trial_assignment(interaction.guild.id, self.trial_id)
        db.log_action(interaction.guild.id, "trial_reassigned", interaction.user.id, self.applicant_id, "Trial reassigned")
        
        await interaction.message.edit(content=f"Reassigned by {interaction.user.mention}", view=None)
        await interaction.response.send_message("Trial reassigned to queue.", ephemeral=True)
        
        # Delete channel
        try:
            await self.channel.delete(reason="Trial reassigned")
        except:
            pass

class TrialCancelButton(discord.ui.Button):
    def __init__(self, trial_id, applicant_id, gatekeeper_id, channel):
        super().__init__(label="❌ Cancel", style=discord.ButtonStyle.danger, emoji="❌")
        self.trial_id = trial_id
        self.applicant_id = applicant_id
        self.gatekeeper_id = gatekeeper_id
        self.channel = channel
        self.custom_id = f"trial_cancel_{trial_id}"

    async def callback(self, interaction: discord.Interaction):
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        if not has_perm:
            return await interaction.response.send_message("No permission.", ephemeral=True)
        
        # Cancel trial
        db.deny_trial(interaction.guild.id, self.trial_id, interaction.user.id)
        db.log_action(interaction.guild.id, "trial_cancelled", interaction.user.id, self.applicant_id, "Trial cancelled")
        
        # Remove Aspirant role
        settings = config.get_guild_settings(interaction.guild.id)
        aspirant_role_id = settings.get("aspirant_role_id")
        if aspirant_role_id:
            try:
                member = interaction.guild.get_member(self.applicant_id)
                role = interaction.guild.get_role(int(aspirant_role_id))
                if member and role:
                    await member.remove_roles(role)
            except:
                pass
        
        await interaction.message.edit(content=f"Cancelled by {interaction.user.mention}", view=None)
        await interaction.response.send_message("Trial cancelled.", ephemeral=True)
        
        # Delete channel
        try:
            await self.channel.delete(reason="Trial cancelled")
        except:
            pass

class TrialButtons(discord.ui.View):
    """Approval/Denial buttons for trial candidates."""
    
    def __init__(self, trial_id: str, guild_id: int, user_id: int, bot):
        super().__init__(timeout=None)
        self.trial_id = trial_id
        self.guild_id = guild_id
        self.user_id = user_id
        self.bot = bot
        self.custom_id = f"trial_buttons_{trial_id}_{guild_id}"
    
    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji=Emojis.CHECK, custom_id="trial_approve")
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
        db.log_action(self.guild_id, "trial_approved", interaction.user.id, self.user_id, f"Trial approved by {interaction.user.display_name}")
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
    
    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, emoji=Emojis.CROSS, custom_id="trial_deny")
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
        db.log_action(self.guild_id, "trial_denied", interaction.user.id, self.user_id, f"Trial denied by {interaction.user.display_name}")
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
    async def apply(self, interaction: discord.Interaction):
        """Submit a trial application."""
        modal = TrialApplicationModal(self)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="assign_gatekeeper", description="Assign a gatekeeper to conduct a trial")
    @app_commands.describe(applicant="The user applying for trial", gatekeeper="The gatekeeper to assign")
    async def assign_gatekeeper(self, interaction: discord.Interaction, applicant: discord.Member, gatekeeper: discord.Member):
        """Assign a gatekeeper to a trial application."""
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        
        if not has_perm:
            embed = create_error_embed(
                "Permission Denied",
                "You don't have permission to assign gatekeepers."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Get pending trial for applicant
        trials = db.get_pending_trials(interaction.guild.id, applicant.id)
        if not trials:
            embed = create_error_embed(
                "No Pending Trial",
                f"{applicant.mention} has no pending trial application."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        trial = trials[0]
        trial_id = trial[0]
        
        # Create private channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            applicant: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            gatekeeper: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel_name = f"trial-{applicant.name}-{gatekeeper.name}"
        channel = await interaction.guild.create_text_channel(channel_name, overwrites=overwrites, category=None)
        
        # Send application embed
        application_text = trial[3]
        try:
            import json
            application_data = json.loads(application_text)
            description = (
                f"**Age:** {application_data.get('age')}\n"
                f"**Region:** {application_data.get('region')}\n"
                f"**Rank:** {application_data.get('rank')}\n"
                f"**Experience:** {application_data.get('experience')}\n"
                f"**Why Join:** {application_data.get('why_join')}\n"
                f"**Availability:** {application_data.get('availability')}"
            )
        except Exception:
            description = application_text

        embed = create_trial_embed(
            f"Trial for {applicant.display_name}",
            description,
            fields=[
                ("Applicant", applicant.mention, True),
                ("Gatekeeper", gatekeeper.mention, True),
                ("Channel", channel.mention, True)
            ],
            status="in_progress"
        )
        await channel.send(embed=embed)
        
        # Send modal to gatekeeper
        await gatekeeper.send(embed=create_info_embed(
            "Trial Assigned",
            f"You have been assigned to conduct the trial for {applicant.mention}.\nPlease review their application in {channel.mention} and submit the result.",
            color=Colors.INFO
        ))
        
        # For simplicity, since modals can't be sent in DM easily, perhaps send a button that opens modal, but modals are for interactions.
        # Actually, to send modal to user, it's tricky. Perhaps send a message with button, and on click, open modal.
        # But for now, since it's DM, perhaps just send instructions, and have a command for gatekeeper to submit result.
        
        # Better: add a command /submit_trial_result trial_id result reason
        
        # But to keep it modal, perhaps the gatekeeper uses /conduct_trial or something.
        
        # For now, send the modal via DM, but since DM doesn't support modals directly, use a button that the gatekeeper clicks in DM to open modal.
        
        # Discord doesn't support modals in DM. So, need to have the gatekeeper use a slash command in the channel.
        
        # So, in the channel, send a button for the gatekeeper to submit result.
        
        # Add a button in the channel for gatekeeper to submit result.
        
        # Create a view with button that opens modal.
        
        class SubmitResultButton(discord.ui.Button):
            def __init__(self, cog, trial_id, applicant_id, channel):
                super().__init__(label="Submit Trial Result", style=discord.ButtonStyle.primary, emoji=Emojis.SCROLL)
                self.cog = cog
                self.trial_id = trial_id
                self.applicant_id = applicant_id
                self.channel = channel
            
            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != gatekeeper.id:
                    return await interaction.response.send_message("Only the assigned gatekeeper can submit the result.", ephemeral=True)
                modal = TrialResultModal(self.trial_id, self.applicant_id, gatekeeper.id, self.channel)
                await interaction.response.send_modal(modal)
        
        view = discord.ui.View()
        view.add_item(SubmitResultButton(self, trial_id, applicant.id, channel))
        await channel.send(embed=create_info_embed("Trial Actions", "Gatekeeper, click the button below to submit the trial result.", color=Colors.INFO), view=view)
        
        # Assign the gatekeeper and update trial state
        db.assign_gatekeeper(interaction.guild.id, trial_id, gatekeeper.id)
        
        embed = create_success_embed(
            "Gatekeeper Assigned",
            f"Assigned {gatekeeper.mention} to conduct the trial for {applicant.mention}.\nCommunication channel: {channel.mention}"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
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
        status_text = f"**Status**: {latest[4].upper()}"
        
        if latest[4] == "approved":
            status_text += f"\n**Approved by**: <@{latest[6]}>"
            status_text += f"\n**Date**: <t:{int(latest[7])}:f>"
        elif latest[4] == "denied":
            status_text += f"\n**Denied by**: <@{latest[6]}>"
            status_text += f"\n**Date**: <t:{int(latest[7])}:f>"
        
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
            trials = [t for t in trials if t[4] == status]
        
        if not trials:
            embed = create_error_embed(
                "No Trials",
                f"No {status} trials found."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        trials_text = "\n".join([
            f"{Emojis.SCROLL} **<@{t[2]}>** - {t[4].upper()} (Applied: <t:{int(t[5])}:R>)"
            for t in trials[:10]  # Show first 10
        ])
        
        embed = create_trial_embed(
            f"Trials ({status.upper()})",
            trials_text,
            status=status if status != "all" else "pending"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="trialqueue", description="View pending trial queue")
    async def trial_queue(self, interaction: discord.Interaction):
        """View pending trials queue (reviewer only)."""
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        
        if not has_perm:
            embed = create_error_embed(
                "Permission Denied",
                "You don't have permission to view the trial queue."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        trials = db.get_pending_trials(interaction.guild.id)
        
        if not trials:
            embed = create_error_embed(
                "Empty Queue",
                "No pending trials in the queue."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        queue_text = ""
        for i, trial in enumerate(trials[:10], 1):
            user_id = trial[2]
            application_date = trial[5]
            queue_text += f"{i}. <@{user_id}> - Applied <t:{int(application_date)}:R>\n"
        
        embed = create_trial_embed(
            "Trial Queue",
            f"**Pending Trials**: {len(trials)}\n\n{queue_text}",
            status="pending"
        )
        view = TrialQueueResetView(interaction.guild.id, self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class TrialQueueResetView(discord.ui.View):
    def __init__(self, guild_id, bot):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.bot = bot

    @discord.ui.button(label="🧹 Clear Inactive (7+ days)", style=discord.ButtonStyle.secondary, emoji="🧹")
    async def clear_inactive(self, interaction: discord.Interaction):
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        if not has_perm:
            return await interaction.response.send_message("No permission.", ephemeral=True)
        
        # Get trials older than 7 days
        cutoff = time.time() - (7 * 24 * 60 * 60)
        old_trials = db._fetchall(
            "SELECT trial_id, user_id FROM trial_candidates WHERE guild_id = ? AND status = 'pending' AND application_date < ?",
            (interaction.guild.id, cutoff)
        )
        
        if not old_trials:
            return await interaction.response.send_message("No inactive trials to clear.", ephemeral=True)
        
        # Clear them
        for trial in old_trials:
            db.deny_trial(interaction.guild.id, trial[0], interaction.user.id)
            db.log_action(interaction.guild.id, "trial_auto_denied", interaction.user.id, trial[1], "Auto-denied for inactivity")
            
            # Remove Aspirant role
            settings = config.get_guild_settings(interaction.guild.id)
            aspirant_role_id = settings.get("aspirant_role_id")
            if aspirant_role_id:
                try:
                    member = interaction.guild.get_member(trial[1])
                    role = interaction.guild.get_role(int(aspirant_role_id))
                    if member and role:
                        await member.remove_roles(role)
                except:
                    pass
        
        await interaction.response.send_message(f"Cleared {len(old_trials)} inactive trials.", ephemeral=True)

    @discord.ui.button(label="🔄 Reset All Pending", style=discord.ButtonStyle.danger, emoji="🔄")
    async def reset_all_pending(self, interaction: discord.Interaction):
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(interaction.guild.id)
        has_perm = any(role.id in reviewer_roles for role in interaction.user.roles)
        if not has_perm:
            return await interaction.response.send_message("No permission.", ephemeral=True)
        
        # Confirmation modal
        modal = ResetConfirmationModal(self.guild_id, self.bot)
        await interaction.response.send_modal(modal)

class ResetConfirmationModal(discord.ui.Modal, title="Confirm Reset"):
    confirm = discord.ui.TextInput(
        label="Type 'RESET' to confirm",
        placeholder="RESET",
        required=True,
        max_length=10
    )

    def __init__(self, guild_id, bot):
        super().__init__()
        self.guild_id = guild_id
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirm.value.upper() != "RESET":
            embed = create_error_embed("Invalid Confirmation", "Please type 'RESET' to confirm.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Reset all pending trials
        pending_trials = db.get_pending_trials(self.guild_id)
        for trial in pending_trials:
            db.update_trial_status(self.guild_id, trial[0], "pending")  # Reset to pending
            db.log_action(self.guild_id, "trial_reset", interaction.user.id, trial[2], "Trial queue reset")
        
        await interaction.response.send_message(f"Reset {len(pending_trials)} trials to pending status.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Trials(bot))
    
    # Load persistent trial views
    trials = db._fetchall("SELECT guild_id, trial_id, user_id, message_id FROM trial_candidates WHERE status = 'pending' AND message_id IS NOT NULL")
    for trial in trials:
        guild_id = int(trial[0])
        trial_id = trial[1]
        user_id = int(trial[2])
        message_id = int(trial[3])
        view = TrialQueueView(trial_id, user_id, bot)
        bot.add_view(view, message_id=message_id)
