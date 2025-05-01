import os
import datetime
import json

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from logic import *
import config


async def reset_daily(context: ContextTypes.DEFAULT_TYPE):
    """Reset message & warning counts at UTC midnight."""
    users = context.bot_data.get("users", {})
    for data in users.values():
        data["messages"] = 0
        data["warnings"] = 0

    # Optional: log to your private channel
    await context.bot.send_message(
        chat_id=config.LOG_CHANNEL_ID,
        text="🔄 Daily reset of message counts & warnings complete.",
        disable_notification=True,
    )


def main():
    # Load config files
    with open("default_message.json", "r") as f:
        default_msgs = json.load(f)
    with open("command.json", "r") as f:
        commands = json.load(f)

    # Build the bot application
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Shared in-memory state
    app.bot_data["default_messages"] = default_msgs
    app.bot_data["config"]           = config
    app.bot_data["banned_words"]     = set()
    app.bot_data["banned_stickers"]  = set()
    app.bot_data["users"]            = {}
    app.bot_data["reports"]          = {}

    # Admin commands
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("tpmute", tpmute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("unwarn", unwarn))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("clean", clean))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("banwd", banwd))
    app.add_handler(CommandHandler("unwd", unwd))
    app.add_handler(CommandHandler("banstk", banstk))
    app.add_handler(CommandHandler("unbanstk", unbanstk))

    # User commands
    app.add_handler(CommandHandler("me", me))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.Regex(r"@admin"), mention_admin))

    # Catch-all for moderation (links, forwards, spam, banned words/stickers)
    app.add_handler(MessageHandler(filters.ALL, handle_messages), 1)

    # JOB‐QUEUE: schedule daily reset at UTC midnight
    app.job_queue.run_daily(
        reset_daily,
        time=datetime.time(hour=0, minute=0, second=0),
    )

    # Run webhook (synchronous entrypoint)
    PORT = int(os.environ.get("PORT", 8443))
    webhook_path = config.BOT_TOKEN  # Telegram will POST updates here

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=f"{config.WEBHOOK_URL}/{webhook_path}",
    )


if __name__ == "__main__":
    main()
