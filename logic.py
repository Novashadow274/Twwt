# logic.py
import re
import time
import logging
from telegram import ChatPermissions
from config import OWNER_ID, LOG_CHANNEL, GROUP_ID, ADMIN_IDS
from commands.warn import warn_user_auto

# Initialize banned words and stickers lists
banned_words = []
banned_stickers = []

# Spam detection variables
user_last_message = {}
spam_threshold = 5  # messages
spam_window = 10    # seconds

async def handle_message(update, context):
    msg = update.effective_message
    if not msg:
        return

    user = update.effective_user
    chat_id = update.effective_chat.id

    # Skip if not in monitored group
    if GROUP_ID and chat_id != GROUP_ID:
        return

    # Skip if message is from admin/owner
    if user.id in ADMIN_IDS or user.id == OWNER_ID:
        return

    # Spam detection
    current_time = time.time()
    if user.id in user_last_message:
        last_time, count = user_last_message[user.id]
        if current_time - last_time < spam_window:
            count += 1
            if count >= spam_threshold:
                await warn_user_auto(context, user, chat_id)
                await delete_and_log(context, chat_id, msg.message_id, "Spam detected", user)
                user_last_message[user.id] = (current_time, 0)
                return
            user_last_message[user.id] = (last_time, count)
        else:
            user_last_message[user.id] = (current_time, 1)
    else:
        user_last_message[user.id] = (current_time, 1)

    # Check banned words if text message
    if msg.text:
        text = msg.text.lower()
        for word in banned_words:
            if word.lower() in text:
                await warn_user_auto(context, user, chat_id)
                await delete_and_log(context, chat_id, msg.message_id, f"Banned word: {word}", user)
                return

    # Handle different message types
    if msg.forward_date or msg.forward_from:
        await delete_and_log(context, chat_id, msg.message_id, "Forwarded message", user)
        return

    if msg.sticker and msg.sticker.set_name in banned_stickers:
        await warn_user_auto(context, user, chat_id)
        await delete_and_log(context, chat_id, msg.message_id, "Banned sticker", user)
        return

    if msg.text:
        await handle_text_message(msg, context, chat_id, user)
    elif msg.photo or msg.video or msg.gif or msg.document or msg.sticker or msg.voice:
        await warn_user_auto(context, user, chat_id)
        await delete_and_log(context, chat_id, msg.message_id, "Media spam", user)

async def handle_text_message(msg, context, chat_id, user):
    text = msg.text or ""
    
    if re.search(r'https?://', text, re.IGNORECASE):
        await delete_and_log(context, chat_id, msg.message_id, "Link posted", user)
        return

    if len(re.findall(r'[^\w\s,]', text)) > 10:
        await delete_and_log(context, chat_id, msg.message_id, "Excessive emojis/symbols", user)
        return

async def delete_and_log(context, chat_id, message_id, reason, user):
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.error(f"[Delete Error] {e}")

    try:
        mention = user.mention_html() if user else "Unknown user"
        log_text = (
            f"🗑️ Deleted message from {mention} in chat <code>{chat_id}</code>.\n"
            f"Reason: <b>{reason}</b>"
        )
        await context.bot.send_message(LOG_CHANNEL, log_text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"[Log Error] {e}")
