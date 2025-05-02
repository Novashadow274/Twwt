import os
import logging
import threading
import asyncio
from main import build_app
from flask import Flask
from dotenv import load_dotenv
from config import LOG_CHANNEL  # make sure this points to your log chat

load_dotenv()

# Build the Telegram bot application
bot_app = build_app()

def run_bot():
    # Register the webhook and start listening
    bot_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=os.environ["BOT_TOKEN"],
        webhook_url=f"{os.environ['RENDER_EXTERNAL_URL']}/{os.environ['BOT_TOKEN']}"
    )

# Flask app for health checks
flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    return "OK", 200

if __name__ == "__main__":
    # Standard logging setup
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot & webhook (Render)")

    # 1) Start the bot webhook listener in a background thread
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()

    # 2) Send a startup notification to your log channel
    #    We need to run this coroutine on the event loop
    async def notify_startup():
        try:
            await bot_app.bot.send_message(LOG_CHANNEL, "✅ Bot is now running.")
            logger.info("Startup notification sent to log channel")
        except Exception as e:
            logger.error(f"Failed to send startup notification: {e}")

    # Run the notify_startup coroutine
    asyncio.get_event_loop().run_until_complete(notify_startup())

    # 3) Finally, start Flask (Gunicorn will serve this in production)
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
