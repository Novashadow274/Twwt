import time
import random
import logging
from fake_useragent import UserAgent
import snscrape.modules.twitter as sntwitter
import telebot
from config import *
from formatter import format_message
from helper import extract_media_urls, download_media

# Setup
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
ua = UserAgent()

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {username: 0 for username in ACCOUNTS}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def send_alert(message, photos=None, videos=None):
    try:
        if photos:
            media = [telebot.types.InputMediaPhoto(download_media(url)) for url in photos]
            media[0].caption = message
            bot.send_media_group(TELEGRAM_CHAT_ID, media)
        elif videos:
            bot.send_video(TELEGRAM_CHAT_ID, download_media(videos[0]), caption=message)
        else:
            bot.send_message(TELEGRAM_CHAT_ID, message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Send failed: {e}")

def scrape_account(username, last_id):
    try:
        scraper = sntwitter.TwitterUserScraper(
            username,
            headers={
                'User-Agent': ua.random,
                'Accept-Language': 'en-US,en;q=0.9'
            }
        )
        for tweet in scraper.get_items():
            if tweet.id <= last_id:
                break
            if not (tweet.inReplyToTweetId or getattr(tweet, 'retweetedTweet', None)):
                return tweet
    except Exception as e:
        logger.error(f"Scrape failed for {username}: {e}")
    return None

def run():
    state = load_state()
    while True:
        for username in ACCOUNTS:
            time.sleep(random.uniform(15, 45))  # Randomized delay
            if tweet := scrape_account(username, state.get(username, 0)):
                message = format_message(username, tweet.rawContent)
                photos, videos = extract_media_urls(tweet)
                send_alert(message, photos, videos)
                state[username] = tweet.id
                save_state(state)
