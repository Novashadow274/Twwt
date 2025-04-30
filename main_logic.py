import requests
from bs4 import BeautifulSoup
import telebot
from config import BOT_TOKEN, CHANNEL_ID
from formatter import format_tweet
from fake_useragent import UserAgent

bot = telebot.TeleBot(BOT_TOKEN)

def get_latest_tweet(username):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    instance = "https://nitter.tiekoetter.com"
    url = f"{instance}/{username}"

    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    tweet_div = soup.find("div", {"class": "timeline-item"})
    if not tweet_div:
        raise Exception("Tweet not found")

    content_div = tweet_div.find("div", {"class": "tweet-content"})
    link_tag = tweet_div.find("a", {"class": "tweet-link"})

    if not content_div or not link_tag:
        raise Exception("Tweet structure missing")

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
