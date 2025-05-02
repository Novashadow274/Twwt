# server.py

import os
import logging
from main import build_app
import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets this automatically
    render_url = os.environ.get("RENDER_APP_URL")

    if not render_url:
        raise ValueError("Missing RENDER_APP_URL environment variable")

    app = build_app()
    logger.info("Starting bot with webhook (Render)")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=config.BOT_TOKEN,
        webhook_url=f"{render_url}/{config.BOT_TOKEN}"
    )
