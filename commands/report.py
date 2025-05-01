# commands/report.py
from telegram import Update
from telegram.ext import ContextTypes
from config import LOG_CHANNEL

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reporter = update.effective_user
    if update.message.reply_to_message:
        # Forward the replied message to admins
        await context.bot.forward_message(LOG_CHANNEL, update.effective_chat.id,
                                          update.message.reply_to_message.message_id)
        note = f"⚠️ <b>Report</b> by {reporter.mention_html()}"
        await context.bot.send_message(LOG_CHANNEL, note, parse_mode='HTML')
    else:
        text = " ".join(context.args) if context.args else "(no text)"
        await context.bot.send_message(LOG_CHANNEL,
                                       f"⚠️ <b>Report from {reporter.mention_html()}</b>: {text}",
                                       parse_mode='HTML')
    await update.message.delete()
