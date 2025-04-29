import os
from threading import Thread
from waitress import serve
from server import app
from scheduler import run

def run_flask():
    # Render-specific port handling
    port = int(os.getenv("PORT", 8080))
    serve(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Start Flask in background
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start bot
    run()
