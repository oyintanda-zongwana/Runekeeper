"""
Interaction Utilities
Safe interaction handling with error recovery and timeout management.
"""
import discord
from discord.app_commands import AppCommand
from utils.themes import create_error_embed, Lore, Emojis
from typing import Optional, Callable
import asyncio


class InteractionHandler:
    """Safe interaction callback wrapper with error handling."""
    
    @staticmethod
    async def safe_respond(
        interaction: discord.Interaction,
        embed: discord.Embed,
        ephemeral: bool = False
    ) -> bool:
        """
        Safely respond to an interaction with error handling.
        
        Returns:
            bool: True if successful, False if interaction expired or failed
        """
        try:
            if interaction.response.is_done():
                # If response already sent, use followup
                await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
            return True
        except discord.errors.InteractionExpired:
            # Interaction expired, cannot respond
            return False
        except discord.errors.NotFound:
            # Interaction not found, likely expired
            return False
        except Exception as e:
            # Log unexpected errors
            print(f"Error responding to interaction: {e}")
            return False
    
    @staticmethod
    async def safe_defer(
        interaction: discord.Interaction,
        ephemeral: bool = False
    ) -> bool:
        """
        Safely defer an interaction.
        
        Returns:
            bool: True if successful, False if already deferred or failed
        """
        try:
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=ephemeral)
            return True
        except discord.errors.InteractionExpired:
            return False
        except Exception:
            return False
    
    @staticmethod
    async def safe_followup(
        interaction: discord.Interaction,
        embed: discord.Embed,
        ephemeral: bool = False
    ) -> bool:
        """
        Safely send a followup message.
        
        Returns:
            bool: True if successful, False if failed
        """
        try:
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            return True
        except discord.errors.InteractionExpired:
            return False
        except Exception as e:
            print(f"Error sending followup: {e}")
            return False


class PermissionHelper:
    """Permission checking utilities."""
    
    @staticmethod
    def check_role_permission(
        user: discord.Member,
        required_role_ids: list
    ) -> bool:
        """Check if user has any of the required roles."""
        user_role_ids = [r.id for r in user.roles]
        return any(role_id in user_role_ids for role_id in required_role_ids)
    
    @staticmethod
    def get_missing_permissions(
        user: discord.Member,
        required_role_ids: list
    ) -> Optional[str]:
        """
        Get a descriptive message about missing permissions.
        
        Returns:
            str: Descriptive message, or None if user has permission
        """
        if not required_role_ids:
            return None
        
        if PermissionHelper.check_role_permission(user, required_role_ids):
            return None
        
        return f"{Lore.permission_denied()}"


class CooldownHelper:
    """Simple cooldown management for repeated actions."""
    
    def __init__(self):
        self.cooldowns = {}  # {user_id: {action: timestamp}}
    
    def is_on_cooldown(
        self,
        user_id: int,
        action: str,
        cooldown_seconds: int = 5
    ) -> bool:
        """Check if user is on cooldown for an action."""
        import time
        
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = {}
        
        last_use = self.cooldowns[user_id].get(action, 0)
        return (time.time() - last_use) < cooldown_seconds
    
    def set_cooldown(self, user_id: int, action: str):
        """Set a cooldown for a user action."""
        import time
        
        if user_id not in self.cooldowns:
            self.cooldowns[user_id] = {}
        
        self.cooldowns[user_id][action] = time.time()
    
    def get_cooldown_remaining(
        self,
        user_id: int,
        action: str,
        cooldown_seconds: int = 5
    ) -> int:
        """Get remaining cooldown seconds."""
        import time
        
        if user_id not in self.cooldowns:
            return 0
        
        last_use = self.cooldowns[user_id].get(action, 0)
        remaining = cooldown_seconds - int(time.time() - last_use)
        return max(0, remaining)


# Global cooldown manager
cooldown_manager = CooldownHelper()
