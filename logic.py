import re
from telegram import ChatPermissions
from config import OWNER_ID, LOG_CHANNEL, GROUP_ID

banned_words = []
banned_stickers = []  # Future use

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id, chat_member):
    return user_id == OWNER_ID or chat_member.status in ("administrator", "creator")

async def delete_and_log(context, chat_id, message_id, reason, user):
    """Delete message and log reason to LOG_CHANNEL."""
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"[Delete Error] {e}")  # Optional debug

    try:
        user_mention = user.mention_html() if user else "Unknown user"
        log_text = (
            f"🗑️ Deleted message from {user_mention} in chat <code>{chat_id}</code>.\n"
            f"Reason: <b>{reason}</b>"
        )
        await context.bot.send_message(LOG_CHANNEL, log_text, parse_mode='HTML')
    except Exception as e:
        print(f"[Log Error] {e}")  # Optional debug

async def handle_message(update, context):
    """Filters banned content from messages."""
    msg = update.effective_message
    if not msg:
        return

    user = update.effective_user
    chat_id = update.effective_chat.id
    text = msg.text or ""

    # Restrict to target group only
    if GROUP_ID and chat_id != GROUP_ID:
        return

    # Block forwarded messages
    if msg.forward_date or msg.forward_from:
        await delete_and_log(context, chat_id, msg.message_id, "Forwarded message", user)
        return

    # Check for banned words
    for word in banned_words:
        if word.lower() in text.lower():
            await delete_and_log(context, chat_id, msg.message_id, f"Banned word: {word}", user)
            return

    # Block links
    if re.search(r'https?://', text, re.IGNORECASE):
        await delete_and_log(context, chat_id, msg.message_id, "Link posted", user)
        return

    # Block excessive symbols
    if len(re.findall(r'[^\w\s,]', text)) > 10:
        await delete_and_log(context, chat_id, msg.message_id, "Excessive emojis or symbols", user)
        return
