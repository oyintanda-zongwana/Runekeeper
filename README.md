# RUNEKEEPER

RuneKeeper is a multipurpose Discord bot built for the Hall of the Slain community.
It provides moderation tools, role management, server utilities, guild settings, and event systems.


## Quick Start

1. Copy `config.example.json` to `config.json`.
2. Set your bot token:
   - in `config.json` as the `token` field, or
   - with the `DISCORD_TOKEN` environment variable.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

The bot is configured through `config.json`.
Key settings include:
- `token`: Discord bot token
- `prefix`: default command prefix
- `owner_id`, `application_id`, `guild_id`: Discord IDs used by the bot
- `guilds`: per-guild settings for roles, channels, reviewers, and enabled features

Update the IDs and guild settings to match your server before running the bot.

## Main Features

- Command prefix support per guild
- Moderation commands: warn, mute, kick, ban, jail, purge, slowmode, lock/unlock
- Role management: create, delete, assign, remove, rename, recolor, move, hoist, mentionable
- Server utilities: info, avatar, banner, members, boosts, channels, roles count
- Trial, tournament, event, and appeal systems
- Announcement and logging tools
- SQLite persistence for warns, mutes, staff roles, jail state, and settings

## Available Commands

### General
- `help` / `help <command>`: view command categories and syntax
- `serverinfo` / `si`: show guild information
- `userinfo` / `ui`: show user information
- `avatar` / `av`: show a user's avatar
- `banner`: show a user's banner
- `servericon`: show the server icon
- `membercount` / `mc`: show the number of members
- `boosts`: show server boost status
- `rolesnumber`: show total roles count
- `channels`: show channel counts
- `vcs`: show voice channel statistics

### Moderation (Mod+)
- `snipe` / `sn` / `s`: show the last deleted message
- `editsnipe` / `es`: show the last edited message
- `warn` / `w`: warn a user
- `warnings` / `ws`: view a user's warnings
- `clearwarns` / `cw`: clear a user's warnings
- `mute` / `m`: mute a user for a duration
- `unmute` / `um`: unmute a user
- `nickname` / `nick`: change or reset a user's nickname
- `say` / `echo`: make the bot send a message

### Moderation (Admin+)
- `purge` / `clear` / `clean` / `prune`: bulk delete messages
- `slowmode` / `sm`: set channel slowmode
- `lock`: lock a channel for @everyone
- `unlock`: unlock a channel for @everyone
- `kick` / `k`: kick a user
- `ban` / `b`: ban a user
- `jail` / `j`: jail a user in a private cell channel
- `unjail` / `uj`: release a jailed user

### Staff Management
- `addmod` / `am`: promote a user to Mod staff
- `removemod` / `rm`: demote Mod staff
- `addadmin` / `aa`: promote a user to Admin staff
- `removeadmin` / `ra`: demote Admin staff
- `addowner` / `ao`: promote a user to Owner staff
- `removeowner` / `ro`: demote Owner staff
- `staffs` / `staff`: list configured staff members

### Roles (Public)
- `roleinfo` / `ri`: show details for a role
- `rolelist` / `roles` / `listroles`: list server roles by position

### Roles (Admin+)
- `createrole` / `cr` / `rcreate`: create a new role
- `deleterole` / `dr` / `rdelete`: delete a role
- `giverole` / `gr` / `give`: give a role to a member
- `removerole` / `rr` / `take`: remove a role from a member
- `renamerole` / `rn` / `rrename`: rename a role
- `colorrole` / `rc` / `rcolor`: change a role color
- `roleposition` / `rp` / `move`: move a role position
- `rolehoist` / `rh` / `hoist`: toggle role hoist
- `rolementionable` / `rmen` / `mentionable`: toggle @mentionability

### Server Settings
- `prefix`: show the current command prefix
- `setprefix`: set the guild command prefix
- `setlog`: set the moderation log channel
- `setwelcome`: set the welcome message channel
- `setgoodbye`: set the goodbye message channel

### Slash / App Commands
- `help` (slash): browse available commands
- `setlog`, `setwelcome`, `setgoodbye`
- `serverinfo`, `userinfo`, `avatar`, `banner`, `servericon`, `membercount`, `boosts`, `rolesnumber`, `channels`, `vcs`
- `createrole`, `deleterole`, `giverole`, `removerole`, `renamerole`, `rolecolor`, `roleposition`, `rolehoist`, `rolementionable`, `roleinfo`, `rolelist`
- `config`: manage guild configuration
- `configdiag`: check configuration health
- `announce`, `celebratevictory`, `themedmessage`
- `viewlogs`, `logaction`
- `checkpermissions`, `checkroles`, `checkchannels`, `adminstatus`
- `hallinfo`, `members`
- `applyfortrial`, `assign_gatekeeper`, `trialstatus`, `viewtrials`, `deletetrial`, `trialqueue`
- `tourneycreate`, `deletealltourneys`, `managetourney`, `tourneyjoin`, `tourneystart`, `tourneyresult`, `tourneyleaderboard`, `tourneys`, `tourneylist`, `tourneyview`
- `eventcreate`, `deleteallevents`, `eventrsvp`, `eventlist`, `events`, `eventview`, `eventrsvplist`
- `appeal`, `appealstatus`, `viewappeals`

### Systems and Guild Features
- Trial applications and approvals
- Tournament creation, joining, results, and leaderboards
- Event creation, RSVPs, reminders, and event browsing
- Appeals submission and review workflow
- Hall info and membership display
- Action logging and announcement tools

## Repository Structure

- `main.py` — bot startup
- `config.py` — configuration loader
- `config.example.json` — sample settings
- `cogs/` — command modules and event handlers
- `utils/` — helpers and database support
- `requirements.txt` — dependencies

## Contributor Notes

- Use `help` in Discord to browse available commands and syntax.
- Inspect `cogs/` to learn implementation and permissions.
- Keep `config.example.json` as a template; use `config.json` locally.
- When adding commands, add them to the appropriate cog and preserve existing permission logic.

## Authors

- [@Asher-09](https://www.github.com/Asher-09)
- [@oyintanda-zongwana](https://github.com/oyintanda-zongwana)

## Tech Stack

- Python
- Discord.py
- OS
- JSON
