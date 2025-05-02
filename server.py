# server.py

import os
import threading
import asyncio
import logging
from flask import Flask
from dotenv import load_dotenv
from main import build_app

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET", "HEAD"])
def health_check():
    return "Bot is running!", 200

async def start_bot():
    try:
        app = build_app()
        await app.bot.delete_webhook(drop_pending_updates=True)
        await app.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
        logger.info("Webhook set successfully.")
        await app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_path=f"/{BOT_TOKEN}",
        )
    except Exception as e:
        logger.exception(f"Webhook failed to start: {e}")

def run_webhook():
    asyncio.run(start_bot())

if __name__ == "__main__":
    # Start the bot in a separate thread
    threading.Thread(target=run_webhook, name="WebhookThread").start()
    # Start the Flask server
    flask_app.run(host="0.0.0.0", port=PORT)
