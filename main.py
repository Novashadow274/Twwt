import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Import bot token and URL from config or environment
try:
    from config import BOT_TOKEN, RENDER_APP_URL
except ImportError:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    RENDER_APP_URL = os.environ.get("RENDER_APP_URL")

# Basic logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dummy HTTP server handler to keep the dyno alive
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, DummyHandler)
    logger.info("Starting dummy HTTP server on port 8080")
    try:
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Dummy server error: {e}")

# Error handler to log exceptions
async def error_handler(update, context):
    logger.error(f"Error while handling update: {context.error}")

def main():
    # Start dummy server thread
    dummy_thread = threading.Thread(target=run_dummy_server, daemon=True)
    dummy_thread.start()

    # Create the Application and pass it the bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    logger.info("Telegram bot application created")

    # Import message handler and command handlers from logic
    try:
        from logic import handle_message, ban, unban, mute, tpmute, unmute, warn, unwarn
        from logic import info, me, promote, demote, clean, report, banwd, unwd, banstk, unbanstk
    except ImportError as e:
        logger.error(f"Error importing handlers from logic module: {e}")
        return

    # Add command handlers
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("mute", mute))
    application.add_handler(CommandHandler("tpmute", tpmute))
    application.add_handler(CommandHandler("unmute", unmute))
    application.add_handler(CommandHandler("warn", warn))
    application.add_handler(CommandHandler("unwarn", unwarn))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("me", me))
    application.add_handler(CommandHandler("promote", promote))
    application.add_handler(CommandHandler("demote", demote))
    application.add_handler(CommandHandler("clean", clean))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("banwd", banwd))
    application.add_handler(CommandHandler("unwd", unwd))
    application.add_handler(CommandHandler("banstk", banstk))
    application.add_handler(CommandHandler("unbanstk", unbanstk))
    logger.info("Registered command handlers")

    # Add message handler for general messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Registered message handler")

    # Add the error handler
    application.add_error_handler(error_handler)

    # Build webhook URL
    webhook_url = f"https://{RENDER_APP_URL}/{BOT_TOKEN}"
    # Determine port for webhook (use environment or default)
    port = int(os.environ.get("PORT", 8443))
    # Start the webhook server (blocking call) and set webhook
    try:
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=webhook_url
        )
        logger.info(f"Bot started with webhook URL: {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to start webhook server: {e}")

if __name__ == "__main__":
    logger.info("Starting bot")
    main()
