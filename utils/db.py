import json
import os
import sqlite3
import threading
import time
import uuid

DB_PATH = os.path.join("data", "botdata.db")
_lock = threading.Lock()
_conn = None


def _get_connection():
    global _conn
    if _conn is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn


def init_db():
    conn = _get_connection()
    with _lock:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                guild_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                PRIMARY KEY(guild_id, key)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS staff (
                scope TEXT NOT NULL,
                role_type TEXT NOT NULL,
                user_id TEXT NOT NULL,
                PRIMARY KEY(scope, role_type, user_id)
            )
            """
        )
        # Trial Candidates
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trial_candidates (
                guild_id TEXT NOT NULL,
                trial_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                application_text TEXT NOT NULL,
                status TEXT NOT NULL,
                application_date INTEGER NOT NULL,
                approved_by TEXT,
                decision_date INTEGER,
                notes TEXT,
                message_id TEXT,
                PRIMARY KEY(guild_id, trial_id)
            )
            """
        )
        # Tournaments
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tournaments (
                guild_id TEXT NOT NULL,
                tournament_id TEXT NOT NULL,
                name TEXT NOT NULL,
                format TEXT NOT NULL,
                status TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                started_at INTEGER,
                ended_at INTEGER,
                PRIMARY KEY(guild_id, tournament_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tournament_teams (
                guild_id TEXT NOT NULL,
                tournament_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                team_name TEXT NOT NULL,
                members TEXT NOT NULL,
                joined_at INTEGER NOT NULL,
                PRIMARY KEY(guild_id, tournament_id, team_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tournament_matches (
                guild_id TEXT NOT NULL,
                tournament_id TEXT NOT NULL,
                match_id TEXT NOT NULL,
                team1_id TEXT NOT NULL,
                team2_id TEXT NOT NULL,
                winner_id TEXT,
                round INTEGER NOT NULL,
                completed INTEGER NOT NULL,
                PRIMARY KEY(guild_id, tournament_id, match_id)
            )
            """
        )
        # Events
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                guild_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                scheduled_for INTEGER NOT NULL,
                created_by TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                status TEXT NOT NULL,
                PRIMARY KEY(guild_id, event_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS event_rsvps (
                guild_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                PRIMARY KEY(guild_id, event_id, user_id)
            )
            """
        )
        # Appeals
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS appeals (
                guild_id TEXT NOT NULL,
                appeal_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                reviewed_by TEXT,
                decision_date INTEGER,
                notes TEXT,
                PRIMARY KEY(guild_id, appeal_id)
            )
            """
        )
        # Internal Logs
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS internal_logs (
                guild_id TEXT NOT NULL,
                log_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                target_id TEXT,
                details TEXT,
                timestamp INTEGER NOT NULL,
                PRIMARY KEY(guild_id, log_id)
            )
            """
        )
        # Moderation
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS warns (
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                moderator_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mutes (
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                end INTEGER NOT NULL,
                PRIMARY KEY(guild_id, user_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jails (
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                roles TEXT NOT NULL,
                channel_id TEXT,
                PRIMARY KEY(guild_id, user_id)
            )
            """
        )
        conn.commit()


def _execute(query, params=None):
    conn = _get_connection()
    with _lock:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor


def _fetchone(query, params=None):
    cursor = _execute(query, params)
    return cursor.fetchone()


def _fetchall(query, params=None):
    cursor = _execute(query, params)
    return cursor.fetchall()


def get_setting(guild_id, key, default=None):
    row = _fetchone(
        "SELECT value FROM settings WHERE guild_id = ? AND key = ?",
        (str(guild_id), key),
    )
    return row[0] if row else default


def set_setting(guild_id, key, value):
    _execute(
        "INSERT OR REPLACE INTO settings (guild_id, key, value) VALUES (?, ?, ?)",
        (str(guild_id), key, str(value)),
    )


def delete_setting(guild_id, key):
    _execute(
        "DELETE FROM settings WHERE guild_id = ? AND key = ?",
        (str(guild_id), key),
    )


def add_staff(role_type, user_id, scope="global"):
    _execute(
        "INSERT OR IGNORE INTO staff (scope, role_type, user_id) VALUES (?, ?, ?)",
        (scope, role_type, str(user_id)),
    )


def remove_staff(role_type, user_id, scope="global"):
    _execute(
        "DELETE FROM staff WHERE scope = ? AND role_type = ? AND user_id = ?",
        (scope, role_type, str(user_id)),
    )


def get_staff(scope="global"):
    return _fetchall(
        "SELECT role_type, user_id FROM staff WHERE scope = ?",
        (scope,),
    )


def add_warn(guild_id, user_id, moderator_id, reason, timestamp):
    _execute(
        "INSERT INTO warns (guild_id, user_id, moderator_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
        (str(guild_id), str(user_id), str(moderator_id), reason, int(timestamp)),
    )


def get_warns(guild_id, user_id):
    return _fetchall(
        "SELECT moderator_id, reason, timestamp FROM warns WHERE guild_id = ? AND user_id = ? ORDER BY timestamp ASC",
        (str(guild_id), str(user_id)),
    )


def clear_warns(guild_id, user_id):
    _execute(
        "DELETE FROM warns WHERE guild_id = ? AND user_id = ?",
        (str(guild_id), str(user_id)),
    )


def set_mute(guild_id, user_id, end):
    _execute(
        "INSERT OR REPLACE INTO mutes (guild_id, user_id, end) VALUES (?, ?, ?)",
        (str(guild_id), str(user_id), int(end)),
    )


def remove_mute(guild_id, user_id):
    _execute(
        "DELETE FROM mutes WHERE guild_id = ? AND user_id = ?",
        (str(guild_id), str(user_id)),
    )


def get_mute(guild_id, user_id):
    return _fetchone(
        "SELECT end FROM mutes WHERE guild_id = ? AND user_id = ?",
        (str(guild_id), str(user_id)),
    )


def get_due_mutes(now):
    return _fetchall(
        "SELECT guild_id, user_id FROM mutes WHERE end > 0 AND end <= ?",
        (int(now),),
    )


def save_jail(guild_id, user_id, roles, channel_id):
    _execute(
        "INSERT OR REPLACE INTO jails (guild_id, user_id, roles, channel_id) VALUES (?, ?, ?, ?)",
        (str(guild_id), str(user_id), json.dumps(roles), str(channel_id) if channel_id else None),
    )


def get_jail(guild_id, user_id):
    row = _fetchone(
        "SELECT roles, channel_id FROM jails WHERE guild_id = ? AND user_id = ?",
        (str(guild_id), str(user_id)),
    )
    if not row:
        return None
    return {
        "roles": json.loads(row[0]),
        "channel": int(row[1]) if row[1] else None,
    }


def remove_jail(guild_id, user_id):
    _execute(
        "DELETE FROM jails WHERE guild_id = ? AND user_id = ?",
        (str(guild_id), str(user_id)),
    )


# Trial Candidates
def add_trial(guild_id, user_id, application_text, message_id=None):
    import uuid
    trial_id = str(uuid.uuid4())
    _execute(
        "INSERT INTO trial_candidates (guild_id, trial_id, user_id, application_text, status, application_date, message_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(guild_id), trial_id, str(user_id), application_text, "pending", int(time.time()), str(message_id) if message_id else None),
    )
    return trial_id


def get_trial(guild_id, trial_id):
    return _fetchone(
        "SELECT * FROM trial_candidates WHERE guild_id = ? AND trial_id = ?",
        (str(guild_id), trial_id),
    )


def approve_trial(guild_id, trial_id, approved_by):
    _execute(
        "UPDATE trial_candidates SET status = ?, approved_by = ?, decision_date = ? WHERE guild_id = ? AND trial_id = ?",
        ("approved", str(approved_by), int(time.time()), str(guild_id), trial_id),
    )


def deny_trial(guild_id, trial_id, denied_by):
    _execute(
        "UPDATE trial_candidates SET status = ?, approved_by = ?, decision_date = ? WHERE guild_id = ? AND trial_id = ?",
        ("denied", str(denied_by), int(time.time()), str(guild_id), trial_id),
    )


def assign_gatekeeper(guild_id, trial_id, gatekeeper_id):
    _execute(
        "UPDATE trial_candidates SET approved_by = ?, status = ? WHERE guild_id = ? AND trial_id = ?",
        (str(gatekeeper_id), "in_progress", str(guild_id), trial_id),
    )


def reset_trial_assignment(guild_id, trial_id):
    _execute(
        "UPDATE trial_candidates SET approved_by = NULL, status = ?, decision_date = NULL WHERE guild_id = ? AND trial_id = ?",
        ("pending", str(guild_id), trial_id),
    )


def update_trial_message_id(guild_id, trial_id, message_id):
    _execute(
        "UPDATE trial_candidates SET message_id = ? WHERE guild_id = ? AND trial_id = ?",
        (str(message_id), str(guild_id), trial_id),
    )


def update_trial_status(guild_id, trial_id, status):
    _execute(
        "UPDATE trial_candidates SET status = ? WHERE guild_id = ? AND trial_id = ?",
        (status, str(guild_id), trial_id),
    )


def get_pending_trials(guild_id, user_id=None):
    if user_id:
        return _fetchall(
            "SELECT * FROM trial_candidates WHERE guild_id = ? AND user_id = ? AND status = ? ORDER BY application_date ASC",
            (str(guild_id), str(user_id), "pending"),
        )
    else:
        return _fetchall(
            "SELECT * FROM trial_candidates WHERE guild_id = ? AND status = ? ORDER BY application_date ASC",
            (str(guild_id), "pending"),
        )


def get_user_trials(guild_id, user_id):
    return _fetchall(
        "SELECT * FROM trial_candidates WHERE guild_id = ? AND user_id = ? ORDER BY application_date DESC",
        (str(guild_id), str(user_id)),
    )


def get_all_trials(guild_id):
    return _fetchall(
        "SELECT * FROM trial_candidates WHERE guild_id = ? ORDER BY application_date DESC",
        (str(guild_id),),
    )


# Tournaments
def create_tournament(guild_id, name, format_type, created_by):
    tournament_id = str(uuid.uuid4())
    _execute(
        "INSERT INTO tournaments (guild_id, tournament_id, name, format, status, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(guild_id), tournament_id, name, format_type, "registration", str(created_by), int(time.time())),
    )
    return tournament_id


def start_tournament(guild_id, tournament_id):
    _execute(
        "UPDATE tournaments SET status = ?, started_at = ? WHERE guild_id = ? AND tournament_id = ?",
        ("active", int(time.time()), str(guild_id), tournament_id),
    )


def end_tournament(guild_id, tournament_id):
    _execute(
        "UPDATE tournaments SET status = ?, ended_at = ? WHERE guild_id = ? AND tournament_id = ?",
        ("ended", int(time.time()), str(guild_id), tournament_id),
    )


def get_tournament(guild_id, tournament_id):
    return _fetchone(
        "SELECT * FROM tournaments WHERE guild_id = ? AND tournament_id = ?",
        (str(guild_id), tournament_id),
    )


def get_guild_tournaments(guild_id, status=None):
    if status:
        return _fetchall(
            "SELECT * FROM tournaments WHERE guild_id = ? AND status = ? ORDER BY created_at DESC",
            (str(guild_id), status),
        )
    return _fetchall(
        "SELECT * FROM tournaments WHERE guild_id = ? ORDER BY created_at DESC",
        (str(guild_id),),
    )


def get_tournament_team(guild_id, tournament_id, team_id):
    return _fetchone(
        "SELECT * FROM tournament_teams WHERE guild_id = ? AND tournament_id = ? AND team_id = ?",
        (str(guild_id), tournament_id, team_id),
    )


def get_tournament_teams(guild_id, tournament_id):
    return _fetchall(
        "SELECT * FROM tournament_teams WHERE guild_id = ? AND tournament_id = ? ORDER BY joined_at ASC",
        (str(guild_id), tournament_id),
    )


def get_tournament_team_matches(guild_id, tournament_id, team_id):
    return _fetchall(
        "SELECT * FROM tournament_matches WHERE guild_id = ? AND tournament_id = ? AND (team1_id = ? OR team2_id = ?) ORDER BY round ASC",
        (str(guild_id), tournament_id, team_id, team_id),
    )


# Tournament Teams
def register_tournament_team(guild_id, tournament_id, team_name, members):
    team_id = str(uuid.uuid4())
    members_json = json.dumps(members)
    _execute(
        "INSERT INTO tournament_teams (guild_id, tournament_id, team_id, team_name, members, joined_at) VALUES (?, ?, ?, ?, ?, ?)",
        (str(guild_id), tournament_id, team_id, team_name, members_json, int(time.time())),
    )
    return team_id


def get_team_in_tournament(guild_id, tournament_id, team_id):
    return _fetchone(
        "SELECT * FROM tournament_teams WHERE guild_id = ? AND tournament_id = ? AND team_id = ?",
        (str(guild_id), tournament_id, team_id),
    )


# Tournament Matches
def create_match(guild_id, tournament_id, team1_id, team2_id, round_num):
    match_id = str(uuid.uuid4())
    _execute(
        "INSERT INTO tournament_matches (guild_id, tournament_id, match_id, team1_id, team2_id, round, completed) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(guild_id), tournament_id, match_id, team1_id, team2_id, round_num, 0),
    )
    return match_id


def complete_match(guild_id, tournament_id, match_id, winner_id):
    _execute(
        "UPDATE tournament_matches SET winner_id = ?, completed = ? WHERE guild_id = ? AND tournament_id = ? AND match_id = ?",
        (winner_id, 1, str(guild_id), tournament_id, match_id),
    )


def record_tournament_match(guild_id, tournament_id, winning_team_id, losing_team_id, round_num):
    match_id = create_match(guild_id, tournament_id, winning_team_id, losing_team_id, round_num)
    complete_match(guild_id, tournament_id, match_id, winning_team_id)
    return match_id


def get_tournament_matches(guild_id, tournament_id):
    return _fetchall(
        "SELECT * FROM tournament_matches WHERE guild_id = ? AND tournament_id = ?",
        (str(guild_id), tournament_id),
    )


# Events
def create_event(guild_id, name, scheduled_for, created_by, description=""):
    event_id = str(uuid.uuid4())
    _execute(
        "INSERT INTO events (guild_id, event_id, name, description, scheduled_for, created_by, created_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(guild_id), event_id, name, description, int(scheduled_for), str(created_by), int(time.time()), "scheduled"),
    )
    return event_id


def close_event(guild_id, event_id):
    _execute(
        "UPDATE events SET status = ? WHERE guild_id = ? AND event_id = ?",
        ("closed", str(guild_id), event_id),
    )


def get_event(guild_id, event_id):
    return _fetchone(
        "SELECT * FROM events WHERE guild_id = ? AND event_id = ?",
        (str(guild_id), event_id),
    )


def get_guild_events(guild_id, status=None):
    if status:
        return _fetchall(
            "SELECT * FROM events WHERE guild_id = ? AND status = ? ORDER BY scheduled_for ASC",
            (str(guild_id), status),
        )
    return _fetchall(
        "SELECT * FROM events WHERE guild_id = ? ORDER BY scheduled_for ASC",
        (str(guild_id),),
    )


# Event RSVPs
def add_event_rsvp(guild_id, event_id, user_id, status):
    _execute(
        "INSERT OR REPLACE INTO event_rsvps (guild_id, event_id, user_id, status, timestamp) VALUES (?, ?, ?, ?, ?)",
        (str(guild_id), event_id, str(user_id), status, int(time.time())),
    )


def get_event_rsvps(guild_id, event_id, status=None):
    if status:
        return _fetchall(
            "SELECT * FROM event_rsvps WHERE guild_id = ? AND event_id = ? AND status = ? ORDER BY timestamp ASC",
            (str(guild_id), event_id, status),
        )
    return _fetchall(
        "SELECT * FROM event_rsvps WHERE guild_id = ? AND event_id = ? ORDER BY timestamp ASC",
        (str(guild_id), event_id),
    )


def rsvp_event(guild_id, event_id, user_id, status):
    add_event_rsvp(guild_id, event_id, user_id, status)


# Appeals
def submit_appeal(guild_id, user_id, reason):
    appeal_id = str(uuid.uuid4())
    _execute(
        "INSERT INTO appeals (guild_id, appeal_id, user_id, reason, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (str(guild_id), appeal_id, str(user_id), reason, "pending", int(time.time())),
    )
    return appeal_id


def approve_appeal(guild_id, appeal_id, reviewed_by, notes=""):
    _execute(
        "UPDATE appeals SET status = ?, reviewed_by = ?, decision_date = ?, notes = ? WHERE guild_id = ? AND appeal_id = ?",
        ("approved", str(reviewed_by), int(time.time()), notes, str(guild_id), appeal_id),
    )


def deny_appeal(guild_id, appeal_id, reviewed_by, notes=""):
    _execute(
        "UPDATE appeals SET status = ?, reviewed_by = ?, decision_date = ?, notes = ? WHERE guild_id = ? AND appeal_id = ?",
        ("denied", str(reviewed_by), int(time.time()), notes, str(guild_id), appeal_id),
    )


def get_appeal(guild_id, appeal_id):
    return _fetchone(
        "SELECT * FROM appeals WHERE guild_id = ? AND appeal_id = ?",
        (str(guild_id), appeal_id),
    )


def get_pending_appeals(guild_id):
    return _fetchall(
        "SELECT * FROM appeals WHERE guild_id = ? AND status = ? ORDER BY created_at ASC",
        (str(guild_id), "pending"),
    )


def get_user_pending_appeals(guild_id, user_id):
    return _fetchall(
        "SELECT * FROM appeals WHERE guild_id = ? AND user_id = ? AND status = ? ORDER BY created_at ASC",
        (str(guild_id), str(user_id), "pending"),
    )


def get_user_appeals(guild_id, user_id):
    return _fetchall(
        "SELECT * FROM appeals WHERE guild_id = ? AND user_id = ? ORDER BY created_at DESC",
        (str(guild_id), str(user_id)),
    )


def get_all_appeals(guild_id):
    return _fetchall(
        "SELECT * FROM appeals WHERE guild_id = ? ORDER BY created_at DESC",
        (str(guild_id),),
    )


# Internal Logs
def log_action(guild_id, action, actor_id, target_id=None, details=""):
    import uuid
    log_id = str(uuid.uuid4())[:8]
    _execute(
        "INSERT INTO internal_logs (guild_id, log_id, action, actor_id, target_id, details, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(guild_id), log_id, action, str(actor_id), str(target_id) if target_id else None, details, int(time.time())),
    )
    return log_id


def get_guild_logs(guild_id, limit=100):
    return _fetchall(
        "SELECT * FROM internal_logs WHERE guild_id = ? ORDER BY timestamp DESC LIMIT ?",
        (str(guild_id), limit),
    )


def get_logs(guild_id, limit=100):
    return get_guild_logs(guild_id, limit)
