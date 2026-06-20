import random
import discord
from discord import app_commands
from discord.ext import commands
from bot.db import SessionLocal, UserProfile

class EconomyCog(commands.Cog):
    """Simple economy with per-guild balances, daily reward, and transfer."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _get_or_create(self, session, discord_id: int, guild_id: int):
        user = session.query(UserProfile).filter_by(discord_id=discord_id, guild_id=guild_id).first()
        if not user:
            user = UserProfile(discord_id=discord_id, guild_id=guild_id, balance=100)
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            user = self._get_or_create(session, interaction.user.id, interaction.guild_id or 0)
            await interaction.response.send_message(f"{interaction.user.mention}, your balance is {user.balance} Hall Coins.")
        finally:
            session.close()

    @app_commands.command(name="daily", description="Claim daily reward")
    async def daily(self, interaction: discord.Interaction):
        session = SessionLocal()
        try:
            user = self._get_or_create(session, interaction.user.id, interaction.guild_id or 0)
            reward = random.randint(50, 150)
            user.balance += reward
            session.commit()
            await interaction.response.send_message(f"{interaction.user.mention} claimed daily reward of {reward} Hall Coins! New balance: {user.balance}")
        finally:
            session.close()

    @app_commands.guild_only()
    @app_commands.command(name="transfer", description="Transfer Hall Coins to another member")
    @app_commands.describe(member="Member to send coins to", amount="Amount of coins to send")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Amount must be positive.", ephemeral=True)
            return
        session = SessionLocal()
        try:
            sender = self._get_or_create(session, interaction.user.id, interaction.guild_id)
            if sender.balance < amount:
                await interaction.response.send_message("Insufficient funds.", ephemeral=True)
                return
            recipient = self._get_or_create(session, member.id, interaction.guild_id)
            sender.balance -= amount
            recipient.balance += amount
            session.commit()
            await interaction.response.send_message(f"{interaction.user.mention} sent {amount} Hall Coins to {member.mention}.")
        finally:
            session.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
