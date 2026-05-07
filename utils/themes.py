"""
Runekeeper Theme System
Dark Fantasy / Norse Inspired aesthetics for Hall of the Slain
"""
import discord
from typing import Optional, Tuple

# Theme Colors
class Colors:
    """Hall of the Slain themed color palette."""
    GOLD = 0xD4AF37        # Primary gold
    BLACK = 0x1a1a1a       # Primary black
    WHITE = 0xF5F5F5       # Primary white
    BLOOD = 0x8B0000       # Blood red
    STEEL = 0x4A4A4A       # Steel gray
    RUNE = 0x9932CC        # Rune purple
    TRIUMPH = 0xFFD700     # Victory gold
    WARNING = 0xFF6B6B     # Warning red
    SUCCESS = 0x2ECC71     # Success green
    INFO = 0x3498DB        # Info blue

# Lore Responses
class Lore:
    """Lore-accurate responses matching Hall aesthetic."""
    
    @staticmethod
    def trial_submitted() -> str:
        return "Your petition has been received by the Hall. The elders will judge your worthiness."
    
    @staticmethod
    def trial_approved() -> str:
        return "The Hall has recognized your warrior spirit. Welcome to our ranks."
    
    @staticmethod
    def trial_denied() -> str:
        return "The Hall has deemed you unworthy at this time. Prepare yourself and return when ready."
    
    @staticmethod
    def tournament_created(name: str) -> str:
        return f"A new Trial of Combat has been declared: **{name}**\nLet the strongest rise to glory."
    
    @staticmethod
    def tournament_started(name: str) -> str:
        return f"The Trial of Combat begins: **{name}**\nMay the worthy prevail."
    
    @staticmethod
    def tournament_victory(winner: str) -> str:
        return f"Victory belongs to **{winner}**! Their name shall echo through the halls of glory."
    
    @staticmethod
    def event_created(name: str) -> str:
        return f"A gathering has been announced: **{name}**\nGather, warriors, and prepare for what comes."
    
    @staticmethod
    def event_reminder(name: str, time_remaining: str) -> str:
        return f"Reminder: **{name}** begins in {time_remaining}.\nDo not be late."
    
    @staticmethod
    def appeal_submitted() -> str:
        return "Your appeal has been heard by the Council. They shall deliberate on your petition."
    
    @staticmethod
    def appeal_approved() -> str:
        return "The Council has shown mercy. Your petition has been approved."
    
    @staticmethod
    def appeal_denied() -> str:
        return "The Council's judgment stands. Your appeal has been denied."
    
    @staticmethod
    def role_assigned(role_name: str) -> str:
        return f"You have been honored with the position: **{role_name}**"
    
    @staticmethod
    def role_removed(role_name: str) -> str:
        return f"Your station as **{role_name}** has been revoked."


def create_embed(
    title: str,
    description: str = "",
    color: int = Colors.GOLD,
    author_name: Optional[str] = None,
    author_icon: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
    image_url: Optional[str] = None,
    fields: Optional[list] = None,
    footer_text: Optional[str] = None,
    footer_icon: Optional[str] = None,
) -> discord.Embed:
    """Create a themed embed for Runekeeper."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=discord.utils.utcnow()
    )
    
    if author_name:
        embed.set_author(name=author_name, icon_url=author_icon)
    
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    if image_url:
        embed.set_image(url=image_url)
    
    if fields:
        for field_name, field_value, inline in fields:
            embed.add_field(name=field_name, value=field_value, inline=inline)
    
    if footer_text:
        embed.set_footer(text=footer_text, icon_url=footer_icon)
    else:
        embed.set_footer(text="Hall of the Slain")
    
    return embed


def create_success_embed(
    title: str,
    description: str = "",
    footer: str = "Action completed"
) -> discord.Embed:
    """Create a success embed."""
    return create_embed(
        title=f"⚔️ {title}",
        description=description,
        color=Colors.TRIUMPH,
        footer_text=footer
    )


def create_error_embed(
    title: str,
    description: str = "",
    footer: str = "An error occurred"
) -> discord.Embed:
    """Create an error embed."""
    return create_embed(
        title=f"⚠️ {title}",
        description=description,
        color=Colors.WARNING,
        footer_text=footer
    )


def create_info_embed(
    title: str,
    description: str = "",
    color: int = Colors.GOLD,
    footer: str = "Hall Information"
) -> discord.Embed:
    """Create an informational embed."""
    return create_embed(
        title=f"📜 {title}",
        description=description,
        color=color,
        footer_text=footer
    )


def create_tournament_embed(
    title: str,
    tournament_name: str,
    description: str = "",
    fields: Optional[list] = None,
    footer: str = "Trial of Combat"
) -> discord.Embed:
    """Create a tournament-themed embed."""
    full_title = f"⚔️ {title}: {tournament_name}"
    return create_embed(
        title=full_title,
        description=description,
        color=Colors.BLOOD,
        fields=fields,
        footer_text=footer
    )


def create_event_embed(
    title: str,
    event_name: str,
    description: str = "",
    fields: Optional[list] = None,
    footer: str = "Hall Event"
) -> discord.Embed:
    """Create an event-themed embed."""
    full_title = f"📢 {title}: {event_name}"
    return create_embed(
        title=full_title,
        description=description,
        color=Colors.RUNE,
        fields=fields,
        footer_text=footer
    )


def create_trial_embed(
    title: str,
    description: str = "",
    fields: Optional[list] = None,
    status: str = "pending"
) -> discord.Embed:
    """Create a trial candidate embed."""
    status_colors = {
        "pending": Colors.INFO,
        "approved": Colors.SUCCESS,
        "denied": Colors.WARNING
    }
    color = status_colors.get(status, Colors.GOLD)
    
    full_title = f"🛡️ {title}"
    return create_embed(
        title=full_title,
        description=description,
        color=color,
        fields=fields,
        footer_text=f"Trial Status: {status.capitalize()}"
    )


def create_appeal_embed(
    title: str,
    description: str = "",
    fields: Optional[list] = None,
    status: str = "pending"
) -> discord.Embed:
    """Create an appeal embed."""
    status_colors = {
        "pending": Colors.INFO,
        "approved": Colors.SUCCESS,
        "denied": Colors.WARNING
    }
    color = status_colors.get(status, Colors.GOLD)
    
    full_title = f"⚖️ {title}"
    return create_embed(
        title=full_title,
        description=description,
        color=color,
        fields=fields,
        footer_text=f"Appeal Status: {status.capitalize()}"
    )


class Emojis:
    """Themed emoji constants."""
    SWORD = "⚔️"
    SHIELD = "🛡️"
    CROWN = "👑"
    SCROLL = "📜"
    ANNOUNCE = "📢"
    JUDGE = "⚖️"
    VICTORY = "🏆"
    DANGER = "⚠️"
    CHECK = "✅"
    CROSS = "❌"
    FIRE = "🔥"
    BLOOD = "🩸"
    RUNE = "✨"
    HOURGLASS = "⏳"
