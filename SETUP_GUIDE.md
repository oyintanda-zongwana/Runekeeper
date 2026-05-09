# 🏛️ Runekeeper Setup Guide

**A Production-Ready Guild Management System for Hall of the Slain**

---

## 📦 Quick Start (5 minutes)

### 1. Get a Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" → name it "Runekeeper"
3. Go to "Bot" → Click "Add Bot"
4. Under TOKEN, click "Copy" (save this securely!)
5. Go to OAuth2 → URL Generator
6. Select scopes: `bot`, `applications.commands`
7. Select permissions:
   - Read Messages/View Channels
   - Send Messages
   - Manage Messages
   - Embed Links
   - Read Message History
8. Copy generated URL and paste in browser to invite bot to your guild

### 2. Install Runekeeper

```bash
# Clone/extract the repository
cd Runekeeper

# Install Python dependencies
pip install -r requirements.txt

# Create configuration file
cp config.example.json config.json
```

### 3. Configure Bot

Edit `config.json`:

```json
{
  "token": "YOUR_BOT_TOKEN_HERE",
  "prefix": "*hall",
  "owner_id": YOUR_DISCORD_ID,
  "application_id": YOUR_APP_ID,
  "guild_id": YOUR_GUILD_ID,
  "guilds": {
    "YOUR_GUILD_ID": {
      "name": "Hall of the Slain",
      "trial_channel": CHANNEL_ID,
      "tournament_channel": CHANNEL_ID,
      "event_channel": CHANNEL_ID,
      "log_channel": CHANNEL_ID,
      "appeals_channel": CHANNEL_ID
    }
  }
}
```

### 4. Run the Bot

```bash
python main.py
```

You should see:
```
✅ Loaded config_manager
✅ Loaded admin_tools
✅ Loaded help
... [13 total cogs]
✅ Synced X slash commands
✅ [BotName] is ready
```

---

## 📋 Detailed Setup Instructions

### Step 1: Create Required Discord Channels

Create these channels in your guild (adjust category names as needed):

```
📍 Information
├── #⚔-welcome              → Bot welcome messages
├── #📜-rules               → Guild rules
├── #🏛-hall-info           → Hall information
└── #📋-member-guide        → Member guide

🎪 Events & Tournaments
├── #🏆-tournaments         → Tournament announcements
└── #🎉-events              → Event announcements

⚖️ Applications & Appeals
├── #👤-trials              → Trial applications (private)
└── #📢-appeals             → Appeal submissions (private)

🛡️ Moderation & Logging
├── #📝-logs                → Bot logs (read-only, staff only)
└── #⚔-general             → General chat
```

Get the Channel IDs:
- Right-click channel → Copy Channel ID
- Add to `config.json`:

```json
"trial_channel": 123456789,
"tournament_channel": 123456789,
"event_channel": 123456789,
"log_channel": 123456789,
"appeals_channel": 123456789
```

### Step 2: Create Required Discord Roles

Create these roles in your guild:

**Core Roles:**
- High Warden: Admins (for admin commands)
- Einherjar: Mods (for moderation)

**Feature-Specific Roles:**
- Keeper of the Trials: Events Team (can create trials)
- Trial Candidates (role given to trial applicants)

**Get Role IDs:**
- Right-click role → Copy Role ID
- Add to `config.json`:

```json
"guild_roles": {
  "High Warden: Admins": 123456789,
  "Keeper of the Trials: Events Team": 123456789,
  ...
},
"trial_role_id": 123456789,
"trial_reviewers": [123456789],          // roles that can approve/deny trials
"appeal_reviewers": [123456789],        // roles that can review appeals
"tournament_admins": [123456789],       // roles that can create tournaments
"event_admins": [123456789]             // roles that can create events
```

### Step 3: Set Environment Variables

**Option A: Environment Variables (Recommended for Production)**

```bash
# Linux/Mac
export DISCORD_TOKEN="your_token_here"
export OWNER_ID="your_id_here"

# Windows PowerShell
$env:DISCORD_TOKEN = "your_token_here"
$env:OWNER_ID = "your_id_here"

# Then run
python main.py
```

**Option B: Config File (Simpler for Development)**

Edit `config.json` directly:

```json
{
  "token": "your_token_here",
  "owner_id": 123456789,
  ...
}
```

### Step 4: Verify Configuration

Run the bot and check for validation:

```bash
python main.py
```

You should see:
- ✅ All 13 cogs loaded
- ✅ Slash commands synced
- ✅ Bot appears online

Test with:
```
/help
/configdiag
```

---

## 🔧 Configuration Reference

### config.json Structure

