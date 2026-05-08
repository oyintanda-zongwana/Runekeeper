"""
Event Management System
Handles guild event creation, RSVPs, and reminders.
"""
import discord
from discord.ext import commands, tasks
from discord import app_commands
import time
from config import get_config
from utils import db
from utils.themes import (
    create_event_embed, create_success_embed, create_error_embed,
    Colors, Lore, Emojis
)
from utils.decorators import require_event_admin

class Events(commands.Cog):
    """Event management for Hall of the Slain."""
    
    def __init__(self, bot):
        self.bot = bot
        self.event_reminder.start()
    
    def cog_unload(self):
        self.event_reminder.cancel()
    
    @app_commands.command(name="eventcreate", description="Create a new event")
    @app_commands.describe(
        name="Event name",
        description="Event description",
        hours_from_now="Hours from now the event occurs"
    )
    async def create(
        self,
        interaction: discord.Interaction,
        name: str,
        description: str,
        hours_from_now: int
    ):
        """Create a new guild event."""
        config = get_config()
        admin_roles = config.get_event_admins(interaction.guild.id)
        has_perm = any(role.id in admin_roles for role in interaction.user.roles)
        
        if not has_perm:
            embed = create_error_embed("Permission Denied", "You don't have permission to create events.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if hours_from_now < 1:
            embed = create_error_embed("Invalid Time", "Event must be at least 1 hour from now.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Calculate scheduled time
        scheduled_for = int(time.time()) + (hours_from_now * 3600)
        
        event_id = db.create_event(
            guild_id=interaction.guild.id,
            name=name,
            scheduled_for=scheduled_for,
            created_by=interaction.user.id,
            description=description
        )
        
        embed = create_event_embed(
            "Event Created",
            name,
            description,
            fields=[
                ("Time", f"<t:{scheduled_for}:f>", True),
                ("Created by", interaction.user.mention, True)
            ]
        )
        
        # Send to event channel
        settings = config.get_guild_settings(interaction.guild.id)
        event_channel_id = settings.get("event_channel")
        if event_channel_id:
            channel = interaction.guild.get_channel(event_channel_id)
            if channel:
                # Create RSVP buttons
                view = discord.ui.View()
                view.add_item(RsvpButton("yes", event_id, interaction.guild.id, self.bot))
                view.add_item(RsvpButton("no", event_id, interaction.guild.id, self.bot))
                await channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="eventrsvp", description="RSVP to an event")
    @app_commands.describe(
        event_id="Event ID",
        status="RSVP status (attending or not_attending)"
    )
    async def rsvp(
        self,
        interaction: discord.Interaction,
        event_id: str,
        status: str
    ):
        """RSVP to a guild event."""
        if status not in ["attending", "not_attending"]:
            embed = create_error_embed("Invalid Status", "Status must be 'attending' or 'not_attending'.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        event = db.get_event(interaction.guild.id, event_id)
        if not event:
            embed = create_error_embed("Event Not Found", "This event doesn't exist.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        db.rsvp_event(
            guild_id=interaction.guild.id,
            event_id=event_id,
            user_id=interaction.user.id,
            status=status
        )
        
        status_emoji = Emojis.CHECK if status == "attending" else Emojis.CROSS
        embed = create_success_embed(
            f"{status_emoji} RSVP Recorded",
            f"You are {status.replace('_', ' ')} for **{event[2]}**"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="eventlist", description="List all upcoming events")
    async def list_events(self, interaction: discord.Interaction):
        """Display all upcoming events."""
        events = db.get_guild_events(interaction.guild.id, status="scheduled")
        
        if not events:
            embed = create_error_embed("No Events", "No upcoming events scheduled.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        events_text = ""
        for event in events[:10]:
            guild_id, event_id, name, desc, scheduled, creator_id, created_at, status = event
            time_str = f"<t:{int(scheduled)}:R>"
            events_text += f"{Emojis.ANNOUNCE} **{name}** - {time_str}\n"
        
        embed = create_event_embed(
            "Upcoming Events",
            "",
            events_text,
            footer="Hall Events"
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="eventrsvplist", description="See who RSVPed to an event")
    @app_commands.describe(event_id="Event ID")
    async def rsvp_list(
        self,
        interaction: discord.Interaction,
        event_id: str
    ):
        """Display RSVP list for an event."""
        event = db.get_event(interaction.guild.id, event_id)
        if not event:
            embed = create_error_embed("Event Not Found", "This event doesn't exist.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        rsvps = db.get_event_rsvps(interaction.guild.id, event_id)
        
        attending = [r for r in rsvps if r[3] == "attending"]
        not_attending = [r for r in rsvps if r[3] == "not_attending"]
        
        attending_str = "\n".join([f"{Emojis.CHECK} <@{r[2]}>" for r in attending[:20]]) or "None"
        not_attending_str = "\n".join([f"{Emojis.CROSS} <@{r[2]}>" for r in not_attending[:20]]) or "None"
        
        embed = create_event_embed(
            "RSVP List",
            event[2],
            "",
            fields=[
                ("Attending", attending_str, True),
                ("Not Attending", not_attending_str, True)
            ]
        )
        
        await interaction.response.send_message(embed=embed)
    
    @tasks.loop(minutes=5)
    async def event_reminder(self):
        """Send reminders for upcoming events."""
        current_time = int(time.time())
        
        # Get all guilds
        for guild_id in [g.id for g in self.bot.guilds]:
            events = db.get_guild_events(guild_id, status="scheduled")
            
            for event in events:
                guild_id, event_id, name, desc, scheduled, creator_id, created_at, status = event
                
                # 1 hour before
                if scheduled - 3600 <= current_time <= scheduled - 3000:
                    config = get_config()
                    settings = config.get_guild_settings(guild_id)
                    event_channel_id = settings.get("event_channel")
                    
                    if event_channel_id:
                        channel = self.bot.get_channel(event_channel_id)
                        if channel:
                            rsvps = db.get_event_rsvps(guild_id, event_id)
                            attending = [r for r in rsvps if r[3] == "attending"]
                            
                            embed = create_event_embed(
                                "Event Reminder",
                                name,
                                f"{Lore.event_reminder(name, '1 hour')}\n\nAttending: {len(attending)}"
                            )
                            await channel.send(embed=embed)
    
    @event_reminder.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()


class RsvpButton(discord.ui.Button):
    """RSVP button for events."""
    
    def __init__(self, status: str, event_id: str, guild_id: int, bot):
        self.event_id = event_id
        self.guild_id = guild_id
        self.bot = bot
        self.status = status
        
        label = "Attending" if status == "yes" else "Not Attending"
        emoji = Emojis.CHECK if status == "yes" else Emojis.CROSS
        style = discord.ButtonStyle.green if status == "yes" else discord.ButtonStyle.red
        
        super().__init__(label=label, style=style, emoji=emoji)
    
    async def callback(self, interaction: discord.Interaction):
        status = "attending" if self.status == "yes" else "not_attending"
        
        db.rsvp_event(
            guild_id=self.guild_id,
            event_id=self.event_id,
            user_id=interaction.user.id,
            status=status
        )
        
        embed = create_success_embed(
            f"{self.emoji} RSVP Recorded",
            f"Your RSVP has been recorded."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Events(bot))
