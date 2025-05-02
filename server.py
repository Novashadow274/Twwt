import os
import logging
from main import build_app
import config
from threading import Thread
from flask import Flask

# Minimal Flask app for Render to detect an open port
flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    return "OK", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ["PORT"]))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Start Flask in a separate thread
    Thread(target=run_flask).start()

    app = build_app()
    logger.info("Starting bot with webhook (Render)")
    app.run_webhook(
        listen="0.0.0.0",
        port=8443,  # Telegram recommends 443/80/88/8443
        url_path=config.BOT_TOKEN,
        webhook_url=f"{os.environ['RENDER_APP_URL']}/{config.BOT_TOKEN}"
    )
