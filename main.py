import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import json
from logic import *
import config

async def main():
    # Load default messages and command info
    with open("default_message.json", "r") as f:
        default_msgs = json.load(f)
    with open("command.json", "r") as f:
        commands = json.load(f)

    # Initialize bot application (using webhook mode for Render deployment)
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    # Store shared data in bot_data
    app.bot_data["default_messages"] = default_msgs
    app.bot_data["config"] = config  # store config for easy access
    app.bot_data["banned_words"] = set()
    app.bot_data["banned_stickers"] = set()
    app.bot_data["users"] = {}      # user metadata storage
    app.bot_data["reports"] = {}

    # Register admin command handlers
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

    # Register user command handlers
    app.add_handler(CommandHandler("me", me))
    app.add_handler(CommandHandler("report", report))
    # Catch any message containing '@admin'
    app.add_handler(MessageHandler(filters.Regex(r'@admin'), mention_admin))

    # General message handler (spam, links, forwards, banned content)
    app.add_handler(MessageHandler(filters.ALL, handle_messages), 1)

    # Periodic jobs:
    # Reset daily message counts and warnings every midnight
    async def reset_daily(context: ContextTypes.DEFAULT_TYPE):
        for uid, data in context.bot_data.get("users", {}).items():
            data["messages"] = 0
            data["warnings"] = 0
    # Schedule at 00:00 UTC every day
    app.job_queue.run_daily(reset_daily, time=datetime.time(hour=0, minute=0, second=0))

    # Start webhook (listen on all interfaces, port from env)
    PORT = int(os.environ.get("PORT", 8443))
    # The webhook URL is e.g. WEBHOOK_URL + "/" + BOT_TOKEN
    webhook_path = config.BOT_TOKEN
    await app.start_webhook(listen="0.0.0.0", port=PORT, url_path=webhook_path,
                            webhook_url=f"{config.WEBHOOK_URL}/{webhook_path}")
    await app.wait_until_closed()

if __name__ == "__main__":
    asyncio.run(main())
