import os
import logging
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from main import build_app

load_dotenv()

print("Building bot app...")
app = build_app()
print("Bot app built.")

# Start Telegram webhook in a thread
def run_webhook():
    print("Starting bot webhook...")
    try:
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 10000)),
            url_path=os.environ["BOT_TOKEN"],
            webhook_url=f"{os.environ['RENDER_EXTERNAL_URL']}{os.environ['BOT_TOKEN']}"
        )
        print("Webhook running.")
    except Exception as e:
        print(f"Webhook failed to start: {e}")

Thread(target=run_webhook).start()

# Flask health check app for Render
flask_app = Flask(__name__)

@flask_app.route("/")
def health():
    print("Health check route hit.")
    return "OK", 200
