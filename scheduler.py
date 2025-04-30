import time

def start_scraping():
    usernames = ['FabrizioRomano']  # Add more usernames as needed
    for username in usernames:
        try:
            post_latest_tweet(username)
            time.sleep(10)  # Sleep for 10 seconds between requests
        except Exception as e:
            print(f"Failed to scrape {username}: {e}")
