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

class HallInfoSelect(discord.ui.Select):
    def __init__(self, cog, interaction):
        self.cog = cog
        self.original_interaction = interaction
        options = [
            discord.SelectOption(label="📜 Rules", value="rules", description="View the rules of the Hall"),
            discord.SelectOption(label="🏛 Hall Lore", value="lore", description="View the lore of the Hall"),
            discord.SelectOption(label="👥 Roles Guide", value="roles", description="View Hall positions and roles"),
            discord.SelectOption(label="📈 Boost Information", value="boost", description="View server boost details"),
            discord.SelectOption(label="🏠 Server Information", value="server", description="View detailed server stats"),
        ]
        super().__init__(placeholder="Choose a section to view...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        section = self.values[0]
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        if not settings:
            embed = discord.Embed(
                title="❌ Guild Not Configured",
                description="This guild has not been configured for Runekeeper.",
                color=Colors.WARNING
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)
        
        hall_info = settings.get("hall_info", {})
        
        if section == "rules":
            rules = hall_info.get("rules", "No rules configured.")
            embed = create_info_embed(
                "📜 Rules of the Hall",
                rules,
                color=Colors.GOLD
            )
        elif section == "lore":
            lore = hall_info.get("lore", "No lore configured.")
            embed = create_info_embed(
                "🏛 Hall Lore",
                lore,
                color=Colors.RUNE
            )
        elif section == "roles":
            guild_roles = settings.get("guild_roles", {})
            if guild_roles:
                role_text = "\n".join([f"{Emojis.CROWN} **{name}** - <@&{role_id}>" 
                                       for name, role_id in guild_roles.items()])
            else:
                role_text = "No roles configured."
            
            embed = create_info_embed(
                "👥 Roles Guide",
                role_text,
                color=Colors.BLOOD
            )
        elif section == "boost":
            guild = interaction.guild
            boost_level = guild.premium_tier
            boost_count = guild.premium_subscription_count
            # Boost progress: next level requires more boosts
            next_level_boosts = {0: 2, 1: 7, 2: 14}.get(boost_level, "Max")
            if isinstance(next_level_boosts, int):
                remaining = next_level_boosts - boost_count
                progress = f"{remaining} boosts until next level"
            else:
                progress = "Maximum boost level reached"
            
            boost_text = (
                f"🚀 **Boost Level:** {boost_level}\n"
                f"📊 **Boost Count:** {boost_count}\n"
                f"⏭️ **Progress:** {progress}\n\n"
                "**Boost Perks:**\n"
                "• Level 1: 50 emoji slots, 128kb upload, custom invite background\n"
                "• Level 2: 100 emoji slots, 256kb upload, 50mb screen share, custom banner\n"
                "• Level 3: 150 emoji slots, 512kb upload, 100mb screen share, vanity URL"
            )
            embed = create_info_embed(
                "📈 Boost Information",
                boost_text,
                color=Colors.TRIUMPH
            )
        elif section == "server":
            guild = interaction.guild
            owner = guild.owner.mention if guild.owner else "Unknown"
            created = discord.utils.format_dt(guild.created_at, style="F")
            total_members = guild.member_count
            humans = sum(1 for m in guild.members if not m.bot)
            bots = total_members - humans
            online = len([m for m in guild.members if m.status != discord.Status.offline])
            boost_level = guild.premium_tier
            boost_count = guild.premium_subscription_count
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)
            roles_count = len(guild.roles)
            emojis_count = len(guild.emojis)
            stickers_count = len(guild.stickers)
            verification_level = str(guild.verification_level).replace('_', ' ').title()
            afk_channel = guild.afk_channel.mention if guild.afk_channel else "None"
            system_channel = guild.system_channel.mention if guild.system_channel else "None"
            
            server_text = (
                f"👑 **Ownership**\n"
                f"Owner: {owner}\n"
                f"Created: {created}\n\n"
                f"👥 **Community**\n"
                f"Total Members: {total_members}\n"
                f"Humans: {humans}\n"
                f"Bots: {bots}\n"
                f"Currently Online: {online}\n\n"
                f"🚀 **Boost Status**\n"
                f"Boost Level: {boost_level}\n"
                f"Boost Count: {boost_count}\n\n"
                f"💬 **Activity**\n"
                f"Text Channels: {text_channels}\n"
                f"Voice Channels: {voice_channels}\n"
                f"Categories: {categories}\n\n"
                f"🛡 **Guild Stats**\n"
                f"Roles: {roles_count}\n"
                f"Emojis: {emojis_count}\n"
                f"Stickers: {stickers_count}\n"
                f"Verification Level: {verification_level}\n"
                f"AFK Channel: {afk_channel}\n"
                f"System Channel: {system_channel}"
            )
            embed = create_info_embed(
                "🏠 Server Information",
                server_text,
                color=Colors.INFO
            )
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class HallInfoView(discord.ui.View):
    def __init__(self, cog, interaction):
        super().__init__(timeout=300)
        self.add_item(HallInfoSelect(cog, interaction))

class HallInfo(commands.Cog):
    """Hall of the Slain information commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="hallinfo", description="View Hall of the Slain information")
    async def hallinfo(self, interaction: discord.Interaction):
        """Display Hall information with dropdown selection."""
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        if not settings:
            embed = discord.Embed(
                title="❌ Guild Not Configured",
                description="This guild has not been configured for Runekeeper.",
                color=Colors.WARNING
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        embed = create_info_embed(
            "🏛 Hall of the Slain Information",
            "Select a section from the dropdown below to view detailed information about the Hall.",
            color=Colors.GOLD
        )
        
        view = HallInfoView(self, interaction)
        await interaction.response.send_message(embed=embed, view=view)
    
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
