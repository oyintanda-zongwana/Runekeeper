# Runekeeper Quick Reference

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your token
echo DISCORD_TOKEN=your_token_here > .env

# 3. Configure config.json
cp config.example.json config.json
# Edit config.json with your guild IDs, roles, channels

# 4. Run the bot
python main.py
```

## 📋 Command Cheat Sheet

### Trials (`/applyfortrial`, `/trialstatus`, `/viewtrials`)
```
/applyfortrial reason:"I wish to join the Hall"
/trialstatus
/viewtrials status:pending  # Reviewers only
```

### Tournaments (`/tourneycreate`, `/tourneyjoin`, `/tourneystart`, `/tourneyresult`, `/tourneyleaderboard`)
```
/tourneycreate name:"Summer Clash" format:1v1
/tourneyjoin tournament_id:1 team_name:"Solo Warriors"
/tourneystart tournament_id:1
/tourneyresult tournament_id:1 winner_team:1 loser_team:2 round_num:1
/tourneyleaderboard tournament_id:1
```

### Events (`/eventcreate`, `/eventrsvp`, `/eventlist`, `/eventrsvplist`)
```
/eventcreate name:"Guild Gathering" description:"All welcome" hours_from_now:24
/eventrsvp event_id:1 status:attending
/eventlist
/eventrsvplist event_id:1
```

### Appeals (`/appeal`, `/appealstatus`, `/viewappeals`)
```
/appeal reason:"I was wrongly banned, please review"
/appealstatus
/viewappeals status:pending  # Reviewers only
```

### Hall Info (`/hallinfo`, `/members`)
```
/hallinfo section:all
/hallinfo section:rules
/hallinfo section:roles
/members
```

### Logging (`/viewlogs`, `/logaction`)
```
/viewlogs action:all limit:20
/viewlogs action:trial_approved limit:10
/logaction action:"manual_action" target:@user details:"reason"
```

### Announcements (`/announce`, `/celebratevictory`, `/themedmessage`)
```
/announce title:"New Event" message:"Tournament starts tomorrow" color:gold
/celebratevictory winner:@user achievement:"Won Summer Tournament"
/themedmessage title:"Victory" content:"Amazing performance!" theme:tournament
```

## 🎨 Colors Available
- `gold` - Primary theme color
- `blood` - Tournament/combat
- `rune` - Magic/events
- `black` - Dark/serious
- `white` - Light/positive
- `steel` - Neutral/info

## 🔑 Config Template

```json
{
  "guilds": {
    "YOUR_GUILD_ID": {
      "trial_reviewers": [ROLE_ID1, ROLE_ID2],
      "appeal_reviewers": [ROLE_ID1, ROLE_ID2],
      "tournament_admins": [ROLE_ID1, ROLE_ID2],
      "event_admins": [ROLE_ID1, ROLE_ID2],
      "trial_channel": CHANNEL_ID,
      "tournament_channel": CHANNEL_ID,
      "event_channel": CHANNEL_ID,
      "appeals_channel": CHANNEL_ID
    }
  }
}
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Commands not showing | Restart bot, run `/sync` |
| No permissions | Check role IDs in config.json |
| Bot can't post | Give bot Send Messages permission |
| Database locked | Restart bot, check file permissions |
| Token invalid | Check .env file, verify token is correct |

## 📚 Documentation Files

- `README_RUNEKEEPER.md` - Full feature documentation
- `SETUP.md` - Complete setup guide
- `IMPLEMENTATION_SUMMARY.md` - What was built
- `QUICKSTART.md` - This file

## 🎯 System Priorities

**⭐⭐⭐ HIGHEST**: Tournament System
- The core system for Hall of the Slain
- Most feature-rich
- Central to guild competition

**⭐⭐ HIGH**: Trial & Appeals Systems
- New member onboarding
- Conflict resolution
- Important for governance

**⭐ MEDIUM**: Events & Announcements
- Community engagement
- Information sharing

**⭐ STANDARD**: Logging & Hall Info
- Administrative tools
- Reference information

## 📞 Support Resources

- Check Discord.py docs: https://discordpy.readthedocs.io
- Check Discord API docs: https://discord.com/developers/docs
- Bot status: https://status.discord.com

## 🔐 Security Reminder

```bash
# Good ✅
DISCORD_TOKEN=your_token_here  # In .env

# Bad ❌
"token": "your_token_here"     # In config.json
```

Always keep tokens in `.env` file!

## 📊 Database Locations

- Database file: `runekeeper.db` (auto-created)
- Backups: Create manually from `runekeeper.db`
- Reset: Delete `runekeeper.db` and restart bot

## ⚙️ Advanced Config

```json
{
  "trial_expiration_days": 30,
  "features": {
    "trials": true,
    "tournaments": true,
    "events": true,
    "appeals": true
  },
  "hall_info": {
    "rules": "Your guild rules",
    "lore": "Your guild story"
  }
}
```

## 🎪 Testing Checklist

Before going live:
- [ ] All commands respond
- [ ] Permission checks work
- [ ] Roles assign correctly
- [ ] Database persists data
- [ ] Embeds display properly
- [ ] Error messages are clear
- [ ] Bot stays online consistently

---

**Ready to lead the Hall of the Slain! ⚔️**
