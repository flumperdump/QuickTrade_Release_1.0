import json
import os

CONFIG_DIR = "config"
USER_PREFS_FILE = os.path.join(CONFIG_DIR, "user_prefs.json")
API_KEYS_FILE = os.path.join(CONFIG_DIR, "api_keys.json")

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_user_prefs():
    ensure_config_dir()
    if os.path.exists(USER_PREFS_FILE):
        with open(USER_PREFS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_prefs(prefs):
    ensure_config_dir()
    with open(USER_PREFS_FILE, 'w') as f:
        json.dump(prefs, f, indent=4)

def load_api_keys():
    ensure_config_dir()
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_api_keys(keys):
    ensure_config_dir()
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=4)

# ✅ Add this missing function
def load_enabled_exchanges():
    prefs = load_user_prefs()
    return prefs.get("enabled_exchanges", [])
