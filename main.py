import os
import logging
from threading import Thread
from waitress import serve
from server import app
from scheduler import run

# Security note: Tokens are partially masked in logs
def mask_token(token):
    return token[:5] + '****' + token[-4:] if token else 'None'

# Debug configuration
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def verify_config():
    """Validate all critical configurations"""
    logger.info("Verifying configuration...")
    
    # Verify Telegram credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not all([bot_token, chat_id]):
        logger.error("Missing Telegram credentials in environment variables")
        return False
    
    logger.debug(f"Telegram Bot: {mask_token(bot_token)}")
    logger.debug(f"Target Chat ID: {chat_id}")
    
    # Verify data files
    required_files = [
        'data/name_priority.json',
        'data/headline_name.json',
        'data/source_hashtag.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing data files: {missing_files}")
        return False
    
    return True

if __name__ == "__main__":
    if not verify_config():
        logger.critical("Configuration validation failed!")
        exit(1)
    
    # Start Flask server
    flask_thread = Thread(
        target=lambda: serve(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080))),
        daemon=True
    )
    flask_thread.start()
    logger.info("Flask server started")
    
    # Start bot with error handling
    try:
        logger.info("Starting main bot loop")
        run()
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}")
        
        # Attempt to notify admin via Telegram
        try:
            import telebot
            bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
            bot.send_message(
                os.getenv('TELEGRAM_ADMIN_CHAT_ID'),
                f"🚨 Bot crashed: {str(e)[:200]}"  # Truncate long messages
            )
        except Exception as telegram_error:
            logger.error(f"Failed to send crash alert: {str(telegram_error)}")
        
        exit(1)
