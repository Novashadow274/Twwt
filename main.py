# main.py
# Entry point for the Twitter‐scraper Telegram bot
# (for Render Background Worker—no Flask or HTTP server needed)

from scheduler import start_bot

if __name__ == "__main__":
    start_bot()
