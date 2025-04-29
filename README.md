# Twitter to Telegram Scraper Bot

This bot scrapes specific public Twitter accounts (without using the Twitter API) and sends new tweets to a Telegram channel. It supports:

- Text-only tweets  
- Tweets with photos, GIFs, or videos  
- Auto-formatting based on username and custom source hashtags  
- Regular updates (every 7 minutes per account)
- Telegram message for bot health every 4 minutes
- 24/7 operation using Render (free) + UptimeRobot + Flask server

---

## Features

- Uses `snscrape` for scraping tweets (no API keys or login needed)
- Checks 15 journalist accounts in a staggered schedule
- Formats tweets like:
