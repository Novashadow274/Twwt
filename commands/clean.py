# commands/clean.py
from telegram import Update
from telegram.ext import ContextTypes

from config import OWNER_ID

# Store recent messages per chat (in-memory)
recent_messages = {}

async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Guard against non-message updates
    if not update.message:
        return

    chat_id = update.effective_chat.id
    msg_id = update.message.message_id

    recent_messages.setdefault(chat_id, []).append(msg_id)
    # Keep only the last 100 IDs
    if len(recent_messages[chat_id]) > 100:
        recent_messages[chat_id] = recent_messages[chat_id][-100:]

async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if user.id != OWNER_ID:
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /clean <number_of_messages>")
        return

    n = int(context.args[0])
    message_ids = recent_messages.get(chat_id, [])[-n:]

    for msg_id in message_ids:
        try:
            await context.bot.delete_message(chat_id, msg_id)
        except Exception:
            pass  # ignore deletion failures

    # delete the /clean command message itself
    try:
        await update.message.delete()
    except Exception:
        pass
