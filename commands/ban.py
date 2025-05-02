# commands/ban.py
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, GROUP_ID, LOG_CHANNEL

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return  # only owner can ban

    # Determine the target user
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    else:
        # e.g. /ban @username or /ban user_id
        if not context.args:
            await update.message.reply_text("Usage: /ban @username")
            return
        target_username = context.args[0]
        target = None
        # Try to find the user in chat by username
        chat_members = await context.bot.get_chat_administrators(GROUP_ID)
        for member in chat_members:
            if member.user.username == target_username.lstrip('@'):
                target = member.user
                break

    if not target:
        await update.message.reply_text("Could not find that user.")
        return

    # Ban the target user
    await context.bot.ban_chat_member(GROUP_ID, target.id, revoke_messages=True)
    # Clean up the command message
    await update.message.delete()
    # Log the action
    log = f"🔨 <b>Banned</b>: {target.mention_html()} by {user.mention_html()}"
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return  # only owner can unban

    # Expect a user_id argument
    if not context.args:
        await update.message.reply_text("Usage: /unban user_id")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("User ID must be an integer.")
        return

    # Unban the user
    await context.bot.unban_chat_member(GROUP_ID, target_id, only_if_banned=True)
    # Clean up the command message
    await update.message.delete()
    # Log the action
    log = f"🚫 <b>Unbanned</b>: user_id {target_id} by {user.mention_html()}"
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')
