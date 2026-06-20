import random
import discord
from discord import app_commands
from discord.ext import commands
from bot.db import SessionLocal, UserProfile

class LevelsCog(commands.Cog):
    """Basic XP/leveling system. XP awarded per message."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bots
        if message.author.bot or not message.guild:
            return
        session = SessionLocal()
        try:
            user = session.query(UserProfile).filter_by(discord_id=message.author.id, guild_id=message.guild.id).first()
            if not user:
                user = UserProfile(discord_id=message.author.id, guild_id=message.guild.id, balance=100)
                session.add(user)
                session.commit()
                session.refresh(user)
            gained = random.randint(5, 15)
            user.xp += gained
            leveled = False
            # simple level formula: level = xp // 100
            new_level = user.xp // 100
            if new_level > user.level:
                user.level = new_level
                leveled = True
            session.commit()
            if leveled:
                try:
                    await message.channel.send(f"Congratulations {message.author.mention}, you reached level {user.level}!")
                except Exception:
                    pass
        finally:
            session.close()

    @app_commands.command(name="profile", description="Show your level/profile")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        session = SessionLocal()
        try:
            user = session.query(UserProfile).filter_by(discord_id=member.id, guild_id=interaction.guild_id or 0).first()
            if not user:
                await interaction.response.send_message("No profile found.", ephemeral=True)
                return
            embed = discord.Embed(title=f"{member.display_name}'s Profile", color=discord.Color.gold())
            embed.add_field(name="Level", value=str(user.level))
            embed.add_field(name="XP", value=str(user.xp))
            embed.add_field(name="Balance", value=str(user.balance))
            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(LevelsCog(bot))
