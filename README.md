# 🔥 X (Twitter) to Telegram Football News Bot ⚽
**Real-time updates from top football journalists without API limits**  
*Optimized for 2025 scraping • Runs 24/7 on Render's free tier*

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 📌 Key Features
| Feature | Implementation Details |
|---------|-----------------------|
| **Zero-API Scraping** | Uses `snscrape` with rotating user-agents to bypass X's bot detection |
| **Smart Scheduling** | 15 accounts checked every 7 minutes (30s staggered intervals) |
| **Multi-Media Support** | Photos (up to 4), Videos (MP4), and GIFs with auto-cleanup |
| **Self-Healing** | Atomic state saving + automatic recovery after crashes |
| **Anti-Block System** | Randomized delays (15-45s) + residential-like headers |
| **Cost-Free** | Designed for Render's free tier (512MB RAM) |

## 🧩 File Structure
```bash
.
├── data/                   # Configurations (git-tracked)
│   ├── name_priority.json  # Account priority tiers
│   ├── headline_name.json  # Display names for Telegram
│   ├── source_hashtag.json # Custom hashtags per journalist
│   └── state.json          # Last seen tweet IDs
├── temp_media/             # Auto-deleted after 1h
├── .env                    # Secrets (TELEGRAM_BOT_TOKEN etc.)
├── config.py               # Central configuration loader
├── scheduler.py            # Main scraping logic
├── formatter.py            # Telegram message formatting
├── helper.py               # Media downloader/cleaner
├── server.py               # Flask health check server
├── main.py                 # Entry point
└── requirements.txt        # Python dependencies
