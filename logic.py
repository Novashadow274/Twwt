import re
import datetime
from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes

# Helper to check if a user is the group owner (creator).
async def is_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status == 'creator'
    except Exception:
        return False

# Send a humorous rejection if a non-owner attempts an admin command.
async def reject_unauthorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = [
        "🚫 Nice try, but only the group owner can do that!",
        "🙄 You don't have the master key for this.",
        "😏 Whoa there! That's above your pay grade.",
        "😂 Only the boss can use that command, sorry!",
        "⛔ Access denied. Admin only business here."
    ]
    reply = f"{messages[hash(update.effective_user.id) % len(messages)]}"
    msg = await update.message.reply_text(reply)
    await update.message.delete()
    # Schedule deletion of the bot’s rejection message.
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# /ban command
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text("Usage: /ban @username or reply to user.")
        await update.message.delete(); return
    # Identify target user
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    else:
        arg = context.args[0]
        if arg.startswith('@'):
            try:
                # Attempt to get user by username
                user_chat = await context.bot.get_chat(arg)
                target_id = user_chat.id
            except Exception:
                await update.message.reply_text("User not found.")
                await update.message.delete(); return
        else:
            try:
                target_id = int(arg)
            except ValueError:
                await update.message.reply_text("Invalid user ID.")
                await update.message.delete(); return
    chat_id = update.effective_chat.id
    try:
        await context.bot.ban_chat_member(chat_id, target_id, revoke_messages=True)
        text = context.bot_data["default_messages"]["ban"]
        msg = await update.message.reply_text(text)
        # Log to private channel
        await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                       f"User {target_id} was banned by {update.effective_user.id} at {datetime.datetime.now()}.",
                                       disable_notification=True)
        # Delete command and schedule bot message deletion
        await update.message.delete()
        context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)
    except Exception as e:
        await update.message.reply_text(f"Failed to ban user: {e}")
        await update.message.delete()

# /unban command
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        await update.message.delete(); return
    try:
        target_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, target_id)
        text = context.bot_data["default_messages"]["unban"]
        msg = await update.message.reply_text(text)
        await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                       f"User {target_id} was unbanned by {update.effective_user.id} at {datetime.datetime.now()}.",
                                       disable_notification=True)
        await update.message.delete()
        context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)
    except Exception as e:
        await update.message.reply_text(f"Failed to unban user: {e}")
        await update.message.delete()

# /mute command (permanent mute until unmute)
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid user ID.")
            await update.message.delete(); return
    else:
        await update.message.reply_text("Usage: /mute @user or reply.")
        await update.message.delete(); return
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, target_id,
                                               ChatPermissions(can_send_messages=False))
        text = context.bot_data["default_messages"]["mute"]
        msg = await update.message.reply_text(text)
        await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                       f"User {target_id} was muted by {update.effective_user.id}.",
                                       disable_notification=True)
        await update.message.delete()
        context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)
    except Exception as e:
        await update.message.reply_text(f"Failed to mute user: {e}")
        await update.message.delete()

# /tpmute command (temporary mute)
async def tpmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if not context.args or not update.message.reply_to_message:
        await update.message.reply_text("Usage: /tpmute <minutes> (reply to user).")
        await update.message.delete(); return
    try:
        minutes = int(context.args[0].rstrip('mM'))  # e.g. "10m"
        target_id = update.message.reply_to_message.from_user.id
        until = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        await context.bot.restrict_chat_member(update.effective_chat.id, target_id,
                                               ChatPermissions(can_send_messages=False),
                                               until_date=until)
        text = context.bot_data["default_messages"]["tpmute"] + f" for {minutes} minutes."
        msg = await update.message.reply_text(text)
        await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                       f"User {target_id} was temp-muted by {update.effective_user.id} for {minutes}m.",
                                       disable_notification=True)
        await update.message.delete()
        context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)
    except Exception as e:
        await update.message.reply_text(f"Failed to tpmute user: {e}")
        await update.message.delete()

