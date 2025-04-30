import time
import random
import json
import logging
import requests
import telebot
import snscrape.modules.twitter as sntwitter
from config import *
from formatter import format_message
from helper import download_media
from pathlib import Path

# Enhanced logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug.log')
    ]
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
REQUEST_TIMEOUT = 30

def load_state():
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                logger.info("Loaded existing state file")
                return state
    except Exception as e:
        logger.warning(f"Error loading state: {e}")
    state = {username: 0 for username in ACCOUNTS}
    logger.info("Created new state file")
    return state

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
            logger.debug("State saved successfully")
    except Exception as e:
        logger.error(f"Failed to save state: {e}")

def get_latest_tweet(username):
    """
    Uses snscrape to fetch the very latest tweet from @username.
    Returns a dict with 'id', 'content', and a list of 'media' URLs.
    """
    logger.info(f" Scraping @{username} with snscrape")
    try:
        scraper = sntwitter.TwitterUserScraper(username)
        for tweet in scraper.get_items():
            media_urls = []
            if tweet.media:
                for m in tweet.media:
                    if hasattr(m, 'fullUrl'):
                        media_urls.append(m.fullUrl)
            return {
                'id': str(tweet.id),
                'content': tweet.content,
                'media': media_urls
            }
    except Exception as e:
        logger.error(f"snsc​rape error for @{username}: {e}", exc_info=True)
    return None

def process_account(username, state):
    try:
        logger.info(f" Checking @{username}")
        tweet_data = get_latest_tweet(username)
        if not tweet_data:
            return
        current_id = str(state.get(username, 0))
        if tweet_data['id'] == current_id:
            logger.debug(f"No new tweets for @{username}")
            return
        logger.info(f" New tweet from @{username} (ID: {tweet_data['id']})")

        # Test notification
        try:
            bot.send_message(TELEGRAM_CHAT_ID, f" New update from @{username}", disable_notification=True)
        except Exception as e:
            logger.error(f"Telegram test failed: {e}")
            return

        message = format_message(username, tweet_data['content'])
        media_paths = []
        if tweet_data['media']:
            for url in tweet_data['media'][:4]:
                try:
                    path = download_media(url)
                    if path:
                        media_paths.append(path)
                except Exception as e:
                    logger.error(f"Media download failed: {e}")

        try:
            if media_paths:
                media_group = []
                for i, path in enumerate(media_paths):
                    with open(path, 'rb') as f:
                        if i == 0:
                            media_group.append(telebot.types.InputMediaPhoto(f, caption=message))
                        else:
                            media_group.append(telebot.types.InputMediaPhoto(f))
                bot.send_media_group(TELEGRAM_CHAT_ID, media_group)
            else:
                bot.send_message(TELEGRAM_CHAT_ID, message)
            state[username] = tweet_data['id']
            save_state(state)
            logger.info(f"✅ Successfully posted update from @{username}")
        except Exception as e:
            logger.error(f"Failed to send update: {e}")
    except Exception as e:
        logger.error(f"Processing error for @{username}: {e}")
        time.sleep(10)

def run():
    logger.info(" Starting monitoring loop")
    state = load_state()
    try:
        bot.send_message(TELEGRAM_CHAT_ID, "⚽ Bot activated! Starting monitoring...")
    except Exception as e:
        logger.error(f"Initial message failed: {e}")
    while True:
        try:
            for username in ACCOUNTS:
                start_time = time.time()
                process_account(username, state)
                elapsed = time.time() - start_time
                time.sleep(max(5, 15 - elapsed))
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run()
