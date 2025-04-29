import time
import random
import logging
import json
from playwright.sync_api import sync_playwright  # NEW
import telebot
from config import *
from formatter import format_message
from helper import download_media

# Setup
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def get_latest_tweet(username):
    """Get latest tweet using browser automation"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(f"https://x.com/{username}", timeout=15000)
            page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
            
            tweets = page.query_selector_all('article[data-testid="tweet"]')
            if not tweets:
                return None
                
            first_tweet = tweets[0]
            content = first_tweet.query_selector('div[data-testid="tweetText"]').inner_text()
            tweet_id = first_tweet.get_attribute('data-tweet-id')
            
            # Get media if exists
            media = []
            media_elements = first_tweet.query_selector_all('img[alt="Image"]')
            for img in media_elements:
                media.append(img.get_attribute('src'))
            
            return {
                'id': tweet_id,
                'content': content,
                'media': media
            }
        except Exception as e:
            logger.error(f"Browser scrape failed for {username}: {str(e)}")
            return None
        finally:
            browser.close()

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {username: 0 for username in ACCOUNTS}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def process_account(username, state):
    try:
        tweet_data = get_latest_tweet(username)
        if not tweet_data or tweet_data['id'] == state.get(username):
            return
            
        message = format_message(username, tweet_data['content'])
        
        # Handle media
        media_paths = []
        if tweet_data['media']:
            for url in tweet_data['media']:
                try:
                    media_paths.append(download_media(url))
                except Exception as e:
                    logger.error(f"Media download failed: {str(e)}")
        
        # Send message
        if media_paths:
            media_group = []
            for i, path in enumerate(media_paths):
                if i == 0:
                    media_group.append(telebot.types.InputMediaPhoto(
                        open(path, 'rb'), caption=message))
                else:
                    media_group.append(telebot.types.InputMediaPhoto(
                        open(path, 'rb')))
            bot.send_media_group(TELEGRAM_CHAT_ID, media_group)
        else:
            bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode='Markdown')
            
        state[username] = tweet_data['id']
        save_state(state)
        
    except Exception as e:
        logger.error(f"Account {username} failed: {str(e)}")
        time.sleep(300)  # Wait 5 minutes if error occurs

def run():
    state = load_state()
    while True:
        for username in ACCOUNTS:
            process_account(username, state)
            time.sleep(random.randint(60, 120))  # 1-2 minutes between accounts
