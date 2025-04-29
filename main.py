import os
from threading import Thread
from server import app
from scheduler import run
import playwright.sync_api

def install_browsers():
    """Ensure Playwright browsers are installed"""
    if not os.path.exists("/opt/render/.cache/ms-playwright"):
        os.system("playwright install chromium")
        os.system("playwright install-deps")

if __name__ == "__main__":
    # Install browsers first
    install_browsers()
    
    # Start Flask in background
    Thread(target=app.run, kwargs={
        'host': "0.0.0.0",
        'port': int(os.getenv("PORT", 8080))
    }, daemon=True).start()
    
    # Start bot
    run()
