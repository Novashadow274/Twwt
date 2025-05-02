import os
import logging
from main import build_app
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

# Initialize the Flask app
flask_app = Flask(__name__)

# Health check route for Render to detect an open port
@flask_app.route("/")
def health():
    return "OK", 200

# Build the Telegram bot app
app = build_app()

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot with webhook (Render)")

    # Start the Flask app to serve the webhook
    flask_app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),  # PORT is defined by Render
    )
