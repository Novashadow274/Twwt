import os
from threading import Thread
from server import app
from scheduler import run
from playwright.sync_api import sync_playwright

def verify_playwright():
    """Verify Playwright can launch browser without system dependencies"""
    try:
        with sync_playwright() as p:
            # Force use of Playwright's bundled Chromium
            browser = p.chromium.launch(
                headless=True,
                channel="chrome"  # Use Playwright's managed browser
            )
            browser.close()
    except Exception as e:
        logger.error(f"Playwright verification failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Verify Playwright first
    verify_playwright()
    
    # Start Flask in background
    Thread(target=app.run, kwargs={
        'host': "0.0.0.0",
        'port': int(os.getenv("PORT", 8080))
    }, daemon=True).start()
    
    # Start bot
    run()
