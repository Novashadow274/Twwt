# commands/ban_stickers.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import OWNER_ID
import logic

async def banstk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can use this command.")
        return
    
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("Please reply to a sticker to ban its pack.")
        return
    
    sticker = update.message.reply_to_message.sticker
    if sticker.set_name not in logic.banned_stickers:
        logic.banned_stickers.append(sticker.set_name)
        await update.message.reply_text(f"Sticker pack '{sticker.set_name}' banned.")
    else:
        await update.message.reply_text(f"Sticker pack '{sticker.set_name}' is already banned.")

async def unbanstk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a sticker pack name to unban.")
        return
    
    pack_name = ' '.join(context.args)
    if pack_name in logic.banned_stickers:
        logic.banned_stickers.remove(pack_name)
        await update.message.reply_text(f"Sticker pack '{pack_name}' unbanned.")
    else:
        await update.message.reply_text(f"Sticker pack '{pack_name}' wasn't banned.")

def add_handlers(application):
    application.add_handler(CommandHandler("banstk", banstk))
    application.add_handler(CommandHandler("unbanstk", unbanstk))
