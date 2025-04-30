import time
import random
import logging
import json
from playwright.sync_api import sync_playwright
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

def get_browser():
    """Safe browser launcher for Render"""
    try:
        # Try with system Chrome first
        return p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/google-chrome"
        )
    except:
        # Fallback to Playwright's bundled browser
        return p.chromium.launch(headless=True)

def get_latest_tweet(username):
    """Get latest tweet using browser automation"""
    with sync_playwright() as p:
        try:
            browser = get_browser()
            page = browser.new_page()
            
            # Configure to look more like a normal browser
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            })
            
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
                src = img.get_attribute('src')
                if src and 'https://' in src:
                    media.append(src)
            
            return {
                'id': tweet_id,
                'content': content,
                'media': media
            }
        except Exception as e:
            logger.error(f"Browser scrape failed for {username}: {str(e)}")
            return None
        finally:
            try:
                browser.close()
            except:
                pass

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {username: 0 for username in ACCOUNTS}

def save_state(state):
    temp = STATE_FILE.with_suffix('.tmp')
    with open(temp, 'w') as f:
        json.dump(state, f)
    temp.replace(STATE_FILE)

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
                    path = download_media(url)
                    if path:  # Only add if download succeeded
                        media_paths.append(path)
                except Exception as e:
                    logger.error(f"Media download failed for {url}: {str(e)}")
        
        # Send message
        try:
            if media_paths:
                media_group = []
                for i, path in enumerate(media_paths):
                    with open(path, 'rb') as f:
                        if i == 0:
                            media_group.append(telebot.types.InputMediaPhoto(
                                f, caption=message))
                        else:
                            media_group.append(telebot.types.InputMediaPhoto(f))
                bot.send_media_group(TELEGRAM_CHAT_ID, media_group)
            else:
                bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode='Markdown')
            
            state[username] = tweet_data['id']
            save_state(state)
            
        except Exception as e:
            logger.error(f"Telegram send failed: {str(e)}")
            
    except Exception as e:
        logger.error(f"Account {username} failed: {str(e)}")
        time.sleep(300)  # Wait 5 minutes if error occurs

def run():
    state = load_state()
    while True:
        for username in ACCOUNTS:
            process_account(username, state)
            time.sleep(random.randint(90, 180))  # 1.5-3 minutes between accounts
