"""
Decorators and utilities for Runekeeper commands.
"""
import discord
from discord.ext import commands
from functools import wraps
from typing import Callable, List, Optional
from config import get_config
from utils.themes import create_error_embed

def require_trial_reviewer():
    """Require user to have trial reviewer role."""
    async def predicate(ctx):
        config = get_config()
        if not ctx.guild:
            raise commands.CheckFailure("This command can only be used in a guild.")
        
        reviewer_roles = config.get_trial_reviewers(ctx.guild.id)
        if not reviewer_roles:
            raise commands.CheckFailure("No trial reviewers configured for this guild.")
        
        has_role = any(role.id in reviewer_roles for role in ctx.author.roles)
        if not has_role:
            raise commands.CheckFailure("You do not have permission to review trials.")
        
        return True
    
    return commands.check(predicate)


def require_appeal_reviewer():
    """Require user to have appeal reviewer role."""
    async def predicate(ctx):
        config = get_config()
        if not ctx.guild:
            raise commands.CheckFailure("This command can only be used in a guild.")
        
        reviewer_roles = config.get_appeal_reviewers(ctx.guild.id)
        if not reviewer_roles:
            raise commands.CheckFailure("No appeal reviewers configured for this guild.")
        
        has_role = any(role.id in reviewer_roles for role in ctx.author.roles)
        if not has_role:
            raise commands.CheckFailure("You do not have permission to review appeals.")
        
        return True
    
    return commands.check(predicate)


def require_tournament_admin():
    """Require user to have tournament admin role."""
    async def predicate(ctx):
        config = get_config()
        if not ctx.guild:
            raise commands.CheckFailure("This command can only be used in a guild.")
        
        admin_roles = config.get_tournament_admins(ctx.guild.id)
        if not admin_roles:
            raise commands.CheckFailure("No tournament admins configured for this guild.")
        
        has_role = any(role.id in admin_roles for role in ctx.author.roles)
        if not has_role:
            raise commands.CheckFailure("You do not have permission to manage tournaments.")
        
        return True
    
    return commands.check(predicate)


def require_event_admin():
    """Require user to have event admin role."""
    async def predicate(ctx):
        config = get_config()
        if not ctx.guild:
            raise commands.CheckFailure("This command can only be used in a guild.")
        
        admin_roles = config.get_event_admins(ctx.guild.id)
        if not admin_roles:
            raise commands.CheckFailure("No event admins configured for this guild.")
        
        has_role = any(role.id in admin_roles for role in ctx.author.roles)
        if not has_role:
            raise commands.CheckFailure("You do not have permission to manage events.")
        
        return True
    
    return commands.check(predicate)


def require_guild_configured():
    """Require guild to be configured."""
    async def predicate(ctx):
        config = get_config()
        if not ctx.guild:
            raise commands.CheckFailure("This command can only be used in a guild.")
        
        settings = config.get_guild_settings(ctx.guild.id)
        if not settings:
            raise commands.CheckFailure(f"Guild {ctx.guild.name} is not configured. Please contact an administrator.")
        
        return True
    
    return commands.check(predicate)


class PermissionHelper:
    """Helper methods for permission validation."""
    
    @staticmethod
    def has_trial_reviewer_role(member: discord.Member, guild_id: int) -> bool:
        """Check if member has trial reviewer role."""
        config = get_config()
        reviewer_roles = config.get_trial_reviewers(guild_id)
        return any(role.id in reviewer_roles for role in member.roles)
    
    @staticmethod
    def has_appeal_reviewer_role(member: discord.Member, guild_id: int) -> bool:
        """Check if member has appeal reviewer role."""
        config = get_config()
        reviewer_roles = config.get_appeal_reviewers(guild_id)
        return any(role.id in reviewer_roles for role in member.roles)
    
    @staticmethod
    def has_tournament_admin_role(member: discord.Member, guild_id: int) -> bool:
        """Check if member has tournament admin role."""
        config = get_config()
        admin_roles = config.get_tournament_admins(guild_id)
        return any(role.id in admin_roles for role in member.roles)
    
    @staticmethod
    def has_event_admin_role(member: discord.Member, guild_id: int) -> bool:
        """Check if member has event admin role."""
        config = get_config()
        admin_roles = config.get_event_admins(guild_id)
        return any(role.id in admin_roles for role in member.roles)
    
    @staticmethod
    async def send_error(ctx, title: str, description: str):
        """Send an error embed."""
        embed = create_error_embed(title, description)
        if isinstance(ctx, discord.Interaction):
            await ctx.response.send_message(embed=embed, ephemeral=True)
        else:
            await ctx.send(embed=embed)
