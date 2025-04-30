import requests
from bs4 import BeautifulSoup
import telebot
from config import BOT_TOKEN, CHANNEL_ID, NITTER_INSTANCE
from formatter import format_tweet
from fake_useragent import UserAgent

bot = telebot.TeleBot(BOT_TOKEN)

def get_latest_tweet(username):
    headers = {"User-Agent": UserAgent().random}
    url = f"{NITTER_INSTANCE}/{username}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    tweet_div = soup.find("div", {"class": "timeline-item"})
    if not tweet_div:
        raise Exception("Tweet not found")

    text = tweet_div.find("div", {"class": "tweet-content"}).get_text(strip=True)
    link = tweet_div.find("a", {"class": "tweet-link"})["href"]
    full_url = f"https://x.com{link}"

    return text, full_url

def post_latest_tweet(username, last_url=None):
    tweet_text, tweet_url = get_latest_tweet(username)
    if tweet_url == last_url:
        return None

    msg = format_tweet(tweet_text, tweet_url)
    bot.send_message(CHANNEL_ID, msg)
    return tweet_url
