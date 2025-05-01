# main.py
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import config
import logic

from commands.ban import ban, unban
from commands.mute import mute, tpmute, unmute
from commands.warn import warn, unwarn
from commands.info_me import info, me
from commands.admin import promote, demote
from commands.clean import clean
from commands.report import report
from commands.ban_words import banwd, unwd
from commands.ban_stickers import banstk, unbanstk

# Build the application
app = ApplicationBuilder().token(config.BOT_TOKEN).build()

# Command handlers (owner-only checks are done inside the functions)
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

# Handle all normal text messages for spam/bad-content filtering
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, logic.handle_message))

# Start webhook (Render provides PORT and RENDER_APP_URL in env)
PORT = int(os.environ.get("PORT", "8443"))
RENDER_URL = os.environ.get("RENDER_APP_URL")  # e.g. "https://myapp.onrender.com"
# The webhook path is usually the bot token for security
app.run_webhook(listen="0.0.0.0",
                port=PORT,
                url_path=config.BOT_TOKEN,
                webhook_url=f"{RENDER_URL}/{config.BOT_TOKEN}") 
