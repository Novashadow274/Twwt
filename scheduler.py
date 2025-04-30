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
    """Browser launcher that works on Render without root"""
    return playwright.chromium.launch(
        headless=True,
        executable_path="/opt/render/.cache/ms-playwright/chromium-1105/chrome-linux/chrome",
        args=[
            '--disable-gpu',
            '--single-process',
            '--no-zygote',
            '--no-sandbox'
        ],
        timeout=30000
    )

def get_latest_tweet(username):
    """Browser-based scraping that avoids API blocks"""
    with sync_playwright() as p:
        browser = None
        try:
            browser = get_browser(p)
            page = browser.new_page(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Load profile page
            page.goto(f"https://x.com/{username}", timeout=15000)
            
            # Wait for content
            try:
                page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
            except:
                return None
                
            # Extract tweet data
            tweets = page.query_selector_all('article[data-testid="tweet"]')
            if not tweets:
                return None
                
            tweet = tweets[0]
            return {
                'id': tweet.get_attribute('data-tweet-id'),
                'content': tweet.query_selector('div[data-testid="tweetText"]').inner_text(),
                'media': [img.get_attribute('src') for img in tweet.query_selector_all('img[alt="Image"]') if img.get_attribute('src')]
            }
        except Exception as e:
            logger.error(f"Scrape error for {username}: {str(e)}")
            return None
        finally:
            if browser:
                browser.close()

# ... [keep all other existing functions unchanged] ...

def run():
    """Main loop with Render-specific optimizations"""
    state = load_state()
    while True:
        for username in ACCOUNTS:
            start_time = time.time()
            process_account(username, state)
            elapsed = time.time() - start_time
            delay = max(60, random.randint(120, 240) - int(elapsed))  # 2-4 minute intervals
            time.sleep(delay)
