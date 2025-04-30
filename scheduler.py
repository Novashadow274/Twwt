import time
import random
import logging
import json
import requests
from bs4 import BeautifulSoup
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

def get_latest_tweet(username):
    """Get latest tweet using HTML scraping"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # Fetch profile page
        response = requests.get(f"https://x.com/{username}", headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        tweet = soup.find('article', {'data-testid': 'tweet'})
        if not tweet:
            return None
            
        # Extract data
        content = tweet.find('div', {'data-testid': 'tweetText'}).get_text()
        tweet_id = tweet.get('data-tweet-id')
        
        # Get media
        media = []
        for img in tweet.find_all('img', alt='Image'):
            src = img.get('src')
            if src and src.startswith('http'):
                media.append(src)
        
        return {
            'id': tweet_id,
            'content': content,
            'media': media
        }
    except Exception as e:
        logger.error(f"Scrape error for {username}: {str(e)}")
        return None

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
        if not tweet_data or tweet_data['id'] == state.get(username, 0):
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
            
        # Cleanup old files
        cleanup_media()
            
    except Exception as e:
        logger.error(f"Account {username} failed: {str(e)}")
        time.sleep(300)  # Wait 5 minutes on error

def run():
    """Main execution function to be imported by main.py"""
    logger.info("Starting Twitter scraper bot")
    state = load_state()
    while True:
        for username in ACCOUNTS:
            start_time = time.time()
            logger.info(f"Checking account @{username}")
            process_account(username, state)
            elapsed = time.time() - start_time
            delay = max(60, random.randint(120, 240) - int(elapsed))  # 2-4 minute intervals
            logger.info(f"Completed @{username} in {elapsed:.1f}s. Sleeping for {delay}s")
            time.sleep(delay)

if __name__ == "__main__":
    run()
