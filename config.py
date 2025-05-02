import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required values
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Optional values
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))    # Channel ID for logging deleted messages
GROUP_ID = int(os.getenv("GROUP_ID", "0"))          # ID of the group to monitor (0 = no restriction)

# Optional admin overrides
ADMIN_IDS = set()
admin_ids_raw = os.getenv("ADMIN_IDS", "")
if admin_ids_raw:
    try:
        ADMIN_IDS = {int(x) for x in admin_ids_raw.strip().split()}
    except ValueError:
        print("Warning: Invalid ADMIN_IDS in .env file.")
