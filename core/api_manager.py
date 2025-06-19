# api_manager.py
import os
import json

CONFIG_DIR = "config"
API_KEYS_FILE = os.path.join(CONFIG_DIR, "api_keys.json")

# Ensures the config folder exists
os.makedirs(CONFIG_DIR, exist_ok=True)

def load_api_keys():
    """Load API keys from the local JSON file."""
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_api_keys(api_data):
    """Save API keys to the local JSON file."""
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(api_data, f, indent=2)

def add_subaccount(exchange, subaccount_name=None):
    """Add a new subaccount under the given exchange."""
    api_data = load_api_keys()
    if exchange not in api_data:
        api_data[exchange] = {}

    # Create a default subaccount name if none provided
    if not subaccount_name:
        existing = api_data[exchange].keys()
        count = len(existing) + 1
        subaccount_name = f"Sub{count}"

    api_data[exchange][subaccount_name] = {"api_key": "", "api_secret": ""}
    save_api_keys(api_data)
    return subaccount_name

def delete_subaccount(exchange, subaccount):
    """Delete a subaccount from the given exchange."""
    api_data = load_api_keys()
    if exchange in api_data and subaccount in api_data[exchange]:
        del api_data[exchange][subaccount]
        if not api_data[exchange]:
            del api_data[exchange]  # Clean up if empty
        save_api_keys(api_data)

def update_api_credentials(exchange, subaccount, api_key, api_secret):
    """Update the credentials for a given subaccount."""
    api_data = load_api_keys()
    if exchange not in api_data:
        api_data[exchange] = {}

    api_data[exchange][subaccount] = {
        "api_key": api_key.strip(),
        "api_secret": api_secret.strip()
    }
    save_api_keys(api_data)

def get_api_credentials(exchange, subaccount):
    """Get API credentials for a specific subaccount."""
    api_data = load_api_keys()
    return api_data.get(exchange, {}).get(subaccount, None)
