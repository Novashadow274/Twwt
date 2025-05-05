# commands/ban_words.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import OWNER_ID
import logic

async def banwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a word to ban.")
        return
    
    word = ' '.join(context.args).lower()
    if word not in logic.banned_words:
        logic.banned_words.append(word)
        await update.message.reply_text(f"Word '{word}' added to banned list.")
    else:
        await update.message.reply_text(f"Word '{word}' is already banned.")

async def unwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a word to unban.")
        return
    
    word = ' '.join(context.args).lower()
    if word in logic.banned_words:
        logic.banned_words.remove(word)
        await update.message.reply_text(f"Word '{word}' removed from banned list.")
    else:
        await update.message.reply_text(f"Word '{word}' wasn't in the banned list.")

def add_handlers(application):
    application.add_handler(CommandHandler("banwd", banwd))
    application.add_handler(CommandHandler("unwd", unwd))