# /unmute command
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid user ID.")
            await update.message.delete(); return
    else:
        await update.message.reply_text("Usage: /unmute @user or reply.")
        await update.message.delete(); return
    try:
        # Restore permissions
        await context.bot.restrict_chat_member(update.effective_chat.id, target_id,
                                               ChatPermissions(can_send_messages=True,
                                                               can_send_media_messages=True,
                                                               can_send_other_messages=True,
                                                               can_add_web_page_previews=True))
        text = context.bot_data["default_messages"]["unmute"]
        msg = await update.message.reply_text(text)
        await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                       f"User {target_id} was unmuted by {update.effective_user.id}.",
                                       disable_notification=True)
        await update.message.delete()
        context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)
    except Exception as e:
        await update.message.reply_text(f"Failed to unmute user: {e}")
        await update.message.delete()

# /warn command
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid user ID.")
            await update.message.delete(); return
    else:
        await update.message.reply_text("Usage: /warn @user or reply.")
        await update.message.delete(); return
    user_data = context.bot_data.setdefault("users", {}).setdefault(target_id, {"warnings": 0, "messages": 0})
    user_data["warnings"] += 1
    text = context.bot_data["default_messages"]["warn"]
    msg = await update.message.reply_text(f"{text} Total warns: {user_data['warnings']}.")
    await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                   f"User {target_id} was warned by {update.effective_user.id}. Now has {user_data['warnings']} warns.",
                                   disable_notification=True)
    await update.message.delete()
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# /unwarn command
async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid user ID.")
            await update.message.delete(); return
    else:
        await update.message.reply_text("Usage: /unwarn @user or reply.")
        await update.message.delete(); return
    user_data = context.bot_data.setdefault("users", {}).setdefault(target_id, {"warnings": 0, "messages": 0})
    if user_data["warnings"] > 0:
        user_data["warnings"] -= 1
    text = context.bot_data["default_messages"]["unwarn"]
    msg = await update.message.reply_text(f"{text} Now has {user_data['warnings']} warns.")
    await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                   f"User {target_id} was unwarned by {update.effective_user.id}. Now has {user_data['warnings']} warns.",
                                   disable_notification=True)
    await update.message.delete()
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# /info command (show user info)
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    elif context.args:
        user_id = int(context.args[0]) if context.args[0].isdigit() else None
        if user_id:
            try:
                target = await context.bot.get_chat_member(update.effective_chat.id, user_id)
                target = target.user
            except:
                await update.message.reply_text("User not found in chat.")
                await update.message.delete(); return
        else:
            await update.message.reply_text("Usage: /info @user or /info <id>.")
            await update.message.delete(); return
    else:
        target = update.effective_user
    user_data = context.bot_data.setdefault("users", {}).setdefault(target.id, {"warnings": 0, "messages": 0, "joined": None})
    joined = user_data.get("joined", "Unknown")
    messages = user_data.get("messages", 0)
    warns = user_data.get("warnings", 0)
    text = (f"ℹ *User Info:*\n"
            f"- ID: `{target.id}`\n"
            f"- Name: {target.full_name}\n"
            f"- Joined: {joined}\n"
            f"- Messages: {messages}\n"
            f"- Warnings: {warns}")
    msg = await update.message.reply_text(text, parse_mode='Markdown')
    await update.message.delete()
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# /clean command (delete recent N messages)
async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    count = int(context.args[0]) if context.args and context.args[0].isdigit() else 10
    deleted = 0
    try:
        messages = await context.bot.get_chat_history(update.effective_chat.id, limit=count+1)
        for m in messages:
            try:
                await context.bot.delete_message(update.effective_chat.id, m.message_id)
                deleted += 1
            except:
                continue
        msg = await update.message.reply_text(f"🧹 Deleted {deleted} messages.")
        await update.message.delete()
        context.job_queue.run_once(lambda ctx: ctx.job.context(), 10, context=msg.delete)
    except Exception as e:
        await update.message.reply_text(f"Clean failed: {e}")
        await update.message.delete()

# /kick command (ban then unban)
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid user ID.")
            await update.message.delete(); return
    else:
        await update.message.reply_text("Usage: /kick @user or reply.")
        await update.message.delete(); return
    chat_id = update.effective_chat.id
    try:
        await context.bot.ban_chat_member(chat_id, target_id, revoke_messages=True)
        await context.bot.unban_chat_member(chat_id, target_id)
        text = context.bot_data["default_messages"]["kick"]
        msg = await update.message.reply_text(text)
        await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                       f"User {target_id} was kicked by {update.effective_user.id}.",
                                       disable_notification=True)
        await update.message.delete()
        context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)
    except Exception as e:
        await update.message.reply_text(f"Kick failed: {e}")
        await update.message.delete()

