# commands/warn.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db import get_warn_count, add_warning, remove_warning, has_removed_this_cycle, mark_removed
from config import OWNER_ID
from utils import is_admin_or_owner
from datetime import datetime, timedelta
import asyncio

WARNING_MESSAGES = {
    1: "{} 1 Well, it's okay",
    2: "{} 2 Follow the rules",
    3: "{} 3 Read the rules or leave",
    4: "{} 4 Not here to babysit",
    5: "{} 5You're pushing it",
    6: "{} Done wasting time. 24hr sleep"
}

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.message

    # Must reply
    if not msg.reply_to_message:
        await msg.reply_text("Reply to a user to warn them.", quote=True, timeout=10)
        return await msg.delete()

    target = msg.reply_to_message.from_user
    if target.id == user.id:
        return await msg.delete()

    member = await context.bot.get_chat_member(chat.id, user.id)
    target_member = await context.bot.get_chat_member(chat.id, target.id)

    if not is_admin_or_owner(user.id, member):
        text = f"{user.first_name} can't warn anyone because I think you are not admin here."
        m = await msg.reply_text(text, timeout=10)
        await asyncio.sleep(60)
        return await m.delete()

    if is_admin_or_owner(target.id, target_member):
        return await msg.delete()

    # Prevent warnings for muted/banned
    if target_member.status == "kicked":
        m = await msg.reply_text(f"{target.first_name} Already banned 😒", timeout=10)
        await asyncio.sleep(60)
        return await m.delete()

    if target_member.status == "restricted":
        m = await msg.reply_text(f"{target.first_name} Already muted 😖", timeout=10)
        await asyncio.sleep(60)
        return await m.delete()

    count = await add_warning(context, chat.id, target)

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Warning ❗", callback_data=f"warn:{chat.id}:{target.id}:{count}")]]
    )

    text = WARNING_MESSAGES.get(count, WARNING_MESSAGES[5]).format(target.first_name)

    if count >= 6:
        await context.bot.restrict_chat_member(
            chat.id,
            target.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=datetime.utcnow() + timedelta(hours=24),
        )
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Muted 😴", callback_data=f"warn:{chat.id}:{target.id}:{count}")]]
        )

    sent = await msg.reply_text(text, reply_markup=button)
    if count >= 6:
        await asyncio.sleep(86400)
    else:
        await asyncio.sleep(36000)
    await sent.delete()
    await msg.delete()

async def rwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.message

    if not msg.reply_to_message:
        await msg.reply_text("Reply to a user to remove a warning.", timeout=10)
        return await msg.delete()

    target = msg.reply_to_message.from_user
    if target.id == user.id:
        return await msg.delete()

    member = await context.bot.get_chat_member(chat.id, user.id)
    target_member = await context.bot.get_chat_member(chat.id, target.id)

    if not is_admin_or_owner(user.id, member):
        m = await msg.reply_text(f"{user.first_name} can't remove warnings because I think you are not admin here.")
        await asyncio.sleep(60)
        return await m.delete()

    if is_admin_or_owner(target.id, target_member):
        return await msg.delete()

    if await get_warn_count(chat.id, target.id) == 0:
        m = await msg.reply_text("Can’t undo what hasn’t happened. No warnings to remove.")
        await asyncio.sleep(60)
        return await m.delete()

    if target_member.status in ("kicked", "restricted"):
        m = await msg.reply_text("That user is already muted. Let them rest.")
        await asyncio.sleep(60)
        return await m.delete()

    if await has_removed_this_cycle(chat.id, user.id, target.id):
        m = await msg.reply_text("You’ve already given them a break this cycle.")
        await asyncio.sleep(60)
        return await m.delete()

    await remove_warning(chat.id, target.id)
    await mark_removed(chat.id, user.id, target.id)

    m = await msg.reply_text(f"{target.first_name} Your warning has been lifted! Just don’t go wild now 😊")
    await asyncio.sleep(60)
    await m.delete()
    await msg.delete()

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(":")
    chat_id, user_id, count = int(data[1]), int(data[2]), int(data[3])
    clicker = query.from_user

    if clicker.id == int(user_id) and count < 6:
        await query.answer("Pope\nPlease note that if you receive six warnings, you will be muted 🤷‍♀️")
        await query.message.delete()
    elif clicker.id == int(user_id) and count == 6:
        await query.answer("pope\nYou’ve been muted for 24 hours because you received 6 warnings.")
    else:
        await query.answer("Mind your own business 😬", show_alert=True)
