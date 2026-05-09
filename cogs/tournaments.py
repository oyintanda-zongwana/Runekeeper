"""
Tournament System
The most important system for Hall of the Slain.
Manages tournament creation, team registration, matches, brackets, and results.
"""
import discord
from discord.ext import commands
from discord import app_commands
import json
import time
from config import get_config
from utils import db
from utils.themes import (
    create_tournament_embed, create_success_embed, create_error_embed,
    Colors, Lore, Emojis
)
from utils.decorators import require_tournament_admin

async def tournament_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Autocomplete for tournament selection."""
    tournaments = db.get_guild_tournaments(interaction.guild.id)
    choices = []
    for t in tournaments:
        name = t[1]
        if current.lower() in name.lower():
            choices.append(app_commands.Choice(name=f"{name} ({t[4]})", value=name))
    return choices[:25]  # Discord limit

class Tournaments(commands.Cog):
    """Tournament management for Hall of the Slain."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="tourneycreate", description="Create a new tournament")
    @app_commands.describe(
        name="Tournament name",
        format="Tournament format (1v1 or 2v2)"
    )
    async def create(
        self,
        interaction: discord.Interaction,
        name: str,
        format: str
    ):
        """Create a new tournament."""
        config = get_config()
        admin_roles = config.get_tournament_admins(interaction.guild.id)
        has_perm = any(role.id in admin_roles for role in interaction.user.roles)
        
        if not has_perm:
            embed = create_error_embed("Permission Denied", "You don't have permission to create tournaments.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if format not in ["1v1", "2v2"]:
            embed = create_error_embed("Invalid Format", "Format must be '1v1' or '2v2'.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        tournament_id = db.create_tournament(
            guild_id=interaction.guild.id,
            name=name,
            format_type=format,
            created_by=interaction.user.id
        )
        
        db.log_action(interaction.guild.id, "tournament_created", interaction.user.id, None, f"Tournament '{name}' ({format}) created")
        
        embed = create_tournament_embed(
            "Tournament Created",
            name,
            f"{Lore.tournament_created(name)}\n\n**Format**: {format}",
            fields=[
                ("Status", "Registration Open", True),
                ("Created by", interaction.user.mention, True)
            ]
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="tourneyjoin", description="Join a tournament with a team")
    @app_commands.describe(
        tournament_name="Select tournament to join",
        team_name="Your team name",
        teammate="Your teammate for 2v2 tournaments"
    )
    @app_commands.autocomplete(tournament_name=tournament_autocomplete)
    async def join(
        self,
        interaction: discord.Interaction,
        tournament_name: str,
        team_name: str,
        teammate: discord.Member = None
    ):
        """Register a team for a tournament."""
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)

        if not settings:
            embed = create_error_embed("Guild Not Configured", "This guild hasn't set up tournaments.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Find tournament by name
        tournaments = db.get_guild_tournaments(interaction.guild.id, "registration")
        tournament = None
        for t in tournaments:
            if t[1].lower() == tournament_name.lower() or t[0] == tournament_name:
                tournament = t
                break
        
        if not tournament:
            embed = create_error_embed("Tournament Not Found", f"No registration-open tournament found with name '{tournament_name}'.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        tournament_id = tournament[0]

        if tournament[4] != "registration":
            embed = create_error_embed("Registration Closed", "This tournament is no longer accepting registrations.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        team_members = [interaction.user.id]
        if tournament[2] == "2v2":
            if teammate is None:
                embed = create_error_embed("Missing Teammate", "2v2 tournaments require a teammate. Please specify a teammate.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if teammate.id == interaction.user.id:
                embed = create_error_embed("Invalid Teammate", "You cannot add yourself as your own teammate.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            team_members.append(teammate.id)
        else:
            if teammate is not None:
                embed = create_error_embed("Invalid Format", "1v1 tournaments do not support teammates.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)

        existing_teams = db.get_tournament_teams(interaction.guild.id, tournament_id)
        for team in existing_teams:
            members = json.loads(team[4])
            if interaction.user.id in members:
                embed = create_error_embed("Already Registered", "You are already registered in this tournament.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if teammate and teammate.id in members:
                embed = create_error_embed("Teammate Already Registered", "Your teammate is already registered in another team.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)

        team_id = db.register_tournament_team(
            guild_id=interaction.guild.id,
            tournament_id=tournament_id,
            team_name=team_name,
            members=team_members
        )

        member_str = " + ".join([f"<@{m}>" for m in team_members])
        embed = create_tournament_embed(
            "Team Registered",
            tournament[1],
            f"**Team**: {team_name}\n**Members**: {member_str}",
            fields=[("Status", "Registered", True), ("Team ID", team_id, True)]
        )

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="tourneystart", description="Start a tournament")
    @app_commands.describe(tournament_name="Select tournament to start")
    @app_commands.autocomplete(tournament_name=tournament_autocomplete)
    async def start(
        self,
        interaction: discord.Interaction,
        tournament_name: str
    ):
        """Start a tournament and begin matches."""
        config = get_config()
        admin_roles = config.get_tournament_admins(interaction.guild.id)
        has_perm = any(role.id in admin_roles for role in interaction.user.roles)
        
        if not has_perm:
            embed = create_error_embed("Permission Denied", "You don't have permission to start tournaments.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Find tournament by name
        tournaments = db.get_guild_tournaments(interaction.guild.id, "registration")
        tournament = None
        for t in tournaments:
            if t[1].lower() == tournament_name.lower() or t[0] == tournament_name:
                tournament = t
                break
        
        if not tournament:
            embed = create_error_embed("Tournament Not Found", f"No registration-open tournament found with name '{tournament_name}'.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        tournament_id = tournament[0]
        if tournament[4] != "registration":
            embed = create_error_embed("Tournament Cannot Start", "This tournament is not in registration state.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        teams = db.get_tournament_teams(interaction.guild.id, tournament_id)
        if len(teams) < 2:
            embed = create_error_embed("Not Enough Teams", "At least two teams are required to start the tournament.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        db.start_tournament(interaction.guild.id, tournament_id)

        embed = create_tournament_embed(
            "Tournament Started",
            tournament[1],
            f"{Lore.tournament_started(tournament[1])}\n\n**Format**: {tournament[2]}",
            fields=[("Status", "Active", True), ("Registered Teams", str(len(teams)), True)]
        )

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="tourneyresult", description="Report a match result")
    @app_commands.describe(
        tournament_id="Tournament ID",
        winner_team="Winning team ID",
        loser_team="Losing team ID",
        round_num="Round number"
    )
    async def result(
        self,
        interaction: discord.Interaction,
        tournament_id: str,
        winner_team: str,
        loser_team: str,
        round_num: int = 1
    ):
        """Report tournament match results."""
        config = get_config()
        admin_roles = config.get_tournament_admins(interaction.guild.id)
        has_perm = any(role.id in admin_roles for role in interaction.user.roles)

        if not has_perm:
            embed = create_error_embed("Permission Denied", "You don't have permission to report results.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        tournament = db.get_tournament(interaction.guild.id, tournament_id)
        if not tournament:
            embed = create_error_embed("Tournament Not Found", "This tournament doesn't exist.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if tournament[4] != "active":
            embed = create_error_embed("Tournament Not Active", "This tournament is not currently active.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        winner = db.get_tournament_team(interaction.guild.id, tournament_id, winner_team)
        loser = db.get_tournament_team(interaction.guild.id, tournament_id, loser_team)
        if not winner or not loser:
            embed = create_error_embed("Team Not Found", "One or both team IDs do not exist.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        match_id = db.record_tournament_match(
            guild_id=interaction.guild.id,
            tournament_id=tournament_id,
            winning_team_id=winner_team,
            losing_team_id=loser_team,
            round_num=round_num
        )

        winner_mentions = " + ".join([f"<@{m}>" for m in json.loads(winner[4])])
        embed = create_success_embed(
            "Match Recorded",
            f"**Winners**: {winner_mentions}\n**Tournament**: {tournament[1]}\n**Round**: {round_num}\n**Match ID**: {match_id}"
        )

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="tourneyleaderboard", description="View tournament leaderboard")
    @app_commands.describe(tournament_id="Tournament ID")
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        tournament_id: str
    ):
        """Display tournament leaderboard."""
        tournament = db.get_tournament(interaction.guild.id, tournament_id)
        if not tournament:
            embed = create_error_embed("Tournament Not Found", "This tournament doesn't exist.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        teams = db.get_tournament_teams(interaction.guild.id, tournament_id)
        if not teams:
            embed = create_error_embed("No Teams", "No teams have registered for this tournament.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Get win counts for each team
        leaderboard_text = ""
        for i, team in enumerate(teams[:10], 1):
            matches = db.get_tournament_team_matches(interaction.guild.id, tournament_id, team[0])
            wins = len([m for m in matches if m[5] == team[0]])  # m[5] is winner_id
            leaderboard_text += f"{i}. **{team[2]}** - {wins} wins\n"
        
        embed = create_tournament_embed(
            "Leaderboard",
            tournament[1],
            leaderboard_text or "No matches yet.",
            fields=[("Status", tournament[4].upper(), True)]
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tourneys", description="Browse active tournaments")
    @app_commands.describe(status="Filter by status (registration, active, completed, or all)")
    async def browse_tournaments(
        self,
        interaction: discord.Interaction,
        status: str = "all"
    ):
        """Browse tournaments."""
        if status == "all":
            tournaments = db.get_guild_tournaments(interaction.guild.id)
        else:
            tournaments = db.get_guild_tournaments(interaction.guild.id, status)
        
        if not tournaments:
            embed = create_error_embed(
                "No Tournaments",
                f"No {status} tournaments found."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        tournaments_text = "\n".join([
            f"{Emojis.TROPHY} **{t[1]}** ({t[3]}) - {t[4].upper()}"
            for t in tournaments[:10]  # Show first 10
        ])
        
        embed = create_tournament_embed(
            f"Tournaments ({status.upper()})",
            tournaments_text,
            color=Colors.GOLD
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tourneylist", description="List tournaments with details")
    @app_commands.describe(status="Filter by status (registration, active, completed, or all)")
    async def list_tournaments(
        self,
        interaction: discord.Interaction,
        status: str = "registration"
    ):
        """List tournaments with registration info."""
        if status == "all":
            tournaments = db.get_guild_tournaments(interaction.guild.id)
        else:
            tournaments = db.get_guild_tournaments(interaction.guild.id, status)
        
        if not tournaments:
            embed = create_error_embed(
                "No Tournaments",
                f"No {status} tournaments found."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        tournaments_text = ""
        for t in tournaments[:5]:  # Show first 5 with details
            teams = db.get_tournament_teams(interaction.guild.id, t[0])
            tournaments_text += f"\n{Emojis.TROPHY} **{t[1]}**\n"
            tournaments_text += f"Format: {t[3]} | Status: {t[4].upper()}\n"
            tournaments_text += f"Teams: {len(teams)}\n"
            if t[5]:  # started_at
                tournaments_text += f"Started: <t:{int(t[5])}:R>\n"
            tournaments_text += "---\n"
        
        embed = create_tournament_embed(
            f"Tournament List ({status.upper()})",
            tournaments_text or "No tournaments found.",
            color=Colors.RUNE
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tourneyview", description="View tournament details")
    @app_commands.describe(tournament_name="Select tournament to view")
    @app_commands.autocomplete(tournament_name=tournament_autocomplete)
    async def view_tournament(
        self,
        interaction: discord.Interaction,
        tournament_name: str
    ):
        """View detailed tournament information."""
        # Find tournament by name
        tournaments = db.get_guild_tournaments(interaction.guild.id)
        tournament = None
        for t in tournaments:
            if t[1].lower() == tournament_name.lower() or t[0] == tournament_name:
                tournament = t
                break
        
        if not tournament:
            embed = create_error_embed("Tournament Not Found", f"No tournament found with name '{tournament_name}'.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        tournament_id = tournament[0]
        teams = db.get_tournament_teams(interaction.guild.id, tournament_id)
        
        embed = create_tournament_embed(
            tournament[1],  # name
            f"**Format**: {tournament[3]}\n**Status**: {tournament[4].upper()}\n**Teams**: {len(teams)}",
            color=Colors.GOLD
        )
        
        if teams:
            teams_text = "\n".join([f"• {team[2]}" for team in teams[:10]])
            embed.add_field(name="Registered Teams", value=teams_text, inline=False)
        
        if tournament[5]:  # started_at
            embed.add_field(name="Started", value=f"<t:{int(tournament[5])}:R>", inline=True)
        
        if tournament[6]:  # ended_at
            embed.add_field(name="Ended", value=f"<t:{int(tournament[6])}:R>", inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Tournaments(bot))
