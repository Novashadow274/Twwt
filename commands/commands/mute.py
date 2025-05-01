# commands/mute.py
import re
from datetime import datetime, timedelta
from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes
from config import OWNER_ID, GROUP_ID, LOG_CHANNEL

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /mute @username")
        return
    # similar lookup as /ban (omitted for brevity)
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Please reply to a user's message to mute them.")
        return
    await context.bot.restrict_chat_member(
        GROUP_ID, target.id, ChatPermissions(can_send_messages=False)
    )
    await update.message.delete()
    log = f"🔇 <b>Muted</b>: {target.mention_html()} by {user.mention_html()}"
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')

async def tpmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /tpmute 10m (duration) replying to user")
        return
    dur_arg = context.args[0]
    m = re.match(r'(\d+)([smhd])', dur_arg)
    if not m:
        await update.message.reply_text("Invalid duration format. e.g. 10m, 1h")
        return
    amount, unit = int(m.group(1)), m.group(2)
    delta = {'s': 1, 'm':60, 'h':3600, 'd':86400}[unit]
    until = datetime.utcnow() + timedelta(seconds=amount * delta)
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Please reply to a user to mute them.")
        return
    await context.bot.restrict_chat_member(
        GROUP_ID, target.id, ChatPermissions(can_send_messages=False), until_date=until
    )
    await update.message.delete()
    log = f"🔇 <b>TempMuted</b>: {target.mention_html()} for {amount}{unit} by {user.mention_html()}"
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        return
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        await update.message.reply_text("Please reply to a user to unmute them.")
        return
    # Lifting restrictions by giving full send permissions
    perms = ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                             can_send_polls=True, can_send_other_messages=True,
                             can_add_web_page_previews=True)
    await context.bot.restrict_chat_member(GROUP_ID, target.id, perms)
    await update.message.delete()
    log = f"🔊 <b>Unmuted</b>: {target.mention_html()} by {user.mention_html()}"
    await context.bot.send_message(LOG_CHANNEL, log, parse_mode='HTML')
