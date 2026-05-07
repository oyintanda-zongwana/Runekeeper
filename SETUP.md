# Runekeeper Setup Guide

## Prerequisites
- Python 3.8+
- Discord.py 2.3.2+
- sqlite3 (included with Python)

## Step 1: Install Dependencies

```bash
pip install discord.py python-dotenv
```

Or use the requirements.txt file:

```bash
pip install -r requirements.txt
```

## Step 2: Create Environment File

Create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_bot_token_here
OWNER_ID=your_user_id
```

**IMPORTANT**: Never commit `.env` to version control. It's already in `.gitignore`.

## Step 3: Configure Your Guild

1. Copy `config.example.json` to `config.json`:
```bash
cp config.example.json config.json
```

2. Edit `config.json` with your guild settings:
   - Replace `guild_id` with your server ID
   - Set all role IDs (use Discord's Developer Mode to copy role IDs)
   - Set all channel IDs
   - Configure which roles can review trials, appeals, etc.
   - Add your guild rules and lore

### Finding IDs in Discord
1. Enable Developer Mode in User Settings → Advanced → Developer Mode
2. Right-click any role/channel and select "Copy User ID" / "Copy Channel ID"

### Example Guild Configuration

```json
{
  "guilds": {
    "YOUR_GUILD_ID": {
      "name": "Hall of the Slain",
      "guild_roles": {
        "Gatekeeper": ROLE_ID,
        "Jarl": ROLE_ID,
        "Battle Herald": ROLE_ID,
        "Chronicler of the Hall": ROLE_ID,
        "Keeper of the Trials": ROLE_ID,
        "Arena Champion": ROLE_ID
      },
      "trial_role_id": ROLE_ID,
      "trial_channel": CHANNEL_ID,
      "tournament_channel": CHANNEL_ID,
      "event_channel": CHANNEL_ID,
      "appeals_channel": CHANNEL_ID,
      "log_channel": CHANNEL_ID,
      "trial_reviewers": [ROLE_ID1, ROLE_ID2],
      "appeal_reviewers": [ROLE_ID1, ROLE_ID2],
      "tournament_admins": [ROLE_ID1, ROLE_ID2],
      "event_admins": [ROLE_ID1, ROLE_ID2],
      "tournament_winner_role": ROLE_ID,
      "tournament_finalist_role": ROLE_ID,
      "trial_expiration_days": 30,
      "features": {
        "trials": true,
        "tournaments": true,
        "events": true,
        "appeals": true
      },
      "hall_info": {
        "rules": "Your guild rules here",
        "lore": "Your guild lore/background here"
      }
    }
  }
}
```

## Step 4: Create Required Channels

In your Discord server, create the following channels:
- `trial-submissions` - For trial candidate submissions
- `tournaments` - For tournament announcements
- `events` - For event announcements
- `appeals` - For appeal submissions
- `logs` - For internal action logs

Make sure Runekeeper has permission to post in these channels.

## Step 5: Create Required Roles

Create roles for your guild (you can customize the names):
- Gatekeeper (Admin role)
- Jarl (Leadership)
- Battle Herald (Moderator)
- Chronicler of the Hall (Role manager)
- Keeper of the Trials (Trial reviewer)
- Arena Champion (Tournament admin)
- Trial Candidate (Assigned automatically to approved candidates)
- Tournament Champion (Assigned to tournament winners)
- Tournament Finalist (Optional - assigned to finalists)

## Step 6: Run the Bot

```bash
python main.py
```

You should see:
```
✅ Loaded hall_info
✅ Loaded trials
✅ Loaded tournaments
✅ Loaded events
✅ Loaded appeals
✅ Loaded logging
✅ Loaded announcements
✅ Synced commands to test guild YOUR_GUILD_ID
✅ RunekeeperBot#0000 is ready
```

## Troubleshooting

### Bot won't start
- Check that `DISCORD_TOKEN` is set correctly in `.env`
- Verify Python 3.8+ is installed
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Commands not showing up
- Make sure the bot has the `applications.commands` scope in Discord Developer Portal
- Run `/sync` or restart the bot to sync commands
- Commands are synced to the test guild specified in config.json

### No permission errors
- Verify the role/channel IDs in config.json are correct
- Make sure Runekeeper has required permissions in those channels
- Check that you've assigned the correct reviewer/admin roles to users

### Database errors
- The database is created automatically in the bot's directory as `runekeeper.db`
- If you need to reset it, just delete `runekeeper.db` and restart the bot

## First Commands to Try

After setup:
1. `/hallinfo` - Verify guild info displays correctly
2. `/applyfortrial` - Test trial system
3. `/tourneycreate` - Test tournament system
4. `/eventcreate` - Test event system
5. `/announce` - Test announcements

## Support

If issues occur:
1. Check the console output for error messages
2. Verify all role and channel IDs are correct
3. Make sure the bot has proper permissions
4. Check Discord's API status at https://status.discord.com

## Security Checklist

- [ ] Bot token is in `.env` file (not config.json)
- [ ] `.env` is in `.gitignore`
- [ ] Never share `.env` file
- [ ] Run on a secure machine
- [ ] Use strong role permissions
- [ ] Regularly check action logs

## Production Deployment

For production, consider:
1. Using a dedicated bot account
2. Running on a VPS or cloud platform
3. Using process manager (PM2, systemd)
4. Setting up backups of the SQLite database
5. Monitoring bot uptime and performance
6. Using a reverse proxy if needed
