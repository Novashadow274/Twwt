# commands/info_me.py
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Anyone can use /info
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    count = warn_counts.get(user.id, 0)
    await update.message.reply_text(f"User {user.mention_html()} has {count} warning(s).", parse_mode='HTML')

async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    count = warn_counts.get(user.id, 0)
    
    # Send the response in a DM (private message)
    await user.send_message(f"You have {count} warning(s).")
    
    # Optionally, delete the command message from the group
    await update.message.delete()
