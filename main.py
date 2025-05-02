# main.py

import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import config
import logic

# import your command callbacks
from commands.ban import ban, unban
from commands.mute import mute, tpmute, unmute
from commands.warn import warn, unwarn
from commands.info_me import info, me
from commands.admin import promote, demote
from commands.clean import clean
from commands.report import report
from commands.ban_words import banwd, unwd
from commands.ban_stickers import banstk, unbanstk

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Dummy HTTP server for Render healthchecks ────────────────────────────────
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

def run_dummy_server():
    server = HTTPServer(("0.0.0.0", 8080), DummyHandler)
    logger.info("Starting dummy HTTP server on port 8080")
    server.serve_forever()

# ─── Build the Telegram application ────────────────────────────────────────────
def build_app():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("tpmute", tpmute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("unwarn", unwarn))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("me", me))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("clean", clean))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("banwd", banwd))
    app.add_handler(CommandHandler("unwd", unwd))
    app.add_handler(CommandHandler("banstk", banstk))
    app.add_handler(CommandHandler("unbanstk", unbanstk))
    logger.info("Registered all command handlers")

    # Message handler for non-command text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, logic.handle_message))
    logger.info("Registered message handler")

    return app

# ─── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Start the dummy server in the background
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # Build and start polling
    application = build_app()
    logger.info("Starting bot with long-polling")
    application.run_polling()
