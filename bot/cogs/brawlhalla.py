import asyncio
import os
import requests
import discord
import requests
from discord import app_commands
from discord.ext import commands
from bot.db import SessionLocal, UserProfile

BRAWLHALLA_API_KEY = os.getenv("BRAWLHALLA_API_KEY")
<<<<<<< HEAD
BRAWLHALLA_API_ENDPOINT = os.getenv("BRAWLHALLA_API_ENDPOINT")
BRAWLHALLA_POLL_INTERVAL = int(os.getenv("BRAWLHALLA_POLL_INTERVAL", "60"))
=======
# Optional: a full URL template that must include '{handle}' and may include '{key}' if needed.
# Example: https://corehalla.example.com/api/player?name={handle}&api_key={key}
BRAWLHALLA_API_ENDPOINT = os.getenv("BRAWLHALLA_API_ENDPOINT")


def _fetch_player_data(handle: str):
    """Fetch player data from configured endpoint. Returns JSON or raises requests.RequestException.
    The endpoint template must contain '{handle}' and may contain '{key}'."""
    if not BRAWLHALLA_API_ENDPOINT:
        raise RuntimeError("No BRAWLHALLA_API_ENDPOINT configured; set the environment variable to an endpoint template.")
    # format endpoint
    try:
        url = BRAWLHALLA_API_ENDPOINT.format(handle=handle, key=BRAWLHALLA_API_KEY or "")
    except Exception:
        # If formatting fails, fallback to simple replacement
        url = BRAWLHALLA_API_ENDPOINT.replace("{handle}", handle).replace("{key}", BRAWLHALLA_API_KEY or "")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

>>>>>>> 1e118554b3af41dc36fae600d0cc7d0f6d50274b

class BrawlhallaCog(commands.Cog):
    """Brawlhalla integration. Stores handles and (optionally) queries a configured CoreHalla/Brawlhalla endpoint.

    Notes:
    - Set BRAWLHALLA_API_ENDPOINT to a URL template that contains '{handle}' and optionally '{key}'.
    - If you prefer to use the official Brawlhalla API or a third-party service, point the endpoint to that service.
    - Examples:
      - CoreHalla: https://corehalla.example.com/api/player?name={handle}&api_key={key}
      - Brawlhalla (if you have a wrapper): https://api.example.com/bh/player/{handle}?key={key}
    """

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

    @app_commands.command(name="brawlhalla_stats", description="Show Brawlhalla stats for a player (1v1, 2v2 elo etc.)")
    @app_commands.describe(member_or_handle="Discord member or Brawlhalla handle (optional)")
    async def stats(self, interaction: discord.Interaction, member_or_handle: str = None):
        # Determine handle: if a mention/member ID was passed, try to resolve; otherwise treat as handle string
        handle = None
        session = SessionLocal()
        try:
