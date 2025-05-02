from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, LOG_CHANNEL
import re

async def fetch_warns_from_log(context, user_id: int) -> int:
    # Fetch last 100 messages from LOG_CHANNEL
    history = await context.bot.get_chat_history(LOG_CHANNEL, limit=100)
    warn_pattern = re.compile(fr"Warning.*?{user_id}.*?at (\d+) warn")
    for msg in reversed(history):
        match = warn_pattern.search(msg.text_html or "")
        if match:
            return int(match.group(1))
    return 0

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to warn them.")
        return

    # Get current warns from log messages
    count = await fetch_warns_from_log(context, target.id)
    count += 1
    reason = " ".join(context.args) if context.args else "No reason"
    log = f"⚠️ <b>Warning</b>: {target.mention_html()} (id: {target.id}) now at {count} warn(s). Reason: {reason}"
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')
    await update.message.delete()

    if count >= 3:
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

    count = await fetch_warns_from_log(context, target.id)
    count = max(count - 1, 0)
    log = f"✅ <b>Unwarned</b>: {target.mention_html()} (id: {target.id}) now at {count} warn(s)."
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')
    await update.message.delete()
