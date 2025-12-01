import json
import os
from typing import Any, Dict

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get backend directory (config.py is at backend/src/vello/core/config.py)
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
_config_dir = os.path.join(_backend_dir, "config")

# Database settings
# Default to vello.db in the backend directory
_default_db_path = os.path.join(_backend_dir, "vello.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_default_db_path}")

# Email settings
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp")  # smtp, sendgrid, ses
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "t")

# Provider-specific settings (for future use)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
AWS_SES_REGION = os.getenv("AWS_SES_REGION", "us-east-1")


# Debug settings
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
IN_MEMORY_DB = os.getenv("IN_MEMORY_DB", "False").lower() in ("true", "1", "t")

# Configuration file loader (must be defined before use)
def load_config_file(filename: str) -> Dict[str, Any]:
    """
    Load a JSON configuration file from the config directory.
    Returns empty dict if file doesn't exist.

    Args:
        filename: Name of the config file (e.g., "warmup.json")

    Returns:
        Dictionary with config values
    """
    config_path = os.path.join(_config_dir, filename)
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file {filename}: {e}")
            return {}
    return {}


# Automation/System Configuration
# Load from JSON file, allow .env overrides
_automation_config = load_config_file("automation.json")
AUTO_ACT_ON_RESPONSE = os.getenv("AUTO_ACT_ON_RESPONSE", str(_automation_config.get("auto_act_on_response", False))).lower() in ("true", "1", "t")
AUTO_CLASSIFY_RESPONSES = os.getenv("AUTO_CLASSIFY_RESPONSES", str(_automation_config.get("auto_classify_responses", True))).lower() in ("true", "1", "t")
AUTO_UNSUBSCRIBE_ON_REQUEST = os.getenv("AUTO_UNSUBSCRIBE_ON_REQUEST", str(_automation_config.get("auto_unsubscribe_on_request", True))).lower() in ("true", "1", "t")
AUTO_ROTATE_INBOXES = os.getenv("AUTO_ROTATE_INBOXES", str(_automation_config.get("auto_rotate_inboxes", False))).lower() in ("true", "1", "t")
AUTO_ADJUST_SEND_TIMES = os.getenv("AUTO_ADJUST_SEND_TIMES", str(_automation_config.get("auto_adjust_send_times", False))).lower() in ("true", "1", "t")
AUTO_PAUSE_RISKY_CAMPAIGNS = os.getenv("AUTO_PAUSE_RISKY_CAMPAIGNS", str(_automation_config.get("auto_pause_risky_campaigns", True))).lower() in ("true", "1", "t")


# Warmup Manager Configuration
# Load from JSON file, allow .env overrides
_warmup_config = load_config_file("warmup.json")
WARMUP_ENABLED = os.getenv("WARMUP_ENABLED", str(_warmup_config.get("enabled", False))).lower() in ("true", "1", "t")
WARMUP_START_VOLUME = int(os.getenv("WARMUP_START_VOLUME", _warmup_config.get("start_volume", 5)))
WARMUP_MAX_VOLUME = int(os.getenv("WARMUP_MAX_VOLUME", _warmup_config.get("max_volume", 50)))
WARMUP_DAILY_INCREASE = int(os.getenv("WARMUP_DAILY_INCREASE", _warmup_config.get("daily_increase", 2)))
WARMUP_DURATION_DAYS = int(os.getenv("WARMUP_DURATION_DAYS", _warmup_config.get("warmup_duration_days", 30)))
WARMUP_MIN_DELAY_MINUTES = int(os.getenv("WARMUP_MIN_DELAY_MINUTES", _warmup_config.get("min_delay_minutes", 60)))
WARMUP_MAX_DELAY_MINUTES = int(os.getenv("WARMUP_MAX_DELAY_MINUTES", _warmup_config.get("max_delay_minutes", 240)))
WARMUP_REPLY_RATE_TARGET = float(os.getenv("WARMUP_REPLY_RATE_TARGET", _warmup_config.get("reply_rate_target", 0.15)))
WARMUP_BOUNCE_RATE_THRESHOLD = float(os.getenv("WARMUP_BOUNCE_RATE_THRESHOLD", _warmup_config.get("bounce_rate_threshold", 0.05)))
WARMUP_SPAM_COMPLAINT_THRESHOLD = float(os.getenv("WARMUP_SPAM_COMPLAINT_THRESHOLD", _warmup_config.get("spam_complaint_threshold", 0.01)))
