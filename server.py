import os
import logging
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from main import build_app

load_dotenv()

# Build the bot application
app = build_app()

# Create a minimal Flask app for health checks
flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    return "OK", 200

def run_webhook():
    print("Bot is running via webhook")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=os.environ["BOT_TOKEN"],
        webhook_url=f"{os.environ['RENDER_EXTERNAL_URL']}{os.environ['BOT_TOKEN']}"
    )

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot via webhook")

    # Start Telegram webhook in a thread
    Thread(target=run_webhook).start()

    # Start Flask app for Render health check
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
