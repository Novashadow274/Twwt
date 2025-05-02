# server.py

import os
import logging
from main import build_app  # Import the app builder only

import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app = build_app()
    logger.info("Starting bot with webhook (Render)")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ["PORT"]),
        url_path=config.BOT_TOKEN,
        webhook_url=f"{os.environ['RENDER_APP_URL']}/{config.BOT_TOKEN}"
    )
