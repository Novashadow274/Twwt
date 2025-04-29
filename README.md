# Twitter Scraper Telegram Bot

This bot automatically scrapes tweets from a list of public Twitter accounts and posts them to a Telegram chat. It uses `snscrape` (no Twitter API required) and `pyTelegramBotAPI` to send messages with or without media.

---

## Features

- Scrapes 15 public Twitter accounts in a fixed order.
- Posts only new, original tweets (ignores replies, retweets, quotes).
- Formats each post with:
  - **DisplayName🚨**  
  - Tweet content (emojis & line breaks preserved)  
  - 🔗Source #Hashtag  
- Sends tweets with:
  - **Photos** as albums  
  - **Videos/GIFs** as Telegram video messages  
  - **Text-only** tweets as plain messages  
- Tracks last-sent tweet IDs in `state.json`.
- On startup, immediately posts the latest tweet from the **top 3 priority** accounts.
- Posts **all unseen** tweets (no limit) in chronological order.
- Sends a “Bot is alive” message to an admin chat every 4 minutes.
- Sends an error alert to the admin if 3 consecutive failures occur.

---

## Requirements

1. **Python 3.8+**  
2. **Packages** — install via:

   ```bash
   pip install -r requirements.txt
