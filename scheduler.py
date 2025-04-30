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

# [Keep all other existing functions unchanged]