<<<<<<< HEAD
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
=======
            # Try to resolve as member in the guild
            if member_or_handle:
                # If it looks like a mention <@!id> or an int id, try member lookup
                if interaction.guild and (member_or_handle.startswith("<@") or member_or_handle.isdigit()):
                    # strip mention chars
                    _id = ''.join(c for c in member_or_handle if c.isdigit())
                    try:
                        member = await interaction.guild.fetch_member(int(_id))
                    except Exception:
                        member = None
                    if member:
                        user = session.query(UserProfile).filter_by(discord_id=member.id, guild_id=interaction.guild_id or 0).first()
                        if user and user.brawlhalla_handle:
                            handle = user.brawlhalla_handle
                # If not a mention or no stored handle, treat as handle string
                if not handle:
                    handle = member_or_handle
            else:
                # no arg: use the invoking user's stored handle
                user = session.query(UserProfile).filter_by(discord_id=interaction.user.id, guild_id=interaction.guild_id or 0).first()
                if user and user.brawlhalla_handle:
                    handle = user.brawlhalla_handle

            if not handle:
                await interaction.response.send_message("No Brawlhalla handle found. Provide a handle or bind one with `/bind_brawlhalla <handle>`.", ephemeral=True)
                return

            # If no endpoint configured, just show stored handle
            if not BRAWLHALLA_API_ENDPOINT:
                await interaction.response.send_message(f"Stored handle: `{handle}`. To fetch live stats, configure BRAWLHALLA_API_ENDPOINT and BRAWLHALLA_API_KEY.")
                return

            await interaction.response.defer()
            try:
                data = _fetch_player_data(handle)
            except Exception as e:
                await interaction.followup.send(f"Failed to fetch data for `{handle}`: {e}")
                return

            # Try to extract common rating fields from returned JSON
            # This attempts multiple common key names so it works with different wrappers/APIs.
            one_v_one = None
            two_v_two = None
            name = handle
            extra_lines = []

            # Flatten keys and search
            def _dig_for_rating(d):
                if not isinstance(d, dict):
                    return None
                # common patterns
                if 'rating' in d and isinstance(d['rating'], (int, float)):
                    return d['rating']
                if 'rating' in d and isinstance(d['rating'], dict):
                    # maybe rating['1v1'] etc
                    r = d['rating']
                    for k in ['1v1', '1v1_elo', '1v1Elo', '1v1_rating']:
                        if k in r:
                            return r[k]
                # top-level keys
                for k in ['1v1', '1v1_elo', '1v1Elo', 'rating_1v1', 'solo_rating']:
                    if k in d:
                        return d[k]
                return None

            # Attempt structured access
            if isinstance(data, dict):
                # name
                for nk in ['name', 'handle', 'username']:
                    if nk in data:
                        name = data.get(nk)
                        break
                # common locations
                for path in ['ratings', 'rating', 'elo', 'stats']:
                    candidate = data.get(path)
                    if candidate:
                        if isinstance(candidate, dict):
                            # try to find 1v1 and 2v2
                            for k in ['1v1', '1v1_rating', 'solo_rating', 'rating']:
                                if k in candidate:
                                    one_v_one = candidate.get(k)
                            for k in ['2v2', '2v2_rating', 'team_rating']:
                                if k in candidate:
                                    two_v_two = candidate.get(k)
                # top-level keys
                if one_v_one is None:
                    one_v_one = _dig_for_rating(data)
                if two_v_two is None:
                    # look for 2v2 keys
                    for k in ['2v2', '2v2_elo', '2v2Elo', 'team_rating']:
                        if k in data:
                            two_v_two = data.get(k)
                # other useful info
                for k in ['wins', 'losses', 'rating', 'rank']:
                    if k in data:
                        extra_lines.append(f"{k.title()}: {data.get(k)}")

            # If still None, attempt to parse lists
            if one_v_one is None and isinstance(data, list) and len(data) > 0:
                # try first element
                elem = data[0]
                if isinstance(elem, dict):
                    one_v_one = _dig_for_rating(elem)
                    for k in ['wins', 'losses']:
                        if k in elem:
                            extra_lines.append(f"{k.title()}: {elem.get(k)}")

            # Build embed
            embed = discord.Embed(title=f"Brawlhalla — {name}", color=discord.Color.blue())
            if one_v_one is not None:
                embed.add_field(name="1v1 ELO", value=str(one_v_one), inline=True)
            else:
                embed.add_field(name="1v1 ELO", value="N/A", inline=True)
            if two_v_two is not None:
                embed.add_field(name="2v2 ELO", value=str(two_v_two), inline=True)
            else:
                embed.add_field(name="2v2 ELO", value="N/A", inline=True)
            if extra_lines:
                embed.add_field(name="Extra", value="\n".join(extra_lines), inline=False)

            await interaction.followup.send(embed=embed)
        finally:
            session.close()

    @app_commands.command(name="brawlhalla_queue", description="(If supported) Show whether the player is currently in an active queue or match")
    @app_commands.describe(member_or_handle="Discord member or Brawlhalla handle (optional)")
    async def queue(self, interaction: discord.Interaction, member_or_handle: str = None):
        # Determine handle similar to stats command
        handle = None
        session = SessionLocal()
        try:
            if member_or_handle:
                if interaction.guild and (member_or_handle.startswith("<@") or member_or_handle.isdigit()):
                    _id = ''.join(c for c in member_or_handle if c.isdigit())
                    try:
                        member = await interaction.guild.fetch_member(int(_id))
                    except Exception:
                        member = None
                    if member:
                        user = session.query(UserProfile).filter_by(discord_id=member.id, guild_id=interaction.guild_id or 0).first()
                        if user and user.brawlhalla_handle:
                            handle = user.brawlhalla_handle
                if not handle:
                    handle = member_or_handle
            else:
                user = session.query(UserProfile).filter_by(discord_id=interaction.user.id, guild_id=interaction.guild_id or 0).first()
                if user and user.brawlhalla_handle:
                    handle = user.brawlhalla_handle

            if not handle:
                await interaction.response.send_message("No Brawlhalla handle found. Provide a handle or bind one with `/bind_brawlhalla <handle>`.", ephemeral=True)
                return

            if not BRAWLHALLA_API_ENDPOINT:
                await interaction.response.send_message(f"Stored handle: `{handle}`. To fetch live queue info, configure BRAWLHALLA_API_ENDPOINT and BRAWLHALLA_API_KEY.")
                return

            await interaction.response.defer()
            try:
                data = _fetch_player_data(handle)
            except Exception as e:
                await interaction.followup.send(f"Failed to fetch data for `{handle}`: {e}")
                return

            # Look for queue or active match fields commonly provided by wrappers
            active = None
            queue_info = []
            if isinstance(data, dict):
                for k in ['in_queue', 'is_in_queue', 'queued', 'inMatch', 'in_match', 'active_match', 'active']:
                    if k in data:
                        active = data.get(k)
                # sometimes there is an 'queues' or 'active_queues' list
                for k in ['queues', 'active_queues', 'activeQueues']:
                    if k in data and isinstance(data[k], (list, dict)):
                        queue_info.append(str(data[k]))
                # some APIs provide 'queue' object
                if 'queue' in data:
                    queue_info.append(str(data['queue']))
            if isinstance(data, list) and len(data) > 0:
                elem = data[0]
                if isinstance(elem, dict):
                    for k in ['in_queue', 'queued', 'inMatch']:
                        if k in elem:
                            active = elem.get(k)

            # Build response
            if active is None and not queue_info:
                await interaction.followup.send(f"No active queue/match information available for `{handle}` from the configured endpoint.")
                return

            desc = f"Handle: `{handle}`\n"
            desc += f"Active: {active}\n" if active is not None else ""
            if queue_info:
                desc += "Queues: \n" + "\n".join(queue_info)

            embed = discord.Embed(title=f"Brawlhalla Queue — {handle}", description=desc, color=discord.Color.orange())
            await interaction.followup.send(embed=embed)
>>>>>>> 1e118554b3af41dc36fae600d0cc7d0f6d50274b
        finally:
            session.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(BrawlhallaCog(bot))
