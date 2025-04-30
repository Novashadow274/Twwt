import time
import random
import json
import logging
import requests
from bs4 import BeautifulSoup
import telebot
from config import *
from formatter import format_message
from helper import download_media
from pathlib import Path
from pprint import pformat

# Enhanced logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot with timeout
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
REQUEST_TIMEOUT = 30

def load_state():
    """Load or initialize state file"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                logger.info("Loaded existing state file")
                return state
    except Exception as e:
        logger.warning(f"Error loading state: {str(e)}")
    
    # Create new state if file doesn't exist or is invalid
    state = {username: 0 for username in ACCOUNTS}
    logger.info("Created new state file")
    return state

def save_state(state):
    """Save state to file"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
        logger.debug("State saved successfully")
    except Exception as e:
        logger.error(f"Failed to save state: {str(e)}")

def get_latest_tweet(username):
    """Improved Twitter scraping with modern selectors"""
    try:
        logger.info(f"🔄 Scraping @{username}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://x.com/'
        }

        # Try multiple endpoints
        endpoints = [
            f"https://x.com/{username}",
            f"https://x.com/{username}/with_replies",
            f"https://mobile.x.com/{username}"
        ]

        for url in endpoints:
            try:
                response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Modern tweet selector
                tweet = soup.find('article', attrs={'role': 'article'}) or \
                       soup.find('div', attrs={'data-testid': 'tweet'})
                
                if tweet:
                    # Extract content
                    content = (tweet.find('div', {'data-testid': 'tweetText'}) or 
                             tweet.find('div', {'class': 'tweet-text'})).get_text()
                    
                    # Get tweet ID
                    tweet_id = (tweet.get('data-tweet-id') or 
                              tweet.get('data-item-id') or
                              str(int(time.time())))  # Fallback ID
                    
                    # Get media
                    media = [
                        img['src'] for img in tweet.find_all('img', {'alt': 'Image'}) 
                        if img.get('src', '').startswith('http')
                    ]
                    
                    return {
                        'id': tweet_id,
                        'content': content,
                        'media': media
                    }
                    
            except Exception as e:
                logger.warning(f"Attempt failed for {url}: {str(e)}")
                continue
        
        logger.error(f"All scraping attempts failed for @{username}")
        return None

    except Exception as e:
        logger.error(f"Scrape error for @{username}: {str(e)}", exc_info=True)
        return None

def process_account(username, state):
    """Processing with immediate visibility"""
    try:
        logger.info(f"🔍 Checking @{username}")
        
        tweet_data = get_latest_tweet(username)
        if not tweet_data:
            return
            
        current_id = str(state.get(username, 0))
        if str(tweet_data['id']) == current_id:
            logger.debug(f"No new tweets for @{username}")
            return
            
        logger.info(f"🎯 New tweet from @{username} (ID: {tweet_data['id']})")
        
        # Send test notification first
        try:
            bot.send_message(
                TELEGRAM_CHAT_ID,
                f"🔔 New update from @{username}",
                disable_notification=True
            )
        except Exception as e:
            logger.error(f"Telegram test failed: {str(e)}")
            return
            
        # Process full tweet
        message = format_message(username, tweet_data['content'])
        
        # Handle media
        media_paths = []
        if tweet_data['media']:
            for url in tweet_data['media'][:4]:  # Limit to 4 media items
                try:
                    path = download_media(url)
                    if path:
                        media_paths.append(path)
                except Exception as e:
                    logger.error(f"Media download failed: {str(e)}")
                    continue
        
        # Send to Telegram
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
            logger.error(f"Failed to send update: {str(e)}")

    except Exception as e:
        logger.error(f"Processing error for @{username}: {str(e)}")
        time.sleep(10)

def run():
    """Main loop with visible activity"""
    logger.info("🚀 Starting monitoring loop")
    state = load_state()
    
    # Initial test message
    try:
        bot.send_message(TELEGRAM_CHAT_ID, "⚽ Bot activated! Starting monitoring...")
    except Exception as e:
        logger.error(f"Initial message failed: {str(e)}")
    
    while True:
        try:
            for username in ACCOUNTS:
                start_time = time.time()
                process_account(username, state)
                
                # Dynamic delay between accounts
                elapsed = time.time() - start_time
                delay = max(5, 15 - elapsed)  # 5-15 second delay
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"Main loop error: {str(e)}")
            time.sleep(30)
