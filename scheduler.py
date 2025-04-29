import time
import random
import logging
from fake_useragent import UserAgent
import snscrape.modules.twitter as sntwitter
import telebot
from config import *
from formatter import format_message
from helper import extract_media_urls, download_media
import requests

# Setup
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
ua = UserAgent()

def get_scraper(username):
    """Create basic scraper without session/headers"""
    return sntwitter.TwitterUserScraper(username)

def rotate_user_agent():
    """Return random user agent and add delay"""
    time.sleep(random.uniform(1, 3))
    return ua.random

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

def send_alert(message, media=None):
    try:
        headers = {'User-Agent': rotate_user_agent()}
        
        if media and media['photos']:
            media_group = []
            for i, url in enumerate(media['photos']):
                path = download_media(url, headers)
                if i == 0:
                    media_group.append(telebot.types.InputMediaPhoto(
                        open(path, 'rb'), caption=message))
                else:
                    media_group.append(telebot.types.InputMediaPhoto(
                        open(path, 'rb')))
            bot.send_media_group(TELEGRAM_CHAT_ID, media_group)
        elif media and media['videos']:
            path = download_media(media['videos'][0], headers)
            bot.send_video(TELEGRAM_CHAT_ID, open(path, 'rb'), caption=message)
        else:
            bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Send failed: {e}")

def process_account(username, state):
    try:
        scraper = get_scraper(username)
        
        # Get most recent tweet only
        for tweet in scraper.get_items():
            if tweet.id <= state.get(username, 0):
                break
                
            if not (tweet.inReplyToTweetId or getattr(tweet, 'retweetedTweet', None)):
                message = format_message(username, getattr(tweet, 'rawContent', tweet.content))
                photos, videos = extract_media_urls(tweet)
                send_alert(message, {'photos': photos, 'videos': videos})
                state[username] = tweet.id
                save_state(state)
                break
                
    except Exception as e:
        logger.error(f"Account {username} failed: {str(e)}")
        if "429" in str(e) or "Too Many Requests" in str(e):
            time.sleep(300)  # Wait 5 minutes if rate limited

def run():
    state = load_state()
    while True:
        for username in ACCOUNTS:
            process_account(username, state)
            time.sleep(random.uniform(15, 45))  # Random delay between accounts
