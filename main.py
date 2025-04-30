import requests
from bs4 import BeautifulSoup
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, NITTER_URL
from formatter import format_tweet
import telebot
import time

# Initialize the Telegram bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Function to scrape the latest tweet from a user on Nitter
def get_latest_tweet(username):
    url = f"{NITTER_URL}/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        tweet = soup.find("article")
        if tweet:
            tweet_text = tweet.find("div", class_="tweet-content").text.strip()
            tweet_url = tweet.find("a", href=True)['href']
            tweet_url = f"{NITTER_URL}{tweet_url}"
            return tweet_text, tweet_url
    return None, None

# Function to send the tweet to Telegram
def send_to_telegram(tweet_text, tweet_url):
    formatted_message = format_tweet(tweet_text, tweet_url)
    bot.send_message(TELEGRAM_CHANNEL_ID, formatted_message)

# Function to check and post the latest tweet
def post_latest_tweet(username):
    tweet_text, tweet_url = get_latest_tweet(username)
    if tweet_text and tweet_url:
        send_to_telegram(tweet_text, tweet_url)

if __name__ == "__main__":
    # Replace with the desired username
    username = "FabrizioRomano"

    # Get and post the latest tweet immediately when the bot starts
    post_latest_tweet(username)

    # Run the bot to continuously check for new tweets
    while True:
        time.sleep(10)  # Sleep for 10 seconds to reduce load
        post_latest_tweet(username)
