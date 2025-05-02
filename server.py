import os
import logging
from threading import Thread
from flask import Flask
from main import build_app
import config

# Minimal Flask app for Render to detect an open port
flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    return "OK", 200

# Start Telegram bot in a background thread
def start_telegram_bot():
    from telegram.ext import Application
    app = build_app()
    logging.info("Starting bot with webhook (Render)")
    app.run_webhook(
        listen="0.0.0.0",
        port=8443,  # Telegram-recommended ports
        url_path=config.BOT_TOKEN,
        webhook_url=f"{os.environ['RENDER_APP_URL']}/{config.BOT_TOKEN}"
    )

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    # Start bot thread
    Thread(target=start_telegram_bot).start()
