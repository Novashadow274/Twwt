# config.py
# Load configuration, mappings, and environment variables.

import os
import json
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_ADMIN_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# --- Load name_priority.json ---
try:
    with open('name_priority.json', 'r') as f:
        name_priority = json.load(f)
    print(f"[DEBUG] Loaded name_priority.json with {len(name_priority)} entries.")
except Exception as e:
    print(f"[ERROR] Could not load name_priority.json: {e}")
    name_priority = []

name_priority_sorted = sorted(name_priority, key=lambda x: x.get("priority", 0))
ACCOUNTS = [entry["username"] for entry in name_priority_sorted]

# --- Load headline_name.json ---
try:
    with open('headline_name.json', 'r') as f:
        HEADLINE_NAME = json.load(f)
    print(f"[DEBUG] Loaded headline_name.json with {len(HEADLINE_NAME)} entries.")
except Exception as e:
    print(f"[ERROR] Could not load headline_name.json: {e}")
    HEADLINE_NAME = {}

# --- Load source_hashtag.json ---
try:
    with open('source_hashtag.json', 'r') as f:
        SOURCE_HASHTAG = json.load(f)
    print(f"[DEBUG] Loaded source_hashtag.json with {len(SOURCE_HASHTAG)} entries.")
except Exception as e:
    print(f"[ERROR] Could not load source_hashtag.json: {e}")
    SOURCE_HASHTAG = {}

# --- Validate account mappings ---
for username in ACCOUNTS:
    if username not in HEADLINE_NAME:
        print(f"[WARNING] No headline name for '{username}' in headline_name.json.")
    if username not in SOURCE_HASHTAG:
        print(f"[WARNING] No source hashtag for '{username}' in source_hashtag.json.")

# --- Other config ---
STATE_FILE = 'state.json'

# --- Optional: Print final account list ---
print(f"[DEBUG] Final account priority list: {ACCOUNTS}")
