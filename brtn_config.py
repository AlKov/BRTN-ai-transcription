import json
import os

CONFIG_PATH = os.path.expanduser("~/.brtn_config.json")

DEFAULT_CONFIG = {
    "start_trigger": "hold",
    "end_trigger": "release",
    "start_key_code": 63, # Fn key
    "start_key_name": "Fn",
    "end_key_code": 63,
    "end_key_name": "Fn",
    "show_icon": True,
    "max_record_seconds": 27, # 90% of ~30s whisper window
    "theme_color_primary": "#EA6363",
    "theme_color_text": "#565656",
    "theme_color_accent": "#212121"
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, 'r') as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    except:
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
