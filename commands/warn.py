# commands/warn.py
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, LOG_CHANNEL

warn_counts = {}  # simplistic in-memory store

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to warn them.")
        return
    count = warn_counts.get(target.id, 0) + 1
    warn_counts[target.id] = count
    reason = " ".join(context.args) if context.args else "No reason"
    log = f"⚠️ <b>Warning</b>: {target.mention_html()} now at {count} warn(s). Reason: {reason}"
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')
    await update.message.delete()
    if count >= 3:
        # auto-ban on 3 warnings
        await context.bot.ban_chat_member(update.effective_chat.id, target.id)
        await context.bot.send_message(LOG_CHANNEL, f"💥 <b>Banned</b> {target.mention_html()} after 3 warnings", parse_mode='HTML')

async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to remove a warning.")
        return
    count = max(warn_counts.get(target.id, 0) - 1, 0)
    warn_counts[target.id] = count
    log = f"✅ <b>Unwarned</b>: {target.mention_html()} now at {count} warn(s)."
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')
    await update.message.delete()
