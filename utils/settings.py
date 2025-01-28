import json
import os

SETTINGS_FILE = "settings.json"
ENABLE_MAPPING_FILE = "./config/mods/enabled_mods.json"

def load_settings():
    """Load settings from the JSON file or return default settings."""
    default_settings = {
        "general": {"localization": "en"},
        "paths": {
            "game_executable": "",
            "migoto_executable": "",
            "migoto_mod_folder": "",
            "log_directory": "logs",
        },
        "user_preferences": {
            "use_3dmigoto": False,
            "toolbar_position": 1,
            "style_dir": "styles",
            "stylesheet": ""
        },
        "3dmigoto": {
            "analyse_options": True
        }
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as file:
                return {**default_settings, **json.load(file)}
        except Exception as e:
            print(f"Error loading settings: {e}")
    return default_settings

def save_settings(settings):
    """Save settings to the JSON file."""
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)

def load_enable_mapping():
    """Load the enable mapping from the JSON file."""
    if os.path.exists(ENABLE_MAPPING_FILE):
        try:
            with open(ENABLE_MAPPING_FILE, "r") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading enable mapping: {e}")
    return {}

def save_enable_mapping(enable_mapping):
    """Save the enable mapping to the JSON file."""
    try:
        with open(ENABLE_MAPPING_FILE, "w") as file:
            json.dump(enable_mapping, file, indent=4)
    except Exception as e:
        print(f"Error saving enable mapping: {e}")
