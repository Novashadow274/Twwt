import time
import threading
import logging
from main_logic import post_latest_tweet

usernames = ["FabrizioRomano", "David_Ornstein"]
last_seen = {}

logging.basicConfig(level=logging.INFO)

def check_users():
    while True:
        for username in usernames:
            logging.info(f"Checking @{username}")
            try:
                tweet = post_latest_tweet(username, last_seen.get(username))
                if tweet:
                    last_seen[username] = tweet
            except Exception as e:
                logging.error(f"Error checking @{username}: {e}")
        time.sleep(60)  # Check every minute

def start_scraping():
    thread = threading.Thread(target=check_users)
    thread.daemon = True
    thread.start()