# /promote command
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except:
            await update.message.reply_text("Invalid user ID.")
            await update.message.delete(); return
    else:
        await update.message.reply_text("Usage: /promote @user or reply.")
        await update.message.delete(); return
    try:
        # Grant all admin privileges except managing other admins
        await context.bot.promote_chat_member(update.effective_chat.id, target_id,
                                              can_change_info=False,
                                              can_delete_messages=True,
                                              can_invite_users=True,
                                              can_restrict_members=True,
                                              can_pin_messages=True,
                                              can_promote_members=False)
        text = context.bot_data["default_messages"]["promote"]
        msg = await update.message.reply_text(text)
        await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                       f"User {target_id} was promoted to admin by {update.effective_user.id}.",
                                       disable_notification=True)
        await update.message.delete()
        context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)
    except Exception as e:
        await update.message.reply_text(f"Promote failed: {e}")
        await update.message.delete()

# /demote command (remove admin privileges)
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except:
            await update.message.reply_text("Invalid user ID.")
            await update.message.delete(); return
    else:
        await update.message.reply_text("Usage: /demote @user or reply.")
        await update.message.delete(); return
    try:
        # Remove all admin privileges
        await context.bot.promote_chat_member(update.effective_chat.id, target_id,
                                              can_change_info=False,
                                              can_delete_messages=False,
                                              can_invite_users=False,
                                              can_restrict_members=False,
                                              can_pin_messages=False,
                                              can_promote_members=False)
        text = context.bot_data["default_messages"]["demote"]
        msg = await update.message.reply_text(text)
        await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                       f"User {target_id} was demoted by {update.effective_user.id}.",
                                       disable_notification=True)
        await update.message.delete()
        context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)
    except Exception as e:
        await update.message.reply_text(f"Demote failed: {e}")
        await update.message.delete()

# /banwd command (ban a word)
async def banwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if not context.args:
        await update.message.reply_text("Usage: /banwd <word_or_phrase>")
        await update.message.delete(); return
    word = " ".join(context.args).lower()
    banned = context.bot_data.setdefault("banned_words", set())
    banned.add(word)
    msg = await update.message.reply_text(f"{context.bot_data['default_messages']['banwd']} \"{word}\"")
    await update.message.delete()
    context.bot_data["banned_words"] = banned
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# /unwd command (unban a word)
async def unwd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if not context.args:
        await update.message.reply_text("Usage: /unwd <word_or_phrase>")
        await update.message.delete(); return
    word = " ".join(context.args).lower()
    banned = context.bot_data.setdefault("banned_words", set())
    banned.discard(word)
    msg = await update.message.reply_text(f"{context.bot_data['default_messages']['unwd']} \"{word}\"")
    await update.message.delete()
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# /banstk command (ban a sticker)
async def banstk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("Reply to a sticker to ban it.")
        await update.message.delete(); return
    file_id = update.message.reply_to_message.sticker.file_id
    banned = context.bot_data.setdefault("banned_stickers", set())
    banned.add(file_id)
    msg = await update.message.reply_text(f"{context.bot_data['default_messages']['banstk']}")
    await update.message.delete()
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# /unbanstk command (unban a sticker)
async def unbanstk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update, context):
        return await reject_unauthorized(update, context)
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("Reply to a sticker to unban it.")
        await update.message.delete(); return
    file_id = update.message.reply_to_message.sticker.file_id
    banned = context.bot_data.setdefault("banned_stickers", set())
    if file_id in banned:
        banned.remove(file_id)
    msg = await update.message.reply_text(f"{context.bot_data['default_messages']['unbanstk']}")
    await update.message.delete()
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# /me command (show user stats)
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = context.bot_data.setdefault("users", {}).setdefault(user_id, {"warnings": 0, "messages": 0, "joined": None})
    joined = user_data.get("joined", "Unknown")
    messages = user_data.get("messages", 0)
    warns = user_data.get("warnings", 0)
    text = (f"👤 *Your Info:*\n"
            f"- Joined: {joined}\n"
            f"- Messages today: {messages}\n"
            f"- Warnings: {warns}")
    msg = await update.message.reply_text(text, parse_mode='Markdown')
    await update.message.delete()
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# /report command
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        reason = " ".join(context.args) if context.args else "No reason given"
    elif context.args:
        if context.args[0].startswith('@') or context.args[0].isdigit():
            try:
                target_id = int(context.args[0].lstrip('@'))
            except:
                target_id = None
            reason = " ".join(context.args[1:]) if len(context.args)>1 else "No reason given"
        else:
            await update.message.reply_text("Usage: /report @user [reason]")
            await update.message.delete(); return
    else:
        await update.message.reply_text("Usage: /report @user [reason]")
        await update.message.delete(); return
    if not target_id:
        await update.message.reply_text("Could not identify user to report.")
        await update.message.delete(); return
    # Increment report count
    reports = context.bot_data.setdefault("reports", {})
    count = reports.setdefault(target_id, 0) + 1
    reports[target_id] = count
    if count >= 30:
        # Auto-mute if 30+ reports
        try:
            await context.bot.restrict_chat_member(update.effective_chat.id, target_id,
                                                   ChatPermissions(can_send_messages=False),
                                                   until_date=datetime.datetime.now()+datetime.timedelta(hours=24))
            await context.bot.send_message(update.effective_chat.id,
                                           f"User [{target_id}](tg://user?id={target_id}) has been muted due to excessive reports.",
                                           parse_mode='Markdown')
        except:
            pass
    msg = await update.message.reply_text(f"{context.bot_data['default_messages']['report']} (Total reports: {count})")
    await update.message.delete()
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)
    await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                   f"User {target_id} was reported by {update.effective_user.id} (reason: {reason}). Total={count}",
                                   disable_notification=True)

