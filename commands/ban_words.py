# commands/ban_words.py
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, LOG_CHANNEL
from logic import banned_words

async def banwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /banwd <word>")
        return
    word = context.args[0].lower()
    if word not in banned_words:
        banned_words.append(word)
        # Update log channel description (store banned words list)
        desc = ", ".join(banned_words)
        await context.bot.set_chat_description(LOG_CHANNEL, desc)
    await update.message.delete()
    await context.bot.send_message(LOG_CHANNEL, f"📝 Banned word added: {word}")

async def unwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /unwd <word>")
        return
    word = context.args[0].lower()
    if word in banned_words:
        banned_words.remove(word)
        desc = ", ".join(banned_words)
        await context.bot.set_chat_description(LOG_CHANNEL, desc)
    await update.message.delete()
    await context.bot.send_message(LOG_CHANNEL, f"🗑️ Banned word removed: {word}")
