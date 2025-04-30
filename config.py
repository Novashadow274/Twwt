import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram bot settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Nitter URL (using Nitter-based scraping)
NITTER_URL = os.getenv("NITTER_URL")
