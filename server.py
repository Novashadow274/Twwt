import os
import logging
from main import build_app
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = build_app()

# Minimal Flask app for Render to detect an open port
flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    return "OK", 200

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot with webhook (Render)")

    # Start Telegram bot webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),  # PORT is defined by Render
        url_path=os.environ["BOT_TOKEN"],
        webhook_url=f"{os.environ['RENDER_EXTERNAL_URL']}/{os.environ['BOT_TOKEN']}"
    )
