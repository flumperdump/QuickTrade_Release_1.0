# data_store.py

import os
import json

CONFIG_DIR = "config"
USER_PREFS_FILE = os.path.join(CONFIG_DIR, "user_prefs.json")
API_KEYS_FILE = os.path.join(CONFIG_DIR, "api_keys.json")

# Ensure the config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# ------------- USER PREFS --------------

def load_user_prefs():
    """Load user preferences from file."""
    if os.path.exists(USER_PREFS_FILE):
        with open(USER_PREFS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_user_prefs(prefs: dict):
    """Save user preferences to file."""
    with open(USER_PREFS_FILE, 'w') as f:
        json.dump(prefs, f, indent=4)

def get_enabled_exchanges():
    """Return list of exchanges enabled by user."""
    prefs = load_user_prefs()
    return prefs.get("enabled_exchanges", [])

def set_enabled_exchanges(exchanges: list):
    """Set the enabled exchanges and save."""
    prefs = load_user_prefs()
    prefs["enabled_exchanges"] = exchanges
    save_user_prefs(prefs)

def get_display_currency():
    prefs = load_user_prefs()
    return prefs.get("display_currency", "USD")

def set_display_currency(currency):
    prefs = load_user_prefs()
    prefs["display_currency"] = currency
    save_user_prefs(prefs)

def get_show_dust_filter():
    prefs = load_user_prefs()
    return prefs.get("show_dust", False)

def set_show_dust_filter(enabled: bool):
    prefs = load_user_prefs()
    prefs["show_dust"] = enabled
    save_user_prefs(prefs)

def get_theme_mode():
    prefs = load_user_prefs()
    return prefs.get("theme", "dark")

def set_theme_mode(mode: str):
    prefs = load_user_prefs()
    prefs["theme"] = mode
    save_user_prefs(prefs)

# ------------- RAW ACCESS UTILITY --------------

def delete_user_prefs():
    """Clear all user prefs (used for debugging or full reset)."""
    if os.path.exists(USER_PREFS_FILE):
        os.remove(USER_PREFS_FILE)
