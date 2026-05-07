# Runekeeper - Hall of the Slain Discord Bot

A specialized Discord bot for managing the "Hall of the Slain" gaming guild with dark fantasy/Norse aesthetics. Runekeeper handles trials, tournaments, events, appeals, and guild operations.

## Features

### 🛡️ Trial System
- Members can apply to become Trial Candidates
- Configurable review roles approve/deny applications
- Automatic role assignment upon approval
- Optional trial expiration

### ⚔️ Tournament System (Most Important)
- Create tournaments with 1v1 or 2v2 formats
- Team registration and management
- Match tracking and bracket support
- Tournament leaderboards
- Champion role assignment
- Tournament history

### 📢 Event Management
- Create and schedule guild events
- RSVP tracking (attending/not attending)
- Automatic reminders 1 hour before events
- Event leaderboards

### ⚖️ Appeals System
- Members can submit appeals for punishments
- Configurable appeal reviewers
- Approval/denial workflow with notifications
- Appeal history tracking

### 👑 Hall Information
- Display guild rules and lore
- Show guild positions and roles
- Member viewing

### 📜 Internal Logging
- Log all Runekeeper actions separately from moderation
- Action types: trial decisions, tournament results, role assignments, appeals
- Searchable action logs

### 📣 Announcements
- Create themed announcements
- Victory celebrations
- Custom themed messages with dark fantasy aesthetic

## Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd Runekeeper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your bot token:
```env
DISCORD_TOKEN=your_token_here
```

4. Copy `config.example.json` to `config.json` and configure:
```bash
cp config.example.json config.json
```

5. Edit `config.json` with your guild settings, roles, and channels.

6. Run the bot:
```bash
python main.py
```

## Configuration

### config.json Structure

```json
{
  "token": "bot-token",
  "prefix": "*",
  "owner_id": 123456789012345678,
  "application_id": 123456789012345678,
  "guilds": {
    "guild_id": {
      "name": "Hall of the Slain",
      "guild_roles": {
        "Gatekeeper": role_id,
        "Jarl": role_id,
        "Battle Herald": role_id
      },
      "trial_role_id": role_id,
      "trial_channel": channel_id,
      "tournament_channel": channel_id,
      "trial_reviewers": [role_id1, role_id2],
      "appeal_reviewers": [role_id1, role_id2],
      "tournament_admins": [role_id1, role_id2],
      "event_admins": [role_id1, role_id2],
      "hall_info": {
        "rules": "Guild rules",
        "lore": "Guild lore"
      }
    }
  }
}
```

## Commands

### Trials
- `/applyfortrial` - Apply to become a Trial Candidate
- `/trialstatus` - Check your trial application status
- `/viewtrials` - View pending/approved/denied trials (reviewer only)

### Tournaments
- `/tourneycreate` - Create a new tournament
- `/tourneyjoin` - Register a team for a tournament
- `/tourneystart` - Start a tournament (admin only)
- `/tourneyresult` - Report match results (admin only)
- `/tourneyleaderboard` - View tournament leaderboard

### Events
- `/eventcreate` - Create a guild event (admin only)
- `/eventrsvp` - RSVP to an event
- `/eventlist` - View upcoming events
- `/eventrsvplist` - See who RSVPed to an event

### Appeals
- `/appeal` - Submit an appeal
- `/appealstatus` - Check your appeal status
- `/viewappeals` - View pending appeals (reviewer only)

### Hall Information
- `/hallinfo` - View hall rules, lore, and roles
- `/members` - View hall members

### Logging
- `/viewlogs` - View action logs
- `/logaction` - Manually log an action (admin only)

### Announcements
- `/announce` - Post a themed announcement
- `/celebratevictory` - Celebrate a victory
- `/themedmessage` - Create a custom themed message

## Database

Runekeeper uses SQLite for persistence. The database is automatically initialized on startup with the following tables:

- `trial_candidates` - Trial applications and status
- `tournaments` - Tournament information
- `tournament_teams` - Team registrations
- `tournament_matches` - Match results
- `events` - Event information
- `event_rsvps` - Event RSVPs
- `appeals` - Appeal submissions
- `internal_logs` - Action logs

## Architecture

- **main.py** - Bot entry point and event handlers
- **config.py** - Configuration management
- **utils/db.py** - Database operations
- **utils/themes.py** - Dark fantasy theming and embeds
- **utils/decorators.py** - Permission and role checkers
- **cogs/trials.py** - Trial system
- **cogs/tournaments.py** - Tournament system
- **cogs/events.py** - Event management
- **cogs/appeals.py** - Appeals system
- **cogs/hall_info.py** - Guild information
- **cogs/logging.py** - Action logging
- **cogs/announcements.py** - Themed announcements

## Important Notes

- **Sapphire Compatibility**: Runekeeper does not conflict with the Sapphire moderation bot
- **Noctaly Compatibility**: No conflicts with economy/leveling/XP systems
- **Dark Fantasy Theme**: All responses are lore-accurate and themed for immersion
- **Security**: Bot token should be stored in environment variables, not in config files

## Contributing

Make sure to follow the dark fantasy aesthetic when adding new features. All messages should be lore-appropriate and themed.

## License

This project is for the Hall of the Slain gaming guild.
