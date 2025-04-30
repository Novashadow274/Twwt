import os
from threading import Thread
from server import app
from scheduler import run

if __name__ == "__main__":
    # Start Flask in background
    Thread(target=app.run, kwargs={
        'host': "0.0.0.0",
        'port': int(os.getenv("PORT", 8080))
    }, daemon=True).start()
    
    # Start bot
    run()
