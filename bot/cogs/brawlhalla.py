import asyncio
import os
import discord
import requests
from discord import app_commands
from discord.ext import commands
from bot.db import SessionLocal, UserProfile

BRAWLHALLA_API_KEY = os.getenv("BRAWLHALLA_API_KEY")
BRAWLHALLA_API_ENDPOINT = os.getenv("BRAWLHALLA_API_ENDPOINT")
BRAWLHALLA_POLL_INTERVAL = int(os.getenv("BRAWLHALLA_POLL_INTERVAL", "60"))

class BrawlhallaCog(commands.Cog):
    """Brawlhalla bindings and simple lookup. This implementation stores handles and can be extended to query the Brawlhalla API."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="bind_brawlhalla", description="Bind your Brawlhalla handle to your Discord account (opt-in storage)")
    async def bind(self, interaction: discord.Interaction, handle: str):
        session = SessionLocal()
        try:
            user = session.query(UserProfile).filter_by(discord_id=interaction.user.id, guild_id=interaction.guild_id or 0).first()
            if not user:
                user = UserProfile(discord_id=interaction.user.id, guild_id=interaction.guild_id or 0, balance=100)
                session.add(user)
            user.brawlhalla_handle = handle
            session.commit()
            await interaction.response.send_message(f"Bound Brawlhalla handle `{handle}` to your profile.")
        finally:
            session.close()

    @app_commands.command(name="brawlhalla_profile", description="Show stored Brawlhalla handle and (optionally) fetch data")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        session = SessionLocal()
        try:
            user = session.query(UserProfile).filter_by(discord_id=member.id, guild_id=interaction.guild_id or 0).first()
            if not user or not user.brawlhalla_handle:
                await interaction.response.send_message("No Brawlhalla handle found for that user.", ephemeral=True)
                return
            # If API key is available we could fetch additional info. Implementers can extend here.
            embed = discord.Embed(title=f"Brawlhalla: {user.brawlhalla_handle}")
            embed.add_field(name="Handle", value=user.brawlhalla_handle)

            if BRAWLHALLA_API_ENDPOINT and "{handle}" in BRAWLHALLA_API_ENDPOINT:
                api_url = BRAWLHALLA_API_ENDPOINT.format(handle=user.brawlhalla_handle)
                headers = {}
                if BRAWLHALLA_API_KEY:
                    headers["Authorization"] = f"Bearer {BRAWLHALLA_API_KEY}"

                try:
                    response = await asyncio.to_thread(
                        requests.get,
                        api_url,
                        headers=headers,
                        timeout=10
                    )
                    if response.ok:
                        embed.add_field(
                            name="API Data",
                            value="Fetched additional profile data from Brawlhalla",
                            inline=False
                        )
                        embed.set_footer(
                            text=f"Brawlhalla API configured — polling every {BRAWLHALLA_POLL_INTERVAL}s"
                        )
                    else:
                        embed.add_field(
                            name="API fetch failed",
                            value=f"HTTP {response.status_code}",
                            inline=False
                        )
                        embed.set_footer(
                            text="Brawlhalla endpoint configured, but request failed"
                        )
                except Exception as exc:
                    embed.add_field(name="API fetch error", value=str(exc), inline=False)
                    embed.set_footer(
                        text="Brawlhalla endpoint configured, but fetch failed"
                    )
            else:
                if BRAWLHALLA_API_KEY:
                    embed.set_footer(
                        text="Brawlhalla API key configured, but no endpoint is set"
                    )
                else:
                    embed.set_footer(
                        text="Brawlhalla API key/endpoint not configured — only stored handle is shown"
                    )

            await interaction.response.send_message(embed=embed)
        finally:
            session.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(BrawlhallaCog(bot))
