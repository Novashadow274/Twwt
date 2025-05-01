# commands/clean.py
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID

async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /clean <number_of_messages>")
        return
    n = int(context.args[0])
    chat = update.effective_chat
    messages = []
    # Retrieve recent messages (requires message history access)
    async for msg in context.bot.get_chat(chat.id).iter_history(limit=n+1):
        messages.append(msg.message_id)
    if messages:
        await context.bot.delete_messages(chat.id, messages)
    await update.message.delete()
