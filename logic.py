# logic.py
import re
from telegram import ChatPermissions, MessageEntity
from config import OWNER_ID, LOG_CHANNEL, GROUP_ID
from db import add_warning
from commands.warn import send_warning_message
from utils import is_admin_or_owner

SPAM_MEDIA_TYPES = {
    "photo", "video", "animation", "voice", "document", "sticker",
}

SPAM_COMMAND_LIMIT = 3  # non-admin command spam

user_command_counts = {}

async def handle_message(update, context):
    msg = update.effective_message
    if not msg:
        return

    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id

    if GROUP_ID and chat_id != GROUP_ID:
        return

    # Ignore admins/owner
    member = await context.bot.get_chat_member(chat_id, user_id)
    if is_admin_or_owner(user_id, member):
        return

    # Handle media-based spam
    if any(getattr(msg, media, None) for media in SPAM_MEDIA_TYPES):
        await msg.delete()
        await add_warning(context, chat_id, user)
        return

    # Handle spammy commands or unknown commands
    if msg.text and msg.text.startswith("/"):
        command = msg.text.split()[0]
        if not context.bot.get_commands():  # fallback
            known_commands = ["/warn", "/rwarn", "/ban", "/mute", "/tpmute", "/unmute", "/unban",
                              "/info", "/me", "/promote", "/demote", "/clean", "/report", "/banwd",
                              "/unwd", "/banstk", "/unbanstk"]
        else:
            known_commands = [f"/{cmd.command}" for cmd in context.bot.get_commands()]
        if command not in known_commands:
            await msg.delete()
            await add_warning(context, chat_id, user)
            return

    # Detect spammy symbols/emojis
    if re.search(r'https?://', msg.text or "", re.IGNORECASE):
        await msg.delete()
        await add_warning(context, chat_id, user)
        return

    if len(re.findall(r'[^\w\s,]', msg.text or "")) > 10:
        await msg.delete()
        await add_warning(context, chat_id, user)
        return
