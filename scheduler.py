import time
import random
import logging
import json
from playwright.sync_api import sync_playwright
import telebot
from config import *
from formatter import format_message
from helper import download_media
from pathlib import Path

# Setup
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def get_browser(playwright):
    """Safe browser launcher for Render"""
    return playwright.chromium.launch(
        headless=True,
        channel="chrome",  # Uses Playwright's managed Chrome
        timeout=30000,     # Increased timeout
        args=[
            '--disable-gpu',
            '--single-process',
            '--no-zygote',
            '--no-sandbox'
        ]
    )

def get_latest_tweet(username):
    """Get latest tweet using browser automation"""
    with sync_playwright() as p:
        browser = None
        try:
            browser = get_browser(p)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            # Navigate to profile
            page.goto(f"https://x.com/{username}", timeout=15000)
            
            # Wait for tweets to load
            try:
                page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
            except:
                logger.warning(f"No tweets found for {username}")
                return None
                
            # Get first tweet
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
                if src and src.startswith('http'):
                    media.append(src)
            
            return {
                'id': tweet_id,
                'content': content,
                'media': media
            }
        except Exception as e:
            logger.error(f"Browser error for {username}: {str(e)}")
            return None
        finally:
            if browser:
                browser.close()

def load_state():
    """Load saved tweet IDs"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {username: 0 for username in ACCOUNTS}

def save_state(state):
    """Atomically save state"""
    temp = STATE_FILE.with_suffix('.tmp')
    with open(temp, 'w') as f:
        json.dump(state, f)
    temp.replace(STATE_FILE)

def cleanup_media():
    """Remove old media files"""
    media_dir = Path('temp_media')
    if media_dir.exists():
        for file in media_dir.glob('*'):
            try:
                if file.stat().st_mtime < time.time() - 3600:  # 1 hour old
                    file.unlink()
            except:
                pass

def process_account(username, state):
    """Process one account's tweets"""
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
                    if path:
                        media_paths.append(path)
                except Exception as e:
                    logger.error(f"Media download failed: {str(e)}")
        
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
            
        # Cleanup old files
        cleanup_media()
            
    except Exception as e:
        logger.error(f"Account {username} failed: {str(e)}")
        time.sleep(300)  # Wait 5 minutes on error

def run():
    """Main execution loop"""
    state = load_state()
    while True:
        for username in ACCOUNTS:
            process_account(username, state)
            time.sleep(random.randint(90, 180))  # 1.5-3 minutes between accounts
