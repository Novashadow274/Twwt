# main.py
# Entry point: launches Flask server and Twitter-scraper bot.
# Also configures SSL certificates for snscrape/requests in restricted environments.

import os
import certifi

# Point both Python and requests at certifi's CA bundle
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from threading import Thread
from server import app
from scheduler import start_bot

def run_flask():
    """Run Flask health-check server on port 8080."""
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    # Start Flask in a daemon thread so it doesn't block bot startup/shutdown
    Thread(target=run_flask, daemon=True).start()

    # Now start the bot (which uses snscrape/requests with our SSL bundle)
    start_bot()
