"""
Admin Quality of Life Tools
Diagnostic utilities and configuration checkers for guild admins.
"""
import discord
from discord.ext import commands
from discord import app_commands
from config import get_config
from utils.themes import create_success_embed, create_error_embed, create_info_embed, Colors, Emojis


class AdminTools(commands.Cog):
    """Admin utilities and diagnostics."""
    
    def __init__(self, bot):
        self.bot = bot
    
    def is_guild_admin(self, interaction: discord.Interaction) -> bool:
        """Check if user is guild owner or admin."""
        return interaction.user.id == interaction.guild.owner_id or interaction.user.guild_permissions.administrator
    
    @app_commands.command(name="checkpermissions", description="Check bot permissions in channels")
    async def check_permissions(self, interaction: discord.Interaction):
        """Verify bot has required permissions in configured channels."""
        if not self.is_guild_admin(interaction):
            embed = create_error_embed("Permission Denied", Emojis.WARN + " Only admins can run this command.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        guild = interaction.guild
        bot_member = guild.me
        
        issues = []
        warnings = []
        
        # Check each configured channel
        channels_to_check = [
            ("trial_channel", "Trial Applications"),
            ("tournament_channel", "Tournament"),
            ("event_channel", "Events"),
            ("appeals_channel", "Appeals"),
            ("log_channel", "Logs"),
        ]
        
        for channel_key, channel_name in channels_to_check:
            channel_id = settings.get(channel_key)
            if not channel_id:
                warnings.append(f"No {channel_name} channel configured")
                continue
            
            channel = guild.get_channel(int(channel_id))
            if not channel:
                issues.append(f"{channel_name} channel {channel_id} not found")
                continue
            
            perms = channel.permissions_for(bot_member)
            if not perms.send_messages:
                issues.append(f"Bot cannot send messages in {channel_name} ({channel.mention})")
            if not perms.embed_links:
                warnings.append(f"Bot cannot embed links in {channel_name}")
            if not perms.manage_webhooks:
                warnings.append(f"Bot cannot manage webhooks in {channel_name}")
        
        # Build response
        embed = discord.Embed(
            title=f"{Emojis.GEAR} Permission Check",
            color=Colors.GOLD
        )
        
        if not issues and not warnings:
            embed.description = f"{Emojis.CHECK} **All systems operational!**"
            embed.color = discord.Color.green()
        else:
            if issues:
                embed.add_field(
                    name=f"{Emojis.CROSS} Critical Issues",
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
    
    @app_commands.command(name="checkroles", description="Check role hierarchy issues")
    async def check_roles(self, interaction: discord.Interaction):
        """Check if bot can manage configured roles."""
        if not self.is_guild_admin(interaction):
            embed = create_error_embed("Permission Denied", Emojis.WARN + " Only admins can run this command.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        guild = interaction.guild
        bot_member = guild.me
        
        issues = []
        
        # Check trial role
        trial_role_id = settings.get("trial_role_id")
        if trial_role_id:
            trial_role = guild.get_role(int(trial_role_id))
            if not trial_role:
                issues.append(f"Trial role {trial_role_id} not found")
            elif trial_role > bot_member.top_role:
                issues.append(f"Bot cannot manage Trial role (hierarchy issue)")
        
        # Check reviewer roles
        for role_name, role_ids in [
            ("Trial Reviewers", settings.get("trial_reviewers", [])),
            ("Appeal Reviewers", settings.get("appeal_reviewers", [])),
            ("Tournament Admins", settings.get("tournament_admins", [])),
            ("Event Admins", settings.get("event_admins", [])),
        ]:
            for role_id in role_ids:
                role = guild.get_role(int(role_id))
                if not role:
                    issues.append(f"{role_name} role {role_id} not found")
        
        embed = discord.Embed(
            title=f"{Emojis.CROWN} Role Check",
            color=Colors.GOLD
        )
        
        if not issues:
            embed.description = f"{Emojis.CHECK} **All roles are properly configured!**"
            embed.color = discord.Color.green()
        else:
            embed.add_field(
                name=f"{Emojis.CROSS} Issues",
                value="\n".join([f"• {i}" for i in issues]),
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="checkchanners", description="Verify all required channels exist")
    async def check_channels(self, interaction: discord.Interaction):
        """Verify required channels are configured and exist."""
        if not self.is_guild_admin(interaction):
            embed = create_error_embed("Permission Denied", Emojis.WARN + " Only admins can run this command.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"{Emojis.ANNOUNCE} Channel Check",
            color=Colors.GOLD
        )
        
        channels_info = []
        for channel_key, channel_name in [
            ("trial_channel", "Trial Applications"),
            ("tournament_channel", "Tournament"),
            ("event_channel", "Events"),
            ("appeals_channel", "Appeals"),
            ("log_channel", "Logs"),
        ]:
            channel_id = settings.get(channel_key)
            if not channel_id:
                channels_info.append(f"❌ {channel_name} - Not configured")
                continue
            
            channel = guild.get_channel(int(channel_id))
            if channel:
                channels_info.append(f"✅ {channel_name} - {channel.mention}")
            else:
                channels_info.append(f"❌ {channel_name} - ID {channel_id} not found")
        
        embed.description = "\n".join(channels_info)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="adminstatus", description="View complete admin dashboard")
    async def admin_status(self, interaction: discord.Interaction):
        """Display comprehensive admin status dashboard."""
        if not self.is_guild_admin(interaction):
            embed = create_error_embed("Permission Denied", Emojis.WARN + " Only admins can run this command.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"{Emojis.GEAR} {guild.name} - Admin Dashboard",
            color=Colors.GOLD
        )
        
        # Channels
        channels_text = ""
        for channel_key, channel_name in [
            ("trial_channel", "Trial"),
            ("tournament_channel", "Tournament"),
            ("event_channel", "Events"),
            ("appeals_channel", "Appeals"),
            ("log_channel", "Logs"),
        ]:
            channel_id = settings.get(channel_key)
            if channel_id:
                channel = guild.get_channel(int(channel_id))
                status = f"✅ {channel.mention}" if channel else f"❌ (ID {channel_id})"
            else:
                status = "⚠️ Not configured"
            channels_text += f"**{channel_name}**: {status}\n"
        
        embed.add_field(name="Channels", value=channels_text, inline=False)
        
        # Permissions
        trial_reviewers = len(settings.get("trial_reviewers", []))
        appeal_reviewers = len(settings.get("appeal_reviewers", []))
        tournament_admins = len(settings.get("tournament_admins", []))
        event_admins = len(settings.get("event_admins", []))
        
        perms_text = f"""
**Trial Reviewers**: {trial_reviewers} roles
**Appeal Reviewers**: {appeal_reviewers} roles
**Tournament Admins**: {tournament_admins} roles
**Event Admins**: {event_admins} roles
"""
        embed.add_field(name="Permissions", value=perms_text, inline=False)
        
        # Trial Role
        trial_role_id = settings.get("trial_role_id")
        trial_role = guild.get_role(int(trial_role_id)) if trial_role_id else None
        trial_role_text = f"✅ {trial_role.mention}" if trial_role else "⚠️ Not configured"
        embed.add_field(name="Trial Role", value=trial_role_text, inline=True)
        
        embed.set_footer(text="Use /config view for detailed settings")
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AdminTools(bot))
