# commands/warn.py
import sqlite3
from datetime import datetime, timedelta
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
)
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import OWNER_ID, ADMIN_IDS, GROUP_ID
import logging

# Database setup
DB_FILE = "warnings.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warnings (
            user_id INTEGER,
            chat_id INTEGER,
            warnings INTEGER DEFAULT 0,
            last_warn_time TIMESTAMP,
            mute_time TIMESTAMP,
            last_rwarn_time TIMESTAMP,
            PRIMARY KEY (user_id, chat_id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Warning messages templates
WARNING_MESSAGES = [
    "Well, it's okay",
    "Follow the rules",
    "Read the rules or leave",
    "Not here to babysit",
    "You're pushing it"
]

async def get_user_warnings(user_id, chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT warnings, mute_time FROM warnings WHERE user_id=? AND chat_id=?', (user_id, chat_id))
    result = cursor.fetchone()
    conn.close()
    return result or (0, None)

async def update_warnings(user_id, chat_id, increment=True):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    if increment:
        cursor.execute('''
            INSERT INTO warnings (user_id, chat_id, warnings, last_warn_time) 
            VALUES (?, ?, 1, ?)
            ON CONFLICT(user_id, chat_id) DO UPDATE SET 
            warnings = warnings + 1, last_warn_time = ?
        ''', (user_id, chat_id, now, now))
    else:
        cursor.execute('''
            UPDATE warnings 
            SET warnings = MAX(0, warnings - 1), last_rwarn_time = ?
            WHERE user_id=? AND chat_id=?
        ''', (now, user_id, chat_id))
    
    conn.commit()
    conn.close()

async def set_mute_time(user_id, chat_id, mute_duration=24):
    mute_time = (datetime.now() + timedelta(hours=mute_duration)).isoformat()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO warnings (user_id, chat_id, mute_time) 
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, chat_id) DO UPDATE SET mute_time = ?
    ''', (user_id, chat_id, mute_time, mute_time))
    conn.commit()
    conn.close()
    return mute_time

async def is_muted(user_id, chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT mute_time FROM warnings WHERE user_id=? AND chat_id=?', (user_id, chat_id))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        mute_time = datetime.fromisoformat(result[0])
        return mute_time > datetime.now()
    return False

async def can_rwarn(admin_id, user_id, chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT last_rwarn_time FROM warnings 
        WHERE user_id=? AND chat_id=?
    ''', (user_id, chat_id))
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result[0]:
        return True
        
    last_rwarn = datetime.fromisoformat(result[0])
    return (datetime.now() - last_rwarn) >= timedelta(hours=24)

async def warn_user_auto(context, user, chat_id):
    """Automatically warn user for spam"""
    current_warnings, _ = await get_user_warnings(user.id, chat_id)
    
    if current_warnings >= 5:  # Already at max warnings
        return
    
    await update_warnings(user.id, chat_id)
    current_warnings += 1
    
    warning_msg = WARNING_MESSAGES[min(current_warnings - 1, len(WARNING_MESSAGES) - 1)]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Warning ❗", callback_data=f"warn_ack:{user.id}")]
    ])
    
    warn_message = await context.bot.send_message(
        chat_id,
        f"{user.first_name}\n{warning_msg}",
        reply_markup=keyboard
    )
    
    # Schedule message deletion after 10 hours
    context.job_queue.run_once(
        lambda _: warn_message.delete(), 
        10 * 3600
    )

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    
    # Check if user is admin/owner
    if user.id not in ADMIN_IDS and user.id != OWNER_ID:
        reply = await message.reply_text(f"{user.first_name} you can't, give up")
        context.job_queue.run_once(lambda _: reply.delete(), 300)
        await message.delete()
        return
    
    # Get target user
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif context.args:
        arg = context.args[0]
        try:
            if arg.startswith('@'):
                target = await context.bot.get_chat(arg)
            else:
                target = await context.bot.get_chat(int(arg))
        except Exception:
            pass
    
    if not target:
        reply = await message.reply_text("Reply to a user or specify @username/ID to warn them.")
        context.job_queue.run_once(lambda _: reply.delete(), 300)
        await message.delete()
        return
    
    # Check if target is admin/owner
    if target.id in ADMIN_IDS or target.id == OWNER_ID:
        await message.delete()
        return
    
    # Check if target is already muted/banned
    if await is_muted(target.id, chat.id):
        reply = await message.reply_text(f"{target.first_name}\nAlready muted 😖")
        context.job_queue.run_once(lambda _: reply.delete(), 300)
        await message.delete()
        return
    
    # Get current warnings
    current_warnings, mute_time = await get_user_warnings(target.id, chat.id)
    
    # Handle 6th warning (mute)
    if current_warnings >= 5:
        mute_until = await set_mute_time(target.id, chat.id, 24)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Muted 😴", callback_data=f"mute_ack:{target.id}")]
        ])
        
        mute_message = await message.reply_text(
            f"{target.first_name}\nDone wasting time. 24hr sleep",
            reply_markup=keyboard
        )
        
        # Schedule message deletion after 24 hours
        context.job_queue.run_once(
            lambda _: mute_message.delete(), 
            24 * 3600
        )
        
        # Mute the user
        try:
            await context.bot.restrict_chat_member(
                chat.id, target.id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                ),
                until_date=datetime.fromisoformat(mute_until)
            )
        except Exception as e:
            logging.error(f"Error muting user: {e}")
        
        await message.delete()
        return
    
    # Increment warnings
    await update_warnings(target.id, chat.id)
    current_warnings += 1
    
    # Send warning message with button
    warning_msg = WARNING_MESSAGES[min(current_warnings - 1, len(WARNING_MESSAGES) - 1)]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Warning ❗", callback_data=f"warn_ack:{target.id}")]
    ])
    
    warn_message = await message.reply_text(
        f"{target.first_name}\n{warning_msg}",
        reply_markup=keyboard
    )
    
    # Schedule message deletion after 10 hours
    context.job_queue.run_once(
        lambda _: warn_message.delete(), 
        10 * 3600
    )
    
    await message.delete()