```json
{
  "token": "string - Discord bot token",
  "prefix": "string - Prefix for text commands (default: *hall)",
  "owner_id": "number - Discord ID of bot owner",
  "application_id": "number - Discord Application ID",
  "guild_id": "number - Default guild ID (optional, for testing)",
  "guilds": {
    "guild_id_string": {
      "name": "string - Guild name",
      
      "guild_roles": {
        "Role Name": role_id,
        ...
      },
      
      "trial_role_id": number,
      "trial_channel": number,
      "trial_reviewers": [role_id, ...],
      
      "tournament_channel": number,
      "tournament_admins": [role_id, ...],
      "tournament_winner_role": number,
      "tournament_finalist_role": number,
      
      "event_channel": number,
      "event_admins": [role_id, ...],
      
      "appeals_channel": number,
      "appeal_reviewers": [role_id, ...],
      
      "log_channel": number,
      
      "hall_info": {
        "rules": "string - Hall rules",
        "lore": "string - Hall lore"
      },
      
      "features": {
        "trials": true,
        "tournaments": true,
        "events": true,
        "appeals": true
      }
    }
  }
}
```

### Example: Hall of the Slain Configuration

```json
{
  "token": "MTk4NjIyNDgzNDkxNDkyMjU0.Clwa7A.E3VqIh9r2...",
  "prefix": "*hall",
  "owner_id": 1074578668510261260,
  "application_id": 1499883269788012574,
  "guild_id": 1411503966050717729,
  "guilds": {
    "1411503966050717729": {
      "name": "Hall of the Slain",
      
      "guild_roles": {
        "All Father: Leader": 1411512354780483674,
        "High Warden: Admins": 1429605207494496407,
        "Einherjar: Mods": 1411512576545919058,
        "Keeper of the Trials: Events Team": 1498288858943586384
      },
      
      "trial_role_id": 1467875951038955675,
      "trial_channel": 1467879424308543590,
      "trial_reviewers": [1411512354780483674, 1468978052640931997],
      
      "tournament_channel": 1412152298167079105,
      "tournament_admins": [1411512354780483674, 1429605207494496407],
      
      "event_channel": 1427634742727147661,
      "event_admins": [1498288858943586384],
      
      "appeals_channel": 1473596215198351390,
      "appeal_reviewers": [1074578668510261260, 520600574148870152],
      
      "log_channel": 1412164651986194503,
      
      "hall_info": {
        "rules": "Respect all members. No spam. Follow Discord ToS.",
        "lore": "The Hall of the Slain stands as a beacon of courage and honor..."
      }
    }
  }
}
```

---

## 🎮 Using the Bot

### Basic Commands

**Help**
```
/help              → Browse all commands
*hall help [cmd]   → Get help for specific command
```

**Information**
```
/hallinfo          → View hall information and rules
/serverinfo        → View server information
/members           → View trial candidates
```

**Trials**
```
/applyfortrial [reason]     → Apply to join
/trialstatus                → Check your application
/viewtrials [status]        → View pending trials (staff only)
```

**Tournaments**
```
/tourneycreate [name] [format]   → Create tournament
/tourneyjoin [tournament_id] [team_name]
/tourneystart [tournament_id]
/tourneyresult [tournament_id] [team1] [team2] [winner]
/tourneyleaderboard [tournament_id]
```

**Events**
```
/eventcreate [name] [description] [hours]
/eventlist
/eventrsvp [event_id] [attending/not_attending]
```

**Appeals**
```
/appeal [reason]     → Submit an appeal
/appealstatus        → Check appeal status
/viewappeals         → View pending appeals (staff only)
```

**Admin**
```
/checkpermissions    → Verify bot permissions
/checkroles          → Check role hierarchy
/checkchanners       → Verify required channels
/adminstatus         → View admin dashboard
/configdiag          → Diagnose configuration
```

### Staff Commands

Trial reviewers can approve/deny applications with buttons in the trial channel.
Appeal reviewers can review appeals with buttons in the appeals channel.
Tournament admins can manage tournament brackets.
Event admins can create and manage events.

---

## 🔐 Security Best Practices

### Token Security
- ❌ Never commit token to Git
- ❌ Never share token in Discord
- ✅ Use environment variables
- ✅ Rotate token if exposed
- ✅ Use `.gitignore` to exclude config.json

**.gitignore**
```
config.json
data/botdata.db
*.log
__pycache__/
.env
```

### Bot Permissions
- Keep bot role below staff roles
- Restrict bot to appropriate channels
- Use role-based permission checks
- Log sensitive actions

### Role Hierarchy
```
@everyone (lowest)
    ↓
Guild Members
    ↓
Event Members
    ↓
Moderators (Einherjar)
    ↓
Admins (High Warden)
    ↓
Bot Role (should be here or above)
    ↓
@Owner (highest)
```

---

## 🐛 Troubleshooting

### Bot Won't Start

**Check 1: Python Version**
```bash
python --version  # Should be 3.8+
```

**Check 2: Dependencies**
```bash
pip install -r requirements.txt
```

**Check 3: Token**
```bash
python -c "from config import init_config; c = init_config('config.json'); print(c.get_token())"
```

### Commands Don't Work

