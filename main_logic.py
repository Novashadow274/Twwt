import requests
from bs4 import BeautifulSoup
import telebot
from config import BOT_TOKEN, CHANNEL_ID
from formatter import format_tweet
from fake_useragent import UserAgent

bot = telebot.TeleBot(BOT_TOKEN)

def get_latest_tweet(username):
    headers = {"User-Agent": UserAgent().random}
    nitter_instances = [
        "https://nitter.kavin.rocks",
        "https://nitter.poast.org",
        "https://nitter.moomoo.me",
        "https://nitter.pufe.org",
    ]

    for instance in nitter_instances:
        try:
            url = f"{instance}/{username}"
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            tweet_div = soup.find("div", {"class": "timeline-item"})
            if not tweet_div:
                continue

            content_div = tweet_div.find("div", {"class": "tweet-content"})
            link_tag = tweet_div.find("a", {"class": "tweet-link"})

            if not content_div or not link_tag:
                continue

            text = content_div.get_text(strip=True)
            link = link_tag.get("href")

            if not link:
                continue

            full_url = f"https://x.com{link}"
            return text, full_url
        except Exception:
            continue

    raise Exception("Tweet not found on any Nitter instance")

def post_latest_tweet(username, last_url=None):
    tweet_text, tweet_url = get_latest_tweet(username)
    if tweet_url == last_url:
        return None

    msg = format_tweet(tweet_text, tweet_url)
    bot.send_message(CHANNEL_ID, msg)
    return tweet_url
