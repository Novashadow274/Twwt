import time
from main import post_latest_tweet

def start_scraping():
    username = "FabrizioRomano"
    
    while True:
        print(f"Checking latest tweet from @{username}...")
        post_latest_tweet(username)
        time.sleep(10)  # Check every 10 seconds for a new tweet

if __name__ == "__main__":
    start_scraping()
