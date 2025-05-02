# commands/warn.py
import json
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, LOG_CHANNEL

# Persistent store
WARN_FILE = Path("warn_data.json")
warn_counts = {}

def load_warns() -> None:
    global warn_counts
    if WARN_FILE.exists():
        try:
            warn_counts = json.loads(WARN_FILE.read_text())
        except json.JSONDecodeError:
            warn_counts = {}

def save_warns() -> None:
    WARN_FILE.write_text(json.dumps(warn_counts))

load_warns()

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return

    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to warn them.")
        return

    tid = str(target.id)
    count = warn_counts.get(tid, 0) + 1
    warn_counts[tid] = count
    save_warns()

    reason = " ".join(context.args) if context.args else "No reason"
    log_text = (
        f"⚠️ <b>Warning</b>: {target.mention_html()} (id: {target.id}) "
        f"now at {count} warn(s). Reason: {reason}"
    )
    await context.bot.send_message(LOG_CHANNEL, log_text, parse_mode="HTML")
    await update.message.delete()

    if count >= 3:
        await context.bot.ban_chat_member(update.effective_chat.id, target.id)
        await context.bot.send_message(
            LOG_CHANNEL,
            f"💥 <b>Banned</b> {target.mention_html()} after 3 warnings",
            parse_mode="HTML"
        )

async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return

    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to remove a warning.")
        return

    tid = str(target.id)
    count = max(warn_counts.get(tid, 0) - 1, 0)
    warn_counts[tid] = count
    save_warns()

    log_text = (
        f"✅ <b>Unwarned</b>: {target.mention_html()} (id: {target.id}) now at {count} warn(s)."
    )
    await context.bot.send_message(LOG_CHANNEL, log_text, parse_mode="HTML")
    await update.message.delete()
