"""
Configuration Manager Cog
Allows admins to manage guild settings via slash commands.
"""
import discord
from discord.ext import commands
from discord import app_commands
from config import get_config
from utils.themes import create_success_embed, create_error_embed, create_info_embed, Colors, Emojis


class ConfigManager(commands.Cog):
    """Configuration management for Runekeeper."""
    
    def __init__(self, bot):
        self.bot = bot
    
    def is_guild_owner_or_admin(self, interaction: discord.Interaction) -> bool:
        """Check if user is guild owner or has admin permissions."""
        return interaction.user.id == interaction.guild.owner_id or interaction.user.guild_permissions.administrator
    
    @app_commands.command(name="config", description="Manage guild configuration")
    @app_commands.choices(action=[
        app_commands.Choice(name="view", value="view"),
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="reset", value="reset"),
    ])
    async def config(self, interaction: discord.Interaction, action: app_commands.Choice[str]):
        """Guild configuration commands."""
        if not self.is_guild_owner_or_admin(interaction):
            embed = create_error_embed("Permission Denied", "Only guild admins can configure settings.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if action.value == "view":
            await self.config_view(interaction)
        elif action.value == "set":
            await interaction.response.send_modal(ConfigSetModal(self.bot))
        elif action.value == "reset":
            await self.config_reset(interaction)
    
    async def config_view(self, interaction: discord.Interaction):
        """Display current guild configuration."""
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        # Collect configuration info
        embed = discord.Embed(
            title=f"{Emojis.ANNOUNCE} {interaction.guild.name} Configuration",
            color=Colors.GOLD
        )
        
        # Channels
        channels_info = []
        for channel_key, channel_name in [
            ("trial_channel", "Trial Applications"),
            ("tournament_channel", "Tournament"),
            ("event_channel", "Events"),
            ("appeals_channel", "Appeals"),
            ("log_channel", "Logs"),
        ]:
            channel_id = settings.get(channel_key)
            if channel_id:
                channel = interaction.guild.get_channel(int(channel_id))
                status = f"✓ {channel.mention if channel else f'Unknown ({channel_id})'}"
            else:
                status = f"✗ Not configured"
            channels_info.append(f"**{channel_name}**: {status}")
        
        embed.add_field(name="Channels", value="\n".join(channels_info), inline=False)
        
        # Roles
        trial_role_id = settings.get("trial_role_id")
        trial_role = interaction.guild.get_role(int(trial_role_id)) if trial_role_id else None
        embed.add_field(
            name="Trial Role",
            value=f"{'✓ ' + trial_role.mention if trial_role else '✗ Not configured'}",
            inline=True
        )
        
        # Reviewers
        trial_reviewers = settings.get("trial_reviewers", [])
        appeal_reviewers = settings.get("appeal_reviewers", [])
        tournament_admins = settings.get("tournament_admins", [])
        event_admins = settings.get("event_admins", [])
        
        reviewers_info = f"""
**Trial Reviewers**: {len(trial_reviewers)} roles
**Appeal Reviewers**: {len(appeal_reviewers)} roles
**Tournament Admins**: {len(tournament_admins)} roles
**Event Admins**: {len(event_admins)} roles
"""
        embed.add_field(name="Permissions", value=reviewers_info, inline=False)
        
        embed.set_footer(text="Use /config set to update settings")
        embed.color = Colors.GOLD
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def config_reset(self, interaction: discord.Interaction):
        """Reset configuration to defaults."""
        embed = create_error_embed(
            "Reset Not Implemented",
            "Config reset requires manual JSON editing to prevent accidental data loss."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ConfigSetModal(discord.ui.Modal, title="Configure Guild Settings"):
    """Modal for setting guild configuration."""
    
    trial_channel = discord.ui.TextInput(
        label="Trial Channel ID",
        placeholder="Channel ID for trial applications",
        required=False
    )
    tournament_channel = discord.ui.TextInput(
        label="Tournament Channel ID",
        placeholder="Channel ID for tournament announcements",
        required=False
    )
    event_channel = discord.ui.TextInput(
        label="Event Channel ID",
        placeholder="Channel ID for events",
        required=False
    )
    appeals_channel = discord.ui.TextInput(
        label="Appeals Channel ID",
        placeholder="Channel ID for appeals",
        required=False
    )
    log_channel = discord.ui.TextInput(
        label="Log Channel ID",
        placeholder="Channel ID for internal logs",
        required=False
    )
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        """Process configuration submission."""
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        # Validate and update channel IDs
        channels_updated = []
        
        for field, key in [
            (self.trial_channel, "trial_channel"),
            (self.tournament_channel, "tournament_channel"),
            (self.event_channel, "event_channel"),
            (self.appeals_channel, "appeals_channel"),
            (self.log_channel, "log_channel"),
        ]:
            if field.value.strip():
                try:
                    channel_id = int(field.value.strip())
                    channel = interaction.guild.get_channel(channel_id)
                    if not channel:
                        embed = create_error_embed(
                            "Invalid Channel",
                            f"Channel {channel_id} not found in this guild."
                        )
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                    
                    settings[key] = channel_id
                    channels_updated.append(f"✓ {key}: {channel.mention}")
                except ValueError:
                    embed = create_error_embed(
                        "Invalid Channel ID",
                        f"'{field.value}' is not a valid channel ID."
                    )
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Update config
        if "guilds" not in config.config:
            config.config["guilds"] = {}
        config.config["guilds"][str(interaction.guild.id)] = settings
        config.save()
        
        embed = create_success_embed(
            "Configuration Updated",
            "\n".join(channels_updated) if channels_updated else "No changes made."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ConfigDiagnostics(commands.Cog):
    """Configuration diagnostics and troubleshooting."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="configdiag", description="Check configuration health")
    async def config_diagnostics(self, interaction: discord.Interaction):
        """Diagnose configuration issues."""
        if not self.is_guild_owner_or_admin(interaction):
            embed = create_error_embed("Permission Denied", "Only guild admins can run diagnostics.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        issues = []
        warnings = []
        
        # Check channels
        for channel_key, channel_name in [
            ("trial_channel", "Trial"),
            ("tournament_channel", "Tournament"),
            ("event_channel", "Events"),
            ("appeals_channel", "Appeals"),
            ("log_channel", "Logs"),
        ]:
            channel_id = settings.get(channel_key)
            if not channel_id:
                issues.append(f"Missing {channel_name} channel configuration")
            else:
                channel = interaction.guild.get_channel(int(channel_id))
                if not channel:
                    issues.append(f"{channel_name} channel ({channel_id}) not found")
                elif not channel.permissions_for(interaction.guild.me).send_messages:
                    warnings.append(f"Bot lacks send permissions in {channel_name} channel")
        
        # Check trial role
        trial_role_id = settings.get("trial_role_id")
        if not trial_role_id:
            issues.append("Trial role not configured")
        else:
            trial_role = interaction.guild.get_role(int(trial_role_id))
            if not trial_role:
                issues.append(f"Trial role ({trial_role_id}) not found")
        
        # Check permissions
        trial_reviewers = settings.get("trial_reviewers", [])
        appeal_reviewers = settings.get("appeal_reviewers", [])
        tournament_admins = settings.get("tournament_admins", [])
        event_admins = settings.get("event_admins", [])
        
        if not trial_reviewers:
            warnings.append("No trial reviewers configured")
        if not appeal_reviewers:
            warnings.append("No appeal reviewers configured")
        if not tournament_admins:
            warnings.append("No tournament admins configured")
        if not event_admins:
            warnings.append("No event admins configured")
        
        # Build diagnostic embed
        embed = discord.Embed(title="Configuration Diagnostics", color=Colors.GOLD)
        
        if not issues and not warnings:
            embed.description = f"{Emojis.CHECK} All systems operational!"
            embed.color = discord.Color.green()
        else:
            if issues:
                embed.add_field(
                    name=f"{Emojis.CROSS} Issues",
                    value="\n".join([f"• {i}" for i in issues]),
                    inline=False
                )
            if warnings:
                embed.add_field(
                    name=f"{Emojis.WARN} Warnings",
                    value="\n".join([f"• {w}" for w in warnings]),
                    inline=False
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    def is_guild_owner_or_admin(self, interaction: discord.Interaction) -> bool:
        """Check if user is guild owner or has admin permissions."""
        return interaction.user.id == interaction.guild.owner_id or interaction.user.guild_permissions.administrator


async def setup(bot):
    await bot.add_cog(ConfigManager(bot))
    await bot.add_cog(ConfigDiagnostics(bot))
