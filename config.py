import os
from dotenv import load_dotenv

load_dotenv()  # load .env file

BOT_TOKEN       = os.getenv("BOT_TOKEN")           # Telegram bot token
GROUP_ID        = int(os.getenv("GROUP_ID", 0))    # Target group chat ID
OWNER_ID        = int(os.getenv("GROUP_OWNER_ID", 0)) # Group owner's user ID
LOG_CHANNEL_ID  = int(os.getenv("LOG_CHANNEL_ID", 0)) # Log channel ID (private group)
WEBHOOK_URL     = os.getenv("WEBHOOK_URL")         # Public URL for webhooks (e.g. https://myapp.onrender.com)

if not BOT_TOKEN or not GROUP_ID or not OWNER_ID or not LOG_CHANNEL_ID or not WEBHOOK_URL:
    raise ValueError("Configuration incomplete. Please set BOT_TOKEN, GROUP_ID, GROUP_OWNER_ID, LOG_CHANNEL_ID, WEBHOOK_URL in .env")
