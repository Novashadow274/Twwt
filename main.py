import os
from threading import Thread
from server import app
from scheduler import run
from playwright.sync_api import sync_playwright

def configure_playwright():
    """Configure Playwright without system dependencies"""
    with sync_playwright() as p:
        # Use Render's existing Chrome if available
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/google-chrome"  # Render's Chrome path
        )
        browser.close()

if __name__ == "__main__":
    # Configure Playwright first
    configure_playwright()
    
    # Start Flask in background
    Thread(target=app.run, kwargs={
        'host': "0.0.0.0", 
        'port': int(os.getenv("PORT", 8080))
    }, daemon=True).start()
    
    # Start bot
    run()
