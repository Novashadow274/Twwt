import os
import sys
import logging
from threading import Thread
from waitress import serve
from server import app
from scheduler import run

# Configure logging before anything else
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Security note: Tokens are partially masked in logs
def mask_token(token):
    return token[:5] + '****' + token[-4:] if token else 'None'

def verify_config():
    """Validate all critical configurations"""
    logger.info("🔍 Verifying configuration...")
    
    # Verify Telegram credentials
    required_vars = {
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'TELEGRAM_ADMIN_CHAT_ID': os.getenv('TELEGRAM_ADMIN_CHAT_ID')
    }
    
    missing_vars = [name for name, value in required_vars.items() if not value]
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    logger.debug(f"Telegram Bot: {mask_token(required_vars['TELEGRAM_BOT_TOKEN'])}")
    logger.debug(f"Target Chat ID: {required_vars['TELEGRAM_CHAT_ID']}")
    logger.debug(f"Admin Chat ID: {required_vars['TELEGRAM_ADMIN_CHAT_ID']}")
    
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
        logger.error(f"❌ Missing data files: {missing_files}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("⚡ Initializing Football News Bot")
    
    if not verify_config():
        logger.critical("🛑 Configuration validation failed!")
        exit(1)
    
    # Start Flask server
    try:
        flask_thread = Thread(
            target=lambda: serve(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080))),
            daemon=True
        )
        flask_thread.start()
        logger.info("🌐 Flask server started on port 8080")
    except Exception as e:
        logger.error(f"Failed to start Flask server: {str(e)}")
    
    # Start bot with error handling
    try:
        logger.info("🔄 Starting main bot loop")
        run()
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt, shutting down")
        exit(0)
    except Exception as e:
        logger.critical(f"💥 Bot crashed: {str(e)}")
        
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