async def rwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message
    
    # Check if user is admin/owner
    if user.id not in ADMIN_IDS and user.id != OWNER_ID:
        reply = await message.reply_text(f"{user.first_name} you can't remove warnings because I think you are not admin here.")
        context.job_queue.run_once(lambda _: reply.delete(), 300)
        await message.delete()
        return
    
    # Get target user
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif context.args:
        arg = context.args[0]
        try:
            if arg.startswith('@'):
                target = await context.bot.get_chat(arg)
            else:
                target = await context.bot.get_chat(int(arg))
        except Exception:
            pass
    
    if not target:
        reply = await message.reply_text("Reply to a user or specify @username/ID to remove their warning.")
        context.job_queue.run_once(lambda _: reply.delete(), 300)
        await message.delete()
        return
    
    # Check if target is admin/owner
    if target.id in ADMIN_IDS or target.id == OWNER_ID:
        await message.delete()
        return
    
    # Check if can remove warning
    if not await can_rwarn(user.id, target.id, chat.id):
        reply = await message.reply_text("You've already given them a break this cycle.")
        context.job_queue.run_once(lambda _: reply.delete(), 300)
        await message.delete()
        return
    
    # Get current warnings
    current_warnings, _ = await get_user_warnings(target.id, chat.id)
    
    if current_warnings <= 0:
        reply = await message.reply_text("Can't undo what hasn't happened. No warnings to remove.")
        context.job_queue.run_once(lambda _: reply.delete(), 300)
        await message.delete()
        return
    
    # Check if target is muted
    if await is_muted(target.id, chat.id):
        reply = await message.reply_text("That user is already muted. Let them rest.")
        context.job_queue.run_once(lambda _: reply.delete(), 300)
        await message.delete()
        return
    
    # Decrement warnings
    await update_warnings(target.id, chat.id, increment=False)
    
    reply = await message.reply_text(f"{target.first_name} Your warning has been lifted! Just don't go wild now 😊")
    context.job_queue.run_once(lambda _: reply.delete(), 300)
    await message.delete()

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    
    if data.startswith("warn_ack:"):
        target_id = int(data.split(":")[1])
        
        if user.id == target_id:
            await query.answer("Please note that if you receive six warnings, you will be muted 🤷‍♀️")
            await query.message.delete()
        else:
            await query.answer("Mind your own business 😬", show_alert=True)
    
    elif data.startswith("mute_ack:"):
        target_id = int(data.split(":")[1])
        
        if user.id == target_id:
            await query.answer("You've been muted for 24 hours because you received 6 warnings. It's time to sleep ⏳😴")
            await query.message.delete()
        else:
            await query.answer("Mind your own business 😬", show_alert=True)
    
    await query.answer()

def add_handlers(application):
    application.add_handler(CommandHandler("warn", warn))
    application.add_handler(CommandHandler("rwarn", rwarn))
    application.add_handler(CallbackQueryHandler(button_callback))
