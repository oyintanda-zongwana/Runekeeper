import json
import os
from typing import Optional, Dict, Any

# Global config instance
config: Optional[Config] = None

class Config:
    """Runekeeper configuration handler."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load configuration from JSON file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
        else:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
    
    def save(self):
        """Save configuration to JSON file."""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)
    
    # Bot Settings
    def get_token(self) -> str:
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            token = self.config.get("token")
        if not token or token == "Token here":
            raise ValueError("Discord token not configured")
        return token
    
    def get_owner_id(self) -> int:
        owner = os.getenv("OWNER_ID")
        if not owner:
            owner = self.config.get("owner_id")
        return int(owner) if owner else 0
    
    def get_guild_id(self) -> Optional[int]:
        guild = self.config.get("guild_id")
        return int(guild) if guild else None
    
    def get_application_id(self) -> Optional[int]:
        app = self.config.get("application_id")
        return int(app) if app else None
    
    # Guild Settings
    def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get all guild-specific settings."""
        guilds = self.config.get("guilds", {})
        return guilds.get(str(guild_id), {})
    
    def get_guild_setting(self, guild_id: int, key: str, default: Any = None) -> Any:
        """Get a specific guild setting."""
        settings = self.get_guild_settings(guild_id)
        return settings.get(key, default)
    
    # Guild Roles Configuration
    def get_guild_roles(self, guild_id: int) -> Dict[str, int]:
        """Get configured guild roles for Hall positions."""
        settings = self.get_guild_settings(guild_id)
        return settings.get("guild_roles", {})
    
    def get_trial_role_id(self, guild_id: int) -> Optional[int]:
        """Get Trial Candidate role ID."""
        role_id = self.get_guild_setting(guild_id, "trial_role_id")
        return int(role_id) if role_id else None
    
    # Channel Configuration
    def get_trial_submissions_channel(self, guild_id: int) -> Optional[int]:
        """Get channel for trial applications."""
        channel_id = self.get_guild_setting(guild_id, "trial_channel")
        return int(channel_id) if channel_id else None
    
    def get_tournament_channel(self, guild_id: int) -> Optional[int]:
        """Get tournament announcements channel."""
        channel_id = self.get_guild_setting(guild_id, "tournament_channel")
        return int(channel_id) if channel_id else None
    
    def get_event_channel(self, guild_id: int) -> Optional[int]:
        """Get event announcements channel."""
        channel_id = self.get_guild_setting(guild_id, "event_channel")
        return int(channel_id) if channel_id else None
    
    def get_log_channel(self, guild_id: int) -> Optional[int]:
        """Get internal logging channel."""
        channel_id = self.get_guild_setting(guild_id, "log_channel")
        return int(channel_id) if channel_id else None
    
    def get_appeals_channel(self, guild_id: int) -> Optional[int]:
        """Get appeals submission channel."""
        channel_id = self.get_guild_setting(guild_id, "appeals_channel")
        return int(channel_id) if channel_id else None
    
    # Permissions Configuration
    def get_trial_reviewers(self, guild_id: int) -> list:
        """Get role IDs that can review trials."""
        reviewers = self.get_guild_setting(guild_id, "trial_reviewers", [])
        return [int(r) for r in reviewers]
    
    def get_appeal_reviewers(self, guild_id: int) -> list:
        """Get role IDs that can review appeals."""
        reviewers = self.get_guild_setting(guild_id, "appeal_reviewers", [])
        return [int(r) for r in reviewers]
    
    def get_tournament_admins(self, guild_id: int) -> list:
        """Get role IDs that can manage tournaments."""
        admins = self.get_guild_setting(guild_id, "tournament_admins", [])
        return [int(a) for a in admins]
    
    def get_event_admins(self, guild_id: int) -> list:
        """Get role IDs that can manage events."""
        admins = self.get_guild_setting(guild_id, "event_admins", [])
        return [int(a) for a in admins]
    
    # Reward Roles
    def get_tournament_winner_role(self, guild_id: int) -> Optional[int]:
        """Get role assigned to tournament winners."""
        role_id = self.get_guild_setting(guild_id, "tournament_winner_role")
        return int(role_id) if role_id else None
    
    def get_tournament_finalist_role(self, guild_id: int) -> Optional[int]:
        """Get role assigned to finalists."""
        role_id = self.get_guild_setting(guild_id, "tournament_finalist_role")
        return int(role_id) if role_id else None
    
    # Feature Toggles
    def is_feature_enabled(self, guild_id: int, feature: str) -> bool:
        """Check if a feature is enabled."""
        features = self.get_guild_setting(guild_id, "features", {})
        return features.get(feature, True)
    
    def get_trial_expiration_days(self, guild_id: int) -> int:
        """Get days until trial expires (0 = disabled)."""
        days = self.get_guild_setting(guild_id, "trial_expiration_days", 0)
        return int(days)
    
    # Hall Information
    def get_hall_info(self, guild_id: int) -> Dict[str, Any]:
        """Get Hall information (rules, lore, etc.)."""
        settings = self.get_guild_settings(guild_id)
        return settings.get("hall_info", {})
    
    def get_hall_rules(self, guild_id: int) -> str:
        """Get Hall rules text."""
        info = self.get_hall_info(guild_id)
        return info.get("rules", "No rules configured.")
    
    def get_hall_lore(self, guild_id: int) -> str:
        """Get Hall lore text."""
        info = self.get_hall_info(guild_id)
        return info.get("lore", "No lore configured.")


# Global config instance
config = None

def init_config(config_path: str = "config.json") -> Config:
    """Initialize global config."""
    global config
    config = Config(config_path)
    return config

def get_config() -> Config:
    """Get global config instance."""
    global config
    if config is None:
        config = Config()
    return config
