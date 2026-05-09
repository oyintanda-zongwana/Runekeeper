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
        return "Your petition has been received by the Hall. The elders will judge your worthiness within these ancient walls."
    
    @staticmethod
    def trial_approved() -> str:
        return "The Hall has recognized your warrior spirit. Welcome to our ranks, valiant one."
    
    @staticmethod
    def trial_denied() -> str:
        return "The Hall has deemed you unworthy at this time. Sharpen your skills and return when you are ready to prove yourself."
    
    @staticmethod
    def tournament_created(name: str) -> str:
        return f"⚔️ A new Trial of Combat has been declared: **{name}**\n\nLet the strongest rise to glory. Warriors, prepare your blades."
    
    @staticmethod
    def tournament_started(name: str) -> str:
        return f"🔥 The Trial of Combat begins: **{name}**\n\nMay the worthy prevail. Let blood and honor guide your paths."
    
    @staticmethod
    def tournament_victory(winner: str) -> str:
        return f"🏆 Victory belongs to **{winner}**!\n\nTheir name shall echo through the halls of glory forevermore. They have proven their strength."
    
    @staticmethod
    def tournament_registration_closed() -> str:
        return "The gates have closed. No more warriors may enter this Trial of Combat."
    
    @staticmethod
    def event_created(name: str) -> str:
        return f"📢 A gathering has been announced: **{name}**\n\nGather, warriors, and prepare for what comes. Your presence is required."
    
    @staticmethod
    def event_reminder(name: str, time_remaining: str) -> str:
        return f"⏰ Reminder: **{name}** begins in {time_remaining}.\n\nDo not be late. The Hall waits for none."
    
    @staticmethod
    def event_started(name: str) -> str:
        return f"🎭 **{name}** has begun.\n\nAll warriors who pledged to attend, take your place in the Hall."
    
    @staticmethod
    def appeal_submitted() -> str:
        return "⚖️ Your appeal has been heard by the Council of Elders. They shall deliberate on your petition in due time."
    
    @staticmethod
    def appeal_approved() -> str:
        return "✅ The Council has shown mercy. Your petition has been **approved**. Justice prevails."
    
    @staticmethod
    def appeal_denied() -> str:
        return "❌ The Council's judgment stands. Your appeal has been **denied**. Accept their wisdom."
    
    @staticmethod
    def role_assigned(role_name: str) -> str:
        return f"🏛️ You have been honored with the position: **{role_name}**\n\nMay you serve the Hall with distinction."
    
    @staticmethod
    def role_removed(role_name: str) -> str:
        return f"⚠️ Your station as **{role_name}** has been revoked. You remain a warrior of the Hall, though diminished."
    
    @staticmethod
    def join_tournament() -> str:
        return "⚔️ You have joined the Trial of Combat. Prepare yourself for battle."
    
    @staticmethod
    def leave_tournament() -> str:
        return "You have withdrawn from the Trial of Combat. The other warriors shall continue without you."
    
    @staticmethod
    def error_generic() -> str:
        return "The Hall's magic has faltered. An error has occurred. Try again."
    
    @staticmethod
    def permission_denied() -> str:
        return "🔒 You lack the authority to perform this action. Only the worthy may proceed."
    
    @staticmethod
    def not_configured() -> str:
        return "⚙️ This feature has not been configured by the Hall's administrators. Please contact them."


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
    WARN = "⚠️"
    GOLD = "⭐"
    HAMMER = "🔨"
    WOLF = "🐺"
    DRAGON = "🐉"
    BOOK = "📖"
    MEDAL = "🥇"
    TIMER = "⏰"
    USERS = "👥"
    GEAR = "⚙️"


class HallEmbed:
    """Unified embed builder for Hall of the Slain."""
    
    @staticmethod
    def victory(title: str, description: str = "", fields: Optional[list] = None) -> discord.Embed:
        """Create victory/success announcement embed."""
        embed = create_embed(
            title=f"{Emojis.VICTORY} {title}",
            description=description,
            color=Colors.TRIUMPH,
            fields=fields,
            footer_text="Victory is ours!"
        )
        return embed
    
    @staticmethod
    def announcement(title: str, description: str = "", fields: Optional[list] = None) -> discord.Embed:
        """Create announcement embed."""
        embed = create_embed(
            title=f"{Emojis.ANNOUNCE} {title}",
            description=description,
            color=Colors.GOLD,
            fields=fields,
            footer_text="Hall Announcement"
        )
        return embed
    
    @staticmethod
    def warning(title: str, description: str = "") -> discord.Embed:
        """Create warning embed."""
        return create_error_embed(title, description)
    
    @staticmethod
    def action(title: str, description: str = "", fields: Optional[list] = None) -> discord.Embed:
        """Create action result embed."""
        embed = create_embed(
            title=f"{Emojis.SWORD} {title}",
            description=description,
            color=Colors.GOLD,
            fields=fields,
            footer_text="Action executed"
        )
        return embed
    
    @staticmethod
    def information(title: str, description: str = "", fields: Optional[list] = None) -> discord.Embed:
        """Create informational embed."""
        return create_info_embed(title, description, fields=fields)
