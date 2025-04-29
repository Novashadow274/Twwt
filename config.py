import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Telegram Config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# Paths
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)

# Load JSON files
def load_json(name):
    path = DATA_DIR / name
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load {name}: {e}")
        return {}

name_priority = load_json('name_priority.json')
HEADLINE_NAME = load_json('headline_name.json')
SOURCE_HASHTAG = load_json('source_hashtag.json')

# Account list
ACCOUNTS = sorted(
    [acc['username'] for acc in name_priority],
    key=lambda x: next(a['priority'] for a in name_priority if a['username'] == x),
    reverse=True
)

# State management
STATE_FILE = DATA_DIR / 'state.json'
