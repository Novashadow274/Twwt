import os
from threading import Thread
from waitress import serve
from server import app
from scheduler import run

def run_flask():
    serve(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    run()
