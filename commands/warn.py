## commands/warn.py
import json
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, LOG_CHANNEL

# Path to our persistent warning store
WARN_FILE = Path("warn_data.json")

def load_warns() -> dict:
    if WARN_FILE.exists():
        try:
            return json.loads(WARN_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}

def save_warns(data: dict):
    WARN_FILE.write_text(json.dumps(data))

# Load existing warn counts at startup
warn_counts = load_warns()

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return

    # Identify target
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to warn them.")
        return

    # Increment warn count
    target_id = str(target.id)
    count = warn_counts.get(target_id, 0) + 1
    warn_counts[target_id] = count
    save_warns(warn_counts)

    # Reason text
    reason = " ".join(context.args) if context.args else "No reason"

    # Log to your channel
    log_text = (
        f"⚠️ <b>Warning</b>: {target.mention_html()} (id: {target.id}) "
        f"now at {count} warn(s). Reason: {reason}"
    )
    await context.bot.send_message(LOG_CHANNEL, log_text, parse_mode="HTML")

    # Delete the warning command message for cleanliness
    await update.message.delete()

    # Auto‐ban at 3 warnings
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

    target_id = str(target.id)
    count = max(warn_counts.get(target_id, 0) - 1, 0)
    warn_counts[target_id] = count
    save_warns(warn_counts)

    log_text = (
        f"✅ <b>Unwarned</b>: {target.mention_html()} (id: {target.id}) now at {count} warn(s)."
    )
    await context.bot.send_message(LOG_CHANNEL, log_text, parse_mode="HTML")
    await update.message.delete()
