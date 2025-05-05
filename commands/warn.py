# commands/warn.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from telegram.error import BadRequest
from db import add_warning, get_warning_count, remove_warning, is_muted, set_muted
from config import OWNER_ID, LOG_CHANNEL
from datetime import timedelta

WARNING_MESSAGES = {
    1: "{} 1 Well, it's okay",
    2: "{} 2 Follow the rules",
    3: "{} 3 Read the rules or leave",
    4: "{} 4 Not here to babysit",
    5: "{} 5You're pushing it",
    6: "{} Done wasting time. 24hr sleep"
}

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not await is_authorized(update):
        await send_temp_message(update, f"{user.first_name} can't warn anyone because I think you are not admin here.")
        return

    target = await extract_target_user(update, context)
    if not target:
        return

    if user.id == target.id:
        return  # No self-warn

    member = await chat.get_member(target.id)
    if member.status in ("administrator", "creator") or target.id == OWNER_ID:
        return  # Cannot warn admins/owner

    if await is_muted(target.id):
        await send_temp_message(update, f"{target.first_name}\nAlready muted 😖")
        return

    warning_count = add_warning(target.id)
    warn_text = WARNING_MESSAGES.get(warning_count, f"{target.first_name} Warning {warning_count}")

    if warning_count < 6:
        keyboard = InlineKeyboardMarkup.from_button(InlineKeyboardButton("Warning ❗", callback_data=f"warn:{target.id}"))
        msg = await update.message.reply_text(warn_text.format(target.first_name), reply_markup=keyboard)
        context.job_queue.run_once(delete_message_job, 36000, data=msg)  # 10 hours
    else:
        set_muted(target.id)
        try:
            await context.bot.restrict_chat_member(
                chat.id,
                target.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=timedelta(hours=24)
            )
        except BadRequest:
            pass

        msg = await update.message.reply_text(warn_text.format(target.first_name))
        context.job_queue.run_once(delete_message_job, 86400, data=msg)  # 24 hours
        await context.bot.send_message(
            chat_id=target.id,
            text="You've been muted for 24 hours because you received 6 warnings. It's time to sleep ⏳😴"
        )

    await update.message.delete()

async def rwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not await is_authorized(update):
        await send_temp_message(update, f"{user.first_name} can't remove warnings because I think you are not admin here.")
        return

    target = await extract_target_user(update, context)
    if not target:
        return

    if user.id == target.id:
        return  # No self-rwarn

    member = await chat.get_member(target.id)
    if member.status in ("administrator", "creator") or target.id == OWNER_ID:
        return

    if await is_muted(target.id):
        await send_temp_message(update, f"{target.first_name}\nThat user is already muted. Let them rest.")
        return

    count = get_warning_count(target.id)
    if count == 0:
        await send_temp_message(update, "Can’t undo what hasn’t happened. No warnings to remove.")
        return

    count = remove_warning(target.id)
    msg = await update.message.reply_text(f"{target.first_name} Your warning has been lifted! Just don’t go wild now 😊")
    context.job_queue.run_once(delete_message_job, 60, data=msg)  # auto-delete after 1 minute
    await update.message.delete()

# Utility: Check if user is admin/owner
async def is_authorized(update: Update) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    member = await chat.get_member(user.id)
    return user.id == OWNER_ID or member.status in ("administrator", "creator")

# Utility: Extract target user from reply, @username, or ID
async def extract_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    if context.args:
        arg = context.args[0]
        if arg.startswith("@"):
            try:
                user = await context.bot.get_chat(arg)
                return user
            except Exception:
                return None
        try:
            user_id = int(arg)
            user = await context.bot.get_chat(user_id)
            return user
        except Exception:
            return None
    return None

# Utility: Temporary message deletion
async def send_temp_message(update, text):
    msg = await update.message.reply_text(text)
    update.message.delete()
    update.message.chat.send_action(ChatAction.TYPING)
    update.message.bot.job_queue.run_once(delete_message_job, 60, data=msg)

# Utility: Delete message
async def delete_message_job(context: ContextTypes.DEFAULT_TYPE):
    msg = context.job.data
    try:
        await msg.delete()
    except:
        pass

# Handle inline button click
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split(":")[1])

    if query.from_user.id == user_id:
        await query.message.delete()
        await query.answer("Alert: Pope\nPlease note that if you receive six warnings, you will be muted 🤷‍♀️")
    else:
        await query.answer("Mind your own business 😬", show_alert=True)
