# commands/ban_stickers.py
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, LOG_CHANNEL
from logic import banned_stickers

async def banstk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /banstk <sticker_set_name>")
        return
    stk = context.args[0]
    if stk not in banned_stickers:
        banned_stickers.append(stk)
    await update.message.delete()
    await context.bot.send_message(LOG_CHANNEL, f"📑 Banned sticker set: {stk}")

async def unbanstk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /unbanstk <sticker_set_name>")
        return
    stk = context.args[0]
    if stk in banned_stickers:
        banned_stickers.remove(stk)
    await update.message.delete()
    await context.bot.send_message(LOG_CHANNEL, f"❎ Unbanned sticker set: {stk}")
