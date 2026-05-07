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
            format=format,
            created_by=interaction.user.id
        )
        
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
        tournament_id="Tournament ID",
        team_name="Your team name",
        members="Team members (space-separated mentions for 2v2)"
    )
    async def join(
        self,
        interaction: discord.Interaction,
        tournament_id: str,
        team_name: str,
        members: str = ""
    ):
        """Register a team for a tournament."""
        config = get_config()
        settings = config.get_guild_settings(interaction.guild.id)
        
        if not settings:
            embed = create_error_embed("Guild Not Configured", "This guild hasn't set up tournaments.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        tournament = db.get_tournament(interaction.guild.id, tournament_id)
        if not tournament:
            embed = create_error_embed("Tournament Not Found", "This tournament doesn't exist.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if tournament[4] != "registration":
            embed = create_error_embed("Registration Closed", "This tournament is no longer accepting registrations.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Parse members
        team_members = [interaction.user.id]
        if members.strip():
            for mention in interaction.message.mentions if hasattr(interaction, 'message') else []:
                team_members.append(mention.id)
        
        # Validate team size
        if tournament[2] == "1v1" and len(team_members) > 1:
            embed = create_error_embed("Invalid Team Size", "1v1 tournaments are solo.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if tournament[2] == "2v2" and len(team_members) > 2:
            embed = create_error_embed("Invalid Team Size", "2v2 tournaments require exactly 2 players.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Register team
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
            fields=[("Status", "Registered", True)]
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="tourneystart", description="Start a tournament")
    @app_commands.describe(tournament_id="Tournament ID")
    async def start(
        self,
        interaction: discord.Interaction,
        tournament_id: str
    ):
        """Start a tournament and begin matches."""
        config = get_config()
        admin_roles = config.get_tournament_admins(interaction.guild.id)
        has_perm = any(role.id in admin_roles for role in interaction.user.roles)
        
        if not has_perm:
            embed = create_error_embed("Permission Denied", "You don't have permission to start tournaments.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        tournament = db.get_tournament(interaction.guild.id, tournament_id)
        if not tournament:
            embed = create_error_embed("Tournament Not Found", "This tournament doesn't exist.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.start_tournament(interaction.guild.id, tournament_id)
        
        embed = create_tournament_embed(
            "Tournament Started",
            tournament[1],
            f"{Lore.tournament_started(tournament[1])}\n\n**Format**: {tournament[2]}",
            fields=[("Status", "In Progress", True)]
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
        
        # Get winner team info
        winner = db.get_tournament_team(interaction.guild.id, tournament_id, winner_team)
        if not winner:
            embed = create_error_embed("Team Not Found", "The winning team doesn't exist.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Record match
        match_id = db.record_tournament_match(
            guild_id=interaction.guild.id,
            tournament_id=tournament_id,
            team1_id=winner_team,
            team2_id=loser_team,
            winner_id=winner_team,
            round=round_num
        )
        
        winner_mentions = " + ".join([f"<@{m}>" for m in json.loads(winner[3])])
        embed = create_success_embed(
            "Match Recorded",
            f"**Winners**: {winner_mentions}\n**Tournament**: {tournament[1]}\n**Round**: {round_num}"
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

async def setup(bot):
    await bot.add_cog(Tournaments(bot))
