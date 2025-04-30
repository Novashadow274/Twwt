import time
import requests
from requests.exceptions import ConnectionError

def get_latest_tweet(username, retries=3, delay=5):
    url = f'https://nitter.net/{username}/rss'
    
    # Retry logic for connection errors
    for _ in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Ensure we handle any 4xx/5xx errors
            return response.text  # Assuming the RSS feed is returned as text
        except ConnectionError as e:
            print(f"Connection error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    
    print(f"Failed to retrieve latest tweet for {username} after {retries} retries.")
    return None

def post_latest_tweet(username):
    tweet_data = get_latest_tweet(username)
    if tweet_data:
        # Your logic to post the tweet to the Telegram channel
        print("Posting tweet to Telegram...")
    else:
        print(f"Failed to retrieve tweet for {username}")
