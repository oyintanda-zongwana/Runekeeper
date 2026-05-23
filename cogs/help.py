import discord
from discord import app_commands
from discord.ext import commands
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
with open(CONFIG_PATH) as f:
    config = json.load(f)

PREFIX = config["prefix"]

class Help(commands.Cog):
    FRIENDLY_CATEGORIES = {
        "HallInfo": "🏛 Hall Information",
        "Trials": "⚔️ Trials",
        "Tournaments": "🏆 Tournaments",
        "Events": "📅 Events",
        "Appeals": "📜 Appeals",
        "Logging": "📋 Logging",
        "Announcements": "📢 Announcements",
        "Moderation": "🛡 Moderation",
        "Roles": "👥 Roles",
        "Server": "🏠 Server",
        "AdminTools": "⚙️ Administration",
        "Help": "❓ Help"
    }

    def __init__(self, bot):
        self.bot = bot

    def get_prefix(self, ctx):
        return getattr(ctx, "prefix", PREFIX)

    def _base_embed(self, title: str, color: discord.Color = discord.Color.gold()) -> discord.Embed:
        embed = discord.Embed(title=title, color=color)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        return embed

    def home_embed(self, ctx_or_interaction, prefix: str = None) -> discord.Embed:
        """Main help page."""
        # Handle both Context and Interaction
        if isinstance(ctx_or_interaction, discord.Interaction):
            guild = ctx_or_interaction.guild
            user = ctx_or_interaction.user
        else:
            guild = ctx_or_interaction.guild
            user = ctx_or_interaction.author

        owner = guild.owner.mention if guild and guild.owner else "Unknown"
        member_count = guild.member_count if guild else "N/A"
        online_count = len([m for m in guild.members if m.status != discord.Status.offline]) if guild else "N/A"
        boost_level = guild.premium_tier if guild else 0
        boost_count = guild.premium_subscription_count if guild else 0
        if prefix is None:
            prefix = self.get_prefix(ctx_or_interaction) if hasattr(ctx_or_interaction, 'prefix') else PREFIX

        embed = self._base_embed("🏠 Hall of the Slain Help Center")
        if guild:
            embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)

        embed.description = (
            "Welcome to the Hall management system.\n\n"
            "⚔️ **Server Overview**\n"
            f"👑 Owner: {owner}\n"
            f"👥 Members: {member_count}\n"
            f"📡 Online: {online_count}\n"
            f"🚀 Boost Level: {boost_level} ({boost_count} boosts)\n"
            f"🛠 Prefix: `{prefix}`\n\n"
            "📖 Select a category below to browse commands."
        )

        categories = []
        for name, cog in self.bot.cogs.items():
            if name in self.FRIENDLY_CATEGORIES:
                total = len([cmd for cmd in cog.get_commands() if not cmd.hidden]) + len([cmd for cmd in cog.walk_app_commands() if not getattr(cmd, 'hidden', False) and not isinstance(cmd, app_commands.Group)])
                if total > 0:
                    friendly_name = self.FRIENDLY_CATEGORIES.get(name, name)
                    categories.append(f"• {friendly_name} — {total} commands")

        if categories:
            category_list = "\n".join(categories)
            embed.add_field(name="📁 Command Categories", value=category_list, inline=False)
        else:
            embed.add_field(name="📁 Command Categories", value="No commands found.", inline=False)

        embed.set_footer(text="Use the dropdown to navigate")
        return embed

    def _count_cog_commands(self, cog) -> int:
        prefix_commands = [cmd for cmd in cog.get_commands() if not cmd.hidden]
        app_commands_list = [cmd for cmd in cog.walk_app_commands() if not getattr(cmd, 'hidden', False) and not isinstance(cmd, app_commands.Group)]
        return len(prefix_commands) + len(app_commands_list)

    def _format_command_entry(self, cmd, prefix: str) -> str:
        if isinstance(cmd, app_commands.Command):
            if isinstance(cmd, app_commands.Group):
                return None
            syntax = f"**`/{cmd.qualified_name}`**"
            description = cmd.description or "No description provided."
            return f"{syntax}\n{description}"

        syntax = f"**`{prefix}{cmd.qualified_name} {cmd.signature}`**".strip()
        description = cmd.help or getattr(cmd, 'description', None) or "No description provided."
        return f"{syntax}\n{description}"

    def cog_embed(self, cog_name: str, prefix: str = PREFIX) -> discord.Embed:
        cog = self.bot.get_cog(cog_name)
        if not cog:
            return None

        friendly_name = self.FRIENDLY_CATEGORIES.get(cog_name, cog_name)
        embed = self._base_embed(f"📁 {friendly_name} Commands", discord.Color.blue())
        embed.set_author(name="Command Details", icon_url=self.bot.user.display_avatar.url)

        command_lines = []
        for cmd in cog.get_commands():
            if cmd.hidden:
                continue
            command_lines.append(self._format_command_entry(cmd, prefix))

        for app_cmd in cog.walk_app_commands():
            if getattr(app_cmd, 'hidden', False) or isinstance(app_cmd, app_commands.Group):
                continue
            command_lines.append(self._format_command_entry(app_cmd, prefix))

        command_lines = [line for line in command_lines if line]
        if not command_lines:
            embed.description = "No public commands in this category."
            return embed

        full = "\n\n".join(command_lines)
        if len(full) <= 1024:
            embed.add_field(name="Commands", value=full, inline=False)
        else:
            parts = []
            current = ""
            for line in command_lines:
                if len(current) + len(line) + 2 > 1024:
                    parts.append(current.strip())
                    current = line
                else:
                    if current:
                        current += "\n\n"
                    current += line
            if current:
                parts.append(current.strip())

            for i, part in enumerate(parts):
                field_name = "Commands" if i == 0 else "Commands (cont.)"
                embed.add_field(name=field_name, value=part, inline=False)

        embed.set_footer(text="Use the dropdown to go back")
        return embed

    class HelpDropdown(discord.ui.Select):
        def __init__(self, bot, parent_view, prefix):
            self.bot = bot
            self.parent_view = parent_view
            self.prefix = prefix

            options = [discord.SelectOption(label="🏠 Home", value="Home", description="Main help page")]
            for name, cog in bot.cogs.items():
                command_count = parent_view.cog._count_cog_commands(cog)
                if command_count > 0:
                    friendly_name = parent_view.cog.FRIENDLY_CATEGORIES.get(name, name)
                    options.append(discord.SelectOption(
                        label=friendly_name,
                        value=name,
                        description=f"Browse {friendly_name} commands"
                    ))
            super().__init__(placeholder="Navigate categories...", min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            value = self.values[0]
            if value == "Home":
                embed = self.parent_view.cog.home_embed(interaction, prefix=self.prefix)
            else:
                embed = self.parent_view.cog.cog_embed(value, prefix=self.prefix)
            await interaction.response.edit_message(embed=embed, view=self.parent_view)

    class HelpView(discord.ui.View):
        def __init__(self, bot, cog, prefix):
            super().__init__(timeout=180)
            self.cog = cog
            self.add_item(cog.HelpDropdown(bot, self, prefix))

    @commands.command()
    async def help(self, ctx, *, query: str = None):
        """Browse all commands or get details for a specific one."""
        prefix = getattr(ctx, "prefix", PREFIX)
        if query:
            cmd = self.bot.get_command(query.lower())
            if cmd and not cmd.hidden:
                embed = discord.Embed(
                    title=f"❓ {cmd.qualified_name}",
                    description=f"**Syntax:** `{prefix}{cmd.qualified_name} {cmd.signature}`",
                    color=discord.Color.green()
                )
                example = cmd.extras.get('example', f"`{prefix}{cmd.qualified_name}`")
                embed.add_field(name="Example", value=example, inline=False)
                await ctx.send(embed=embed)
                return
            await ctx.send(f"<:wrong:1501538221530808464> Command not found. Use `{prefix}help` to browse all commands.")
            return

        embed = self.home_embed(ctx, prefix=prefix)
        view = self.HelpView(self.bot, self, prefix)
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="help", description="Browse all Runekeeper commands")
    async def help_slash(self, interaction: discord.Interaction):
        """Browse all commands via slash command."""
        prefix = PREFIX
        embed = self.home_embed(interaction, prefix=prefix)
        view = self.HelpView(self.bot, self, prefix)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
