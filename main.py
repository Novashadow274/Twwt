# main.py
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.error import Conflict as ConflictError
import config
import logic

from commands.ban import ban, unban
from commands.mute import mute, tpmute, unmute
from commands.warn import warn, unwarn
from commands.info_me import info, me
from commands.admin import promote, demote
from commands.clean import clean, track_messages
from commands.report import report
from commands.ban_words import banwd, unwd
from commands.ban_stickers import banstk, unbanstk

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    err = context.error
    if isinstance(err, ConflictError):
        return  # ignore getUpdates 409 conflicts
    logger.error("Exception while handling update", exc_info=err)

def build_app():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Register commands
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

    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_messages))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, logic.handle_message))

    # Global error handler
    app.add_error_handler(error_handler)

    return app

# Health check server for Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running.")

def run_health_server():
    server = HTTPServer(("0.0.0.0", 10000), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    app = build_app()
    app.run_polling()