# @admin mention handling
async def mention_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Hey there! I see you mentioned @admin. If you need help, please specify your issue here or contact the group owner directly."
    msg = await update.message.reply_text(text)
    await update.message.delete()
    context.job_queue.run_once(lambda ctx: ctx.job.context(), 60, context=msg.delete)

# Message handler for general messages (spam check, delete links/forwards, banned content)
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Track join time
    user_data = context.bot_data.setdefault("users", {}).setdefault(user_id, {"warnings":0, "messages":0, "joined":None})
    if user_data["joined"] is None:
        user_data["joined"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Increment message count for spam detection
    msgs = user_data.setdefault("recent_msgs", [])
    now = datetime.datetime.now().timestamp()
    msgs.append(now)
    # Remove messages older than 30 seconds
    msgs = [t for t in msgs if now - t < 30]
    user_data["recent_msgs"] = msgs
    if len(msgs) > 5:
        # Considered spam: auto-warn
        user_data["recent_msgs"].clear()
        user_data["warnings"] += 1
        await context.bot.send_message(chat_id, f"⚠ Slow down, <a href='tg://user?id={user_id}'>user</a>!", parse_mode='HTML')
        await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                       f"User {user_id} auto-warned for spamming. Warnings: {user_data['warnings']}",
                                       disable_notification=True)

    # Delete forwarded messages
    if message.forward_date:
        try:
            await message.delete()
        except:
            pass
        return

    # Delete messages with URLs
    if message.entities:
        for ent in message.entities:
            if ent.type in ['url','text_link']:
                try:
                    await message.delete()
                except:
                    pass
                return

    # Check banned words
    text = message.text.lower() if message.text else ""
    banned_words = context.bot_data.get("banned_words", set())
    for word in banned_words:
        if re.search(rf"\b{re.escape(word)}\b", text):
            try:
                await message.delete()
            except:
                pass
            await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                           f"Deleted message from {user_id} containing banned word '{word}'.",
                                           disable_notification=True)
            return

    # Check banned stickers
    if message.sticker:
        if message.sticker.file_id in context.bot_data.get("banned_stickers", set()):
            try:
                await message.delete()
            except:
                pass
            await context.bot.send_message(context.bot_data["config"].LOG_CHANNEL_ID,
                                           f"Deleted banned sticker from {user_id}.",
                                           disable_notification=True)
            return

    # Check @admin mention in text
    if message.text and "@admin" in message.text:
        await mention_admin(update, context)
