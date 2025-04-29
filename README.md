# 🚨 X (Twitter) to Telegram Scraper Bot ⚽

A lightweight bot that monitors **15+ football journalists** on X (Twitter) and delivers real-time updates to Telegram, **without using the Twitter API**. Optimized for 2025 and runs 24/7 on Render's free tier.

## 🌟 Features
- **Zero-API scraping** using `snscrape` (bypasses rate limits)
- **Smart scheduling**: Checks accounts every 7 minutes (30s staggered)
- **Media support**: Photos, videos, and GIFs with auto-cleanup
- **Anti-block system**: Rotating user agents and randomized delays
- **Self-healing**: Atomic state saving and automatic recovery
- **Render-ready**: Health checks and minimal resource usage

## ⚙️ File Structure
