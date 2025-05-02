import re from telegram import ChatPermissions from config import OWNER_ID, LOG_CHANNEL, GROUP_ID

banned_words = [] banned_stickers = []

def is_owner(user_id): return user_id == OWNER_ID

def is_admin(user_id, chat_member): return user_id == OWNER_ID or chat_member.status in ("administrator", "creator")

async def delete_and_log(context, chat_id, message_id, reason, user): """Delete a message and log the action to the log channel.""" try: await context.bot.delete_message(chat_id, message_id) except Exception: pass log_text = f"Deleted message from {user.mention_html()} in chat {chat_id}. Reason: {reason}" await context.bot.send_message(LOG_CHANNEL, log_text, parse_mode='HTML')

async def handle_message(update, context): """Generic message handler: filters banned content and spam.""" msg = update.effective_message if not msg: return

user = update.effective_user
chat_id = update.effective_chat.id

# Only act in the main group if GROUP_ID is set
if GROUP_ID and chat_id != GROUP_ID:
    return

text = msg.text or ""
# Check forwarded message
if getattr(msg, "forward_date", None) or getattr(msg, "forward_from", None):
    await delete_and_log(context, chat_id, msg.message_id, "Forwarded message", user)
    return

# Check banned words
for word in banned_words:
    if word.lower() in text.lower():
        await delete_and_log(context, chat_id, msg.message_id, f"Banned word: {word}", user)
        return

# Check links (simple regex)
if re.search(r'http[s]?://', text):
    await delete_and_log(context, chat_id, msg.message_id, "Link posted", user)
    return

# Check spammy emoji (e.g., >10 emojis)
if len(re.findall(r'[^\w\s,]', text)) > 10:
    await delete_and_log(context, chat_id, msg.message_id, "Excessive emojis or symbols", user)
    return

# (Additional checks like rapid messaging could be added here)
# If everything is fine, do nothing

