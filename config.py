# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))          # Telegram ID of bot owner
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))    # Private channel ID for logging
GROUP_ID = int(os.getenv("GROUP_ID", "0"))          # (Optional) group ID to restrict in

# Permissions: if needed
ADMIN_IDS = set(int(x) for x in os.getenv("ADMIN_IDS", "").split()) 
