import re
from telegram import ChatPermissions
from config import OWNER_ID, LOG_CHANNEL, GROUP_ID

banned_words = []
banned_stickers = []

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id, chat_member):
    return user_id == OWNER_ID or chat_member.status in ("administrator", "creator")

async def delete_and_log(context, chat_id, message_id, reason, user):
    """Delete a message and log the action to the log channel."""
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception as e:
        # You might want to log this in debug
        pass

    try:
        if user:
            user_mention = user.mention_html()
        else:
            user_mention = "Unknown user"

        log_text = (
            f"🗑️ Deleted message from {user_mention} in chat <code>{chat_id}</code>.\n"
            f"Reason: <b>{reason}</b>"
        )
        await context.bot.send_message(LOG_CHANNEL, log_text, parse_mode='HTML')
    except Exception as e:
        # Fails silently; could log to console if needed
        pass

async def handle_message(update, context):
    """Main handler to process incoming messages for banned content."""
    msg = update.effective_message
    if not msg:
        return

    user = update.effective_user
    chat_id = update.effective_chat.id
    text = msg.text or ""

    # Only act in the main group
    if GROUP_ID and chat_id != GROUP_ID:
        return

    # Delete forwarded messages
    if getattr(msg, "forward_date", None) or getattr(msg, "forward_from", None):
        await delete_and_log(context, chat_id, msg.message_id, "Forwarded message", user)
        return

    # Banned word detection
    for word in banned_words:
        if word.lower() in text.lower():
            await delete_and_log(context, chat_id, msg.message_id, f"Banned word: {word}", user)
            return

    # Delete links
    if re.search(r'https?://', text, re.IGNORECASE):
        await delete_and_log(context, chat_id, msg.message_id, "Link posted", user)
        return

    # Excessive emojis or non-alphanumerics
    if len(re.findall(r'[^\w\s,]', text)) > 10:
        await delete_and_log(context, chat_id, msg.message_id, "Excessive emojis or symbols", user)
        return
