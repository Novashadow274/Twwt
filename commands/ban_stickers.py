# commands/ban_stickers.py
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, LOG_CHANNEL
from logic import banned_stickers

async def banstk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a sticker set by name and log the action."""
    user = update.effective_user
    if user.id != OWNER_ID:
        return

    # Expect a sticker set name argument
    if not context.args:
        await update.message.reply_text("Usage: /banstk <sticker_set_name>")
        return

    stk = context.args[0]
    # Add to banned_stickers list if not already present
    if stk not in banned_stickers:
        banned_stickers.append(stk)

    # Clean up the command message
    await update.message.delete()
    # Log the action
    await context.bot.send_message(LOG_CHANNEL, f"📑 Banned sticker set: {stk}")

async def unbanstk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a sticker set by name and log the action."""
    user = update.effective_user
    if user.id != OWNER_ID:
        return

    # Expect a sticker set name argument
    if not context.args:
        await update.message.reply_text("Usage: /unbanstk <sticker_set_name>")
        return

    stk = context.args[0]
    # Remove from banned_stickers list if present
    if stk in banned_stickers:
        banned_stickers.remove(stk)

    # Clean up the command message
    await update.message.delete()
    # Log the action
    await context.bot.send_message(LOG_CHANNEL, f"❎ Unbanned sticker set: {stk}")
