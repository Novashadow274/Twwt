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

    content_div = tweet_div.find("div", {"class": "tweet-content"})
    link_tag = tweet_div.find("a", {"class": "tweet-link"})

    if not content_div or not link_tag:
        raise Exception("Tweet structure missing required elements")

    text = content_div.get_text(strip=True)
    link = link_tag.get("href")

    if not link:
        raise Exception("Tweet link missing")

    full_url = f"https://x.com{link}"

    return text, full_url

def post_latest_tweet(username, last_url=None):
    tweet_text, tweet_url = get_latest_tweet(username)
    if tweet_url == last_url:
        return None

    msg = format_tweet(tweet_text, tweet_url)
    bot.send_message(CHANNEL_ID, msg)
    return tweet_url
