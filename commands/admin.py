# commands/admin.py
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, GROUP_ID, LOG_CHANNEL

async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return

    # Determine the user to promote (must be replying to their message)
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to promote them.")
        return

    # Promote with all privileges
    await context.bot.promote_chat_member(
        GROUP_ID, target.id,
        can_change_info=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_promote_members=True
    )

    # Clean up the command message
    await update.message.delete()

    # Log the action
    log = f"⭐️ <b>Promoted</b>: {target.mention_html()} by {user.mention_html()}"
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')


async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return

    # Determine the user to demote (must be replying to their message)
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Reply to a user to demote them.")
        return

    # Demote by revoking all privileges
    await context.bot.promote_chat_member(
        GROUP_ID, target.id,
        can_change_info=False,
        can_delete_messages=False,
        can_invite_users=False,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False
    )

    # Clean up the command message
    await update.message.delete()

    # Log the action
    log = f"⬇️ <b>Demoted</b>: {target.mention_html()} by {user.mention_html()}"
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')