```bash
# Check configuration
/configdiag

# Check permissions
/checkpermissions

# Check channels exist
/checkchanners

# Check bot has proper scopes
# Reinvite bot with proper scopes via OAuth2 URL
```

### Database Issues

```bash
# Check database exists and is readable
ls -la data/botdata.db

# Reset database (CAUTION: deletes all data)
rm data/botdata.db
python main.py  # Recreates on startup
```

### Help Menu Not Working

```bash
# Check help cog loaded
/help

# If error, check for duplicate "members" command
python -c "
import asyncio
from config import init_config
from discord.ext import commands
import discord

async def test():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix='*', intents=intents)
    
    cogs = ['config_manager', 'admin_tools', 'help', 'hall_info', 'trials', 
            'tournaments', 'events', 'appeals', 'logging', 'announcements', 
            'moderation', 'roles', 'server']
    
    for cog in cogs:
        try:
            await bot.load_extension(f'cogs.{cog}')
            print(f'✅ {cog}')
        except Exception as e:
            print(f'❌ {cog}: {e}')

asyncio.run(test())
"
```

---

## 📞 Support

### Common Solutions

| Issue | Solution |
|-------|----------|
| Bot offline | Check token, check network, check for errors in console |
| Commands 404 | Reinvite bot to guild with proper scopes, wait 1 hour for sync |
| No permissions | Check bot role position, check permissions in channel |
| Database locked | Stop bot, wait 5 seconds, restart |
| Memory leak | Check for unclosed database connections, restart bot daily |

### Logs

Check console output for errors:
```bash
# Run with output capture
python main.py > bot.log 2>&1 &

# View logs
tail -f bot.log
```

---

## ✨ Advanced Setup

### Multiple Guilds

Add multiple guild configurations to `config.json`:

```json
{
  "guilds": {
    "guild_id_1": { ... },
    "guild_id_2": { ... },
    "guild_id_3": { ... }
  }
}
```

### Custom Prefix

Each guild can have its own prefix:

```bash
*hall prefix *myprefix
```

Saves to database.

### Feature Toggles

Disable features per guild:

```json
"features": {
  "trials": true,
  "tournaments": false,
  "events": true,
  "appeals": true
}
```

### Custom Hall Info

Set hall-specific information:

```bash
/config hall_rules "..."
/config hall_lore "..."
```

---

## 📈 Maintenance

### Daily
- Monitor bot status
- Check for errors in logs
- Backup database

### Weekly
- Review action logs
- Check configuration health
- Update guild roles/channels if needed

### Monthly
- Clean up old logs
- Archive completed tournaments/events
- Review and rotate any sensitive data

### Yearly
- Review code for deprecated discord.py features
- Update dependencies
- Security audit

---

## 🎓 Training Staff

### For Trial Reviewers

1. Applications appear in #trials channel
2. Review application message
3. Click "Approve" or "Deny" button
4. Applicant automatically gets Trial Candidate role
5. Check `/viewtrials` to see all pending

### For Moderators

1. Use moderation commands to enforce rules
2. Warnings auto-logged
3. Mutes auto-expire after duration
4. All actions logged in #logs

### For Tournament Admins

1. `/tourneycreate` to start tournament
2. Share tournament ID with participants
3. Participants use `/tourneyjoin`
4. Use `/tourneystart` when ready
5. Use `/tourneyresult` to report matches
6. Winner announced via `/tourneyleaderboard`

### For Event Admins

1. `/eventcreate` to schedule event
2. Announcement posts to #events with RSVP buttons
3. Members click buttons to RSVP
4. `/eventlist` to see all events
5. `/eventrsvplist` to see who's attending

---

## 📊 Monitoring

### Check Bot Health

```bash
/adminstatus      # Full dashboard
/configdiag       # Configuration check
/checkpermissions # Permission audit
/checkchanners    # Channel verification
/checkroles       # Role hierarchy check
```

### Monitor Logs

```bash
/viewlogs [limit]      # Recent actions
/logaction [action]    # Manual log entry
```

---

## ✅ Deployment Checklist

Before going live:

- [ ] config.json configured with all required IDs
- [ ] All required channels created
- [ ] All required roles created
- [ ] Bot invited with proper scopes and permissions
- [ ] Bot role positioned correctly in hierarchy
- [ ] Test `/help` command
- [ ] Test `/adminstatus` dashboard
- [ ] Test one command from each cog
- [ ] Verify logs appearing in #logs
- [ ] Staff trained on commands
- [ ] Database backed up
- [ ] Ready to announce to members!

---

## 🎉 Next Steps

After setup:

1. **Welcome your members** with `/announce`
2. **Announce server rules** in #rules
3. **Post Hall information** using `/hallinfo`
4. **Create your first tournament** with `/tourneycreate`
5. **Schedule your first event** with `/eventcreate`
6. **Train your staff** on moderation commands

---

**Runekeeper is now ready to serve your Hall of the Slain! ⚔️**

For detailed command documentation, use `/help` in Discord.
