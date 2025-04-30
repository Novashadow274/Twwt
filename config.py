import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
NITTER_INSTANCE = os.getenv("NITTER_INSTANCE", "https://nitter.net")
