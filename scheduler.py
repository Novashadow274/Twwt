import os
import sys
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

# Debug logging setup
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def debug_log_tweet(username, tweet_data):
    """Safe logging of tweet data"""
    if not tweet_data:
        logger.debug(f"No tweet data for @{username}")
        return
    
    debug_info = {
        'id': tweet_data.get('id'),
        'content': tweet_data.get('content')[:50] + '...' if tweet_data.get('content') else None,
        'media_count': len(tweet_data.get('media', [])),
        'media_sample': tweet_data.get('media', [])[:1] if tweet_data.get('media') else None
    }
    logger.debug(f"Tweet data for @{username}:\n{pformat(debug_info)}")

def get_latest_tweet(username):
    """Get latest tweet using HTML scraping with debug"""
    try:
        logger.debug(f"Starting scrape for @{username}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://x.com/'
        }
        
        # Try both profile and with_replies endpoints
        endpoints = [
            f"https://x.com/{username}",
            f"https://x.com/{username}/with_replies"
        ]
        
        for url in endpoints:
            try:
                response = requests.get(url, headers=headers, timeout=20)
                response.raise_for_status()
                
                # Debug: Save HTML for inspection if needed
                with open(f"debug_{username}.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                tweet = soup.find('article', {'data-testid': 'tweet'})
                
                if tweet:
                    break
            except Exception as e:
                logger.warning(f"Attempt failed for {url}: {str(e)}")
                continue
        
        if not tweet:
            logger.debug(f"No tweet found for @{username} on any endpoint")
            return None
            
        # Extract data
        content_div = tweet.find('div', {'data-testid': 'tweetText'})
        if not content_div:
            logger.debug("Tweet content div not found")
            return None
            
        content = content_div.get_text()
        tweet_id = tweet.get('data-tweet-id')
        
        if not tweet_id:
            logger.debug("No tweet ID found")
            return None
        
        # Get media
        media = []
        media_tags = tweet.find_all('img', alt='Image') + tweet.find_all('video')
        for media_item in media_tags:
            src = media_item.get('src') or media_item.get('poster')
            if src and src.startswith('http'):
                media.append(src)
        
        result = {
            'id': tweet_id,
            'content': content,
            'media': media
        }
        
        debug_log_tweet(username, result)
        return result
        
    except Exception as e:
        logger.error(f"Scrape failed for @{username}: {str(e)}")
        return None

def load_state():
    """Load state with debug"""
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            logger.debug(f"Loaded state: {state}")
            # Initialize any missing accounts
            for username in ACCOUNTS:
                if username not in state:
                    state[username] = 0
            return state
    except Exception as e:
        logger.warning(f"State file error: {str(e)}. Creating new state.")
        return {username: 0 for username in ACCOUNTS}

def save_state(state):
    """Save state with debug"""
    try:
        temp = STATE_FILE.with_suffix('.tmp')
        with open(temp, 'w') as f:
            json.dump(state, f)
        temp.replace(STATE_FILE)
        logger.debug("State saved successfully")
    except Exception as e:
        logger.error(f"Failed to save state: {str(e)}")

def process_account(username, state):
    """Enhanced processing with debug"""
    try:
        logger.debug(f"Processing @{username}...")
        tweet_data = get_latest_tweet(username)
        
        if not tweet_data:
            logger.debug(f"No valid tweet data for @{username}")
            return
            
        if str(tweet_data['id']) == str(state.get(username)):
            logger.debug(f"No new tweets for @{username}")
            return
            
        logger.debug(f"New tweet found for @{username}")
        message = format_message(username, tweet_data['content'])
        logger.debug(f"Formatted message: {message[:100]}...")
        
        # Handle media
        media_paths = []
        if tweet_data['media']:
            logger.debug(f"Processing {len(tweet_data['media'])} media items")
            for url in tweet_data['media']:
                try:
                    path = download_media(url)
                    if path:
                        media_paths.append(path)
                        logger.debug(f"Downloaded media: {url} -> {path}")
                except Exception as e:
                    logger.error(f"Media download failed: {str(e)}")
        
        # Send message
        try:
            # First test Telegram connection with simple message
            bot.send_message(TELEGRAM_CHAT_ID, f"🔍 Testing bot functionality for @{username}")
            
            if media_paths:
                logger.debug(f"Sending media group with {len(media_paths)} items")
                media_group = []
                for i, path in enumerate(media_paths):
                    with open(path, 'rb') as f:
                        if i == 0:
                            media_group.append(telebot.types.InputMediaPhoto(f, caption=message))
                        else:
                            media_group.append(telebot.types.InputMediaPhoto(f))
                bot.send_media_group(TELEGRAM_CHAT_ID, media_group)
            else:
                logger.debug("Sending text-only message")
                bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode='Markdown')
            
            state[username] = tweet_data['id']
            save_state(state)
            logger.info(f"✅ Successfully posted update from @{username}")
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            
    except Exception as e:
        logger.error(f"Account processing failed for @{username}: {str(e)}")
        time.sleep(300)

def run():
    """Main loop with enhanced logging"""
    logger.info("🚀 Starting main bot loop")
    state = load_state()
    
    while True:
        try:
            for username in ACCOUNTS:
                start_time = time.time()
                process_account(username, state)
                elapsed = time.time() - start_time
                delay = max(60, random.randint(120, 240) - int(elapsed))
                logger.debug(f"Cycle completed in {elapsed:.2f}s. Sleeping for {delay}s")
                time.sleep(delay)
                
        except Exception as e:
            logger.critical(f"Main loop crashed: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before restarting
